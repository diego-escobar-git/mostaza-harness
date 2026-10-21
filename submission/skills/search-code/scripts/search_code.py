#!/usr/bin/env python3
"""Disposable, standard-library-only lexical index and conservative Python graph.

All operations reconcile source fingerprints under a private writer lock. SQLite
holds the graph; only the bounded answer and one parsed file live in Python RAM.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import fcntl
import hashlib
import io
import json
import os
import re
import shlex
import sqlite3
import stat
import sys
import tempfile
import time
import tokenize
from collections import Counter
from pathlib import Path

SCHEMA = 6
PARSER_VERSION = list(sys.version_info[:2])
MAX_FILE = 1024 * 1024
MAX_FILES = 50000
MAX_BYTES = 256 * 1024 * 1024
MAX_OUTPUT = 4500
MAX_NODES = 40
MAX_EDGES = 80
MAX_AST_TOKENS = 100000
DEADLINE = 45.0
LOCK_WAIT = 2.0
EXCLUDED_DIRS = {
    "node_modules",
    "vendor",
    "vendors",
    "venv",
    "env",
    "__pycache__",
    "build",
    "dist",
    "target",
    "site-packages",
    "results",
    "resources",
    "embeddings",
    "graphs",
    "verifier",
    "verifiers",
    "solutions",
    "references",
    "coverage",
    "htmlcov",
    "generated",
    "cache",
    "caches",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".o",
    ".a",
    ".dll",
    ".dylib",
    ".exe",
    ".zip",
    ".gz",
    ".bz2",
    ".xz",
    ".tar",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".ico",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".npy",
    ".npz",
    ".pkl",
    ".pickle",
    ".parquet",
    ".arrow",
    ".patch",
    ".lock",
    ".ipynb",
}
FALLBACK = "Use run_command with quoted literal grep -R -n -F -- QUERY PATH."


class Failure(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def tick(deadline):
    if time.monotonic() >= deadline:
        raise Failure("timeout", "Operation exceeded its cooperative deadline.")


def source_version():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def workspace(value):
    candidate = Path(value)
    if not candidate.is_absolute() or not candidate.is_dir():
        raise Failure("invalid_arguments", "--root must be an absolute directory.")
    # Reject caller-controlled symlink components, including the root itself.
    for part in (candidate, *candidate.parents):
        if part.is_symlink():
            raise Failure("unsafe_path", "Workspace symlinks are not accepted.")
    return candidate.resolve()


def identity(root):
    return {
        "workspace": str(root),
        "source": source_version(),
        "schema": SCHEMA,
        "parser": PARSER_VERSION,
    }


def private_directory(root):
    expected = identity(root)
    digest = hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()
    directory = Path(tempfile.gettempdir()).resolve() / (
        f"mostaza-search-code-{os.getuid()}-{digest[:32]}"
    )
    if directory == root or root in directory.parents:
        raise Failure("unsafe_cache", "Temporary cache must be outside workspace.")
    try:
        directory.mkdir(mode=0o700)
    except FileExistsError:
        pass
    info = directory.lstat()
    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise Failure("unsafe_cache", "Cache requires a private owned directory.")
    for entry in directory.iterdir():
        validate_private_file(entry)
    return directory, expected


def validate_private_file(path):
    info = path.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_uid != os.getuid()
        or info.st_nlink != 1
        or info.st_mode & 0o077
    ):
        raise Failure("unsafe_cache", "Cache contains an unsafe file.")


@contextlib.contextmanager
def writer_lock(directory, deadline):
    fd = os.open(
        directory / "writer.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
    )
    try:
        validate_private_file(directory / "writer.lock")
        stop = min(deadline, time.monotonic() + LOCK_WAIT)
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= stop:
                    raise Failure(
                        "busy", "Another index writer holds the lock."
                    ) from None
                time.sleep(0.02)
        yield
    finally:
        os.close(fd)


def excluded(name, directory=False):
    lower = name.lower()
    # Reserved artifacts can be directories at any depth, not just file names.
    if lower.startswith(".") or re.match(
        r"^(solutions?|references?|test[_-]patch|ground[_-]truth)([_.-]|$)", lower
    ):
        return True
    if directory:
        return lower in EXCLUDED_DIRS or lower.endswith((".egg-info", ".dist-info"))
    stem = Path(lower).stem
    return (
        Path(lower).suffix in EXCLUDED_SUFFIXES
        or lower.endswith((".min.js", ".min.css", ".map"))
        or stem in {"tasks", "task", "instances", "instance", "metadata", "test_patch"}
    )


def read_at(root_fd, relative):
    """Open every component without following a symlink, even during a rename race."""
    parts = relative.split("/")
    fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
            )
            os.close(fd)
            fd = child
        source = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd
        )
        try:
            info = os.fstat(source)
            if not stat.S_ISREG(info.st_mode):
                return None, "non_regular"
            if info.st_size > MAX_FILE:
                return None, "large"
            with os.fdopen(source, "rb", closefd=False) as stream:
                data = stream.read(MAX_FILE + 1)
            if len(data) > MAX_FILE:
                return None, "large"
            if b"\0" in data:
                return None, "binary"
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                return None, "non_utf8"
            return data, None
        finally:
            os.close(source)
    finally:
        os.close(fd)


def snapshot(root_fd, deadline):
    manifest, reasons = {}, Counter()
    total = 0

    def walk(fd, prefix="", depth=0):
        nonlocal total
        if depth > 64:
            reasons["depth_limit"] += 1
            return
        with os.scandir(fd) as entries:
            # Filesystem iteration order does not determine the retained subset.
            for entry in sorted(entries, key=lambda item: item.name):
                tick(deadline)
                relative = prefix + entry.name
                try:
                    if entry.is_symlink():
                        reasons["symlink"] += 1
                    elif entry.is_dir(follow_symlinks=False):
                        if excluded(entry.name, True):
                            reasons["excluded_directory"] += 1
                            continue
                        child = os.open(
                            entry.name,
                            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=fd,
                        )
                        try:
                            walk(child, relative + "/", depth + 1)
                        finally:
                            os.close(child)
                    elif excluded(entry.name):
                        reasons["excluded_file"] += 1
                    elif not entry.is_file(follow_symlinks=False):
                        reasons["non_regular"] += 1
                    elif len(manifest) >= MAX_FILES:
                        reasons["file_limit"] += 1
                    else:
                        data, reason = read_at(root_fd, relative)
                        if reason:
                            reasons[reason] += 1
                        elif total + len(data) > MAX_BYTES:
                            reasons["source_byte_limit"] += 1
                        else:
                            total += len(data)
                            manifest[relative] = hashlib.sha256(data).hexdigest()
                except OSError:
                    reasons["unreadable"] += 1

    walk(root_fd)
    return manifest, dict(reasons), total


DDL = """
CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE files(path TEXT PRIMARY KEY, digest TEXT, text TEXT, error TEXT);
CREATE VIRTUAL TABLE lexical USING fts5(path, text, tokenize='unicode61');
CREATE TABLE symbols(
 id TEXT PRIMARY KEY, path TEXT, name TEXT, qualified_name TEXT, kind TEXT,
 start_line INTEGER, end_line INTEGER, column_no INTEGER, scope TEXT, module TEXT,
 lookup_name TEXT);
CREATE INDEX symbol_scope ON symbols(scope,lookup_name);
CREATE INDEX symbol_path ON symbols(path);
CREATE INDEX symbol_module ON symbols(module,qualified_name);
CREATE INDEX symbol_name ON symbols(name);
CREATE TABLE bindings(owner TEXT, name TEXT, module TEXT, member TEXT,
 dynamic INTEGER, bound_module TEXT, line INTEGER, column_no INTEGER);
