"""Build the data files of the tutorial from WSDB; they are attached to a GitHub release, not stored in git.

Usage:  python scripts/build_data.py [name ...|all]   (writes data_build/<name>.parquet and data/MANIFEST.json)

Needs access to WSDB (Cambridge) through sqlutilpy. Every query goes through q3c, and its plan is checked
with EXPLAIN before it runs (a sequential scan of a survey table is refused). The same public tables can be
queried elsewhere (SDSS SkyServer, MAST for PS1, NOIRLab Astro Data Lab for Legacy Surveys, the HSC-SSP
archive, IRSA for COSMOS), so the SQL below documents each selection exactly.

Magnitudes are stored as observed (not dereddened); extinction is stored separately. Missing values are NaN.
"""
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import sqlutilpy as sqlutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data_build"
MANIFEST = ROOT / "data" / "MANIFEST.json"

# Centres: Local Volume Database v1.1.1 (Pace 2025); Abell 370 and COSMOS field centres.
CONES = {"bootes1": (210.0200, 14.5135, 2.0), "willman1": (162.3436, 51.0501, 1.5),
         "segue1": (151.7504, 16.0756, 1.5), "a370": (39.970, -1.577, 0.33), "cosmos": (150.12, 2.21, 0.6)}
BOXES = {"pal5": (222.0, 244.0, -8.0, 8.0), "holdout": (165.0, 181.0, -3.0, 8.0)}  # ra_min, ra_max, dec_min, dec_max

SDSS_STAR = """objid, ra, dec, psfmag_g, psfmag_r, psfmag_i, psfmagerr_g, psfmagerr_r, psfmagerr_i,
               extinction_g, extinction_r, extinction_i"""
SDSS_ALL = SDSS_STAR + ", type, cmodelmag_g, cmodelmag_r, cmodelmag_i, psfmag_z"
PS1 = """s.objid, s.ra, s.dec, s.gpsfmag, s.rpsfmag, s.ipsfmag, s.zpsfmag, s.gpsfmagerr, s.rpsfmagerr,
         s.ipsfmagerr, s.rkronmag, s.ikronmag, s.ebv, h.ps_score"""
LS = """release, brickid, objid, type, ra, dec, flux_g, flux_r, flux_z, flux_w1, flux_ivar_g, flux_ivar_r,
        flux_ivar_z, flux_ivar_w1, mw_transmission_g, mw_transmission_r, mw_transmission_z, mw_transmission_w1,
        dchisq_1, dchisq_2, psfsize_r, maskbits"""
HSC = """object_id, ra, dec, g_psfflux_mag, r_psfflux_mag, i_psfflux_mag, z_psfflux_mag, g_psfflux_magerr,
         r_psfflux_magerr, i_psfflux_magerr, g_cmodel_mag, r_cmodel_mag, i_cmodel_mag,
         g_extendedness_value, r_extendedness_value, i_extendedness_value"""
# Legacy Surveys DR9: the north (release 9011) and south (9010) overlap; keep one of each pair (WSDB note).
LS_DEDUP = "((release = 9011 AND dec > 32.375) OR (release != 9011 AND dec < 32.375))"


def cone(name):
    ra, dec, r = CONES[name]
    return f"q3c_radial_query(ra, dec, {ra}, {dec}, {r})"


def box_tiles(name, width=2.0):
    """q3c polygons of `width`-degree RA strips covering a box (q3c polygons must be < ~25 deg across)."""
    r0, r1, d0, d1 = BOXES[name]
    for a in np.arange(r0, r1, width):
        b = min(a + width, r1)
        yield f"q3c_poly_query(ra, dec, ARRAY[{a}, {d0}, {b}, {d0}, {b}, {d1}, {a}, {d1}])"


def sdss_points(where, extra=""):
    return f"""SELECT {SDSS_STAR} FROM sdssdr9.phototag
               WHERE {where} AND mode = 1 AND type = 6 AND psfmag_g < 23 {extra}"""


