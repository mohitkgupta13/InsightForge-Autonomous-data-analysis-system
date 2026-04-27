# InsightForge — Autonomous Data Analysis System

> Upload a CSV. Get insights, models, charts, and natural language queries — automatically.

[![Branch](https://img.shields.io/badge/branch-v0-e94560?style=flat-square)](https://github.com/mohitkgupta13/InsightForge-Autonomous-data-analysis-system)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)]()
[![Flask](https://img.shields.io/badge/backend-Flask-green?style=flat-square)]()

---

## What is InsightForge?

InsightForge is an **autonomous, end-to-end data analysis platform** built for both technical and non-technical users. You upload a structured dataset (CSV or Excel) and the system:

1. **Preprocesses** it automatically — handles missing values, removes duplicates, detects outliers, encodes categoricals, and scales features.
2. **Detects the problem type** — Classification, Regression, or Clustering — based on the target column.
3. **Trains multiple ML models** and selects the best one by primary metric (Accuracy, R², or Silhouette Score).
4. **Generates visualizations** — histograms, correlation heatmaps, confusion matrices, ROC curves, feature importance plots, cluster scatter plots, and more.
5. **Answers natural language questions** about your data — filter rows, aggregate columns, plot distributions, find correlations.
6. **Produces a downloadable JSON report** summarising the entire analysis.

---

## Project Structure

```
insightforge/
├── backend/                    # Flask API
│   ├── app.py                  # Entry point — all blueprints registered here
│   ├── config.py               # Paths, allowed extensions, DB URI
│   ├── database.py             # SQLite schema + CRUD helpers
│   ├── requirements.txt        # Python dependencies
│   ├── preprocessing/
│   │   └── pipeline.py         # 8-step PreprocessingPipeline class
│   ├── analytics/
│   │   ├── detector.py         # DatasetAnalyzer — auto problem-type detection
│   │   ├── classifiers.py      # 5 classifiers + metrics
│   │   ├── regressors.py       # 5 regressors + metrics
│   │   ├── clustering.py       # K-Means + elbow method
│   │   └── model_selector.py   # Best model selection + joblib serialization
│   ├── visualization/
│   │   ├── chart_generator.py  # 9 chart types (Matplotlib/Seaborn)
│   │   └── manager.py          # Auto-select charts by problem type
│   ├── nlp/
│   │   ├── intent_classifier.py  # Keyword-based intent detection
│   │   ├── entity_extractor.py   # Column, operator, value extraction
│   │   └── query_executor.py     # Pandas operations from NL queries
│   ├── routes/
│   │   ├── upload.py           # POST /api/upload
│   │   ├── preview.py          # GET  /api/preview/<session_id>
│   │   ├── preprocess.py       # POST /api/preprocess/<session_id>
│   │   ├── analyze.py          # POST /api/analyze/<session_id>
│   │   ├── results.py          # GET  /api/results/<session_id>
│   │   ├── visualize.py        # GET  /api/visualize/<session_id>
│   │   ├── query.py            # POST /api/query/<session_id>
│   │   └── report.py           # GET  /api/report/<session_id>
│   └── models_store/           # Saved .joblib model artifacts
├── frontend/                   # Vanilla HTML/CSS/JS SPA
│   ├── index.html
│   └── static/
│       ├── css/style.css       # Dark-mode premium design system
│       └── js/
│           ├── api.js          # fetch() wrappers for all endpoints
│           └── app.js          # 7-step SPA logic
├── data/
│   ├── uploads/                # Raw uploaded files
│   └── outputs/
│       └── charts/             # Generated PNG charts
├── tests/
│   └── test_preprocessing.py   # Unit tests (pytest)
├── ARCHITECTURE.MD             # System architecture document
├── PLAN.MD                     # Phase-by-phase development roadmap
└── PROGRESS.MD                 # Live implementation progress tracker
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload CSV/Excel — returns `session_id` |
| `GET`  | `/api/preview/<session_id>` | First N rows + column info |
| `POST` | `/api/preprocess/<session_id>` | Run preprocessing pipeline |
| `POST` | `/api/analyze/<session_id>` | Detect problem type + train models |
| `GET`  | `/api/results/<session_id>` | Fetch stored model metrics |
| `GET`  | `/api/visualize/<session_id>` | Generate + return all charts (Base64) |
| `POST` | `/api/query/<session_id>` | Natural language data query |
| `GET`  | `/api/report/<session_id>` | Full JSON analysis report |

---

## Setup & Installation

Please refer to our **[Setup Guide (SETUP.md)](SETUP.md)** for simple, step-by-step instructions on how to install and run InsightForge locally.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (Vanilla), JavaScript |
| Backend | Python 3.10+, Flask 3.0 |
| Data Processing | Pandas, NumPy, SciPy |
| Machine Learning | Scikit-learn |
| Visualization | Matplotlib, Seaborn |
| NLP | Keyword-based intent/entity engine |
| Database | SQLite |
| Model Storage | Joblib |

---

## Team

| Member | Module |
|---|---|
| M Kavana Reddy | Preprocessing Module + Data Layer |
| **Mohit Kumar Gupta** | Analytical Engine + ML Pipeline |
| Sahana N S | Visualization + NLP Engine |
| Yuktha Reddy B K | Frontend UI + Backend API |

**Guide:** Dr. S Krishna Anand

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, reviewed code |
| `v0` | Active development — full clean-slate implementation |

---

*InsightForge — Turning raw data into autonomous insight.*
