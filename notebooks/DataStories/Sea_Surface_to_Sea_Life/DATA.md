# Data download guide

The figure scripts don't ship the satellite data — the files are large and live
behind NASA/AVISO data portals. This guide lists exactly what to download and
where to put it so the scripts find it automatically.

## Where the data goes

Downloads live in a **shared data root outside the repo** — by default
`~/Data` — organised as `~/Data/<SOURCE>/<LEVEL>/...`. This keeps the repo small
and lets several projects share one copy of each product (download once, reuse
everywhere).

```
~/Data/
├── SWOT/LR_SSH_Expert/          # SWOT L2 + L3 LR SSH Expert
├── NISAR/L2_GCOV/               # NISAR L2 GCOV
├── MUR-JPL-L4-GLOB-v4.1/        # MUR L4 SST
├── DUACS/MIOST_L4/              # MIOST v3 gridded ADT
├── PACE_OCI/L4m_MOANA/          # PACE OCI L4 MOANA
└── VIIRS_SNPP/L2/               # SNPP VIIRS L2 SST + Ocean Color
```

The code finds each file by **glob pattern, searched recursively** within that
dataset's sub-directory (see `SUBDIR_FOR` and `data_path()` in
`figureN_common.py`). That means:

- Filenames don't have to match the author's exactly. Slightly different
  processing timestamps or version suffixes are fine, as long as the file still
  matches the pattern (e.g. any `SWOT_L3_LR_SSH_Expert_043_410_*_v3.0.nc`).
- Keep **one** file per pattern in each dataset dir. If two files match the same
  pattern the script stops with a "Multiple files match" error asking you to
  remove one.

**Custom location:** to use a different shared root, set the `DATA_ROOT`
environment variable (the legacy `SWOT_DIA_DATA_DIR` still works and takes
precedence if set):

```bash
export DATA_ROOT=/path/to/my/Data          # macOS / Linux
set DATA_ROOT=C:\path\to\my\Data            # Windows (cmd)
```

## Accounts you'll need (all free)

- **NASA Earthdata Login** — for PO.DAAC, OB.DAAC, and ASF: https://urs.earthdata.nasa.gov/
- **AVISO+ account** — for the SWOT L3 product and MIOST: https://www.aviso.altimetry.fr/en/data/data-access.html

