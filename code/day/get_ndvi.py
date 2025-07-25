import geemap ### package for google earth engine analysis 
import ee ### packge neccsary for using geemap
from os import makedirs, environ
from datetime import date, datetime, timedelta
from sys import argv
from os.path import join
import json
import requests
from ndvi_recrop import mask_and_reproject

WINDOW_SIZE = 16
EXTENTS = ["statewide", "bi", "mn", "oa", "ka"]
HI_STATE_GEOMETRY = [[[-154.668, 18.849], [-154.668, 22.269], [-159.816, 22.269], [-159.816, 18.849]]]
gee_cred_file = environ["GEE_CREDENTIALS"]
hcdp_api_token = environ["HCDP_API_TOKEN"]
project_root = environ["PROJECT_ROOT"]

def get_modis_data(geometry):
    modis = ee.ImageCollection('MODIS/061/MOD09GQ')
    linked = modis.linkCollection(ee.ImageCollection("MODIS/061/MOD09GA"), ["state_1km"])
    bounded = linked.filterBounds(geometry)
    sorted = bounded.sort('system:time_start', False)
    last_date = date.fromisoformat(sorted.first().date().format("YYYY-MM-dd").getInfo())
    return (last_date, sorted)

def get_modis_window(modis, agg_date):
    date_s = agg_date.strftime("%Y-%m-%d")
    ee_date = ee.Date(date_s)
    ee_date_start = ee.Date("1970-01-01")
    date_bounded = modis.filterDate(ee_date_start, ee_date)
    limited = date_bounded.limit(WINDOW_SIZE)
    return limited

# Cloud masking function
def maskMODISclouds(image):
    qa = image.select('state_1km')
    cloudBitMask = 1 << 10
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    return image.updateMask(mask)

# NDVI calculation function
def addNDVI(image):
    ndvi = image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename('ndvi')
    return image.addBands(ndvi)

# Gap-filling function
def fill(image):
    ima = image.focal_mean(1, 'square', 'pixels', 20)
    return ima.blend(image)

def process_image(src, agg_date):
    for extent in EXTENTS:
        outfile = f"ndvi_modis_day_{extent}_data_map_{agg_date.strftime('%Y_%m_%d')}.tif"
        outdir = join(project_root, "data_outputs/processed", f"{extent}/data_map/{agg_date.strftime('%Y/%m')}/")
        makedirs(outdir, exist_ok = True)
        outpath = join(outdir, outfile)
        mask_file = join(project_root, f"dependencies/{extent}_mask.tif")
        print(f"Masking and reprojecting NDVI data for extent {extent}.")
        mask_and_reproject(src, mask_file, outpath)

def process_date(modis, geometry, agg_date):
    window = get_modis_window(modis, agg_date)
    #get first image date and format as the aggregation date
    agg_date_str = agg_date.isoformat()

    print(f"Aggregating NDVI data for {agg_date_str}")

    filtered = window.map(maskMODISclouds) 
    withNdvi = filtered.map(addNDVI)
    filled = withNdvi.map(fill)

    # Reduce to median values
    medians = filled.median()
    ndvi = medians.select('ndvi')

    outdir = join(project_root, "data_outputs/raw")
    outfile = join(outdir, f"ndvi_statewide_{agg_date.strftime('%Y_%m_%d')}.tif")
    makedirs(outdir, exist_ok = True)
    print("Creating raw NDVI from GEE")
    geemap.ee_export_image(ndvi, filename = outfile, scale = 250, region = geometry)
    process_image(outfile, agg_date)


def main():
    api_headers = {
        "Authorization": f"Bearer {hcdp_api_token}"
    }
    #get the last day of data that has already been processed
    api_range_url = "https://api.hcdp.ikewai.org/datasets/date/range?datatype=ndvi_modis&period=day"
    res = requests.get(api_range_url, headers = api_headers)
    res.raise_for_status()
    ds_end = res.json()[1]
    #start processing at the next day
    start_date = datetime.fromisoformat(ds_end).date() + timedelta(days = 1)

    #set the last day to the passed date
    #default to yesterday if no date provided
    end_date = date.today() - timedelta(days = 1)
    if len(argv) > 1:
        end_date = datetime.fromisoformat(argv[1]).date()
    #if the date passed is before the last day in the dataset range, only process that day (historical data)
    if end_date < start_date:
        start_date = end_date

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
    ee_geometry = ee.Geometry.Polygon(HI_STATE_GEOMETRY)

    last_available_date, modis = get_modis_data(ee_geometry)
    #if modis data availability ends before configured end date only process up to the last available date
    if last_available_date < end_date:
        end_date = last_available_date

    agg_date = start_date
    while agg_date <= end_date:
        process_date(modis, ee_geometry, agg_date)
        agg_date += timedelta(days = 1)
        
if __name__ == "__main__":
    main()