CREATE INDEX binding_owner ON bindings(owner,name);
CREATE INDEX binding_module ON bindings(module);
CREATE TABLE ineligible(symbol TEXT PRIMARY KEY, reason TEXT, namespace INTEGER);
CREATE TABLE implicit_class(owner TEXT, name TEXT, line INTEGER, column_no INTEGER);
CREATE INDEX implicit_class_owner ON implicit_class(owner,name);
CREATE TABLE type_bindings(owner TEXT, name TEXT);
CREATE INDEX type_binding_owner ON type_bindings(owner,name);
CREATE TABLE declarations(path TEXT, owner TEXT, name TEXT, kind TEXT);
CREATE INDEX declaration_owner ON declarations(owner,name);
CREATE TABLE writes(path TEXT, writer TEXT, expression TEXT, kind TEXT, line INTEGER);
CREATE INDEX write_path ON writes(path);
CREATE TABLE write_bindings(path TEXT, owner TEXT, name TEXT, binding INTEGER);
CREATE INDEX write_binding_owner ON write_bindings(owner,name);
CREATE TABLE mutations(path TEXT, owner TEXT, name TEXT, line INTEGER,
 UNIQUE(path,owner,name,line));
CREATE INDEX mutation_owner ON mutations(owner,name);
CREATE INDEX mutation_path ON mutations(path);
CREATE TABLE refs(source TEXT, expression TEXT, kind TEXT, path TEXT, line INTEGER,
 binding INTEGER, context TEXT, lookup_expression TEXT);
CREATE INDEX reference_source ON refs(source);
CREATE TABLE edges(source TEXT, target TEXT, kind TEXT, path TEXT, line INTEGER,
 UNIQUE(source,target,kind,path,line));
CREATE INDEX edge_source ON edges(source,kind);
CREATE INDEX edge_target ON edges(target,kind);
CREATE TABLE unresolved(source TEXT, expression TEXT, kind TEXT, path TEXT,
 line INTEGER, reason TEXT);
CREATE INDEX unresolved_source ON unresolved(source);
"""


def initialize(connection, expected):
    try:
        connection.executescript(DDL)
    except sqlite3.OperationalError as exc:
        if "fts5" in str(exc).lower():
            raise Failure(
                "unavailable", "SQLite FTS5 is unavailable. " + FALLBACK
            ) from None
        raise
    connection.executemany(
        "INSERT INTO metadata VALUES (?,?)",
        [(key, json.dumps(value)) for key, value in expected.items()]
        + [("generation", "0")],
    )
    connection.commit()


def connect(directory, expected):
    path = directory / "index.sqlite3"
    connection = None
    if path.exists():
        validate_private_file(path)
        try:
            connection = sqlite3.connect(path)
            stored = dict(connection.execute("SELECT key,value FROM metadata"))
            # A valid foreign identity is never silently accepted or overwritten.
            if any(
                json.loads(stored[key]) != expected[key]
                for key in ("workspace", "source")
            ):
                raise Failure(
                    "unsafe_cache", "Cache identity does not match workspace/source."
                )
            if json.loads(stored["schema"]) != SCHEMA:
                raise sqlite3.DatabaseError("Incompatible disposable schema")
            if json.loads(stored["parser"]) != expected["parser"]:
                raise sqlite3.DatabaseError("Incompatible parser generation")
            if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise sqlite3.DatabaseError("Corrupt disposable cache")
            connection.execute("SELECT count(*) FROM lexical").fetchone()
            for table in (
                "files",
                "symbols",
                "bindings",
                "write_bindings",
                "ineligible",
                "implicit_class",
                "type_bindings",
                "declarations",
                "writes",
                "mutations",
                "refs",
                "edges",
                "unresolved",
            ):
                connection.execute(f"SELECT * FROM {table} LIMIT 0")
            return connection
        except Failure:
            connection.close()
            raise
        except (sqlite3.DatabaseError, KeyError, ValueError):
            if connection is not None:
                connection.close()
            # Only owned disposable files inside the verified directory are removed.
            for suffix in ("", "-journal", "-wal", "-shm"):
                target = Path(str(path) + suffix)
                if target.exists():
                    validate_private_file(target)
                    target.unlink()
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    connection = sqlite3.connect(path)
    initialize(connection, expected)
    return connection


def module_name(path):
    parts = path[:-3].split("/")
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def expression(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = expression(node.value)
        return prefix + "." + node.attr if prefix else None
    return None


def mangle(name, private):
    """Python's class compilation identity, separate from the source spelling."""
    if not private or not name.startswith("__") or name.endswith("__") or "." in name:
        return name
    private = private.lstrip("_")
    return "_" + private + name if private else name


