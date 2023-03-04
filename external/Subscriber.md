# Data Subscriber: Continual, Scripted Access to PODAAC data

The PO.DAAC Data subscriber is a python-based tool for continuously downloading data from the PO.DAAC archive. Use this script if you want to constantly download the newest data from PO.DAAC as it comes in.

For installation and dependency information, please see the [top-level README](README.md).

```
$> podaac-data-subscriber -h
usage: PO.DAAC data subscriber [-h] -c COLLECTION -d OUTPUTDIRECTORY [-f] [-sd STARTDATE] [-ed ENDDATE] [-b BBOX] [-dc] [-dydoy] [-dymd] [-dy] [--offset OFFSET] [-m MINUTES] [-e EXTENSIONS] [--process PROCESS_CMD] [--version] [--verbose] [-p PROVIDER]

optional arguments:
  -h, --help            show this help message and exit
  -c COLLECTION, --collection-shortname COLLECTION
                        The collection shortname for which you want to retrieve data.
  -d OUTPUTDIRECTORY, --data-dir OUTPUTDIRECTORY
                        The directory where data products will be downloaded.
  -f, --force           Flag to force downloading files that are listed in CMR query, even if the file exists and checksum matches
  -sd STARTDATE, --start-date STARTDATE
                        The ISO date time before which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z
  -ed ENDDATE, --end-date ENDDATE
                        The ISO date time after which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z
  -b BBOX, --bounds BBOX
                        The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b="-180,-90,180,90" syntax when calling from the command line. Default: "-180,-90,180,90".
  -dc                   Flag to use cycle number for directory where data products will be downloaded.
  -dydoy                Flag to use start time (Year/DOY) of downloaded data for directory where data products will be downloaded.
  -dymd                 Flag to use start time (Year/Month/Day) of downloaded data for directory where data products will be downloaded.
  -dy                   Flag to use start time (Year) of downloaded data for directory where data products will be downloaded.
  --offset OFFSET       Flag used to shift timestamp. Units are in hours, e.g. 10 or -10.
  -m MINUTES, --minutes MINUTES
                        How far back in time, in minutes, should the script look for data. If running this script as a cron, this value should be equal to or greater than how often your cron runs (default: 60 minutes).
  -e EXTENSIONS, --extensions EXTENSIONS
                        The extensions of products to download. Default is [.nc, .h5, .zip]
  --process PROCESS_CMD
                        Processing command to run on each downloaded file (e.g., compression). Can be specified multiple times.
  --version             Display script version information and exit.
  --verbose             Verbose mode.
  -p PROVIDER, --provider PROVIDER
                        Specify a provider for collection search. Default is POCLOUD.
```

## Run the Script

Usage:
```
usage: podaac_data_subscriber.py [-h] -c COLLECTION -d OUTPUTDIRECTORY [-f] [-sd STARTDATE] [-ed ENDDATE] [-b BBOX] [-dc] [-dydoy] [-dymd] [-dy] [--offset OFFSET] [-m MINUTES] [-e EXTENSIONS] [--version] [--verbose] [-p PROVIDER]
```

To run the script, the following parameters are required:

```
-c COLLECTION, --collection-shortname COLLECTION
                        The collection shortname for which you want to retrieve data.
-d OUTPUTDIRECTORY, --data-dir OUTPUTDIRECTORY
                        The directory where data products will be downloaded.
```

And one of

```
-sd STARTDATE, --start-date STARTDATE
                      The ISO date time before which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z
-ed ENDDATE, --end-date ENDDATE
                      The ISO date time after which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z
-m MINUTES, --minutes MINUTES
                      How far back in time, in minutes, should the script look for data. If running this script as a cron, this value should be equal to or greater than how often your cron runs.                    
```


`COLLECTION` is collection shortname of interest. This can be found from the PO.DAAC Portal, CMR, or earthdata search. Please see the included `Finding_shortname.pdf` document on how to find a collection shortname.

`OUTPUTDIRECTORY` is the directory in which files will be downloaded. It's customary to set this to a data directory and include the collection shortname as part of the path so if you run multiple subscribers, the data are not dumped into the same directory.

One last required item is a time entry, one of `--start-date`, `--end-date`, or `--minutes` must be specified. This is done so that a time is explicitly requested, and fewer assumptions are made about how the users is running the subscriber.

The Script will login to CMR and the PO.DAAC Archive using a **netrc** file. See Note 1 for more information on setting this up.

Every time the script runs successfully (that is, no errors), a `.update__<collectionname>` file is created in your download directory with the last run timestamp. This timestamp will be used the next time the script is run. It will look for data between the timestamp in that file and the current time to determine new files to download.

## Note: CMR times
There are numerous 'times' available to query on in CMR. For the default subscriber, we look at the 'created at' field, which will look for when a granule file was ingested into the archive. This means as PO.DAAC gets data, your subscriber will also get data, regardless of the time range within the granule itself.

