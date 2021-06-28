# PO.DAAC Tutorials

![N|Solid](https://podaac.jpl.nasa.gov/sites/default/files/image/custom_thumbs/podaac_logo.png)


A place to find cloud relevant tutorials on how to use PO.DAAC and Earthdata tools, services, and data.

Most tutorials in this repository take the form of python notebooks. [Jupyter](https://jupyter.org/) is a very popular version of python notebooks, and is used extensively by the PO.DAAC team.

| Notebook| Link | Summary | Services and Tools |
|----|-----| ----| ----|
|Amazon River Estuary Exploration|[notebook](./notebooks/AmazonRiver_Estuary_Exploration.ipynb)|Explore relationship between oceanography and hydrology data in the Amazon Estuary from the on-prem and Earthdata Cloud archives|CMR, OPeNDAP|
|MODIS L2P SST Datacube|[notebook](./notebooks/MODIS_L2P_SST_DataCube.ipynb)|How to create a gridded "Data Cube", essentially an ARD, from native Level 2P sea surface temperature (SST) data from MODIS Aqua|Harmony, GDAL NCO|
|HUC Feature Translation Service Examples|[notebook](./notebooks/HUC%20Feature%20Translation%20Service%20Examples.ipynb)||CMR, FTS|
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