class Extractor(ast.NodeVisitor):
    def __init__(self, connection, path, tree, deadline):
        self.db, self.path, self.deadline = connection, path, deadline
        self.module = module_name(path)
        self.private, self.selective = "", None
        self.owner = self.add_symbol("", "module", 1, tree.end_lineno or 1, 0, "")
        self.qualified = ""
        self.context = None

    def add_symbol(self, name, kind, line, end, column, scope):
        qualified = (
            self.qualified + "." if getattr(self, "qualified", "") else ""
        ) + name
        symbol = f"{self.path}::{qualified}:{kind}:{line}:{column}"
        self.db.execute(
            "INSERT INTO symbols VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                symbol,
                self.path,
                name or self.path,
                qualified,
                kind,
                line,
                end,
                column,
                scope,
                self.module,
                self.lookup(name or self.path),
            ),
        )
        if scope:
            self.db.execute(
                "INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?)",
                (scope, symbol, "contains", self.path, line),
            )
        return symbol

    def visit(self, node):
        tick(self.deadline)
        return super().visit(node)

    def lookup(self, name):
        if self.selective is not None and name not in self.selective:
            return name
        return mangle(name, self.private)

    def lookup_expression(self, expr):
        return ".".join(self.lookup(part) for part in expr.split("."))

    def reference(self, expr, line, kind="calls", binding=None):
        self.db.execute(
            "INSERT INTO refs VALUES (?,?,?,?,?,?,?,?)",
            (
                self.owner,
                expr,
                kind,
                self.path,
                line,
                binding,
                self.context,
                self.lookup_expression(expr) if kind == "calls" else expr,
            ),
        )

    def definition(self, node, kind):
        previous_private, previous_selective = self.private, self.selective
        # Decorators and function defaults execute outside the type-parameter
        # scope. Generic class bases execute inside it, outside the class body.
        for decorator in node.decorator_list:
            self.visit(decorator)
        parent, qualified = self.owner, self.qualified
        self.write(node.name, "binding", node.lineno)
        symbol = self.add_symbol(
            node.name, kind, node.lineno, node.end_lineno, node.col_offset, parent
        )
        class_creation = isinstance(node, ast.ClassDef) and bool(
            node.bases or node.keywords
        )
        if node.decorator_list or class_creation:
            # Explicit bases can inherit an arbitrary metaclass, and class
            # keywords can select one. Its namespace/returned value are unproved.
            self.db.execute(
                "INSERT INTO ineligible VALUES (?,?,?)",
                (
                    symbol,
                    "decorated_binding" if node.decorator_list else "class_creation",
                    class_creation,
                ),
            )
        for parameter in getattr(node, "type_params", ()):
            tick(self.deadline)
            self.db.execute(
                "INSERT INTO type_bindings VALUES (?,?)",
                (
                    symbol,
                    mangle(
                        parameter.name,
                        node.name if isinstance(node, ast.ClassDef) else self.private,
                    ),
                ),
            )
        previous_context = self.context
        if isinstance(node, ast.ClassDef):
            self.context = symbol
            if getattr(node, "type_params", ()):
                # Generic class headers selectively mangle only their parameter
                # names; other private identifiers retain literal spellings.
                self.private = node.name
                self.selective = {parameter.name for parameter in node.type_params}
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword)
        else:
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)
        self.context = previous_context
        self.private, self.selective = previous_private, previous_selective
        self.owner = symbol
        self.qualified = (qualified + "." if qualified else "") + node.name
        if isinstance(node, ast.ClassDef):
            self.private, self.selective = node.name, None
            names = ["__module__", "__qualname__"]
            if ast.get_docstring(node, clean=False) is not None:
                names.append("__doc__")
            if getattr(node, "type_params", ()):
                names.append("__type_params__")
            if sys.version_info >= (3, 13):  # noqa: UP036 - standalone supports 3.12
                names.append("__firstlineno__")
                # This compiler write happens after the body. It must not block
                # earlier body lookups, but declarations can redirect its write.
                self.implicit(
                    "__static_attributes__",
                    node.end_lineno + 1,
                    node.body[0].col_offset,
                )
            for name in names:
                self.implicit(name, node.lineno, node.body[0].col_offset)
        # Bounds/defaults use lazy annotation scopes, not function-body call
        # execution. Preserve their uncertainty without fabricating outer calls.
        for parameter in getattr(node, "type_params", ()):
            for field in ("bound", "default_value"):
                value = getattr(parameter, field, None)
                if value is not None:
                    self.reference("<type_parameter_" + field + ">", value.lineno)
        if not isinstance(node, ast.ClassDef):
            for argument in (
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
                *([node.args.vararg] if node.args.vararg else []),
                *([node.args.kwarg] if node.args.kwarg else []),
            ):
                self.dynamic(argument.arg)
        for child in node.body:
            self.visit(child)
        self.owner, self.qualified = parent, qualified
        self.private, self.selective = previous_private, previous_selective

    def implicit(self, name, line, column, redirect=True):
        self.db.execute(
            "INSERT INTO implicit_class VALUES (?,?,?,?)",
            (self.owner, name, line, column),
        )
        if redirect:
            self.write(name, "implicit", line)

    def visit_AnnAssign(self, node):
        row = self.db.execute(
            "SELECT kind,start_line,column_no FROM symbols WHERE id=?", (self.owner,)
        ).fetchone()
        if row[0] == "class":
            # SETUP_ANNOTATIONS writes the class dictionary directly, even when
            # the identifier itself is declared global in the class body.
            column = self.db.execute(
                "SELECT column_no FROM implicit_class WHERE owner=? LIMIT 1",
                (self.owner,),
            ).fetchone()[0]
            if not self.db.execute(
                "SELECT 1 FROM implicit_class WHERE owner=? "
                "AND name='__annotations__' LIMIT 1",
                (self.owner,),
            ).fetchone():
                self.implicit("__annotations__", row[1], column, redirect=False)
        self.generic_visit(node)

    def visit_TypeAlias(self, node):
        # Alias values also have lazy annotation scopes. The alias name binds
        # here, while its type parameters must never leak into this scope.
        self.dynamic(node.name.id, node.lineno)
        self.reference("<type_alias>", node.lineno)

    def visit_FunctionDef(self, node):
        self.definition(node, "function")

    def visit_AsyncFunctionDef(self, node):
        self.definition(node, "async_function")

    def visit_ClassDef(self, node):
        self.definition(node, "class")

    def write(self, value, kind, line):
        self.db.execute(
            "INSERT INTO writes VALUES (?,?,?,?,?)",
            (self.path, self.owner, self.lookup_expression(value), kind, line),
        )

    def dynamic(self, name, line=None):
        self.db.execute(
            "INSERT INTO bindings VALUES (?,?,?,?,1,'',NULL,NULL)",
            (self.owner, self.lookup(name), "", ""),
        )
        if line is not None:
            self.write(name, "name", line)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.dynamic(node.id, node.lineno)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            dotted = expression(node)
            if dotted:
                self.write(dotted, "attribute", node.lineno)
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self.db.execute(
                "INSERT INTO declarations VALUES (?,?,?,?)",
                (self.path, self.owner, self.lookup(name), "global"),
            )

    def visit_Nonlocal(self, node):
        for name in node.names:
            self.db.execute(
                "INSERT INTO declarations VALUES (?,?,?,?)",
                (self.path, self.owner, self.lookup(name), "nonlocal"),
            )

    def visit_ExceptHandler(self, node):
        if node.name:
            self.dynamic(node.name, node.lineno)
        self.generic_visit(node)

    def visit_MatchAs(self, node):
        if node.name:
            self.dynamic(node.name, node.lineno)
        self.generic_visit(node)

    def visit_MatchStar(self, node):
        if node.name:
            self.dynamic(node.name, node.lineno)

    def visit_MatchMapping(self, node):
        if node.rest:
            self.dynamic(node.rest, node.lineno)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        # Defaults execute in the containing scope; the body has lambda locals.
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)
        self.reference("<lambda>", node.lineno)

    def visit_ListComp(self, node):
        self.reference("<comprehension>", node.lineno)
        ComprehensionWrites(self).visit(node)

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_Call(self, node):
        self.reference(expression(node.func) or "<dynamic>", node.lineno)
        self.generic_visit(node)

    def imports(self, node, module, member, local, bound_module=""):
        self.write(local, "binding", node.lineno)
        binding = self.db.execute(
            "INSERT INTO bindings VALUES (?,?,?,?,0,?,?,?)",
            (
                self.owner,
                self.lookup(local),
                module,
                member,
                bound_module,
                node.lineno,
                node.col_offset,
            ),
        )
        target = module + ("." + member if member else "")
        self.reference(target, node.lineno, "imports", binding.lastrowid)

    def visit_Import(self, node):
        for alias in node.names:
            # Explicit aliases bind the full module even when the alias happens
            # to equal its package prefix: `import p.a as p` binds p.a, not p.
            module = self.lookup(alias.name)
            bound = module if alias.asname is not None else module.split(".")[0]
            self.imports(node, module, "", alias.asname or bound, bound_module=bound)

    def visit_ImportFrom(self, node):
        package = self.module.split(".")
        if not self.path.endswith("/__init__.py") and self.path != "__init__.py":
            package = package[:-1]
        if node.level:
            if node.level > len(package):
                module = "<invalid-relative>"
            else:
                module = ".".join(package[: len(package) - node.level + 1])
                if node.module:
                    module += "." + self.lookup(node.module)
        else:
            module = self.lookup(node.module or "")
        for alias in node.names:
            self.imports(
                node, module, self.lookup(alias.name), alias.asname or alias.name
            )


class ComprehensionWrites(ast.NodeVisitor):
    """Extract escaping writes while keeping ordinary iteration bindings local."""

    def __init__(self, extractor):
        self.extractor = extractor
        self.locals = set()

    def visit(self, node):
        tick(self.extractor.deadline)
        return super().visit(node)

    def visit_ListComp(self, node):
        previous = self.locals
        self.locals = previous | {
            self.extractor.lookup(item.id)
            for generator in node.generators
            for item in ast.walk(generator.target)
            if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Store)
        }
        self.generic_visit(node)
        self.locals = previous

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_NamedExpr(self, node):
        self.extractor.visit(node.target)
        self.visit(node.value)

    def visit_Attribute(self, node):
        dotted = expression(node)
        if (
            dotted
            and self.extractor.lookup(dotted.split(".")[0]) not in self.locals
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ):
            self.extractor.write(dotted, "attribute", node.lineno)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        # Defaults execute here; the lambda body owns its own assignment expressions.
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)


def parse_file(db, path, text, deadline):
    if not path.endswith(".py"):
        return None
    try:
        for count, _ in enumerate(
            tokenize.generate_tokens(io.StringIO(text).readline), 1
        ):
            if count % 256 == 0:
                tick(deadline)
            if count > MAX_AST_TOKENS:
                return "graph_limit"
        tree = ast.parse(text, filename=path)
        # ast.Module has no end_lineno.
        tree.end_lineno = max(1, len(text.splitlines()))
        extractor = Extractor(db, path, tree, deadline)
        extractor.visit(tree)
    except (SyntaxError, ValueError, RecursionError, tokenize.TokenError):
        # Remove any partially extracted graph (lexical source remains current).
        delete_graph(db, path)
        return "parse_error"
    return None


