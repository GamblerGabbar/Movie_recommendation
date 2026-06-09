#!/bin/bash
# 2_preprocess_mahout.sh
# Run this inside the Hadoop/Mahout Docker container (exec into namenode)

set -e

HDFS_URI="hdfs://namenode:9000"
export HADOOP_CONF_DIR=/opt/hadoop-3.2.1/etc/hadoop
unset MAHOUT_LOCAL

echo "=== Step 1: Converting filtered HDFS text dirs into Hadoop SequenceFiles ==="
mahout seqdirectory \
  -i ${HDFS_URI}/movie_data_filtered \
  -o ${HDFS_URI}/movie_data_seq \
  -c UTF-8 \
  -ow

echo ""
echo "=== Step 2: TF-IDF Vectorization with English Stemmer (seq2sparse) ==="
# Key improvements over previous run:
#   -a org.apache.lucene.analysis.en.EnglishAnalyzer
#       -> Porter stemmer + English stop-word removal
#       -> "running/runs/ran" all become "run"; removes "the/a/is/etc."
#       -> This is the single biggest NLP accuracy lever available in Mahout
#   -ng 2     -> Unigrams AND bigrams
#   -ml 5     -> Keep terms with log-likelihood >= 5 (less aggressive, keep more signal)
#   -x 70     -> Ignore terms in >70% of docs (stricter common-word removal)
#   -n 2      -> L2 normalize vectors
#   -wt tfidf -> TF-IDF weighting
#   -nv       -> Named vectors
mahout seq2sparse \
  -i ${HDFS_URI}/movie_data_seq \
  -o ${HDFS_URI}/movie_data_vectors \
  -a org.apache.lucene.analysis.en.EnglishAnalyzer \
  -ng 2 \
  -ml 5 \
  -x 70 \
  -n 2 \
  -wt tfidf \
  -nv \
  -ow

echo ""
echo "=== Preprocessing Complete. Stemmed TF-IDF vectors at ${HDFS_URI}/movie_data_vectors ==="
