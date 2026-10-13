"""Bounded official asset retrieval and fail-closed provenance checks."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_RESOURCE_BYTES = 16 * 1024 * 1024


class ResourceError(ValueError):
    """An authentic required resource is unavailable or changed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def resource_path(root: Path, relative: str) -> Path:
    parts = relative.split("/")
    if (
        not relative.startswith("resources/official/")
        or any(part in {"", ".", ".."} for part in parts)
        or "\\" in relative
        or ":" in relative
    ):
        raise ResourceError(f"Invalid resource path: {relative}")
    path = root / relative
    for parent in [path, *path.parents]:
        if parent == root.parent:
            break
        if parent.is_symlink():
            raise ResourceError(f"Symlink resource path: {relative}")
    if not path.resolve().is_relative_to(root.resolve() / "resources" / "official"):
        raise ResourceError(f"Resource escapes inventory: {relative}")
    return path


def read_manifest(root: Path) -> dict[str, Any]:
    value = json.loads((root / "resources/manifest.json").read_text())
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ResourceError("Unsupported resource manifest")
    entries = value.get("resources")
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        raise ResourceError("Invalid resource inventory")
    ids = [entry.get("id") for entry in entries]
    if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        raise ResourceError("Duplicate or invalid resource IDs")
    return value


def require_resources(root: Path, ids: list[str]) -> dict[str, Path]:
    entries = {entry["id"]: entry for entry in read_manifest(root)["resources"]}
    result: dict[str, Path] = {}
    for resource_id in ids:
        entry = entries.get(resource_id)
        if entry is None or entry.get("status") != "verified":
            raise ResourceError(f"Official prerequisite pending: {resource_id}")
        path = resource_path(root, entry["path"])
        if not path.is_file() or sha256(path) != entry.get("sha256"):
            raise ResourceError(f"Resource missing or hash mismatch: {resource_id}")
        result[resource_id] = path
    return result


def fetch_resource(root: Path, resource_id: str) -> Path:
    """Fetch one pinned public file, never datasets, archives or model weights."""
    entries = {entry["id"]: entry for entry in read_manifest(root)["resources"]}
    entry = entries.get(resource_id)
    if entry is None or not entry.get("download_url") or not entry.get("sha256"):
        raise ResourceError("Resource needs an authenticated official download/review")
    url = entry["download_url"]
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "www.kaggle.com":
        raise ResourceError("Download must originate at the official Kaggle endpoint")
    target = resource_path(root, entry["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha256(target) != entry["sha256"]:
            raise ResourceError("Existing resource differs; refusing to overwrite")
        return target
    temporary: Path | None = None
    try:
        with urlopen(
            Request(url, headers={"User-Agent": "Mostaza/0.1"}), timeout=60
        ) as response:
            final_host = urlsplit(response.url).hostname or ""
            if not (
                final_host == "www.kaggle.com"
                or final_host == "storage.googleapis.com"
                or final_host.endswith(".googleusercontent.com")
            ):
                raise ResourceError("Unexpected official download redirect")
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
                temporary = Path(output.name)
                total = 0
                while block := response.read(65536):
                    total += len(block)
                    if total > min(
                        entry.get("max_bytes", MAX_RESOURCE_BYTES), MAX_RESOURCE_BYTES
                    ):
                        raise ResourceError("Resource exceeds bounded download size")
                    output.write(block)
        if sha256(temporary) != entry["sha256"]:
            raise ResourceError("Downloaded bytes differ from the approved pin")
        # Hard link publishes atomically without replacing concurrent/user files.
        os.link(temporary, target)
        return target
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
