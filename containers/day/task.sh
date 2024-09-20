#!/bin/bash

echo "[task.sh] [1/5] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE
source envs/prod.env

echo "[task.sh] [2/5] Getting NDVI data from GEE."
echo "--- start get_ndvi.py ---"
python3 -u code/day/get_ndvi.py $CUSTOM_DATE
echo "--- end get_ndvi.py ---"

source envs/date.env
echo "NDVI aggregation date is: " $CUSTOM_DATE

echo "[task.sh] [3/5] NDVI processing."
# INSERT NDVI PROCESSING SCRIPT CALL HERE

echo "[task.sh] [4/5] Preparing to upload data."
# cd /sync
# python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [5/5] Uploading data."
# python3 upload.py

echo "[task.sh] All done!"