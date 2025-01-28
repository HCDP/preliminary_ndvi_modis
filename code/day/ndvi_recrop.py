import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
import numpy.ma as ma
from os import environ, makedirs
from os.path import join

def mask_and_reproject(ndvi_file, mask_file, out_file):
    #open NDVI source file and mask
    with rasterio.open(ndvi_file) as src, rasterio.open(mask_file) as mask:
        #get mask projection
        dst_crs = mask.crs
        #calculate the output transform matrix
        dst_transform, dst_width, dst_height = calculate_default_transform(src.crs, dst_crs, mask.width, mask.height, *mask.bounds)
        nodata = mask.nodata

        #copy source metadata and update with destination properties
        dst_profile = src.profile.copy()
        dst_profile.update({
            "crs": dst_crs,
            "transform": dst_transform,
            "width": dst_width,
            "height": dst_height,
            "nodata": nodata,
            "compress": "lzw"
        })
        
        #open destination file with metadata
        with rasterio.open(out_file, "w+", **dst_profile) as dst:
            #reproject source NDVI into destination file with bilinear sampling and computed properties
            reproject(source = rasterio.band(src, 1), destination = rasterio.band(dst, 1), src_transform = src.transform, src_crs = src.crs, dst_transform = dst_transform, dst_crs = dst_crs, resampling = Resampling.bilinear)
            #read data from reprojection
            dst_data = dst.read(1)
            #mask nodata values from mask
            mask_data = mask.read(1, masked = True).mask
            masked_data = ma.masked_array(dst_data, mask = mask_data)
            #write data back to file
            dst.write(masked_data, indexes = 1)

project_root = environ["PROJECT_ROOT"]
src_file = join(project_root, f"data_outputs/raw/ndvi_statewide.tif")

outdir = join(project_root, "data_outputs/processed")
makedirs(outdir, exist_ok = True)

extents = ["hi", "bi", "mn", "oa", "ka"]
for extent in extents:
    out_file = join(outdir, f"{extent}.tif")
    mask_file = join(project_root, f"dependencies/{extent}_mask.tif")
    mask_and_reproject(src_file, mask_file, out_file)