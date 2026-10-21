"""search-code:AC-2/3/4/5/6: executable source, graph and cache boundaries."""

import contextlib
import fcntl
import hashlib
import importlib.util
import io
import json
import os
import shlex
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "submission/skills/search-code/scripts/search_code.py"
)
PYTHON312 = Path("/Users/diego/.pyenv/versions/3.12.8/bin/python3.12")


@pytest.fixture
def cli(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("standalone_search_code", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(temporary))
    root = tmp_path / "workspace with spaces"
    root.mkdir()
    return module, root


def write(root, path, source):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return target


def invoke(cli, mode="status", **options):
    module, root = cli
    argv = [mode, "--root", str(root)]
    for key, value in options.items():
        for element in value if isinstance(value, list) else [value]:
            argv += ["--" + key.replace("_", "-"), str(element)]
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        module.main(argv)
    wire = output.getvalue()
    assert wire.endswith("\n") and len(wire) <= 4500
    result = json.loads(wire)
    assert result["schema_version"] == 1
    return result


def database(cli):
    module, root = cli
    directory, _ = module.private_directory(root)
    return sqlite3.connect(directory / "index.sqlite3")


@pytest.fixture(params=[sys.executable, str(PYTHON312)], ids=["python313", "python312"])
def standalone_python(request):
    assert Path(request.param).is_file(), "Required interpreter must not silently skip"
    return request.param


@pytest.fixture
def subprocess_cli(cli, standalone_python):
    """Run correctness regressions with both required real standalone interpreters."""
    module, root = cli
    interpreter = standalone_python
    # Database inspection must use the same parser-specific disposable identity
    # as the real child, without changing the host interpreter's global state.
    module.PARSER_VERSION = (
        [3, 12] if interpreter == str(PYTHON312) else list(sys.version_info[:2])
    )

    def run(mode="status", **options):
        argv = [interpreter, str(SCRIPT), mode, "--root", str(root)]
        for key, value in options.items():
            for element in value if isinstance(value, list) else [value]:
                argv += ["--" + key.replace("_", "-"), str(element)]
        child = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            env=dict(
                os.environ,
                TMPDIR=module.tempfile.gettempdir(),
                PYTHONDONTWRITEBYTECODE="1",
            ),
            timeout=45,
            check=False,
        )
        assert child.stderr == ""
        assert child.stdout.endswith("\n") and len(child.stdout) <= 4500
        result = json.loads(child.stdout)
        assert result["schema_version"] == 1
        assert child.returncode == (0 if result["status"] == "ok" else 2)
        return result

    return cli, run


def call_edges(db):
    return set(
        db.execute(
            "SELECT a.path,a.qualified_name,b.path,b.qualified_name,e.line "
            "FROM edges e JOIN symbols a ON e.source=a.id "
            "JOIN symbols b ON e.target=b.id WHERE e.kind='calls'"
        )
    )


def execute_use(root, interpreter):
    """Observe real Python import behavior in a fresh, bytecode-free process."""
    child = subprocess.run(
        [
            interpreter,
            "-c",
            "import json\ntry:\n import consumer\n value = consumer.use()\n"
            "except (AttributeError, ImportError, TypeError, NameError) as exc:\n"
            " print(json.dumps({'error': type(exc).__name__}))\n"
            "else:\n print(json.dumps({'value': value}))\n",
        ],
        cwd=root,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert child.stderr == ""
    return json.loads(child.stdout)


@pytest.mark.parametrize(
    ("initializer", "imports", "call", "target"),
    [
        pytest.param(
            "", "import pkg", "pkg.child.target", None, id="unloaded-unaliased"
        ),
        pytest.param(
            "", "import pkg as pkg", "pkg.child.target", None, id="unloaded-same-prefix"
        ),
        pytest.param(
            "", "import pkg as alias", "alias.child.target", None, id="unloaded"
        ),
        pytest.param(
            "", "import pkg.child as pkg", "pkg.target", "child", id="same-prefix-alias"
        ),
        pytest.param(
            "",
            "import pkg.child as alias",
            "alias.target",
            "child",
            id="ordinary-alias",
        ),
        pytest.param(
            "", "import pkg.child", "pkg.child.target", "child", id="unaliased-dotted"
        ),
        pytest.param(
            "", "from pkg import child", "child.target", "child", id="from-loads-child"
        ),
        pytest.param(
            "",
            "import pkg as alias\nimport pkg.child as loaded",
            "alias.child.target",
            "child",
            id="lexically-loaded-child",
        ),
        pytest.param(
            "from . import child\n",
            "import pkg as alias",
            "alias.child.target",
            "child",
            id="relative-loaded-child",
        ),
        pytest.param(
            "import pkg.child\n",
            "import pkg as alias",
            "alias.child.target",
            "child",
            id="initializer-loaded-child",
        ),
        pytest.param(
            "from .child import target\n",
            "import pkg as alias",
            "alias.child.target",
            "child",
            id="from-member-loads-child",
        ),
        pytest.param(
            "from . import child as loaded\n",
            "import pkg as alias",
            "alias.loaded.target",
            "child",
            id="module-reexport",
        ),
        pytest.param(
            "from .child import target as public\n",
            "from pkg import public as exported",
            "exported",
            "child",
            id="function-reexport",
        ),
        pytest.param(
            "from .child import target as public\n",
            "import pkg as alias",
            "alias.public",
            "child",
            id="attribute-reexport",
        ),
        pytest.param(
            "def child():\n    return 42\n",
            "import pkg as alias",
            "alias.child.target",
            None,
            id="function-collision-attribute",
        ),
        pytest.param(
            "def child():\n    return 42\n",
            "from pkg import child",
            "child",
            "package",
            id="function-collision-from",
        ),
        pytest.param(
            "def child():\n    return 42\n",
            "import pkg.child as pkg",
            "pkg.target",
            "unresolved_child",
            id="function-collision-alias",
        ),
        pytest.param(
            "def child():\n    return 42\n",
            "import pkg.child",
            "pkg.child.target",
            "unresolved_child",
            id="function-collision-dotted",
        ),
    ],
)
def test_ac4_import_binding_provenance_is_conservative(
    subprocess_cli, standalone_python, initializer, imports, call, target
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "pkg/__init__.py", initializer)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "consumer.py", imports + f"\ndef use():\n    return {call}()\n")
    result = run("neighbors", symbol="use", edge_kind="callees")
    assert result["status"] == "ok" and not result["truncated"]
    with database(cli) as db:
        if target in {None, "unresolved_child"}:
            assert result["edges"] == [] and result["incomplete"]
            assert result["unresolved_count"] == 1
            assert [item["expression"] for item in result["unresolved"]] == [call]
            assert call_edges(db) == set()
            if target == "unresolved_child":
                assert (
                    result["unresolved"][0]["reason"] == "ambiguous_package_attribute"
                )
        else:
            path, name = (
                ("pkg/child.py", "target")
                if target == "child"
                else ("pkg/__init__.py", "child")
            )
            assert not result["incomplete"] and result["unresolved_count"] == 0
            assert call_edges(db) == {
                ("consumer.py", "use", path, name, len(imports.splitlines()) + 2)
            }
    observed = execute_use(root, standalone_python)
    assert observed == (
        {"error": "AttributeError"} if target is None else {"value": 42}
    )


@pytest.mark.parametrize("load_position", ["before", "after", "caller"])
@pytest.mark.parametrize("rebind", [False, True], ids=["definition", "rebinding"])
@pytest.mark.parametrize(
    ("imports", "call", "calls_value"),
    [
        ("import pkg as alias", "alias.child", True),
        ("import pkg as alias", "alias.child.target", False),
        ("import pkg.child", "pkg.child.target", False),
        ("import pkg.child as alias", "alias.target", False),
        ("import pkg.child as pkg", "pkg.target", False),
        ("from pkg import child as alias", "alias.target", False),
        ("from pkg import child as alias", "alias", True),
        ("from bridge import exposed as alias", "alias.target", False),
    ],
    ids=[
        "parent-value",
        "parent-attribute",
        "dotted",
        "alias",
        "same-prefix-alias",
        "from-attribute",
        "from-value",
        "reexport",
    ],
)
def test_ac4_package_collisions_fail_closed_across_all_import_paths(
    subprocess_cli, standalone_python, load_position, rebind, imports, call, calls_value
):
    cli, run = subprocess_cli
    _, root = cli
    competing = "child = 7\n" if rebind else "def child():\n    return 7\n"
    load = "import pkg.child\n"
    initializer = (
        load + competing
        if load_position == "before"
        else competing + load
        if load_position == "after"
        else competing
    )
    initializer += "def safe():\n    return 11\n"
    write(root, "pkg/__init__.py", initializer)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "bridge.py", "from pkg import child as exposed\n")
    if load_position == "caller":
        imports = "import pkg.child as loaded\n" + imports
    imports += "\nimport pkg as safe_package"
    write(
        root,
        "consumer.py",
        imports + f"\ndef use():\n    return {call}()\n"
        "def keep():\n    return safe_package.safe()\n",
    )
    result = run("neighbors", symbol="use", edge_kind="callees")
    assert result["status"] == "ok" and result["incomplete"]
    assert not result["truncated"] and result["edges"] == []
    assert result["unresolved_count"] == 1
    assert [(item["expression"], item["reason"]) for item in result["unresolved"]] == [
        (call, "ambiguous_package_attribute")
    ]
    preserved = run("neighbors", symbol="keep", edge_kind="callees")
    assert not preserved["incomplete"] and len(preserved["edges"]) == 1
    with database(cli) as db:
        assert call_edges(db) == {
            (
                "consumer.py",
                "keep",
                "pkg/__init__.py",
                "safe",
                len(imports.splitlines()) + 4,
            )
        }
    if calls_value:
        expected = (
            {"value": 7}
            if load_position == "before" and not rebind
            else {"error": "TypeError"}
        )
    else:
        expected = (
            {"error": "AttributeError"} if load_position == "before" else {"value": 42}
        )
    # Both runtime outcomes are possible. The index declines either claim when
    # order would be needed to distinguish the definition from the child module.
    assert execute_use(root, standalone_python) == expected


@pytest.mark.parametrize("load_first", [False, True], ids=["load-after", "load-before"])
def test_ac4_ac5_package_collision_edits_refresh_unchanged_aliases(
    subprocess_cli, standalone_python, load_first
):
    cli, run = subprocess_cli
    _, root = cli
    load, comment = "import pkg.child\n", "#hild = 7\n"
    clean = load + comment if load_first else comment + load
    initializer = write(root, "pkg/__init__.py", clean)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(
        root,
        "consumer.py",
        "import pkg.child as alias\ndef use():\n    return alias.target()\n",
    )
    initial = run("neighbors", symbol="use", edge_kind="callees")
    assert not initial["incomplete"] and len(initial["edges"]) == 1
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["index"]["reparsed_files"] == 0
    previous = initializer.stat()
    initializer.write_text(clean.replace("#hild", "child"))
    os.utime(initializer, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    changed = run("neighbors", symbol="use", edge_kind="callees")
    assert changed["index"]["reparsed_files"] == changed["index"]["updated_files"] == 1
    assert changed["index"]["generation"] == initial["index"]["generation"] + 1
    assert changed["incomplete"] and changed["edges"] == []
    assert [(item["expression"], item["reason"]) for item in changed["unresolved"]] == [
        ("alias.target", "ambiguous_package_attribute")
    ]
    assert execute_use(root, standalone_python) == (
        {"error": "AttributeError"} if load_first else {"value": 42}
    )
    with database(cli) as db:
        assert call_edges(db) == set()
    initializer.write_text(clean)
    restored = run("neighbors", symbol="use", edge_kind="callees")
    assert restored["index"]["reparsed_files"] == 1
    assert not restored["incomplete"] and restored["unresolved_count"] == 0
    with database(cli) as db:
        assert call_edges(db) == {("consumer.py", "use", "pkg/child.py", "target", 3)}


@pytest.mark.parametrize("load_first", [False, True])
def test_ac4_true_import_target_is_distinct_from_colliding_parent_attribute(
    subprocess_cli, standalone_python, load_first
):
    cli, run = subprocess_cli
    _, root = cli
    load, definition = "import pkg.child\n", "def child():\n    return 7\n"
    write(
        root, "pkg/__init__.py", load + definition if load_first else definition + load
    )
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(
        root,
        "consumer.py",
        "from pkg.child import target as exact\ndef use():\n    return exact()\n",
    )
    result = run("neighbors", symbol="use", edge_kind="callees")
    assert not result["incomplete"] and result["unresolved_count"] == 0
    assert execute_use(root, standalone_python) == {"value": 42}
    with database(cli) as db:
        assert call_edges(db) == {("consumer.py", "use", "pkg/child.py", "target", 3)}
        assert (
            db.execute(
                "SELECT count(*) FROM edges WHERE kind='imports' AND path='consumer.py'"
            ).fetchone()[0]
            == 1
        )


@pytest.mark.parametrize("load_first", [False, True], ids=["load-after", "load-before"])
@pytest.mark.parametrize("context", ["module", "function", "nested"])
@pytest.mark.parametrize(
    "imported", [False, True], ids=["definition", "import-binding"]
)
def test_ac4_lexical_candidates_use_actual_scope_in_all_graph_views(
    subprocess_cli, standalone_python, load_first, context, imported
):
    cli, run = subprocess_cli
    _, root = cli
    definition = (
        "from .other import target as child\n"
        if imported
        else "def child():\n    return 1\n"
    )
    load = "import pkg.child\n"
    prefix = load + definition if load_first else definition + load
    bodies = {
        "module": ("child()\n", "", "1", 1),
        "function": ("def use():\n    return child()\n", "use", "pkg.use()", 2),
        "nested": (
            "def outer():\n    def inner():\n        return child()\n"
            "    return inner()\n",
            "outer.inner",
            "pkg.outer()",
            3,
        ),
    }
    body, caller_name, entry, line = bodies[context]
    line += len(prefix.splitlines())
    controls = (
        "def local():\n    def child():\n        return 2\n    return child()\n"
        "def lexical():\n    def child():\n        return 3\n"
        "    def inner():\n        return child()\n    return inner()\n"
    )
    write(root, "pkg/__init__.py", prefix + body + controls)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "pkg/other.py", "def target():\n    return 1\n")
    consumer = write(
        root, "consumer.py", f"import pkg\ndef use():\n    return {entry}\n"
    )
    assert execute_use(root, standalone_python) == (
        {"value": 1} if load_first else {"error": "TypeError"}
    )
    assert run()["status"] == "ok"
    with database(cli) as db:
        identifiers = dict(
            db.execute(
                "SELECT qualified_name,id FROM symbols WHERE path='pkg/__init__.py'"
            )
        )
        expected = {
            ("local", "local.child"),
            ("lexical.inner", "lexical.child"),
            ("lexical", "lexical.inner"),
        }
        if context == "nested":
            expected.add(("outer", "outer.inner"))
        assert {
            (source, target)
            for path, source, _, target, _ in call_edges(db)
            if path == "pkg/__init__.py"
        } == expected
    with database(cli) as db:
        child = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
            ("pkg/other.py", "target") if imported else ("pkg/__init__.py", "child"),
        ).fetchone()[0]
    caller = identifiers[caller_name]
    callees = run("neighbors", symbol=caller, edge_kind="callees")
    assert callees["edges"] == [] and callees["incomplete"]
    assert [
        (item["expression"], item["line"], item["reason"])
        for item in callees["unresolved"]
    ] == [("child", line, "ambiguous_package_attribute")]
    callers = run("neighbors", symbol=child, edge_kind="callers")
    assert callers["edges"] == []
    induced = run("subgraph", symbol=[caller, child], hops=0)
    assert induced["incomplete"]
    assert all(edge["kind"] != "calls" for edge in induced["edges"])
    assert [(item["expression"], item["reason"]) for item in induced["unresolved"]] == [
        ("child", "ambiguous_package_attribute")
    ]
    assert execute_use(root, standalone_python) == (
        {"value": 1} if load_first else {"error": "TypeError"}
    )
    for local_name, expected_target in (
        ("local", "local.child"),
        ("lexical.inner", "lexical.child"),
    ):
        positive = run("neighbors", symbol=identifiers[local_name], edge_kind="callees")
        assert not positive["incomplete"] and len(positive["edges"]) == 1
        assert positive["edges"][0]["target"] == identifiers[expected_target]
    if context != "module":
        consumer.write_text(
            "import pkg\ndef use():\n    return pkg.local() + pkg.lexical()\n"
        )
        assert execute_use(root, standalone_python) == {"value": 5}


