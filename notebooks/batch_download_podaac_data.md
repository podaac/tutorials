# Instructions for HTTPS download from the PO.DAAC and NASA Earthdata

## Set up your netrc file

[Follow these instructions on the Earthdata Wiki](https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+cURL+And+Wget?src=contextnavpagetreemode) to authenticate and store your URS cookies in a local file. You can batch download really efficiently this way, effectively "pre-authenticated" through your previous session.    


## Prepare a list of files to download

Now the only step that remains is to get a list of URLs to pass to *wget* or *curl* for downloading. There's a lot of ways to do this -- even more so for ECCO V4r4 data because the files/datasets follow well-structured naming conventions -- but we will rely on Earthdata Search to do this from the browser for the sake of simplicity.

**1. Find the collection/dataset of interest in Earthdata Search.**

Start from this [complete list of ECCO collections](https://search.earthdata.nasa.gov/portal/podaac-cloud/search?fpj=ECCO) in Earthdata Search (79 in total), and refine the results until you see your dataset of interest.
In this case we want [monthly sea surface height grids](https://search.earthdata.nasa.gov/portal/podaac-cloud/search/granules?p=C1990404799-POCLOUD) provided at 0.5-degree cell resolution on an interpolated latitude/longitude grid.

**2. Pick your collection, then click the green *Download All* button on the next page.**

Click the big green button identified by the red arrow/box in the screenshot below.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc1.png" width="70%" />

That will add all the granules in the collection to your "shopping cart" and then redirect you straight there and present you with the available options for customizing the data prior to download. We will ignore those because they're mostly in active development and because we want to download all data in the collection.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc2.png" width="70%" />
<center><i>The screenshot above shows the download customization interface (i.e. "shopping cart")</i></center>

**3. Click *Download Data* to get your list of download urls (bottom-left, another green button)**

The *Download Data* button takes you to one final page that provides the list of urls from which to download the files matching your search parameters and any customization options that you selected in the steps that followed. This page will be retained in your User History in case you need to return to it later.

<img src="https://raw.githubusercontent.com/podaac/ECCO/main/Data_Access/resources/edsc3.png" width="70%" />

There are several ways that you could get the list of urls into a text file that's accessible from Jupyter or your local shell. I clicked the save button in my browser and downloaded them as a text file to a subdirectory called *resources* inside this workspace. (You could also copy them into a new notebook cell and write them to a file like we did with the netrc file above.)

### Download files in a batch with GNU *Wget*

I find *wget* options to be convenient and easy to remember. There are only a handful that I use with any regularity.

The most important wget option for our purpose is set by the `-i` argument, which takes a path to the input text file containing our download urls. Another nice feature of wget is the ability to continue downloads where you left of during a previously-interuppted download session. That option is turned on by passing the `-c` argument.

Go ahead and create a *data/* directory to keep the downloaded files, and then start the downloads into that location by including the `-P` argument:

```sh
mkdir -p data

wget --no-verbose \
     --no-clobber \
     --continue \
     -i 5237392644-download.txt -P data/
```
