# PO.DAAC Tutorials

![N|Solid](https://podaac.jpl.nasa.gov/sites/default/files/image/custom_thumbs/podaac_logo.png)

Explore the [**PO.DAAC Cookbook**](https://podaac.github.io/tutorials/), a curated webpage of our data recipes. It's a place to find cloud relevant tutorials on how to use PO.DAAC and Earthdata tools, services, and data.

Most tutorials in this repository take the form of python notebooks. [Jupyter](https://jupyter.org/) is a very popular version of python notebooks, and is used extensively by the PO.DAAC team.

| Notebook| Link | Summary | Services and Tools |
|----|-----| ----| ----|
|Amazon River Estuary Exploration|[notebook (direct access in AWS cloud)](https://github.com/podaac/tutorials/blob/master/notebooks/meetings_workshops/workshop_osm_2022/CloudAWS_AmazonRiver_Estuary_Exploration.ipynb)|Explore relationship between oceanography and hydrology data in the Amazon Estuary from the on-prem and Earthdata Cloud archives|Earthdata Search, S3, s3fs, direct in region cloud acess|
|Amazon River Estuary Exploration|[notebook (download data & run on local machine)](https://github.com/podaac/tutorials/blob/master/notebooks/meetings_workshops/workshop_osm_2022/Cloud_DirectDownload_AmazonRiver_Estuary_Exploration.ipynb)|Explore relationship between oceanography and hydrology data in the Amazon Estuary from the on-prem and Earthdata Cloud archives|Earthdata Search|
|MODIS L2P SST Datacube|[notebook](./notebooks/MODIS_L2P_SST_DataCube.ipynb)|How to create a gridded "Data Cube", essentially an ARD, from native Level 2P sea surface temperature (SST) data from MODIS Aqua|Harmony, GDAL NCO|
|HUC Feature Translation Service Examples|[notebook](https://github.com/podaac/tutorials/blob/master/notebooks/HUC%20Feature%20Translation%20Service%20Examples-updated-20210804.ipynb)|Examples of how to use the PO.DAAC Feature Translation Service (FTS) to search using USGS HUC ID or name.|CMR, FTS|
|Feature Translation Service - SWORD River Demo|[notebook](https://github.com/podaac/tutorials/blob/master/notebooks/SWORD_River_Demo.ipynb)|Search and visualize river reaches and nodes from the SWOT River Database (SWORD), and geospatially search for data for the river reach/note of interest in NASA CMR.|FTS-SWORD, CMR|
|Estuary exploration in the cloud using ZARR|[notebook](./notebooks/SWOT-EA-2021/Estuary_explore_inCloud_zarr.ipynb)|Analyze relationships between river height and land water equivalent thickness in the Amazon River estuary in the cloud, using cloud optimized format (zarr).|Harmony, ZARR|
|Co-locating satellite and in-situ data|[notebook](./notebooks/SWOT-EA-2021/Colocate_satellite_insitu_ocean.ipynb)|Co-locate in-situ measurements and satellite data near the European coast for cross-validation of data or model validation.|CMR, Harmony L2 Subsetter|
|Pre-SWOT ECCO-based Simulation data example|[notebook](./notebooks/Pre-SWOT_Numerical_Simulation_Demo.ipynb)|A demonstration of direct access of the ECCO-based Pre-SWOT numerical simulation data from the PO.DAAC Earthdata Cloud.|direct S3 access, download|
|Subsetting Swath data with Harmony |[notebook](./notebooks/harmony%20subsetting/Harmony%20L2%20Subsetter.ipynb)||Harmony|
|CMR Tutorials|[notebook](./notebooks/podaac_cmr_tutorial.ipynb)||CMR|
|CMR Shapefile Search|[notebook](./notebooks/Podaac_CMR_Shapefile_Search.ipynb)||CMR|
|Using a shapefile to search MODIS data in CMR|[notebook](./notebooks/PODAAC_CMR_Shapefile_Search_MODIS_UAT.ipynb)||CMR|
|Accessiing near-real time Sentinel-6 MF data|[notebook](./notebooks/sentinel-6/Access_Sentinel6_NRT.ipynb)||CMR, download|
|Accessing Sentinel-6 data by cycle and pass|[notebook](./notebooks/sentinel-6/Access_Sentinel6_By_CyclePass.ipynb)| For more recent, python script, see [here](https://github.com/podaac/sentinel6)|CMR, download|
|Subsetting and plotting swath data in the cloud|[notebook](./notebooks/Cloud%20L2SS%20subset%20and%20plot%20-%20JH.ipynb)||Harmony, Subsetting|
|Regridding swath data in the cloud|[notebook](./notebooks/l2-regridding/reprojection%20notebook.ipynb)||Harmony, Regridding|
|Subsetting via OPeNDAP in the cloud|[notebook](./notebooks/opendap/MUR-OPeNDAP.ipynb)||Subsetting, OPeNDAP|
|Batch Download PODAAC Data|[notebook](./notebooks/batch_download_podaac_data.md)|Instructions for HTTPS download from the PO.DAAC and NASA Earthdata||
| Data Access using R| [R script](./notebooks/cloudwebinar/data_access_R.R) | Simple starter script for direct S3 access using R from within aws| Direct cloud access|
| Data Access using Python| [Python script](./notebooks/cloudwebinar/cloud_direct_access_s3.py) | Simple starter script for direct S3 access using python from within aws| Direct cloud access|
| Direct S3 Access using Python| [Python script](./notebooks/s3/S3-Access.py) | Basic python script for S3 access and exploration in us-west-2| Direct cloud access|
| Obtaining subset using Harmony API| [Python script](./notebooks/cloudwebinar/harmony_subset.py) | Sample starter script for subsetting data using Harmony API leveraging the Harmony module| Harmony, ZARR,Subsetting|
