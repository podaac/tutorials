# Harmony EOSS L2SS API Tutorial

## Before you start
Before you beginning this tutorial, make sure you have an account in the Earthdata Login UAT or Production environment, which 
will be used for this notebook by visiting [https://uat.urs.earthdata.nasa.gov](https://uat.urs.earthdata.nasa.gov).
These accounts, as all Earthdata Login accounts, are free to create and only take a moment to set up.

## Set Up Authentication

We need some boilerplate up front to log in to Earthdata Login.  The function below will allow Python
scripts to log into any Earthdata Login application programmatically.  To avoid being prompted for
credentials every time you run and also allow clients such as curl to log in, you can add the following
to a `.netrc` (`_netrc` on Windows) file in your home directory:

```
machine uat.urs.earthdata.nasa.gov
    login <your username>
    password <your password>
    
machine urs.earthdata.nasa.gov
    login <your username>
    password <your password>
```

Make sure that this file is only readable by the current user or you will receive an error stating
"netrc access too permissive."

`$ chmod 0600 ~/.netrc` 



```python
from urllib import request
from http.cookiejar import CookieJar
import getpass
import netrc
import json
import requests
import sys
import shutil
import xarray as xa



def setup_earthdata_login_auth(endpoint):
    """
    Set up the request library so that it authenticates against the given Earthdata Login
    endpoint and is able to track cookies between requests.  This looks in the .netrc file 
    first and if no credentials are found, it prompts for them.

    Valid endpoints include:
        uat.urs.earthdata.nasa.gov - Earthdata Login UAT (Harmony's current default)
        urs.earthdata.nasa.gov - Earthdata Login production
    """
    try:
        username, _, password = netrc.netrc().authenticators(endpoint)
    except (FileNotFoundError, TypeError):
        # FileNotFound = There's no .netrc file
        # TypeError = The endpoint isn't in the netrc file, causing the above to try unpacking None
        print('Please provide your Earthdata Login credentials to allow data access')
        print('Your credentials will only be passed to %s and will not be exposed in Jupyter' % (endpoint))
        username = input('Username:')
        password = getpass.getpass()

    manager = request.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, endpoint, username, password)
    auth = request.HTTPBasicAuthHandler(manager)

    jar = CookieJar()
    processor = request.HTTPCookieProcessor(jar)
    opener = request.build_opener(auth, processor)
    request.install_opener(opener)


# GET TOKEN FROM CMR 
def get_token( url: str,client_id: str, user_ip: str,endpoint: str) -> str:
    try:
        token: str = ''
        username, _, password = netrc.netrc().authenticators(endpoint)
        xml: str = """<?xml version='1.0' encoding='utf-8'?>
        <token><username>{}</username><password>{}</password><client_id>{}</client_id>
        <user_ip_address>{}</user_ip_address></token>""".format(username, password, client_id, user_ip)
        headers: Dict = {'Content-Type': 'application/xml','Accept': 'application/json'}
        resp = requests.post(url, headers=headers, data=xml)
        
        response_content: Dict = json.loads(resp.content)
        token = response_content['token']['id']
    except:
        print("Error getting the token - check user name and password", sys.exc_info()[0])
    return token
```

### Find a granule for subsetting

Below we call out a specific granule (G1226018995-POCUMULUS) on which we will use the podaac L2 subsetter. Finding this information would complicate the tutorial- but po.daac has a tutorial available for using the CMR API to find collections and granules of interest. Please see the following tutorial for that information:

PODAAC_CMR.ipynb



```python
collection = 'C1940473819-POCLOUD'
variable = 'sea_surface_temperature'
lat_var = 'lat'
lon_var = 'lon'
venue = 'prod'
```


```python
# Defaults
cmr_root = 'cmr.earthdata.nasa.gov'
harmony_root = 'https://harmony.earthdata.nasa.gov'
edl_root = 'urs.earthdata.nasa.gov'
```


```python
if venue == 'uat':
    cmr_root = 'cmr.uat.earthdata.nasa.gov'
    harmony_root = 'https://harmony.uat.earthdata.nasa.gov'
    edl_root = 'uat.urs.earthdata.nasa.gov'

print ("Environments: ")
print ("\t" + cmr_root)
print ("\t" + harmony_root)
print ("\t" + edl_root)
```

    Environments: 
    	cmr.earthdata.nasa.gov
    	https://harmony.earthdata.nasa.gov
    	urs.earthdata.nasa.gov


Now call the above function to set up Earthdata Login for subsequent requests


```python
setup_earthdata_login_auth(edl_root)
token_url="https://"+cmr_root+"/legacy-services/rest/tokens"
token=get_token(token_url,'jupyter', '127.0.0.1',edl_root)
```

##  Subset of a PO.DAAC Granule

We can now build onto the root URL in order to actually perform a transformation.  The first transformation is a subset of a selected granule.  _At this time, this requires discovering the granule id from CMR_.  That information can then be appended to the root URL and used to call Harmony with the help of the `request` library.

Above we show how to find a granule id for processing.

**Notes:**
  The L2 subsetter current streams the data back to the user, and does not stage data in S3 for redirects. This is functionality we will be adding over time.
  It doesn't work with URS backed files, which is coming in the next few weeks
  it only works on the show dataset, but 
    


```python
cmr_url = "https://"+cmr_root+"/search/granules.umm_json?collection_concept_id="+collection+"&bounding_box=-90,-45.75,90,-45&token="+token
response = requests.get(cmr_url)

gid=response.json()['items'][0]['meta']['concept-id']
print(response.json()['items'][0])
print(gid)



```

    {'meta': {'concept-type': 'granule', 'concept-id': 'G1966151265-POCLOUD', 'revision-id': 1, 'native-id': '20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0', 'provider-id': 'POCLOUD', 'format': 'application/vnd.nasa.cmr.umm+json', 'revision-date': '2020-11-12T12:09:42.586Z'}, 'umm': {'TemporalExtent': {'RangeDateTime': {'EndingDateTime': '2002-07-04T00:29:59.000Z', 'BeginningDateTime': '2002-07-04T00:25:01.000Z'}}, 'MetadataSpecification': {'URL': 'https://cdn.earthdata.nasa.gov/umm/granule/v1.6.2', 'Name': 'UMM-G', 'Version': '1.6.2'}, 'GranuleUR': '20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0', 'ProviderDates': [{'Type': 'Insert', 'Date': '2020-11-12T12:09:21.073Z'}, {'Type': 'Update', 'Date': '2020-11-12T12:09:21.073Z'}], 'SpatialExtent': {'HorizontalSpatialDomain': {'Geometry': {'BoundingRectangles': [{'WestBoundingCoordinate': -17.698, 'SouthBoundingCoordinate': -62.406, 'EastBoundingCoordinate': 24.515, 'NorthBoundingCoordinate': -40.386}]}}}, 'DataGranule': {'ArchiveAndDistributionInformation': [{'SizeUnit': 'MB', 'Size': 26.490304946899414, 'Checksum': {'Value': '14936c086c7b8ddbc9dcf45cbf0bf89d', 'Algorithm': 'MD5'}, 'SizeInBytes': 27777098, 'Name': '20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc'}, {'SizeUnit': 'MB', 'Size': 9.34600830078125e-05, 'Checksum': {'Value': 'aeacc9d31befa540706e363fd6b76ea3', 'Algorithm': 'MD5'}, 'SizeInBytes': 98, 'Name': '20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc.md5'}], 'DayNightFlag': 'Unspecified', 'ProductionDateTime': '2020-07-27T16:25:20.000Z'}, 'CollectionReference': {'Version': '2019.0', 'ShortName': 'MODIS_A-JPL-L2P-v2019.0'}, 'RelatedUrls': [{'URL': 'https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-public/MODIS_A-JPL-L2P-v2019.0/20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc.md5', 'Description': 'Download 20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc.md5', 'Type': 'EXTENDED METADATA'}, {'URL': 'https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MODIS_A-JPL-L2P-v2019.0/20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc', 'Description': 'Download 20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.nc', 'Type': 'GET DATA'}, {'URL': 'https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-public/MODIS_A-JPL-L2P-v2019.0/20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.cmr.json', 'Description': 'Download 20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0.cmr.json', 'Type': 'EXTENDED METADATA'}, {'URL': 'https://archive.podaac.earthdata.nasa.gov/s3credentials', 'Description': 'api endpoint to retrieve temporary credentials valid for same-region direct s3 access', 'Type': 'VIEW RELATED INFORMATION'}, {'URL': 'https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/GHRSST%20Level%202P%20Global%20Sea%20Surface%20Skin%20Temperature%20from%20the%20Moderate%20Resolution%20Imaging%20Spectroradiometer%20(MODIS)%20on%20the%20NASA%20Aqua%20satellite%20(GDS2)/granules/20020704002506-JPL-L2P_GHRSST-SSTskin-MODIS_A-N-v02.0-fv01.0', 'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA', 'Description': 'OPeNDAP request URL'}]}}
    G1966151265-POCLOUD



```python
bboxSubsetConfig = {
    'collection_id': collection,
    'ogc-api-coverages_version': '1.0.0',
    'variable': 'all',
    'granuleid': gid,
    'lat': '(-45.75:45)',
    'lon': '(-90:90)'
}
bbox_url = harmony_root+'/{collection_id}/ogc-api-coverages/{ogc-api-coverages_version}/collections/{variable}/coverage/rangeset?granuleid={granuleid}&subset=lat{lat}&subset=lon{lon}'.format(**bboxSubsetConfig)
print('Request URL', bbox_url)

```

    Request URL https://harmony.earthdata.nasa.gov/C1940473819-POCLOUD/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset?granuleid=G1966151265-POCLOUD&subset=lat(-45.75:45)&subset=lon(-90:90)



```python
with request.urlopen(bbox_url) as response, open('ogc_temp.nc', 'wb') as out_file:
    print('Content Size:', response.headers['Content-length'])
    shutil.copyfileobj(response, out_file)
    print("Downloaded request to ogc_temp.nc")
```

    Content Size: 19618245
    Downloaded request to ogc_temp.nc



```python
ds = xa.open_dataset('ogc_temp.nc')
ds
```




<div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
<defs>
<symbol id="icon-database" viewBox="0 0 32 32">
<path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
<path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
<path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
</symbol>
<symbol id="icon-file-text2" viewBox="0 0 32 32">
<path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
<path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
</symbol>
</defs>
</svg>
<style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
 *
 */

:root {
  --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
  --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
  --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
  --xr-border-color: var(--jp-border-color2, #e0e0e0);
  --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
  --xr-background-color: var(--jp-layout-color0, white);
  --xr-background-color-row-even: var(--jp-layout-color1, white);
  --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
}

html[theme=dark],
body.vscode-dark {
  --xr-font-color0: rgba(255, 255, 255, 1);
  --xr-font-color2: rgba(255, 255, 255, 0.54);
  --xr-font-color3: rgba(255, 255, 255, 0.38);
  --xr-border-color: #1F1F1F;
  --xr-disabled-color: #515151;
  --xr-background-color: #111111;
  --xr-background-color-row-even: #111111;
  --xr-background-color-row-odd: #313131;
}

.xr-wrap {
  display: block;
  min-width: 300px;
  max-width: 700px;
}

.xr-text-repr-fallback {
  /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
  display: none;
}

.xr-header {
  padding-top: 6px;
  padding-bottom: 6px;
  margin-bottom: 4px;
  border-bottom: solid 1px var(--xr-border-color);
}

.xr-header > div,
.xr-header > ul {
  display: inline;
  margin-top: 0;
  margin-bottom: 0;
}

.xr-obj-type,
.xr-array-name {
  margin-left: 2px;
  margin-right: 10px;
}

.xr-obj-type {
  color: var(--xr-font-color2);
}

.xr-sections {
  padding-left: 0 !important;
  display: grid;
  grid-template-columns: 150px auto auto 1fr 20px 20px;
}

.xr-section-item {
  display: contents;
}

.xr-section-item input {
  display: none;
}

.xr-section-item input + label {
  color: var(--xr-disabled-color);
}

.xr-section-item input:enabled + label {
  cursor: pointer;
  color: var(--xr-font-color2);
}

.xr-section-item input:enabled + label:hover {
  color: var(--xr-font-color0);
}

.xr-section-summary {
  grid-column: 1;
  color: var(--xr-font-color2);
  font-weight: 500;
}

.xr-section-summary > span {
  display: inline-block;
  padding-left: 0.5em;
}

.xr-section-summary-in:disabled + label {
  color: var(--xr-font-color2);
}

.xr-section-summary-in + label:before {
  display: inline-block;
  content: '►';
  font-size: 11px;
  width: 15px;
  text-align: center;
}

.xr-section-summary-in:disabled + label:before {
  color: var(--xr-disabled-color);
}

.xr-section-summary-in:checked + label:before {
  content: '▼';
}

.xr-section-summary-in:checked + label > span {
  display: none;
}

.xr-section-summary,
.xr-section-inline-details {
  padding-top: 4px;
  padding-bottom: 4px;
}

.xr-section-inline-details {
  grid-column: 2 / -1;
}

.xr-section-details {
  display: none;
  grid-column: 1 / -1;
  margin-bottom: 5px;
}

.xr-section-summary-in:checked ~ .xr-section-details {
  display: contents;
}

.xr-array-wrap {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 20px auto;
}

.xr-array-wrap > label {
  grid-column: 1;
  vertical-align: top;
}

.xr-preview {
  color: var(--xr-font-color3);
}

.xr-array-preview,
.xr-array-data {
  padding: 0 5px !important;
  grid-column: 2;
}

.xr-array-data,
.xr-array-in:checked ~ .xr-array-preview {
  display: none;
}

.xr-array-in:checked ~ .xr-array-data,
.xr-array-preview {
  display: inline-block;
}

.xr-dim-list {
  display: inline-block !important;
  list-style: none;
  padding: 0 !important;
  margin: 0;
}

.xr-dim-list li {
  display: inline-block;
  padding: 0;
  margin: 0;
}

.xr-dim-list:before {
  content: '(';
}

.xr-dim-list:after {
  content: ')';
}

.xr-dim-list li:not(:last-child):after {
  content: ',';
  padding-right: 5px;
}

.xr-has-index {
  font-weight: bold;
}

.xr-var-list,
.xr-var-item {
  display: contents;
}

.xr-var-item > div,
.xr-var-item label,
.xr-var-item > .xr-var-name span {
  background-color: var(--xr-background-color-row-even);
  margin-bottom: 0;
}

.xr-var-item > .xr-var-name:hover span {
  padding-right: 5px;
}

.xr-var-list > li:nth-child(odd) > div,
.xr-var-list > li:nth-child(odd) > label,
.xr-var-list > li:nth-child(odd) > .xr-var-name span {
  background-color: var(--xr-background-color-row-odd);
}

.xr-var-name {
  grid-column: 1;
}

.xr-var-dims {
  grid-column: 2;
}

.xr-var-dtype {
  grid-column: 3;
  text-align: right;
  color: var(--xr-font-color2);
}

.xr-var-preview {
  grid-column: 4;
}

.xr-var-name,
.xr-var-dims,
.xr-var-dtype,
.xr-preview,
.xr-attrs dt {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 10px;
}

.xr-var-name:hover,
.xr-var-dims:hover,
.xr-var-dtype:hover,
.xr-attrs dt:hover {
  overflow: visible;
  width: auto;
  z-index: 1;
}

.xr-var-attrs,
.xr-var-data {
  display: none;
  background-color: var(--xr-background-color) !important;
  padding-bottom: 5px !important;
}

.xr-var-attrs-in:checked ~ .xr-var-attrs,
.xr-var-data-in:checked ~ .xr-var-data {
  display: block;
}

.xr-var-data > table {
  float: right;
}

.xr-var-name span,
.xr-var-data,
.xr-attrs {
  padding-left: 25px !important;
}

.xr-attrs,
.xr-var-attrs,
.xr-var-data {
  grid-column: 1 / -1;
}

dl.xr-attrs {
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 125px auto;
}

.xr-attrs dt, dd {
  padding: 0;
  margin: 0;
  float: left;
  padding-right: 10px;
  width: auto;
}

.xr-attrs dt {
  font-weight: normal;
  grid-column: 1;
}

.xr-attrs dt:hover span {
  display: inline-block;
  background: var(--xr-background-color);
  padding-right: 10px;
}

.xr-attrs dd {
  grid-column: 2;
  white-space: pre-wrap;
  word-break: break-all;
}

.xr-icon-database,
.xr-icon-file-text2 {
  display: inline-block;
  vertical-align: middle;
  width: 1em;
  height: 1.5em !important;
  stroke-width: 0;
  stroke: currentColor;
  fill: currentColor;
}
</style><pre class='xr-text-repr-fallback'>&lt;xarray.Dataset&gt;
Dimensions:                      (ni: 1354, nj: 656, time: 1)
Coordinates:
    lat                          (nj, ni) float32 ...
    lon                          (nj, ni) float32 ...
  * time                         (time) datetime64[ns] 2002-07-04T00:25:01
Dimensions without coordinates: ni, nj
Data variables:
    sea_surface_temperature      (time, nj, ni) float32 ...
    sst_dtime                    (time, nj, ni) timedelta64[ns] ...
    quality_level                (time, nj, ni) float32 ...
    sses_bias                    (time, nj, ni) float32 ...
    sses_standard_deviation      (time, nj, ni) float32 ...
    l2p_flags                    (time, nj, ni) int16 ...
    sea_surface_temperature_4um  (time, nj, ni) float32 ...
    quality_level_4um            (time, nj, ni) float32 ...
    sses_bias_4um                (time, nj, ni) float32 ...
    sses_standard_deviation_4um  (time, nj, ni) float32 ...
    wind_speed                   (time, nj, ni) float32 ...
    dt_analysis                  (time, nj, ni) float32 ...
Attributes:
    Conventions:                CF-1.7, ACDD-1.3
    title:                      MODIS Aqua L2P SST
    summary:                    Sea surface temperature retrievals produced a...
    references:                 GHRSST Data Processing Specification v2r5
    institution:                NASA/JPL/OBPG/RSMAS
    history:                    MODIS L2P created at JPL PO.DAAC\n2021-04-20 ...
    comment:                    L2P Core without DT analysis or other ancilla...
    license:                    GHRSST and PO.DAAC protocol allow data use as...
    id:                         MODIS_A-JPL-L2P-v2019.0
    naming_authority:           org.ghrsst
    product_version:            2019.0
    uuid:                       f6e1f61d-c4a4-4c17-8354-0c15e12d688b
    gds_version_id:             2.0
    netcdf_version_id:          4.1
    date_created:               20200727T162520Z
    file_quality_level:         3
    spatial_resolution:         1km
    start_time:                 20020704T002501Z
    time_coverage_start:        20020704T002501Z
    stop_time:                  20020704T002959Z
    time_coverage_end:          20020704T002959Z
    northernmost_latitude:      -40.3864
    southernmost_latitude:      -62.4058
    easternmost_longitude:      24.5151
    westernmost_longitude:      -17.6983
    source:                     MODIS sea surface temperature observations fo...
    platform:                   Aqua
    sensor:                     MODIS
    metadata_link:              http://podaac.jpl.nasa.gov/ws/metadata/datase...
    keywords:                   Oceans &gt; Ocean Temperature &gt; Sea Surface Temp...
    keywords_vocabulary:        NASA Global Change Master Directory (GCMD) Sc...
    standard_name_vocabulary:   NetCDF Climate and Forecast (CF) Metadata Con...
    geospatial_lat_units:       degrees_north
    geospatial_lat_resolution:  0.01
    geospatial_lon_units:       degrees_east
    geospatial_lon_resolution:  0.01
    acknowledgment:             The MODIS L2P sea surface temperature data ar...
    creator_name:               Ed Armstrong, JPL PO.DAAC
    creator_email:              edward.m.armstrong@jpl.nasa.gov
    creator_url:                http://podaac.jpl.nasa.gov
    project:                    Group for High Resolution Sea Surface Tempera...
    publisher_name:             The GHRSST Project Office
    publisher_url:              http://www.ghrsst.org
    publisher_email:            ghrsst-po@nceo.ac.uk
    processing_level:           L2P
    cdm_data_type:              swath
    startDirection:             Descending
    endDirection:               Descending
    day_night_flag:             Night</pre><div class='xr-wrap' hidden><div class='xr-header'><div class='xr-obj-type'>xarray.Dataset</div></div><ul class='xr-sections'><li class='xr-section-item'><input id='section-34e08a1c-bd5e-4aad-b4da-8137e695b065' class='xr-section-summary-in' type='checkbox' disabled ><label for='section-34e08a1c-bd5e-4aad-b4da-8137e695b065' class='xr-section-summary'  title='Expand/collapse section'>Dimensions:</label><div class='xr-section-inline-details'><ul class='xr-dim-list'><li><span>ni</span>: 1354</li><li><span>nj</span>: 656</li><li><span class='xr-has-index'>time</span>: 1</li></ul></div><div class='xr-section-details'></div></li><li class='xr-section-item'><input id='section-382b8159-54af-4fbf-a07e-e3f2015b303b' class='xr-section-summary-in' type='checkbox'  checked><label for='section-382b8159-54af-4fbf-a07e-e3f2015b303b' class='xr-section-summary' >Coordinates: <span>(3)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span>lat</span></div><div class='xr-var-dims'>(nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-ca1e8138-f4f6-4599-84fa-88b2baec6667' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-ca1e8138-f4f6-4599-84fa-88b2baec6667' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-8a8b5c49-909c-4074-86f7-1790f890bd10' class='xr-var-data-in' type='checkbox'><label for='data-8a8b5c49-909c-4074-86f7-1790f890bd10' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>latitude</dd><dt><span>standard_name :</span></dt><dd>latitude</dd><dt><span>units :</span></dt><dd>degrees_north</dd><dt><span>valid_min :</span></dt><dd>-90.0</dd><dt><span>valid_max :</span></dt><dd>90.0</dd><dt><span>comment :</span></dt><dd>geographical coordinates, WGS84 projection</dd><dt><span>coverage_content_type :</span></dt><dd>coordinate</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>lon</span></div><div class='xr-var-dims'>(nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-9b0ce198-b014-46ca-859b-e64cedaf3c43' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-9b0ce198-b014-46ca-859b-e64cedaf3c43' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-90b62baf-fd52-4471-96ff-8c8f105162ed' class='xr-var-data-in' type='checkbox'><label for='data-90b62baf-fd52-4471-96ff-8c8f105162ed' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>longitude</dd><dt><span>standard_name :</span></dt><dd>longitude</dd><dt><span>units :</span></dt><dd>degrees_east</dd><dt><span>valid_min :</span></dt><dd>-180.0</dd><dt><span>valid_max :</span></dt><dd>180.0</dd><dt><span>comment :</span></dt><dd>geographical coordinates, WGS84 projection</dd><dt><span>coverage_content_type :</span></dt><dd>coordinate</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2002-07-04T00:25:01</div><input id='attrs-6a9feb73-3a61-4020-b57c-049b8b621897' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-6a9feb73-3a61-4020-b57c-049b8b621897' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-ac6fae17-dc9e-4853-8b56-e2bf425108f1' class='xr-var-data-in' type='checkbox'><label for='data-ac6fae17-dc9e-4853-8b56-e2bf425108f1' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>reference time of sst file</dd><dt><span>standard_name :</span></dt><dd>time</dd><dt><span>comment :</span></dt><dd>time of first sensor observation</dd><dt><span>coverage_content_type :</span></dt><dd>coordinate</dd></dl></div><div class='xr-var-data'><pre>array([&#x27;2002-07-04T00:25:01.000000000&#x27;], dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-8a396ac4-3b1f-4292-ba52-2a2a1fc27ed7' class='xr-section-summary-in' type='checkbox'  checked><label for='section-8a396ac4-3b1f-4292-ba52-2a2a1fc27ed7' class='xr-section-summary' >Data variables: <span>(12)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span>sea_surface_temperature</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-25e5eb5d-a6bd-472e-9432-15bff117c3f8' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-25e5eb5d-a6bd-472e-9432-15bff117c3f8' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-fcb67375-416f-43cf-9f46-048c22ae5158' class='xr-var-data-in' type='checkbox'><label for='data-fcb67375-416f-43cf-9f46-048c22ae5158' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>sea surface temperature</dd><dt><span>standard_name :</span></dt><dd>sea_surface_skin_temperature</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-1000</dd><dt><span>valid_max :</span></dt><dd>10000</dd><dt><span>comment :</span></dt><dd>sea surface temperature from thermal IR (11 um) channels</dd><dt><span>source :</span></dt><dd>NASA and University of Miami</dd><dt><span>coverage_content_type :</span></dt><dd>physicalMeasurement</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sst_dtime</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>timedelta64[ns]</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-f33cc51b-d858-4e1e-b5dd-9642aa60de02' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-f33cc51b-d858-4e1e-b5dd-9642aa60de02' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-05cf4ed6-a15f-4cf4-9e56-07647f323bf2' class='xr-var-data-in' type='checkbox'><label for='data-05cf4ed6-a15f-4cf4-9e56-07647f323bf2' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>time difference from reference time</dd><dt><span>valid_min :</span></dt><dd>-32767</dd><dt><span>valid_max :</span></dt><dd>32767</dd><dt><span>comment :</span></dt><dd>time plus sst_dtime gives seconds after 00:00:00 UTC January 1, 1981</dd><dt><span>coverage_content_type :</span></dt><dd>referenceInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=timedelta64[ns]]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>quality_level</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-af13fb20-9c7f-40e0-aef2-ffa340d144c9' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-af13fb20-9c7f-40e0-aef2-ffa340d144c9' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-d9fcb603-c7fd-454b-81aa-cc340f508b7e' class='xr-var-data-in' type='checkbox'><label for='data-d9fcb603-c7fd-454b-81aa-cc340f508b7e' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>quality level of SST pixel</dd><dt><span>valid_min :</span></dt><dd>0</dd><dt><span>valid_max :</span></dt><dd>5</dd><dt><span>comment :</span></dt><dd>thermal IR SST proximity confidence value; signed byte array: WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>flag_values :</span></dt><dd>[0 1 2 3 4 5]</dd><dt><span>flag_meanings :</span></dt><dd>no_data bad_data worst_quality low_quality acceptable_quality best_quality</dd><dt><span>coverage_content_type :</span></dt><dd>qualityInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sses_bias</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-362adc21-2f1e-46ac-8750-a1a4e82fb9be' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-362adc21-2f1e-46ac-8750-a1a4e82fb9be' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-a8d35627-871b-4217-9c07-dd02d25a29ef' class='xr-var-data-in' type='checkbox'><label for='data-a8d35627-871b-4217-9c07-dd02d25a29ef' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>SSES bias error based on proximity confidence flags</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>thermal IR SST bias error; signed byte array: WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sses_standard_deviation</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-9992507b-8556-4403-a6f6-067e6b417d1d' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-9992507b-8556-4403-a6f6-067e6b417d1d' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-8305f69c-b3c9-4ce6-9432-521197de11c2' class='xr-var-data-in' type='checkbox'><label for='data-8305f69c-b3c9-4ce6-9432-521197de11c2' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>SSES standard deviation error based on proximity confidence flags</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>thermal IR SST standard deviation error; signed byte array: WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>l2p_flags</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>int16</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-650b3c13-703e-440f-bc4d-e0c001ba4973' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-650b3c13-703e-440f-bc4d-e0c001ba4973' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-645bb0a9-2d24-4e1b-89be-4b8ea782fa89' class='xr-var-data-in' type='checkbox'><label for='data-645bb0a9-2d24-4e1b-89be-4b8ea782fa89' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>L2P flags</dd><dt><span>valid_min :</span></dt><dd>0</dd><dt><span>valid_max :</span></dt><dd>16</dd><dt><span>comment :</span></dt><dd>These flags can be used to further filter data variables</dd><dt><span>flag_meanings :</span></dt><dd>microwave land ice lake river</dd><dt><span>flag_masks :</span></dt><dd>[ 1  2  4  8 16]</dd><dt><span>coverage_content_type :</span></dt><dd>qualityInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=int16]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sea_surface_temperature_4um</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-ff8c7096-591b-45ed-8f75-772b3fc11ece' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-ff8c7096-591b-45ed-8f75-772b3fc11ece' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-708d036c-cd3d-41ac-b3fb-e27025789960' class='xr-var-data-in' type='checkbox'><label for='data-708d036c-cd3d-41ac-b3fb-e27025789960' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>sea surface temperature</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-1000</dd><dt><span>valid_max :</span></dt><dd>10000</dd><dt><span>comment :</span></dt><dd>sea surface temperature from mid-IR (4 um) channels; non L2P core field</dd><dt><span>coverage_content_type :</span></dt><dd>physicalMeasurement</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>quality_level_4um</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-da3e6092-bb98-4634-b565-4a75d317a9fd' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-da3e6092-bb98-4634-b565-4a75d317a9fd' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-9fbd391c-3987-4ab0-a031-a8811c589269' class='xr-var-data-in' type='checkbox'><label for='data-9fbd391c-3987-4ab0-a031-a8811c589269' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>quality level of SST pixel</dd><dt><span>valid_min :</span></dt><dd>0</dd><dt><span>valid_max :</span></dt><dd>5</dd><dt><span>comment :</span></dt><dd>mid-IR SST proximity confidence value; non L2P core field; signed byte array:  WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>flag_values :</span></dt><dd>[0 1 2 3 4 5]</dd><dt><span>flag_meanings :</span></dt><dd>no_data bad_data worst_quality low_quality acceptable_quality best_quality</dd><dt><span>coverage_content_type :</span></dt><dd>qualityInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sses_bias_4um</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-5a952037-ce37-4c70-841d-124c25074374' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-5a952037-ce37-4c70-841d-124c25074374' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-48d64f47-c747-4523-a4f2-f4992639c2e2' class='xr-var-data-in' type='checkbox'><label for='data-48d64f47-c747-4523-a4f2-f4992639c2e2' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>SSES bias error based on proximity confidence flags</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>mid-IR SST bias error; non L2P core field; signed byte array:  WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>sses_standard_deviation_4um</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-55ca8581-939c-44b8-979b-12e745a3f895' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-55ca8581-939c-44b8-979b-12e745a3f895' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e30d386b-d6a1-45ca-a00e-34541827ee61' class='xr-var-data-in' type='checkbox'><label for='data-e30d386b-d6a1-45ca-a00e-34541827ee61' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>SSES standard deviation error based on proximity confidence flags</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>mid-IR SST standard deviation error; non L2P core field; signed byte array:  WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>wind_speed</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-cb983d64-f4fd-4d54-824e-048581a68d31' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-cb983d64-f4fd-4d54-824e-048581a68d31' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-6c3693f8-278a-493e-a41d-7dca23806ec0' class='xr-var-data-in' type='checkbox'><label for='data-6c3693f8-278a-493e-a41d-7dca23806ec0' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>10m wind speed</dd><dt><span>standard_name :</span></dt><dd>wind_speed</dd><dt><span>units :</span></dt><dd>m s-1</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>Wind at 10 meters above the sea surface</dd><dt><span>source :</span></dt><dd>TBD.  Placeholder.  Currently empty</dd><dt><span>grid_mapping :</span></dt><dd>TBD</dd><dt><span>time_offset :</span></dt><dd>2.0</dd><dt><span>height :</span></dt><dd>10 m</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>dt_analysis</span></div><div class='xr-var-dims'>(time, nj, ni)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-55fb083b-4c32-429f-b826-39026abafd6a' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-55fb083b-4c32-429f-b826-39026abafd6a' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-a57790ae-4b32-407d-8456-391ca05415b4' class='xr-var-data-in' type='checkbox'><label for='data-a57790ae-4b32-407d-8456-391ca05415b4' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>deviation from SST reference climatology</dd><dt><span>units :</span></dt><dd>kelvin</dd><dt><span>valid_min :</span></dt><dd>-127</dd><dt><span>valid_max :</span></dt><dd>127</dd><dt><span>comment :</span></dt><dd>TBD</dd><dt><span>source :</span></dt><dd>TBD. Placeholder.  Currently empty</dd><dt><span>coverage_content_type :</span></dt><dd>auxiliaryInformation</dd></dl></div><div class='xr-var-data'><pre>[888224 values with dtype=float32]</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-e2ca93ec-7623-4b7a-8432-7657f015459d' class='xr-section-summary-in' type='checkbox'  ><label for='section-e2ca93ec-7623-4b7a-8432-7657f015459d' class='xr-section-summary' >Attributes: <span>(49)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>Conventions :</span></dt><dd>CF-1.7, ACDD-1.3</dd><dt><span>title :</span></dt><dd>MODIS Aqua L2P SST</dd><dt><span>summary :</span></dt><dd>Sea surface temperature retrievals produced at the NASA OBPG for the MODIS Aqua sensor.  These have been reformatted to GHRSST GDS specifications by the JPL PO.DAAC</dd><dt><span>references :</span></dt><dd>GHRSST Data Processing Specification v2r5</dd><dt><span>institution :</span></dt><dd>NASA/JPL/OBPG/RSMAS</dd><dt><span>history :</span></dt><dd>MODIS L2P created at JPL PO.DAAC
2021-04-20 19:25:03.631835 podaac-subsetter v0.9.0 (bbox=[[-90.0, 90.0], [-45.75, 45.0]] cut=True)</dd><dt><span>comment :</span></dt><dd>L2P Core without DT analysis or other ancillary fields; Night, Start Node:Descending, End Node:Descending; WARNING Some applications are unable to properly handle signed byte values. If values are encountered &gt; 127, please subtract 256 from this reported value; Refined</dd><dt><span>license :</span></dt><dd>GHRSST and PO.DAAC protocol allow data use as free and open.</dd><dt><span>id :</span></dt><dd>MODIS_A-JPL-L2P-v2019.0</dd><dt><span>naming_authority :</span></dt><dd>org.ghrsst</dd><dt><span>product_version :</span></dt><dd>2019.0</dd><dt><span>uuid :</span></dt><dd>f6e1f61d-c4a4-4c17-8354-0c15e12d688b</dd><dt><span>gds_version_id :</span></dt><dd>2.0</dd><dt><span>netcdf_version_id :</span></dt><dd>4.1</dd><dt><span>date_created :</span></dt><dd>20200727T162520Z</dd><dt><span>file_quality_level :</span></dt><dd>3</dd><dt><span>spatial_resolution :</span></dt><dd>1km</dd><dt><span>start_time :</span></dt><dd>20020704T002501Z</dd><dt><span>time_coverage_start :</span></dt><dd>20020704T002501Z</dd><dt><span>stop_time :</span></dt><dd>20020704T002959Z</dd><dt><span>time_coverage_end :</span></dt><dd>20020704T002959Z</dd><dt><span>northernmost_latitude :</span></dt><dd>-40.3864</dd><dt><span>southernmost_latitude :</span></dt><dd>-62.4058</dd><dt><span>easternmost_longitude :</span></dt><dd>24.5151</dd><dt><span>westernmost_longitude :</span></dt><dd>-17.6983</dd><dt><span>source :</span></dt><dd>MODIS sea surface temperature observations for the OBPG</dd><dt><span>platform :</span></dt><dd>Aqua</dd><dt><span>sensor :</span></dt><dd>MODIS</dd><dt><span>metadata_link :</span></dt><dd>http://podaac.jpl.nasa.gov/ws/metadata/dataset/?format=iso&amp;shortName=MODIS_A-JPL-L2P-v2019.0</dd><dt><span>keywords :</span></dt><dd>Oceans &gt; Ocean Temperature &gt; Sea Surface Temperature</dd><dt><span>keywords_vocabulary :</span></dt><dd>NASA Global Change Master Directory (GCMD) Science Keywords</dd><dt><span>standard_name_vocabulary :</span></dt><dd>NetCDF Climate and Forecast (CF) Metadata Convention</dd><dt><span>geospatial_lat_units :</span></dt><dd>degrees_north</dd><dt><span>geospatial_lat_resolution :</span></dt><dd>0.01</dd><dt><span>geospatial_lon_units :</span></dt><dd>degrees_east</dd><dt><span>geospatial_lon_resolution :</span></dt><dd>0.01</dd><dt><span>acknowledgment :</span></dt><dd>The MODIS L2P sea surface temperature data are sponsored by NASA</dd><dt><span>creator_name :</span></dt><dd>Ed Armstrong, JPL PO.DAAC</dd><dt><span>creator_email :</span></dt><dd>edward.m.armstrong@jpl.nasa.gov</dd><dt><span>creator_url :</span></dt><dd>http://podaac.jpl.nasa.gov</dd><dt><span>project :</span></dt><dd>Group for High Resolution Sea Surface Temperature</dd><dt><span>publisher_name :</span></dt><dd>The GHRSST Project Office</dd><dt><span>publisher_url :</span></dt><dd>http://www.ghrsst.org</dd><dt><span>publisher_email :</span></dt><dd>ghrsst-po@nceo.ac.uk</dd><dt><span>processing_level :</span></dt><dd>L2P</dd><dt><span>cdm_data_type :</span></dt><dd>swath</dd><dt><span>startDirection :</span></dt><dd>Descending</dd><dt><span>endDirection :</span></dt><dd>Descending</dd><dt><span>day_night_flag :</span></dt><dd>Night</dd></dl></div></li></ul></div></div>




```python
ds[variable].plot()
```




    <matplotlib.collections.QuadMesh at 0x7fd2a8f8d340>




    
![png](Harmony%20L2%20Subsetter_files/Harmony%20L2%20Subsetter_15_1.png)
    


## Verify the subsetting worked

Bounds used were: 

  'lat': '(-45.75:45)',
  'lon': '(-90:90)'


```python
lat_max = ds[lat_var].max()
lat_min = ds[lat_var].min()

lon_min = ds[lon_var].min()
lon_max = ds[lon_var].max()

lon_min = (ds.lon.min() + 180) % 360 - 180
lon_max = (ds.lon.max() + 180) % 360 - 180

# print(lon_min)
# print(lon_max)
# print(lat_min)
# print(lat_max)

if lat_max <= 45 and lat_min >= -45.75:
    print("Successful Latitude subsetting")
else:
    assert False


if lon_max <= 90 and lon_min >= -90:
    print("Successful Longitude subsetting")
else:
    assert False
    
```

    Successful Latitude subsetting
    Successful Longitude subsetting



```python

```
