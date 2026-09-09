"""
Some ground level functions
"""

import requests
from pprint import pprint
CMR_OPS = 'https://cmr.earthdata.nasa.gov/search'
collection_url = 'https://cmr.earthdata.nasa.gov/search/collections'
var_url = "https://cmr.earthdata.nasa.gov/search/variables"

def find_dataset(provider='podaac',
                 keywords=['swot','level-2']):
    """
    Find a list of collections/datasets that match all the keywords from the keywords list.
    
    
    """
    import pandas as pd

    if 'podaac' in provider.lower().replace('.',''):
        provider='POCLOUD'
        
    response = requests.get(collection_url,params={'cloud_hosted': 'True',
                                        'has_granules': 'True',
                                        'provider': provider,
                                        'page_size':2000,},
                                headers={'Accept': 'application/json', } )
    
    collections = response.json()['feed']['entry']
    
    entries={}
    entries['short_name']=[]
    entries['long_name']=[]
    entries['concept_id']=[]
    
    for collection in collections:
        
        title="%s %s %s"%(collection["short_name"],collection["dataset_id"][:97],collection["id"])
        match=1
        for kw in keywords:
            match *= kw.lower() in title.lower()
            
        if match==1:
            entries['short_name'].append(collection["short_name"])
            entries['concept_id'].append(collection["id"])
            entries['long_name'].append(collection["dataset_id"])
    
    
    return pd.DataFrame(entries)

def direct_s3(provider='podaac'):
    import requests,s3fs
    s3_cred_endpoint = {
        'podaac':'https://archive.podaac.earthdata.nasa.gov/s3credentials',
        'lpdaac':'https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials'}

    temp_creds_url = s3_cred_endpoint[provider]
    creds = requests.get(temp_creds_url).json()
    s3 = s3fs.S3FileSystem(anon=False,
                           key=creds['accessKeyId'],
                           secret=creds['secretAccessKey'], 
                           token=creds['sessionToken'])
    return s3
