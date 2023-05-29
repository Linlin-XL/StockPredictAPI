#!/bin/sh

# Copy the stock input files

echo "Start Stock Data Pipeline"
python etl_task.py

# Copy the stock output files into predict_model
echo "Copy: $ETL_Model_Path/* to $API_Model_Path/"
rsync -azvh $ETL_Model_Path/* $API_Model_Path/

exec "$@"