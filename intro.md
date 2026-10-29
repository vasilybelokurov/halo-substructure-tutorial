# Finding Milky Way halo substructure

This tutorial teaches how faint satellites of the Milky Way and the debris of disrupted ones — stellar
streams — are found in large imaging surveys, starting from a catalogue of stars and ending with a frozen,
null-calibrated search of a held-out patch of sky.

Each chapter is a Jupyter notebook that runs on its own (in Google Colab, or locally), downloads the small data
files it needs, and backs every claim with a figure and an explicit numerical check (`assert`).

**Chapters**

0. Survey catalogues and the data of this tutorial
1. Star or galaxy? Classifying individual objects (SDSS, PS1, Legacy Surveys and HSC against HST)
2. Colour–magnitude diagrams, isochrones and distance
3. Is an overdensity made of stars? (Abell 370 vs Boötes I)
4. The matched filter (Boötes I and the tails of Pal 5)
5. Searching for overdensities, and calibrating the search with null patches
6. An unbinned likelihood: the structure of Boötes I
7. A stellar stream: the tidal tails of Pal 5

More chapters — injection–recovery, a blind search and an all-sky Gaia search — are being added; see `STRUCTURE.md` in the
repository.

**Prerequisites.** Basic Python (numpy, matplotlib) and elementary astronomy (magnitudes, colours).

**Data.** Public survey catalogues, extracted from the WSDB database in Cambridge with q3c
(Koposov & Bartunov 2006). See `data/README.md` for sources and licences.
