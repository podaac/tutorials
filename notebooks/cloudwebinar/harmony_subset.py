#!/usr/bin/env python3


# This script shows a simple way to create a subset of ECCO data using Harmony API.
## Access ECCO Data using Harmony API
## https://harmony.earthdata.nasa.gov/ 
## Python module for Harmony API can be installed from https://github.com/nasa/harmony


#Other modules needed
#pip3 install helper
#pip3 install progressbar
#pip3 install python-dotenv

import helper
import netrc
import datetime as dt
from harmony import BBox, Client, Collection, LinkType, Request, s3_components, Environment


###################
def harmony_client_login_auth(endpoint):
    """
    Set up the request library so that it authenticates against the given Earthdata Login
    endpoint.  This looks in the .netrc file first and if no credentials are found, it prompts for them.

    Valid endpoints include:
        urs.earthdata.nasa.gov - Earthdata Login production
    """
    try:
        username, _, password = netrc.netrc().authenticators(endpoint)
    except (FileNotFoundError, TypeError):
        # FileNotFound = There's no .netrc file
        # TypeError = The endpoint isn't in the netrc file, causing the above to try unpacking None
        print("There's no .netrc file or the The endpoint isn't in the netrc file")
    return Client(auth=(username, password))
###################
## Harmomny subset configurations
edl="urs.earthdata.nasa.gov"
collection=Collection(id='C1990404791-POCLOUD')

harmony_client=harmony_client_login_auth(edl)

request = Request(
    collection=collection,
    temporal={
        'start': dt.datetime(2010, 10, 1),
        'stop': dt.datetime(2010, 12, 30)
    },
    format="application/x-zarr"
)

## Submitting the subset request and tracking results

request.is_valid()
job_id = harmony_client.submit(request)
print(harmony_client.status(job_id))
print(harmony_client.result_json(job_id, show_progress=True))

urls = harmony_client.result_urls(job_id)


results = harmony_client.result_urls(job_id,link_type=LinkType.s3)
print(results)
creds = harmony_client.aws_credentials()

import boto3

## Obtaining the subsetted data
s3 = boto3.client('s3', **creds)
for url in results:
    bucket, obj, fn = s3_components(url)
    with open(fn, 'wb') as f:
        s3.download_fileobj(bucket, obj, f)


