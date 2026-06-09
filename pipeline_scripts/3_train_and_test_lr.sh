#!/bin/bash
# 3_train_and_test_nb.sh - Final pipeline (best settings)

set -e

HDFS_URI="hdfs://namenode:9000"
export HADOOP_CONF_DIR=/opt/hadoop-3.2.1/etc/hadoop
unset MAHOUT_LOCAL

VECTORS_PATH=${HDFS_URI}/movie_data_vectors/tfidf-vectors
TRAIN_DIR=${HDFS_URI}/movie_data_train
TEST_DIR=${HDFS_URI}/movie_data_test
MODEL_DIR=${HDFS_URI}/movie_genre_model
LABEL_INDEX=${HDFS_URI}/labelindex
TEST_RESULTS=${HDFS_URI}/test_results

echo "================================================================"
echo " Movie Genre Classification (Mahout MapReduce)"
echo " 6 genres | Stemmed TF-IDF bigrams | 20% test split"
echo "================================================================"

echo ""
echo "=== Step 1: Split TF-IDF vectors 80%/20% Train/Test ==="
mahout split \
  -i ${VECTORS_PATH} \
  --trainingOutput ${TRAIN_DIR} \
  --testOutput ${TEST_DIR} \
  --randomSelectionPct 20 \
  --overwrite \
  --sequenceFiles -xm sequential

echo ""
echo "=== Step 2: Train Complementary Naive Bayes (MapReduce) ==="
mahout trainnb \
  -i ${TRAIN_DIR} \
  -o ${MODEL_DIR} \
  -li ${LABEL_INDEX} \
  -a 1 \
  -ow \
  -c

echo ""
echo "=== Step 3: Evaluate on Test Set ==="
mahout testnb \
  -i ${TEST_DIR} \
  -m ${MODEL_DIR} \
  -l ${LABEL_INDEX} \
  -ow \
  -o ${TEST_RESULTS} \
  -c

echo ""
echo "=== Pipeline Complete! ==="
