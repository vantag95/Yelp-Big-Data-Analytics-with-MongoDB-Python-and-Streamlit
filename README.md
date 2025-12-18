# Yelp Big Data Analytics with MongoDB, Python, and Streamlit

This project builds an end-to-end Big Data analytics pipeline on top of a 1,000,000-row Yelp-style dataset.
The goal is to help users **find and recommend the best organizations** using ratings, review counts, and location information stored and processed in a realistic Big Data stack.

---

## 1. Project Overview

- **Objective:**
Transform a large raw CSV (`yelp_database.csv`) into clean, reliable, and aggregated data inside MongoDB, and present insights through an interactive Streamlit dashboard.

- **Key Questions:**
- Which cities and states have the highest average ratings?
- Where are there many organizations with strong ratings and many reviews?
- How can users quickly discover and recommend the best services?

- **Tech Stack:**
- **Big Data Platform:** MongoDB (single-node) running in Docker Compose
- **Processing:** Python, uv, pandas, Pydantic, pymongo
- **Visualization:** Streamlit
- **Dev Tools:** pytest, mypy, loguru

---

## 2. Dataset

- **File:** `yelp_database.csv`
- **Size:** 1,000,000 rows (satisfies the “≥ 750k rows” requirement)
- **Format:** CSV
- **Columns (14):**
- `ID`
- `Time_GMT`
- `Phone`
- `Organization`
- `OLF`
- `Rating`
- `NumberReview`
- `Category`
- `Country`
- `CountryCode`
- `State`
- `City`
- `Street`
- `Building`

Each row represents an organization/business with metadata, rating, review count, and location attributes.

---

## 3. Architecture

This project follows a layered data architecture:

- **Raw Layer:** `yelp_raw` collection in MongoDB
Raw documents are loaded directly from the CSV.

- **Clean Layer:** `yelp_clean` collection
Data is validated and cleaned using Pydantic (`YelpRecord` model), handling missing values, text normalization, type conversion, and basic date parsing.

- **Aggregated (Gold) Layer:** `agg_city`, `agg_state` collections
Aggregations compute metrics such as average rating and number of organizations per city and per state.
These gold tables are used by the dashboard.

### Architecture Diagram

flowchart LR
A[CSV: yelp_database.csv
1,000,000 rows] --> B[Python Ingestion
ingest.py]
B --> C[(MongoDB - yelp_raw
Docker Compose, single-node)]
C --> D[Cleaning + Validation
clean.py + Pydantic]
D --> E[(MongoDB - yelp_clean)]
E --> F[Aggregations
aggregate.py]
F --> G[(MongoDB - agg_city, agg_state)]
G --> H[Streamlit Dashboard
app.py]

<img width="1758" height="341" alt="Screenshot 2025-12-17 195440" src="https://github.com/user-attachments/assets/b65e8a7d-67f2-4202-9496-20d7b63695ac" />



- **Cluster structure:**
Single-node MongoDB instance running as a container via Docker Compose (no replica set or sharding, but can be extended).

---

## 4. Environment & Setup

### 4.1 Prerequisites

- Docker & Docker Compose
- Python 3.11+
- `uv` package manager

### 4.2 Clone and prepare

git clone <your-repo-url>.git
cd biddata_project


### 4.3 Project Structure

biddata_project/
docker-compose.yml
pyproject.toml
yelp_database.csv
src/
bigdata_project/
init.py
ingest.py
clean.py
aggregate.py
app.py
tests/
test_sample.py # (optional simple pytest tests)
README.md


---

## 5. Pipeline: Raw → Clean → Aggregated

### 5.1 Ingestion (Raw Layer)

**File:** `src/bigdata_project/ingest.py`

Responsibilities:

- Read `yelp_database.csv` with pandas.
- Convert each row to a Python dictionary.
- Insert all rows into MongoDB collection `yelp_raw`.
- Print:
- `Loaded rows from file: ...`
- `Raw row count in Mongo: ...`

Run:

uv run python src/bigdata_project/ingest.py


### 5.2 Cleaning & Validation (Clean Layer)

**File:** `src/bigdata_project/clean.py`

Responsibilities:

- Define a Pydantic model `YelpRecord` matching the real columns:

ID, Time_GMT, Phone, Organization, OLF, Rating,
NumberReview, Category, Country, CountryCode,
State, City, Street, Building


- Normalize text fields (`Organization`, `Category`, `Country`, `State`, `City`, `Street`, `Building`).
- Convert `Rating` to `float`, `NumberReview` to `int`.
- Attempt to parse `Time_GMT` into `datetime`, handling failures.
- Skip invalid rows and insert valid, cleaned documents into `yelp_clean`.
- Print:
- `Raw docs read from Mongo: ...`
- `Clean row count in Mongo: ...`

Run:

uv run python src/bigdata_project/clean.py


### 5.3 Aggregations (Gold Layer)

**File:** `src/bigdata_project/aggregate.py`

Responsibilities:

- `aggregate_by_city`:
- Filter out rows with missing `City`.
- Group by `City`.
- Compute:
- `avg_rating` = average of `Rating`
- `count` = number of organizations in the city
- Write to `agg_city`.

- `aggregate_by_state`:
- Similar logic grouped by `State`.
- Write to `agg_state`.

- Print:
- `agg_city documents: ...`
- `agg_state documents: ...`
- `Aggregations complete.`

Run:

uv run python src/bigdata_project/aggregate.py


---

## 6. Streamlit Dashboard

**File:** `src/bigdata_project/app.py`

The dashboard connects directly to MongoDB (`agg_city`, `agg_state`) and provides three main views.

### 6.1 Running the App

uv run streamlit run src/bigdata_project/app.py

1) Start MongoDB
docker compose up -d

2) Install dependencies
uv sync

3) Run pipeline
uv run python src/bigdata_project/ingest.py
uv run python src/bigdata_project/clean.py
uv run python src/bigdata_project/aggregate.py

4) Launch dashboard
uv run streamlit run src/bigdata_project/app.py


---

## 7. What This Project Demonstrates

- Using Docker Compose to run MongoDB as a Big Data platform.
- Designing a three-layer data pipeline (raw, clean, gold) for a million-row dataset.
- Applying Pydantic for schema validation and data cleaning.
- Building MongoDB aggregation pipelines for analytic queries.
- Creating an interactive Streamlit dashboard that reads directly from MongoDB aggregated collections.
- Managing a Python project with uv, including dependencies, structure, and dev tools.

This shows a realistic end-to-end Big Data workflow where raw data becomes actionable insights that help users **discover and recommend the best organizations** based on ratings, reviews, and location.
