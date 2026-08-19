SWOT River Time-Series Tutorial in R
================
Navid Khizri (NASA JPL PO.DAAC Summer Intern; Alaska Pacific University
Student)

**Summary**

This introductory tutorial guides students through plotting a river
water surface elevation (WSE) time series in R using observations from
NASA’s Surface Water and Ocean Topography (SWOT) mission. Students will
learn how to locate river reach identifiers (reach_id) in the SWOT River
Database (SWORD), request observations via the Hydrocron API, clean
missing-data placeholders, and visualize the results using base R.

**Requirements**

Any compute environment (local RStudio or cloud-based RStudio).

**Learning Objectives**

- Identify river reach IDs of interest using the SWOT River Database
  (SWORD) <https://www.swordexplorer.com/>.  
- Interact with Hydrocron <https://podaac.github.io/hydrocron/>, NASA’s
  API for accessing SWOT hydrology time series.  
- Clean raw river height and slope time series.  
- Plot a time series using base R.

**Why SWOT Matters**

SWOT (Surface Water and Ocean Topography) is the first satellite mission
to survey nearly 90% of Earth’s rivers, lakes, and hydrologic systems.
SWOT uses Ka-band radar interferometry to measure water surface
elevation globally, providing data crucial for hydrology, flood
forecasting, and water management.

Alaska, with more than 12,000 rivers and limited stream gauges due to
high installation and maintenance costs, stands to benefit
significantly. SWOT’s wide-swath coverage provides consistent 21‑day
revisit observations — helping fill data gaps for remote communities and
improving hydrologic modeling, especially under climate change.

This tutorial shows an example of exploring river observations from SWOT
for a river in Alaska.

As a student at Alaska Pacific University in Anchorage, I had the
privilege of learning about Alaska Native communities. Many of these
communities are accessible only by plane or boat, and face increasing
flood risks driven by climate change. SWOT can help improve flood models
and provide critical water-level data to support flood readiness in
rural Alaska. For additional reading, see Water Mission to Gauge Alaskan
Rivers on Front Lines of Climate Change.

Link:
<https://sealevel.jpl.nasa.gov/news/1599/water-mission-to-gauge-alaskan-rivers-on-front-lines-of-climate-change/>

Explore the SWORD River Database to find your river reach_id of interest

Visit the interactive dashboard:

**<https://www.swordexplorer.com/>**

``` r
library(knitr)
```

![](https://github.com/podaac/tutorials/blob/master/images/SWOT_RiverDB_Basin.png?raw=true)<!-- -->

Click on the North American basin, then click on one of the numbers that
has your river in it. I will click on Alaska which is \#81.

![](https://github.com/podaac/tutorials/blob/master/images/Alaska.png?raw=true)<!-- -->

After clicking on the basin you will see colorful lines which represent
reach_ids. You can zoom in on the map into the river area of interest.

![](https://github.com/podaac/tutorials/blob/master/images/Area_Of_interest.png?raw=true)<!-- -->

The example in this tutorial uses reaches from the Kuskokwim River in
Southwestern Alaska. In the right-hand corner, you can see fields that
are available. For now, just keep reach_id selected. Hovering the mouse
over a river reach will display information about that reach, including
the reach ID. When you find your reach ID, note it because will use it
later when creating a time series.

**What is Hydrocron?**

Hydrocron is an API developed by NASA’s PO.DAAC that provides
time-series hydrology data from SWOT in formats such as GeoJSON and CSV.
At the time of the making of this tutorial each request retrieves data
for a **single reach_id**.

**Required Packages**

``` r
library(httr)
library(jsonlite)
```

**Functions Used in This Tutorial**

To simplify utilization of this workflow, several helper functions are
defined. - This part of the tutorial typically would only need to be run
once. - After that, if the user wishes to change the Hydrocron API query
parameters (start_time,end_time,fields), they can do so in the next
section below: Fetch, Clean, and Plot. - If a user wishes to modify the
API parameters requested, some modification of the helper functions may
be needed.

What the functions do: get_reach_data() creates the url to connect with
Hydrocron API to get your river reach data.

clean_hydrocron() filters out missing data.

plot_reach() plots the data.

``` r
# Fetch Hydrocron data
# Send a request to NASA's Hydrocron API, download SWOT river data, and prepare it for R.

get_reach_data <- function(reach_id, start_time, end_time, fields = "reach_id,time_str,wse,slope") {
  
  # Constructs a valid Hydrocron API URL by plugging in: your reach_id, your start date, your end date
  url <- paste0(
    "https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/timeseries?",
    "feature=Reach",
    "&feature_id=", reach_id,
    "&output=geojson",
    "&start_time=", start_time,
    "&end_time=", end_time,
    "&fields=", fields
  )

  # R sends the request to NASA's servers
  res <- GET(url) 

  # Convert returned JSON into an R list
  geo <- fromJSON(content(res, "text")) 

  # Extract the actual river measurements
  data <- geo$results$geojson$features$properties 

  # Convert time strings into real time stamps
  data$time <- as.POSIXct(data$time_str, format = "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
 
  # Return the clean data table
  return(data)
}


clean_hydrocron <- function(df) {

  # Convert wse and slope to numeric. Hydrocron stores data as characters strings instead of numeric which will crash the plot if not converted.
  df$wse   <- as.numeric(df$wse)
  df$slope <- as.numeric(df$slope)

  # Remove rows with "no_data"
  df <- df[df$time_str != "no_data", ]

  # Remove fill value rows
  df <- df[df$wse   != -999999999999.0, ] 
  df <- df[df$slope != -999999999999.0, ]

  # Remove rows where timestamp conversion failed
  df <- df[!is.na(df$time), ]

  # Output the cleaned dataset
  return(df) 
}


# Plot a SWOT river reach
plot_reach <- function(data, title = "SWOT River Time-Series") {

  plot(
    data$time, data$wse,
    main = title,
    xlab = "Time",
    ylab = "Water Surface Elevation (m)",
    col = "red",
    pch = 16
  )

  lines(data$time, data$wse, col = "black")
  grid() # Improves readability for students
}
```

**Fetch, Clean, and Plot SWOT Data**

In this example, we request all observations for reach `81181700021`
from 2023–2026. A user can change these inputs to request different time
periods and/or river IDs. User only needs to re-run the cell below when
modifying the query parameters(reach_id,start_time,end_time).

Note: At the time of writing this tutorial, there is a limit on how much
data the API can query. If you’re reach is too large, consider breaking
the query up into smaller requests. If interested in 2023 to 2027 data,
you could do two queries: 2023-10-01 to 2025-05-31 and 2025-06-01 to
2027-07-25.

``` r
data_raw <- get_reach_data(
  reach_id   = "81181700021", # Insert your reach ID here
  start_time = "2025-06-01T00:00:00Z", # Insert Start Date
  end_time   = "2027-07-25T00:00:00Z"  # Insert End Date
)
```

    ## No encoding supplied: defaulting to UTF-8.

``` r
data <- clean_hydrocron(data_raw)

plot_reach(data, title = "Kuskokwim River")
```

![](SWOT_River_Time_Series_Tutorial_in_R4_files/figure-gfm/unnamed-chunk-7-1.png)<!-- -->

**Conclusion**

You successfully retrieved SWOT river surface elevation data using
Hydrocron, cleaned missing data, and plotted a time series. This
workflow can be reused for any river reach available in the SWORD
database.

SWOT offers valuable high-resolution hydrologic data — especially for
remote and ungauged regions like rural Alaska — unlocking new
opportunities for hydrology education, research, and community impact.