def delete_graph(db, path):
    for table, column in (("ineligible", "symbol"), ("implicit_class", "owner")):
        db.execute(
            f"DELETE FROM {table} WHERE {column} IN "
            "(SELECT id FROM symbols WHERE path=?)",
            (path,),
        )
    db.execute(
        "DELETE FROM type_bindings WHERE owner IN "
        "(SELECT id FROM symbols WHERE path=?)",
        (path,),
    )
    for table in ("declarations", "writes", "write_bindings", "mutations"):
        db.execute(f"DELETE FROM {table} WHERE path=?", (path,))
    db.execute(
        "DELETE FROM mutations WHERE owner IN (SELECT id FROM symbols WHERE path=?)",
        (path,),
    )
    db.execute(
        "DELETE FROM bindings WHERE owner IN (SELECT id FROM symbols WHERE path=?)",
        (path,),
    )
    db.execute("DELETE FROM refs WHERE path=?", (path,))
    db.execute(
        "DELETE FROM edges WHERE path=? OR target IN "
        "(SELECT id FROM symbols WHERE path=?)",
        (path, path),
    )
    db.execute("DELETE FROM symbols WHERE path=?", (path,))


def unique(rows):
    return rows[0][0] if len(rows) == 1 else None


def has_binding(db, owner, name):
    return (
        db.execute(
            "SELECT 1 FROM bindings WHERE owner=? AND name=? UNION ALL "
            "SELECT 1 FROM symbols WHERE scope=? AND lookup_name=? LIMIT 1",
            (owner, name, owner, name),
        ).fetchone()
        is not None
    )


def write_owner(db, writer, name, deadline):
    """Declarations apply to the whole scope, including writes visited earlier."""
    declaration = db.execute(
        "SELECT kind FROM declarations WHERE owner=? AND name=? LIMIT 1", (writer, name)
    ).fetchone()
    if declaration is None:
        return writer
    if declaration[0] == "global":
        return unique(
            db.execute(
                "SELECT id FROM symbols WHERE kind='module' AND path="
                "(SELECT path FROM symbols WHERE id=?) LIMIT 2",
                (writer,),
            ).fetchall()
        )
    current = writer
    for _ in range(64):
        tick(deadline)
        row = db.execute("SELECT scope FROM symbols WHERE id=?", (current,)).fetchone()
        if row is None or not row[0]:
            return None
        current = row[0]
        kind = db.execute("SELECT kind FROM symbols WHERE id=?", (current,)).fetchone()[
            0
        ]
        if kind == "module":
            return None
        if (
            kind in {"function", "async_function"}
            and not db.execute(
                "SELECT 1 FROM declarations WHERE owner=? AND name=? LIMIT 1",
                (current, name),
            ).fetchone()
            and has_binding(db, current, name)
        ):
            return current
    raise Failure("incomplete", "Write ownership exceeded its bounded scope depth.")


def implicit_override(db, owner, name, line, column):
    """A unique earlier direct class statement can replace a compiler value.

    Conditional/nested statements and later bindings do not prove replacement.
    Dynamic assignments remain unresolved through ordinary binding eligibility.
    """
    bindings = db.execute(
        "SELECT dynamic,line,column_no FROM bindings WHERE owner=? AND name=? LIMIT 2",
        (owner, name),
    ).fetchall()
    definitions = db.execute(
        "SELECT start_line,column_no FROM symbols "
        "WHERE scope=? AND lookup_name=? LIMIT 2",
        (owner, name),
    ).fetchall()
    if bindings and not definitions and len(bindings) == 1:
        dynamic, start, col = bindings[0]
        return not dynamic and start < line and col == column
    return (
        not bindings
        and len(definitions) == 1
        and definitions[0][0] < line
        and definitions[0][1] == column
    )


def lookup_owner(db, scopes, name, deadline, line=0, potential=False):
    """Keep body locals, class dictionaries, class cells and type frames distinct."""
    for scope, lexical, cell in scopes:
        tick(deadline)
        if lexical:
            if db.execute(
                "SELECT 1 FROM declarations WHERE owner=? AND name=? LIMIT 1",
                (scope, name),
            ).fetchone():
                return write_owner(db, scope, name, deadline), None
            if (
                not potential
                and db.execute(
                    "SELECT 1 FROM ineligible WHERE symbol=? AND namespace=1", (scope,)
                ).fetchone()
            ):
                return None, "class_creation"
            implicit = db.execute(
                "SELECT column_no FROM implicit_class "
                "WHERE owner=? AND name=? AND line<=? LIMIT 1",
                (scope, name, line),
            ).fetchone()
            if implicit and not implicit_override(db, scope, name, line, implicit[0]):
                return None, "implicit_class_binding"
            if (
                has_binding(db, scope, name)
                or db.execute(
                    "SELECT 1 FROM bindings WHERE owner=? AND name='*' LIMIT 1",
                    (scope,),
                ).fetchone()
            ):
                return scope, None
        if cell and name == "__class__":
            return None, "implicit_class_binding"
        if db.execute(
            "SELECT 1 FROM type_bindings WHERE owner=? AND name=? LIMIT 1",
            (scope, name),
        ).fetchone():
            return None, "type_parameter"
        if (
            db.execute("SELECT kind FROM symbols WHERE id=?", (scope,)).fetchone()[0]
            == "module"
        ):
            return scope, None
    return None, None


