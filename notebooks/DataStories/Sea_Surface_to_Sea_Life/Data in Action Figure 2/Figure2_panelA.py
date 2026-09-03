# %% [markdown]
# # Figure 2 panel (a): SWOT L2 absolute dynamic topography
#
# Rendered in both variants: panelA_miost (MIOST v3 ADT in the background) and
# panelA_nomiost (SWOT swath only). ADT = (ssha_karin + height_cor_xover) +
# mean_dynamic_topography, keeping good-quality open-ocean pixels, with the 4 black
# swath-edge bars on top and color limits pinned to 1..85 cm. Exports both variants'
# pieces into ./pieces/, plus the globe context inset.
#
# Run top-to-bottom, or `python Figure2_panelA.py`.

# %%
import os
import sys

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
print(f"ADT_CLIM = {c.ADT_CLIM} cm")

# %% [markdown]
# ## Draw

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

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
for panel in (panelA_miost, panelA_nomiost):
    c.save_panel_pieces(panel)
c.save_globe()
print("Done.")
