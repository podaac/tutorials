#Modules needed for accesing S3 data in the cloud
library("aws.s3")
library("ncdf4")
library("raster")
#Setting Environment variables with AWS access keys  - See links below
#https://archive.podaac.earthdata.nasa.gov/s3credentials 
#https://archive.podaac.earthdata.nasa.gov/s3credentialsREADME 
Sys.setenv(AWS_ACCESS_KEY_ID="key",AWS_SECRET_ACCESS_KEY="secret",AWS_DEFAULT_REGION="us-west-2",AWS_REGION="us-west-2",AWS_SESSION_TOKEN="token")

#Opening a specific file
nc_data <- s3read_using(FUN = nc_open, object = "20040111090000-JPL-L4_GHRSST-SSTfnd-MUR25-GLOB-v02.0-fv04.2.nc", bucket="podaac-ops-cumulus-protected/MUR25-JPL-L4-GLOB-v04.2" )
lat <- ncvar_get(nc_data, "lat")
lon <- ncvar_get(nc_data, "lon")
analysed_sst <- ncvar_get(nc_data, "analysed_sst")

#Obtaining Fill value from attributes

fillvalue <- ncatt_get(nc_data, "analysed_sst", "_FillValue")
analysed_sst[analysed_sst == fillvalue$value] <- NA
nc_close(nc_data)

#Saving plot to jpeg
r <- raster(t(analysed_sst), xmn=min(lon), xmx=max(lon), ymn=min(lat), ymx=max(lat), crs=CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs+ towgs84=0,0,0"))
r <- flip(r, direction='y')
jpeg('20040111090000-JPL-L4_GHRSST-SSTfnd-MUR25-GLOB-v02.0-fv04.2.jpg')
plot(r)
dev.off()