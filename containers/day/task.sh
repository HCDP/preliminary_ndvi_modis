#!/bin/bash

echo "[task.sh] [1/4] Starting Execution."
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

echo "[task.sh] [2/4] Getting NDVI data from GEE. Mask, reproject, and split into counties."
echo "--- start get_ndvi.py ---"
python3 -u code/get_ndvi.py $CUSTOM_DATE
echo "--- end get_ndvi.py ---"

echo "[task.sh] [3/4] Preparing to upload data."
cd /sync
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [4/4] Uploading data."
python3 upload.py

echo "[task.sh] All done!"