@pytest.mark.parametrize("load_first", [False, True])
def test_ac4_ac5_lexical_collision_refresh_removes_all_views_without_losing_locals(
    subprocess_cli, standalone_python, load_first
):
    cli, run = subprocess_cli
    _, root = cli
    definition, comment = "def child():\n    return 1\n", "#mport pkg.child\n"
    clean = comment + definition if load_first else definition + comment
    clean += "def use():\n    return child()\n"
    clean += "def local():\n    def child():\n        return 2\n    return child()\n"
    initializer = write(root, "pkg/__init__.py", clean)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "consumer.py", "import pkg\ndef use():\n    return pkg.use()\n")
    first = run()
    with database(cli) as db:
        identifiers = dict(
            db.execute(
                "SELECT qualified_name,id FROM symbols WHERE path='pkg/__init__.py'"
            )
        )
    caller, child = identifiers["use"], identifiers["child"]
    initial = run("neighbors", symbol=caller, edge_kind="callees")
    assert not initial["incomplete"] and len(initial["edges"]) == 1
    assert initial["edges"][0]["target"] == child
    assert execute_use(root, standalone_python) == {"value": 1}
    assert run()["index"]["reparsed_files"] == 0
    previous = initializer.stat()
    initializer.write_text(clean.replace("#mport", "import"))
    os.utime(initializer, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    changed = run("neighbors", symbol=caller, edge_kind="callees")
    assert changed["index"]["generation"] == first["index"]["generation"] + 1
    assert changed["index"]["reparsed_files"] == changed["index"]["updated_files"] == 1
    assert changed["edges"] == [] and changed["incomplete"]
    assert changed["unresolved"][0]["reason"] == "ambiguous_package_attribute"
    assert run("neighbors", symbol=child, edge_kind="callers")["edges"] == []
    induced = run("subgraph", symbol=[caller, child], hops=0)
    assert induced["incomplete"] and induced["edges"] == []
    preserved = run("neighbors", symbol=identifiers["local"], edge_kind="callees")
    assert not preserved["incomplete"] and len(preserved["edges"]) == 1
    assert preserved["edges"][0]["target"] == identifiers["local.child"]
    assert execute_use(root, standalone_python) == (
        {"value": 1} if load_first else {"error": "TypeError"}
    )
    initializer.write_text(clean)
    restored = run("neighbors", symbol=caller, edge_kind="callees")
    assert restored["index"]["reparsed_files"] == 1
    assert not restored["incomplete"] and restored["unresolved_count"] == 0
    assert restored["edges"][0]["target"] == child
    assert (
        run("neighbors", symbol=child, edge_kind="callers")["edges"]
        == restored["edges"]
    )
    restored_induced = run("subgraph", symbol=[caller, child], hops=0)
    assert not restored_induced["incomplete"]
    assert restored_induced["edges"] == restored["edges"]


@pytest.mark.parametrize(
    "imported", [False, True], ids=["definition", "import-binding"]
)
def test_ac4_consumer_loading_cannot_fabricate_package_global_call(
    subprocess_cli, standalone_python, imported
):
    cli, run = subprocess_cli
    _, root = cli
    definition = (
        "from .other import target as child\n"
        if imported
        else "def child():\n    return 1\n"
    )
    write(
        root, "pkg/__init__.py", definition + "def package_use():\n    return child()\n"
    )
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "pkg/other.py", "def target():\n    return 1\n")
    source = "import pkg\nimport pkg.child\ndef use():\n    return pkg.package_use()\n"
    consumer = write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    callees = run("neighbors", symbol="package_use", edge_kind="callees")
    assert callees["edges"] == [] and callees["incomplete"]
    assert [(item["expression"], item["reason"]) for item in callees["unresolved"]] == [
        ("child", "ambiguous_package_attribute")
    ]
    previous = consumer.stat()
    consumer.write_text(source.replace("import pkg.child", "#mport pkg.child"))
    os.utime(consumer, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    restored = run("neighbors", symbol="package_use", edge_kind="callees")
    assert (
        restored["index"]["reparsed_files"] == restored["index"]["updated_files"] == 1
    )
    assert not restored["incomplete"] and len(restored["edges"]) == 1
    assert execute_use(root, standalone_python) == {"value": 1}
    consumer.write_text(source)
    loaded = run("neighbors", symbol="package_use", edge_kind="callees")
    assert loaded["index"]["reparsed_files"] == 1
    assert loaded["incomplete"] and loaded["edges"] == []


@pytest.mark.parametrize("reexport", [False, True], ids=["loaded-child", "reexport"])
def test_ac4_ac5_import_edits_refresh_unchanged_dependents(
    subprocess_cli, standalone_python, reexport
):
    cli, run = subprocess_cli
    _, root = cli
    before = (
        "from .child import target as public\n" if reexport else "#rom . import child\n"
    )
    after = (
        "from .other import target as public\n" if reexport else "from . import child\n"
    )
    initializer = write(root, "pkg/__init__.py", before)
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "pkg/other.py", "def target():\n    return 99\n")
    call = "alias.public" if reexport else "alias.child.target"
    write(
        root, "consumer.py", f"import pkg as alias\ndef use():\n    return {call}()\n"
    )
    initial = run("neighbors", symbol="use", edge_kind="callees")
    assert execute_use(root, standalone_python) == (
        {"value": 42} if reexport else {"error": "AttributeError"}
    )
    with database(cli) as db:
        assert call_edges(db) == (
            {("consumer.py", "use", "pkg/child.py", "target", 3)} if reexport else set()
        )
    assert run()["index"]["reparsed_files"] == 0
    stat_before = initializer.stat()
    assert len(before) == len(after)
    initializer.write_text(after)
    os.utime(initializer, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))
    changed = run("neighbors", symbol="use", edge_kind="callees")
    assert changed["index"]["reparsed_files"] == changed["index"]["updated_files"] == 1
    assert changed["index"]["generation"] == initial["index"]["generation"] + 1
    assert not changed["incomplete"] and changed["unresolved_count"] == 0
    expected_path = "pkg/other.py" if reexport else "pkg/child.py"
    with database(cli) as db:
        assert call_edges(db) == {("consumer.py", "use", expected_path, "target", 3)}
    assert execute_use(root, standalone_python) == {"value": 99 if reexport else 42}
    initializer.write_text(before)
    restored = run("neighbors", symbol="use", edge_kind="callees")
    assert restored["index"]["reparsed_files"] == 1
    assert restored["incomplete"] is (not reexport)
    with database(cli) as db:
        assert call_edges(db) == (
            {("consumer.py", "use", "pkg/child.py", "target", 3)} if reexport else set()
        )
    if not reexport:
        assert [item["expression"] for item in restored["unresolved"]] == [call]


def test_ac4_cyclic_reexports_and_unrelated_loads_remain_unresolved(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "pkg/__init__.py", "from bridge import public\n")
    write(root, "bridge.py", "from pkg import public\n")
    write(root, "pkg/child.py", "def target():\n    return 42\n")
    write(root, "unrelated.py", "import pkg.child\n")
    write(
        root, "consumer.py", "from pkg import public\ndef use():\n    return public()\n"
    )
    result = run("neighbors", symbol="use", edge_kind="callees")
    assert result["incomplete"] and result["edges"] == []
    assert [item["expression"] for item in result["unresolved"]] == ["public"]
    assert execute_use(root, standalone_python) == {"error": "ImportError"}
    write(root, "pkg/__init__.py", "")
    write(
        root,
        "consumer.py",
        "import pkg as alias\ndef use():\n    return alias.child.target()\n",
    )
    unloaded = run("neighbors", symbol="use", edge_kind="callees")
    assert unloaded["incomplete"] and unloaded["edges"] == []
    assert [item["expression"] for item in unloaded["unresolved"]] == [
        "alias.child.target"
    ]
    assert execute_use(root, standalone_python) == {"error": "AttributeError"}
    with database(cli) as db:
        assert call_edges(db) == set()


def test_ac4_reexport_limits_are_explicit_and_deadline_is_enforced(subprocess_cli):
    cli, run = subprocess_cli
    module, root = cli
    for index in range(40):
        write(root, f"link{index}.py", f"from link{index + 1} import target\n")
    write(root, "link40.py", "def target():\n    return 42\n")
    consumer = write(
        root, "consumer.py", "from link0 import target\ndef use():\n    target()\n"
    )
    limited = run("neighbors", symbol="use", edge_kind="callees")
    assert limited["edges"] == [] and limited["incomplete"]
    assert [(item["expression"], item["reason"]) for item in limited["unresolved"]] == [
        ("target", "resolution_limit")
    ]
    consumer.write_text("from link35 import target\ndef use():\n    target()\n")
    bounded = run("neighbors", symbol="use", edge_kind="callees")
    assert bounded["index"]["reparsed_files"] == 1
    assert not bounded["incomplete"] and len(bounded["edges"]) == 1
    with database(cli) as db:
        owner = db.execute("SELECT id FROM symbols WHERE name='use'").fetchone()[0]
        resolver = module.Resolver(db, owner, time.monotonic() + 10)
        resolver.deadline = time.monotonic() - 1
        with pytest.raises(module.Failure, match="deadline") as exc:
            resolver.call("target")
        assert exc.value.status == "timeout"


def test_ac3_reserved_directory_components_and_refresh(subprocess_cli):
    cli, run = subprocess_cli
    _, root = cli
    reserved = (
        "solution",
        "solutions",
        "reference",
        "references",
        "test_patch",
        "ground_truth",
        "test-patch",
        "ground-truth",
        "solution.extra",
        "reference-copy",
        "test_patch_extra",
        "ground_truth-copy",
    )
    for name in reserved:
        for prefix, component in (("", name), ("nested/deep/", name.upper())):
            write(
                root,
                f"{prefix}{component}/hidden.py",
                "def forbidden_marker():\n    return forbidden_marker()\n",
            )
    write(root, "solutionary.py", "def visible():\n    pass\n")
    write(root, "ground_truthful.py", "from solutionary import visible\nvisible()\n")
    write(root, "safe/hidden.py", "def relocate_target():\n    pass\n")
    write(
        root,
        "consumer.py",
        "from safe.hidden import relocate_target\n"
        "def consumer():\n    relocate_target()\n",
    )
    result = run("search", query="forbidden_marker")
    assert result["results"] == []
    assert result["index"]["excluded"]["excluded_directory"] == 2 * len(reserved)
    assert run("neighbors", symbol="forbidden_marker")["status"] == "not_found"
    expected_files = {
        "solutionary.py",
        "ground_truthful.py",
        "safe/hidden.py",
        "consumer.py",
    }
    with database(cli) as db:
        assert {
            row[0] for row in db.execute("SELECT path FROM files")
        } == expected_files
        assert {
            row[0] for row in db.execute("SELECT DISTINCT path FROM symbols")
        } == expected_files
        assert call_edges(db) == {
            ("ground_truthful.py", "", "solutionary.py", "visible", 2),
            ("consumer.py", "consumer", "safe/hidden.py", "relocate_target", 3),
        }
    assert run("search", query="relocate_target", path="safe")["results"]
    assert run()["index"]["reparsed_files"] == 0
    hidden = root / "nested/SoLuTiOn"
    (root / "safe").rename(hidden)
    moved = run("neighbors", symbol="consumer", edge_kind="callees")
    assert moved["index"]["reparsed_files"] == 0
    assert moved["index"]["deleted_files"] == 1
    assert moved["edges"] == [] and moved["incomplete"]
    assert [item["expression"] for item in moved["unresolved"]] == ["relocate_target"]
    assert run("search", query="relocate_target", path="nested")["results"] == []
    with database(cli) as db:
        assert {row[0] for row in db.execute("SELECT path FROM files")} == (
            expected_files - {"safe/hidden.py"}
        )
        assert call_edges(db) == {
            ("ground_truthful.py", "", "solutionary.py", "visible", 2)
        }
    hidden.rename(root / "safe")
    restored = run("neighbors", symbol="consumer", edge_kind="callees")
    assert restored["index"]["reparsed_files"] == 1
    assert not restored["incomplete"] and len(restored["edges"]) == 1


def test_ac4_exports_require_static_module_members_not_function_attributes(
    subprocess_cli,
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "leaf.py", "def leaf():\n    pass\n")
    write(root, "wild.py", "def wildcard_target():\n    pass\nfrom external import *\n")
    write(
        root,
        "nested.py",
        "def outer():\n    def inner():\n        pass\n    return inner()\n"
        "class Container:\n    def method(self):\n        pass\n",
    )
    # A discoverable module with the same spelling cannot make outer.inner a
    # supported attribute of the function exported by nested.py.
    write(root, "nested/outer.py", "def inner():\n    pass\n")
    write(
        root,
        "consumer.py",
        "import wild\nimport nested\nfrom wild import wildcard_target as imported\n"
        "from nested import outer as factory\nfrom leaf import leaf as alias\n"
        "import leaf as module\nfrom nested import Container as ClassAlias\n"
        "def run():\n    wild.wildcard_target()\n    imported()\n"
        "    nested.outer.inner()\n    factory.inner()\n"
        "    nested.Container.method()\n    ClassAlias.method()\n"
        "    module.leaf()\n    alias()\n    nested.outer()\n    ClassAlias()\n",
    )
    result = run("neighbors", symbol="run", edge_kind="callees")
    negative = {
        "wild.wildcard_target",
        "imported",
        "nested.outer.inner",
        "factory.inner",
        "nested.Container.method",
        "ClassAlias.method",
    }
    assert result["incomplete"] and not result["truncated"]
    assert result["unresolved_count"] == len(negative)
    assert {item["expression"] for item in result["unresolved"]} == negative
    with database(cli) as db:
        assert call_edges(db) == {
            ("nested.py", "outer", "nested.py", "outer.inner", 4),
            ("consumer.py", "run", "leaf.py", "leaf", 15),
            ("consumer.py", "run", "leaf.py", "leaf", 16),
            ("consumer.py", "run", "nested.py", "outer", 17),
            ("consumer.py", "run", "nested.py", "Container", 18),
        }
        assert set(
            db.execute(
                "SELECT expression,kind FROM unresolved WHERE path='consumer.py'"
            )
        ) == {(name, "calls") for name in negative} | {
            ("wild.wildcard_target", "imports")
        }
        assert set(
            db.execute(
                "SELECT b.path,b.qualified_name FROM edges e "
                "JOIN symbols b ON b.id=e.target "
                "WHERE e.kind='imports' AND e.path='consumer.py'"
            )
        ) == {
            ("wild.py", ""),
            ("nested.py", ""),
            ("nested.py", "outer"),
            ("leaf.py", "leaf"),
            ("leaf.py", ""),
            ("nested.py", "Container"),
        }


