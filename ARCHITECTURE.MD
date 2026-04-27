# InsightForge: System Architecture
### An Autonomous AI System for End-to-End Data Analysis
*

---

## 1. Overview

InsightForge is a unified, autonomous data analysis platform that takes raw structured datasets (CSV/Excel) as input and produces meaningful insights, predictive models, and interactive visualizations — with minimal human intervention. The system is designed for both technical and non-technical users, incorporating NLP-based query interaction, automated ML pipelines, and a modular web-based interface.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                  │
│         Web Browser (Chrome / Edge) — HTML, CSS, JavaScript        │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTP / REST API
┌────────────────────────────▼────────────────────────────────────────┐
│                     FRONTEND LAYER                                  │
│   - Dataset Upload UI        - Results Dashboard                    │
│   - NLP Query Interface      - Chart & Report Viewer                │
│   - Analysis Configuration   - Model Performance Panel             │
└────────────────────────────┬────────────────────────────────────────┘
                             │  REST API (JSON)
┌────────────────────────────▼────────────────────────────────────────┐
│                     BACKEND LAYER  (Django / Flask)                 │
│   - API Gateway              - Session & Auth Manager               │
│   - Request Router           - File Handler                         │
│   - Task Queue (Celery)      - Response Formatter                   │
└───┬────────────┬─────────────┬───────────────┬───────────────┬──────┘
    │            │             │               │               │
┌───▼──┐  ┌─────▼────┐  ┌─────▼──────┐  ┌────▼─────┐  ┌─────▼─────┐
│ Pre- │  │Analytical│  │  ML Model  │  │  Visual- │  │   NLP     │
│proce-│  │  Engine  │  │  Training  │  │  ization │  │  Query    │
│ssing │  │          │  │  & Eval    │  │  Module  │  │  Engine   │
│Module│  │          │  │            │  │          │  │           │
└───┬──┘  └─────┬────┘  └─────┬──────┘  └────┬─────┘  └─────┬─────┘
    └────────────┴─────────────┴───────────────┴──────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                     DATA LAYER                                      │
│   - Uploaded Dataset Storage    - Model Artifact Store              │
│   - SQLite / MySQL / Firebase   - JSON / CSV Cache                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module-by-Module Architecture

### 3.1 Frontend Layer

**Technology Stack:** HTML5, CSS3, JavaScript (vanilla or lightweight framework)

| Component | Description |
|---|---|
| **Upload Panel** | Drag-and-drop or file-picker for CSV/Excel datasets |
| **NLP Query Box** | Free-text input for natural language data queries |
| **Analysis Dashboard** | Displays preprocessing summary, selected model, and metrics |
| **Visualization Panel** | Renders charts, plots, and summary reports dynamically |
| **Model Results View** | Shows accuracy, confusion matrix, regression scores, etc. |

**Communication:** All frontend components communicate with the backend via RESTful API calls (JSON format).

---

### 3.2 Backend Layer (API & Orchestration)

**Technology Stack:** Python, Django or Flask, Celery (task queue), REST APIs

```
Client Request
      │
      ▼
 API Gateway
      │
      ├──► /upload          → File Handler → Preprocessing Module
      ├──► /analyze         → Analytical Engine → ML Pipeline
      ├──► /query           → NLP Engine → Data Query Handler
      ├──► /visualize       → Visualization Module
      └──► /results         → Response Formatter → Client
```

**Key Responsibilities:**
- Receive and validate uploaded files
- Route requests to appropriate processing modules
- Manage asynchronous long-running tasks (model training) via Celery
- Format and return structured JSON responses to the frontend

---

### 3.3 Preprocessing Module

**Technology Stack:** Python, Pandas, NumPy

