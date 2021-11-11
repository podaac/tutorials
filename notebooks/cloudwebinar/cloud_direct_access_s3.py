#!/usr/bin/env python3


######Importing modules needed for the subseting operation

import s3fs
import requests
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from os.path import dirname, join
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import earthdata

###############################################################################
from earthdata import Auth 
auth = Auth().login()

def begin_s3_direct_access():
    url="https://archive.podaac.earthdata.nasa.gov/s3credentials"
    response = requests.get(url).json()
    return s3fs.S3FileSystem(key=response['accessKeyId'],secret=response['secretAccessKey'],token=response['sessionToken'],client_kwargs={'region_name':'us-west-2'})

###############################################################################
####################### Begin S3 access 

fs = begin_s3_direct_access()
mur_v42_2020_files = fs.glob(join("podaac-ops-cumulus-protected/", "MUR25-JPL-L4-GLOB-v04.2", "202001*.nc"))


mur_v42_2020_Dataset = xr.open_mfdataset(
    paths=[fs.open(f) for f in mur_v42_2020_files],
    combine='by_coords',
    mask_and_scale=True,
    decode_cf=True,
    chunks={'time': 1}      # analysis.
)
mur_v42_2020_Dataset.close()
mur_v42_2020 = mur_v42_2020_Dataset.analysed_sst


####################### Slice MUR data
mur_v42_2020_gom = mur_v42_2020.sel(lat=slice(-89, 89), lon=slice(-179, 179))


fig = plt.figure(figsize=(16,6))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.coastlines()
ax.set_extent([mur_v42_2020_gom.lon.min(), 
                mur_v42_2020_gom.lon.max(), 
                mur_v42_2020_gom.lat.min(), 
                mur_v42_2020_gom.lat.max()])
                
####################### Plot and save the data
mur_v42_2020_gom.isel(time=0).plot(ax=ax, transform=ccrs.PlateCarree(), cmap='Spectral_r')
plt.savefig("pltsavefile.png")
plt.clf()