def test_ac4_ac5_wildcard_export_edits_refresh_unchanged_dependents(subprocess_cli):
    cli, run = subprocess_cli
    _, root = cli
    static = "def target():\n    pass\n#rom external import *\n"
    provider = write(root, "provider.py", static)
    write(
        root,
        "consumer.py",
        "import provider\nfrom provider import target\n"
        "def use():\n    provider.target()\n    target()\n",
    )
    initial = run("neighbors", symbol="use", edge_kind="callees")
    assert not initial["incomplete"] and len(initial["edges"]) == 2
    assert run()["index"]["reparsed_files"] == 0
    before = provider.stat()
    provider.write_text(static.replace("#rom", "from"))
    os.utime(provider, ns=(before.st_atime_ns, before.st_mtime_ns))
    changed = run("neighbors", symbol="use", edge_kind="callees")
    assert changed["index"]["generation"] == initial["index"]["generation"] + 1
    assert changed["index"]["reparsed_files"] == changed["index"]["updated_files"] == 1
    assert changed["edges"] == [] and changed["incomplete"]
    assert {item["expression"] for item in changed["unresolved"]} == {
        "provider.target",
        "target",
    }
    with database(cli) as db:
        assert call_edges(db) == set()
        assert set(db.execute("SELECT expression,kind FROM unresolved")) == {
            ("external.*", "imports"),
            ("provider.target", "imports"),
            ("provider.target", "calls"),
            ("target", "calls"),
        }
    provider.write_text(static)
    restored = run("neighbors", symbol="use", edge_kind="callees")
    assert restored["index"]["reparsed_files"] == 1
    assert not restored["incomplete"] and restored["unresolved_count"] == 0
    with database(cli) as db:
        assert call_edges(db) == {
            ("consumer.py", "use", "provider.py", "target", 4),
            ("consumer.py", "use", "provider.py", "target", 5),
        }


def test_ac4_ac5_pattern_captures_shadow_in_own_scope_and_refresh(subprocess_cli):
    cli, run = subprocess_cli
    _, root = cli
    source = (
        "def captured_target():\n    pass\n"
        "def star_target():\n    pass\n"
        "def rest_target():\n    pass\n"
        "def alias_target():\n    pass\n"
        "def match_as(value):\n    match value:\n"
        '        case {"key": captured_target} if captured_target():\n'
        "            captured_target()\n"
        "async def match_star(value):\n    match value:\n"
        "        case [*star_target]:\n            star_target()\n"
        "def match_rest(value):\n    match value:\n"
        "        case {**rest_target}:\n            rest_target()\n"
        "def match_alias(value):\n    match value:\n"
        "        case [item] as alias_target:\n            alias_target()\n"
        "def outside():\n    captured_target()\n    star_target()\n"
        "    rest_target()\n    alias_target()\n"
    )
    path = write(root, "patterns.py", source)
    expected_outside = {
        ("patterns.py", "outside", "patterns.py", target, line)
        for target, line in (
            ("captured_target", 26),
            ("star_target", 27),
            ("rest_target", 28),
            ("alias_target", 29),
        )
    }
    expected_unresolved = {
        ("captured_target", 11),
        ("captured_target", 12),
        ("star_target", 16),
        ("rest_target", 20),
        ("alias_target", 24),
    }
    first = run("neighbors", symbol="match_as", edge_kind="callees")
    assert first["incomplete"] and first["edges"] == []
    assert first["unresolved_count"] == 2
    assert {item["line"] for item in first["unresolved"]} == {11, 12}
    with database(cli) as db:
        assert call_edges(db) == expected_outside
        assert set(db.execute("SELECT expression,line FROM unresolved")) == (
            expected_unresolved
        )
    assert run()["index"]["reparsed_files"] == 0
    # Remove captures of the outer definitions: the same calls become static.
    unshadowed = source.replace('"key": captured_target', '"key": local_value')
    unshadowed = unshadowed.replace("[*star_target]", "[*local_value]")
    unshadowed = unshadowed.replace("{**rest_target}", "{**local_value}")
    unshadowed = unshadowed.replace("as alias_target:", "as local_value:")
    path.write_text(unshadowed)
    unbound = run("neighbors", symbol="match_as", edge_kind="callees")
    assert unbound["index"]["reparsed_files"] == 1
    assert not unbound["incomplete"] and len(unbound["edges"]) == 2
    with database(cli) as db:
        assert call_edges(db) == expected_outside | {
            ("patterns.py", owner, "patterns.py", target, line)
            for owner, target, line in (
                ("match_as", "captured_target", 11),
                ("match_as", "captured_target", 12),
                ("match_star", "star_target", 16),
                ("match_rest", "rest_target", 20),
                ("match_alias", "alias_target", 24),
            )
        }
        assert db.execute("SELECT count(*) FROM unresolved").fetchone()[0] == 0
    path.write_text(source)
    rebound = run("neighbors", symbol="match_as", edge_kind="callees")
    assert rebound["index"]["reparsed_files"] == 1
    assert rebound["edges"] == [] and rebound["incomplete"]
    with database(cli) as db:
        assert call_edges(db) == expected_outside
        assert set(db.execute("SELECT expression,line FROM unresolved")) == (
            expected_unresolved
        )


def test_ac3_literal_search_exact_symbols_locations_and_text(cli):
    _, root = cli
    write(
        root,
        "pkg/api.py",
        "class Client:\n    async def fetch(self):\n        return 1\n",
    )
    write(root, "notes.txt", 'Literal AND OR NEAR quote" * token\n')
    found = invoke(cli, "search", query="fetch")
    assert found["status"] == "ok"
    first = found["results"][0]
    assert (first["path"], first["qualified_name"], first["kind"]) == (
        "pkg/api.py",
        "Client.fetch",
        "async_function",
    )
    assert (first["start_line"], first["end_line"]) == (2, 3)
    assert invoke(cli, "search", query='AND OR NEAR quote" *')["status"] == "ok"
    text = invoke(cli, "search", query="Literal")
    assert text["results"][0]["path"] == "notes.txt"
    assert invoke(cli, "search", query="notes.txt")["results"][0]["start_line"] == 1
    assert invoke(cli, "search", query="notes.txt", path="pkg")["results"] == []
    assert invoke(cli, "search", query="fetch", path="notes.txt")["results"] == []
    assert invoke(cli, "search", query="fetch", path="pkg")["results"]


def test_ac3_duplicate_identity_and_no_suffix_resolution(cli):
    _, root = cli
    write(root, "a.py", "def same():\n    pass\ndef same():\n    pass\n")
    write(root, "b.py", "async def same():\n    pass\n")
    result = invoke(cli, "neighbors", symbol="same")
    assert result["status"] == "ambiguous"
    nodes = result["ambiguities"][0]["candidates"]
    assert len(nodes) == len({item["id"] for item in nodes}) == 3
    assert invoke(cli, "neighbors", symbol="a.same")["status"] == "not_found"
    assert invoke(cli, "neighbors", symbol=nodes[0]["id"])["status"] == "ok"


def test_ac4_exact_nested_async_relative_alias_edges(cli):
    _, root = cli
    write(root, "p/__init__.py", "")
    write(root, "p/a.py", "async def leaf():\n    return 1\n")
    write(
        root,
        "p/b.py",
        "from .a import leaf as go\ndef outer():\n    async def inner():\n"
        "        return await go()\n    return inner()\n",
    )
    assert invoke(cli)["status"] == "ok"
    with database(cli) as db:
        pairs = set(
            db.execute(
                "SELECT a.qualified_name,b.qualified_name,e.kind,a.path,b.path "
                "FROM edges e JOIN symbols a ON e.source=a.id "
                "JOIN symbols b ON e.target=b.id"
            )
        )
        assert pairs == {
            ("", "leaf", "contains", "p/a.py", "p/a.py"),
            ("", "outer", "contains", "p/b.py", "p/b.py"),
            ("outer", "outer.inner", "contains", "p/b.py", "p/b.py"),
            ("", "leaf", "imports", "p/b.py", "p/a.py"),
            ("outer.inner", "leaf", "calls", "p/b.py", "p/a.py"),
            ("outer", "outer.inner", "calls", "p/b.py", "p/b.py"),
        }
    callers = invoke(cli, "neighbors", symbol="leaf", edge_kind="callers")
    assert [edge["kind"] for edge in callers["edges"]] == ["calls"]
    assert {node["qualified_name"] for node in callers["nodes"]} == {
        "leaf",
        "outer.inner",
    }
    imports = invoke(cli, "neighbors", symbol="p/b.py", edge_kind="imports")
    assert len(imports["edges"]) == 1 and imports["edges"][0]["kind"] == "imports"
    induced = invoke(cli, "subgraph", symbol="outer", hops=1)
    assert {node["qualified_name"] for node in induced["nodes"]} == {
        "",
        "outer",
        "outer.inner",
    }
    assert {edge["kind"] for edge in induced["edges"]} == {"contains", "calls"}
    seed_only = invoke(cli, "subgraph", symbol=["outer", "outer.inner"], hops=0)
    assert len(seed_only["edges"]) == 2  # Calls plus containment: induced at zero hops.


def test_ac4_module_alias_calls_and_dynamic_shadowing(cli):
    _, root = cli
    write(root, "p/__init__.py", "")
    write(root, "p/a.py", "def leaf():\n    pass\n")
    write(
        root,
        "b.py",
        "import p.a as mod\nimport p.a\ndef go():\n    mod.leaf()\n    p.a.leaf()\n",
    )
    write(
        root,
        "c.py",
        "def leaf():\n    pass\ndef shadow(leaf):\n    leaf()\ndef assigned():\n"
        "    leaf = lambda: 1\n    leaf()\ndef dynamic(obj):\n    obj.leaf()\n"
        "from p.a import *\n",
    )
    assert invoke(cli)["status"] == "ok"
    with database(cli) as db:
        calls = list(
            db.execute(
                "SELECT path,line FROM edges WHERE kind='calls' ORDER BY path,line"
            )
        )
        assert calls == [("b.py", 4), ("b.py", 5)]
        assert (
            db.execute("SELECT count(*) FROM unresolved WHERE path='c.py'").fetchone()[
                0
            ]
            >= 4
        )


def test_ac5_equal_stat_edit_add_delete_rename_and_dependent_resolution(cli):
    _, root = cli
    leaf = write(root, "a.py", "def leaf():\n    return 1\n")
    write(root, "b.py", "from a import leaf\ndef go():\n    return leaf()\n")
    first = invoke(cli)["index"]
    warm = invoke(cli)["index"]
    assert warm["generation"] == first["generation"]
    assert warm["reparsed_files"] == warm["updated_files"] == 0
    before = leaf.stat()
    leaf.write_text("def dead():\n    return 1\n")
    os.utime(leaf, ns=(before.st_atime_ns, before.st_mtime_ns))
    changed = invoke(cli)["index"]
    assert changed["reparsed_files"] == changed["updated_files"] == 1
    assert changed["generation"] == first["generation"] + 1
    with database(cli) as db:
        assert (
            db.execute(
                "SELECT count(*) FROM edges WHERE kind IN ('calls','imports')"
            ).fetchone()[0]
            == 0
        )
        assert (
            db.execute("SELECT count(*) FROM unresolved WHERE path='b.py'").fetchone()[
                0
            ]
            == 2
        )
    write(root, "a.py", "def leaf():\n    return 1\n")
    assert invoke(cli)["index"]["reparsed_files"] == 1
    with database(cli) as db:
        assert (
            db.execute("SELECT count(*) FROM edges WHERE kind='calls'").fetchone()[0]
            == 1
        )
    leaf.rename(root / "renamed.py")
    renamed = invoke(cli)["index"]
    assert (renamed["reparsed_files"], renamed["deleted_files"]) == (1, 1)
    (root / "renamed.py").unlink()
    assert invoke(cli)["index"]["deleted_files"] == 1


def test_ac5_parse_error_keeps_current_text_without_stale_graph(cli):
    _, root = cli
    write(root, "a.py", "def leaf():\n    pass\n")
    write(root, "b.py", "from a import leaf\ndef go():\n    leaf()\n")
    invoke(cli)
    write(root, "a.py", "def leaf(: # broken_current_token\n")
    result = invoke(cli, "search", query="broken_current_token")
    assert result["incomplete"] and result["index"]["parse_errors"] == 1
    assert result["results"][0]["path"] == "a.py"
    with database(cli) as db:
        assert (
            db.execute("SELECT count(*) FROM symbols WHERE path='a.py'").fetchone()[0]
            == 0
        )
        assert (
            db.execute(
                "SELECT count(*) FROM edges WHERE kind IN ('calls','imports')"
            ).fetchone()[0]
            == 0
        )


@pytest.mark.parametrize("damage", ["corrupt", "schema", "interrupted"])
def test_ac5_disposable_cache_recovery(cli, damage):
    module, root = cli
    write(root, "a.py", "def recover():\n    pass\n")
    invoke(cli)
    directory, _ = module.private_directory(root)
    if damage == "corrupt":
        (directory / "index.sqlite3").write_bytes(b"not a database")
    elif damage == "schema":
        with database(cli) as db:
            db.execute("UPDATE metadata SET value='0' WHERE key='schema'")
    else:
        db = database(cli)
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM symbols")
        db.close()  # Uncommitted, interrupted transaction rolls back.
    answer = invoke(cli, "search", query="recover")
    assert answer["status"] == "ok"
    assert answer["results"][0]["name"] == "recover"


def test_ac5_concurrent_modification_rolls_back_then_recovers(cli, monkeypatch):
    module, root = cli
    target = write(root, "a.py", "def old():\n    pass\n")
    first = invoke(cli)["index"]["generation"]
    target.write_text("def new():\n    pass\n")
    original = module.snapshot
    calls = 0

    def unstable(*args):
        nonlocal calls
        result = original(*args)
        calls += 1
        if calls % 2 == 0:
            return {}, {}, 0
        return result

    monkeypatch.setattr(module, "snapshot", unstable)
    assert invoke(cli)["status"] == "busy"
    with database(cli) as db:
        assert (
            int(
                db.execute(
                    "SELECT value FROM metadata WHERE key='generation'"
                ).fetchone()[0]
            )
            == first
        )
        assert (
            db.execute("SELECT name FROM symbols WHERE kind='function'").fetchone()[0]
            == "old"
        )
    monkeypatch.setattr(module, "snapshot", original)
    assert invoke(cli, "search", query="new")["results"][0]["name"] == "new"


def test_ac5_writer_lock_is_bounded(cli, monkeypatch):
    module, root = cli
    directory, _ = module.private_directory(root)
    monkeypatch.setattr(module, "LOCK_WAIT", 0.05)
    with (directory / "writer.lock").open("w") as stream:
        os.chmod(stream.name, 0o600)
        fcntl.flock(stream, fcntl.LOCK_EX)
        start = time.monotonic()
        assert invoke(cli)["status"] == "busy"
        assert time.monotonic() - start < 0.5
    assert invoke(cli)["status"] == "ok"


