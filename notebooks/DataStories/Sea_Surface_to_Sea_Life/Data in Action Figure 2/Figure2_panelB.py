# %% [markdown]
# # Figure 2 panel (b): VIIRS sea surface temperature
#
# VIIRS L2 SST masked to the chlorophyll panel's valid pixels (keep SST where
# chlor_a from the same OC granule is finite and > 0), clouds/masked pixels white,
# with the SWOT swath-edge bars on top. Color limits are the robust 2-98
# percentiles of the in-box field. Pieces go to ./pieces/.
#
# Run top-to-bottom, or `python Figure2_panelB.py`.

# %%
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

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
swot = c.load_swot()                               # swath-edge bars only
viirs = c.load_viirs_swath()
print(f"SST_CLIM = {c.set_sst_clim(viirs)} degC")

# %% [markdown]
# ## Draw

# %%
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


panelB = dict(key="panelB_sst", letter="b", extent=c.ZOOM_EXTENT, draw=draw_panel_b,
              facecolor="white",
              title="VIIRS sea surface temperature",
              subtitle=f"VIIRS {viirs['time'][:16].replace('T', ' ')} UTC",
              colorbars=[c.sst_cbar()])

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(panelB)
print("Done.")
