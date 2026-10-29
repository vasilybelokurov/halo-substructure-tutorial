# STRUCTURE.md

Plan of the tutorial **Finding Milky Way halo substructure in survey data**. Audience: students
(beginner upwards) who want to learn how faint satellites and stellar streams are found in large
imaging surveys. Exit level: a frozen, null-calibrated search of a held-out sky region, with a
recovery efficiency measured by injection.

Scope: (1) intact satellites, however faint (dwarf galaxies and faint star clusters);
(2) disrupted satellites (streams; later, other photometric debris). Kinematic substructure in
integrals of motion is out of scope.

This plan was reviewed independently by Codex (OpenAI) and by Claude Fable on 2026-10-29. Their
main recommendations are adopted: a smaller first release built end to end on one survey;
explicit null calibration and injection–recovery; variance-aware statistics; a data contract with
native photometry, extinction provenance, IDs, a manifest and per-product licence terms; and
checks phrased as tests with stated tolerances, not as "agrees with the literature".

## Principles

1. **Doubt first.** Unresolved galaxies are the main contaminant of faint point-source samples,
   and galaxy clusters are a main source of false satellites. Star–galaxy separation is taught
   at the object level (Ch 01) and the population level (Ch 03) before detection.
2. **One framework, adapted.** Satellites and streams are both an excess of stars sharing a
   stellar population and a distance (and, with Gaia, a proper motion) over a smooth foreground.
   The matched filter and the Poisson likelihood are shared; spatial kernels, CMD and background
   models are adapted (streams can carry distance gradients; diffuse debris has depth).
3. **One survey carries the pipeline, others test it.** v0.1 runs the detection pipeline on
   SDSS DR9 (the survey of the classic discoveries, covering every v0.1 object), and uses PS1,
   Legacy Surveys DR9 and HSC PDR3 where comparing surveys *is* the lesson (star–galaxy
   separation). DES DR2 and HSC satellites come in v0.2.
4. **Calibrate, don't just compare.** Significances are calibrated with null simulations and
   injections; agreement with a published value is checked with a stated tolerance against a pinned
   reference (Local Volume Database v1.1.1, Pace 2025; `galstreams`, Mateu 2023). Recovery
   efficiencies are conditional on the catalogue selection: injecting into a catalogue does not
   model source detection or deblending.
5. **Public data as pre-extracted snippets.** Students have no WSDB access.
   `scripts/build_data.py` queries WSDB (sqlutilpy, q3c, plans checked with `EXPLAIN`) and writes
   small parquet files plus a manifest (query, table, rows, SHA-256). The files are attached to a
   GitHub release of this repository; notebooks download them and check the SHA-256.
6. **Plot + assertion.** Every claim comes with a figure and an `assert` with a tolerance.
7. **Least code that works.** Each notebook is self-contained (runs alone in Colab); small helpers
   are repeated rather than hidden in a package.

## Releases

| Release | Content | Status |
|---|---|---|
| **v0.1** | Ch 00–10: data; object- and population-level star–galaxy separation (SDSS, PS1, LS DR9, HSC vs COSMOS HST); CMDs and isochrones; matched filter; multi-scale search with null calibration; Poisson likelihood; Pal 5 stream; injection–recovery; blind holdout search; all-sky Gaia DR1/DR3 search (Koposov et al. 2017). Pipeline survey: SDSS DR9. | built 2026-10-29 |
| v0.2 | DES DR2 (Reticulum II, Tucana III and its tails); survey ladder to HSC (Leo IV, Virgo I, Boötes IV); Gaia proper motions and membership (Boötes I, Crater 2); luminosity and dwarf/cluster classification. | planned |
| v0.3 | Wide-area stream maps (SDSS "Field of Streams"); GD-1 with Gaia + PS1; star–galaxy III (three-hypothesis likelihood, H_S vs H_G calibrated on held-out clusters); colour + optical–IR classifier; injection including classification losses; DES blind survey. | planned |

## v0.1 chapters

Tolerances are starting budgets, frozen after a development run and before the holdout (Ch 09)
is opened.