class Resolver:
    """Bounded SQLite lookups keep import targets separate from bound namespaces."""

    def __init__(self, db, owner, deadline, context=None, line=0):
        self.db, self.deadline = db, deadline
        self.active, self.steps = set(), 0
        self.limited = False
        self.collided = False
        self.mutated = False
        self.binding_reason = None
        self.transformed = None
        self.line = line
        self.binding_scopes = [(context, False, False)] if context else []
        self.scopes = []
        while owner and len(self.binding_scopes) < 64:
            tick(deadline)
            row = db.execute(
                "SELECT scope,kind FROM symbols WHERE id=?", (owner,)
            ).fetchone()
            if row is None:
                break
            lexical = not self.scopes or row[1] != "class"
            self.binding_scopes.append(
                (owner, lexical, not lexical and row[1] == "class")
            )
            if lexical:
                self.scopes.append(owner)
            owner = row[0]
        self.limited = bool(owner)

    @contextlib.contextmanager
    def guard(self, key):
        tick(self.deadline)
        self.steps += 1
        self.limited |= len(self.active) >= 64 or self.steps > 256
        allowed = key not in self.active and not self.limited
        if allowed:
            self.active.add(key)
        try:
            yield allowed
        finally:
            if allowed:
                self.active.remove(key)

    def module(self, name):
        """Find a true import target; a .py file cannot be a parent package."""
        tick(self.deadline)
        pieces = name.split(".")
        if len(pieces) > 64:
            self.limited = True
            return None
        for length in range(1, len(pieces) + 1):
            tick(self.deadline)
            prefix = ".".join(pieces[:length])
            rows = self.db.execute(
                "SELECT id,path FROM symbols WHERE module=? AND kind='module' LIMIT 2",
                (prefix,),
            ).fetchall()
            if len(rows) > 1:
                return None
            if length == len(pieces):
                return rows[0][0] if rows else None
            if rows and not rows[0][1].endswith("/__init__.py"):
                return None
            if (
                not rows
                and self.db.execute(
                    "SELECT 1 FROM files WHERE path IN (?,?) LIMIT 1",
                    (
                        prefix.replace(".", "/") + ".py",
                        prefix.replace(".", "/") + "/__init__.py",
                    ),
                ).fetchone()
            ):
                return None  # A broken/limited parent is not a namespace package.
        return None

    def module_value(self, name):
        """An import target is not proof of its current bound package attribute."""
        target = self.module(name)
        if target is None:
            return None
        pieces = name.split(".")
        for length in range(1, len(pieces)):
            tick(self.deadline)
            row = self.db.execute(
                "SELECT id FROM symbols WHERE module=? AND kind='module' LIMIT 1",
                (".".join(pieces[:length]),),
            ).fetchone()
            if row and (
                self.package_collision(row[0], pieces[length], loading=True)
                or self.written(row[0], pieces[length])
            ):
                return None
        return target

    def package_collision(self, owner, name, loading=False, potential=False):
        """Reject competing package values when child import ordering is unproved.

        A true module import identifies a source file, not the current value of
        its parent attribute (which explicit aliases can also retrieve).
        """
        tick(self.deadline)
        row = self.db.execute(
            "SELECT module,path FROM symbols WHERE id=? AND kind='module'", (owner,)
        ).fetchone()
        if row is None or not row[1].endswith("/__init__.py"):
            return False
        module, _ = row
        child = module + "." + name
        if not self.db.execute(
            "SELECT 1 FROM symbols WHERE module=? AND kind='module' LIMIT 1", (child,)
        ).fetchone():
            return False
        competing = bool(
            self.db.execute(
                "SELECT 1 FROM symbols WHERE scope=? AND lookup_name=? LIMIT 1",
                (owner, name),
            ).fetchone()
        )
        # These forms introduce the child module itself, not a competing value:
        # `import p.child as child` / `from . import child`.
        competing |= bool(
            self.db.execute(
                "SELECT 1 FROM bindings WHERE owner=? AND name IN (?, '*') "
                "AND (name='*' OR dynamic!=0 OR NOT ((member='' AND bound_module=?) "
                "OR (module=? AND member=?))) LIMIT 1",
                (owner, name, child, module, name),
            ).fetchone()
        )
        if not competing:
            return False
        if loading:
            self.collided = True
            return True
        # A caller in another file may load child before calling this package
        # global. This is possible interference, not proof of a loaded attribute;
        # only candidate rejection uses it, never positive attribute traversal.
        # The dot-to-slash range selects child.<descendants> through the index.
        if (
            potential
            and self.db.execute(
                "SELECT 1 FROM bindings WHERE dynamic=0 AND "
                "(module=? OR (module>=? AND module<?)) LIMIT 1",
                (child, child + ".", child + "/"),
            ).fetchone()
        ):
            self.collided = True
            return True
        # Merely finding child.py does not load it. Count only imports within
        # this initializer or the current caller's lexical scopes. A caller's
        # `from p import child` can retrieve the existing function, so that form
        # alone is not evidence of loading the child in the caller.
        for scope in dict.fromkeys((owner, *self.scopes)):
            tick(self.deadline)
            loading |= bool(
                self.db.execute(
                    "SELECT 1 FROM bindings WHERE owner=? AND dynamic=0 "
                    "AND (module=? OR substr(module,1,?)=? "
                    "OR (owner=? AND module=? AND member=?)) LIMIT 1",
                    (scope, child, len(child) + 1, child + ".", owner, module, name),
                ).fetchone()
            )
            if loading:
                self.collided = True
                return True
        return False

    def namespace(self, owner, name, skip=None):
        """Return (present, target); an uncertain name blocks fallback."""
        tick(self.deadline)
        if self.package_collision(owner, name) or self.written(owner, name):
            return True, None
        if self.db.execute(
            "SELECT 1 FROM bindings WHERE owner=? AND name='*' LIMIT 1", (owner,)
        ).fetchone():
            return True, None
        bindings = self.db.execute(
            "SELECT rowid FROM bindings WHERE owner=? AND name=? AND rowid!=? LIMIT 2",
            (owner, name, skip or -1),
        ).fetchall()
        definitions = self.db.execute(
            "SELECT id FROM symbols WHERE scope=? AND lookup_name=? LIMIT 2",
            (owner, name),
        ).fetchall()
        if bindings:
            return True, (
                self.candidate(self.binding(bindings[0][0]), origin=(owner, name))
                if len(bindings) == 1 and not definitions
                else None
            )
        return bool(definitions), self.candidate(
            unique(definitions), origin=(owner, name)
        )

    def candidate(self, target, require_callable=False, origin=None):
        """Classify the actual binding location and the definition's own scope.

        Package globals can be replaced by child imports even for bare lexical
        calls. Local/nested definitions have their own scope and do not share
        that package attribute. Rejection is terminal, not an outer-name retry.
        """
        tick(self.deadline)
        if (
            origin is not None
            and self.db.execute(
                "SELECT 1 FROM ineligible WHERE symbol=? AND namespace=1", (origin[0],)
            ).fetchone()
        ):
            self.transformed = "class_creation"
            return None
        if origin is not None and (
            self.package_collision(*origin, potential=True) or self.written(*origin)
        ):
            return None
        if target is None:
            return None
        transformed = self.db.execute(
            "SELECT reason FROM ineligible WHERE symbol=?", (target,)
        ).fetchone()
        if transformed:
            self.transformed = transformed[0]
            return None
        row = self.db.execute(
            "SELECT scope,lookup_name,kind FROM symbols WHERE id=?", (target,)
        ).fetchone()
        if row is None:
            return None
        owner, name, kind = row
        if kind == "module":
            return None if require_callable else target
        if self.package_collision(owner, name, potential=True) or self.written(
            owner, name
        ):
            return None
        return target

    def written(self, owner, name):
        owner = write_owner(self.db, owner, name, self.deadline)
        if self.db.execute(
            "SELECT 1 FROM mutations WHERE owner=? AND name=? LIMIT 1", (owner, name)
        ).fetchone():
            self.mutated = True
            return True
        return False

    def binding_row(self, binding):
        return self.db.execute(
            "SELECT owner,module,member,dynamic,bound_module,name "
            "FROM bindings WHERE rowid=?",
            (binding,),
        ).fetchone()

    def import_target(self, binding):
        with self.guard(("import", binding)) as allowed:
            if not allowed:
                return None
            row = self.binding_row(binding)
            if row is None or row[3] or row[2] == "*":
                return None
            _, module, member, _, _, _ = row
            target = self.module(module)
            if not member:
                return target
            if target:
                present, exported = self.namespace(target, member, skip=binding)
                if present:
                    return self.candidate(exported)
            # `from pkg import child` may load child. Ordinary attributes may not.
            return self.module(module + "." + member)

    def binding(self, binding):
        with self.guard(("binding", binding)) as allowed:
            if not allowed:
                return None
            row = self.binding_row(binding)
            if row is None or row[3]:
                return None
            if row[2]:
                target = self.import_target(binding)
            else:
                target = self.module_value(row[4]) if self.module(row[1]) else None
            return self.candidate(target, origin=(row[0], row[5]))

    def loaded_child(self, owner, module, name):
        child = module + "." + name
        target = self.module_value(child)
        if target is None:
            return None
        # Only imports in this package initializer or the caller's lexical
        # scopes establish loaded children; disk presence and unrelated callers do not.
        for scope in dict.fromkeys((owner, *self.scopes)):
            for binding, imported, member in self.db.execute(
                "SELECT rowid,module,member FROM bindings WHERE owner=? AND dynamic=0 "
                "AND (module=? OR substr(module,1,?)=? OR (module=? AND member=?))",
                (scope, child, len(child) + 1, child + ".", module, name),
            ):
                tick(self.deadline)
                if self.steps >= 256:
                    self.limited = True
                    return None
                resolved = self.import_target(binding)
                if resolved and (
                    imported != module or (member == name and resolved == target)
                ):
                    return target
        return None

    def attributes(self, target, parts):
        with self.guard(("attributes", target, tuple(parts))) as allowed:
            if not allowed or target is None:
                return None
            target = self.candidate(target)
            if target is None:
                return None
            if not parts:
                return target
            row = self.db.execute(
                "SELECT module,kind FROM symbols WHERE id=?", (target,)
            ).fetchone()
            if row is None or row[1] != "module":
                return None  # Lexical nested definitions are not function attributes.
            present, exported = self.namespace(target, parts[0])
            if not present:
                exported = self.loaded_child(target, row[0], parts[0])
            return self.attributes(exported, parts[1:])

    def bound_call(self, binding, parts):
        row = self.binding_row(binding)
        if row is None or row[3]:
            return None
        owner, module, member, _, bound, name = row
        if not member and module != bound:
            # An unaliased dotted import loads this exact path, including for
            # implicit namespace packages with no __init__.py symbol.
            suffix = module.split(".")[1:]
            if parts[: len(suffix)] == suffix:
                target = self.candidate(self.module_value(module), origin=(owner, name))
                return self.attributes(target, parts[len(suffix) :])
        return self.attributes(self.binding(binding), parts)

    def call(self, dotted):
        parts = dotted.split(".")
        scope, self.binding_reason = lookup_owner(
            self.db, self.binding_scopes, parts[0], self.deadline, self.line
        )
        if (
            scope is None
            or self.db.execute(
                "SELECT 1 FROM bindings WHERE owner=? AND name='*' LIMIT 1", (scope,)
            ).fetchone()
        ):
            return None
        bindings = self.db.execute(
            "SELECT rowid FROM bindings WHERE owner=? AND name=? LIMIT 2",
            (scope, parts[0]),
        ).fetchall()
        definitions = self.db.execute(
            "SELECT id FROM symbols WHERE scope=? AND lookup_name=? LIMIT 2",
            (scope, parts[0]),
        ).fetchall()
        if bindings:
            target = (
                self.bound_call(bindings[0][0], parts[1:])
                if len(bindings) == 1 and not definitions
                else None
            )
        else:
            target = unique(definitions) if len(parts) == 1 else None
        return self.candidate(target, require_callable=True, origin=(scope, parts[0]))