```
Raw Dataset Input (CSV / Excel)
        │
        ▼
┌───────────────────────────────────────┐
│         Preprocessing Pipeline        │
│                                       │
│  1. File Parser & Schema Detector     │
│     └─ Detect column types, dtypes   │
│                                       │
│  2. Missing Value Handler             │
│     ├─ Mean/Median imputation         │
│     └─ Row/column drop (threshold)   │
│                                       │
│  3. Duplicate Remover                 │
│                                       │
│  4. Outlier Detector                  │
│     └─ IQR / Z-score method          │
│                                       │
│  5. Data Type Normalizer              │
│     └─ Parse dates, encode strings   │
│                                       │
│  6. Feature Encoder                   │
│     ├─ Label Encoding                 │
│     └─ One-Hot Encoding               │
│                                       │
│  7. Feature Scaler                    │
│     ├─ StandardScaler                 │
│     └─ MinMaxScaler                   │
│                                       │
│  8. Preprocessing Report Generator   │
└──────────────────┬────────────────────┘
                   │
                   ▼
         Clean, Structured Dataset
```

**Output:** A cleaned, encoded, and normalized DataFrame ready for analysis + a preprocessing summary report.

---

### 3.4 Analytical Engine

**Technology Stack:** Python, Scikit-learn, Pandas

```
Clean Dataset
      │
      ▼
┌─────────────────────────────────┐
│   Dataset Nature Detector       │
│                                 │
│   Checks:                       │
│   - Target column present?      │
│   - Target dtype (numeric /     │
│     categorical)?               │
│   - Number of unique labels?    │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
Classification    Regression       (Clustering if no target)
     │                │
     ▼                ▼
Multiple Models  Multiple Models
- Logistic Reg   - Linear Reg
- Decision Tree  - Ridge / Lasso
- Random Forest  - Decision Tree
- SVM            - Random Forest
- KNN            - SVR
     │                │
     └───────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Model Evaluator  │
    │                 │
    │ Classification: │
    │  Accuracy, F1,  │
    │  Precision,     │
    │  Recall, ROC    │
    │                 │
    │ Regression:     │
    │  MAE, MSE,      │
    │  RMSE, R²       │
    │                 │
    │ Clustering:     │
    │  Silhouette,    │
    │  Inertia        │
    └────────┬────────┘
             │
             ▼
     Best Model Selected
     & Saved as Artifact
```

---

### 3.5 ML Model Training & Evaluation Module

**Technology Stack:** Python, Scikit-learn, TensorFlow/Keras (advanced), Joblib

```
Selected Algorithm + Clean Data
            │
            ▼
   Train/Test Split (80/20)
            │
            ├──► Training Set → Model.fit()
            │
            └──► Test Set → Model.predict()
                               │
                               ▼
                      Metrics Computation
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Cross-Validation    │
                    │  (K-Fold, k=5)       │
                    └──────────┬───────────┘
                               │
                               ▼
                    Model Serialization
                    (joblib / pickle)
                    Saved to Artifact Store
```

---

### 3.6 Visualization Module

**Technology Stack:** Python, Matplotlib, Seaborn; JavaScript chart rendering on frontend

| Plot Type | Trigger Condition |
|---|---|
| Histogram / Distribution Plot | Numeric feature exploration |
| Correlation Heatmap | Multi-feature dataset |
| Bar / Pie Chart | Categorical target analysis |
| Scatter Plot | Regression tasks |
| Confusion Matrix Heatmap | Classification results |
| ROC Curve | Binary classification |
| Feature Importance Bar Chart | Tree-based models |
| Cluster Scatter Plot | Clustering tasks |
| Pairplot | Exploratory data analysis |

**Output:** Charts are generated server-side (Matplotlib/Seaborn) as PNG/SVG, sent to frontend, and rendered inline in the dashboard.

---

### 3.7 NLP Query Engine

**Technology Stack:** Python, spaCy or basic NLP libraries, keyword mapping

```
User Natural Language Query
           │
           ▼
   Query Preprocessor
   (tokenize, lowercase,
    remove stopwords)
           │
           ▼
   Intent Classifier
   ┌────────────────────────┐
   │ Intents:               │
   │ - summarize_data       │
   │ - filter_data          │
   │ - plot_column          │
   │ - find_correlation     │
   │ - predict_value        │
   │ - compare_columns      │
   └─────────┬──────────────┘
             │
             ▼
   Entity Extractor
   (column names, operators,
    values, aggregations)
             │
             ▼
   Query Executor
   (maps to Pandas operations
    or triggers analysis module)
             │
             ▼
   Result → Visualization or
            Text Response
```

