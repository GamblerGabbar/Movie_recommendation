# Movie Genre Classification Pipeline

This repository contains a full Big Data pipeline to fetch real movie metadata via the TMDB API
and classify genres using **Hadoop HDFS**, **MapReduce**, and **Apache Mahout** Logistic Regression.

## Architecture Overview

```
TMDB API ──► fetch_tmdb_movies.py ──► dataset/movies/<Genre>/<id>.txt
                                              │
                                        [Docker]
                                              │
                                    HDFS (NameNode + DataNode)
                                              │
                                  Mahout seqdirectory (SequenceFiles)
                                              │
                                  Mahout seq2sparse (TF-IDF via MapReduce)
                                              │
                                  Mahout trainlogistic (Logistic Regression)
                                              │
                                    Confusion Matrix + AUC Score
```

---

## Prerequisites

1. **Python 3.8+** with `pip`
2. **Docker Desktop** installed and running on Windows

---

## Step 1: Fetch Movie Dataset from TMDB API

Activate the virtual environment and run the ingestion script:

```powershell
# From the project root
.\.venv\Scripts\python.exe .\data_ingestion\fetch_tmdb_movies.py
```

> ⚠️ If you get a `ConnectionResetError`, your ISP/network may be blocking TMDB.
> Enable a **VPN** and rerun the command.

This will create `dataset/movies/<Genre>/` folders each containing `.txt` files
(one per movie), with the title and description as content.

---

## Step 2: Build and Start the Hadoop + Mahout Docker Cluster

The cluster has two services:
- **NameNode** — custom image with Mahout 0.13.0 installed
- **DataNode** — stores HDFS data blocks (required for any HDFS write to succeed)

```powershell
cd docker_environment
docker-compose up -d --build
```

Wait ~30 seconds for the cluster to fully initialize, then verify it is up:

```powershell
docker ps
# Should show: hadoop-mahout-namenode and hadoop-mahout-datanode running
```

You can also open the HDFS Web UI at: **http://localhost:9870**

---

## Step 3: Enter the NameNode Container

```powershell
docker exec -it hadoop-mahout-namenode bash
```

You are now inside the Linux container where Hadoop and Mahout are available.

---

## Step 4: Run the Pipeline (Inside the Container)

Execute the three pipeline scripts in order:

### A. Upload Dataset to HDFS
```bash
bash /data/pipeline_scripts/1_upload_to_hdfs.sh
```
This creates `/movie_data_raw/<Genre>/` directories in HDFS and uploads all `.txt` files.

### B. MapReduce Vectorization (TF-IDF)
```bash
bash /data/pipeline_scripts/2_preprocess_mahout.sh
```
This runs two Mahout MapReduce jobs:
1. `seqdirectory` — converts text files into Hadoop SequenceFile format
2. `seq2sparse` — computes TF-IDF term weights across the corpus in a distributed MapReduce fashion

### C. Train & Evaluate Logistic Regression Model
```bash
bash /data/pipeline_scripts/3_train_and_test_lr.sh
```
This:
1. Splits vectors 80/20 into train/test sets
2. Dumps vectors to CSV (required format for `trainlogistic`)
3. Trains an SGD-based Logistic Regression model over 50 passes
4. Evaluates and prints **Confusion Matrix** and **AUC Score** to the terminal

---

## Expected Output

At the end of script 3, you should see output like:
```
AUC = 0.87
Confusion Matrix:
              Action  Comedy  Drama  ...
  Action        234      12     5   ...
  Comedy         8      198    14   ...
  ...
```
