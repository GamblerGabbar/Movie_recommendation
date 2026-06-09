#!/bin/bash
# 0_prepare_filtered_hdfs.sh
# Uses ALL genres with >= 100 movies - maximizes dataset coverage (~13,600 movies)
# Run inside: docker exec -it hadoop-mahout-namenode bash

set -e

HDFS_URI="hdfs://namenode:9000"
export HADOOP_CONF_DIR=/opt/hadoop-3.2.1/etc/hadoop
unset MAHOUT_LOCAL

# All genres with >= 100 movies in the 13,711-movie dataset:
# Drama:3235, Comedy:2449, Action:1642, Horror:1125, Animation:866,
# Thriller:673, Adventure:609, Crime:606, Romance:529, Science_Fiction:388,
# Family:373, Fantasy:278, Documentary:259, Mystery:173, Music:135,
# Western:122, War:117
# (Excluded: History:95, TV_Movie:37 - too sparse)
KEEP_GENRES="Drama Comedy Action Horror Animation Thriller Adventure Crime Romance Science_Fiction Family Fantasy Documentary Mystery Music Western War"

echo "================================================================"
echo " Step 0: Rebuilding HDFS dataset (17 genres, all 13K movies)"
echo "================================================================"

echo "Clearing old derived data..."
hdfs dfs -rm -r -f ${HDFS_URI}/movie_data_filtered
hdfs dfs -rm -r -f ${HDFS_URI}/movie_data_seq
hdfs dfs -rm -r -f ${HDFS_URI}/movie_data_vectors
hdfs dfs -rm -r -f ${HDFS_URI}/movie_data_train
hdfs dfs -rm -r -f ${HDFS_URI}/movie_data_test
hdfs dfs -rm -r -f ${HDFS_URI}/movie_genre_model
hdfs dfs -rm -r -f ${HDFS_URI}/labelindex
hdfs dfs -rm -r -f ${HDFS_URI}/test_results

echo "Copying all 17 genres from movie_data_raw to movie_data_filtered..."
hdfs dfs -mkdir -p ${HDFS_URI}/movie_data_filtered

for genre in ${KEEP_GENRES}; do
    count=$(hdfs dfs -count ${HDFS_URI}/movie_data_raw/${genre} 2>/dev/null | awk '{print $2}')
    echo "  Copying: ${genre} (${count} movies)"
    hdfs dfs -cp ${HDFS_URI}/movie_data_raw/${genre} ${HDFS_URI}/movie_data_filtered/${genre}
done

echo ""
echo "Filtered HDFS dataset (17 genres):"
hdfs dfs -ls ${HDFS_URI}/movie_data_filtered/
