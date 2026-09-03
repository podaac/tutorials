# %% [markdown]
# # Data in Action Figure 1 -- SWOT x NISAR x MUR x PACE mosaic (2x2)
#
# * **(a)** MUR L4 SST + SWOT geostrophic speed swath + NISAR footprint box
# * **(b)** MIOST v3 ADT + SWOT ADT swath + swath-edge bars + geostrophic velocity
# * **(c)** NISAR L2 GCOV VH gamma-naught backscatter, grayscale
# * **(d)** PACE MOANA picophytoplankton ternary composite
#
# Writes the composite layout reference and exports every element separately into
# ./pieces/ for assembly in PowerPoint/Photoshop.
#
# Run top-to-bottom, or `python Figure1.py`.

# %%
import os
import sys

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

import figure1_common as c

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

etopo = c.load_etopo()                             # globe-inset bathymetry (or None)

nisar = c.load_nisar(c.NISAR_FILE, c.NISAR_POL)    # VHVH
box_extent = c.nisar_box_extent(nisar)
c.set_nisar_clim(nisar)                            # dB; clip already rounded

mur = c.load_mur(c.MUR_FILE, (-91.0, 91.0), (-181.0, 181.0))
wide_extent = (float(mur["lon"].min()), c.WIDE_EAST_CUTOFF, 28.0, 35.0)

swot = c.load_swot(c.SWOT_EXPERT_FILE,
                   (wide_extent[2], wide_extent[3]), (wide_extent[0], wide_extent[1]))
miost_adt = c.load_grid_field(c.MIOST_FILE, c.GRID_ADT_VAR,
                              (box_extent[2], box_extent[3]),
                              (box_extent[0], box_extent[1]))
moana = c.load_moana(c.MOANA_FILE,
                     (box_extent[2], box_extent[3]), (box_extent[0], box_extent[1]))
print(f"MOANA valid pixels: {moana['n_valid']} / {moana['n_total']}")

# Color limits. ADT shared by the SWOT swath + MIOST grid; SST over the wide window.
c.set_adt_clim(swot, miost_adt)
c.set_sst_clim(mur, wide_extent)
print(f"ADT_CLIM = {c.ADT_CLIM} cm   SST_CLIM = {c.SST_CLIM} degC   "
      f"NISAR_CLIM = {c.NISAR_CLIM} dB")

# %% [markdown]
# ## Per-panel draw functions (data + coast + overlays only; no ticks/title/bar)

# %%
def draw_panel_a(ax, pc):
    """MUR SST bg + SWOT geostrophic speed swath + NISAR footprint box."""
    pm = ax.pcolormesh(mur["lon"], mur["lat"], mur["sst"], cmap=c.SST_CMAP,
                       vmin=c.SST_CLIM[0], vmax=c.SST_CLIM[1], shading="auto",
                       transform=pc, zorder=1)
    c.draw_swot_speed(ax, swot, pc, zorder=3)
    c.draw_box_rect(ax, (box_extent[0], box_extent[1]),
                    (box_extent[2], box_extent[3]), pc)
    c.coast(ax, "k")
    return pm


def draw_panel_b(ax, pc):
    """MIOST v3 ADT bg + SWOT ADT swath + black swath bars + geostrophic quiver."""
    ax.pcolormesh(miost_adt["lon"], miost_adt["lat"], miost_adt["val"],
                  cmap=c.ADT_CMAP, vmin=c.ADT_CLIM[0], vmax=c.ADT_CLIM[1],
                  shading="auto", transform=pc, zorder=1)
    c.draw_swot_adt(ax, swot, pc, zorder=3)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    c.draw_geostrophic(ax, swot, pc)
    c.draw_nisar_footprint(ax, nisar, pc)
    c.coast(ax, "k")


def draw_panel_c(ax, pc):
    """NISAR GCOV VH grayscale + SWOT swath edges + footprint."""
    c.draw_nisar(ax, nisar, pc)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    c.draw_nisar_footprint(ax, nisar, pc, color="0.4", lw=1.0)
    c.coast(ax, "k")


def draw_panel_d(ax, pc):
    """PACE MOANA ternary composite + footprint."""
    ax.imshow(moana["rgba"], extent=moana["extent"], origin="lower",
              transform=pc, interpolation="nearest", zorder=1)
    c.draw_nisar_footprint(ax, nisar, pc, color="w", lw=1.0)
    c.coast(ax, "w")

