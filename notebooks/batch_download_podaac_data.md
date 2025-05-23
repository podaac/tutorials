# Instructions for HTTPS download from the PO.DAAC and NASA Earthdata

## Set up your netrc file

[Follow these instructions on the Earthdata Wiki](https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+cURL+And+Wget?src=contextnavpagetreemode) to authenticate and store your URS cookies in a local file. You can batch download really efficiently this way, effectively "pre-authenticated" through your previous session.    


## Prepare a list of files to download

Now the only step that remains is to get a list of URLs to pass to *wget* or *curl* for downloading. There's a lot of ways to do this but here we will rely on Earthdata Search.

**1. Find the collection/dataset of interest in Earthdata Search.**

Start by searching for your collection of interest. Here we are providing an ECCO example from this [complete list of ECCO collections](https://search.earthdata.nasa.gov/portal/podaac-cloud/search?fpj=ECCO) in Earthdata Search (79 in total), and refine the results until we see the dataset of interest.
In this example we want [monthly sea surface height grids](https://search.earthdata.nasa.gov/search/granules?p=C1990404799-POCLOUD) provided at 0.5-degree cell resolution on an interpolated latitude/longitude grid.

**2. Pick your collection, then click the green *Download All* button on the next page.**

Click the big green button identified by the red arrow/box in the screenshot below.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc1.png" width="70%" />

That will add all the granules in the collection to your "shopping cart" and then redirect you straight there and present you with the available options for customizing the data prior to download. We will ignore those because they're mostly in active development and because we want to download all data in the collection.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc2.png" width="70%" />
<p><center><i>The screenshot above shows the download customization interface (i.e. "shopping cart")</i></center></p>

**3. Click *Download Data* to get your list of download urls (bottom-left, another green button)**

The *Download Data* button takes you to one final page that provides the list of urls from which to download the files matching your search parameters and any customization options that you selected in the steps that followed. This page will be retained in your User History in case you need to return to it later.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc3.png" width="70%" />

There are several ways that you could get the list of urls into a text file that's accessible from Jupyter or your local shell. Click the *Save* button to download the list of files to a text file. This will by default save it with a name like `5237392644-download.txt` (numbers will be different for each download job).

>*Note: Earthdata Search also provides a shell script for downloading this list of files, accessible from the "Download Script" tab.*

## Download files in a batch with GNU *Wget*

The key *wget* option for this purpose is specified using the `-i` argument -- it takes the path to the text file containing the download urls.

Another nice feature of wget is the capability to continue downloads started during a previous session if they were interrupted. Pass `-c` to enable.

Make a *data/* directory, then run wget and give its path to the `-P` argument to download the files into that directory:

```sh
mkdir data

wget --no-verbose \
     --no-clobber \
     --continue \
     -i 5237392644-download.txt -P data/
```
