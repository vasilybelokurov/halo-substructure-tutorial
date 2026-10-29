# Finding Milky Way halo substructure in survey data

A step-by-step Python tutorial on detecting substructure in the Milky Way's stellar halo — faint satellites
(dwarf galaxies and star clusters) and disrupted satellites (stellar streams) — in public imaging surveys:
SDSS, Pan-STARRS1, the Legacy Surveys, HSC-SSP and Gaia.

**Read online:** https://vasilybelokurov.github.io/halo-substructure-tutorial/

Status: in development (v0.1). The plan, including later chapters, is in [STRUCTURE.md](STRUCTURE.md).

## Run in the browser

Open any notebook in Google Colab, e.g.
[Chapter 0 — Data](https://colab.research.google.com/github/vasilybelokurov/halo-substructure-tutorial/blob/main/notebooks/00_data.ipynb).
Each notebook downloads the small data files it needs from this repository's
[`data-v0.1` release](https://github.com/vasilybelokurov/halo-substructure-tutorial/releases/tag/data-v0.1)
and checks their SHA-256 checksums.

## Run locally

```bash
pip install -r requirements.txt jupyter pytest nbmake
pytest tests/ --nbmake notebooks/
jupyter lab notebooks/
```

## Data

The data files are sky patches extracted from public survey catalogues with `scripts/build_data.py`, which
records the exact SQL of each file in `data/MANIFEST.json`. Sources, licences and acknowledgements:
[data/README.md](data/README.md).

## Licence

Tutorial code and text: MIT (see [LICENSE](LICENSE)). Data files: see [data/README.md](data/README.md).