COLOUR = "AND psfmag_g - psfmag_r BETWEEN -0.3 AND 1.2 AND psfmag_g < 22.5"
QUERIES = {
    **{f"{n}_sdss": [sdss_points(cone(n))] for n in ("bootes1", "willman1", "segue1")},
    **{f"{n}_sdss": [sdss_points(t, COLOUR) for t in box_tiles(n)] for n in BOXES},
    **{f"{n}_sdss": [f"SELECT {SDSS_ALL} FROM sdssdr9.phototag WHERE {cone(n)} AND mode = 1 AND psfmag_r < 24"]
       for n in ("a370", "cosmos")},
    **{f"{n}_ps1": [f"""WITH s AS MATERIALIZED (SELECT * FROM panstarrs_dr1.stackobjectthin
                                                WHERE {cone(n)} AND primarydetection = 1)
                        SELECT {PS1} FROM s LEFT JOIN panstarrs_dr1.hlsp h ON h.objid = s.objid"""]
       for n in ("a370", "cosmos")},
    **{f"{n}_ls": [f"""SELECT {LS} FROM decals_dr9.main WHERE {cone(n)} AND {LS_DEDUP}
                       AND flux_r > 0 AND 22.5 - 2.5 * log(flux_r) < 24"""] for n in ("a370", "cosmos")},
    **{f"{n}_hsc": [f"SELECT {HSC} FROM hsc_dr3.wide_summary_small WHERE {cone(n)} AND r_psfflux_mag < 25"]
       for n in ("a370", "cosmos")},
    "cosmos_hst": [f"""SELECT ra, dec, mag_auto, mu_class, flux_radius, class_star FROM cosmos.hstcat
                       WHERE {cone('cosmos')} AND mag_auto < 25.5"""],
    "isochrones_sdss": ["""SELECT logage, feh, m_ini, int_imf, stage, u, g, r, i, z
                           FROM isochrones.girardi_sdss_ugriz_1601
                           WHERE logage BETWEEN 9.89 AND 10.11 AND feh BETWEEN -2.11 AND -0.99
                           ORDER BY logage, feh, m_ini"""],
}

# v0.2: southern satellites in DES DR2 (Chapter 11) and the survey ladder (Chapter 12).
# DES DR2 point sources: extended_class_coadd 0 or 1 (high-confidence and likely stars).
CONES.update({"retii": (53.9203, -54.0513, 2.0), "tuc3": (359.1075, -59.5833, 4.5),
              "leo4": (173.2405, -0.5453, 0.75), "virgo1": (180.0380, -0.6810, 0.75), "bootes4": (233.6890, 43.7260, 0.75)})
DES = """coadd_object_id, ra, dec, wavg_mag_psf_g, wavg_mag_psf_r, wavg_mag_psf_i, wavg_magerr_psf_g,
         wavg_magerr_psf_r, wavg_magerr_psf_i, ebv_sfd98"""
QUERIES.update({
    "retii_des": [f"""SELECT {DES} FROM des_dr2.main WHERE {cone('retii')} AND extended_class_coadd BETWEEN 0 AND 1
                      AND wavg_mag_psf_g < 24 AND wavg_mag_psf_r < 24"""],
    "tuc3_des": [f"""SELECT {DES} FROM des_dr2.main WHERE {cone('tuc3')} AND extended_class_coadd BETWEEN 0 AND 1
                     AND wavg_mag_psf_g < 24 AND wavg_mag_psf_g - wavg_mag_psf_r BETWEEN -0.3 AND 1.0"""],
    "isochrones_des": ["""SELECT logage, feh, m_ini, int_imf, stage, g, r, i, z
                          FROM isochrones.girardi_des_ugrizy_1601
                          WHERE logage BETWEEN 9.89 AND 10.11 AND feh BETWEEN -2.11 AND -0.99
                          ORDER BY logage, feh, m_ini"""],
    "isochrones_ps1": ["""SELECT logage, feh, m_ini, int_imf, stage, g, r, i, z
                          FROM isochrones.girardi_panstarrs_grizy_1701
                          WHERE logage BETWEEN 9.89 AND 10.11 AND feh BETWEEN -2.11 AND -0.99
                          ORDER BY logage, feh, m_ini"""],
})
# Chapter 13: Gaia DR3 astrometry around Boötes I (1.5 deg) and Crater 2 (2.5 deg), with the full PM covariance.
CONES.update({"bootes1_gaia": (210.0200, 14.5135, 1.5), "crater2_gaia": (177.3100, -18.4130, 2.5)})
GAIA_AST = """source_id, ra, dec, parallax, parallax_error, pmra, pmra_error, pmdec, pmdec_error, pmra_pmdec_corr,
              phot_g_mean_mag, bp_rp, ruwe, astrometric_excess_noise, phot_bp_rp_excess_factor"""
QUERIES["isochrones_gaia"] = ["""SELECT age, feh, mini, label, gmag, g_bpmag, g_rpmag FROM isochrones.gaia_1804
                                 WHERE age >= 1e10 AND feh <= -1.0 ORDER BY age, feh, mini"""]
