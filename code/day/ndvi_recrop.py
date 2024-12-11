import os
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
import numpy as np

# Get daily ndvi
os.chdir("dir/raw")
ndvi_tiffs = [f for f in os.listdir() if f.startswith("ndvi_statewide_")]
with rasterio.open(ndvi_tiffs[-1]) as src:
    ndvi = src.read(1)

# Get mask raster
os.chdir("dir/masks")
hi_mask = rasterio.open("hi_mask.tif")
bi_mask = rasterio.open("bi_mask.tif")
mn_mask = rasterio.open("mn_mask.tif")
oa_mask = rasterio.open("oa_mask.tif")
ka_mask = rasterio.open("ka_mask.tif")

# Resample and mask input ndvi
ndvi_re = ndvi  # need resample to align ndvi grid to hi_mask (statewide mask)
ndvi_hi, _ = mask(hi_mask, [hi_mask.read(1)], crop=True)

# Crop ndvi hi to each county mask
ndvi_bi, _ = mask(bi_mask, [ndvi_hi], crop=True)
ndvi_mn, _ = mask(mn_mask, [ndvi_hi], crop=True)
ndvi_oa, _ = mask(oa_mask, [ndvi_hi], crop=True)
ndvi_ka, _ = mask(ka_mask, [ndvi_hi], crop=True)

# Write final rasters as geo tiffs
os.chdir("dir/out")
with rasterio.open("statewide/ndvi/ndvi_hi.tif", 'w', driver='GTiff', height=ndvi_hi.shape[0], width=ndvi_hi.shape[1], count=1, dtype=ndvi_hi.dtype) as dst:
    dst.write(ndvi_hi, 1)

with rasterio.open("county/BI/ndvi/ndvi_bi.tif", 'w', driver='GTiff', height=ndvi_bi.shape[0], width=ndvi_bi.shape[1], count=1, dtype=ndvi_bi.dtype) as dst:
    dst.write(ndvi_bi, 1)

with rasterio.open("county/MN/ndvi/ndvi_mn.tif", 'w', driver='GTiff', height=ndvi_mn.shape[0], width=ndvi_mn.shape[1], count=1, dtype=ndvi_mn.dtype) as dst:
    dst.write(ndvi_mn, 1)

with rasterio.open("county/OA/ndvi/ndvi_oa.tif", 'w', driver='GTiff', height=ndvi_oa.shape[0], width=ndvi_oa.shape[1], count=1, dtype=ndvi_oa.dtype) as dst:
    dst.write(ndvi_oa, 1)

with rasterio.open("county/KA/ndvi/ndvi_ka.tif", 'w', driver='GTiff', height=ndvi_ka.shape[0], width=ndvi_ka.shape[1], count=1, dtype=ndvi_ka.dtype) as dst:
    dst.write(ndvi_ka, 1)

# Code pau