| Ch | Notebook | Learning objective | Data | Assert (tolerance) |
|---|---|---|---|---|
| 00 | `00_data` | What WSDB, q3c and a survey catalogue row are; download + SHA-256; magnitudes, errors, extinction (SFD98 with SDSS coefficients, as stored in `phototag`); depth from S/N; a first look at Boötes I (sky map and on/off CMD) | `bootes1_sdss` | checksums; 10σ depth g ∈ [21.5, 23.0]; point-source density inside r_h ≥ 2× background |
| 01 | `01_star_galaxy_objects` | PSF vs extended-model magnitude; SDSS `type`, PS1 psf − kron, LS Tractor `type`, HSC `extendedness`; crossmatch to COSMOS HST (`mu_class`); completeness, galaxy leakage and purity vs magnitude with binomial intervals; a numpy toy image (PSF vs slightly extended profile + noise) showing why faint galaxies look point-like; the stellar locus in g−r vs r−i | `cosmos_hst`, `cosmos_{sdss,ps1,ls,hsc}` | SDSS star completeness > 0.9 at r < 20; SDSS galaxy contamination among "stars" > 20% at 21.5 < r < 22.5; HSC contamination below SDSS's there; toy model: misclassification rises as S/N falls |
| 02 | `02_cmd_isochrones` | CMD, Hess diagrams, on − off subtraction with area scaling; PARSEC isochrones in SDSS bands; distance modulus; a profile likelihood in distance for Boötes I | `bootes1_sdss`, `isochrones_sdss` | Boötes I μ within 0.3 mag of LVDB (19.11) |
| 03 | `03_star_galaxy_populations` | Is an overdensity made of stars? Abell 370 (z = 0.375) vs Boötes I: radial profiles of "stars" in four surveys; on/off colour–colour of the excess; star fraction of the excess from a joint fit of on and off counts; the morphology of the excess | `a370_{sdss,ps1,ls,hsc}`, `bootes1_sdss` | A370 SDSS excess at R < 2′ with p < 1e-6; A370 HSC "stars" at R < 2′: 95% upper limit on density ratio < 2; f★(Boötes I) > 0.7, f★(A370 SDSS) < 0.3, 68% intervals disjoint |
| 04 | `04_matched_filter` | Box cut vs isochrone mask vs signal/background CMD weights (Rockosi+02); a variance-aware statistic S/√B measured on injections, then applied to Boötes I and Pal 5 | `bootes1_sdss`, `pal5_sdss`, `isochrones_sdss` | mean gain of weighted over box statistic > 1 with 95% interval above 1 (200 injections) |
| 05 | `05_overdensity_search` | CMD mask (cells ranked by s/b) and Poisson counts; smoothed maps, background from a 30′ kernel, exact Poisson tail significance; several kernel sizes; distance-modulus scan; search-wide calibration of the maximum with 200 null patches. (Continuous s/b weights failed the null test: sparse high-weight stars.) | `{bootes1,willman1,segue1}_sdss` | each object is the maximum of its patch, within max(1′, 0.5 r_h) of LVDB; its statistic exceeds the 99th percentile of 200 null maxima |
| 06 | `06_likelihood` | Unbinned likelihood: elliptical exponential satellite + uniform background (r_h ≥ 0.5′: the mixture likelihood is unbounded); TS and why √TS is not a Gaussian significance; interval coverage on 200 simulations | `bootes1_sdss`, `isochrones_sdss` | centre within 2′ and ε, PA of LVDB; r_h within 2 combined σ of Martin et al. 2008 (same SDSS data; the deeper LVDB/Muñoz+18 r_h is 30% smaller); r_h coverage in 60–76% |
| 07 | `07_pal5_stream` | A stream as a 1-d overdensity: matched-filter map of the Pal 5 field; rotation to stream coordinates (φ1, φ2); track and width in φ1 bins from a Gaussian + background fit; comparison with the `galstreams` Pal 5 track | `pal5_sdss`, `isochrones_sdss` | rotation round trip < 1e-6 deg; tail excess > 3σ in ≥ 2 disjoint segments on each side; median \|track − galstreams\| < 0.2° |
| 08 | `08_injection_recovery` | Synthetic satellites from an isochrone + IMF, with the SDSS error model and magnitude limit, injected into a real patch; recovery with the Ch 05 search; efficiency vs (M_V, distance) at r_h = 50 pc, conditional on the catalogue selection; 25 injections per cell | `segue1_sdss` (outer field), `isochrones_sdss` | efficiency > 0.9 for M_V = −6 at 50 kpc; < 0.2 for M_V = −2 at 100 kpc |
| 09 | `09_blind_search` | The frozen pipeline run once on a held-out SDSS region (136 deg² searched); threshold from 30 null realisations; candidate reports; unblinding against LVDB and SIMBAD | `holdout_sdss` | Leo IV and Leo V recovered. Outcome: 16 candidates vs ≲ 1 expected from uniform nulls — shredded nearby galaxies (UGC 6903, UGC 6780, NGC 3664) and clustered faint galaxies; the uniform null is too optimistic |
| 10 | `10_gaia_allsky` | All-sky HEALPix counts computed in the database (source_id → HEALPix); Koposov et al. 2017 statistic (kernel density, annulus mean and variance) via spherical harmonics; Fig. 1 reproduced with DR1; kernels 3′/6′/12′; DR3, DR3 without stars with ϖ − 3σ_ϖ > 1 mas, and with 0.3 < BP−RP < 1.3 | `gaia_dr1_counts`, `gaia_dr3_counts`, `lvdb_mw` | Gaia 2 S > 6 (3′), Gaia 1 S > 5 (6′), Crater 2 S > 5 (12′); recovery of known objects and spurious peaks per data version reported |

