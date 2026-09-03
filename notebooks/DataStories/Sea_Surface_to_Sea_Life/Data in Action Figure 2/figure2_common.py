# %% [markdown]
# # Figure 2 common: shared config, loaders, draw primitives, modular piece renderer
#
# Shared by the composite script and the panel scripts, so each can be run on its
# own:
#
#   * Figure2.py / .ipynb          -- both composites + every piece (all panels)
#   * Figure2_panelA.py / .ipynb   -- SWOT L2 ADT, MIOST-background and no-background
#                                     variants (+ the globe inset)
#   * Figure2_panelB.py / .ipynb   -- VIIRS SST
#   * Figure2_panelC.py / .ipynb   -- VIIRS chlorophyll a
#
# Nothing here draws on import; the panel scripts load only the data they need.

# %%
import os
import re
import glob
import warnings

import numpy as np
import xarray as xr
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# %% [markdown]
# ## Config

# %%
# Input data is resolved by glob pattern at load time (see data_path below).
# Raw inputs live under the shared data root, organised as
# DATA_ROOT/<SOURCE>/<LEVEL>/... so each product is downloaded only once and
# reused across projects. Defaults to ~/Data. Override with the DATA_ROOT env
# var (or the legacy SWOT_DIA_DATA_DIR, which wins if set).
# See DATA.md for what to download and where to put it.
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("DATA_ROOT", os.path.join(os.path.expanduser("~"), "Data"))
DATA_ROOT = os.environ.get("SWOT_DIA_DATA_DIR", DATA_ROOT)

# Each constant is a filename glob (not a full path); data_path() resolves it to
# the actual downloaded file under its shared-root subdirectory (see SUBDIR_FOR).
# NOTE: Figure 2 uses the SWOT L2 product (Figure 1 uses L3), hence the distinct
# L2 pattern below; both live under SWOT/LR_SSH_Expert.
SWOT_EXPERT_FILE = "SWOT_L2_LR_SSH_Expert_043_410_*.nc"
NISAR_FILE       = "NISAR_L2_PR_GCOV_008_170_*.h5"
MIOST_FILE       = "dt_global_allsat_phy_l4_*.nc"
VIIRS_FILE       = "*VIIRS*.L2.SST*.nc"
VIIRS_OC_FILE    = "*VIIRS*.L2.OC*.nc"

# Map each input glob to its shared-root subdirectory under DATA_ROOT.
SUBDIR_FOR = {
    SWOT_EXPERT_FILE: os.path.join("SWOT", "LR_SSH_Expert"),
    NISAR_FILE:       os.path.join("NISAR", "L2_GCOV"),
    MIOST_FILE:       os.path.join("DUACS", "MIOST_L4"),
    VIIRS_FILE:       os.path.join("VIIRS_SNPP", "L2"),
    VIIRS_OC_FILE:    os.path.join("VIIRS_SNPP", "L2"),
}


def data_path(pattern):
    """Resolve one input file under DATA_ROOT by glob pattern (searched
    recursively within the dataset's shared-root subdirectory). An already-
    existing explicit path is returned as-is, so a user can still pass a full
    path. Raises a clear error pointing at DATA.md when the file is missing or
    ambiguous -- a fresh clone fails with instructions instead of a cryptic
    error deep in a loader."""
    if os.path.isfile(pattern):
        return pattern
    base = os.path.join(DATA_ROOT, SUBDIR_FOR.get(pattern, ""))
    matches = sorted(glob.glob(os.path.join(base, "**", pattern), recursive=True))
    hint = (f"See DATA.md for what to download and where to put it. "
            f"Looked under: {base}")
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"No data file matching '{pattern}'. {hint}")
    raise RuntimeError(
        f"Multiple files match '{pattern}': {matches}. Keep only one. {hint}")

# Tight zoom shared by all three panels:  80.25 W .. 79 W,  30.25 N .. 32 N
ZOOM_EXTENT = (-80.25, -79.0, 30.25, 32.0)           # (west, east, south, north)
LON_RANGE   = (ZOOM_EXTENT[0], ZOOM_EXTENT[1])
LAT_RANGE   = (ZOOM_EXTENT[2], ZOOM_EXTENT[3])
WIDE_EXTENT = (-84.0, -76.0, 28.0, 35.0)             # globe-inset context box

