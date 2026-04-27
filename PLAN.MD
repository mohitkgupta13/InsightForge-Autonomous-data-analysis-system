# InsightForge: Complete Project Plan
### Phase-by-Phase Development Roadmap


---

## Project Timeline at a Glance

| Phase | Name | Duration | Key Deliverable |
|---|---|---|---|
| Phase 1 | Planning & Setup | Week 1–2 | Project structure, tools ready |
| Phase 2 | Data Layer & Preprocessing | Week 3–5 | Working preprocessing pipeline |
| Phase 3 | Analytical Engine & ML Pipeline | Week 6–9 | Auto model selection & evaluation |
| Phase 4 | Visualization Module | Week 10–11 | Chart generation system |
| Phase 5 | NLP Query Engine | Week 12–13 | Natural language data querying |
| Phase 6 | Backend API & Integration | Week 14–15 | All modules wired via REST API |
| Phase 7 | Frontend UI Development | Week 16–17 | Complete web interface |
| Phase 8 | Testing & Debugging | Week 18–19 | Bug-free, tested system |
| Phase 9 | Documentation & Report | Week 20–21 | Final report + demo |
| Phase 10 | Final Review & Submission | Week 22 | Project submission |

**Total Duration: ~22 Weeks**

---

## Phase 1: Planning & Environment Setup
**Duration:** Week 1–2

### Goals
Set up the development environment, finalize team responsibilities, and establish the project repository structure.

### Tasks

**Week 1 — Planning**
- Finalize system architecture (refer `architecture.md`)
- Divide modules among team members:
  - Member 1 (M Kavana Reddy): Preprocessing Module + Data Layer
  - Member 2 (Mohit Kumar Gupta): Analytical Engine + ML Pipeline
  - Member 3 (Sahana N S): Visualization Module + NLP Engine
  - Member 4 (Yuktha Reddy B K): Frontend UI + Backend API Integration
- Create GitHub repository with branch strategy (`main`, `dev`, `feature/module-name`)
- Define coding standards and commit conventions

**Week 2 — Setup**
- Install all required tools and libraries:
  ```
  Python 3.10+, pip, virtualenv
  Django / Flask
  pandas, numpy, scikit-learn, matplotlib, seaborn
  spacy / nltk
  tensorflow / keras (optional advanced)
  celery, redis (for task queue)
  git, VS Code / PyCharm
  ```
- Set up project folder structure:
  ```
  insightforge/
  ├── backend/
  │   ├── api/
  │   ├── preprocessing/
  │   ├── analytics/
  │   ├── visualization/
  │   ├── nlp/
  │   └── models_store/
  ├── frontend/
  │   ├── templates/
  │   ├── static/
  │   │   ├── css/
  │   │   └── js/
  ├── data/
  │   ├── uploads/
  │   └── outputs/
  ├── tests/
  ├── docs/
  ├── requirements.txt
  └── README.md
  ```
- Initialize database schema (SQLite for development)
- Create a "Hello World" Flask/Django app to verify setup

### Deliverables
- [ ] GitHub repo initialized with all branches
- [ ] Development environment working on all team machines
- [ ] `requirements.txt` finalized
- [ ] Task assignment sheet signed off by guide

---

## Phase 2: Data Layer & Preprocessing Module
**Duration:** Week 3–5

### Goals
Build the complete data ingestion and preprocessing pipeline — the foundation that all other modules depend on.

### Tasks

**Week 3 — File Ingestion & Schema Detection**
- Build file upload handler (accept `.csv` and `.xlsx`)
- Parse uploaded file using Pandas
- Detect and report:
  - Column names and data types
  - Number of rows and columns
  - Count of missing values per column
  - Count of duplicate rows
- Generate a "Dataset Summary" JSON object
- Store raw file in `/data/uploads/`

**Week 4 — Cleaning Pipeline**
- Implement each preprocessing step as a separate function:
  ```python
  handle_missing_values(df, strategy='mean')
  remove_duplicates(df)
  detect_outliers(df, method='iqr')
  encode_categoricals(df, method='onehot')
  scale_features(df, method='standard')
  ```
- Build a `PreprocessingPipeline` class that chains these steps
- Allow basic configuration (e.g., choose imputation strategy)
- Store cleaned dataset as a new CSV in `/data/outputs/`

**Week 5 — Preprocessing Report & Testing**
- Auto-generate a preprocessing summary report:
  - Original shape vs. cleaned shape
  - Columns dropped / imputed
  - Encoding applied
  - Scaling applied
- Write unit tests for each preprocessing function using sample datasets:
  - Dataset with all missing values
  - Dataset with all duplicates
  - Dataset with mixed data types