The holdout region is RA 165°–181°, Dec −3°…+8°. Students are told what it contains only after
running the frozen search.

## Data (v0.1)

All snippets keep native catalogue columns: object ID, `ra`, `dec`, PSF magnitudes and errors,
extinction, and for the star–galaxy files the classifier columns of each survey. SDSS point
sources are `mode = 1 AND type = 6` unless stated. Magnitudes are not dereddened in the files;
notebooks subtract the extinction explicitly.

| File | Content | Area |
|---|---|---|
| `bootes1_sdss` | SDSS point sources, g < 23 | 2° radius around Boötes I |
| `willman1_sdss`, `segue1_sdss` | as above | 1.5° radius |
| `pal5_sdss` | SDSS point sources, −0.3 < g−r < 1.2, g < 23 | RA 222°–244°, Dec −8°…+8° |
| `holdout_sdss` | as `pal5_sdss` | RA 165°–181°, Dec −3°…+8° |
| `a370_{sdss,ps1,ls,hsc}` | all sources with classifier columns | 0.33° radius around Abell 370 |
| `cosmos_hst` | COSMOS ACS: ra, dec, mag_auto (F814W), `mu_class`, `flux_radius` | 0.6° radius |
| `cosmos_{sdss,ps1,ls,hsc}` | all sources with classifier columns | 0.6° radius |
| `isochrones_sdss` | PARSEC 1.2S, SDSS ugriz: log age 9.9–10.1, [Fe/H] −2.1…−1.0 | — |
| `lvdb` | LVDB v1.1.1 (CC0) rows used as references | — |

Every file is listed in `data/MANIFEST.json` (query text, WSDB table, rows, SHA-256, UTC time).
Licences and acknowledgements are listed per product in `data/README.md`.

## Later chapters (v0.2, v0.3)

| Ch | Title | Key data | Key check |
|---|---|---|---|
| 11 | Southern satellites in DES DR2: Reticulum II, Tucana III and its tails — **built** | DES DR2 | Ret II r_h, ε, PA vs LVDB (Mutlu-Pakdil+18); Tuc III tail PA within 10° of Shipp+19 track; both tails > 3σ (measured 10σ) |
| 12 | Faint and deep: the survey ladder (Leo IV, Virgo I, Boötes IV in SDSS, PS1, LS, HSC) — **built** | all | each survey against its own null; HSC recovers Virgo I and Boötes IV, SDSS misses Virgo I; NGC 4030 shredded-galaxy peak noted |
| 13 | Gaia proper motions and membership (Pace & Li 19): Boötes I, Crater 2 — **built** | Gaia DR3 | systemic PM within the 99% ellipse of LVDB (Pace+22) incl. 0.025 mas/yr systematic floor (Vasiliev & Baumgardt 21); measured χ² 0.05 (Boötes I) |
| 13 | Luminosity and classification | — | M_V posterior coverage on stochastic simulations |
| 14 | Wide-area stream maps | SDSS HEALPix count maps | excess in two disjoint segments vs control strips |
| 15 | GD-1 with Gaia + PS1 | Gaia DR3, PS1 | independently fitted track vs `galstreams` on held-out bins |
| 16 | Star–galaxy III: a three-hypothesis likelihood | redMaPPer clusters, satellites | classification tested on held-out clusters and satellites |
| 17 | Injection with classification losses; DES blind survey | DES DR2 | ≥ 1000 simulated null regions; zero exceedances reported as ≤ 3/N |