def test_ac5_edit_during_answer_is_busy_instead_of_stale(cli, monkeypatch):
    module, root = cli
    write(root, "a.py", "def old():\n    pass\n")
    original = module.search

    def changing(*args):
        answer = original(*args)
        write(root, "a.py", "def new():\n    pass\n")
        return answer

    monkeypatch.setattr(module, "search", changing)
    result = invoke(cli, "search", query="old")
    assert result["status"] == "busy" and "results" not in result
    monkeypatch.setattr(module, "search", original)
    assert invoke(cli, "search", query="new")["results"][0]["name"] == "new"


def test_ac3_omitted_search_counts_cover_matches_beyond_candidate_window(cli):
    _, root = cli
    for index in range(55):
        write(root, f"docs/{index:02}.txt", "needle\n")
    result = invoke(cli, "search", query="needle", limit=2)
    assert result["result_count"] == 55
    assert result["omitted_count"] == 53
    assert len(result["results"]) == 2 and result["incomplete"]


def test_ac4_ambiguous_module_and_wildcard_never_fabricate_calls(cli):
    _, root = cli
    write(root, "a.py", "def leaf():\n    pass\n")
    write(root, "a/__init__.py", "def leaf():\n    pass\n")
    write(root, "b.py", "from a import leaf\ndef go():\n    leaf()\n")
    write(root, "c.py", "def local():\n    pass\nfrom unknown import *\nlocal()\n")
    invoke(cli)
    with database(cli) as db:
        assert (
            db.execute("SELECT count(*) FROM edges WHERE kind='calls'").fetchone()[0]
            == 0
        )
        assert (
            db.execute("SELECT count(*) FROM unresolved WHERE kind='calls'").fetchone()[
                0
            ]
            == 2
        )


def test_ac6_dense_ast_limit_is_explicit_and_preserves_lexical_source(cli, monkeypatch):
    module, root = cli
    write(root, "a.py", "def needle():\n    return 1\n")
    monkeypatch.setattr(module, "MAX_AST_TOKENS", 3)
    result = invoke(cli, "search", query="needle")
    assert result["incomplete"] and result["index"]["graph_limited_files"] == 1
    assert result["index"]["parse_errors"] == 0
    assert result["results"][0]["kind"] == "text"


def test_ac6_graph_bounds_and_induced_edges(cli):
    _, root = cli
    source = "def seed():\n" + "".join(f"    f{i}()\n" for i in range(45))
    source += "".join(f"def f{i}():\n    pass\n" for i in range(45))
    write(root, "a.py", source)
    result = invoke(cli, "subgraph", symbol="seed", hops=2)
    assert len(result["nodes"]) <= 40 and len(result["edges"]) <= 80
    assert result["incomplete"] and result["omitted_count"] > 0
    retained = {node["id"] for node in result["nodes"]}
    assert all(
        edge["source"] in retained and edge["target"] in retained
        for edge in result["edges"]
    )


def test_ac3_exclusions_symlinks_binary_and_file_limits(cli, monkeypatch):
    module, root = cli
    write(root, "good.py", "visible = 'needle'\n")
    for name in (
        ".git/config",
        "venv/a.py",
        "vendor/a.py",
        "resources/graph.json",
        "solutions/a.py",
        "task.json",
        "test_patch.py",
        "reference.txt",
        "data.patch",
    ):
        write(root, name, "forbiddenneedle")
    (root / "binary.bin").write_bytes(b"needle\0")
    (root / "invalid.txt").write_bytes(b"\xff")
    write(root, "large.txt", "x" * 128)
    write(root.parent, "outside.py", "outside_secret = 1")
    (root / "escape.py").symlink_to(root.parent / "outside.py")
    (root / "escape_dir").symlink_to(root.parent, target_is_directory=True)
    monkeypatch.setattr(module, "MAX_FILE", 100)
    result = invoke(cli, "search", query="forbiddenneedle")
    assert result["results"] == []
    counts = result["index"]["excluded"]
    assert (
        counts["symlink"] == 2
        and counts["binary"] == counts["non_utf8"] == counts["large"] == 1
    )
    assert result["incomplete"]
    monkeypatch.setattr(module, "MAX_FILES", 0)
    assert invoke(cli)["index"]["excluded"]["file_limit"] > 0
    monkeypatch.setattr(module, "MAX_FILES", 50000)
    monkeypatch.setattr(module, "MAX_BYTES", 1)
    assert invoke(cli)["index"]["excluded"]["source_byte_limit"] > 0


def test_ac2_cache_identity_private_modes_and_symlink_rejection(cli):
    module, root = cli
    invoke(cli)
    directory, _ = module.private_directory(root)
    other = root.parent / "other"
    other.mkdir()
    other_dir, _ = module.private_directory(other)
    assert directory != other_dir
    with database(cli) as db:
        db.execute(
            "UPDATE metadata SET value=? WHERE key='workspace'",
            (json.dumps(str(other)),),
        )
    assert invoke(cli)["status"] == "unsafe_cache"
    (directory / "index.sqlite3").unlink()
    (directory / "index.sqlite3").symlink_to(root / "unwritten")
    assert invoke(cli)["status"] == "unsafe_cache"
    (directory / "index.sqlite3").unlink()
    directory.chmod(0o755)
    assert invoke(cli)["status"] == "unsafe_cache"
    directory.chmod(0o700)
    alias = root.parent / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(module.Failure, match="symlink"):
        module.workspace(str(alias))
    with pytest.raises(module.Failure, match="absolute"):
        module.workspace("relative")


def test_ac2_foreign_cache_owner_fails_closed(cli, monkeypatch):
    module, root = cli
    invoke(cli)
    monkeypatch.setattr(module.os, "getuid", lambda: os.stat(root).st_uid + 1)
    # The directory created under the simulated identity still has the real UID.
    assert invoke(cli)["status"] == "unsafe_cache"


@pytest.mark.parametrize(
    "options",
    [
        ["search", "--query", ""],
        ["search", "--query", "x" * 513],
        ["search", "--query", "x", "--path", "../bad"],
        ["search", "--query", "x", "--path", "/absolute"],
        ["search", "--query", "x", "--limit", "21"],
        ["search", "--query", "x", "--limit", "x"],
        ["subgraph", "--symbol", "x", "--hops", "3"],
        ["neighbors", "--symbol", "x", "--edge-kind", "fake"],
        ["unrecognized"],
        ["--help"],
    ],
)
def test_ac6_arguments_are_bounded_json_with_empty_stderr(cli, capsys, options):
    module, root = cli
    module.main([*options, "--root", str(root)])
    captured = capsys.readouterr()
    assert captured.err == "" and len(captured.out) <= 4500
    assert json.loads(captured.out)["status"] in {"invalid_arguments", "help"}


def test_ac6_json_truncation_drops_whole_entries_and_no_dangling_edges(cli):
    module, _ = cli
    nodes = [{"id": str(i), "path": "é" * 500, "start_line": i} for i in range(40)]
    edges = [
        {"source": str(i), "target": str(i + 1), "kind": "calls"} for i in range(39)
    ]
    result = json.loads(
        module.serialize(
            {"schema_version": 1, "mode": "subgraph", "nodes": nodes, "edges": edges}
        )
    )
    assert result["truncated"] and result["incomplete"] and result["omitted_count"] > 0
    retained = {node["id"] for node in result["nodes"]}
    assert all(
        edge["source"] in retained and edge["target"] in retained
        for edge in result["edges"]
    )


def test_ac6_deadline_and_fts5_capability(cli, monkeypatch):
    module, _ = cli
    monkeypatch.setattr(module, "DEADLINE", -1)
    assert invoke(cli)["status"] == "timeout"

    class MissingFTS:
        def executescript(self, ddl):
            raise sqlite3.OperationalError("no such module: fts5")

    with pytest.raises(module.Failure, match="FTS5.*grep") as exc:
        module.initialize(MissingFTS(), {})
    assert exc.value.status == "unavailable"


@pytest.mark.parametrize("interpreter", [sys.executable, str(PYTHON312)])
def test_ac2_real_bootstrap_persists_exact_source_and_second_command(cli, interpreter):
    _, root = cli
    assert Path(interpreter).is_file(), "Required interpreter must not silently skip"
    write(root, "hello.py", "async def visible():\n    return 1\n")
    transient = root.parent / "transient skill"
    transient.mkdir()
    script = transient / "search_code.py"
    script.write_bytes(SCRIPT.read_bytes())
    temporary = root.parent / "subprocess temp"
    temporary.mkdir()
    env = dict(os.environ, TMPDIR=str(temporary), PYTHONDONTWRITEBYTECODE="1")
    first = subprocess.run(
        [
            interpreter,
            str(script),
            "bootstrap",
            "--root",
            str(root),
            "--query",
            "visible",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=True,
        timeout=45,
    )
    result = json.loads(first.stdout)
    assert first.stderr == "" and len(first.stdout) <= 4500
    assert result["results"][0]["name"] == "visible"
    executable = Path(result["executable_path"])
    assert root not in executable.parents
    assert (
        hashlib.sha256(executable.read_bytes()).digest()
        == hashlib.sha256(SCRIPT.read_bytes()).digest()
    )
    command = shlex.split(result["command"])
    assert command[1] == str(executable) and command[-1] == "QUERY"
    script.unlink()
    transient.rmdir()
    command[0], command[-1] = interpreter, "visible"
    second = subprocess.run(
        command,
        cwd=root.parent,
        text=True,
        capture_output=True,
        env=env,
        check=True,
        timeout=45,
    )
    assert (
        second.stderr == ""
        and json.loads(second.stdout)["index"]["reparsed_files"] == 0
    )
    assert sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    ) == ["hello.py"]


def assert_written_views(
    cli,
    run,
    caller_name,
    target_name,
    expression,
    path="consumer.py",
    target_path=None,
    reason="written_binding",
):
    """AC4: forward/reverse/induced views agree on an invalidated callable."""
    with database(cli) as db:
        caller = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
            (path, caller_name),
        ).fetchone()[0]
        target = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
            (target_path or path, target_name),
        ).fetchone()[0]
        assert not db.execute(
            "SELECT 1 FROM edges WHERE source=? AND target=? AND kind='calls'",
            (caller, target),
        ).fetchone()
    forward = run("neighbors", symbol=caller, edge_kind="callees")
    assert forward["incomplete"]
    assert (expression, reason) in {
        (u["expression"], u["reason"]) for u in forward["unresolved"]
    }
    reverse = run("neighbors", symbol=target, edge_kind="callers")
    assert all(e["source"] != caller for e in reverse["edges"])
    graph = run("subgraph", symbol=[caller, target], hops=0)
    assert graph["incomplete"]
    assert all(e["kind"] != "calls" or e["target"] != target for e in graph["edges"])
    assert (expression, reason) in {
        (u["expression"], u["reason"]) for u in graph["unresolved"]
    }


@pytest.mark.parametrize(
    "operation,error",
    [("alias.target = 7", "TypeError"), ("del alias.target", "AttributeError")],
)
@pytest.mark.parametrize(
    "imports,access",
    [
        ("import provider as alias", "provider.target"),
        ("import provider as provider\nalias = provider", "provider.target"),
        ("from pkg import provider as alias", "pkg.provider.target"),
        ("from bridge import alias", "provider.target"),
    ],
)
def test_ac4_imported_attribute_writes_are_owned_by_provider(
    subprocess_cli, standalone_python, operation, error, imports, access
):
    cli, run = subprocess_cli
    _, root = cli
    package = access.startswith("pkg.")
    provider = "pkg/provider.py" if package else "provider.py"
    write(root, provider, "def target():\n    return 42\ndef safe():\n    return 11\n")
    write(root, "pkg/__init__.py", "")
    write(root, "bridge.py", "import provider as alias\n")
    # The second route explicitly reuses the import name rather than inferring
    # arbitrary assignment aliases, which remain outside static import support.
    if imports.startswith("import provider as provider"):
        operation = operation.replace("alias.", "provider.")
    write(root, "mutator.py", imports + "\n" + operation + "\n")
    load = "import pkg.provider" if package else "import provider"
    write(
        root,
        "consumer.py",
        f"import mutator\n"
        f"{load}\n"
        f"def use():\n"
        f"    return {access}()\n"
        f"def positive():\n"
        f"    return {access.rsplit('.', 1)[0]}.safe()\n",
    )
    assert execute_use(root, standalone_python) == {"error": error}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, "use", "target", access, target_path=provider)
    with database(cli) as db:
        assert ("consumer.py", "positive", provider, "safe", 6) in call_edges(db)
        assert db.execute(
            "SELECT DISTINCT path FROM mutations WHERE name='target'"
        ).fetchall() == [("mutator.py",)]


@pytest.mark.parametrize(
    "body",
    [
        "[target := 7 for x in [1]]",
        "{target := 7 for x in [1]}",
        "{x: (target := 7) for x in [1]}",
        "list(target := 7 for x in [1])",
        "[[target := 7 for y in [1]] for x in [1]]",
        "[(lambda value=(target := 7): value) for x in [1]]",
    ],
)
def test_ac4_comprehension_walrus_uses_containing_owner(
    subprocess_cli, standalone_python, body
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        "def target():\n    return 42\ndef use():\n    "
        + body
        + "\n    return target()\n",
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, "use", "target", "target")


@pytest.mark.parametrize(
    "body",
    [
        "[target for target in [7]]",
        "[[target for target in [7]] for x in [1]]",
        "[(lambda: (target := 7))() for x in [1]]",
        "[provider.target for provider in []]",
    ],
)
def test_ac4_comprehension_iteration_and_lambda_locals_preserve_outer(
    subprocess_cli, standalone_python, body
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        "def target():\n    return 42\ndef use():\n    "
        + body
        + "\n    return target()\n",
    )
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert ("consumer.py", "use", "consumer.py", "target", 5) in call_edges(db)
        assert not db.execute("SELECT 1 FROM mutations WHERE name='target'").fetchone()


@pytest.mark.parametrize("declaration", ["global", "nonlocal"])
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize(
    "mutation,error",
    [
        ("target = 7", "TypeError"),
        ("del target", "NameError"),
        ("def target():\n    return 99", None),
        ("from other import replacement as target", None),
        (
            "try:\n    raise ValueError()\nexcept ValueError as target:\n    pass",
            "NameError",
        ),
        ("match 7:\n    case target:\n        pass", "TypeError"),
    ],
)
def test_ac4_declared_writes_use_actual_outer_owner(
    subprocess_cli, standalone_python, declaration, nested, mutation, error
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "other.py", "def replacement():\n    return 99\n")
    target = "def target():\n    return 42\n"
    changer = (
        "def change():\n    "
        + declaration
        + " target\n"
        + "".join("    " + line + "\n" for line in mutation.splitlines())
    )
    if nested:
        changer = (
            "def dispatch():\n"
            + "".join("    " + line + "\n" for line in changer.splitlines())
            + "    change()\n"
        )
    entry = "dispatch" if nested else "change"
    source = target + changer + f"def use():\n    {entry}()\n    return target()\n"
    caller, old = "use", "target"
    if declaration == "nonlocal":
        source = (
            "def use():\n"
            + "".join("    " + line + "\n" for line in (target + changer).splitlines())
            + f"    {entry}()\n    return target()\n"
        )
        old = "use.target"
    write(root, "consumer.py", source)
    if error == "NameError" and declaration == "nonlocal":
        error = "UnboundLocalError"
    assert execute_use(root, standalone_python) == (
        {"error": error} if error else {"value": 99}
    )
    assert run()["status"] == "ok"
    assert_written_views(cli, run, caller, old, "target")
    with database(cli) as db:
        assert any(
            a == "use" and b == ("use." if declaration == "nonlocal" else "") + entry
            for _, a, _, b, _ in call_edges(db)
        )


