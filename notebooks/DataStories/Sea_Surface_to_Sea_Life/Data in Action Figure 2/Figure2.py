# %% [markdown]
# # Data in Action Figure 2 -- SWOT L2 ADT x VIIRS SST & chlorophyll triptych (1x3)
#
# All three panels share the inner-shelf zoom 80.25 W .. 79 W, 30.25 N .. 32 N.
#
# * **(a)** SWOT L2 ADT swath over MIOST v3 ADT + swath-edge bars. Two versions:
#           panelA_miost (MIOST background) and panelA_nomiost (swath only).
# * **(b)** VIIRS L2 SST, masked to the chlorophyll panel's valid pixels
# * **(c)** VIIRS L2 log10(chlor_a), colorbar ticked in mg m^-3
#
# SWOT ADT = (ssha_karin + height_cor_xover) + mean_dynamic_topography, keeping
# good-quality open-ocean pixels.
#
# Writes both composite layout references and exports every element separately
# into ./pieces/ for assembly in PowerPoint/Photoshop.
#
# Run top-to-bottom, or `python Figure2.py`.

# %%
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                                  # notebook
    HERE = os.getcwd()
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import figure2_common as c

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

nisar = c.load_nisar_footprint()
swot = c.load_swot()
miost_adt = c.load_grid_field()
viirs = c.load_viirs_swath()
chlor = c.load_viirs_chlor()

c.set_sst_clim(viirs)
print(f"ADT_CLIM = {c.ADT_CLIM} cm   SST_CLIM = {c.SST_CLIM} degC")

# %% [markdown]
# ## Per-panel draw functions (data + coast + overlays only; no ticks/title/bar)

# %%
def draw_panel_a(ax, pc, with_miost=True):
    """SWOT ADT swath over optional MIOST ADT bg + swath bars + NISAR footprint."""
    if with_miost:
        ax.pcolormesh(miost_adt["lon"], miost_adt["lat"], miost_adt["val"],
                      cmap=c.ADT_CMAP, vmin=c.ADT_CLIM[0], vmax=c.ADT_CLIM[1],
                      shading="auto", transform=pc, zorder=1)
    pm = c.draw_swot_adt(ax, swot, pc, zorder=3)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    if "a" in c.NISAR_BOX_PANELS:
        c.draw_nisar_footprint(ax, nisar, pc)
    c.coast(ax, "k")
    return pm


def draw_panel_a_miost(ax, pc):
    return draw_panel_a(ax, pc, with_miost=True)


def draw_panel_a_nomiost(ax, pc):
    return draw_panel_a(ax, pc, with_miost=False)


def draw_panel_b(ax, pc):
    """VIIRS SST (clouds/masked -> white) + SWOT swath bars."""
    sst_cmap = plt.get_cmap(c.SST_CMAP).copy()
    sst_cmap.set_bad("white")
    ax.set_facecolor("white")
    pm = ax.pcolormesh(viirs["lon"], viirs["lat"], np.ma.masked_invalid(viirs["sst"]),
                       cmap=sst_cmap, vmin=c.SST_CLIM[0], vmax=c.SST_CLIM[1],
                       shading="auto", transform=pc, zorder=1)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    if "b" in c.NISAR_BOX_PANELS:
        c.draw_nisar_footprint(ax, nisar, pc)
    c.coast(ax, "k")
    return pm


def draw_panel_c(ax, pc):
    """VIIRS log10(chlor_a) (clouds/masked -> white) + SWOT swath bars."""
    chl_cmap = c.CHLOR_CMAP.copy()
    chl_cmap.set_bad("white")
    ax.set_facecolor("white")
    log_chl = np.log10(chlor["chl"])
    pm = ax.pcolormesh(chlor["lon"], chlor["lat"], np.ma.masked_invalid(log_chl),
                       cmap=chl_cmap, vmin=c.CHLOR_LOG_CLIM[0],
                       vmax=c.CHLOR_LOG_CLIM[1], shading="auto", transform=pc,
                       zorder=1)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    if "c" in c.NISAR_BOX_PANELS:
        c.draw_nisar_footprint(ax, nisar, pc)
    c.coast(ax, "k")
    return pm

