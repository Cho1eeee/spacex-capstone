# SpaceX Falcon 9 First-Stage Landing Prediction — Data Science Capstone

End-to-end data science capstone project: collect, clean, analyse and model
SpaceX Falcon 9 launch data to answer the question — **at what cost can we
reuse a first-stage booster?** (i.e. predicting whether a booster will
successfully land, which drives the ~$62M vs ~$283M launch-cost advantage).

## Pipeline

| Stage | Script | Output |
|---|---|---|
| 1. Data collection (SpaceX API v4, w/ mirror fallback + Launch Library 2 cross-check) | `scripts/01_collect_data.py` | `data/spacex_launch_data.csv` |
| 2. Web scraping (requests + BeautifulSoup, NextSpaceFlight) | `scripts/02_scrape_wikipedia.py` | `data/spacex_web_scraped.csv` |
| 3. Data wrangling (label engineering, imputation, one-hot) | `scripts/03_clean_data.py` | `data/dataset_part_2.csv`, `data/dataset_part_3.csv` |
| 4. EDA (matplotlib/seaborn) | `scripts/04_eda.py` | `plots/eda_*.png` |
| 5. SQL analysis (sqlite3, 8 queries) | `scripts/05_sql_analysis.py` | `data/spacex.db`, `sql/sql_results.txt` |
| 6. Folium maps (sites, records, proximity) | `scripts/06_folium_maps.py` | `maps/*.html` |
| 7. Interactive Dash dashboard | `scripts/07_dash_app.py` | run locally, port 8050 |
| 8. Classification models (LR/SVM/DT/KNN/RF + GridSearchCV) | `scripts/08_ml_models.py` | `models/model_results.txt`, confusion matrix |

The same pipeline is also provided as **Jupyter notebooks with executed outputs**
in `notebooks/`:

| Notebook | Stage |
|---|---|
| `01_spacex_data_collection_api.ipynb` | SpaceX API data collection |
| `02_spacex_data_collection_webscraping.ipynb` | Web scraping |
| `03_data_wrangling.ipynb` | Data wrangling |
| `04_eda_dataviz.ipynb` | EDA visualization |
| `05_eda_sql.ipynb` | SQL analysis |
| `06_folium_maps.ipynb` | Folium maps |
| `07_plotly_dash.ipynb` | Plotly Dash app |
| `08_ml_prediction.ipynb` | Classification models |

## Quick start

```bash
pip install -r requirements.txt
python scripts/01_collect_data.py
python scripts/02_scrape_wikipedia.py
python scripts/03_clean_data.py
python scripts/04_eda.py
python scripts/05_sql_analysis.py
python scripts/06_folium_maps.py
python scripts/08_ml_models.py
python scripts/07_dash_app.py   # open http://127.0.0.1:8050
```

## Key results

- Landing attempts in dataset: 69 → 60 successes (87.0%), overall success rate incl. non-attempts: 66.7%
- Site success rates: KSC LC-39A 77.3%, VAFB SLC-4E 76.9%, CCAFS SLC-40 60.0%
- Orbit insight: VLEO (Starlink) missions carry the heaviest payloads (~15,316 kg avg) yet land reliably
- Best model: Decision Tree (entropy, depth 2) — test accuracy 88.9%
  (SVM 83.3%, KNN 83.3%, Logistic Regression 77.8%)

## Note on data source

The official `api.spacexdata.com` v4 API was down (Cloudflare 522/525) during
collection. The pipeline attempts the live API first and falls back to a
hosted snapshot of the same SpaceX API v4 export; totals were cross-validated
against the live Launch Library 2 API (821 Falcon 9 launches to date).

## Tech stack

Python · requests · BeautifulSoup · pandas · NumPy · Matplotlib · Seaborn ·
SQLite · Folium · Plotly Dash · scikit-learn
