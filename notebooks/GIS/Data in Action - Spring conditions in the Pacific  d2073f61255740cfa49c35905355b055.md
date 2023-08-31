# Mapping Sea Surface Temperature Anomalies to Observe Potential El Niño Conditions

Author: Julie Sanchez, NASA JPL PO.DAAC

## Summary
- El Niño-Southern Oscillation (ENSO) is a climate pattern in the Pacific Ocean that has two phases: El Niño (warm/wet phase) and La Niña (cold/dry phase). ENSO has global impacts on wildfires, weather, and ecosystems. We have been experiencing La Niña conditions for the last 2 and a half years. The last El Niño event occurred in 2015/2016 and a weak El Niño event was also experienced during the winter of 2018/2019.

- This tutorial uses the SST anomaly variable derived from a MUR climatology dataset - MUR25-JPL-L4-GLOB-v04.2 (average between 2003 and 2014). This tutorial uses the PO.DAAC Downloader which downloads data to your local computer and uses QGIS to visulaize the data. The following tutorial visualizes the sea surface temperature anomalies (SSTA) over the Pacific Ocean for April 24, 2023.

1. Earthdata Login
An Earthdata Login account is required to access data, as well as discover restricted data, from the NASA Earthdata system. Thus, to access NASA data, you need Earthdata Login. Please visit https://urs.earthdata.nasa.gov to register and manage your Earthdata Login account. This account is free to create and only takes a moment to set up.
2. netrc File
You will need a .netrc file containing your NASA Earthdata Login credentials in order to execute the notebooks. A .netrc file can be created manually within text editor and saved to your home directory. For additional information see: Authentication for NASA Earthdata tutorial.
3. PO.DAAC Data Downloader
To download the data via command line, this tutorial uses PO.DAAC’s Data Downloader. The downloader can be installed using these instructions The Downloader is useful if you need to download PO.DAAC data once in a while or prefer to do it “on-demand”. The Downloader makes no assumptions about the last time run or what is new in the archive, it simply uses the provided requests and downloads all matching data.

# 2. How to use **GHRSST Sea Surface Temperature in** QGIS

## Open QGIS or download it from the following website:

- [https://www.qgis.org/en/site/forusers/download.html](https://www.qgis.org/en/site/forusers/download.html)

### Download the data:

- GHRSST: [https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2#](https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2#)
- World Boarders shape file: [https://thematicmapping.org/downloads/world_borders.php](https://thematicmapping.org/downloads/world_borders.php)

- Click on the Open Data Source Manager and add the World boarders shapefile. Make sure you click ‘Add’ on the bottom right and then ‘Close’.
    
    ![Screenshot 2023-06-05 at 6.32.39 PM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-05_at_6.32.39_PM.png)
    

![Screenshot 2023-06-06 at 9.29.29 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_9.29.29_AM.png)

- Next, add the MUR SSTA raster file by clicking the Open Data Source Manager, but this time choose the ‘Raster’ option. When you click ‘Add’ another window will open click on ‘Add Layers’ and then close the window. When you click ‘Add’ another window will open click on ‘sst_anomaly’, click on ‘Add Layers’, and then close the window.
    
    ![Screenshot 2023-06-06 at 9.31.52 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_9.31.52_AM.png)
    
    ![Screenshot 2023-06-06 at 9.58.10 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_9.58.10_AM.png)
    
- You now should have your layers like this:
    
    ![Screenshot 2023-06-06 at 9.34.33 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_9.34.33_AM.png)
    

- Click on ‘Settings’ and click on “Custom Projections..’

![Screenshot 2023-06-06 at 10.05.49 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.05.49_AM.png)

- Click on the green plus on the right hand corner, provide a name, and on the ‘Parameters’ section, copy and paste this formula: +proj=ortho +lat_0=10 +lon_0=-150 +x_0=0 +y_0=0 +a=6371000 +b=6371000 +units=m +no_defs
    
    ![Screenshot 2023-06-06 at 10.18.24 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.18.24_AM.png)
    

- click on the bottom right where it says ‘’EPSG:4326’ and change it to whatever you have named it.
    
    ![Screenshot 2023-06-06 at 10.18.55 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.18.55_AM.png)
    

- Right click on the sst_anomaly’ layer and click on ‘Properties’.
    
    ![Screenshot 2023-06-06 at 10.35.30 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.35.30_AM.png)
    

- Select ‘Single pseudocolor’ and change the max to -2 to 2. Add the classes and change the colors.
    
    ![Screenshot 2023-06-06 at 10.40.42 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.40.42_AM.png)
    

- Here is the final image that you can further change the background, add labels, etc: [https://docs.qgis.org/3.4/en/docs/training_manual/map_composer/map_composer.html](https://docs.qgis.org/3.4/en/docs/training_manual/map_composer/map_composer.html)

![Screenshot 2023-06-06 at 10.43.38 AM.png](Data%20in%20Action%20-%20Spring%20conditions%20in%20the%20Pacific%20%20d2073f61255740cfa49c35905355b055/Screenshot_2023-06-06_at_10.43.38_AM.png)