## Repository layout

```
notebooks/      NN_<slug>.ipynb, committed without outputs, each runs standalone in Colab
scripts/        build_data.py (WSDB → parquet + manifest; instructor only)
data/           README.md (licences, columns) and MANIFEST.json; parquet files are release assets
tests/          pytest tests
prototypes/     exploratory scripts (not part of the book)
_config.yml, _toc.yml, intro.md   Jupyter Book
.github/workflows/book.yml        tests, executes notebooks, publishes to GitHub Pages
```

## Testing

- `pytest tests/ --nbmake notebooks/` executes every notebook in a fresh kernel; notebooks contain
  explicit `assert` cells. `jupyter-book build . -W -n --keep-going` builds the site.
- Both run in CI on every push; fixed random seeds.

## Literature (checked in ADS)

Satellites: Willman+05 https://doi.org/10.1086/431760 ·
Belokurov+07 https://ui.adsabs.harvard.edu/abs/2007ApJ...654..897B ·
Koposov+08 https://arxiv.org/abs/0706.2687 · Tollerud+08 https://arxiv.org/abs/0806.4381 ·
Martin+08 https://arxiv.org/abs/0805.2945 · Walsh+09 https://doi.org/10.1088/0004-6256/137/1/450 ·
Bechtol+15 https://arxiv.org/abs/1503.02584 · Koposov+15 https://doi.org/10.1088/0004-637X/805/2/130 ·
Antoja+15 https://ui.adsabs.harvard.edu/abs/2015MNRAS.453..541A ·
Torrealba+16 https://arxiv.org/abs/1601.07178 · Homma+16 https://ui.adsabs.harvard.edu/abs/2016ApJ...832...21H ·
Koposov+17 https://arxiv.org/abs/1702.01122 · Homma+19 https://ui.adsabs.harvard.edu/abs/2019PASJ...71...94H ·
Pace & Li 19 https://arxiv.org/abs/1806.02345 · Torrealba+19 https://arxiv.org/abs/1811.04082 ·
Simon 19 https://arxiv.org/abs/1901.05465 · Drlica-Wagner+20 https://doi.org/10.3847/1538-4357/ab7eb9 ·
Cerny+23 https://arxiv.org/abs/2209.12422 · Tan+26 https://ui.adsabs.harvard.edu/abs/2026ApJ..1000...87T ·
McConnachie 12 https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M ·
Pace 25 (Local Volume Database) https://ui.adsabs.harvard.edu/abs/2025OJAp....8E.142P

