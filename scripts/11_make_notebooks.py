# -*- coding: utf-8 -*-
"""
Generate course-style Jupyter notebooks from the pipeline scripts.
Each notebook: markdown intro + logically split code cells, ready to execute.
Output: notebooks/*.ipynb (repo root, so relative data/ plots/ paths work)
"""
import os, re, sys

HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(HERE, "scripts")
OUTDIR = os.path.join(HERE, "notebooks")
os.makedirs(OUTDIR, exist_ok=True)

try:
    import nbformat
    from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
except ImportError:
    sys.exit("nbformat missing - install first")

INTROS = {
    "01_collect_data.py": ("SpaceX Launch Data Collection - SpaceX REST API v4",
        "Calls `POST /v4/launches/query` with `populate` for rockets, launchpads and payloads, "
        "with an automatic fallback to the course-hosted snapshot of the same API export, "
        "and a live cross-check against Launch Library 2.\n\n"
        "**Output:** `data/spacex_launch_data.csv`"),
    "02_scrape_wikipedia.py": ("Data Collection - Web Scraping (requests + BeautifulSoup)",
        "Scrapes launch cards from a public spaceflight listing site (NextSpaceFlight.com), "
        "extracting mission name, rocket, provider and location, then cross-validates "
        "against the API dataset launch sites.\n\n**Output:** `data/spacex_web_scraped.csv`"),
    "03_clean_data.py": ("Data Wrangling / Cleaning",
        "Derives the binary landing-success label (`Class`), imputes missing payload mass, "
        "parses dates into `Year`, fills categorical NaNs, and one-hot encodes "
        "Orbit / LaunchSite / LandingPad / Serial.\n\n"
        "**Outputs:** `data/dataset_part_2.csv` (labelled clean data), "
        "`data/dataset_part_3.csv` (ML feature matrix)."),
    "04_eda.py": ("Exploratory Data Analysis - Visualization",
        "Six matplotlib/seaborn plots: payload vs outcome scatter, yearly success trend, "
        "site counts, success rate by orbit, payload distribution by orbit, reuse vs success.\n\n"
        "**Outputs:** `plots/eda_*.png`"),
    "05_sql_analysis.py": ("Exploratory Analysis with SQL (SQLite)",
        "Loads the cleaned dataset into SQLite as `SPACEXTBL` and runs the 8 required "
        "query groups (sites, payloads, success rankings, boosters, time trends).\n\n"
        "**Output:** `sql/sql_results.txt`"),
    "06_folium_maps.py": ("Interactive Visual Analytics - Folium Maps",
        "Builds three maps: launch sites with success/failure circle markers, all launch "
        "records clustered by outcome, and a proximity analysis from KSC LC-39A to "
        "coastline / railway / highway / nearest city.\n\n**Outputs:** `maps/*.html`"),
    "07_dash_app.py": ("Interactive Visual Analytics - Plotly Dash App",
        "A Dash dashboard with a site dropdown linked to a landing-outcome pie chart and a "
        "payload-vs-outcome scatter. Run the last cell's `app.run(...)` locally, then open "
        "http://127.0.0.1:8050. Screenshots of the running app are shown below."),
    "08_ml_models.py": ("Predictive Analysis - Classification (Landing Success)",
        "Trains and tunes 5 classifiers (Logistic Regression, SVM, Decision Tree, KNN, "
        "Random Forest) with 10-fold GridSearchCV, reports test accuracy and the best "
        "model's confusion matrix.\n\n**Outputs:** `models/model_results.txt`, "
        "`plots/ml_confusion_matrix.png`"),
}

# cell split anchors: new code cell starts at the first line matching each prefix
ANCHORS = {
    "01_collect_data.py": ["def try_spacex_api_v4", "def crosscheck_launch_library", "def main"],
    "02_scrape_wikipedia.py": ["def scrape", "def main"],
    "03_clean_data.py": ["def main"],
    "04_eda.py": ["# 1.", "# 2.", "# 3.", "# 4.", "# 5.", "# 6."],
    "05_sql_analysis.py": ["QUERIES = [", "lines = []", 'out = os.path.join'],
    "06_folium_maps.py": ["def haversine_km", "# ---- Map 1", "# ---- Map 2", "# ---- Map 3"],
    "07_dash_app.py": ["app = Dash(__name__)", "@app.callback"],
    "08_ml_models.py": ["PARAMS = {", "results, best_models", "best_name = max"],
}

