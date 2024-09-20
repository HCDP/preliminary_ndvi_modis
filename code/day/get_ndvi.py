import geemap ### package for google earth engine analysis 
import ee ### packge neccsary for using geemap
from os import makedirs, environ, system
import datetime
from sys import argv
from os.path import join

WINDOW_SIZE = 30

# get credentials and initialize ee and geemap
credentials = ee.ServiceAccountCredentials(environ["GEE_SERVICE_ACCOUNT"], environ["GEE_CREDENTIALS"])
ee.Initialize(credentials, project = environ["GC_PROJECT"])
geemap.ee_initialize()

HI_STATE_GEOMETRY = ee.Geometry.Polygon([[[-154.668, 18.849], [-154.668, 22.269], [-159.816, 22.269], [-159.816, 18.849]]])

def get_last_window():
    modis = ee.ImageCollection('MODIS/061/MOD09GQ')
    linked = modis.linkCollection(ee.ImageCollection("MODIS/061/MOD09GA"), ["state_1km"])
    bounded = linked.filterBounds(HI_STATE_GEOMETRY)
    sorted = bounded.sort('system:time_start', False)
    limited = sorted.limit(WINDOW_SIZE)
    return limited

def get_window_from_date(date):
    date_s = date.strftime("%Y-%m-%d")
    ee_date = ee.Date(date_s, "Pacific/Honolulu")
    ee_date_start = ee_date.advance(-WINDOW_SIZE, 'day')
    modis = ee.ImageCollection('MODIS/061/MOD09GQ')
    linked = modis.linkCollection(ee.ImageCollection("MODIS/061/MOD09GA"), ["state_1km"])
    bounded = linked.filterBounds(HI_STATE_GEOMETRY)
    sorted = bounded.sort('system:time_start', False)
    limited = sorted.filterDate(ee_date_start, ee_date)
    if limited.size().getInfo() < WINDOW_SIZE:
        limited = sorted.limit(WINDOW_SIZE)
    return limited


today = datetime.date.today()
date = datetime.date.today()
if len(argv) > 1:
    date = datetime.datetime.fromisoformat(argv[1]).date()

modis = None
#if date is today just grab the last 16 images
if date == today:
   modis = get_last_window()
else:
    modis = get_window_from_date(date)

#get first image date and format as the aggregation date
agg_date_str = modis.first().date().format("YYYY-MM-dd").getInfo()

# Cloud masking function
def maskMODISclouds(image):
    qa = image.select('state_1km')
    cloudBitMask = 1 << 10
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    return image.updateMask(mask)

filtered = modis.map(maskMODISclouds)

# NDVI calculation function
def addNDVI(image):
    ndvi = image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename('ndvi')
    return image.addBands(ndvi)

withNdvi = filtered.map(addNDVI)

# Gap-filling function
def fill(image):
    ima = image.focal_mean(1, 'square', 'pixels', 20)
    return ima.blend(image)

filled = withNdvi.map(fill)

# Reduce to median values
medians = filled.median()
ndvi = medians.select('ndvi')

outdir = join(environ["PROJECT_ROOT"], "data_outputs/raw")
outfile = join(outdir, f"ndvi_statewide_{agg_date_str}.tif")
makedirs(outdir, exist_ok = True)

dateenv = join(environ["PROJECT_ROOT"], "envs", "date.env")
with open(dateenv, "w") as f:
    f.write(f"export CUSTOM_DATE={agg_date_str}")

geemap.ee_export_image(ndvi, filename = outfile, scale = 250, region = HI_STATE_GEOMETRY)