# %% [markdown]
# ## Panel registry
#
# Panel (a) has two variants (MIOST background / none); both share the (a) letter
# and colorbar but render into distinct piece keys + composites.

# %%
panelA_miost = dict(key="panelA_miost", letter="a", extent=c.ZOOM_EXTENT,
                    draw=draw_panel_a_miost,
                    title="SWOT L2 absolute dynamic topography over MIOST",
                    subtitle=f"MIOST {miost_adt['date']} / SWOT {swot['time'][11:19]} UTC",
                    colorbars=[c.adt_cbar()])
panelA_nomiost = dict(key="panelA_nomiost", letter="a", extent=c.ZOOM_EXTENT,
                      draw=draw_panel_a_nomiost,
                      title="SWOT L2 absolute dynamic topography",
                      subtitle=f"SWOT {swot['time'].replace('T', ' ')} UTC",
                      colorbars=[c.adt_cbar()])
panelB = dict(key="panelB_sst", letter="b", extent=c.ZOOM_EXTENT, draw=draw_panel_b,
              facecolor="white",
              title="VIIRS sea surface temperature",
              subtitle=f"VIIRS {viirs['time'][:16].replace('T', ' ')} UTC",
              colorbars=[c.sst_cbar()])
panelC = dict(key="panelC_chl", letter="c", extent=c.ZOOM_EXTENT, draw=draw_panel_c,
              facecolor="white",
              title="VIIRS chlorophyll-a",
              subtitle=f"VIIRS {chlor['time'][:16].replace('T', ' ')} UTC",
              colorbars=[c.chl_cbar()])

all_panels = [panelA_miost, panelA_nomiost, panelB, panelC]

# %% [markdown]
# ## Composites (layout references, one per version of panel a)

# %%
def style_axis(ax, label):
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray",
                      alpha=0.5, linestyle=":")
    gl.top_labels = gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    ax.text(0.02, 0.98, f"({label})", transform=ax.transAxes, fontsize=16,
            va="top", ha="left",
            bbox=dict(facecolor="w", edgecolor="none", alpha=0.7, pad=1.5))


def make_composite(panels, out_path, suptitle):
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(18, 9), facecolor="w")
    gs = GridSpec(1, 3, figure=fig, wspace=0.12)
    for i, p in enumerate(panels):
        ax = fig.add_subplot(gs[0, i], projection=pc)
        ax.set_extent(p["extent"], crs=pc)
        if p.get("facecolor", "none") != "none":
            ax.set_facecolor(p["facecolor"])
        p["draw"](ax, pc)
        style_axis(ax, p["letter"])
        ax.set_title(f"{p['title']}\n{p['subtitle']}", fontsize=11)
        for cb in p.get("colorbars", []):
            sm = plt.cm.ScalarMappable(norm=Normalize(cb["clim"][0], cb["clim"][1]),
                                       cmap=cb["cmap"])
            cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", pad=0.06,
                                shrink=0.9, aspect=30)
            cbar.set_label(cb["label"])
            if cb.get("ticks") is not None:
                cbar.set_ticks(cb["ticks"])
                if cb.get("ticklabels") is not None:
                    cbar.set_ticklabels(cb["ticklabels"])
    fig.suptitle(suptitle, fontsize=14)
    fig.savefig(out_path, dpi=c.DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


suptitle = (f"SWOT L2 {swot['cycle_pass']} ADT  +  VIIRS SST & chlorophyll-a"
            f"   ({swot['date']})")
make_composite([panelA_miost, panelB, panelC],
               os.path.join(HERE, "Figure2_composite_miost.png"), suptitle)
make_composite([panelA_nomiost, panelB, panelC],
               os.path.join(HERE, "Figure2_composite_nomiost.png"), suptitle)

# %% [markdown]
# ## Modular pieces

# %%
print("Pieces:")
for p in all_panels:
    c.save_panel_pieces(p)
c.save_globe()
print("Done.")
