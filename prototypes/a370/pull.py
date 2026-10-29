"""Pull point sources around Abell 370 (z=0.375) from five public surveys; cache to npz."""
import os, numpy as np, sqlutilpy as sqlutil
RA, DEC, R = 39.970, -1.577, 0.33
C = f"q3c_radial_query(ra, dec, {RA}, {DEC}, {R})"
Q = {
 'SDSS': f"SELECT ra, dec, psfmag_g g, psfmag_r r, psfmag_i i FROM sdssdr9.phototag WHERE {C} AND mode=1 AND type=6",
 'PS1':  f"SELECT ra, dec, gpsfmag g, rpsfmag r, ipsfmag i FROM panstarrs_dr1.stackobjectthin WHERE {C} AND primarydetection=1 AND rpsfmag>0 AND rkronmag>0 AND rpsfmag-rkronmag<0.05",
 'LS DR9': f"SELECT ra, dec, 22.5-2.5*log(greatest(flux_g,1e-3)) g, 22.5-2.5*log(greatest(flux_r,1e-3)) r, 22.5-2.5*log(greatest(flux_z,1e-3)) i FROM decals_dr9.main WHERE {C} AND type='PSF'",
 'DES DR2': f"SELECT ra, dec, wavg_mag_psf_g g, wavg_mag_psf_r r, wavg_mag_psf_i i FROM des_dr2.main WHERE {C} AND extended_class_coadd BETWEEN 0 AND 1",
 'HSC': f"SELECT ra, dec, g_psfflux_mag g, r_psfflux_mag r, i_psfflux_mag i FROM hsc_dr3.wide_summary_small WHERE {C} AND i_extendedness_value=0",
}
os.makedirs('cache', exist_ok=True)
for k, q in Q.items():
    f = f"cache/{k.replace(' ', '_')}.npz"
    if os.path.exists(f): continue
    d = sqlutil.get(q, asDict=True)
    np.savez_compressed(f, **d); print(k, len(d['ra']))
