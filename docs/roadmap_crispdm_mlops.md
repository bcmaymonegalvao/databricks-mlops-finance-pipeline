# Roadmap (CRISP-DM + MLOps on Databricks/MLflow)

This roadmap is optimized for interview presentations: it is explicit about **deliverables**, **evidence**, and **acceptance criteria**.

---

## Deliverables (high level)
- Bronze/Silver/Gold (Delta) pipeline with data quality checks (DLT expectations or equivalent)
- Feature engineering versioned and reproducible
- MLflow Experiments with params/metrics/artifacts + dataset version tagging
- Model Registry promotion (Staging → Production) behind a **quality gate**
- Batch scoring and publication of predictions for consumption (SQL/BI)
- Monitoring (data drift, model drift, data quality) + alerts + runbook
- Documentation + “Interview Pack”

---

## CRISP-DM mapped to Databricks / MLflow

### 1) Business Understanding
**Goal:** define the business question, KPIs, cost/benefit, and success criteria.  
**Artifacts:** 1-page scope, KPI definitions, “Definition of Done”, risks & constraints.

### 2) Data Understanding
**Goal:** understand sources, frequency, schema, drift risks, and quality issues.  
**Artifacts:** EDA notebook, data dictionary, initial data quality rules.

### 3) Data Preparation
**Goal:** build reproducible transformations and a model-ready Gold table.  
**Artifacts:** Bronze/Silver/Gold tables, transformations documented, quality checks automated.

### 4) Modeling
**Goal:** train baseline + candidate models, compare them, track everything.  
**Artifacts:** MLflow runs, model artifacts, signatures, reproducible training code.

### 5) Evaluation
**Goal:** validate with temporal splits/backtesting + “real data” checks, decide promotion.  
**Artifacts:** evaluation report, gate criteria checklist, staging model registration.

### 6) Deployment
**Goal:** operationalize (batch scoring and/or serving) and deliver value.  
**Artifacts:** workflow/job orchestration, prediction table, BI/dashboard integration.

### 7) Operation & Continuous Improvement (MLOps)
**Goal:** monitor drift and quality, retrain safely, manage incidents.  
**Artifacts:** monitoring dashboards, alerting, runbooks, incident log & RCA.

---

## Sprint plan (Scrum example)

### Sprint 0 — Setup & Planning
- Repo scaffolding + docs + board + issue templates
- Databricks/MLflow conventions: naming, tags, environments

### Sprint 1 — Data pipeline (Bronze/Silver/Gold)
- Ingestion (API/file) → Bronze (Delta)
- Transformations → Silver → Gold
- Data quality checks (expectations/tests)

### Sprint 2 — Features + baseline + MLflow experiments
- Feature engineering (lags, rolling windows, calendar, FX deltas)
- Baseline + 2 candidate models tracked in MLflow

### Sprint 3 — Evaluation + Gate + Registry
- Temporal validation (walk-forward/backtest)
- Quality gate definition
- Register model in Staging; approve/push to Production when ready

### Sprint 4 — Deploy + scoring + monitoring
- Databricks Workflows DAG: ingest → dlt → features → train → gate → register → score
- Prediction table and consumption layer
- Drift + quality monitoring + alerts + runbook

### Sprint 5 — Hardening + FinOps + Interview pack
- Tests + CI
- Cost controls and documentation
- Final demo script and README improvements

---

## Evidence checklist (for interviews)
- A GitHub Project (Scrum) with issues, sprints, and PR links
- MLflow screenshots showing runs, metrics, artifacts, and model versions
- A full DAG run log (Databricks Workflow)
- Prediction table + simple dashboard
- Monitoring + an example alert + runbook
