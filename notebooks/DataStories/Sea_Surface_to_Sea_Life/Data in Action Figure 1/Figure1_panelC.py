# %% [markdown]
# # Figure 1 panel (c): NISAR L2 GCOV VH gamma-naught backscatter
#
# The cross-pol VH band is warped to EPSG:4326, converted linear power -> dB,
# clipped to the 5-95 percentile (rounded to whole dB once, so the same clip drives
# both the image stretch and the colorbar axis), then gamma-stretched (gamma 0.5)
# to grayscale. GCOV stores gamma-naught, so the colorbar reads gamma^0. SWOT swath
# edges and the NISAR footprint are drawn on top. Pieces go to ./pieces/.
#
# Run top-to-bottom, or `python Figure1_panelC.py`.

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

KEY = "panelC"

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

nisar = c.load_nisar(c.NISAR_FILE, c.NISAR_POL)    # VHVH
box_extent = c.nisar_box_extent(nisar)
print(f"NISAR_CLIM = {c.set_nisar_clim(nisar)} dB ({c.NISAR_POL})")

swot = c.load_swot(c.SWOT_EXPERT_FILE,
                   (box_extent[2], box_extent[3]), (box_extent[0], box_extent[1]))

# %% [markdown]
# ## Draw

# %%
def draw_panel_c(ax, pc):
    """NISAR GCOV VH grayscale + SWOT swath edges + footprint."""
    c.draw_nisar(ax, nisar, pc)
    c.draw_swath_bars(ax, swot, pc, field="adt")
    c.draw_nisar_footprint(ax, nisar, pc, color="0.4", lw=1.0)
    c.coast(ax, "k")

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(
    KEY, box_extent, draw_panel_c,
    title=f"NISAR GCOV {c.NISAR_POL_SHORT}",
    subtitle=f"{nisar['time'].replace('T', ' ')} UTC",
    colorbars=[dict(cmap=c.NISAR_CMAP, clim=c.NISAR_CLIM,
                    label=rf"{c.NISAR_POL_SHORT} Backscatter ($\gamma^0$, dB)",
                    label_top=rf"{c.NISAR_POL_SHORT} backscatter (dB)")])
print("Done.")