# Which panels draw the NISAR footprint box. Subset of {"a","b","c"}.
NISAR_BOX_PANELS = set()

# SWOT JPL L2 LR SSH Expert (flat). Crossover correction:
#   corrected SSHA = ssha_karin + height_cor_xover   (m)
#   ADT            = corrected SSHA + mean_dynamic_topography   (m)
# Keep open-ocean (surface flag == 0), good-quality (ssha_karin_qual == 0) pixels.
L2_SSHA_VAR  = "ssha_karin"
L2_XOVER_VAR = "height_cor_xover"
L2_SSHA_QUAL = "ssha_karin_qual"
L2_SFC_FLAG  = "ancillary_surface_classification_flag"   # 0 = open ocean
MDT_VAR      = "mean_dynamic_topography"

# MIOST v3 grid (panel a background)
GRID_ADT_VAR = "adt"
GRID_LAT = "latitude"
GRID_LON = "longitude"

# ADT color limits pinned to 1..85 cm so panel-a colors match across figures,
# rather than auto-deriving from this tight zoom's in-box percentiles.
ADT_CMAP = "Spectral_r"      # ADT (cm)
ADT_CLIM = (1.0, 85.0)

# VIIRS SST (panel b)
SST_CMAP = "turbo"
SST_CLIM = None              # set from robust 2-98 pct of VIIRS SST in-box

# VIIRS chlor_a (panel c): log10(Chl a), linear color scale on log values
CHLOR_LOG_CLIM = (np.log10(0.05), 0.3)
_XML_POINTS = [  # control points from 8-31b2.xml (x=0 near-white .. x=1 dark blue)
    (0.000, 0.894118, 1.000000, 0.878431),
    (0.020, 0.784314, 0.968627, 0.792157),
    (0.050, 0.713725, 0.949020, 0.772549),
    (0.100, 0.556863, 0.901961, 0.705882),
    (0.150, 0.494118, 0.839216, 0.690196),
    (0.200, 0.454902, 0.800000, 0.686275),
    (0.250, 0.423529, 0.768627, 0.682353),
    (0.300, 0.376471, 0.741176, 0.674510),
    (0.350, 0.349020, 0.709804, 0.666667),
    (0.400, 0.317647, 0.678431, 0.666667),
    (0.450, 0.298039, 0.639216, 0.650980),
    (0.500, 0.274510, 0.576471, 0.611765),
    (0.550, 0.250980, 0.509804, 0.568627),
    (0.600, 0.223529, 0.454902, 0.529412),
    (0.650, 0.200000, 0.403922, 0.490196),
    (0.700, 0.180392, 0.356863, 0.450980),
    (0.750, 0.164706, 0.305882, 0.419608),
    (0.800, 0.149020, 0.262745, 0.388235),
    (0.850, 0.141176, 0.219608, 0.380392),
    (0.900, 0.129412, 0.184314, 0.360784),
    (0.950, 0.113725, 0.137255, 0.329412),
    (1.000, 0.101961, 0.133333, 0.301961),
]
CHLOR_CMAP = LinearSegmentedColormap.from_list(
    "chl_blue_green_white",
    [(1.0 - x, (r, g, b)) for x, r, g, b in reversed(_XML_POINTS)])

# VIIRS SST is masked to the chlorophyll panel's valid pixels (see load_viirs_swath).

# Output
OUT_DIR   = os.path.dirname(os.path.abspath(__file__))
PIECE_DIR = os.path.join(OUT_DIR, "pieces")

# Piece rendering quality. SCALE inches/deg * DPI = pixels/deg.
DPI      = 600
SCALE    = 2.0               # inches per degree (1200 px/deg at 600 dpi)
RULER_IN = 0.6               # ruler strip thickness (inches)


def set_piece_dir(path):
    """Point every save_* helper at `path` (created if needed)."""
    global PIECE_DIR
    PIECE_DIR = path
    os.makedirs(PIECE_DIR, exist_ok=True)
    return PIECE_DIR