class WriteAddress(Resolver):
    """Potential imported lvalues, independent of callable/mutation eligibility.

    These addresses only invalidate values. They never establish positive
    attributes or execute source. Ambiguous import aliases are streamed rather
    than silently dropped because another binding shadows their spelling.
    """

    def owner_for(self, name):
        owner, self.binding_reason = lookup_owner(
            self.db, self.binding_scopes, name, self.deadline, self.line, potential=True
        )
        return owner

    def addresses(self, parts):
        owner = self.owner_for(parts[0])
        if owner is None:
            return
        for (binding,) in self.db.execute(
            "SELECT binding FROM write_bindings WHERE owner=? AND name=?",
            (owner, parts[0]),
        ):
            yield from self.imported(binding, parts[1:])
        if (
            self.db.execute("SELECT kind FROM symbols WHERE id=?", (owner,)).fetchone()[
                0
            ]
            == "module"
        ):
            yield from self.members(owner, parts)

    def imported(self, binding, parts):
        with self.guard(("write-import", binding, tuple(parts))) as allowed:
            if not allowed:
                return
            row = self.binding_row(binding)
            if row is None or row[3] or row[2] == "*":
                return
            _, module, member, _, bound, _ = row
            if member:
                source = self.module(module)
                if source:
                    yield from self.members(source, [member, *parts])
                else:
                    target = self.module(module + "." + member)
                    if target:
                        yield from self.members(target, parts)
            else:
                suffix = module.split(".")[1:]
                if module != bound and parts[: len(suffix)] == suffix:
                    target = self.module(module)
                    if target:
                        yield from self.members(target, parts[len(suffix) :])
                target = self.module(bound)
                if target:
                    yield from self.members(target, parts)

    def members(self, target, parts):
        with self.guard(("write-members", target, tuple(parts))) as allowed:
            if not allowed:
                return
            if not parts:
                yield target
                return
            for (binding,) in self.db.execute(
                "SELECT binding FROM write_bindings WHERE owner=? AND name=?",
                (target, parts[0]),
            ):
                yield from self.imported(binding, parts[1:])
            module = self.db.execute(
                "SELECT module FROM symbols WHERE id=?", (target,)
            ).fetchone()[0]
            child = self.module(module + "." + parts[0])
            if child:
                yield from self.members(child, parts[1:])


def rebuild_mutations(db, deadline):
    db.execute("DELETE FROM write_bindings")
    # Normalize import addresses separately from graph value eligibility. Nested
    # declared imports may write an outer binding even when their value is uncertain.
    for binding, writer, name, path in db.execute(
        "SELECT b.rowid,b.owner,b.name,s.path FROM bindings b "
        "JOIN symbols s ON b.owner=s.id WHERE b.dynamic=0"
    ):
        tick(deadline)
        owner = write_owner(db, writer, name, deadline)
        if owner:
            db.execute(
                "INSERT INTO write_bindings VALUES (?,?,?,?)",
                (path, owner, name, binding),
            )
    db.execute("DELETE FROM mutations")
    for path, writer, expr, kind, line in db.execute(
        "SELECT * FROM writes ORDER BY rowid"
    ):
        tick(deadline)
        if kind == "attribute":
            parts = expr.split(".")
            resolver = WriteAddress(db, writer, deadline, line=line)
            for owner in resolver.addresses(parts[:-1]):
                db.execute(
                    "INSERT OR IGNORE INTO mutations VALUES (?,?,?,?)",
                    (path, owner, parts[-1], line),
                )
            if resolver.limited:
                raise Failure(
                    "incomplete",
                    "Mutation address resolution exceeded its bounded depth/steps.",
                )
        else:
            owner = write_owner(db, writer, expr, deadline)
            if owner and (kind not in {"binding", "implicit"} or owner != writer):
                db.execute(
                    "INSERT OR IGNORE INTO mutations VALUES (?,?,?,?)",
                    (path, owner, expr, line),
                )


def rebuild_edges(db, deadline):
    db.execute("DELETE FROM edges WHERE kind!='contains'")
    db.execute("DELETE FROM unresolved")
    # Streaming cursor: do not materialize a whole-repository adjacency graph.
    for source, expr, kind, path, line, binding, context, lookup in db.execute(
        "SELECT * FROM refs ORDER BY rowid"
    ):
        tick(deadline)
        resolver = Resolver(db, source, deadline, context, line)
        target = (
            resolver.import_target(binding)
            if kind == "imports"
            else resolver.call(lookup)
        )
        if target is None:
            db.execute(
                "INSERT INTO unresolved VALUES (?,?,?,?,?,?)",
                (
                    source,
                    expr,
                    kind,
                    path,
                    line,
                    "resolution_limit"
                    if resolver.limited
                    else "ambiguous_package_attribute"
                    if resolver.collided
                    else resolver.transformed
                    if resolver.transformed
                    else resolver.binding_reason
                    if resolver.binding_reason
                    else "written_binding"
                    if resolver.mutated
                    else "dynamic_external_or_ambiguous",
                ),
            )
        else:
            db.execute(
                "INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?)",
                (source, target, kind, path, line),
            )


def refresh(db, root, deadline):
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for attempt in range(2):
            manifest, reasons, size = snapshot(root_fd, deadline)
            old = dict(db.execute("SELECT path,digest FROM files"))
            changed = [
                path for path, digest in manifest.items() if old.get(path) != digest
            ]
            deleted = sorted(old.keys() - manifest.keys())
            db.execute("BEGIN IMMEDIATE")
            try:
                for path in [*changed, *deleted]:
                    tick(deadline)
                    delete_graph(db, path)
                    db.execute("DELETE FROM files WHERE path=?", (path,))
                    db.execute("DELETE FROM lexical WHERE path=?", (path,))
                for path in changed:
                    tick(deadline)
                    data, reason = read_at(root_fd, path)
                    if reason or hashlib.sha256(data).hexdigest() != manifest[path]:
                        raise Failure("busy", "Workspace changed while indexing.")
                    text = data.decode("utf-8")
                    error = parse_file(db, path, text, deadline)
                    db.execute(
                        "INSERT INTO files VALUES (?,?,?,?)",
                        (path, manifest[path], text, error),
                    )
                    db.execute("INSERT INTO lexical VALUES (?,?)", (path, text))
                if changed or deleted:
                    rebuild_mutations(db, deadline)
                    rebuild_edges(db, deadline)
                after, after_reasons, after_size = snapshot(root_fd, deadline)
                if (after, after_reasons, after_size) != (manifest, reasons, size):
                    raise Failure("busy", "Workspace changed while indexing.")
                if changed or deleted:
                    db.execute(
                        "UPDATE metadata SET value=CAST(value AS INTEGER)+1 "
                        "WHERE key='generation'"
                    )
                db.commit()
                index = {
                    "generation": int(
                        db.execute(
                            "SELECT value FROM metadata WHERE key='generation'"
                        ).fetchone()[0]
                    ),
                    "reparsed_files": sum(path.endswith(".py") for path in changed),
                    "updated_files": len(changed),
                    "deleted_files": len(deleted),
                    "files": len(manifest),
                    "source_bytes": size,
                    "excluded": reasons,
                    "parse_errors": db.execute(
                        "SELECT count(*) FROM files WHERE error='parse_error'"
                    ).fetchone()[0],
                    "graph_limited_files": db.execute(
                        "SELECT count(*) FROM files WHERE error='graph_limit'"
                    ).fetchone()[0],
                    "unresolved_count": db.execute(
                        "SELECT count(*) FROM unresolved"
                    ).fetchone()[0],
                    "symbol_count": db.execute(
                        "SELECT count(*) FROM symbols"
                    ).fetchone()[0],
                    "edge_count": db.execute("SELECT count(*) FROM edges").fetchone()[
                        0
                    ],
                    "retries": attempt,
                }
                return index, (manifest, reasons, size)
            except (Failure, OSError) as exc:
                db.rollback()
                if attempt == 0 and (
                    not isinstance(exc, Failure) or exc.status == "busy"
                ):
                    continue
                raise
            except BaseException:
                db.rollback()
                raise
    finally:
        os.close(root_fd)
    raise Failure("busy", "Workspace did not stabilize.")


