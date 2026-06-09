# Movie Genre Classification and Recommendation Pipeline

This project is a Big Data workflow for collecting real movie metadata from TMDB, enriching the dataset, and training a genre classifier with Hadoop MapReduce and Apache Mahout. It also includes a static movie recommendation UI and supporting assets for the final report and architecture diagram.

## Tech Stack

- Python 3 for data ingestion, enrichment, and JSON generation
- TMDB API for fetching live movie metadata
- Docker and Docker Compose for the Hadoop + Mahout environment
- Hadoop HDFS and MapReduce for distributed preprocessing
- Apache Mahout for TF-IDF vectorization and classification
- HTML, CSS, and JavaScript for the website and recommender UI
- Static assets and screenshots for documentation and reporting

## Website Preview

![CineVault website preview](report_assets/screenshots/website_image.png)

## What is in this repository

- `data_ingestion/` - Python scripts that fetch TMDB data, enrich movie text files, and build the compact JSON database.
- `dataset/` - Genre-organized movie text files used as the training corpus.
- `docker_environment/` - Docker image and Compose setup for the Hadoop + Mahout environment.
- `pipeline_scripts/` - Shell scripts that upload data to HDFS, preprocess it, and train/evaluate the model.
- `movie_recommender/` - Static recommender frontend and the generated `movies_db.json` dataset.
- `website/` - Presentation-style landing page for the project.
- `docs/` - Additional project documentation.
- `report_assets/` - Figures and summary material used in the report.

## Pipeline Overview

1. Fetch movie metadata from TMDB into `dataset/movies/<Genre>/<movie_id>.txt`.
2. Enrich the text files with tagline, keywords, cast, and director.
3. Build `movie_recommender/movies_db.json` for the web UI.
4. Start the Hadoop + Mahout Docker environment.
5. Upload the dataset to HDFS and run the Mahout preprocessing and training scripts.

## Python Requirements

Use the top-level `requirements.txt` to install the Python dependencies used by the utility scripts:

```powershell
python -m pip install -r requirements.txt
```

If you prefer to install only the ingestion dependencies, you can also use `data_ingestion/requirements.txt`.

## Typical Workflow

### 1. Set up TMDB credentials

Create a `.env` file for local runs and define `TMDB_API_KEY`.

### 2. Fetch and enrich the dataset

Run the ingestion scripts from the project root:

```powershell
python .\data_ingestion\fetch_tmdb_movies.py
python .\data_ingestion\enrich_dataset.py
python .\data_ingestion\build_movie_db.py
```

### 3. Start Hadoop + Mahout

```powershell
cd docker_environment
docker compose up -d --build
```

### 4. Run the pipeline inside the container

```bash
bash /data/pipeline_scripts/0_prepare_filtered_hdfs.sh
bash /data/pipeline_scripts/1_upload_to_hdfs.sh
bash /data/pipeline_scripts/2_preprocess_mahout.sh
bash /data/pipeline_scripts/3_train_and_test_lr.sh
```

## Notes

- The project currently uses a mix of generated and source assets. Keep the dataset and JSON outputs if you want the repository to be immediately runnable.
- Large generated artifacts that are not needed for collaboration can be removed before publishing, but the core scripts and documentation should stay in version control.
