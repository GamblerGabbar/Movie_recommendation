#!/bin/bash
# 1_upload_to_hdfs.sh
# Run this inside the Hadoop/Mahout Docker container

echo "Creating directory in HDFS for movie dataset..."
hdfs dfs -mkdir -p /movie_data_raw

echo "Uploading local dataset to HDFS..."
hdfs dfs -put /data/dataset/movies/* /movie_data_raw/

echo "Listing HDFS contents to verify upload:"
hdfs dfs -ls /movie_data_raw/