## Note: netrc file
The netrc used within the script  will allow Python scripts to log into any Earthdata Login without being prompted for
credentials every time you run. The netrc file should be placed in your HOME directory.
To find the location of your HOME directory

On UNIX you can use
```
echo $HOME
```
On Windows you can use
```
echo %HOMEDRIVE%%HOMEPATH%
```

The output location from the command above should be the location of the `.netrc` (`_netrc` on Windows) file.

The format of the `netrc` file is as follows:

```
machine urs.earthdata.nasa.gov
    login <your username>
    password <your password>
```
for example:

```
machine urs.earthdata.nasa.gov
    login podaacUser
    password podaacIsAwesome
```

**If the script cannot find the netrc file, you will be prompted to enter the username and password and the script wont be able to generate the CMR token**


## Advanced Usage

### Request data from another DAAC...

Use the 'provider' flag to point at a non-PO.DAAC provider. Be aware, the default data types (--extensions) may need to be specified if the desired data are not in the defaults.

```
podaac-data-subscriber -c SENTINEL-1A_SLC -d myData  -p ASF -sd 2014-06-01T00:46:02Z
```

### Logging

For error troubleshooting, one can set an environment variable to gain more insight into errors:

```
export PODAAC_LOGLEVEL=DEBUG
```

And then run the script. This should give you more verbose output on URL requests to CMR, tokens, etc.

### Controlling output directories

The subscriber allows the placement of downloaded files into one of several directory structures based on the flags used to run the subscriber.

* -d - required, specifies the directory to which data is downloaded. If this is the only flag specified, all files will be downloaded to this single directory.
* -dc - optional, if 'cycle' information exists in the product metadata, download it to the data directory and use a relative c<CYCLE> path to store granules. The relative path is 0 padded to 4 total digits (e.g. c0001)
* -dydoy - optional, relative paths use the start time of a granule to layout data in a YEAR/DAY-OF-YEAR path
* -dymd  - optional, relative paths use the start time of a granule to layout data in a YEAR/MONTH/DAY path

### Subscriber behavior when a file already exists

By default, when the subscriber is about to download a file, it first:
- Checks if the file already exists in the target location
- Creates a checksum for the file and sees if it matches the checksum for that file in CMR

If the file already exists AND the checksum matches, the subscriber will skip downloading that file.

This can drastically reduce the time for the subscriber to complete. Also, since the checksum is verified, files will still be re-downloaded if for some reason the file has changed (or the file already on disk is corrupted).

You can override this default behavior - forcing the subscriber to always download matching files, by using --force/-f.

```
podaac-data-subscriber -c SENTINEL-1A_SLC -d myData -f
```

### Running as a Cron job

To automatically run and update a local file system with data files from a collection, one can use a syntax like the following:

```
10 * * * * podaac-data-subscriber -c VIIRS_N20-OSPO-L2P-v2.61 -d /path/to/data/VIIRS_N20-OSPO-L2P-v2.61 -e .nc -e .h5 -m 60 -b="-180,-90,180,90" --verbose >> ~/.subscriber.log

```

This will run every hour at ten minutes passed, and output will be appended to a local file called ~/.subscriber.log

### Setting a bounding rectangle for filtering results

If you're interested in a specific region, you can set the bounds parameter on your request to filter data that passes through a certain area. This is useful in particular for non-global datasets (such as swath datasets) with non-global coverage per file.

***Note: This does not subset the data, it just uses file metadata to see if any part of the datafile passes through your region. This will download the entire file, including data outside of the region specified.***

```
-b BBOX, --bounds BBOX
                      The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b="-180,-90,180,90" syntax when calling from
                      the command line. Default: "-180,-90,180,90\.

```
An example of the -b usage:

```
podaac-data-subscriber -c VIIRS_N20-OSPO-L2P-v2.61 -d ./data -b="-180,-90,180,90"
```

### Setting extensions

Some collections have many files. To download a specific set of files, you can set the extensions on which downloads are filtered. By default, ".nc", ".h5", and ".zip" files are downloaded by default.

```
-e EXTENSIONS, --extensions EXTENSIONS
                       The extensions of products to download. Default is [.nc, .h5, .zip]
```

An example of the -e usage- note the -e option is additive:
```
podaac-data-subscriber -c VIIRS_N20-OSPO-L2P-v2.61 -d ./data -e .nc -e .h5
```
### run a post download process

Using the `--process` option, you can run a simple command agaisnt the "just" downloaded file. This will take the format of "<command> <path/to/file>". This means you can run a command like `--process gzip` to gzip all downloaded files. We do not support more advanced processes at this time (piping, running a process on a directory, etc).


### In need of Help?
The PO.DAAC User Services Office is the primary point of contact for answering your questions concerning data and information held by the PO.DAAC. User Services staff members are knowledgeable about both the data ordering system and the data products themselves. We answer questions about data, route requests to other DAACs, and direct questions we cannot answer to the appropriate information source.

Please contact us via email at podaac@podaac.jpl.nasa.gov
