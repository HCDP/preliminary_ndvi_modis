import geemap ### package for google earth engine analysis 
import ee ### packge neccsary for using geemap
from os import makedirs, environ, system
import datetime
from sys import argv
from os.path import join
import json

WINDOW_SIZE = 16

gee_cred_file = environ["GEE_CREDENTIALS"]
gee_project_id = None
service_account = None
with open(gee_cred_file) as f:
    config = json.load(f)
    gee_project_id = config["project_id"]
    service_account = config["client_email"]

# get credentials and initialize ee and geemap
credentials = ee.ServiceAccountCredentials(service_account, gee_cred_file)
ee.Initialize(credentials, project = gee_project_id)
geemap.ee_initialize()

HI_STATE_GEOMETRY = ee.Geometry.Polygon([[[-154.668, 18.849], [-154.668, 22.269], [-159.816, 22.269], [-159.816, 18.849]]])

def get_window_from_date(date):
    date_s = date.strftime("%Y-%m-%d")
    ee_date = ee.Date(date_s)
    ee_date_start = ee.Date("1970-01-01")
    modis = ee.ImageCollection('MODIS/061/MOD09GQ')
    linked = modis.linkCollection(ee.ImageCollection("MODIS/061/MOD09GA"), ["state_1km"])
    bounded = linked.filterBounds(HI_STATE_GEOMETRY)
    sorted = bounded.sort('system:time_start', False)
    last_date = datetime.date.fromisoformat(sorted.first().date().format("YYYY-MM-dd").getInfo())
    agg_date = date if date < last_date else last_date
    date_bounded = sorted.filterDate(ee_date_start, ee_date)
    limited = date_bounded.limit(WINDOW_SIZE)
    return (agg_date, limited)

# how to handle missing days that are filled

#default to yesterday if no date provided
date = datetime.date.today() - datetime.timedelta(days = 1)
if len(argv) > 1:
    date = datetime.datetime.fromisoformat(argv[1]).date()

modis = None
agg_date, modis = get_window_from_date(date)

#get first image date and format as the aggregation date
agg_date_str = agg_date.isoformat()

print(f"Aggregating NDVI data for {agg_date_str}")

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
ndvi.unmask(-9999)

outdir = join(environ["PROJECT_ROOT"], "data_outputs/raw")
outfile = join(outdir, f"ndvi_statewide.tif")
makedirs(outdir, exist_ok = True)

dateenv = join(environ["PROJECT_ROOT"], "envs", "date.env")
with open(dateenv, "w") as f:
    f.write(f"export CUSTOM_DATE={agg_date_str}")

geemap.ee_export_image(ndvi, filename = outfile, scale = 250, region = HI_STATE_GEOMETRY, formatOptions = { "COMPRESS": "LZW" })