DASH_FINAL = '''\
# Run the Dash app locally (uncomment, then open http://127.0.0.1:8050):
# app.run(host="127.0.0.1", port=8050, debug=False)

# Screenshots of the running app (All Sites + KSC LC 39A filtered):
from IPython.display import Image, display
display(Image("plots/dash_dashboard_all.png"))
display(Image("plots/dash_dashboard_ksc.png"))
'''


def transform(src):
    # make paths notebook-relative (repo root)
    src = re.sub(r'os\.path\.join\(os\.path\.dirname\(__file__\), "\.\.", ("(?:data|plots|maps|sql|models)")\)',
                 r'os.path.abspath(\1)', src)
    src = src.replace('os.path.join(os.path.dirname(__file__), "..")', 'os.path.abspath(".")')
    src = re.sub(r'# -\*- .*? -\*-\n', '', src)
    src = src.replace('sys.stdout.reconfigure(encoding="utf-8")\n', '')
    src = src.replace('import matplotlib\nmatplotlib.use("Agg")\n', '')
    src = src.replace('plt.close("all")\n', '')  # let inline backend display figures
    src = re.sub(r'os\.environ\.get\("SITE_FILTER", "ALL"\)', '"ALL"', src)
    return src


def extract_docstring(src):
    m = re.match(r'\s*"""(.*?)"""', src, re.S)
    if m:
        return m.group(1).strip(), src[m.end():].strip("\n")
    return None, src


def strip_main_guard(src):
    lines = src.split("\n")
    for i, l in enumerate(lines):
        if l.startswith('if __name__'):
            body = "\n".join(x[4:] for x in lines[i + 1:] if x.startswith("    "))
            body = body.replace('sys.stdout.reconfigure(encoding="utf-8")\n', '')
            return "\n".join(lines[:i]).rstrip() + "\n", body.strip()
    return src.rstrip() + "\n", None


def split_cells(src, anchors):
    lines = src.split("\n")
    cuts = []
    for i, l in enumerate(lines):
        for a in anchors:
            if l.startswith(a):
                cuts.append(i)
                break
    cuts = sorted(set(cuts))
    cells, prev = [], 0
    for c in cuts:
        seg = "\n".join(lines[prev:c]).strip("\n")
        if seg.strip():
            cells.append(seg)
        prev = c
    seg = "\n".join(lines[prev:]).strip("\n")
    if seg.strip():
        cells.append(seg)
    return cells


def build(script_name):
    src = open(os.path.join(SCRIPTS, script_name), encoding="utf-8").read()
    src = transform(src)
    doc, body = extract_docstring(src)
    guard_body = None
    if script_name in ("01_collect_data.py", "02_scrape_wikipedia.py", "03_clean_data.py"):
        body, guard_body = strip_main_guard(body)
    title, desc = INTROS[script_name]
    md = f"# {title}\n\n{desc}"
    if doc and doc.splitlines()[0].strip() != title.split(" - ")[0]:
        md += f"\n\n```text\n{doc}\n```"
    cells = [new_markdown_cell(md)]
    for c in split_cells(body, ANCHORS[script_name]):
        cells.append(new_code_cell(c))
    if script_name == "07_dash_app.py":
        cells.append(new_code_cell(DASH_FINAL))
    elif guard_body:
        cells.append(new_code_cell(guard_body))
    nb = new_notebook(cells=cells,
                      metadata={"kernelspec": {"display_name": "Python 3", "language": "python",
                                               "name": "python3"},
                                "language_info": {"name": "python"}})
    out = os.path.join(OUTDIR, script_name.replace("_", "_", 1).replace(".py", ".ipynb")
                       .replace("01_collect_data", "01_spacex_data_collection_api")
                       .replace("02_scrape_wikipedia", "02_spacex_data_collection_webscraping")
                       .replace("03_clean_data", "03_data_wrangling")
                       .replace("04_eda", "04_eda_dataviz")
                       .replace("05_sql_analysis", "05_eda_sql")
                       .replace("06_folium_maps", "06_folium_maps")
                       .replace("07_dash_app", "07_plotly_dash")
                       .replace("08_ml_models", "08_ml_prediction"))
    nbformat.write(nb, out)
    print("built:", os.path.basename(out), f"({len(cells)} cells)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for f in sorted(os.listdir(SCRIPTS)):
        if re.match(r"0[1-8]_", f):
            build(f)