# %% [markdown]
# ## Panel registry (drives both the composite and the modular pieces)

# %%
panels = [
    dict(key="panelA", letter="a", extent=wide_extent, draw=draw_panel_a,
         title="SWOT geostrophic speed over MUR SST",
         subtitle=f"SWOT {swot['time'].replace('T', ' ')} UTC",
         colorbars=[dict(cmap=c.SST_CMAP, clim=c.SST_CLIM,
                         label=r"Sea Surface Temperature ($^\circ$C)",
                         label_top=r"Sea surface temperature ($^\circ$C)"),
                    dict(cmap=c.SPEED_CMAP, clim=c.SPEED_CLIM,
                         label=r"Geostrophic Speed (m s$^{-1}$)",
                         label_top=r"Geostrophic speed (m s$^{-1}$)")]),
    dict(key="panelB", letter="b", extent=box_extent, draw=draw_panel_b,
         title="SWOT ADT + geostrophic velocity over MIOST v3 ADT",
         subtitle=f"MIOST {miost_adt['date']} / SWOT {swot['time'][11:19]} UTC",
         colorbars=[dict(cmap=c.ADT_CMAP, clim=c.ADT_CLIM,
                         label="Absolute Dynamic Topography (cm)",
                         label_top="ADT (cm)")]),
    dict(key="panelC", letter="c", extent=box_extent, draw=draw_panel_c,
         title=f"NISAR GCOV {c.NISAR_POL_SHORT}",
         subtitle=f"{nisar['time'].replace('T', ' ')} UTC",
         colorbars=[dict(cmap=c.NISAR_CMAP, clim=c.NISAR_CLIM,
                         label=rf"{c.NISAR_POL_SHORT} Backscatter ($\gamma^0$, dB)",
                         label_top=rf"{c.NISAR_POL_SHORT} backscatter (dB)")]),
    dict(key="panelD", letter="d", extent=box_extent, draw=draw_panel_d,
         title="PACE MOANA picophytoplankton community",
         subtitle=f"PACE {moana['date']}", coast_color="w", facecolor=c.MOANA_BG,
         colorbars=[]),
]

# %% [markdown]
# ## Composite (layout reference)

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


def make_composite(panels):
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(20, 16), facecolor="w")
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1.5, 1],
                  height_ratios=[1.2, 1], hspace=0.18, wspace=0.12)
    cells = {"panelA": gs[0, 0], "panelB": gs[0, 1],
             "panelC": gs[1, 0], "panelD": gs[1, 1]}
    for p in panels:
        ax = fig.add_subplot(cells[p["key"]], projection=pc)
        ax.set_extent(p["extent"], crs=pc)
        if p.get("facecolor", "none") != "none":
            ax.set_facecolor(p["facecolor"])
        p["draw"](ax, pc)
        style_axis(ax, p["letter"])
        ax.set_title(f"{p['title']}\n{p['subtitle']}", fontsize=11)
        for cb in p.get("colorbars", []):
            sm = plt.cm.ScalarMappable(norm=Normalize(cb["clim"][0], cb["clim"][1]),
                                       cmap=cb["cmap"])
            fig.colorbar(sm, ax=ax, orientation="horizontal", pad=0.06,
                         shrink=0.9, aspect=30).set_label(cb["label"])
    c.draw_globe_inset(fig, [0.005, 0.80, 0.14, 0.18], wide_extent, etopo=etopo)
    legax = fig.add_axes([0.78, 0.06, 0.12, 0.16])
    legax.set_facecolor("w"); legax.patch.set_alpha(1.0)
    c.draw_moana_legend(legax, text_color="k")
    fig.suptitle(
        f"SWOT L3 {swot['cycle_pass']} ({swot['date']}) x NISAR GCOV 008_170 "
        f"({nisar['date']})", fontsize=15)
    fig.savefig(c.COMPOSITE + ".png", dpi=c.DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {c.COMPOSITE}.png")


make_composite(panels)

# %% [markdown]
# ## Modular pieces

# %%
print("Pieces:")
for p in panels:
    c.save_panel_pieces(p["key"], p["extent"], p["draw"], p["title"], p["subtitle"],
                        colorbars=p["colorbars"],
                        facecolor=p.get("facecolor", "none"),
                        label_color=p.get("coast_color", "k"))

# Extras
c.save_globe(wide_extent, etopo)
c.save_velocity_key()
c.save_moana_legend()
print("Done.")
