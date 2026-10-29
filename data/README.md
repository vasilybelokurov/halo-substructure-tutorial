# Data for the halo-substructure tutorial

Small extracts of public survey catalogues, prepared for the notebooks of
https://github.com/vasilybelokurov/halo-substructure-tutorial and attached to its
[`data-v0.1` release](https://github.com/vasilybelokurov/halo-substructure-tutorial/releases/tag/data-v0.1).
Despite its name, the release holds the data of every chapter built so far (0–13). Files are only added to it, never
replaced: a changed selection is published under a new name, so a checksum in `MANIFEST.json` never changes.

Every file is rebuilt by `scripts/build_data.py`, which ran the queries on WSDB (Cambridge) using q3c sky indexing
(Koposov & Bartunov 2006, https://ui.adsabs.harvard.edu/abs/2006ASPC..351..735K). `MANIFEST.json` lists, for each file,
the exact SQL, the row count, the size, the SHA-256 checksum and the creation time. Every query plan was checked to use
the sky index before running.

Format: Apache Parquet (zstd). Read with `pandas.read_parquet(path)`. Angles in degrees; magnitudes as published by each
survey (not dereddened; extinction is given separately); Legacy Surveys fluxes in nanomaggies
(m = 22.5 − 2.5 log10 flux); values ≤ −900 (missing-value sentinels, e.g. PS1's −999) are replaced by NaN.
Floating-point columns are float32 except `ra` and `dec`.

## Files

| File | Content |
|---|---|
| `bootes1_sdss`, `willman1_sdss`, `segue1_sdss` | SDSS DR9 primary point sources (`mode = 1`, `type = 6`), g < 23, within 2° / 1.5° / 1.5° of Boötes I / Willman 1 / Segue 1 |
| `pal5_sdss`, `holdout_sdss` | SDSS DR9 point sources with −0.3 < g − r < 1.2, g < 22.5, in RA 222°–244°, Dec −8°…+8° (Pal 5) and RA 165°–181°, Dec −3°…+8° |
| `*_coverage` | counts of all SDSS primary objects (any type, r < 22) in 0.1° × 0.1° cells (`ira = floor(ra/0.1)`, `idec = floor(dec/0.1)`): where SDSS observed |
| `a370_{sdss,ps1,ls,hsc}` | all sources within 0.33° of the galaxy cluster Abell 370, with each survey's star–galaxy information |
| `cosmos_{sdss,ps1,ls,hsc}` | the same within 0.6° of the COSMOS field centre (150.12°, 2.21°) |
| `cosmos_hst` | COSMOS HST/ACS catalogue (Leauthaud et al. 2007): position, F814W `mag_auto` < 25.5, `mu_class` (1 galaxy, 2 star, 3 artifact), `flux_radius`, `class_star` |
| `isochrones_sdss` | PARSEC 1.2S isochrones (Bressan et al. 2012) in SDSS ugriz, log age 9.9–10.1, [Fe/H] −2.1 to −1.0 |
| `isochrones_des`, `isochrones_ps1` | the same grid in DES (DECam) griz and Pan-STARRS1 griz |
| `isochrones_gaia` | PARSEC isochrones in Gaia G, BP, RP: age ≥ 10 Gyr, [Fe/H] ≤ −1.0 (WSDB `isochrones.gaia_1804`) |
| `retii_des`, `tuc3_des` | DES DR2 point sources (`extended_class_coadd` 0 or 1), g < 24, within 2° of Reticulum II (also r < 24) and 4.5° of Tucana III (−0.3 < g − r < 1.0) |
| `{leo4,virgo1,bootes4}_{sdss,ps1,ls,hsc}` | point sources by each survey's own classifier, within 0.75° of Leo IV, Virgo I, Boötes IV: SDSS `type = 6`, g < 23; PS1 r_PSF − r_Kron < 0.05, g < 23.5; LS DR9 `type = 'PSF'`, g < 24.5; HSC `i_extendedness_value = 0`, g < 25.5 |
| `bootes1_gaia`, `crater2_gaia` | Gaia DR3 sources with a proper motion and G < 21 within 1.5° of Boötes I and 2.5° of Crater 2, with astrometric errors, the pmra–pmdec correlation and quality columns |
| `lvdb` | rows of the Local Volume Database v1.1.1 (Pace 2025) for the objects used in Chapters 0–12 |
| `lvdb_mw` | all Milky Way satellites and star clusters of LVDB v1.1.1 (`host = mw`): key, name, position, distance modulus, r_h, M_V, classification |
| `lvdb_pm` | the LVDB v1.1.1 rows (all columns, including proper motions) for Boötes I and Crater 2 |
| `gaia_dr1_counts`, `gaia_dr3_counts` | all-sky Gaia star counts on a HEALPix nside = 1024 nested grid (selection in `scripts/build_data.py`) |

Survey-specific columns: SDSS `psfmag_*`, `psfmagerr_*`, `cmodelmag_*`, `extinction_*` (SFD98 × SDSS coefficients), `type`;
PS1 stack `*psfmag`, `*kronmag`, `ebv`, and `ps_score` (Tachibana & Miller 2018); Legacy Surveys DR9 Tractor `type`,
`flux_*`, `flux_ivar_*`, `mw_transmission_*`, `dchisq_1/2` (χ² improvement of PSF/REX over no source), `psfsize_r`,
`maskbits` (the ladder files also `ebv`; north/south duplicates removed with `(release = 9011 AND dec > 32.375) OR (release != 9011 AND dec < 32.375)`);
HSC PDR3 Wide `*_psfflux_mag`, `*_cmodel_mag`, `*_extendedness_value`; DES DR2 `wavg_mag_psf_*`, `wavg_magerr_psf_*`,
`ebv_sfd98`; Gaia DR3 `parallax`, `pmra`, `pmdec` and errors, `pmra_pmdec_corr`, `phot_g_mean_mag`, `bp_rp`, `ruwe`,
`astrometric_excess_noise`, `phot_bp_rp_excess_factor`.

## Licences and terms

The files are distributed under **CC BY-NC 4.0** because the most restrictive component, HSC-SSP PDR3, may be used
for non-commercial scientific and educational purposes only. Per product:

| Product | Terms | Please cite |
|---|---|---|
| SDSS DR9 | public data; acknowledge SDSS-III | Ahn et al. 2012, https://ui.adsabs.harvard.edu/abs/2012ApJS..203...21A |
| Pan-STARRS1 DR1 | public data; acknowledge PS1 | Chambers et al. 2016, https://ui.adsabs.harvard.edu/abs/2016arXiv161205560C ; Flewelling et al. 2020, https://ui.adsabs.harvard.edu/abs/2020ApJS..251....7F ; `ps_score`: Tachibana & Miller 2018, https://ui.adsabs.harvard.edu/abs/2018PASP..130l8001T |
| Legacy Surveys DR9 | public data; acknowledge the Legacy Surveys | Dey et al. 2019, https://ui.adsabs.harvard.edu/abs/2019AJ....157..168D |
| DES DR2 | public data; acknowledge DES | Abbott et al. 2021, https://ui.adsabs.harvard.edu/abs/2021ApJS..255...20A |
| HSC-SSP PDR3 | non-commercial scientific/educational use (HSC data archive terms) | Aihara et al. 2022, https://ui.adsabs.harvard.edu/abs/2022PASJ...74..247A |
| COSMOS HST/ACS | public data (IRSA) | Scoville et al. 2007, https://ui.adsabs.harvard.edu/abs/2007ApJS..172....1S ; Koekemoer et al. 2007, https://ui.adsabs.harvard.edu/abs/2007ApJS..172..196K ; Leauthaud et al. 2007, https://ui.adsabs.harvard.edu/abs/2007ApJS..172..219L |
| Gaia DR1, DR3 | open, with ESA/Gaia/DPAC credit | Gaia Collaboration 2016, https://ui.adsabs.harvard.edu/abs/2016A&A...595A...1G ; DR1: https://ui.adsabs.harvard.edu/abs/2016A&A...595A...2G ; DR3: https://ui.adsabs.harvard.edu/abs/2023A&A...674A...1G |
| PARSEC isochrones | public | Bressan et al. 2012, https://ui.adsabs.harvard.edu/abs/2012MNRAS.427..127B |
| Local Volume Database v1.1.1 | CC0 | Pace 2025, https://ui.adsabs.harvard.edu/abs/2025OJAp....8E.142P |

Redistribution terms for catalogue extracts are not stated explicitly by every survey; if you are a data owner and
object to these extracts, please open an issue.

## Acknowledgements

Funding for SDSS-III has been provided by the Alfred P. Sloan Foundation, the Participating Institutions, the National
Science Foundation, and the U.S. Department of Energy Office of Science (https://www.sdss3.org). The Pan-STARRS1 Surveys
and the PS1 public science archive have been made possible through contributions by the Institute for Astronomy, the
University of Hawaii, the Pan-STARRS Project Office, the Max-Planck Society and its participating institutes, and many
others (https://outerspace.stsci.edu/display/PANSTARRS/). The Legacy Surveys acknowledgement is at
https://www.legacysurvey.org/acknowledgment/. The Hyper Suprime-Cam (HSC) collaboration includes the astronomical
communities of Japan and Taiwan, and Princeton University (https://hsc-release.mtk.nao.ac.jp). This work has made use of
data from the European Space Agency (ESA) mission Gaia (https://www.cosmos.esa.int/gaia), processed by the Gaia Data
Processing and Analysis Consortium (DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium). Based on observations
with the NASA/ESA Hubble Space Telescope (COSMOS). The Dark Energy Survey acknowledgement is given in Abbott et al. (2021,
https://ui.adsabs.harvard.edu/abs/2021ApJS..255...20A).