- Test with at least 3 real-world CSV datasets (e.g., Titanic, Iris, Housing)

### Deliverables
- [ ] `preprocessing/pipeline.py` — complete and tested
- [ ] Preprocessing summary report generated as JSON
- [ ] Unit tests passing for all preprocessing functions
- [ ] Cleaned datasets saved correctly to output directory

---

## Phase 3: Analytical Engine & ML Pipeline
**Duration:** Week 6–9

### Goals
Build the intelligent core of InsightForge — automatic problem-type detection, model selection, training, and evaluation.

### Tasks

**Week 6 — Problem Type Detector**
- Build `DatasetAnalyzer` class:
  - If no target column → suggest Clustering
  - If target column is numeric → Regression
  - If target column is categorical → Classification
- Let user optionally specify or confirm the target column via API
- Auto-select top 3–5 candidate algorithms based on problem type

**Week 7 — Classification Pipeline**
- Implement training for the following classifiers:
  - Logistic Regression
  - Decision Tree Classifier
  - Random Forest Classifier
  - Support Vector Machine (SVM)
  - K-Nearest Neighbors (KNN)
- For each model, compute:
  - Accuracy, Precision, Recall, F1-Score
  - Confusion Matrix
  - ROC-AUC (for binary classification)
- Use 80/20 train-test split + 5-Fold Cross Validation

**Week 8 — Regression & Clustering Pipeline**
- Implement training for the following regressors:
  - Linear Regression
  - Ridge / Lasso Regression
  - Decision Tree Regressor
  - Random Forest Regressor
  - Support Vector Regressor (SVR)
- Compute: MAE, MSE, RMSE, R² Score
- Implement clustering (when no target column):
  - K-Means Clustering
  - Auto-detect optimal K using Elbow Method
  - Compute Silhouette Score

**Week 9 — Model Selection & Serialization**
- Build `ModelSelector` class:
  - Ranks all trained models by primary metric (Accuracy / R² / Silhouette)
  - Selects and returns the best model
- Serialize best model using `joblib` to `/backend/models_store/`
- Store results (all model metrics) as JSON for frontend consumption
- Write integration tests: feed cleaned dataset → get best model + metrics

### Deliverables
- [ ] `analytics/detector.py` — problem type detection
- [ ] `analytics/classifiers.py` — all classifiers trained & evaluated
- [ ] `analytics/regressors.py` — all regressors trained & evaluated
- [ ] `analytics/clustering.py` — K-Means with elbow method
- [ ] `analytics/model_selector.py` — best model selection logic
- [ ] Best model serialized and retrievable
- [ ] All metrics returned as structured JSON

---

## Phase 4: Visualization Module
**Duration:** Week 10–11

### Goals
Build the chart and plot generation system that turns raw results into clear, interpretable graphics.

### Tasks

**Week 10 — Core Chart Functions**
- Implement the following plot generators using Matplotlib and Seaborn:

  | Function | When Generated |
  |---|---|
  | `plot_distribution(col)` | For every numeric column |
  | `plot_correlation_heatmap(df)` | Multi-feature datasets |
  | `plot_bar_chart(col)` | Categorical columns |
  | `plot_scatter(x, y)` | Regression tasks |
  | `plot_confusion_matrix(cm)` | Classification results |
  | `plot_roc_curve(fpr, tpr)` | Binary classification |
  | `plot_feature_importance(model)` | Tree-based models |
  | `plot_elbow_curve(k, inertia)` | Clustering tasks |
  | `plot_cluster_scatter(df)` | After K-Means |

- Save all plots as `.png` files to `/data/outputs/charts/`
- Build a `VisualizationManager` class that auto-selects which plots to generate based on problem type

**Week 11 — Integration & Optimization**
- Convert generated PNGs to Base64 strings for easy API transfer
- Build API endpoint to serve charts to frontend
- Ensure all chart filenames are session-scoped (no overwrites between users)
- Test visualization output with classification, regression, and clustering datasets

### Deliverables
- [ ] `visualization/chart_generator.py` — all chart functions implemented
- [ ] `visualization/manager.py` — auto-selection logic
- [ ] Charts saved and retrievable per session
- [ ] API endpoint `/api/visualize/<session_id>` working

---

## Phase 5: NLP Query Engine
**Duration:** Week 12–13

### Goals
Allow users to query their dataset in plain English without writing code or knowing SQL.

### Tasks

**Week 12 — Intent & Entity Recognition**
- Define a set of supported query intents:
  ```
  summarize     → "Show me a summary of the dataset"
  filter        → "Show rows where Age > 30"
  plot          → "Plot the distribution of Salary"
  correlate     → "What columns are correlated with Price?"
  aggregate     → "What is the average Income by City?"
  predict       → "Predict the value for a new data point"
  top_n         → "Show top 5 rows by Sales"
  ```