for n in ("bootes1_gaia", "crater2_gaia"):
    QUERIES[n] = [f"""SELECT {GAIA_AST} FROM gaia_dr3.gaia_source WHERE {cone(n)}
                      AND pmra IS NOT NULL AND phot_g_mean_mag < 21"""]

# The ladder: point sources by each survey's own classifier, to each survey's depth.
for n in ("leo4", "virgo1", "bootes4"):
    QUERIES[f"{n}_sdss"] = [sdss_points(cone(n))]
    QUERIES[f"{n}_ps1"] = [f"""SELECT objid, ra, dec, gpsfmag, rpsfmag, ipsfmag, gpsfmagerr, rpsfmagerr, ebv
                               FROM panstarrs_dr1.stackobjectthin WHERE {cone(n)} AND primarydetection = 1
                               AND rpsfmag > 0 AND rkronmag > 0 AND rpsfmag - rkronmag < 0.05 AND gpsfmag BETWEEN 0 AND 23.5"""]
    QUERIES[f"{n}_ls"] = [f"""SELECT release, brickid, objid, ra, dec, flux_g, flux_r, flux_z, flux_ivar_g, flux_ivar_r,
                              mw_transmission_g, mw_transmission_r, ebv FROM decals_dr9.main
                              WHERE {cone(n)} AND {LS_DEDUP} AND type = 'PSF' AND flux_g > 0 AND flux_r > 0
                              AND 22.5 - 2.5 * log(flux_g) < 24.5"""]
    QUERIES[f"{n}_hsc"] = [f"""SELECT object_id, ra, dec, g_psfflux_mag, r_psfflux_mag, i_psfflux_mag, g_psfflux_magerr,
                               r_psfflux_magerr FROM hsc_dr3.wide_summary_small WHERE {cone(n)}
                               AND i_extendedness_value = 0 AND g_psfflux_mag < 25.5"""]
# Coverage of each SDSS file: counts of all primary objects (any type, r < 22) in 0.1 x 0.1 deg cells.
COVERAGE = "SELECT floor(ra / 0.1)::int AS ira, floor(dec / 0.1)::int AS idec, count(*) AS n FROM sdssdr9.phototag " \
           "WHERE {where} AND mode = 1 AND psfmag_r < 22 GROUP BY 1, 2"
LVDB_URL = "https://github.com/apace7/local_volume_database/releases/download/v1.1.1/comb_all.csv"
LVDB_KEYS = ["bootes_1", "willman_1", "segue_1", "palomar_05", "leo_4", "leo_5", "virgo_1", "reticulum_2", "tucana_3"]


def check_plan(q):
    """Refuse a query whose plan sequentially scans a large table (i.e. misses the q3c index)."""
    if "isochrones" in q:
        return
    plan = "\n".join(r[0] for r in zip(*sqlutil.get("EXPLAIN " + q, batched=False)))
    if "Seq Scan" in plan:
        raise RuntimeError("plan contains a sequential scan:\n" + plan)


def save(name, df, queries):
    OUT.mkdir(exist_ok=True)
    for c in df.columns:                      # float32 for everything except positions; sentinels -> NaN
        if df[c].dtype.kind == "f":
            v = df[c].to_numpy()
            v = np.where(v <= -900, np.nan, v)
            df[c] = v if c in ("ra", "dec") else v.astype(np.float32)
    path, tmp = OUT / f"{name}.parquet", OUT / f"{name}.parquet.tmp"
    df.to_parquet(tmp, compression="zstd", index=False)
    tmp.replace(path)                          # atomic: an interrupted run never leaves a partial file
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    man[name] = {"rows": len(df), "bytes": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "columns": list(df.columns), "queries": [" ".join(q.split()) for q in queries]}
    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(dict(sorted(man.items())), indent=1))
    print(f"{name}: {len(df):,} rows, {path.stat().st_size / 1e6:.1f} MB")


