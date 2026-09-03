# %% [markdown]
# # Figure 1 panel (a): SWOT geostrophic speed over MUR L4 SST
#
# MUR L4 SST background, SWOT geostrophic speed swath on top, box marking the
# NISAR footprint; east edge cut at 75 W. Exports this panel's pieces into
# ./pieces/, plus the globe inset (ETOPO 2022 bathymetry).
#
# Run top-to-bottom, or `python Figure1_panelA.py`.

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

KEY = "panelA"

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

nisar = c.load_nisar(c.NISAR_FILE)                 # footprint box only (VH)
box_extent = c.nisar_box_extent(nisar)

mur = c.load_mur(c.MUR_FILE, (-91.0, 91.0), (-181.0, 181.0))
wide_extent = (float(mur["lon"].min()), c.WIDE_EAST_CUTOFF, 28.0, 35.0)

swot = c.load_swot(c.SWOT_EXPERT_FILE,
                   (wide_extent[2], wide_extent[3]), (wide_extent[0], wide_extent[1]))
etopo = c.load_etopo()                             # globe-inset bathymetry (or None)

print(f"SST_CLIM = {c.set_sst_clim(mur, wide_extent)} degC")

# %% [markdown]
# ## Draw

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

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(
    KEY, wide_extent, draw_panel_a,
    title="SWOT geostrophic speed over MUR SST",
    subtitle=f"SWOT {swot['time'].replace('T', ' ')} UTC",
    colorbars=[
        dict(cmap=c.SST_CMAP, clim=c.SST_CLIM,
             label=r"Sea Surface Temperature ($^\circ$C)",
             label_top=r"Sea surface temperature ($^\circ$C)"),
        dict(cmap=c.SPEED_CMAP, clim=c.SPEED_CLIM,
             label=r"Geostrophic Speed (m s$^{-1}$)",
             label_top=r"Geostrophic speed (m s$^{-1}$)"),
    ])
c.save_globe(wide_extent, etopo)
print("Done.")
