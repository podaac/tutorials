# Mapping Sea Surface Temperature Anomalies in QGIS

Author: Julie Sanchez, NASA JPL PO.DAAC

## Summary
- El Niño-Southern Oscillation (ENSO) is a climate pattern in the Pacific Ocean that has two phases: El Niño (warm/wet phase) and La Niña (cold/dry phase). ENSO has global impacts on wildfires, weather, and ecosystems. We have been experiencing La Niña conditions for the last 2 and a half years. The last El Niño event occurred in 2015/2016 and a weak El Niño event was also experienced during the winter of 2018/2019.

- This tutorial uses the SST anomaly variable derived from a MUR climatology dataset - MUR25-JPL-L4-GLOB-v04.2 (average between 2003 and 2014). This tutorial uses QGIS to visulaize the the sea surface temperature anomalies (SSTA) over the Pacific Ocean for April 24, 2023.

# Data needed for tutorial:
- Download QGIS if not already downloaded: [https://www.qgis.org/en/site/forusers/download.html](https://www.qgis.org/en/site/forusers/download.html)
- World Boarders shape file: [https://thematicmapping.org/downloads/world_borders.php](https://thematicmapping.org/downloads/world_borders.php)
- GHRSST data from April 24, 2023: [https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2#](https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2#)

# How to use **GHRSST Sea Surface Temperature in** QGIS

- Click on the Open Data Source Manager:
![Figure 1](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-05_at_6.32.39_PM.png)
    
- Click on Vector on the left hand side of the panel. Click on the three dots that says 'Vector Dataset(s) and add the World boarders shapefile. Make sure you click ‘Add’ on the bottom right and then ‘Close’.
![Figure 2](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_9.29.29_AM.png)

- Next, add the GHRSST SSTA raster file by clicking the Open Data Source Manager, but this time choose the ‘Raster’ option. Click on the three dots that says 'Raster Dataset(s) and add the GHRSST SSTA data.
![Figure 3](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_9.31.52_AM.png)

- When you click ‘Add’ another window will open click on ‘Add Layers’ and then close the window. When you click ‘Add’ another window will open click on ‘sst_anomaly’, click on ‘Add Layers’, and then close the window.
![Figure 4](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_9.58.10_AM.png)
    
- Your layers should look like this:
![Figure 5](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_9.34.33_AM.png)
    
- We are now going to change the projection to focus on the El Niño region. Click on ‘Settings’ and click on “Custom Projections...’
![Figure 6](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.05.49_AM.png)

- Click on the green plus on the right hand corner, provide a Name, and on the ‘Parameters’ section, copy and paste this formula: +proj=ortho +lat_0=10 +lon_0=-150 +x_0=0 +y_0=0 +a=6371000 +b=6371000 +units=m +no_defs . Then click 'OK'. 
![Figure 7](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.18.24_AM.png)
    

- On the bottom right of the map where it says 'EPSG:4326' change it to whatever you have named it.
![Figure 8](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.18.55_AM.png)
    

- Right click on the sst_anomaly’ layer and click on ‘Properties’.
![Figure 9](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.35.30_AM.png)
    

- Select ‘Single pseudocolor’ and change the max to -2 to 2. Add the classes and change the colors.
![Figure 10](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.40.42_AM.png)
    

- Here is the final image. You can further change the background, add labels, etc: [https://docs.qgis.org/3.4/en/docs/training_manual/map_composer/map_composer.html](https://docs.qgis.org/3.4/en/docs/training_manual/map_composer/map_composer.html)
![Figure 11](../../images/MUR_SSTA_QGIS_IMAGES/Screenshot_2023-06-06_at_10.43.38_AM.png)