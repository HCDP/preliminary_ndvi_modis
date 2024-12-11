library(raster)

#get daily ndvi
setwd("/home/hawaii_climate_products_container/preliminary/ndvi_modis/data_outputs/raw")
ndvi_tiffs<-list.files(pattern="ndvi_statewide_*")
ndvi<-raster(ndvi_tiffs[length(ndvi_tiffs)])
plot(ndvi)

#get mask raster
setwd("/home/hawaii_climate_products_container/preliminary/ndvi_modis/dependencies/masks")
hi_mask<-raster("hi_mask.tif")
bi_mask<-raster("bi_mask.tif")
mn_mask<-raster("mn_mask.tif")
oa_mask<-raster("oa_mask.tif")
ka_mask<-raster("ka_mask.tif")
plot(hi_mask)

#resample and mask ndvi
ndvi_re<-resample(ndvi, hi_mask, method="bilinear")
ndvi_hi<-mask(ndvi_re,hi_mask)
plot(ndvi_hi)

#crop ndvi hi to each county
ndvi_bi<-crop(ndvi_hi,bi_mask)
ndvi_mn<-crop(ndvi_hi,mn_mask)
ndvi_oa<-crop(ndvi_hi,oa_mask)
ndvi_ka<-crop(ndvi_hi,ka_mask)
plot(ndvi_mn)

#write final rasters
setwd("/home/hawaii_climate_products_container/preliminary/ndvi_modis/data_outputs/tiffs/daily")
writeRaster(ndvi_hi,"statewide/ndvi/ndvi_hi.tif")
writeRaster(ndvi_bi,"county/BI/ndvi/ndvi_bi.tif")
writeRaster(ndvi_mn,"county/MN/ndvi/ndvi_mn.tif")
writeRaster(ndvi_oa,"county/OA/ndvi/ndvi_oa.tif")
writeRaster(ndvi_ka,"county/KA/ndvi/ndvi_ka.tif")

#Code pau


