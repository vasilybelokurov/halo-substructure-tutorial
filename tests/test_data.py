"""The data manifest is complete and self-consistent (no network needed).

Run: pytest tests/test_data.py
"""
import json
from pathlib import Path

MANIFEST = json.loads((Path(__file__).resolve().parent.parent / "data" / "MANIFEST.json").read_text())


def test_manifest_entries_complete():
    for name, m in MANIFEST.items():
        assert len(m["sha256"]) == 64 and m["rows"] > 0 and m["bytes"] > 0, name
        assert m["queries"], name


def test_files_used_by_notebooks_are_in_manifest():
    """Names passed as string literals, load('name'), must be in the manifest. Names built at run time
    (e.g. load(f'{obj}_{survey}') in Chapter 12) are not seen here; they are checked when the notebooks run."""
    nb = Path(__file__).resolve().parent.parent / "notebooks"
    used = set()
    for p in nb.glob("*.ipynb"):
        for cell in json.loads(p.read_text())["cells"]:
            src = "".join(cell["source"])
            used |= {s.split("'")[1] for s in src.split("load(")[1:] if s.startswith("'")}
    assert used and used <= set(MANIFEST), used - set(MANIFEST)


def test_lvdb_pinned_identically_in_every_notebook():
    """Every chapter reads the Local Volume Database with load_lvdb(), pinned to one version with its SHA-256."""
    import re
    nb = Path(__file__).resolve().parent.parent / "notebooks"
    pins = {}
    for p in sorted(nb.glob("*.ipynb")):
        src = "".join("".join(c["source"]) for c in json.loads(p.read_text())["cells"])
        version = re.search(r"^LVDB_VERSION = '([^']+)'", src, re.M).group(1)
        sha = re.search(r"^LVDB_SHA256 = \{'([^']+)': '([0-9a-f]{64})'\}", src, re.M)
        assert sha and sha.group(1) == version, p.name
        pins[p.name] = (version, sha.group(2))
    assert len(pins) == 14 and len(set(pins.values())) == 1, pins
