"""Run pinned native source on local synthetic fixtures, never Gemma inference."""

import subprocess
from pathlib import Path

import pytest

from mostaza.resources import require_resources

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / ".tools/official/bin/python"
SETUP = """
import sys
from pathlib import Path
import networkx as nx
import numpy as np
from swegemma import graph as sg
from swegemma.graph import graph_utils as gu, embedding_utils as eu
from swegemma.context import SwegemmaContext
from swegemma.tools import create_tools
base = Path(sys.argv[1])
gd, ed = base / 'graphs', base / 'embeddings'
g = nx.MultiDiGraph(repo_name='fixture')
vectors = {'pkg.a.seed': [1., 0.], 'pkg.b.seed': [0., 1.],
           'pkg.helper': [.9, .1], 'pkg.next': [.1, .9],
           'pkg.caller': [.5, .5]}
for name in vectors:
    g.add_node(name, name=name, text='def ' + name + '(): pass')
g.add_edge('pkg.a.seed', 'pkg.helper', type='calls')
g.add_edge('pkg.a.seed', 'pkg.helper', type='calls')
g.add_edge('pkg.helper', 'pkg.next', type='calls')
g.add_edge('pkg.caller', 'pkg.a.seed', type='uses')
gu.save_graph_to_json(g, str(gd))
eu.save_embeddings_to_npz('fixture', vectors, str(ed))
ctx = SwegemmaContext(max_tool_calls=100, max_time_minutes=1,
                      graph_dir=gd, embeddings_dir=ed)
ctx.repo = 'fixture'
tools = create_tools(ctx)
loaded = sg.get_graph('fixture', graph_dir=str(gd), embeddings_dir=str(ed))
"""


@pytest.mark.parametrize(
    "contract",
    [
        # agent-retrieval:AC-6: source resolver chooses deterministic ambiguous suffix.
        """
assert gu.resolve_node_name('pkg.b.seed', loaded) == 'pkg.b.seed'
assert gu.resolve_node_name('helper', loaded) == 'pkg.helper'
assert gu.resolve_node_name('seed', loaded) == 'pkg.a.seed'
assert gu.resolve_node_name('seed', list(reversed(list(loaded)))) == 'pkg.a.seed'
assert gu.resolve_node_name('unfindable_xyz', loaded) is None
assert gu.resolve_node_name('', loaded) is None
""",
        # AC-6: actual native neighbors deduplicate, filter, bound and stay one-hop.
        """
r = tools['get_code_neighbors']('pkg.a.seed', max_neighbors=10)
assert r['status'] == 'ok'
assert r['neighbors'] == ['fixture;pkg.caller', 'fixture;pkg.helper']
assert 'fixture;pkg.next' not in r['neighbors']
assert tools['get_code_neighbors']('pkg.a.seed', max_neighbors=1)['count'] == 1
filtered = tools['get_code_neighbors']('pkg.a.seed', edge_type='CALLS')
assert filtered['neighbors'] == ['fixture;pkg.helper']
assert tools['get_code_neighbors']('seed')['neighbors'] == r['neighbors']
assert tools['get_code_neighbors']('unfindable_xyz')['neighbors'] == []
assert tools['get_code_neighbors']('pkg.a.seed', max_neighbors=0)['status'] == 'error'
s = tools['get_code_subgraph'](['pkg.a.seed', 'pkg.helper'])
assert s['node_count'] == 2 and s['edge_count'] == 2
assert 'pkg.next' not in s['nodes']
""",
        # AC-6: NPZ embeddings are actually loaded; native similarity excludes seed.
        """
exact = eu.embed('pkg.a.seed', 'fixture', embeddings_dir=str(ed))
np.testing.assert_allclose(exact, [1., 0.])
suffix = eu.embed('seed', 'fixture', embeddings_dir=str(ed))
np.testing.assert_allclose(suffix, [1., 0.])
r = tools['search_similar_code']('pkg.a.seed', k=1)
assert r['status'] == 'ok' and r['count'] == 1
assert r['results'][0]['node_name'] == 'pkg.helper'
assert r['results'][0]['similarity'] > .99
assert tools['search_similar_code']('helper', k=5)['count'] == 4
assert tools['search_similar_code']('unfindable_xyz', k=5)['results'] == []
assert tools['search_similar_code']('pkg.a.seed', k=0)['status'] == 'error'
""",
        # AC-6: unavailable resources produce errors/None, not fabricated evidence.
        """
ctx.graph_dir = base / 'absent_graphs'
assert tools['get_code_neighbors']('pkg.a.seed')['error_type'] == 'GraphLookupError'
r = tools['search_similar_code']('pkg.a.seed')
assert r['error_type'] == 'SimilaritySearchError'
r = tools['get_code_subgraph'](['pkg.a.seed'])
assert r['error_type'] == 'SubgraphExtractionError'
missing = str(base / 'absent_embeddings')
assert eu.embed('pkg.a.seed', 'missing_repo', embeddings_dir=missing) is None
ctx.repo = None
assert tools['get_code_neighbors']('pkg.a.seed')['error_type'] == 'MissingRepoContext'
""",
    ],
    ids=["symbols", "bounded-one-hop", "native-embeddings", "missing-resources"],
)
def test_ac6_pinned_native_retrieval_contract(tmp_path: Path, contract: str) -> None:
    require_resources(ROOT, ["swegemma"])
    result = subprocess.run(
        [str(NATIVE), "-c", SETUP + contract, str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ac2_ac5_actual_e1_official_compiler_and_selected_closure(
    tmp_path: Path,
) -> None:
    import zipfile

    from mostaza.packaging import build_submission

    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    digest = build_submission(ROOT, "E1", first, NATIVE)
    assert build_submission(ROOT, "E1", second, NATIVE) == digest
    with zipfile.ZipFile(first) as archive:
        assert set(archive.namelist()) == {
            "agent.yaml",
            "eval_config.yaml",
            "prompts/hybrid-retrieval.md",
        }
        assert (
            archive.read("prompts/hybrid-retrieval.md")
            == (ROOT / "submission/prompts/hybrid-retrieval.md").read_bytes()
        )
