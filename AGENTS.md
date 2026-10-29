# AGENTS.md

## Project

A Python tutorial, in Jupyter notebooks published from a public git repo, on detecting
substructure in the Milky Way halo in large survey data: (1) intact satellites, however
faint; (2) disrupted satellites (streams and other debris). Data come from WSDB
(Whole Sky Database) and are shipped to students as pre-extracted files. **Public data only**
(SDSS, PS1, Legacy Surveys DR9, DES DR2, HSC PDR3, Gaia DR3); no DELVE DR3, DES Y6 or other
proprietary releases.

## Rules

1. **Write the least code that works.**
2. **Reproduce every bug with a failing test** before fixing it.
3. **Show a plot before claiming a result.**

## Workflow

- Chapters are `notebooks/NN_<slug>.ipynb`, committed without outputs; each runs standalone in Colab.
- Students have no WSDB access: `scripts/build_data.py` queries WSDB (sqlutilpy, q3c, plan checked
  with `EXPLAIN`) and writes the parquet files that notebooks download (with an MD5 check).
- Each notebook backs every claim with a plot and an `assert` against a known result
  (e.g. a published satellite position, distance, or stream track).
- Before pushing: `pytest tests/ --nbmake notebooks/`.
- Every literature reference carries a working ADS/arXiv/DOI link, checked before it is committed.