@pytest.mark.parametrize("declaration", ["global", "nonlocal"])
@pytest.mark.parametrize("body", ["return target()", "target = 7\nreturn 11"])
def test_ac4_readonly_declarations_and_local_writes_preserve_outer(
    subprocess_cli, standalone_python, declaration, body
):
    cli, run = subprocess_cli
    _, root = cli
    readonly = body.startswith("return")
    inner = (
        "def read():\n"
        + (f"    {declaration} target\n" if readonly else "")
        + "".join("    " + line + "\n" for line in body.splitlines())
    )
    definition = "def target():\n    return 42\n"
    source = definition + inner + "def use():\n    read()\n    return target()\n"
    target, reader = "target", "read"
    if declaration == "nonlocal":
        source = (
            "def use():\n"
            + "".join(
                "    " + line + "\n" for line in (definition + inner).splitlines()
            )
            + "    read()\n    return target()\n"
        )
        target, reader = "use.target", "use.read"
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    with database(cli) as db:
        pairs = {(a, b) for _, a, _, b, _ in call_edges(db)}
        assert ("use", target) in pairs
        if readonly:
            assert (reader, target) in pairs


@pytest.mark.parametrize("declaration", ["global", "nonlocal"])
def test_ac4_declared_import_lvalue_addresses_remain_independent(
    subprocess_cli, standalone_python, declaration
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 42\n")
    mutation = (
        f"def change():\n"
        f"    {declaration} alias\n"
        f"    import provider as alias\n"
        f"    alias.target = 7\n"
    )
    if declaration == "nonlocal":
        mutation = (
            "def outer():\n    alias = None\n"
            + "".join("    " + line + "\n" for line in mutation.splitlines())
            + "    change()\nouter()\n"
        )
    else:
        mutation += "change()\n"
    write(root, "mutator.py", mutation)
    write(
        root,
        "consumer.py",
        "import mutator\nimport provider\ndef use():\n    return provider.target()\n",
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, "use", "target", "provider.target", target_path="provider.py"
    )


@pytest.mark.parametrize("kind", ["attribute", "global", "nonlocal", "walrus"])
def test_ac4_ac5_equal_stat_write_removal_restoration_and_provenance(
    subprocess_cli, standalone_python, kind
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 42\n")
    if kind == "attribute":
        source = "import provider\n#rovider.target=7\n"
        active = source.replace("#rovider", "provider")
        consumer = (
            "import mutator\n"
            "from provider import target\n"
            "def use():\n"
            "    return target()\n"
        )
        target_path, target_name = "provider.py", "target"
    elif kind == "walrus":
        source = (
            "def target():\n"
            "    return 42\n"
            "def use():\n"
            "    pass;#target:=7 for x in [1]]\n"
            "    return target()\n"
        )
        active = source.replace("pass;#", "[     ")
        consumer = "from mutator import use\n"
        target_path, target_name = "mutator.py", "target"
    else:
        source = (
            "def target():\n"
            "    return 42\n"
            "def change():\n"
            "    global target\n"
            "    pass;#arget=7\n"
            "def use():\n"
            "    change()\n"
            "    return target()\n"
        )
        if kind == "nonlocal":
            source = (
                "def use():\n"
                "    def target():\n"
                "        return 42\n"
                "    def change():\n"
                "        nonlocal target\n"
                "        pass;#arget=7\n"
                "    change()\n"
                "    return target()\n"
            )
        active = source.replace("pass;#arget", "target     ")
        consumer = "from mutator import use\n"
        target_path, target_name = (
            "mutator.py",
            "use.target" if kind == "nonlocal" else "target",
        )
    assert len(source) == len(active)
    mutator = write(root, "mutator.py", source)
    write(root, "consumer.py", consumer)
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    for text, written in [
        (active, True),
        (source, False),
        (active, True),
        (source, False),
    ]:
        stat = mutator.stat()
        mutator.write_text(text)
        os.utime(mutator, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        assert execute_use(root, standalone_python) == (
            {"error": "TypeError"} if written else {"value": 42}
        )
        result = run()
        assert result["status"] == "ok" and result["index"]["reparsed_files"] == 1
        with database(cli) as db:
            edges = call_edges(db)
            assert any(
                p == target_path and name == target_name for _, _, p, name, _ in edges
            ) == (not written)
            assert (
                bool(
                    db.execute(
                        "SELECT 1 FROM mutations WHERE path='mutator.py' "
                        "AND name='target'"
                    ).fetchone()
                )
                == written
            )
    if kind == "attribute":
        mutator.write_text(active)
        assert run()["index"]["reparsed_files"] == 1
        mutator.rename(root / "renamed.py")
        write(root, "consumer.py", consumer.replace("mutator", "renamed"))
        result = run()
        assert (
            result["index"]["reparsed_files"] == 2
            and result["index"]["deleted_files"] == 1
        )
        assert execute_use(root, standalone_python) == {"error": "TypeError"}
        with database(cli) as db:
            assert db.execute(
                "SELECT DISTINCT path FROM mutations WHERE name='target'"
            ).fetchall() == [("renamed.py",)]
        (root / "renamed.py").unlink()
        write(root, "consumer.py", consumer.replace("import mutator\n", ""))
        assert run()["index"]["deleted_files"] == 1
        assert execute_use(root, standalone_python) == {"value": 42}
        with database(cli) as db:
            assert not db.execute("SELECT 1 FROM mutations").fetchone()


@pytest.mark.parametrize("route", ["ordinary", "same-prefix", "dotted", "from-package"])
@pytest.mark.parametrize("delete", [False, True])
def test_ac4_module_attribute_lvalues_cover_import_identities(
    subprocess_cli, standalone_python, route, delete
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "pkg/__init__.py", "")
    write(root, "pkg/provider.py", "def target():\n    return 42\n")
    imports, alias = {
        "ordinary": ("import pkg.provider as alias", "alias"),
        "same-prefix": ("import pkg.provider as pkg", "pkg"),
        "dotted": ("import pkg.provider", "pkg.provider"),
        "from-package": ("from pkg import provider as alias", "alias"),
    }[route]
    operation = f"del {alias}.target" if delete else f"{alias}.target = 7"
    write(root, "mutator.py", imports + "\n" + operation + "\n")
    write(
        root,
        "consumer.py",
        "import mutator\n"
        "import pkg.provider\n"
        "def use():\n"
        "    return pkg.provider.target()\n",
    )
    assert execute_use(root, standalone_python) == {
        "error": "AttributeError" if delete else "TypeError"
    }
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, "use", "target", "pkg.provider.target", target_path="pkg/provider.py"
    )
    with database(cli) as db:
        assert db.execute(
            "SELECT 1 FROM edges e JOIN symbols t ON e.target=t.id "
            "WHERE e.kind='imports' AND t.path='pkg/provider.py'"
        ).fetchone()


@pytest.mark.parametrize(
    "operation",
    ["fn.note = 7", "fn.note = 7\ndel fn.note", "[alias.target for alias in []]"],
)
def test_ac4_member_object_and_comprehension_locals_do_not_write_provider(
    subprocess_cli, standalone_python, operation
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 42\n")
    write(
        root,
        "consumer.py",
        "from provider import target as fn\nimport provider as alias\n"
        + operation
        + "\ndef use():\n    return fn()\n",
    )
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(
            a == "use" and p == "provider.py" and b == "target"
            for _, a, p, b, _ in call_edges(db)
        )
        assert not db.execute("SELECT 1 FROM mutations WHERE name='target'").fetchone()


@pytest.mark.parametrize(
    "form", ["[value for alias.target in [7]]", "[alias.target for value in [1]]"]
)
def test_ac4_comprehension_attribute_store_distinguishes_reads(
    subprocess_cli, standalone_python, form
):
    cli, run = subprocess_cli
    _, root = cli
    # Store into an imported module attribute is a write even when the ordinary
    # comprehension name is local; an attribute Load is not a mutation.
    form = form.replace("[value for", "[0 for")
    write(root, "provider.py", "def target():\n    return 42\n")
    write(
        root,
        "consumer.py",
        "import provider as alias\n"
        + form
        + "\ndef use():\n    return alias.target()\n",
    )
    mutated = "alias.target in" in form
    assert execute_use(root, standalone_python) == (
        {"error": "TypeError"} if mutated else {"value": 42}
    )
    assert run()["status"] == "ok"
    if mutated:
        assert_written_views(
            cli, run, "use", "target", "alias.target", target_path="provider.py"
        )
    else:
        with database(cli) as db:
            assert any(a == "use" and b == "target" for _, a, _, b, _ in call_edges(db))


def test_ac4_lambda_default_walrus_has_containing_owner(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        "def target():\n    return 42\ndef use():\n"
        "    callback = lambda value=(target := 7): value\n    return target()\n",
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, "use", "target", "target")


@pytest.mark.parametrize("parameter", ["T", "*T", "**T"])
@pytest.mark.parametrize(
    "context",
    [
        "function",
        "async",
        "nested-function",
        "class-method",
        "class-dictionary",
        "nested-class",
        "function-class",
    ],
)
def test_ac4_generic_type_bindings_block_outer_callables(
    subprocess_cli, standalone_python, parameter, context
):
    cli, run = subprocess_cli
    _, root = cli
    prefix = "def T():\n    return 42\ndef safe():\n    return 11\n"
    cases = {
        "function": (f"def use[{parameter}]():\n    safe()\n    return T()\n", "use"),
        "async": (
            (
                f"async def typed[{parameter}]():\n"
                f"    safe()\n"
                f"    return T()\n"
                f"import asyncio\n"
                f"def use():\n"
                f"    return asyncio.run(typed())\n"
            ),
            "typed",
        ),
        "nested-function": (
            (
                f"def use[{parameter}]():\n"
                f"    def inner():\n"
                f"        safe()\n"
                f"        return T()\n"
                f"    return inner()\n"
            ),
            "use.inner",
        ),
        "class-method": (
            (
                f"class Box[{parameter}]:\n"
                f"    def method(self):\n"
                f"        safe()\n"
                f"        return T()\n"
                f"def use():\n"
                f"    return Box().method()\n"
            ),
            "Box.method",
        ),
        "class-dictionary": (
            (
                f"class Box[{parameter}]:\n"
                f"    def T():\n"
                f"        return 99\n"
                f"    def method(self):\n"
                f"        safe()\n"
                f"        return T()\n"
                f"def use():\n"
                f"    return Box().method()\n"
            ),
            "Box.method",
        ),
        "nested-class": (
            (
                f"class Box[{parameter}]:\n"
                f"    class Inner:\n"
                f"        def method(self):\n"
                f"            safe()\n"
                f"            return T()\n"
                f"def use():\n"
                f"    return Box.Inner().method()\n"
            ),
            "Box.Inner.method",
        ),
        "function-class": (
            (
                f"def use[{parameter}]():\n"
                f"    class Box:\n"
                f"        def method(self):\n"
                f"            safe()\n"
                f"            return T()\n"
                f"    return Box().method()\n"
            ),
            "use.Box.method",
        ),
    }
    source, caller = cases[context]
    write(root, "consumer.py", prefix + source)
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, caller, "T", "T", reason="type_parameter")
    with database(cli) as db:
        assert any(a == caller and b == "safe" for _, a, _, b, _ in call_edges(db))
        assert (
            db.execute("SELECT count(*) FROM type_bindings WHERE name='T'").fetchone()[
                0
            ]
            == 1
        )


@pytest.mark.parametrize(
    "context",
    [
        "local-def",
        "local-import",
        "enclosing-local",
        "global",
        "ordinary-class",
        "class-body",
        "unrelated-type",
    ],
)
def test_ac4_generic_nearest_bindings_and_class_namespace_controls(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 99\n")
    cases = {
        "local-def": (
            "def use[T]():\n    def T():\n        return 99\n    return T()\n",
            "use",
            "consumer.py",
            "use.T",
            99,
        ),
        "local-import": (
            "def use[T]():\n    from provider import target as T\n    return T()\n",
            "use",
            "provider.py",
            "target",
            99,
        ),
        "enclosing-local": (
            (
                "def use[T]():\n"
                "    def T():\n"
                "        return 99\n"
                "    def inner():\n"
                "        return T()\n"
                "    return inner()\n"
            ),
            "use.inner",
            "consumer.py",
            "use.T",
            99,
        ),
        "global": (
            "def use[T]():\n    global T\n    return T()\n",
            "use",
            "consumer.py",
            "T",
            42,
        ),
        "ordinary-class": (
            (
                "class Box:\n"
                "    def T():\n"
                "        return 99\n"
                "    def method(self):\n"
                "        return T()\n"
                "def use():\n"
                "    return Box().method()\n"
            ),
            "Box.method",
            "consumer.py",
            "T",
            42,
        ),
        "class-body": (
            (
                "class Box[T]:\n"
                "    def T():\n"
                "        return 99\n"
                "    value = T()\n"
                "def use():\n"
                "    return Box.value\n"
            ),
            "Box",
            "consumer.py",
            "Box.T",
            99,
        ),
        "unrelated-type": (
            "def use[U]():\n    return T()\n",
            "use",
            "consumer.py",
            "T",
            42,
        ),
    }
    source, caller, target_path, target, value = cases[context]
    write(root, "consumer.py", "def T():\n    return 42\n" + source)
    assert execute_use(root, standalone_python) == {"value": value}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(
            a == caller and p == target_path and b == target
            for _, a, p, b, _ in call_edges(db)
        )
        identifier = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
            ("consumer.py", caller),
        ).fetchone()[0]
    result = run("neighbors", symbol=identifier, edge_kind="callees")
    assert not result["incomplete"] and len(result["edges"]) == 1


@pytest.mark.parametrize("context", ["function-default", "decorator", "class-base"])
def test_ac4_generic_evaluation_contexts_use_correct_binding_frame(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    cases = {
        "function-default": (
            (
                "def T():\n"
                "    return 42\n"
                "def generic[T](value=T()):\n"
                "    return value\n"
                "def use():\n"
                "    return generic()\n"
            ),
            {"value": 42},
            False,
        ),
        "decorator": (
            "def T(value):\n    return value\n@T\ndef use[T]():\n    return T()\n",
            {"error": "TypeError"},
            False,
        ),
        "class-base": (
            (
                "def T():\n"
                "    return object\n"
                "class Box[T](T()):\n"
                "    pass\n"
                "def use():\n"
                "    return 42\n"
            ),
            {"error": "TypeError"},
            True,
        ),
    }
    source, actual, blocked = cases[context]
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == actual
    assert run()["status"] == "ok"
    if blocked:
        assert_written_views(cli, run, "", "T", "T", reason="type_parameter")
    elif context == "function-default":
        with database(cli) as db:
            assert any(a == "" and b == "T" for _, a, _, b, _ in call_edges(db))
    else:
        assert_written_views(cli, run, "use", "T", "T", reason="type_parameter")


@pytest.mark.parametrize("context", ["type-alias", "alias-name", "bound", "default"])
def test_ac4_lazy_annotation_scopes_are_conservative(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    if context == "default" and standalone_python == str(PYTHON312):
        # Type-parameter defaults were added in 3.13; 3.12 must report the actual
        # parse failure and current lexical source instead of stale graph data.
        source = "def T():\n    return 42\ndef use[T = T()]():\n    return 11\n"
        write(root, "consumer.py", source)
        assert run()["index"]["parse_errors"] == 1
        return
    cases = {
        "type-alias": (
            "type Alias[T] = T()\ndef use():\n    return Alias.__value__\n",
            "<type_alias>",
            "",
        ),
        "alias-name": ("type T = int\ndef use():\n    return T()\n", "T", "use"),
        "bound": (
            (
                "def generic[T: T()]():\n"
                "    pass\n"
                "def use():\n"
                "    return generic.__type_params__[0].__bound__\n"
            ),
            "<type_parameter_bound>",
            "generic",
        ),
        "default": (
            (
                "def generic[T = T()]():\n"
                "    pass\n"
                "def use():\n"
                "    return generic.__type_params__[0].__default__\n"
            ),
            "<type_parameter_default_value>",
            "generic",
        ),
    }
    source, expression, owner = cases[context]
    write(root, "consumer.py", "def T():\n    return 42\n" + source)
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert not any(b == "T" for _, _, _, b, _ in call_edges(db))
        assert db.execute(
            "SELECT expression FROM unresolved u JOIN symbols s ON u.source=s.id "
            "WHERE s.qualified_name=? AND u.expression=?",
            (owner, expression),
        ).fetchone()


@pytest.mark.parametrize("context", ["function", "class"])
def test_ac4_ac5_generic_scope_equal_stat_refresh_and_dependents(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    if context == "function":
        plain = "def T():\n    return 42\ndef use   ():\n    return T()\n"
        generic = plain.replace("use   ", "use[T]")
        caller = "use"
        consumer = "from provider import use\n"
    else:
        plain = (
            "def T():\n"
            "    return 42\n"
            "class Box   :\n"
            "    def method(self):\n"
            "        return T()\n"
        )
        generic = plain.replace("Box   ", "Box[T]")
        caller = "Box.method"
        consumer = "from provider import Box\ndef use():\n    return Box().method()\n"
    provider = write(root, "provider.py", plain)
    write(root, "consumer.py", consumer)
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    for source, blocked in [
        (generic, True),
        (plain, False),
        (generic, True),
        (plain, False),
    ]:
        stat = provider.stat()
        provider.write_text(source)
        os.utime(provider, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        assert execute_use(root, standalone_python) == (
            {"error": "TypeError"} if blocked else {"value": 42}
        )
        result = run()
        assert result["status"] == "ok" and result["index"]["reparsed_files"] == 1
        with database(cli) as db:
            edges = call_edges(db)
            assert any(a == caller and b == "T" for _, a, _, b, _ in edges) == (
                not blocked
            )
            assert bool(db.execute("SELECT 1 FROM type_bindings").fetchone()) == blocked
        if blocked:
            assert_written_views(
                cli, run, caller, "T", "T", path="provider.py", reason="type_parameter"
            )
    provider.rename(root / "renamed.py")
    write(root, "consumer.py", consumer.replace("provider", "renamed"))
    result = run()
    assert (
        result["index"]["reparsed_files"] == 2 and result["index"]["deleted_files"] == 1
    )
    assert execute_use(root, standalone_python) == {"value": 42}
    (root / "renamed.py").unlink()
    assert run()["index"]["deleted_files"] == 1
    with database(cli) as db:
        assert not db.execute("SELECT 1 FROM type_bindings").fetchone()
        assert not db.execute(
            "SELECT 1 FROM edges e JOIN symbols t ON e.target=t.id "
            "WHERE t.path IN ('provider.py','renamed.py')"
        ).fetchone()


@pytest.mark.parametrize(
    "definition",
    [
        "def target():\n    return 42\n",
        "async def target():\n    return 42\n",
        "class target:\n    pass\n",
    ],
)
@pytest.mark.parametrize("route", ["direct", "nested", "alias", "module", "reexport"])
def test_ac4_decorated_definition_identity_is_not_binding_identity(
    subprocess_cli, standalone_python, definition, route
):
    cli, run = subprocess_cli
    _, root = cli
    prefix = "def replace(value):\n    return 7\ndef safe():\n    return 11\n"
    if route == "nested":
        source = (
            prefix
            + "def use():\n"
            + "".join(
                "    " + line + "\n"
                for line in ("@replace\n" + definition).splitlines()
            )
            + "    safe()\n    return target()\n"
        )
        target, path, expr = "use.target", "consumer.py", "target"
    elif route == "direct":
        source = (
            prefix
            + "@replace\n"
            + definition
            + "def use():\n    safe()\n    return target()\n"
        )
        target, path, expr = "target", "consumer.py", "target"
    else:
        write(root, "provider.py", prefix + "@replace\n" + definition)
        write(root, "bridge.py", "from provider import target as exported\n")
        imports, expr = {
            "alias": (
                "from provider import target as alias\nfrom provider import safe\n",
                "alias",
            ),
            "module": (
                "import provider as alias\nfrom provider import safe\n",
                "alias.target",
            ),
            "reexport": (
                "from bridge import exported as alias\nfrom provider import safe\n",
                "alias",
            ),
        }[route]
        source = imports + "def use():\n    safe()\n    return " + expr + "()\n"
        target, path = "target", "provider.py"
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, "use", target, expr, target_path=path, reason="decorated_binding"
    )
    with database(cli) as db:
        assert any(a == "use" and b == "safe" for _, a, _, b, _ in call_edges(db))
        assert db.execute(
            "SELECT 1 FROM symbols WHERE path=? AND qualified_name=?", (path, target)
        ).fetchone()


@pytest.mark.parametrize(
    "name",
    [
        "__module__",
        "__qualname__",
        "__doc__",
        "__annotations__",
        "__type_params__",
        "__firstlineno__",
    ],
)
def test_ac4_compiler_class_namespace_blocks_outer_fallback(
    subprocess_cli, standalone_python, name
):
    cli, run = subprocess_cli
    _, root = cli
    doc = '    "class doc"\n' if name == "__doc__" else ""
    parameter = "[T]" if name == "__type_params__" else ""
    annotation = "    x: int\n" if name == "__annotations__" else ""
    source = (
        (
            f"def {name}():\n"
            f"    return 42\n"
            f"def safe():\n"
            f"    return 11\n"
            f"class Box{parameter}:\n"
        )
        + doc
        + "    safe()\n    value = "
        + name
        + "()\n"
        + annotation
        + "def use():\n    return Box.value\n"
    )
    write(root, "consumer.py", source)
    blocked = name != "__firstlineno__" or standalone_python != str(PYTHON312)
    assert execute_use(root, standalone_python) == (
        {"error": "TypeError"} if blocked else {"value": 42}
    )
    assert run()["status"] == "ok"
    if blocked:
        assert_written_views(
            cli, run, "Box", name, name, reason="implicit_class_binding"
        )
    with database(cli) as db:
        assert any(a == "Box" and b == "safe" for _, a, _, b, _ in call_edges(db))
        assert any(a == "Box" and b == name for _, a, _, b, _ in call_edges(db)) == (
            not blocked
        )


@pytest.mark.parametrize(
    "context", ["method", "nested-method", "nested-class-body", "class-in-method"]
)
def test_ac4_class_cell_does_not_resolve_outer_function(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    cases = {
        "method": (
            (
                "class Box:\n"
                "    def method(self):\n"
                "        return __class__()\n"
                "def use():\n"
                "    return type(Box().method()).__name__\n"
            ),
            "Box.method",
            {"value": "Box"},
        ),
        "nested-method": (
            (
                "class Box:\n"
                "    def method(self):\n"
                "        def inner():\n"
                "            return __class__()\n"
                "        return inner()\n"
                "def use():\n"
                "    return type(Box().method()).__name__\n"
            ),
            "Box.method.inner",
            {"value": "Box"},
        ),
        "nested-class-body": (
            (
                "class Box:\n"
                "    class Inner:\n"
                "        value = __class__()\n"
                "def use():\n"
                "    return 42\n"
            ),
            "Box.Inner",
            {"error": "NameError"},
        ),
        "class-in-method": (
            (
                "class Box:\n"
                "    def method(self):\n"
                "        class Inner:\n"
                "            value = __class__()\n"
                "        return Inner.value\n"
                "def use():\n"
                "    return type(Box().method()).__name__\n"
            ),
            "Box.method.Inner",
            {"value": "Box"},
        ),
    }
    source, caller, actual = cases[context]
    write(root, "consumer.py", "def __class__():\n    return 42\n" + source)
    assert execute_use(root, standalone_python) == actual
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, caller, "__class__", "__class__", reason="implicit_class_binding"
    )


@pytest.mark.parametrize(
    "context",
    [
        "body",
        "default",
        "global",
        "local",
        "enclosing-local",
        "docless",
        "unannotated",
        "explicit-def",
        "explicit-import",
        "global-annotations",
    ],
)
def test_ac4_implicit_class_bindings_preserve_actual_explicit_and_outer_bindings(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 99\n")
    cases = {
        "body": (
            "__class__",
            "class Box:\n    value = __class__()\ndef use():\n    return Box.value\n",
            "Box",
            "__class__",
            42,
        ),
        "default": (
            "__class__",
            (
                "class Box:\n"
                "    def method(self, value=__class__()):\n"
                "        return value\n"
                "def use():\n"
                "    return Box().method()\n"
            ),
            "Box",
            "__class__",
            42,
        ),
        "global": (
            "__class__",
            (
                "class Box:\n"
                "    def method(self):\n"
                "        global __class__\n"
                "        return __class__()\n"
                "def use():\n"
                "    return Box().method()\n"
            ),
            "Box.method",
            "__class__",
            42,
        ),
        "local": (
            "__class__",
            (
                "class Box:\n"
                "    def method(self):\n"
                "        def __class__():\n"
                "            return 99\n"
                "        return __class__()\n"
                "def use():\n"
                "    return Box().method()\n"
            ),
            "Box.method",
            "Box.method.__class__",
            99,
        ),
        "enclosing-local": (
            "__class__",
            (
                "class Box:\n"
                "    def method(self):\n"
                "        def __class__():\n"
                "            return 99\n"
                "        def inner():\n"
                "            return __class__()\n"
                "        return inner()\n"
                "def use():\n"
                "    return Box().method()\n"
            ),
            "Box.method.inner",
            "Box.method.__class__",
            99,
        ),
        "docless": (
            "__doc__",
            "class Box:\n    value = __doc__()\ndef use():\n    return Box.value\n",
            "Box",
            "__doc__",
            42,
        ),
        "unannotated": (
            "__annotations__",
            (
                "class Box:\n"
                "    value = __annotations__()\n"
                "def use():\n"
                "    return Box.value\n"
            ),
            "Box",
            "__annotations__",
            42,
        ),
        "explicit-def": (
            "__module__",
            (
                "class Box:\n"
                "    def __module__():\n"
                "        return 99\n"
                "    value = __module__()\n"
                "def use():\n"
                "    return Box.value\n"
            ),
            "Box",
            "Box.__module__",
            99,
        ),
        "explicit-import": (
            "__module__",
            (
                "class Box:\n"
                "    from provider import target as __module__\n"
                "    value = __module__()\n"
                "def use():\n"
                "    return Box.value\n"
            ),
            "Box",
            "target",
            99,
        ),
        "global-annotations": (
            "__annotations__",
            (
                "class Box:\n"
                "    global __annotations__\n"
                "    x: int\n"
                "    value = __annotations__()\n"
                "def use():\n"
                "    return Box.value\n"
            ),
            "Box",
            "__annotations__",
            42,
        ),
    }
    name, source, caller, target, value = cases[context]
    write(root, "consumer.py", f"def {name}():\n    return 42\n" + source)
    assert execute_use(root, standalone_python) == {"value": value}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(a == caller and b == target for _, a, _, b, _ in call_edges(db))


@pytest.mark.parametrize("position", ["later", "conditional"])
def test_ac4_uncertain_implicit_class_overrides_are_not_callable_proof(
    subprocess_cli, standalone_python, position
):
    cli, run = subprocess_cli
    _, root = cli
    override = "    def __module__():\n        return 99\n"
    body = (
        "    value = __module__()\n" + override
        if position == "later"
        else "    if False:\n"
        + "".join("    " + line + "\n" for line in override.splitlines())
        + "    value = __module__()\n"
    )
    write(
        root,
        "consumer.py",
        "def __module__():\n    return 42\nclass Box:\n"
        + body
        + "def use():\n    return Box.value\n",
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, "Box", "__module__", "__module__", reason="implicit_class_binding"
    )


@pytest.mark.parametrize(
    "definition", ["def target():\n    return 42\n", "class target:\n    pass\n"]
)
def test_ac4_ac5_decorator_refresh_updates_unchanged_imported_consumers(
    subprocess_cli, standalone_python, definition
):
    cli, run = subprocess_cli
    _, root = cli
    source = (
        "def replace(value):\n    return 7\ndef safe():\n    return 11\n#replace\n"
        + definition
    )
    active = source.replace("#replace", "@replace")
    provider = write(root, "provider.py", source)
    write(
        root,
        "consumer.py",
        (
            "from provider import target as alias, safe\n"
            "def use():\n"
            "    alias()\n"
            "    return 42\n"
            "def positive():\n"
            "    return safe()\n"
        ),
    )
    assert run()["status"] == "ok"
    for text, blocked in [
        (active, True),
        (source, False),
        (active, True),
        (source, False),
    ]:
        stat = provider.stat()
        provider.write_text(text)
        os.utime(provider, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        actual = execute_use(root, standalone_python)
        assert actual == ({"error": "TypeError"} if blocked else {"value": 42})
        result = run()
        assert result["status"] == "ok" and result["index"]["reparsed_files"] == 1
        with database(cli) as db:
            edges = call_edges(db)
            assert any(a == "use" and b == "target" for _, a, _, b, _ in edges) == (
                not blocked
            )
            assert any(a == "positive" and b == "safe" for _, a, _, b, _ in edges)
        if blocked:
            assert_written_views(
                cli,
                run,
                "use",
                "target",
                "alias",
                target_path="provider.py",
                reason="decorated_binding",
            )
    provider.unlink()
    assert run()["index"]["deleted_files"] == 1
    with database(cli) as db:
        assert not db.execute("SELECT 1 FROM ineligible").fetchone()
        assert not any(p == "provider.py" for _, _, p, _, _ in call_edges(db))


@pytest.mark.parametrize("kind", ["cell", "doc"])
def test_ac4_ac5_implicit_binding_refresh_changes_scope_without_stale_edges(
    subprocess_cli, standalone_python, kind
):
    cli, run = subprocess_cli
    _, root = cli
    if kind == "cell":
        source = (
            "def __class__():\n"
            "    return 42\n"
            "if True:  \n"
            "    def use():\n"
            "        return __class__()\n"
        )
        active = source.replace("if True:  ", "class Box:")
        consumer = "from provider import use\n"
        changed_consumer = (
            "from provider import Box\n"
            "def use():\n"
            "    return type(Box.use()).__name__\n"
        )
        target = "__class__"
    else:
        source = (
            "def __doc__():\n"
            "    return 42\n"
            "class Box:\n"
            "    #doc#\n"
            "    value = __doc__()\n"
            "def use():\n"
            "    return Box.value\n"
        )
        active = source.replace("#doc#", '"doc"')
        consumer = changed_consumer = "from provider import use\n"
        target = "__doc__"
    provider = write(root, "provider.py", source)
    write(root, "consumer.py", consumer)
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    for text, blocked in [
        (active, True),
        (source, False),
        (active, True),
        (source, False),
    ]:
        stat = provider.stat()
        provider.write_text(text)
        os.utime(provider, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        if kind == "cell":
            write(root, "consumer.py", changed_consumer if blocked else consumer)
        result = run()
        assert result["status"] == "ok" and result["index"]["reparsed_files"] == (
            2 if kind == "cell" else 1
        )
        assert execute_use(root, standalone_python) == (
            {"value": "Box"}
            if blocked and kind == "cell"
            else {"error": "TypeError"}
            if blocked
            else {"value": 42}
        )
        with database(cli) as db:
            assert any(b == target for _, _, _, b, _ in call_edges(db)) == (not blocked)
    provider.rename(root / "renamed.py")
    write(root, "consumer.py", consumer.replace("provider", "renamed"))
    result = run()
    assert (
        result["index"]["reparsed_files"] == 2 and result["index"]["deleted_files"] == 1
    )
    assert execute_use(root, standalone_python) == {"value": 42}


@pytest.mark.parametrize("route", ["direct", "alias"])
def test_ac4_explicit_metaclass_creation_does_not_prove_class_value(
    subprocess_cli, standalone_python, route
):
    cli, run = subprocess_cli
    _, root = cli
    source = (
        "def meta(*args, **kwargs):\n"
        "    return 7\n"
        "class target(metaclass=meta):\n"
        "    pass\n"
    )
    if route == "alias":
        write(root, "provider.py", source)
        source = "from provider import target\n"
    write(root, "consumer.py", source + "def use():\n    return target()\n")
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(
        cli,
        run,
        "use",
        "target",
        "target",
        target_path="provider.py" if route == "alias" else "consumer.py",
        reason="class_creation",
    )


def test_ac4_inherited_metaclass_transform_is_not_callable_proof(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        (
            "class Meta(type):\n"
            "    def __new__(meta, name, bases, namespace):\n"
            '        if name == "target":\n'
            "            return 7\n"
            "        return super().__new__(meta, name, bases, namespace)\n"
            "class Base(metaclass=Meta):\n"
            "    pass\n"
            "class target(Base):\n"
            "    pass\n"
            "def use():\n"
            "    return target()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, "use", "target", "target", reason="class_creation")


def test_ac4_custom_class_namespace_does_not_prove_local_definition_value(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        (
            "class Namespace(dict):\n"
            "    def __setitem__(self, name, value):\n"
            "        return super().__setitem__(name, "
            '7 if name == "target" else value)\n'
            "class Meta(type):\n"
            "    @classmethod\n"
            "    def __prepare__(meta, name, bases):\n"
            "        return Namespace()\n"
            "class Box(metaclass=Meta):\n"
            "    def target():\n"
            "        return 42\n"
            "    value = target()\n"
            "def use():\n"
            "    return 42\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(
        cli, run, "Box", "Box.target", "target", reason="class_creation"
    )


@pytest.mark.parametrize("name", ["__module__", "__qualname__", "__doc__"])
def test_ac4_method_lookup_skips_ordinary_implicit_class_namespace(
    subprocess_cli, standalone_python, name
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        (
            f"def {name}():\n"
            f"    return 42\n"
            f"class Box:\n"
            f'    "doc"\n'
            f"    def method(self):\n"
            f"        return {name}()\n"
            f"def use():\n"
            f"    return Box().method()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(a == "Box.method" and b == name for _, a, _, b, _ in call_edges(db))


@pytest.mark.parametrize(
    "name", ["__module__", "__doc__", "__firstlineno__", "__static_attributes__"]
)
def test_ac4_declared_compiler_class_writes_invalidate_actual_global_binding(
    subprocess_cli, standalone_python, name
):
    cli, run = subprocess_cli
    _, root = cli
    doc = '    "doc"\n' if name == "__doc__" else ""
    write(
        root,
        "consumer.py",
        f"def {name}():\n    return 42\nclass Box:\n"
        + doc
        + f"    global {name}\ndef use():\n    return {name}()\n",
    )
    blocked = name not in {
        "__firstlineno__",
        "__static_attributes__",
    } or standalone_python != str(PYTHON312)
    assert execute_use(root, standalone_python) == (
        {"error": "TypeError"} if blocked else {"value": 42}
    )
    assert run()["status"] == "ok"
    if blocked:
        assert_written_views(cli, run, "use", name, name)
    else:
        with database(cli) as db:
            assert any(a == "use" and b == name for _, a, _, b, _ in call_edges(db))


def test_ac4_ac5_class_binding_cache_tracks_actual_interpreter(cli):
    module, root = cli
    write(
        root,
        "consumer.py",
        (
            "def __firstlineno__():\n"
            "    return 42\n"
            "class Box:\n"
            "    value = __firstlineno__()\n"
        ),
    )
    for interpreter, blocked in [
        (sys.executable, True),
        (str(PYTHON312), False),
        (sys.executable, True),
        (str(PYTHON312), False),
    ]:
        child = subprocess.run(
            [interpreter, str(SCRIPT), "status", "--root", str(root)],
            capture_output=True,
            text=True,
            check=True,
            env=dict(
                os.environ,
                TMPDIR=module.tempfile.gettempdir(),
                PYTHONDONTWRITEBYTECODE="1",
            ),
            timeout=45,
        )
        assert child.stderr == ""
        result = json.loads(child.stdout)
        directory_child = subprocess.run(
            [
                interpreter,
                "-c",
                (
                    "import importlib.util,sys\n"
                    "from pathlib import Path\n"
                    's=importlib.util.spec_from_file_location("cli",sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n'
                    "print(m.private_directory(Path(sys.argv[2]))[0])"
                ),
                str(SCRIPT),
                str(root),
            ],
            capture_output=True,
            text=True,
            check=True,
            env=dict(
                os.environ,
                TMPDIR=module.tempfile.gettempdir(),
                PYTHONDONTWRITEBYTECODE="1",
            ),
            timeout=10,
        )
        with sqlite3.connect(
            Path(directory_child.stdout.strip()) / "index.sqlite3"
        ) as db:
            assert any(
                a == "Box" and b == "__firstlineno__"
                for _, a, _, b, _ in call_edges(db)
            ) == (not blocked)
            assert (
                bool(
                    db.execute(
                        "SELECT 1 FROM unresolved WHERE expression='__firstlineno__' "
                        "AND reason='implicit_class_binding'"
                    ).fetchone()
                )
                == blocked
            )
        assert result["status"] == "ok"


@pytest.mark.parametrize(
    "context", ["class-base", "class-decorator", "method-decorator", "method-default"]
)
def test_ac4_class_implicit_bindings_respect_evaluation_context(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    if context == "class-base":
        source = (
            "def __class__():\n"
            "    return object\n"
            "class Box(__class__()):\n"
            "    pass\n"
            "def use():\n"
            "    return type(Box()).__name__\n"
        )
        caller, expr, value = "", "__class__", "Box"
    elif context == "method-default":
        source = (
            "def __module__():\n"
            "    return 42\n"
            "class Box:\n"
            "    def method(self, value=__module__()):\n"
            "        return value\n"
            "def use():\n"
            "    return Box().method()\n"
        )
        caller, expr, value = "Box", "__module__", None
    else:
        prefix = (
            "def identity(value):\n"
            "    return value\n"
            "def __class__():\n"
            "    return identity\n"
        )
        source = prefix + (
            (
                "@__class__()\n"
                "class Box:\n"
                "    pass\n"
                "def use():\n"
                "    return type(Box()).__name__\n"
            )
            if context == "class-decorator"
            else (
                "class Box:\n"
                "    @__class__()\n"
                "    def method(self):\n"
                "        return 42\n"
                "def use():\n"
                "    return Box().method()\n"
            )
        )
        caller, expr, value = (
            ("", "__class__", "Box")
            if context == "class-decorator"
            else ("Box", "__class__", 42)
        )
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == (
        {"error": "TypeError"} if value is None else {"value": value}
    )
    assert run()["status"] == "ok"
    if value is None:
        assert_written_views(
            cli, run, caller, expr, expr, reason="implicit_class_binding"
        )
    else:
        with database(cli) as db:
            assert any(a == caller and b == expr for _, a, _, b, _ in call_edges(db))


@pytest.mark.parametrize("declared", [False, True])
def test_ac4_custom_class_namespace_lookup_and_global_bypass(
    subprocess_cli, standalone_python, declared
):
    cli, run = subprocess_cli
    _, root = cli
    source = (
        (
            "def target():\n"
            "    return 42\n"
            "class Namespace(dict):\n"
            "    def __getitem__(self, name):\n"
            '        if name == "target":\n'
            "            return 7\n"
            "        return super().__getitem__(name)\n"
            "class Meta(type):\n"
            "    @classmethod\n"
            "    def __prepare__(meta, name, bases):\n"
            "        return Namespace()\n"
            "class Box(metaclass=Meta):\n"
        )
        + ("    global target\n" if declared else "")
        + "    value = target()\ndef use():\n    return Box.value\n"
    )
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == (
        {"value": 42} if declared else {"error": "TypeError"}
    )
    assert run()["status"] == "ok"
    if declared:
        with database(cli) as db:
            assert any(a == "Box" and b == "target" for _, a, _, b, _ in call_edges(db))
    else:
        assert_written_views(
            cli, run, "Box", "target", "target", reason="class_creation"
        )


def test_ac4_class_creation_uncertainty_does_not_suppress_mutation_addresses(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 42\n")
    write(
        root,
        "mutator.py",
        (
            "class Meta(type):\n"
            "    pass\n"
            "class Box(metaclass=Meta):\n"
            "    import provider as alias\n"
            "    alias.target = 7\n"
        ),
    )
    write(
        root,
        "consumer.py",
        (
            "import mutator\n"
            "from provider import target\n"
            "def use():\n"
            "    return target()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"error": "TypeError"}
    assert run()["status"] == "ok"
    assert_written_views(cli, run, "use", "target", "target", target_path="provider.py")


def assert_private_lookup(
    cli,
    run,
    caller,
    expression,
    expected,
    wrong="__target",
    path="consumer.py",
    target_path=None,
):
    """AC4: source spellings stay visible while graph identity follows compilation."""
    with database(cli) as db:
        source = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?", (path, caller)
        ).fetchone()[0]
        wrong_id = db.execute(
            "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
            (target_path or path, wrong),
        ).fetchone()[0]
        target = (
            db.execute(
                "SELECT id FROM symbols WHERE path=? AND qualified_name=?",
                (target_path or path, expected),
            ).fetchone()[0]
            if expected
            else None
        )
    forward = run("neighbors", symbol=source, edge_kind="callees")
    targets = {e["target"] for e in forward["edges"]}
    if expected:
        assert target in targets
        assert not any(u["expression"] == expression for u in forward["unresolved"])
    else:
        assert (
            any(u["expression"] == expression for u in forward["unresolved"])
            and forward["incomplete"]
        )
    if target != wrong_id:
        assert wrong_id not in targets
        reverse = run("neighbors", symbol=wrong_id, edge_kind="callers")
        assert all(e["source"] != source for e in reverse["edges"])
    graph = run(
        "subgraph",
        symbol=list(dict.fromkeys([source, wrong_id] + ([target] if target else []))),
        hops=0,
    )
    assert {
        (e["source"], e["target"]) for e in graph["edges"] if e["kind"] == "calls"
    } == ({(source, target)} if target else set())
    if not target:
        assert graph["incomplete"] and any(
            u["expression"] == expression for u in graph["unresolved"]
        )


@pytest.mark.parametrize(
    "context",
    ["body", "method", "nested", "nested-class", "private-class", "all-underscore"],
)
@pytest.mark.parametrize("present", [False, True])
def test_ac4_private_names_follow_class_compilation_context(
    subprocess_cli, standalone_python, context, present
):
    cli, run = subprocess_cli
    _, root = cli
    name = {
        "private-class": "__Box",
        "all-underscore": "___",
        "nested-class": "Outer",
    }.get(context, "Box")
    canonical = "_Inner__target" if context == "nested-class" else "_Box__target"
    prefix = "def __target():\n    return 42\n" + (
        f"def {canonical}():\n    return 99\n" if present else ""
    )
    cases = {
        "body": (
            (
                f"class {name}:\n"
                f"    value = __target()\n"
                f"def use():\n"
                f"    return {name}.value\n"
            ),
            name,
        ),
        "method": (
            (
                f"class {name}:\n"
                f"    def method(self):\n"
                f"        return __target()\n"
                f"def use():\n"
                f"    return {name}().method()\n"
            ),
            name + ".method",
        ),
        "nested": (
            (
                f"class {name}:\n"
                f"    def method(self):\n"
                f"        def inner():\n"
                f"            return __target()\n"
                f"        return inner()\n"
                f"def use():\n"
                f"    return {name}().method()\n"
            ),
            name + ".method.inner",
        ),
        "nested-class": (
            (
                "class Outer:\n"
                "    class Inner:\n"
                "        def method(self):\n"
                "            return __target()\n"
                "def use():\n"
                "    return Outer.Inner().method()\n"
            ),
            "Outer.Inner.method",
        ),
        "private-class": (
            (
                "class __Box:\n"
                "    def method(self):\n"
                "        return __target()\n"
                "def use():\n"
                "    return __Box().method()\n"
            ),
            "__Box.method",
        ),
        "all-underscore": (
            (
                "class ___:\n"
                "    def method(self):\n"
                "        return __target()\n"
                "def use():\n"
                "    return ___().method()\n"
            ),
            "___.method",
        ),
    }
    source, caller = cases[context]
    write(root, "consumer.py", prefix + source)
    expected = (
        "__target" if context == "all-underscore" else canonical if present else None
    )
    assert execute_use(root, standalone_python) == (
        {"value": 42 if context == "all-underscore" else 99}
        if expected
        else {"error": "NameError"}
    )
    assert run()["status"] == "ok"
    assert_private_lookup(cli, run, caller, "__target", expected)


@pytest.mark.parametrize(
    "binding",
    ["definition", "import", "parameter", "pattern", "exception", "assignment"],
)
def test_ac4_private_local_bindings_share_normalized_identity(
    subprocess_cli, standalone_python, binding
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def target():\n    return 21\n")
    bodies = {
        "definition": (
            (
                "    def method(self):\n"
                "        def __target():\n"
                "            return 21\n"
                "        return __target()\n"
            ),
            "Box.method.__target",
            21,
        ),
        "import": (
            (
                "    def method(self):\n"
                "        from provider import target as __target\n"
                "        return __target()\n"
            ),
            "target",
            21,
        ),
        "parameter": (
            "    def method(self, __target=7):\n        return __target()\n",
            None,
            "TypeError",
        ),
        "pattern": (
            (
                "    def method(self):\n"
                "        match 7:\n"
                "            case __target:\n"
                "                pass\n"
                "        return __target()\n"
            ),
            None,
            "TypeError",
        ),
        "exception": (
            (
                "    def method(self):\n"
                "        try:\n"
                "            raise ValueError()\n"
                "        except ValueError as __target:\n"
                "            pass\n"
                "        return __target()\n"
            ),
            None,
            "UnboundLocalError",
        ),
        "assignment": (
            "    def method(self):\n        __target = 7\n        return __target()\n",
            None,
            "TypeError",
        ),
    }
    body, expected, actual = bodies[binding]
    write(
        root,
        "consumer.py",
        (
            "def __target():\n"
            "    return 42\n"
            "def _Box__target():\n"
            "    return 99\n"
            "class Box:\n"
        )
        + body
        + "def use():\n    return Box().method()\n",
    )
    assert execute_use(root, standalone_python) == (
        {"value": actual} if expected else {"error": actual}
    )
    assert run()["status"] == "ok"
    if binding == "import":
        with database(cli) as db:
            assert any(
                a == "Box.method" and p == "provider.py" and b == "target"
                for _, a, p, b, _ in call_edges(db)
            )
    else:
        assert_private_lookup(
            cli, run, "Box.method", "__target", expected, wrong="_Box__target"
        )
    with database(cli) as db:
        assert not any(
            a == "Box.method" and b == "__target" for _, a, _, b, _ in call_edges(db)
        )
        if binding == "definition":
            row = db.execute(
                "SELECT name,qualified_name,lookup_name FROM symbols "
                "WHERE qualified_name='Box.method.__target'"
            ).fetchone()
            assert row == ("__target", "Box.method.__target", "_Box__target")


@pytest.mark.parametrize(
    "route",
    [
        "module",
        "from-member",
        "from-module",
        "dotted-alias",
        "dotted-attribute",
        "attribute",
    ],
)
def test_ac4_private_import_paths_aliases_and_attributes(
    subprocess_cli, standalone_python, route
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "provider.py",
        "def __target():\n    return 42\ndef _Box__target():\n    return 99\n",
    )
    write(root, "__provider.py", "def target():\n    return 42\n")
    write(root, "_Box__provider.py", "def target():\n    return 99\n")
    write(root, "pkg/__init__.py", "")
    write(root, "pkg/__child.py", "def target():\n    return 99\n")
    imports, call, target_path, target = {
        "module": (
            "import __provider",
            "__provider.target",
            "_Box__provider.py",
            "target",
        ),
        "from-member": (
            "from provider import __target as __alias",
            "__alias",
            "provider.py",
            "_Box__target",
        ),
        "from-module": (
            "from __provider import target as __alias",
            "__alias",
            "_Box__provider.py",
            "target",
        ),
        "dotted-alias": (
            "import pkg.__child as __alias",
            "__alias.target",
            "pkg/__child.py",
            "target",
        ),
        "dotted-attribute": (
            "import pkg.__child",
            "pkg.__child.target",
            "pkg/__child.py",
            None,
        ),
        "attribute": (
            "import provider as __alias",
            "__alias.__target",
            "provider.py",
            "_Box__target",
        ),
    }[route]
    source = (
        "class Box:\n    def method(self):\n        "
        + imports
        + "\n        return "
        + call
        + "()\ndef use():\n    return Box().method()\n"
    )
    write(root, "consumer.py", source)
    assert execute_use(root, standalone_python) == (
        {"value": 99} if target else {"error": "AttributeError"}
    )
    assert run()["status"] == "ok"
    with database(cli) as db:
        edges = call_edges(db)
        assert any(
            a == "Box.method" and p == target_path and b == target
            for _, a, p, b, _ in edges
        ) == bool(target)
        if route in {"from-member", "attribute"}:
            assert not any(
                a == "Box.method" and p == "provider.py" and b == "__target"
                for _, a, p, b, _ in edges
            )
        identifier = db.execute(
            "SELECT id FROM symbols WHERE qualified_name='Box.method'"
        ).fetchone()[0]
    result = run("neighbors", symbol=identifier, edge_kind="callees")
    assert bool(result["unresolved"]) == (target is None)
    if not target:
        assert any(u["expression"] == call for u in result["unresolved"])


@pytest.mark.parametrize("kind", ["global", "nonlocal", "read-only-global"])
def test_ac4_private_declarations_and_mutations_use_actual_binding_owner(
    subprocess_cli, standalone_python, kind
):
    cli, run = subprocess_cli
    _, root = cli
    prefix = "def __target():\n    return 42\ndef _Box__target():\n    return 99\n"
    if kind == "global":
        body = (
            "class Box:\n"
            "    def method():\n"
            "        global __target\n"
            "        __target = 7\n"
            "def use():\n"
            "    Box.method()\n"
            "    return _Box__target()\n"
        )
        caller, target, expression = "use", "_Box__target", "_Box__target"
    elif kind == "nonlocal":
        body = (
            "class Box:\n"
            "    def method():\n"
            "        def __target():\n"
            "            return 21\n"
            "        def change():\n"
            "            nonlocal __target\n"
            "            __target = 7\n"
            "        change()\n"
            "        return __target()\n"
            "def use():\n"
            "    return Box.method()\n"
        )
        caller, target, expression = "Box.method", "Box.method.__target", "__target"
    else:
        body = (
            "class Box:\n"
            "    def method():\n"
            "        global __target\n"
            "        return __target()\n"
            "def use():\n"
            "    return Box.method()\n"
        )
        caller, target, expression = "Box.method", "_Box__target", "__target"
    write(
        root, "consumer.py", prefix + body + "def positive():\n    return __target()\n"
    )
    assert execute_use(root, standalone_python) == (
        {"value": 99} if kind == "read-only-global" else {"error": "TypeError"}
    )
    assert run()["status"] == "ok"
    if kind == "read-only-global":
        assert_private_lookup(cli, run, caller, expression, target)
    else:
        assert_written_views(cli, run, caller, target, expression)
    with database(cli) as db:
        assert any(
            a == "positive" and b == "__target" for _, a, _, b, _ in call_edges(db)
        )


@pytest.mark.parametrize(
    "context",
    [
        "method-default",
        "regular-base",
        "generic-base",
        "method-decorator",
        "generic-method",
        "generic-class-body",
        "generic-private-base",
    ],
)
def test_ac4_private_names_follow_header_and_type_parameter_contexts(
    subprocess_cli, standalone_python, context
):
    cli, run = subprocess_cli
    _, root = cli
    prefix = (
        "events = []\n"
        "class Base:\n"
        "    pass\n"
        "def __target():\n"
        "    return 42\n"
        "def _Box__target():\n"
        "    return 99\n"
    )
    if context == "method-default":
        body = (
            "class Box:\n"
            "    def method(self, value=__target()):\n"
            "        return value\n"
            "def use():\n"
            "    return Box().method()\n"
        )
        caller, expression, expected, actual = (
            "Box",
            "__target",
            "_Box__target",
            {"value": 99},
        )
    elif context in {"regular-base", "generic-base"}:
        prefix += (
            "def __base():\n"
            "    events.append(42)\n"
            "    return Base\n"
            "def _Outer__base():\n"
            "    events.append(99)\n"
            "    return Base\n"
        )
        generic = "[T]" if context == "generic-base" else ""
        body = (
            f"class Outer:\n"
            f"    class Box{generic}(__base()):\n"
            f"        pass\n"
            f"def use():\n"
            f"    return events[0]\n"
        )
        caller, expression, expected, actual = (
            "Outer",
            "__base",
            "__base" if generic else "_Outer__base",
            {"value": 42 if generic else 99},
        )
    elif context == "method-decorator":
        prefix += (
            "def identity(value):\n"
            "    return value\n"
            "def _Box__decorate():\n"
            "    return identity\n"
            "def __decorate():\n"
            "    return 7\n"
        )
        body = (
            "class Box:\n"
            "    @__decorate()\n"
            "    def method(self):\n"
            "        return 99\n"
            "def use():\n"
            "    return Box().method()\n"
        )
        caller, expression, expected, actual = (
            "Box",
            "__decorate",
            "_Box__decorate",
            {"value": 99},
        )
    elif context == "generic-method":
        body = (
            "class Box:\n"
            "    def method[__target](self):\n"
            "        return __target()\n"
            "def use():\n"
            "    return Box().method()\n"
        )
        caller, expression, expected, actual = (
            "Box.method",
            "__target",
            None,
            {"error": "TypeError"},
        )
    elif context == "generic-class-body":
        body = (
            "class Box[__target]:\n"
            "    def method(self):\n"
            "        return __target()\n"
            "def use():\n"
            "    return Box().method()\n"
        )
        caller, expression, expected, actual = (
            "Box.method",
            "__target",
            None,
            {"error": "TypeError"},
        )
    else:
        body = "class Box[__target](__target()):\n    pass\ndef use():\n    return 42\n"
        caller, expression, expected, actual = (
            "",
            "__target",
            None,
            {"error": "TypeError"},
        )
    write(root, "consumer.py", prefix + body)
    assert execute_use(root, standalone_python) == actual
    assert run()["status"] == "ok"
    assert_private_lookup(
        cli,
        run,
        caller,
        expression,
        expected,
        wrong="__base"
        if context in {"regular-base", "generic-base"}
        else "__decorate"
        if context == "method-decorator"
        else "__target",
    )


@pytest.mark.parametrize("operation", ["assignment", "deletion"])
def test_ac4_ac5_private_attribute_mutations_and_context_refresh(
    subprocess_cli, standalone_python, operation
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "provider.py",
        (
            "def __target():\n"
            "    return 42\n"
            "def _Box__target():\n"
            "    return 99\n"
            "def _Dog__target():\n"
            "    return 11\n"
        ),
    )
    action = "alias.__target = 7" if operation == "assignment" else "del alias.__target"
    source = "import provider as alias\nclass Box:\n    " + action + "\n"
    mutator = write(root, "mutator.py", source)
    write(
        root,
        "consumer.py",
        (
            "import mutator\n"
            "import provider\n"
            "def use():\n"
            "    return provider._Box__target()\n"
            "def positive():\n"
            "    return provider.__target()\n"
        ),
    )
    assert run()["status"] == "ok"
    for name in ["Box", "Dog", "Box", "Dog"]:
        stat = mutator.stat()
        mutator.write_text(source.replace("Box", name))
        os.utime(mutator, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        result = run()
        assert result["index"]["reparsed_files"] == (
            0 if name == "Box" and result["index"]["generation"] == 1 else 1
        )
        assert execute_use(root, standalone_python) == (
            {"value": 99}
            if name == "Dog"
            else {
                "error": "TypeError" if operation == "assignment" else "AttributeError"
            }
        )
        with database(cli) as db:
            edges = call_edges(db)
            assert any(
                a == "use" and b == "_Box__target" for _, a, _, b, _ in edges
            ) == (name == "Dog")
            assert any(a == "positive" and b == "__target" for _, a, _, b, _ in edges)
            assert db.execute(
                "SELECT DISTINCT name FROM mutations WHERE path=?", ("mutator.py",)
            ).fetchall() == [(f"_{name}__target",)]
    mutator.unlink()
    write(
        root,
        "consumer.py",
        "import provider\ndef use():\n    return provider._Dog__target()\n",
    )
    result = run()
    assert result["index"]["deleted_files"] == 1
    assert execute_use(root, standalone_python) == {"value": 11}
    with database(cli) as db:
        assert not db.execute(
            "SELECT 1 FROM mutations WHERE path='mutator.py'"
        ).fetchone()


@pytest.mark.parametrize("name", ["target", "_target", "__target__"])
def test_ac4_nonprivate_spellings_keep_ordinary_bindings(
    subprocess_cli, standalone_python, name
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        (
            f"def {name}():\n"
            f"    return 42\n"
            f"class Box:\n"
            f"    def method(self):\n"
            f"        return {name}()\n"
            f"def use():\n"
            f"    return Box().method()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"value": 42}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(a == "Box.method" and b == name for _, a, _, b, _ in call_edges(db))


def test_ac4_private_comprehension_iteration_identity_is_isolated(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "provider.py", "def _Box__target():\n    return 99\n")
    write(
        root,
        "consumer.py",
        (
            "import provider as _Box__alias\n"
            "class Box:\n"
            "    [0 for __alias in [] for _Box__alias.__target in []]\n"
            "def use():\n"
            "    return _Box__alias._Box__target()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"value": 99}
    assert run()["status"] == "ok"
    with database(cli) as db:
        assert any(
            a == "use" and b == "_Box__target" for _, a, _, b, _ in call_edges(db)
        )
        assert not db.execute(
            "SELECT 1 FROM mutations WHERE name='_Box__target'"
        ).fetchone()


def test_ac4_private_relative_import_preserves_physical_module_identity(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(root, "pkg/__init__.py", "")
    write(root, "pkg/__provider.py", "def __target():\n    return 42\n")
    write(
        root,
        "pkg/_Box__provider.py",
        "def __target():\n    return 42\ndef _Box__target():\n    return 99\n",
    )
    write(
        root,
        "pkg/reader.py",
        (
            "class Box:\n"
            "    def method(self):\n"
            "        from .__provider import __target\n"
            "        return __target()\n"
            "def use():\n"
            "    return Box().method()\n"
        ),
    )
    write(root, "consumer.py", "from pkg.reader import use\n")
    assert execute_use(root, standalone_python) == {"value": 99}
    assert run()["status"] == "ok"
    assert_private_lookup(
        cli,
        run,
        "Box.method",
        "__target",
        "_Box__target",
        path="pkg/reader.py",
        target_path="pkg/_Box__provider.py",
    )
    with database(cli) as db:
        assert not any(p == "pkg/__provider.py" for _, _, p, _, _ in call_edges(db))


def test_ac4_nested_private_class_binding_and_compilation_name_are_distinct(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    write(
        root,
        "consumer.py",
        (
            "def __target():\n"
            "    return 42\n"
            "def _Inner__target():\n"
            "    return 99\n"
            "class Outer:\n"
            "    class __Inner:\n"
            "        def method(self):\n"
            "            return __target()\n"
            "    value = __Inner()\n"
            "def use():\n"
            "    return Outer.value.method()\n"
        ),
    )
    assert execute_use(root, standalone_python) == {"value": 99}
    assert run()["status"] == "ok"
    assert_private_lookup(
        cli, run, "Outer.__Inner.method", "__target", "_Inner__target"
    )
    with database(cli) as db:
        assert any(
            a == "Outer" and b == "Outer.__Inner" for _, a, _, b, _ in call_edges(db)
        )
        assert db.execute(
            "SELECT name,lookup_name FROM symbols WHERE qualified_name='Outer.__Inner'"
        ).fetchone() == ("__Inner", "_Outer__Inner")


def test_ac4_ac5_private_definition_context_equal_stat_refresh_and_removal(
    subprocess_cli, standalone_python
):
    cli, run = subprocess_cli
    _, root = cli
    source = (
        "def __target():\n"
        "    return 42\n"
        "def _Box__target():\n"
        "    return 99\n"
        "def _Dog__target():\n"
        "    return 11\n"
        "class Box:\n"
        "    def method(self):\n"
        "        return __target()\n"
        "def use():\n"
        "    return Box().method()\n"
    )
    provider = write(root, "provider.py", source)
    write(root, "consumer.py", "from provider import use\n")
    assert run()["status"] == "ok"
    for name in ["Dog", "Box", "Dog", "Box"]:
        stat = provider.stat()
        text = source.replace("class Box:", f"class {name}:").replace(
            "return Box()", f"return {name}()"
        )
        assert len(text) == len(source)
        provider.write_text(text)
        os.utime(provider, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        result = run()
        assert result["index"]["reparsed_files"] == 1
        assert execute_use(root, standalone_python) == {
            "value": 11 if name == "Dog" else 99
        }
        assert_private_lookup(
            cli,
            run,
            name + ".method",
            "__target",
            f"_{name}__target",
            path="provider.py",
        )
        with database(cli) as db:
            assert any(a == "use" and b == name for _, a, _, b, _ in call_edges(db))
            assert not db.execute(
                "SELECT 1 FROM symbols WHERE kind='class' AND name!=?", (name,)
            ).fetchone()
            assert db.execute(
                "SELECT 1 FROM edges e JOIN symbols t ON e.target=t.id "
                "WHERE e.kind='imports' AND t.path='provider.py' "
                "AND t.qualified_name='use'"
            ).fetchone()
    provider.unlink()
    assert run()["index"]["deleted_files"] == 1
    with database(cli) as db:
        assert not any(p == "provider.py" for _, _, p, _, _ in call_edges(db))