# %% [markdown]
# ## Loaders

# %%
def parse_swot_id(path):
    m = re.search(r"_(\d{3}_\d{3})_\d{8}T", path)
    return m.group(1) if m else "pass"


def parse_bounding_polygon(wkt):
    nums = re.findall(r"-?\d+\.\d+", wkt)
    vals = np.array(nums, dtype=float).reshape(-1, 3)
    return vals[:, 0], vals[:, 1]


def _crop_rows(ds, lat_range, lon_range):
    lat = ds["latitude"].values
    lon = ((ds["longitude"].values + 180.0) % 360.0) - 180.0
    in_box = ((lat > lat_range[0]) & (lat < lat_range[1])
              & (lon > lon_range[0]) & (lon < lon_range[1]))
    rows = np.where(in_box.any(axis=1))[0]
    if rows.size == 0:
        raise RuntimeError("SWOT pass does not cross the box.")
    sub = ds.isel(num_lines=slice(int(rows.min()), int(rows.max()) + 1))
    lat = sub["latitude"].values
    lon = ((sub["longitude"].values + 180.0) % 360.0) - 180.0
    return sub, lat, lon


def load_swot(swot_file=SWOT_EXPERT_FILE, lat_range=LAT_RANGE, lon_range=LON_RANGE):
    """JPL L2 LR SSH Expert (flat). Crossover-correct ssha_karin, mask to good
    open-ocean pixels, form ADT = corrected SSHA + MDT."""
    swot_file = data_path(swot_file)
    ds = xr.open_dataset(swot_file)
    sub, lat, lon = _crop_rows(ds, lat_range, lon_range)
    good = (sub[L2_SSHA_QUAL].values == 0) & (sub[L2_SFC_FLAG].values == 0)
    ssha_corr = sub[L2_SSHA_VAR].values + sub[L2_XOVER_VAR].values   # crossover-corrected (m)
    ssha_cm = np.where(good, ssha_corr, np.nan) * 100.0
    adt_cm = ssha_cm + sub[MDT_VAR].values * 100.0
    t = str(sub["time"].values[len(sub["time"]) // 2])
    if not t[:4].isdigit():                            # L2 time can be NaT -> fall back
        t = str(ds.attrs.get("time_coverage_start", ""))[:19]
    return dict(lat=lat, lon=lon, ssha=ssha_cm, adt=adt_cm,
                time=t[:19], date=t[:10], cycle_pass=parse_swot_id(swot_file))


def swath_boundary_cols(field2d):
    """4 across-track columns marking the swath edges: outer-left, outer-right,
    and the two nadir-gap edges."""
    colnan = np.isnan(field2d).all(axis=0)
    valid = np.where(~colnan)[0]
    if valid.size == 0:
        return []
    left, right = int(valid.min()), int(valid.max())
    gap = [c for c in range(left, right + 1) if colnan[c]]
    cols = [left, right]
    if gap:
        cols += [int(min(gap)) - 1, int(max(gap)) + 1]
    return sorted(set(c for c in cols if 0 <= c < field2d.shape[1]))


def load_grid_field(path=MIOST_FILE, var=GRID_ADT_VAR, lat_range=LAT_RANGE,
                    lon_range=LON_RANGE):
    path = data_path(path)
    ds = xr.open_dataset(path)
    da = ds[var]
    if "time" in da.dims:
        da = da.isel(time=0)
    if float(da[GRID_LON].max()) > 180.0:
        da = da.assign_coords({GRID_LON: (((da[GRID_LON] + 180) % 360) - 180)})
    if not np.all(np.diff(da[GRID_LON].values) > 0):
        da = da.sortby(GRID_LON)
    if not np.all(np.diff(da[GRID_LAT].values) > 0):
        da = da.sortby(GRID_LAT)
    sub = da.sel({GRID_LAT: slice(lat_range[0], lat_range[1]),
                  GRID_LON: slice(lon_range[0], lon_range[1])})
    val_cm = sub.values.astype(float) * 100.0
    lon = sub[GRID_LON].values; lat = sub[GRID_LAT].values
    LON2, LAT2 = np.meshgrid(lon, lat)
    t = str(ds["time"].values[0])[:19] if "time" in ds.coords else ""
    return dict(lat=LAT2, lon=LON2, val=val_cm, date=t[:10])


def load_nisar_footprint(path=NISAR_FILE):
    """Footprint polygon + acquisition time only (no GCOV warp needed here)."""
    path = data_path(path)
    with h5py.File(path, "r") as f:
        wkt = f["science/LSAR/identification/boundingPolygon"][()].decode()
        t0 = f["science/LSAR/identification/zeroDopplerStartTime"][()].decode()
    flon, flat = parse_bounding_polygon(wkt)
    return dict(flon=flon, flat=flat, date=t0[:10], time=t0[:19])


def _viirs_crop(lon, lat, field, lat_range, lon_range):
    in_box = ((lat > lat_range[0]) & (lat < lat_range[1])
              & (lon > lon_range[0]) & (lon < lon_range[1]))
    rows = np.where(in_box.any(axis=1))[0]
    cols = np.where(in_box.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        raise RuntimeError("swath does not cross the box.")
    rs = slice(int(rows.min()), int(rows.max()) + 1)
    cs = slice(int(cols.min()), int(cols.max()) + 1)
    lon, lat, field = lon[rs, cs], lat[rs, cs], field[rs, cs]
    out = ((lat < lat_range[0]) | (lat > lat_range[1])
           | (lon < lon_range[0]) | (lon > lon_range[1]))
    field[out] = np.nan
    return lon, lat, field


def load_viirs_swath(path=VIIRS_FILE, oc_path=VIIRS_OC_FILE, lat_range=LAT_RANGE,
                     lon_range=LON_RANGE):
    """SST masked to EXACTLY the pixels shown in the chlorophyll panel:
    keep SST iff chlor_a (same OC granule/grid) is valid (finite, > 0)."""
    path = data_path(path)
    oc_path = data_path(oc_path)
    nav = xr.open_dataset(path, group="navigation_data")
    geo = xr.open_dataset(path, group="geophysical_data")
    root = xr.open_dataset(path)
    oc_geo = xr.open_dataset(oc_path, group="geophysical_data")   # same granule/grid
    lon = nav["longitude"].values.astype(float)
    lat = nav["latitude"].values.astype(float)
    sst = geo["sst"].values.astype(float)
    chl = oc_geo["chlor_a"].values.astype(float)
    chl_valid = np.isfinite(chl) & (chl > 0)
    sst = np.where(chl_valid & np.isfinite(sst), sst, np.nan)
    lon, lat, sst = _viirs_crop(lon, lat, sst, lat_range, lon_range)
    t = str(root.attrs.get("time_coverage_start", ""))[:19]
    return dict(lat=lat, lon=lon, sst=sst, date=t[:10], time=t)


def load_viirs_chlor(path=VIIRS_OC_FILE, lat_range=LAT_RANGE, lon_range=LON_RANGE):
    path = data_path(path)
    nav = xr.open_dataset(path, group="navigation_data")
    geo = xr.open_dataset(path, group="geophysical_data")
    root = xr.open_dataset(path)
    lon = nav["longitude"].values.astype(float)
    lat = nav["latitude"].values.astype(float)
    chl = geo["chlor_a"].values.astype(float)      # mg m^-3
    chl = np.where(np.isfinite(chl) & (chl > 0), chl, np.nan)
    lon, lat, chl = _viirs_crop(lon, lat, chl, lat_range, lon_range)
    t = str(root.attrs.get("time_coverage_start", ""))[:19]
    return dict(lat=lat, lon=lon, chl=chl, date=t[:10], time=t)


def set_sst_clim(viirs, pct=(2, 98)):
    """SST color limits from the VIIRS field in-box (robust percentiles, degC)."""
    global SST_CLIM
    s = np.nanpercentile(viirs["sst"], list(pct))
    SST_CLIM = (float(np.floor(s[0])), float(np.ceil(s[1])))
    return SST_CLIM

# %% [markdown]
# ## Draw primitives

# %%
def draw_swot_adt(ax, swot, pc, **kw):
    return ax.pcolormesh(swot["lon"], swot["lat"], np.ma.masked_invalid(swot["adt"]),
                         cmap=ADT_CMAP, vmin=ADT_CLIM[0], vmax=ADT_CLIM[1],
                         shading="auto", transform=pc, **kw)


def draw_swath_bars(ax, swot, pc, field="adt", lw=1.4):
    for col in swath_boundary_cols(swot[field]):
        ax.plot(swot["lon"][:, col], swot["lat"][:, col], "k",
                linewidth=lw, transform=pc, zorder=7)


def draw_nisar_footprint(ax, nisar, pc, color="k", lw=1.6, ls="--"):
    ax.plot(nisar["flon"], nisar["flat"], color=color, linewidth=lw, linestyle=ls,
            transform=pc, zorder=7)


def draw_box_rect(ax, lon_range, lat_range, pc, color="k", lw=1.8):
    lo0, lo1 = lon_range; la0, la1 = lat_range
    ax.plot([lo0, lo1, lo1, lo0, lo0], [la0, la0, la1, la1, la0],
            color=color, linewidth=lw, transform=pc, zorder=7)


def draw_globe_inset(fig, rect, wide_extent=WIDE_EXTENT):
    lon0 = 0.5 * (wide_extent[0] + wide_extent[1])
    lat0 = 0.5 * (wide_extent[2] + wide_extent[3])
    axg = fig.add_axes(rect, projection=ccrs.Orthographic(
        central_longitude=lon0, central_latitude=lat0))
    axg.set_global()
    axg.add_feature(cfeature.OCEAN, facecolor="#9ecbe8", zorder=0)
    axg.add_feature(cfeature.LAND, facecolor="0.7", edgecolor="k",
                    linewidth=0.3, zorder=1)
    draw_box_rect(axg, (wide_extent[0], wide_extent[1]),
                  (wide_extent[2], wide_extent[3]), ccrs.PlateCarree(), lw=1.5)
    return axg


def coast(ax, color="k"):
    try:
        ax.coastlines("10m", linewidth=0.6, color=color)
    except Exception as exc:
        warnings.warn(f"coastlines unavailable: {exc}")

# %% [markdown]
# ## Colorbar specs (shared by the composites and the piece exports)

# %%
def adt_cbar():
    return dict(cmap=ADT_CMAP, clim=ADT_CLIM,
                label="Absolute dynamic topography (cm)",
                label_top="Absolute dynamic topography (cm)")


def sst_cbar():
    return dict(cmap=SST_CMAP, clim=SST_CLIM,
                label=r"Sea surface temperature ($^\circ$C)",
                label_top=r"Sea surface temperature ($^\circ$C)")


# Chl color scale is log10, but the bar is labeled + ticked in real mg m^-3.
_CHL_CONC = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]


def chl_cbar():
    return dict(cmap=CHLOR_CMAP, clim=CHLOR_LOG_CLIM,
                label=r"Chlorophyll $a$ concentration (mg m$^{-3}$)",
                label_top=r"Chlorophyll $a$ concentration (mg m$^{-3}$)",
                ticks=[float(np.log10(c)) for c in _CHL_CONC],
                ticklabels=[f"{c:g}" for c in _CHL_CONC])

# %% [markdown]
# ## Modular piece renderer
#
# Each panel -> a bare map (data fills the canvas edge-to-edge), a lat ruler, a
# lon ruler, a title card, and any colorbars. The map figsize is proportional to
# the lon/lat spans, so in PlateCarree pixel<->degree is linear across the whole
# canvas; the rulers share that width/height and therefore pixel-align to the map.

# %%
def fmt_lon(x):
    x = ((x + 180) % 360) - 180
    h = "W" if x < 0 else ("E" if x > 0 else "")
    return f"{abs(x):.2f}°{h}"


def fmt_lat(y):
    h = "N" if y > 0 else ("S" if y < 0 else "")
    return f"{abs(y):.2f}°{h}"


def _ticks(lo, hi, n=5):
    t = MaxNLocator(nbins=n, steps=[1, 2, 2.5, 5, 10]).tick_values(lo, hi)
    return [v for v in t if lo <= v <= hi]


def _ruler_ticks(lo, hi, width_in, label_in=0.85):
    """Tick count that fits `width_in` inches of strip without crowding labels
    (each '80.25 deg W'-style label needs ~label_in inches incl. spacing)."""
    n = max(2, int(width_in / label_in))
    return _ticks(lo, hi, n)


def save_map_piece(key, extent, draw_fn, facecolor="none"):
    w, e, s, n = extent
    lon_span, lat_span = (e - w), (n - s)
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(lon_span * SCALE, lat_span * SCALE), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1], projection=pc)
    if facecolor != "none":
        ax.set_facecolor(facecolor)
    ax.set_extent(extent, crs=pc)
    draw_fn(ax, pc)
    ax.set_aspect("auto")          # fill the canvas exactly (no cartopy margin)
    ax.axis("off")
    out = os.path.join(PIECE_DIR, f"{key}_map.png")
    transparent = facecolor == "none"
    fig.savefig(out, dpi=DPI, transparent=transparent,
                facecolor=(facecolor if not transparent else "none"))
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_map_piece_ticked(key, extent, draw_fn, sides="latlon", facecolor="none"):
    """Self-contained map with the axis labels TIED to the panel (cartopy gridline
    labels). `sides` selects which labels: 'latlon', 'lat', or 'lon'. Saved with a
    tight bbox so the labels are included (these are not meant to align with the
    separate ruler strips -- the bare map + standalone rulers are still written)."""
    w, e, s, n = extent
    lon_span, lat_span = (e - w), (n - s)
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(lon_span * SCALE, lat_span * SCALE), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1], projection=pc)
    if facecolor != "none":
        ax.set_facecolor(facecolor)
    ax.set_extent(extent, crs=pc)
    draw_fn(ax, pc)
    ax.set_aspect("auto")          # map fills the [0,0,1,1] box; labels go in margins
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray",
                      alpha=0.5, linestyle=":")
    gl.top_labels = gl.right_labels = False
    gl.bottom_labels = sides in ("latlon", "lon")
    gl.left_labels = sides in ("latlon", "lat")
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 10}
    gl.ylabel_style = {"size": 10}
    out = os.path.join(PIECE_DIR, f"{key}_map_{sides}.png")
    transparent = facecolor == "none"
    fig.savefig(out, dpi=DPI, transparent=transparent, bbox_inches="tight",
                facecolor=(facecolor if not transparent else "none"))
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_lon_ruler(key, extent):
    w, e, s, n = extent
    lon_span = e - w
    width_in = lon_span * SCALE
    fig = plt.figure(figsize=(width_in, RULER_IN), dpi=DPI)
    # Drop the tick line a bit so the label row has vertical room in the strip.
    ax = fig.add_axes([0, 0.55, 1, 1e-4])
    ax.set_xlim(w, e); ax.set_ylim(0, 1)
    ticks = _ruler_ticks(w, e, width_in, label_in=0.55)   # tick count scaled to width
    # Drop edge-hugging ticks whose labels would overflow the (un-cropped) strip.
    half_deg = 0.5 * 0.55 / SCALE
    interior = [t for t in ticks if (t - w) > half_deg and (e - t) > half_deg]
    ticks = interior or ticks
    ax.set_xticks(ticks)
    ax.set_xticklabels([fmt_lon(t) for t in ticks], fontsize=9)
    ax.xaxis.set_ticks_position("bottom")
    ax.tick_params(axis="x", top=False, length=5)
    ax.set_yticks([])
    for sp in ("top", "left", "right"):
        ax.spines[sp].set_visible(False)
    out = os.path.join(PIECE_DIR, f"{key}_lon.png")
    # No bbox_inches="tight": keep the figure width == map width so it still aligns.
    fig.savefig(out, dpi=DPI, transparent=True)
    plt.close(fig)


