# %% [markdown]
# # Figure 1 panel (d): PACE MOANA picophytoplankton ternary composite
#
# The three MOANA abundance fields (Prochlorococcus, Synechococcus,
# picoeukaryotes) are normalized per channel and blended barycentrically into one
# RGB composite over the padded NISAR footprint box. Exports this panel's pieces
# into ./pieces/, plus the ternary triangle legend.
#
# Run top-to-bottom, or `python Figure1_panelD.py`.

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

KEY = "panelD"

# %% [markdown]
# ## Load

# %%
c.set_piece_dir(os.path.join(HERE, "pieces"))

nisar = c.load_nisar(c.NISAR_FILE)                 # footprint outline + box (VH)
box_extent = c.nisar_box_extent(nisar)

moana = c.load_moana(c.MOANA_FILE,
                     (box_extent[2], box_extent[3]), (box_extent[0], box_extent[1]))
print(f"MOANA valid pixels: {moana['n_valid']} / {moana['n_total']}")

# %% [markdown]
# ## Draw

# %%
def draw_panel_d(ax, pc):
    """PACE MOANA ternary composite + footprint."""
    ax.imshow(moana["rgba"], extent=moana["extent"], origin="lower",
              transform=pc, interpolation="nearest", zorder=1)
    c.draw_nisar_footprint(ax, nisar, pc, color="w", lw=1.0)
    c.coast(ax, "w")

# %% [markdown]
# ## Pieces

# %%
print("Pieces:")
c.save_panel_pieces(
    KEY, box_extent, draw_panel_d,
    title="PACE MOANA picophytoplankton community",
    subtitle=f"PACE {moana['date']}",
    facecolor=c.MOANA_BG, label_color="w")
c.save_moana_legend()
print("Done.")