The easiest way to find any NASA granule below is **Earthdata Search**
(https://search.earthdata.nasa.gov/) — paste the filename into the search box.

## The overpass

Everything is a single coincident overpass off the U.S. Southeast coast:
**2025-12-28**, SWOT cycle_pass **043_410**, NISAR GCOV **008_170**. The PACE and
VIIRS granules are from the previous day (**2025-12-27**), the nearest clear
ocean-color/SST pass.

## The files

| # | Dataset | Source portal | Put in (under `~/Data/`) | Used by |
|---|---------|---------------|--------|---------|
| 1 | SWOT **L3** LR SSH Expert (v3.0) | AVISO/DUACS (mirrored on PO.DAAC) | `SWOT/LR_SSH_Expert/` | Fig 1 (a, b) |
| 2 | SWOT **L2** LR SSH Expert | PO.DAAC | `SWOT/LR_SSH_Expert/` | Fig 2 (a) |
| 3 | NISAR L2 GCOV | ASF DAAC (Vertex) | `NISAR/L2_GCOV/` | Fig 1 (c) + footprint boxes |
| 4 | MUR L4 SST (GHRSST v4.1) | PO.DAAC | `MUR-JPL-L4-GLOB-v4.1/` | Fig 1 (a) |
| 5 | MIOST v3 gridded ADT | AVISO | `DUACS/MIOST_L4/` | Fig 1 (b), Fig 2 (a) |
| 6 | PACE OCI L4 MOANA | NASA OB.DAAC | `PACE_OCI/L4m_MOANA/` | Fig 1 (d) |
| 7 | SNPP VIIRS L2 SST | NASA OB.DAAC | `VIIRS_SNPP/L2/` | Fig 2 (b) |
| 8 | SNPP VIIRS L2 Ocean Color | NASA OB.DAAC | `VIIRS_SNPP/L2/` | Fig 2 (b, c) |
| — | ETOPO 2022 30″ relief | NOAA NCEI (streamed) | *no download* | Fig 1 globe inset |

### 1 — SWOT L3 LR SSH Expert (v3.0)
- **Author's file:** `SWOT_L3_LR_SSH_Expert_043_410_20251228T034857_20251228T044023_v3.0.nc`
- **Matched by:** `SWOT_L3_LR_SSH_Expert_043_410_*_v3.0.nc`
- **Where:** AVISO+ (product "SWOT L3 SSH", DUACS processing). Also mirrored at
  PO.DAAC (https://podaac.jpl.nasa.gov/) — search Earthdata for the filename.
- Provides SSHA (`ssha_unfiltered`), MDT, and geostrophic velocities for Fig 1.

### 2 — SWOT L2 LR SSH Expert
- **Author's file:** `SWOT_L2_LR_SSH_Expert_043_410_20251228T034856_20251228T043941_PID0_01.nc`
- **Matched by:** `SWOT_L2_LR_SSH_Expert_043_410_*.nc`
- **Where:** PO.DAAC — collection "SWOT Level 2 KaRIn Low Rate Sea Surface Height
  Expert". Find on https://podaac.jpl.nasa.gov/ or Earthdata Search.
- Fig 2 forms ADT from `ssha_karin + height_cor_xover + mean_dynamic_topography`.

### 3 — NISAR L2 GCOV
- **Author's file:** `NISAR_L2_PR_GCOV_008_170_D_073_0005_NADV_A_20251228T000335_20251228T000404_X05009_N_F_J_001.h5`
- **Matched by:** `NISAR_L2_PR_GCOV_008_170_*.h5`
- **Where:** ASF DAAC via Vertex (https://search.asf.alaska.edu/) — search for the
  NISAR GCOV granule `008_170`.
- Fig 1 (c) reads the `VHVH` band from group `science/LSAR/GCOV/grids/frequencyB`;
  both figures also draw its footprint polygon.

### 4 — MUR L4 SST
- **Author's file:** `20251228090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1_subsetted.nc`
- **Matched by:** `*MUR-GLOB*.nc`
- **Where:** PO.DAAC GHRSST — collection **MUR-JPL-L4-GLOB-v4.1**
  (https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1).
- The author spatially **subset** the global file (hence `_subsetted`) via the
  PO.DAAC subsetter/Earthdata. The full global daily file for 2025-12-28 also
  works — the loader crops to the study region itself. Any name still matches
  `*MUR-GLOB*.nc`.

### 5 — MIOST v3 gridded ADT
- **Author's file:** `dt_global_allsat_phy_l4_20251228_20250112.nc`
- **Matched by:** `dt_global_allsat_phy_l4_*.nc`
- **Where:** AVISO+ (MIOST v3 gridded / DUACS delayed-time global L4 `adt`).
- Used as the ADT background in Fig 1 (b) and Fig 2 (a).

### 6 — PACE OCI L4 MOANA
- **Author's file:** `PACE_OCI.20251227.L4m.DAY.MOANA.V3_1.4km.nc`
- **Matched by:** `PACE_OCI.*.L4m.DAY.MOANA.*.nc`
- **Where:** NASA OB.DAAC (https://oceancolor.gsfc.nasa.gov/) — PACE OCI MOANA
  picophytoplankton mapped product. Browse/download via Earthdata Search or
  https://oceandata.sci.gsfc.nasa.gov/.
- Fig 1 (d) blends `prococcus_moana`, `syncoccus_moana`, `picoeuk_moana`.

### 7 & 8 — SNPP VIIRS L2 SST and Ocean Color
- **Author's files:**
  - `SNPP_VIIRS.20251227T184800.L2.SST.NRT.nc`
  - `SNPP_VIIRS.20251227T184800.L2.OC.NRT.nc`
- **Matched by:** `*VIIRS*.L2.SST*.nc` and `*VIIRS*.L2.OC*.nc`
- **Where:** NASA OB.DAAC (https://oceancolor.gsfc.nasa.gov/) — SNPP VIIRS Level-2
  SST and Ocean Color for the **same granule** (2025-12-27 18:48 UTC). Get both.
- Fig 2 (c) plots `chlor_a` from the OC file; Fig 2 (b) plots `sst` from the SST
  file **masked to the OC granule's valid chlorophyll pixels**, so the two must be
  the same granule/grid.

### ETOPO 2022 — no download
Fig 1's globe inset streams ETOPO 2022 (30″) bathymetry from NOAA's THREDDS
OPeNDAP server at run time; you only need an internet connection. If the stream
fails, the inset falls back to a flat ocean fill, so the figure still renders.
Source: https://www.ncei.noaa.gov/products/etopo-global-relief-model.

## Check your setup

With the data in place, from a figure directory:

```bash
cd "Data in Action Figure 2"
python Figure2_panelC.py     # uses only the VIIRS OC file
```

If a file is missing you'll get a clear message naming the pattern and the
directory searched, e.g.:

```
FileNotFoundError: No data file matching '*VIIRS*.L2.OC*.nc'.
See DATA.md for what to download and where to put it. Looked under: .../data
```
