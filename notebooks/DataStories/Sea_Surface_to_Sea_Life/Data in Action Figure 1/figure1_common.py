# %% [markdown]
# # Figure 1 common: shared config, loaders, draw primitives, modular piece renderer
#
# Shared by the composite script and the four panel scripts, so each can be run on
# its own:
#
#   * Figure1.py / .ipynb          -- composite + every piece (all four panels)
#   * Figure1_panelA.py / .ipynb   -- MUR SST + SWOT geostrophic speed (+ globe)
#   * Figure1_panelB.py / .ipynb   -- MIOST v3 ADT + SWOT ADT + velocity quiver
#   * Figure1_panelC.py / .ipynb   -- NISAR GCOV VH grayscale
#   * Figure1_panelD.py / .ipynb   -- PACE MOANA picophytoplankton ternary
#
# Nothing here draws on import; the panel scripts load only the data they need.

# %%
import os
import re
import glob
import socket
import threading
import warnings

import numpy as np
import xarray as xr
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, ListedColormap
from matplotlib.ticker import MaxNLocator
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.transform import array_bounds
from scipy.ndimage import uniform_filter

# %% [markdown]
# ## Config

# %%
# Raw input data lives under the shared data root, organised as
# DATA_ROOT/<SOURCE>/<LEVEL>/... so each product is downloaded only once and
# reused across projects. Defaults to ~/Data. Override with the DATA_ROOT env
# var (or the legacy SWOT_DIA_DATA_DIR, which wins if set).
# See DATA.md for what to download and where to put it.
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("DATA_ROOT", os.path.join(os.path.expanduser("~"), "Data"))
DATA_ROOT = os.environ.get("SWOT_DIA_DATA_DIR", DATA_ROOT)

# Each constant is a filename glob (not a full path); data_path() resolves it to
# the actual downloaded file under its shared-root subdirectory (see SUBDIR_FOR).
SWOT_EXPERT_FILE = "SWOT_L3_LR_SSH_Expert_043_410_*_v3.0.nc"
NISAR_FILE       = "NISAR_L2_PR_GCOV_008_170_*.h5"
MUR_FILE         = "*MUR-GLOB*.nc"
MIOST_FILE       = "dt_global_allsat_phy_l4_*.nc"
MOANA_FILE       = "PACE_OCI.*.L4m.DAY.MOANA.*.nc"