def save_lat_ruler(key, extent):
    w, e, s, n = extent
    lat_span = n - s
    fig = plt.figure(figsize=(RULER_IN, lat_span * SCALE), dpi=DPI)
    ax = fig.add_axes([0.95, 0, 1e-4, 1])
    ax.set_ylim(s, n); ax.set_xlim(0, 1)
    ticks = _ticks(s, n)
    ax.set_yticks(ticks)
    ax.set_yticklabels([fmt_lat(t) for t in ticks], fontsize=11)
    ax.yaxis.set_ticks_position("left")
    ax.tick_params(axis="y", right=False, length=5)
    ax.set_xticks([])
    for sp in ("top", "bottom", "right"):
        ax.spines[sp].set_visible(False)
    out = os.path.join(PIECE_DIR, f"{key}_lat.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)


def save_title(key, title, subtitle=""):
    fig = plt.figure(figsize=(7, 1.0), dpi=DPI)
    txt = title if not subtitle else f"{title}\n{subtitle}"
    fig.text(0.5, 0.5, txt, ha="center", va="center", fontsize=18,
             linespacing=1.4)
    out = os.path.join(PIECE_DIR, f"{key}_title.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def save_colorbar(key, cmap, clim, label, orientation="horizontal",
                  label_pos="bottom", ticks=None, ticklabels=None):
    """`label_pos='top'` puts the text label above the bar (ticks stay below).
    `ticks`/`ticklabels` override the default tick positions/labels (used to show
    the chlorophyll bar in real mg m^-3 even though the color scale is log10)."""
    sm = plt.cm.ScalarMappable(norm=Normalize(clim[0], clim[1]), cmap=cmap)
    if orientation == "horizontal":
        fig = plt.figure(figsize=(4.5, 0.7), dpi=DPI)
        cax = fig.add_axes([0.04, 0.45, 0.92, 0.30])
    else:
        fig = plt.figure(figsize=(0.9, 4.5), dpi=DPI)
        cax = fig.add_axes([0.15, 0.05, 0.30, 0.90])
    cb = fig.colorbar(sm, cax=cax, orientation=orientation)
    cb.set_label(label, fontsize=12)
    if label_pos == "top" and orientation == "horizontal":
        cb.ax.xaxis.set_label_position("top")
    if ticks is not None:
        cb.set_ticks(ticks)
        if ticklabels is not None:
            cb.set_ticklabels(ticklabels)
    cb.ax.tick_params(labelsize=10)
    out = os.path.join(PIECE_DIR, f"{key}.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_globe(wide_extent=WIDE_EXTENT, key="globe"):
    fig = plt.figure(figsize=(3, 3), dpi=DPI)
    draw_globe_inset(fig, [0.03, 0.03, 0.94, 0.94], wide_extent)
    out = os.path.join(PIECE_DIR, f"{key}.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_panel_pieces(panel):
    """Everything one panel exports: bare map + rulers, the three axis-tied maps,
    the title card, and each colorbar with the label below and above the bar."""
    key, extent, draw_fn = panel["key"], panel["extent"], panel["draw"]
    fc = panel.get("facecolor", "none")
    # Standalone: bare map + separate rulers (kept).
    save_map_piece(key, extent, draw_fn, facecolor=fc)
    save_lon_ruler(key, extent)
    save_lat_ruler(key, extent)
    # Axis-tied maps: both / lat-only / lon-only.
    for sides in ("latlon", "lat", "lon"):
        save_map_piece_ticked(key, extent, draw_fn, sides=sides, facecolor=fc)
    save_title(key, panel["title"], panel["subtitle"])
    for i, cb in enumerate(panel.get("colorbars", [])):
        # Label below the bar.
        save_colorbar(f"{key}_cbar{i}", cb["cmap"], cb["clim"], cb["label"],
                      ticks=cb.get("ticks"), ticklabels=cb.get("ticklabels"))
        # Label above the bar.
        if "label_top" in cb:
            save_colorbar(f"{key}_cbar{i}_top", cb["cmap"], cb["clim"],
                          cb["label_top"], label_pos="top",
                          ticks=cb.get("ticks"), ticklabels=cb.get("ticklabels"))