def build(name):
    t = time.time()
    if name in GAIA_COUNTS:
        return build_gaia_counts(name)
    if name in ("lvdb", "lvdb_mw", "lvdb_pm"):
        csv = urllib.request.urlopen(LVDB_URL).read().decode()
        d = pd.read_csv(StringIO(csv))
        if name == "lvdb":
            return save(name, d[d.key.isin(LVDB_KEYS)].reset_index(drop=True), [LVDB_URL])
        if name == "lvdb_pm":                                    # Chapter 13: published files are never changed in place
            return save(name, d[d.key.isin(["bootes_1", "crater_2"])].reset_index(drop=True), [LVDB_URL])
        # all Milky Way satellites and star clusters (host = mw), a few columns
        cols = ["key", "name", "ra", "dec", "distance_modulus", "rhalf", "M_V", "confirmed_galaxy", "confirmed_star_cluster", "table"]
        return save(name, d.loc[d.host == "mw", cols].reset_index(drop=True), [LVDB_URL + "  (host == 'mw')"])
    if name.endswith("_coverage"):
        base = name.removesuffix("_coverage")
        wheres = list(box_tiles(base)) if base in BOXES else [cone(base)]
        queries = [COVERAGE.format(where=w) for w in wheres]
    else:
        queries = QUERIES[name]
    parts = []
    for q in queries:
        check_plan(q)
        parts.append(pd.DataFrame(sqlutil.get(q, asDict=True, intNullVal=-1)))
    df = pd.concat(parts, ignore_index=True)
    if name.endswith("_coverage"):            # strips can share a cell column at their boundary: sum them
        df = df.groupby(["ira", "idec"], as_index=False)["n"].sum()
    print(f"  query time {time.time() - t:.1f} s")
    return save(name, df, queries)


# All-sky Gaia star counts on a HEALPix nside = 1024 (nested) grid, computed in the database so that no star
# is downloaded. A Gaia source_id encodes the nested level-12 HEALPix index: source_id // 2**35; dividing by
# 2**39 gives level 10 (nside 1024, 3.4 arcmin pixels). The selection follows Koposov, Belokurov & Torrealba
# (2017, MNRAS 470, 2702, Eq. 1): 17 < G < 21 and astrometric_excess_noise below 10**(0.15 (G - 15) + 0.25).
# The sky is processed in the 3072 nside-16 pixels (source_id ranges of 2**51), 4 at a time, resumably.
GAIA_CUT = "phot_g_mean_mag BETWEEN 17 AND 21 AND astrometric_excess_noise < power(10, 0.15 * (phot_g_mean_mag - 15) + 0.25)"
# DR3 variants, all in one pass: (b) drop stars whose parallax places them significantly within 1 kpc;
# (c) also keep only 0.3 < BP-RP < 1.3 (stars without BP-RP are dropped). COALESCE: a NULL parallax must count as "not near".
NEAR = "COALESCE(parallax - 3 * parallax_error > 1, false)"
GAIA_COUNTS = {
    "gaia_dr1_counts": ("gaia_dr1.gaia_source", "count(*) AS n_k17"),
    "gaia_dr3_counts": ("gaia_dr3.gaia_source",
                        f"count(*) AS n_k17, count(*) FILTER (WHERE NOT {NEAR}) AS n_far, "
                        f"count(*) FILTER (WHERE NOT {NEAR} AND bp_rp BETWEEN 0.3 AND 1.3) AS n_far_cmd"),
}


def build_gaia_counts(name, workers=4):
    from concurrent.futures import ThreadPoolExecutor
    table, counts = GAIA_COUNTS[name]
    step = 2**51
    q = (f"SELECT source_id / {2**39} AS hpx, {counts} FROM {table} "
         f"WHERE source_id >= %s AND source_id < %s AND {GAIA_CUT} GROUP BY 1")
    partial = OUT / f"{name}.partial.pkl"
    done = pd.read_pickle(partial) if partial.exists() else {}
    todo = [k for k in range(3072) if k not in done]

    def run(k):
        return k, pd.DataFrame(sqlutil.get(q, (k * step, (k + 1) * step), asDict=True))

    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(workers) as ex:
        for i, (k, df) in enumerate(ex.map(run, todo)):
            done[k] = df
            if i % 100 == 99 or len(done) == 3072:
                pd.to_pickle(done, partial)
                print(f"  {len(done)}/3072 chunks", flush=True)
    df = pd.concat(done.values(), ignore_index=True).sort_values("hpx", ignore_index=True)
    df = df.astype({c: np.int32 for c in df.columns})
    save(name, df, [q.replace("%s", "{lo}", 1).replace("%s", "{hi}", 1) + f"  -- for lo = k * 2**51, hi = lo + 2**51, k = 0..3071"])
    partial.unlink()


ALL = list(QUERIES) + [f"{n}_coverage" for n in ("bootes1", "willman1", "segue1", "pal5", "holdout")] + ["lvdb", "lvdb_mw", "lvdb_pm"] \
      + list(GAIA_COUNTS)

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    for n in (ALL if names == ["all"] else names):
        build(n)