- Build a keyword-based intent classifier
- Build an entity extractor to pull:
  - Column names (matched against actual dataset columns)
  - Operators (`>`, `<`, `=`, `contains`)
  - Values and aggregation types

**Week 13 — Query Executor & Response**
- Map each intent to a Pandas operation or module call:
  ```python
  "filter"    → df[df[col] > value]
  "plot"      → VisualizationManager.plot_distribution(col)
  "aggregate" → df.groupby(group_col)[agg_col].mean()
  "predict"   → load_model().predict(input_values)
  ```
- Return results as:
  - Text (for summaries and aggregations)
  - Chart (for plot requests)
  - Table (for filter/top-N results)
- Handle unrecognized queries gracefully with a helpful error message
- Write test cases for at least 10 different query types

### Deliverables
- [ ] `nlp/intent_classifier.py` — intent detection
- [ ] `nlp/entity_extractor.py` — column, operator, value extraction
- [ ] `nlp/query_executor.py` — Pandas mapping and execution
- [ ] API endpoint `/api/query/<session_id>` working
- [ ] 10+ query types tested and passing

---

## Phase 6: Backend API & Module Integration
**Duration:** Week 14–15

### Goals
Wire all five modules together through a clean REST API, implement session management, and ensure end-to-end data flow works correctly.

### Tasks

**Week 14 — API Development**
- Build all REST API endpoints using Django/Flask:

  | Method | Endpoint | Module Called |
  |---|---|---|
  | POST | `/api/upload` | File Handler |
  | GET | `/api/preview/<id>` | Data Layer |
  | POST | `/api/preprocess/<id>` | Preprocessing Module |
  | POST | `/api/analyze/<id>` | Analytical Engine |
  | GET | `/api/results/<id>` | ML Pipeline |
  | GET | `/api/visualize/<id>` | Visualization Module |
  | POST | `/api/query/<id>` | NLP Engine |
  | GET | `/api/report/<id>` | Report Generator |

- Implement session ID generation on file upload
- All endpoints return structured JSON responses:
  ```json
  {
    "status": "success",
    "session_id": "abc123",
    "data": { ... }
  }
  ```

**Week 15 — Integration Testing**
- Run a complete end-to-end test:
  - Upload CSV → Preprocess → Analyze → Get Results → Visualize → Query
- Fix any data contract mismatches between modules
- Set up Celery + Redis for async model training (prevents timeout on large datasets)
- Implement basic error handling and validation on all endpoints
- Test with at least 5 different datasets of varying sizes and types

### Deliverables
- [ ] All 8 API endpoints implemented and returning correct responses
- [ ] Session management working (each upload gets a unique session)
- [ ] End-to-end flow tested successfully with 5 datasets
- [ ] Async task queue working for model training
- [ ] Error handling on all endpoints

---

## Phase 7: Frontend UI Development
**Duration:** Week 16–17

### Goals
Build the complete web interface that makes InsightForge accessible and intuitive for non-technical users.

### Tasks

**Week 16 — Core UI Pages**
- Build the following pages/views:

  **Home / Upload Page**
  - Drag-and-drop file upload area
  - Dataset preview table (first 10 rows)
  - "Start Analysis" button

  **Preprocessing View**
  - Show preprocessing summary (missing values handled, shape changes)
  - Allow user to confirm or adjust settings

  **Analysis Dashboard**
  - Display detected problem type (Classification / Regression / Clustering)
  - Show all models tried + their metrics in a comparison table
  - Highlight the best model with its performance score

**Week 17 — Charts, NLP & Polish**
  **Visualization Panel**
  - Render all generated charts inline
  - Allow toggling between different chart types

  **NLP Query Interface**
  - Text input box with example queries shown
  - Display result (text / chart / table) below the input

  **Report Section**
  - Show full analysis summary
  - Download button for JSON report

- Apply consistent styling (red and white theme matching college branding)
- Make the layout responsive for different screen sizes
- Connect all UI components to backend API endpoints

### Deliverables
- [ ] All pages built and connected to API
- [ ] File upload → preview working in browser
- [ ] Analysis results rendered correctly
- [ ] Charts displayed inline
- [ ] NLP query box functional
- [ ] UI tested on Chrome and Edge

---

## Phase 8: Testing & Debugging
**Duration:** Week 18–19

### Goals
Thoroughly test the entire system, find and fix bugs, and ensure reliability across diverse datasets.

### Testing Strategy

**Week 18 — Functional Testing**

