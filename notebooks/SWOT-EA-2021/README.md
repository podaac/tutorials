# SWOT-EA-2021
This subdirectory contains content developed by the PO.DAAC and presented at the SWOT Early Adopters workshop in March 2021.

<p align="center">
<img src="browse.png" width="75%" border="1px" />
<br>
<i>End result of the procedure demonstrated during the SWOT EA Workshop, part 1</i></p>

**Recommended use:** Build a Python environment from in the [*environment.yml*](environment.yml) file. It includes all Python + Jupyter dependencies. Full instructions given below in *Requirements*.

## <u>Part 1 - Co-locate satellite and in-situ data for cross-validation</u>

[*Colocate_satellite_insitu_ocean.ipynb*](Colocate_satellite_insitu_ocean.ipynb)

### What?

  As a coastal applications researcher, I would like to co-locate in-situ measurements and satellite data near the European coast for cross-validation of data or model validation, during the winter of 2019.

### How?

* Search Earthdata Cloud satellite data by point-based coordinates (CMR API)
* Extract satellite data at the in-situ location for direct comparison (Harmony API)
* Download locally (from the cloud archive)
* Plot time series comparing the in-situ and satellite data at in-situ location(s)

## <u>Part 2 - Explore coastal processes with satellite data in the cloud</u>

[*Estuary_explore_incloud_zarr.ipynb*](Estuary_explore_incloud_zarr.ipynb) -- *This notebook was developed to be executed in the AWS environment since it leveraged cloud-optimized data formats.*

### What?

  As a coastal researcher, I want to monitor terrestrial freshwater river discharge trends, seasonally and inter-annually, to assess impacts on coastal waters and ecosystems in the Amazon River estuary.

### How?

* Search for LWE (GRACE/GRACE-FO) and river discharge data (MEaSUREs Pre-SWOT)
* Access LWE dataset in Zarr format from Earthdata Cloud (AWS)
* Access river discharge dataset from PODAAC on prem data pool
* Subset both, plot and compare coincident data.

## Requirements

### Earthdata Login

You'll be prompted for your NASA Earthdata login credentials (username/password) at the beginning of each notebook. See here for more information about how to sign up for an Earthdata account:

    https://earthdata.nasa.gov/

### Python 3 environment

The [*environment.yml*](environment.yml) file in this directory should produce an environment that will run both ipynbs (inside AWS and/or on your local machine) from start to finish without any modifications.

1. Clone this repository, and then *cd* into the directory:

```shell
git clone https://github.com/podaac/tutorials.git && cd tutorials/notebooks/SWOT-EA-2021
```

2. Build a new conda environment from the provided [*environment.yml*](environment.yml) provided in the repo:

```shell
conda env create --file=environment.yml
```

3. Activate the environment and start jupyter notebook:

```shell
conda activate swotea
jupyter notebook
```

(You will need to modify this last command if you change the name of the environment in the first line of the YAML.)
