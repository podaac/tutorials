# %% [markdown]
# # Figure 1 panel (b): SWOT ADT + geostrophic velocity over MIOST v3 ADT
#
# MIOST v3 ADT background, SWOT ADT swath, the 4 black swath-edge bars, the SWOT
# geostrophic-velocity quiver and the NISAR footprint outline, over the padded
# footprint box. Exports this panel's pieces into ./pieces/, plus the velocity key.
#
# Run top-to-bottom, or `python Figure1_panelB.py`.

# %%
import os
import sys

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                                  # notebook
    HERE = os.getcwd()
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import figure1_common as c

KEY = "panelB"

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

nisar = c.load_nisar(c.NISAR_FILE)                 # footprint outline + box (VH)
box_extent = c.nisar_box_extent(nisar)

swot = c.load_swot(c.SWOT_EXPERT_FILE,
                   (box_extent[2], box_extent[3]), (box_extent[0], box_extent[1]))
miost_adt = c.load_grid_field(c.MIOST_FILE, c.GRID_ADT_VAR,
                              (box_extent[2], box_extent[3]),
                              (box_extent[0], box_extent[1]))

print(f"ADT_CLIM = {c.set_adt_clim(swot, miost_adt)} cm")

# %% [markdown]
# ## Draw

# %%
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

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(
    KEY, box_extent, draw_panel_b,
    title="SWOT ADT + geostrophic velocity over MIOST v3 ADT",
    subtitle=f"MIOST {miost_adt['date']} / SWOT {swot['time'][11:19]} UTC",
    colorbars=[dict(cmap=c.ADT_CMAP, clim=c.ADT_CLIM,
                    label="Absolute Dynamic Topography (cm)",
                    label_top="ADT (cm)")])
c.save_velocity_key()
print("Done.")