# Map each input glob to its shared-root subdirectory under DATA_ROOT.
SUBDIR_FOR = {
    SWOT_EXPERT_FILE: os.path.join("SWOT", "LR_SSH_Expert"),
    NISAR_FILE:       os.path.join("NISAR", "L2_GCOV"),
    MUR_FILE:         "MUR-JPL-L4-GLOB-v4.1",
    MIOST_FILE:       os.path.join("DUACS", "MIOST_L4"),
    MOANA_FILE:       os.path.join("PACE_OCI", "L4m_MOANA"),
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


NISAR_GROUP = "science/LSAR/GCOV/grids/frequencyB"
BOX_PAD = 0.15               # deg padding around the NISAR footprint (zoom extent)

WIDE_EAST_CUTOFF = -75.0     # panel (a) east edge (deg lon)

# NISAR grayscale: warp linear power -> dB -> stretch -> gamma.
NISAR_POL        = "VHVH"          # cross-pol VH
NISAR_POL_SHORT  = "VH"
NISAR_DST_EPSG   = 4326
NISAR_STRETCH    = "percentile"
NISAR_DB_CLIP    = (-20.0, -10.0)  # fallback when NISAR_STRETCH != "percentile"
NISAR_DB_PCT     = (5.0, 95.0)
NISAR_GAMMA      = 0.5
NISAR_SMOOTH_PX  = 0

# Scale for the NISAR panel: grayscale in backscatter (dB) over the percentile clip.
# The displayed brightness is stretch(dB)**GAMMA, so the colorbar uses a gamma-
# encoded gray ramp (gray = x**GAMMA) on a linear dB axis -> bar matches the image.
_nisar_g = np.linspace(0.0, 1.0, 256) ** NISAR_GAMMA
NISAR_CMAP = ListedColormap(
    np.column_stack([_nisar_g, _nisar_g, _nisar_g, np.ones_like(_nisar_g)]),
    name="nisar_gray_gamma")
NISAR_CLIM = None                 # set from the percentile dB clip at run time

# SWOT L3 Expert: SSHA = ssha_unfiltered, ADT = ssha_unfiltered + mdt (m)
SSHA_VAR = "ssha_unfiltered"
MDT_VAR  = "mdt"
SSHA_QUALITY_MAX = 3
# Geostrophic velocity (absolute) read straight from the L3 file (geos_v1 style).
UGOS_VAR = "ugos_filtered"
VGOS_VAR = "vgos_filtered"
# Geostrophic SPEED = hypot(ugos, vgos) -- panel (a) swath fill
SPEED_CMAP = "Spectral_r"
SPEED_CLIM = (0.0, 1.5)      # m/s
GEOS_SUBSAMPLE = 2           # quiver every n-th pixel
GEOS_SCALE     = 20          # quiver scale (m/s per unit length)
GEOS_WIDTH     = 0.0015
GEOS_KEY_MS    = 0.5         # reference-arrow magnitude (m/s)

MUR_VAR  = "analysed_sst"    # kelvin -> degC
GRID_ADT_VAR = "adt"
GRID_LAT = "latitude"
GRID_LON = "longitude"

ADT_CMAP = "Spectral_r"      # ADT (cm)
SST_CMAP = "turbo"           # MUR SST (degC)
ADT_CLIM = None
SST_CLIM = None

# PACE MOANA ternary composite
MOANA_VARS   = ["prococcus_moana", "syncoccus_moana", "picoeuk_moana"]
MOANA_LABELS = ["Prochlorococcus", "Synechococcus", "Picoeukaryotes"]
MOANA_CORNER_COLORS = np.array([
    [0.00, 0.00, 1.00],
    [1.00, 0.40, 0.50],
    [0.60, 0.85, 1.00],
])
MOANA_CHANNEL_MAX = np.array([5.0e5, 8.0e4, 3.0e4])
MOANA_TRI_XY = np.array([[0.5, 1.0], [0.0, 0.0], [1.0, 0.0]])
MOANA_BG = "#101418"

# ETOPO 2022 (30 arc-second) global surface elevation, streamed from NOAA THREDDS
# OPeNDAP. Subsampled by ETOPO_STRIDE for the small inset; ocean depths colored,
# land left to the gray LAND feature.
ETOPO_URL    = "https://www.ngdc.noaa.gov/thredds/dodsC/global/ETOPO2022/30s/30s_surface_elev_netcdf/ETOPO_2022_v1_30s_N90W180_surface.nc"
ETOPO_STRIDE = 30            # keep every Nth point (30s * 30 ~ 0.25 deg inset grid)
ETOPO_TIMEOUT = 60           # seconds to wait for the OPeNDAP stream before giving up
ETOPO_CMAP   = "Blues_r"     # deep = dark navy, shelf = near-white
ETOPO_CLIM   = (-6000.0, 0.0)  # m (ocean only)

# Output
OUT_DIR   = os.path.dirname(os.path.abspath(__file__))
PIECE_DIR = os.path.join(OUT_DIR, "pieces")
COMPOSITE = os.path.join(OUT_DIR, "Figure1_composite")

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


def load_swot(swot_file, lat_range, lon_range):
    swot_file = data_path(swot_file)
    ds = xr.open_dataset(swot_file)
    sub, lat, lon = _crop_rows(ds, lat_range, lon_range)
    ssha_cm = (sub[SSHA_VAR].where(sub["quality_flag"] <= SSHA_QUALITY_MAX).values
               * 100.0)
    adt_cm = ssha_cm + sub[MDT_VAR].values * 100.0
    ugos = sub[UGOS_VAR].values                       # absolute geostrophic u (m/s)
    vgos = sub[VGOS_VAR].values                       # absolute geostrophic v (m/s)
    spd = np.hypot(ugos, vgos)                         # geostrophic speed (m/s)
    t = str(sub["time"].values[len(sub["time"]) // 2])
    return dict(lat=lat, lon=lon, ssha=ssha_cm, adt=adt_cm, ugos=ugos, vgos=vgos,
                spd=spd, time=t[:19], date=t[:10], cycle_pass=parse_swot_id(swot_file))


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


def load_mur(path, lat_range, lon_range):
    path = data_path(path)
    ds = xr.open_dataset(path)
    da = ds[MUR_VAR]
    if "time" in da.dims:
        da = da.isel(time=0)
    sub = da.sel(lat=slice(lat_range[0], lat_range[1]), lon=slice(lon_range[0], lon_range[1]))
    sst = sub.values.astype(float) - 273.15
    return dict(lat=sub["lat"].values, lon=sub["lon"].values, sst=sst)


def load_grid_field(path, var, lat_range, lon_range):
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


def moana_blend_rgba(arrs):
    normed = [np.clip(a / mx, 0.0, 1.0) for a, mx in zip(arrs, MOANA_CHANNEL_MAX)]
    stack = np.dstack(normed)
    valid = np.all(np.isfinite(stack), axis=2)
    rgb = np.nan_to_num(stack) @ MOANA_CORNER_COLORS
    rgb = np.clip(rgb, 0, 1)
    alpha = valid.astype(float)[:, :, None]
    return np.concatenate([rgb, alpha], axis=2), valid


def load_moana(path, lat_range, lon_range):
    path = data_path(path)
    ds = xr.open_dataset(path)
    sub = ds.sortby("lat").sortby("lon").sel(
        lat=slice(lat_range[0], lat_range[1]),
        lon=slice(lon_range[0], lon_range[1]))
    arrs = [np.where(np.isfinite(sub[v].values) & (sub[v].values > 0),
                     sub[v].values, np.nan).astype(float) for v in MOANA_VARS]
    rgba, valid = moana_blend_rgba(arrs)
    lat = sub["lat"].values
    lon = sub["lon"].values
    extent = [float(lon.min()), float(lon.max()), float(lat.min()), float(lat.max())]
    date = str(ds.attrs.get("time_coverage_start", ""))[:10]
    return dict(rgba=rgba, extent=extent, date=date,
                n_valid=int(valid.sum()), n_total=int(valid.size))


def _stretch(db, clip):
    lo, hi = clip
    return np.clip((db - lo) / (hi - lo), 0.0, 1.0)


def _nan_boxcar(arr, size):
    filled = np.where(np.isfinite(arr), arr, 0.0)
    wsum = uniform_filter(filled, size)
    wcnt = uniform_filter(np.isfinite(arr).astype(float), size)
    return np.where(wcnt > 0, wsum / np.maximum(wcnt, 1e-12), np.nan)


def _warp_band(path, pol, dst_crs, transform, width, height):
    sub = f'NETCDF:"{path}":/{NISAR_GROUP}/{pol}'
    with rasterio.open(sub) as src:
        out = np.full((height, width), np.nan, dtype="float32")
        reproject(
            source=rasterio.band(src, 1), destination=out,
            src_transform=src.transform, src_crs=src.crs,
            dst_transform=transform, dst_crs=dst_crs,
            src_nodata=src.nodata, dst_nodata=np.nan,
            resampling=Resampling.cubic)
    return out


def load_nisar(path, pol=NISAR_POL):
    """Warp one GCOV polarization to EPSG:4326, dB-stretch, gamma-encode -> RGBA.

    NISAR GCOV stores gamma-naught (gamma0) backscatter -- the h5 metadata
    radiometricTerrainCorrection.outputBackscatterNormalizationConvention =
    "gamma0" and rtcGammaToSigmaFactor is NOT applied -- so the colorbar label is
    gamma^0. The percentile clip is rounded to whole dB ONCE here so that the same
    clip drives BOTH the image stretch and the colorbar dB axis.
    """
    path = data_path(path)
    dst_crs = f"EPSG:{NISAR_DST_EPSG}"
    pol_sub = f'NETCDF:"{path}":/{NISAR_GROUP}/{pol}'
    with rasterio.open(pol_sub) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)

    band = _warp_band(path, pol, dst_crs, transform, width, height)
    if NISAR_SMOOTH_PX and NISAR_SMOOTH_PX > 1:
        band = _nan_boxcar(band, NISAR_SMOOTH_PX)

    valid = np.isfinite(band) & (band > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        band_db = np.where(valid, 10.0 * np.log10(band), np.nan)

    if NISAR_STRETCH == "percentile":
        raw = np.nanpercentile(band_db, NISAR_DB_PCT)
        clip = (float(np.floor(raw[0])), float(np.ceil(raw[1])))
        print(f"NISAR {pol} percentile clip: {raw[0]:.1f} .. {raw[1]:.1f} dB "
              f"-> rounded {clip[0]:.0f} .. {clip[1]:.0f} dB")
    else:
        clip = NISAR_DB_CLIP
    gray = _stretch(band_db, clip)
    if NISAR_GAMMA != 1.0:
        gray = gray ** NISAR_GAMMA

    rgba = np.zeros((height, width, 4), dtype=float)
    for ch in range(3):
        rgba[..., ch] = np.where(valid, gray, 0.0)
    rgba[..., 3] = valid.astype(float)

    west, south, east, north = array_bounds(height, width, transform)
    with h5py.File(path, "r") as f:
        wkt = f["science/LSAR/identification/boundingPolygon"][()].decode()
        t0 = f["science/LSAR/identification/zeroDopplerStartTime"][()].decode()
    flon, flat = parse_bounding_polygon(wkt)
    return dict(rgba=rgba, pc_extent=[west, east, south, north], clip=clip, pol=pol,
                flon=flon, flat=flat, date=t0[:10], time=t0[:19])


def nisar_box_extent(nisar, pad=BOX_PAD):
    """Zoom extent (w, e, s, n) padded around the NISAR footprint."""
    return (float(nisar["flon"].min() - pad), float(nisar["flon"].max() + pad),
            float(nisar["flat"].min() - pad), float(nisar["flat"].max() + pad))


def load_etopo(url=ETOPO_URL, stride=ETOPO_STRIDE, timeout=ETOPO_TIMEOUT):
    """Stream ETOPO 2022 (subsampled) from NOAA OPeNDAP. Returns None on failure
    OR if the stream does not complete within `timeout` seconds, so the globe
    inset falls back to a flat ocean fill instead of hanging on a slow or
    unreachable OPeNDAP server. The fetch runs in a daemon thread with a socket
    timeout, so a stuck request never blocks the figure."""
    result = {}

    def _fetch():
        try:
            ds = xr.open_dataset(url)
            sub = ds.isel(lat=slice(None, None, stride), lon=slice(None, None, stride))
            sub = sub.sortby("lat").sortby("lon")
            z = sub["z"].values.astype(float)
            result["out"] = dict(lon=sub["lon"].values, lat=sub["lat"].values, z=z)
            print(f"ETOPO streamed: {z.shape} (stride {stride})")
        except Exception as exc:                          # network / OPeNDAP / engine
            result["err"] = exc

    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        t = threading.Thread(target=_fetch, daemon=True)
        t.start()
        t.join(timeout)
    finally:
        socket.setdefaulttimeout(old_timeout)

    if t.is_alive():
        warnings.warn(f"ETOPO stream timed out after {timeout}s; inset uses flat ocean fill.")
        return None
    if "err" in result:
        warnings.warn(f"ETOPO stream failed ({result['err']}); inset uses flat ocean fill.")
        return None
    return result.get("out")

# %% [markdown]
# ## Color limits (set once from the loaded data, read by the draw functions)

# %%
def set_adt_clim(swot, grid=None, pct=(2, 98)):
    """ADT color limits shared by the SWOT swath and the MIOST grid (cm)."""
    global ADT_CLIM
    vals = [swot["adt"][np.isfinite(swot["adt"])].ravel()]
    if grid is not None:
        vals.append(grid["val"][np.isfinite(grid["val"])].ravel())
    a = np.nanpercentile(np.concatenate(vals), list(pct))
    ADT_CLIM = (float(np.floor(a[0])), float(np.ceil(a[1])))
    return ADT_CLIM


def set_sst_clim(mur, extent, pct=(2, 98)):
    """MUR SST color limits over the panel (a) window (degC)."""
    global SST_CLIM
    lat_win = (mur["lat"] >= extent[2]) & (mur["lat"] <= extent[3])
    lon_win = (mur["lon"] >= extent[0]) & (mur["lon"] <= extent[1])
    s = np.nanpercentile(mur["sst"][np.ix_(lat_win, lon_win)], list(pct))
    SST_CLIM = (float(np.floor(s[0])), float(np.ceil(s[1])))
    return SST_CLIM


def set_nisar_clim(nisar):
    """NISAR colorbar dB limits = the clip already rounded in load_nisar."""
    global NISAR_CLIM
    NISAR_CLIM = (float(nisar["clip"][0]), float(nisar["clip"][1]))
    return NISAR_CLIM

# %% [markdown]
# ## Draw primitives

# %%
def draw_swot_adt(ax, swot, pc, **kw):
    return ax.pcolormesh(swot["lon"], swot["lat"], swot["adt"], cmap=ADT_CMAP,
                         vmin=ADT_CLIM[0], vmax=ADT_CLIM[1], shading="auto",
                         transform=pc, **kw)


def draw_swot_speed(ax, swot, pc, **kw):
    return ax.pcolormesh(swot["lon"], swot["lat"], swot["spd"], cmap=SPEED_CMAP,
                         vmin=SPEED_CLIM[0], vmax=SPEED_CLIM[1], shading="auto",
                         transform=pc, **kw)


def draw_nisar(ax, nisar, pc, **kw):
    return ax.imshow(nisar["rgba"], extent=nisar["pc_extent"], origin="upper",
                     transform=pc, interpolation="nearest", **kw)


def draw_nisar_footprint(ax, nisar, pc, color="k", lw=1.6, ls="--"):
    ax.plot(nisar["flon"], nisar["flat"], color=color, linewidth=lw, linestyle=ls,
            transform=pc, zorder=7)


def draw_box_rect(ax, lon_range, lat_range, pc, color="k", lw=1.8):
    lo0, lo1 = lon_range; la0, la1 = lat_range
    ax.plot([lo0, lo1, lo1, lo0, lo0], [la0, la0, la1, la1, la0],
            color=color, linewidth=lw, transform=pc, zorder=7)


def draw_swath_bars(ax, swot, pc, field="adt", lw=1.4):
    for col in swath_boundary_cols(swot[field]):
        ax.plot(swot["lon"][:, col], swot["lat"][:, col], "k",
                linewidth=lw, transform=pc, zorder=7)


def draw_geostrophic(ax, swot, pc):
    n = GEOS_SUBSAMPLE
    return ax.quiver(swot["lon"][::n, ::n], swot["lat"][::n, ::n],
                     swot["ugos"][::n, ::n], swot["vgos"][::n, ::n],
                     color="k", scale=GEOS_SCALE, width=GEOS_WIDTH,
                     transform=pc, zorder=8)


def coast(ax, color="k"):
    try:
        ax.coastlines("10m", linewidth=0.6, color=color)
    except Exception as exc:
        warnings.warn(f"coastlines unavailable: {exc}")


def draw_moana_legend(ax, n=120, text_color="k", labels=True):
    """Ternary triangle color key (barycentric blend of the corner colors)."""
    xs, ys, cols = [], [], []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            k = n - i - j
            f = np.array([i, j, k]) / n
            xy = f @ MOANA_TRI_XY
            xs.append(xy[0]); ys.append(xy[1])
            cols.append(np.clip(f @ MOANA_CORNER_COLORS, 0, 1))
    ax.scatter(xs, ys, c=cols, s=4, marker="s", edgecolors="none")
    if labels:
        ax.text(0.5, 1.06, MOANA_LABELS[0], ha="center", va="bottom", color=text_color, fontsize=7)
        ax.text(-0.12, -0.06, MOANA_LABELS[1], ha="center", va="top", color=text_color, fontsize=7)
        ax.text(1.12, -0.06, MOANA_LABELS[2], ha="center", va="top", color=text_color, fontsize=7)
    ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.28, 1.30)
    ax.set_aspect("equal"); ax.axis("off")


def draw_globe_inset(fig, rect, wide_extent, etopo=None):
    lon0 = 0.5 * (wide_extent[0] + wide_extent[1])
    lat0 = 0.5 * (wide_extent[2] + wide_extent[3])
    axg = fig.add_axes(rect, projection=ccrs.Orthographic(
        central_longitude=lon0, central_latitude=lat0))
    axg.set_global()
    if etopo is not None:
        axg.imshow(np.ma.masked_greater(etopo["z"], 0.0), origin="lower",
                   extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree(),
                   cmap=ETOPO_CMAP, vmin=ETOPO_CLIM[0], vmax=ETOPO_CLIM[1], zorder=0)
    else:
        axg.add_feature(cfeature.OCEAN, facecolor="#9ecbe8", zorder=0)
    axg.add_feature(cfeature.LAND, facecolor="0.7", edgecolor="k",
                    linewidth=0.3, zorder=1)
    draw_box_rect(axg, (wide_extent[0], wide_extent[1]),
                  (wide_extent[2], wide_extent[3]), ccrs.PlateCarree(), lw=1.5)
    return axg

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
    return f"{abs(x):.0f}°{h}"


def fmt_lat(y):
    h = "N" if y > 0 else ("S" if y < 0 else "")
    return f"{abs(y):.0f}°{h}"


def _fmt_lon_prec(v, ticks):
    """Lon label with just enough decimals for the tick spacing (avoids '.0f'
    rounding adjacent sub-degree ticks to the same integer)."""
    step = min((abs(b - a) for a, b in zip(ticks, ticks[1:])), default=1.0)
    dec = 0 if step >= 1 else (1 if step >= 0.1 else 2)
    x = ((v + 180) % 360) - 180
    h = "W" if x < 0 else ("E" if x > 0 else "")
    return f"{abs(x):.{dec}f}°{h}"


def _ticks(lo, hi, n=5):
    t = MaxNLocator(nbins=n, steps=[1, 2, 2.5, 5, 10]).tick_values(lo, hi)
    return [v for v in t if lo <= v <= hi]


def _ruler_ticks(lo, hi, width_in, label_in=0.55):
    """Tick count that fits `width_in` inches of strip without crowding labels."""
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


def save_map_piece_ticked(key, extent, draw_fn, sides="latlon", facecolor="none",
                          label_color="k"):
    """Self-contained map with the axis labels TIED to the panel (cartopy gridline
    labels). `sides`: 'latlon', 'lat', or 'lon'. Saved with a tight bbox so the
    labels are included (the bare map + standalone rulers are still written too)."""
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
    gl.xlabel_style = {"size": 10, "color": label_color}
    gl.ylabel_style = {"size": 10, "color": label_color}
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
    ticks = _ruler_ticks(w, e, width_in)          # tick count scaled to strip width
    # Drop edge-hugging ticks whose labels would overflow the (un-cropped) strip.
    half_deg = 0.5 * 0.55 / SCALE
    interior = [t for t in ticks if (t - w) > half_deg and (e - t) > half_deg]
    ticks = interior or ticks
    ax.set_xticks(ticks)
    ax.set_xticklabels([_fmt_lon_prec(t, ticks) for t in ticks], fontsize=9)
    ax.xaxis.set_ticks_position("bottom")
    ax.tick_params(axis="x", top=False, length=5)
    ax.set_yticks([])
    for sp in ("top", "left", "right"):
        ax.spines[sp].set_visible(False)
    out = os.path.join(PIECE_DIR, f"{key}_lon.png")
    # No bbox_inches="tight": keep figure width == map width so it still aligns.
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
                  label_pos="bottom"):
    """`label_pos='top'` puts the text label above the bar (ticks stay below)."""
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
    cb.ax.tick_params(labelsize=10)
    out = os.path.join(PIECE_DIR, f"{key}.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_colorbar_set(key, cmap, clim, label, label_top=None):
    """The three bar variants each panel ships: horizontal (label below),
    horizontal (short label above), and vertical."""
    save_colorbar(key, cmap, clim, label)
    if label_top:
        save_colorbar(f"{key}_top", cmap, clim, label_top, label_pos="top")
    save_colorbar(f"{key}_vert", cmap, clim, label, orientation="vertical")


def save_velocity_key(key="panelB_velkey"):
    fig = plt.figure(figsize=(2.2, 1.0), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.annotate("", xy=(0.80, 0.62), xytext=(0.15, 0.62),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=2.0))
    ax.text(0.475, 0.40, f"{GEOS_KEY_MS:g} m s$^{{-1}}$",
            ha="center", va="top", fontsize=13)
    out = os.path.join(PIECE_DIR, f"{key}.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_globe(wide_extent, etopo=None, key="panelA_globe"):
    fig = plt.figure(figsize=(3, 3), dpi=DPI)
    draw_globe_inset(fig, [0.03, 0.03, 0.94, 0.94], wide_extent, etopo=etopo)
    out = os.path.join(PIECE_DIR, f"{key}.png")
    fig.savefig(out, dpi=DPI, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {os.path.basename(out)}")


def save_moana_legend(key="panelD_moana_legend"):
    for suffix, labels in (("", True), ("_triangle", False)):
        fig = plt.figure(figsize=(3, 3), dpi=DPI, facecolor="w")
        ax = fig.add_axes([0.05, 0.05, 0.90, 0.90])
        ax.set_facecolor("w")
        draw_moana_legend(ax, text_color="k", labels=labels)
        out = os.path.join(PIECE_DIR, f"{key}{suffix}.png")
        fig.savefig(out, dpi=DPI, facecolor="w", bbox_inches="tight")
        plt.close(fig)
        print(f"  {os.path.basename(out)}")


def save_panel_pieces(key, extent, draw_fn, title, subtitle, colorbars=(),
                      facecolor="none", label_color="k"):
    """Everything one panel exports: bare map + rulers, the three axis-tied maps,
    the title card, and each colorbar in its three variants."""
    save_map_piece(key, extent, draw_fn, facecolor=facecolor)
    save_lon_ruler(key, extent)
    save_lat_ruler(key, extent)
    for sides in ("latlon", "lat", "lon"):
        save_map_piece_ticked(key, extent, draw_fn, sides=sides,
                              facecolor=facecolor, label_color=label_color)
    save_title(key, title, subtitle)
    for i, cb in enumerate(colorbars):
        save_colorbar_set(f"{key}_cbar{i}", cb["cmap"], cb["clim"], cb["label"],
                          cb.get("label_top"))
