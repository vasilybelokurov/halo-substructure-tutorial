"""Radial profile of 'point sources' around Abell 370 and CMD/colour-colour of the central excess."""
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
RA, DEC = 39.970, -1.577
S = ['SDSS', 'PS1', 'LS DR9', 'DES DR2', 'HSC']
edges = np.array([0, 1, 2, 4, 8, 19.8])                          # arcmin
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
res = {}
for k in S:
    d = np.load(f"cache/{k.replace(' ', '_')}.npz")
    g, r, i = d['g'], d['r'], d['i']
    ok = np.isfinite(g) & np.isfinite(r) & (r > 14) & (r < 23.0) & (g > 0) & (g < 30)
    x = (d['ra'] - RA) * np.cos(np.radians(DEC)) * 60; y = (d['dec'] - DEC) * 60
    R = np.hypot(x, y)[ok]
    n, _ = np.histogram(R, edges); area = np.pi * np.diff(edges**2)
    bg = n[-1] / area[-1]
    prof = n / area / bg
    res[k] = (n, prof)
    ax[0].errorbar(0.5*(edges[1:]+edges[:-1]), prof, np.sqrt(np.maximum(n,1))/area/bg, marker='o', label=f'{k} (bg {bg*3600:.0f} deg$^{{-2}}$)')
    if k in ('SDSS', 'DES DR2', 'HSC'):
        inn, out = (R < 2), (R > 8)
        gr, ri, rr = (g-r)[ok], (r-i)[ok], r[ok]
        if k == 'HSC':
            ax[1].scatter(gr[out], rr[out], s=1, c='0.7', label='HSC 8–20′ (all)')
        ax[1].scatter(gr[inn], rr[inn], s=8, label=f'{k} R<2′')
        if k in ('SDSS', 'DES DR2', 'HSC'):
            if k == 'HSC': ax[2].scatter(gr[out], ri[out], s=1, c='0.7', label='HSC 8–20′')
            ax[2].scatter(gr[inn], ri[inn], s=10, label=f'{k} R<2′')
ax[0].set(xscale='log', xlabel='R from Abell 370 [arcmin]', ylabel='point-source density / background', title='"stars" with 14<r<23'); ax[0].axhline(1, c='k', lw=.5); ax[0].legend(fontsize=8)
ax[1].set(xlim=(-0.5, 2.2), ylim=(23, 16), xlabel='g−r', ylabel='r', title='CMD'); ax[1].legend(fontsize=7, markerscale=2)
ax[2].set(xlim=(-0.5, 2.2), ylim=(-0.5, 1.8), xlabel='g−r', ylabel='r−i', title='colour–colour'); ax[2].legend(fontsize=7, markerscale=2)
plt.tight_layout(); plt.savefig('a370.png', dpi=110)
for k, (n, p) in res.items(): print(f"{k:8s} N/bin={n.tolist()}  rel.density={np.round(p,2).tolist()}")