Star–galaxy separation: Stoughton+02 https://ui.adsabs.harvard.edu/abs/2002AJ....123..485S ·
Leauthaud+07 (COSMOS HST) https://ui.adsabs.harvard.edu/abs/2007ApJS..172..219L ·
Covey+07 https://ui.adsabs.harvard.edu/abs/2007AJ....134.2398C ·
Baldry+10 https://ui.adsabs.harvard.edu/abs/2010MNRAS.404...86B ·
Henrion+11 https://ui.adsabs.harvard.edu/abs/2011MNRAS.412.2286H ·
Desai+12 https://ui.adsabs.harvard.edu/abs/2012ApJ...757...83D ·
Fadely+12 https://ui.adsabs.harvard.edu/abs/2012ApJ...760...15F ·
Farrow+14 https://ui.adsabs.harvard.edu/abs/2014MNRAS.437..748F ·
Rykoff+14 (redMaPPer) https://ui.adsabs.harvard.edu/abs/2014ApJ...785..104R ·
Kim+15 https://ui.adsabs.harvard.edu/abs/2015MNRAS.453..507K ·
Kovács & Szapudi 15 https://ui.adsabs.harvard.edu/abs/2015MNRAS.448.1305K ·
Lang+16 (Tractor) https://ui.adsabs.harvard.edu/abs/2016ascl.soft04008L ·
Suchyta+16 https://ui.adsabs.harvard.edu/abs/2016MNRAS.457..786S ·
Bosch+18 https://ui.adsabs.harvard.edu/abs/2018PASJ...70S...5B ·
Sevilla-Noarbe+18 https://ui.adsabs.harvard.edu/abs/2018MNRAS.481.5451S ·
Tachibana & Miller 18 https://ui.adsabs.harvard.edu/abs/2018PASP..130l8001T ·
Slater+20 https://ui.adsabs.harvard.edu/abs/2020AJ....159...65S ·
Delchambre+23 https://ui.adsabs.harvard.edu/abs/2023A&A...674A..31D ·
SDSS classification https://classic.sdss.org/dr6/algorithms/classify.php ·
HSC star–galaxy separation https://hsc-release.mtk.nao.ac.jp/doc/index.php/stargalaxy-separation/

Streams and debris: Odenkirchen+01 https://ui.adsabs.harvard.edu/abs/2001ApJ...548L.165O ·
Rockosi+02 https://ui.adsabs.harvard.edu/abs/2002AJ....124..349R ·
Majewski+03 https://ui.adsabs.harvard.edu/abs/2003ApJ...599.1082M ·
Grillmair & Dionatos 06 https://ui.adsabs.harvard.edu/abs/2006ApJ...643L..17G ·
Belokurov+06 https://ui.adsabs.harvard.edu/abs/2006ApJ...642L.137B ·
Belokurov+07 (Hercules-Aquila) https://ui.adsabs.harvard.edu/abs/2007ApJ...657L..89B ·
Jurić+08 https://ui.adsabs.harvard.edu/abs/2008ApJ...673..864J ·
Bernard+16 https://ui.adsabs.harvard.edu/abs/2016MNRAS.463.1759B ·
Shipp+18 https://ui.adsabs.harvard.edu/abs/2018ApJ...862..114S ·
Malhan & Ibata 18 https://ui.adsabs.harvard.edu/abs/2018MNRAS.477.4063M ·
Price-Whelan & Bonaca 18 https://ui.adsabs.harvard.edu/abs/2018ApJ...863L..20P ·
Koposov+19 https://ui.adsabs.harvard.edu/abs/2019MNRAS.485.4726K ·
Erkal+19 https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.2685E ·
Ibata+21 https://ui.adsabs.harvard.edu/abs/2021ApJ...914..123I ·
Li+21 https://ui.adsabs.harvard.edu/abs/2021ApJ...911..149L ·
Shih+22 https://ui.adsabs.harvard.edu/abs/2022MNRAS.509.5992S ·
Pearson+22 https://ui.adsabs.harvard.edu/abs/2022ApJ...926..166P ·
Mateu 23 (galstreams) https://ui.adsabs.harvard.edu/abs/2023MNRAS.520.5225M

Surveys: Chambers+16 (PS1) https://ui.adsabs.harvard.edu/abs/2016arXiv161205560C ·
Dey+19 (Legacy Surveys) https://ui.adsabs.harvard.edu/abs/2019AJ....157..168D ·
Abbott+21 (DES DR2) https://ui.adsabs.harvard.edu/abs/2021ApJS..255...20A ·
Aihara+22 (HSC PDR3) https://ui.adsabs.harvard.edu/abs/2022PASJ...74..247A ·
q3c: Koposov & Bartunov 06 https://ui.adsabs.harvard.edu/abs/2006ASPC..351..735K

## Open items

- Provenance of `koposov_public.{cfht,cosmos}_sdss_sg` (ask S. Koposov); not used in v0.1.
- HSC PDR3 redistribution: archive allows non-commercial scientific/educational use; no explicit
  redistribution clause. The data release is therefore CC BY-NC 4.0.
- Pal 5 core deficit in LS (crowding): a stated limitation.
- Isochrone colour terms for HSC and LS North (needed in v0.2).
