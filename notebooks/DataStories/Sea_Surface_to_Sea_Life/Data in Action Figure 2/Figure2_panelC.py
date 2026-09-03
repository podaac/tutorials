# %% [markdown]
# # Figure 2 panel (c): VIIRS chlorophyll a
#
# VIIRS L2 chlor_a on a log10 color scale with the custom white->green->blue map,
# clouds/masked pixels white, with the SWOT swath-edge bars on top. The colorbar is
# labeled and ticked in real mg m^-3. Pieces go to ./pieces/.
#
# Run top-to-bottom, or `python Figure2_panelC.py`.

# %%
import os
import sys

import numpy as np

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
chlor = c.load_viirs_chlor()

# %% [markdown]
# ## Draw

# %%
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


panelC = dict(key="panelC_chl", letter="c", extent=c.ZOOM_EXTENT, draw=draw_panel_c,
              facecolor="white",
              title="VIIRS chlorophyll-a",
              subtitle=f"VIIRS {chlor['time'][:16].replace('T', ' ')} UTC",
              colorbars=[c.chl_cbar()])

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(panelC)
print("Done.")