---

### 3.8 Data Layer

```
┌───────────────────────────────────────────────────────┐
│                     DATA LAYER                        │
│                                                       │
│  ┌─────────────────┐    ┌──────────────────────────┐  │
│  │  File Storage    │    │   Database (SQLite /     │  │
│  │                 │    │   MySQL / Firebase)       │  │
│  │  /uploads/      │    │                          │  │
│  │  - raw CSVs     │    │  Tables:                 │  │
│  │  - Excel files  │    │  - users (optional auth) │  │
│  │                 │    │  - upload_sessions       │  │
│  │  /models/       │    │  - analysis_results      │  │
│  │  - .pkl files   │    │  - query_logs            │  │
│  │  - .joblib      │    │                          │  │
│  │                 │    │                          │  │
│  │  /outputs/      │    │                          │  │
│  │  - charts/      │    │                          │  │
│  │  - reports/     │    │                          │  │
│  └─────────────────┘    └──────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

---

## 4. Complete Data Flow

```
User uploads CSV
      │
      ▼
File validated & stored
      │
      ▼
Preprocessing Module runs
  → Clean dataset produced
  → Preprocessing report generated
      │
      ▼
Analytical Engine detects problem type
  → Selects candidate algorithms
      │
      ▼
ML Module trains & evaluates models
  → Best model selected & serialized
      │
      ▼
Visualization Module generates charts
      │
      ▼
Results sent to Frontend Dashboard
  → Metrics, charts, summary displayed
      │
      ▼
User queries data via NLP box (optional)
  → NLP Engine processes query
  → Returns answer / new chart
```

---

## 5. API Endpoint Design

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload a CSV/Excel file |
| GET | `/api/preview/<session_id>` | Get first N rows of uploaded dataset |
| POST | `/api/preprocess/<session_id>` | Trigger preprocessing pipeline |
| POST | `/api/analyze/<session_id>` | Run analytical engine + model training |
| GET | `/api/results/<session_id>` | Fetch model metrics and evaluation |
| GET | `/api/visualize/<session_id>` | Fetch generated charts |
| POST | `/api/query/<session_id>` | Submit NLP query |
| GET | `/api/report/<session_id>` | Download full analysis report (PDF/JSON) |

---

## 6. Technology Stack Summary

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend Framework** | Python, Django / Flask |
| **Task Queue** | Celery + Redis (for async model training) |
| **ML Libraries** | Scikit-learn, TensorFlow / Keras |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **NLP** | spaCy / NLTK / keyword matching |
| **Database** | SQLite (dev) / MySQL / Firebase (prod) |
| **Version Control** | Git & GitHub |
| **IDE** | VS Code / PyCharm |
| **Additional Tools** | Jupyter Notebook, REST APIs, JSON/CSV |

---

## 7. Scalability & Modularity

Each of the five core modules (Preprocessing, Analytical Engine, ML Training, Visualization, NLP) is designed as an **independent, swappable component**:

- New ML algorithms can be plugged into the Analytical Engine without touching other modules.
- The NLP Engine can be upgraded from keyword-matching to a full LLM-based interface in a future version.
- The Visualization Module can be extended to support D3.js or Plotly for interactive web charts.
- Real-time data source connectors (APIs, databases) can be added to the Data Layer.

---

## 8. Current Scope Boundaries

The following are **outside** the current project scope (academic prototype):

- Unstructured data (images, audio, text documents)
- Large-scale distributed computing
- Complex deep learning architectures
- Real-time streaming data
- Multi-user authentication and enterprise deployment

---

## 9. Future Enhancements

- Integration of LLM (e.g., GPT / Claude API) for advanced NLP queries
- Real-time dataset streaming support
- AutoML with hyperparameter tuning (GridSearchCV / Optuna)
- Explainability layer using SHAP / LIME
- Export of full analysis as downloadable PDF report
- Support for unstructured data modalities