NODE_COLUMNS = "id,path,name,qualified_name,kind,start_line,end_line"


def node_dict(row):
    return dict(zip(NODE_COLUMNS.split(","), row, strict=True))


def get_node(db, symbol):
    row = db.execute(
        f"SELECT {NODE_COLUMNS} FROM symbols WHERE id=?", (symbol,)
    ).fetchone()
    return node_dict(row) if row else None


def path_filter(value):
    if value is None:
        return None
    parts = value.split("/")
    if not value or any(part in {"", ".", ".."} for part in parts) or "\\" in value:
        raise Failure(
            "invalid_arguments", "--path must be a workspace-relative path prefix."
        )
    return value


def search(db, query, path, limit, deadline):
    if not query or len(query) > 512 or "\0" in query:
        raise Failure(
            "invalid_arguments", "--query must contain 1 to 512 literal characters."
        )
    path = path_filter(path)
    allowed = "(? IS NULL OR path=? OR substr(path,1,length(?)+1)=?||'/')"
    params = (path, path, path, path)
    # Literal tokens are quoted individually; user text never becomes FTS syntax.
    tokens = re.findall(r"[^\W_]+", query, re.UNICODE)[:32]
    terms = " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens)
    candidates = {}
    exact_clause = (
        f"SELECT {NODE_COLUMNS} FROM symbols WHERE "
        + allowed
        + " AND (name=? OR qualified_name=? OR path=?) "
    )
    exact_params = (*params, query, query, query)
    exact_count = db.execute(
        "SELECT count(*) FROM (" + exact_clause + ")", exact_params
    ).fetchone()[0]
    for row in db.execute(
        exact_clause + "ORDER BY path,start_line,id LIMIT 21", exact_params
    ):
        candidate = node_dict(row)
        candidate["rank"] = 0 if candidate["name"] == query else 1
        candidate["score"] = 0
        candidates[candidate["id"]] = candidate
    for path_value, text in db.execute(
        "SELECT path,text FROM files WHERE path=? AND " + allowed, (query, *params)
    ):
        key = f"text:{path_value}:1"
        candidates[key] = {
            "id": key,
            "path": path_value,
            "kind": "text",
            "start_line": 1,
            "end_line": 1,
            "snippet": text.splitlines()[0][:240] if text else "",
            "rank": 1,
            "score": 0,
        }
    matched_files = 0
    if terms:
        matched_files = db.execute(
            "SELECT count(*) FROM lexical WHERE lexical MATCH ? AND " + allowed,
            (terms, *params),
        ).fetchone()[0]
        for path_value, score in db.execute(
            "SELECT path,bm25(lexical) FROM lexical WHERE lexical MATCH ? AND "
            + allowed
            + " ORDER BY bm25(lexical),path LIMIT 40",
            (terms, *params),
        ):
            tick(deadline)
            # Always include the actual matched source line for lexical text.
            text = db.execute(
                "SELECT text FROM files WHERE path=?", (path_value,)
            ).fetchone()[0]
            lines = text.splitlines()
            number = next(
                (
                    i
                    for i, line in enumerate(lines, 1)
                    if query.casefold() in line.casefold()
                ),
                None,
            )
            if number is None:
                number = next(
                    (
                        i
                        for i, line in enumerate(lines, 1)
                        if any(token.casefold() in line.casefold() for token in tokens)
                    ),
                    1,
                )
            key = f"text:{path_value}:{number}"
            candidates.setdefault(
                key,
                {
                    "id": key,
                    "path": path_value,
                    "kind": "text",
                    "start_line": number,
                    "end_line": number,
                    "snippet": lines[number - 1][:240] if lines else "",
                    "rank": 2,
                    "score": score,
                },
            )
    ordered = sorted(
        candidates.values(),
        key=lambda item: (
            item["rank"],
            item["score"],
            item["path"],
            item["start_line"],
            item["id"],
        ),
    )
    total = max(len(ordered), exact_count + matched_files)
    return {
        "results": ordered[:limit],
        "result_count": total,
        "omitted_count": max(0, total - limit),
        "incomplete": total > limit,
    }


def seeds(db, names):
    found, ambiguous = [], []
    for name in names:
        exact = get_node(db, name)
        if exact:
            found.append(exact["id"])
            continue
        rows = db.execute(
            f"SELECT {NODE_COLUMNS} FROM symbols WHERE name=? OR qualified_name=? "
            "ORDER BY path,start_line,id LIMIT 21",
            (name, name),
        ).fetchall()
        if len(rows) == 1:
            found.append(rows[0][0])
        else:
            ambiguous.append(
                {
                    "symbol": name[:512],
                    "reason": "ambiguous" if rows else "not_found",
                    "candidates": [node_dict(row) for row in rows[:20]],
                }
            )
    return sorted(set(found)), ambiguous


def edge_dict(row):
    return dict(zip(("source", "target", "kind", "path", "line"), row, strict=True))


def graph(db, args, deadline):
    names = args.symbol if args.mode == "subgraph" else [args.symbol]
    chosen, ambiguous = seeds(db, names)
    if ambiguous:
        return {
            "status": "ambiguous"
            if any(item["candidates"] for item in ambiguous)
            else "not_found",
            "ambiguities": ambiguous,
            "incomplete": True,
        }
    retained = set(chosen)
    edges = {}
    omitted = 0
    hops = args.hops if args.mode == "subgraph" else 1
    kinds = {
        "callers": "calls",
        "callees": "calls",
        "imports": "imports",
        "containment": "contains",
        "all": None,
    }
    edge_kind = kinds[args.edge_kind] if args.mode == "neighbors" else None
    frontier = chosen
    for _ in range(hops):
        next_frontier = set()
        for symbol in frontier:
            tick(deadline)
            if args.mode == "neighbors" and args.edge_kind == "callers":
                clause, parameters = "target=? AND kind='calls'", (symbol,)
            elif args.mode == "neighbors" and args.edge_kind in {"callees", "imports"}:
                clause, parameters = "source=? AND kind=?", (symbol, edge_kind)
            else:
                clause, parameters = "(source=? OR target=?)", (symbol, symbol)
                if edge_kind:
                    clause += " AND kind=?"
                    parameters += (edge_kind,)
            for row in db.execute(
                "SELECT * FROM edges WHERE "
                + clause
                + " ORDER BY kind,source,target,path,line",
                parameters,
            ):
                tick(deadline)
                target = row[1] if row[0] == symbol else row[0]
                if target not in retained:
                    if len(retained) >= (
                        args.limit if args.mode == "neighbors" else MAX_NODES
                    ):
                        omitted += 1
                        continue
                    retained.add(target)
                    next_frontier.add(target)
                if len(edges) < MAX_EDGES:
                    edges[row] = edge_dict(row)
                else:
                    omitted += 1
        frontier = sorted(next_frontier)
    if args.mode == "subgraph":
        # Return the induced graph, including edges between newly reached nodes.
        edges.clear()
        for source in sorted(retained):
            for row in db.execute(
                "SELECT * FROM edges WHERE source=? ORDER BY kind,target,path,line",
                (source,),
            ):
                tick(deadline)
                if row[1] in retained:
                    if len(edges) < MAX_EDGES:
                        edges[row] = edge_dict(row)
                    else:
                        omitted += 1
    unresolved = []
    unresolved_count = 0
    for symbol in sorted(retained):
        unresolved_count += db.execute(
            "SELECT count(*) FROM unresolved WHERE source=?", (symbol,)
        ).fetchone()[0]
        if len(unresolved) < 8:
            for row in db.execute(
                "SELECT expression,kind,path,line,reason FROM unresolved "
                "WHERE source=? ORDER BY line,expression LIMIT ?",
                (symbol, 8 - len(unresolved)),
            ):
                unresolved.append(
                    dict(
                        zip(
                            ("expression", "kind", "path", "line", "reason"),
                            row,
                            strict=True,
                        )
                    )
                )
    return {
        "nodes": [get_node(db, item) for item in sorted(retained)],
        "edges": list(edges.values()),
        "unresolved": unresolved,
        "unresolved_count": unresolved_count,
        "omitted_count": omitted,
        "incomplete": bool(omitted or unresolved_count),
    }