| Test Type | What to Test |
|---|---|
| Unit Tests | Each function in each module |
| Integration Tests | Module-to-module data flow |
| API Tests | Every endpoint with valid and invalid inputs |
| UI Tests | All pages and interactions in browser |

- Test datasets to use:
  - **Iris Dataset** — Classification (small, clean)
  - **Titanic Dataset** — Classification (missing values, mixed types)
  - **Boston Housing** — Regression
  - **Mall Customer Dataset** — Clustering
  - **Custom synthetic dataset** — Edge cases (all nulls, single column, etc.)

**Week 19 — Bug Fixes & Edge Cases**
- Handle edge cases:
  - Dataset with only 1 column
  - Dataset with 100% missing values in a column
  - Non-UTF-8 encoded CSV files
  - Very large files (>10MB)
  - NLP query with completely unrecognized words
- Performance testing: measure time taken for preprocessing and training on datasets of 1K, 10K, and 100K rows
- Fix all identified bugs
- Re-run all tests after fixes

### Deliverables
- [ ] Unit test coverage > 80% across all modules
- [ ] All 5 test datasets producing correct outputs
- [ ] Edge cases handled gracefully (no crashes)
- [ ] Performance benchmarks recorded
- [ ] Zero critical bugs remaining

---

## Phase 9: Documentation & Report Writing
**Duration:** Week 20–21

### Goals
Complete all project documentation, finalize the project report, and prepare demo materials.

### Tasks

**Week 20 — Technical Documentation**
- Write `README.md` with:
  - Project overview
  - Installation instructions
  - How to run the system
  - API documentation
- Update `architecture.md` with any changes made during development
- Document all module APIs (functions, parameters, return values)
- Write a user guide (how to upload a dataset and interpret results)
- Record a short demo video (3–5 minutes) showing end-to-end usage

**Week 21 — Final Project Report**
- Complete all remaining chapters of the project report:
  - Chapter 3: System Design (use `architecture.md`)
  - Chapter 4: Implementation Details (code snippets, screenshots)
  - Chapter 5: Testing & Results (tables, charts, metrics)
  - Chapter 6: Conclusion & Future Work
- Add screenshots of the running system to the report
- Compile references (all 24 papers from literature survey)
- Proofread and format the report per VTU guidelines

### Deliverables
- [ ] `README.md` complete
- [ ] User guide written
- [ ] Demo video recorded
- [ ] All report chapters written and formatted
- [ ] Report reviewed by guide Dr. S Krishna Anand

---

## Phase 10: Final Review & Submission
**Duration:** Week 22

### Goals
Final review with the guide, fix any last feedback, and submit the complete project.

### Tasks
- Present the working system to Dr. S Krishna Anand for review
- Incorporate any final feedback from guide
- Prepare for viva / project demonstration:
  - Be ready to explain each module
  - Be ready to run live demo with a new dataset
  - Be ready to answer questions on ML models used, preprocessing decisions, and NLP approach
- Final submission:
  - Hard copy of project report
  - Soft copy (CD / Google Drive link)
  - GitHub repository link (make public or share with guide)
  - Demo video link

### Deliverables
- [ ] Guide review completed and sign-off obtained
- [ ] Hard copy report submitted
- [ ] GitHub repository finalized and shared
- [ ] System demo ready to run live

---

## Team Responsibility Matrix

| Module | Primary Owner | Support |
|---|---|---|
| Preprocessing Module | M Kavana Reddy | Sahana N S |
| Analytical Engine + ML | Mohit Kumar Gupta | Yuktha Reddy B K |
| Visualization Module | Sahana N S | M Kavana Reddy |
| NLP Query Engine | Sahana N S | Mohit Kumar Gupta |
| Backend API & Integration | Yuktha Reddy B K | Mohit Kumar Gupta |
| Frontend UI | Yuktha Reddy B K | M Kavana Reddy |
| Testing | All Members | — |
| Report & Documentation | All Members | — |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Module integration failures | Medium | High | Define clear JSON contracts between modules early |
| Model training too slow on large datasets | Medium | Medium | Use Celery async tasks; test with small data first |
| NLP queries misunderstood | High | Low | Limit to well-defined intents; show example queries to user |
| Team member unavailable | Low | High | Each module documented so any member can continue |
| Dataset format not supported | Medium | Medium | Validate file type and encoding on upload |
| Scope creep (adding too many features) | Medium | High | Stick to defined scope; log enhancements for future work |

---

## Definition of Done

A phase is considered **complete** when:
1. All tasks in that phase are checked off
2. Code is committed and pushed to GitHub
3. At least one other team member has reviewed the code
4. Tests for that phase are written and passing
5. Guide has been updated on progress (weekly meeting)