def bootstrap(directory, root):
    source = Path(__file__).read_bytes()
    target = directory / "search_code.py"
    if target.exists():
        validate_private_file(target)
        if target.read_bytes() != source:
            raise Failure(
                "unsafe_cache", "Persistent executable differs from source identity."
            )
    else:
        fd, name = tempfile.mkstemp(prefix="bootstrap-", dir=directory)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(source)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    return {
        "executable_path": str(target),
        "command": shlex.join(
            ["python3", str(target), "search", "--root", str(root), "--query", "QUERY"]
        ),
    }


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("invalid_arguments", message[:240])

    def exit(self, status=0, message=None):
        raise Failure(
            "help" if status == 0 else "invalid_arguments",
            message or self.format_help(),
        )

    def print_help(self, file=None):
        raise Failure("help", self.format_help())


def arguments(argv):
    parser = Parser(description=__doc__)
    subcommands = parser.add_subparsers(dest="mode", required=True, parser_class=Parser)
    for mode in ("bootstrap", "search", "neighbors", "subgraph", "status"):
        command = subcommands.add_parser(mode)
        command.add_argument("--root", required=True)
        if mode in {"bootstrap", "search"}:
            command.add_argument("--query", required=mode == "search")
            command.add_argument("--path")
            command.add_argument("--limit", type=int, default=8)
        elif mode == "neighbors":
            command.add_argument("--symbol", required=True)
            command.add_argument(
                "--edge-kind",
                choices=("all", "callers", "callees", "imports", "containment"),
                default="all",
            )
            command.add_argument("--limit", type=int, default=20)
        elif mode == "subgraph":
            command.add_argument("--symbol", required=True, action="append")
            command.add_argument("--hops", type=int, choices=(0, 1, 2), default=1)
    args = parser.parse_args(argv)
    if hasattr(args, "limit") and not 1 <= args.limit <= 20:
        raise Failure("invalid_arguments", "--limit must be between 1 and 20.")
    if hasattr(args, "symbol"):
        symbols = args.symbol if isinstance(args.symbol, list) else [args.symbol]
        if len(symbols) > 20 or any(not name or len(name) > 512 for name in symbols):
            raise Failure(
                "invalid_arguments", "Use at most 20 symbols of 1 to 512 characters."
            )
    if getattr(args, "query", None) is not None:
        if not args.query or len(args.query) > 512 or "\0" in args.query:
            raise Failure(
                "invalid_arguments", "--query must contain 1 to 512 literal characters."
            )
    if hasattr(args, "path"):
        path_filter(args.path)
    return args


def execute(args, deadline):
    root = workspace(args.root)
    directory, expected = private_directory(root)
    with writer_lock(directory, deadline):
        db = connect(directory, expected)
        try:
            db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
            index, current = refresh(db, root, deadline)
            result = {
                "status": "ok",
                "index": index,
                "omitted_count": 0,
                "unresolved_count": index["unresolved_count"],
            }
            result["incomplete"] = bool(
                index["parse_errors"]
                or index["graph_limited_files"]
                or any(
                    reason in index["excluded"]
                    for reason in (
                        "large",
                        "unreadable",
                        "file_limit",
                        "source_byte_limit",
                        "depth_limit",
                    )
                )
            )
            if args.mode == "bootstrap":
                result.update(bootstrap(directory, root))
            if args.mode == "search" or (args.mode == "bootstrap" and args.query):
                answer = search(db, args.query, args.path, args.limit, deadline)
                answer["incomplete"] |= result["incomplete"]
                result.update(answer)
            elif args.mode in {"neighbors", "subgraph"}:
                answer = graph(db, args, deadline)
                answer["incomplete"] |= result["incomplete"]
                result.update(answer)
            result["index"]["database_bytes"] = (
                (directory / "index.sqlite3").stat().st_size
            )
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                if snapshot(fd, deadline) != current:
                    raise Failure(
                        "busy", "Workspace changed while preparing the answer."
                    )
            finally:
                os.close(fd)
            tick(deadline)
            return result
        finally:
            db.close()


def serialize(result):
    """Measure the final wire representation, then drop complete entries only."""
    result.setdefault("truncated", False)
    result.setdefault("omitted_count", 0)
    result.setdefault("incomplete", False)

    def dump():
        return json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n"

    while len(dump()) > MAX_OUTPUT:
        result["truncated"] = result["incomplete"] = True
        if result.get("results"):
            result["results"].pop()
        elif result.get("unresolved"):
            result["unresolved"].pop()
        elif any(item.get("candidates") for item in result.get("ambiguities", [])):
            next(
                item
                for item in reversed(result["ambiguities"])
                if item.get("candidates")
            )["candidates"].pop()
        elif result.get("ambiguities"):
            result["ambiguities"].pop()
        elif result.get("edges"):
            result["edges"].pop()
        elif result.get("nodes"):
            removed = result["nodes"].pop()
            previous = len(result.get("edges", []))
            result["edges"] = [
                edge
                for edge in result.get("edges", [])
                if removed["id"] not in (edge["source"], edge["target"])
            ]
            result["omitted_count"] += previous - len(result["edges"])
        elif "message" in result and len(result["message"]) > 80:
            result["message"] = result["message"][:80]
        else:
            # Pathological long workspace paths can exceed the stream even with
            # no entries; fail explicitly rather than emit an unusable command.
            result = {
                "schema_version": 1,
                "mode": result.get("mode", "unknown"),
                "status": "output_limit",
                "duration_ms": result.get("duration_ms", 0),
                "truncated": True,
                "incomplete": True,
                "omitted_count": result["omitted_count"] + 1,
            }
            break
        result["omitted_count"] += 1
    return dump()


def main(argv=None):
    start = time.monotonic()
    result = {"schema_version": 1, "mode": "unknown"}
    try:
        args = arguments(sys.argv[1:] if argv is None else argv)
        result["mode"] = args.mode
        result.update(execute(args, start + DEADLINE))
    except Failure as exc:
        result.update(status=exc.status, message=str(exc)[:1200], incomplete=True)
    except sqlite3.Error as exc:
        status = "timeout" if time.monotonic() - start >= DEADLINE else "index_error"
        result.update(status=status, message=str(exc)[:240], incomplete=True)
    except (OSError, ValueError, RecursionError) as exc:
        result.update(status="unavailable", message=str(exc)[:240], incomplete=True)
    result["duration_ms"] = round((time.monotonic() - start) * 1000, 3)
    sys.stdout.write(serialize(result))
    return 0 if result.get("status") in {"ok", "help"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
