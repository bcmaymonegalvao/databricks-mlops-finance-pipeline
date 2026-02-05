# **Databricks MLOps Finance Pipeline — Professional Template**

A professional template to build **end-to-end Data + ML pipelines** for **finance / logistics / customer analytics** on **Databricks**, using **MLflow** and strong engineering practices.

This template supports a repeatable workflow:
**ingest → Bronze/Silver/Gold → features → train → evaluate → quality gate → register → batch scoring → monitoring → retrain**

---

## Design goals

- **Databricks-native**: Delta/Unity Catalog patterns, and deployment via **Databricks Asset Bundles (DAB)**.
- **Professional-by-default**: clean structure, documentation, conventions, testing, and CI.
- **Reproducible & traceable**: MLflow tracking, dataset/version tagging, and artifact logging.
- **Operational ready**: monitoring, alerting hooks, and runbooks for incident response.
- **Free-friendly (GitHub side)**: public repo, GitHub Actions, and open-source lint/test tooling.

---

## What’s included

- **Databricks Asset Bundles (DAB)** entrypoint (`databricks.yml`)
- **Workflow/Job definitions** under `resources/`
- **Notebooks exported as .py** (works well with Git versioning) under `notebooks/`
- **Reusable Python package** under `src/`
- **Tests** under `tests/` (smoke/unit)
- **Docs**:
  - CRISP-DM + MLOps roadmap: `docs/roadmap_crispdm_mlops.md`
  - ADRs (decisions): `docs/decisions/`
  - Runbooks: `docs/runbook/`
  - Architecture assets (optional): `docs/architecture/`
- **GitHub templates** (Issues/PR) and **CI** workflows under `.github/`

---

## Repository structure

```
.
├─ databricks.yml                  # Databricks Asset Bundle (DAB) entrypoint
├─ resources/                      # DAB resources (workflows/jobs/pipelines)
├─ notebooks/                      # Databricks notebooks (exported as .py)
├─ src/                            # Python package (reusable logic)
├─ tests/                          # Unit/smoke tests
├─ docs/
│  ├─ roadmap_crispdm_mlops.md     # CRISP-DM mapped to MLOps deliverables
│  ├─ architecture/                # Diagrams and architecture evidence (optional)
│  ├─ decisions/                   # ADRs (architecture decision records)
│  └─ runbook/                     # Operational runbooks
└─ .github/                        # CI, issue templates, PR template, label sync
```

---

## Local development (free)

1) Create a virtual environment and install dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

2) Run lint + tests:

```bash
ruff check .
pytest -q
```

---

## Databricks deployment (DAB)

This template is designed around **Databricks Asset Bundles**.

Typical commands:

```bash
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run -t dev main_pipeline
```

You must have the Databricks CLI configured and authenticated for your workspace.
Recommended: store workspace credentials using a secure method (never commit tokens).

---

## How to use this template in a new project

1) Implement ingestion in:
- `notebooks/01_ingest_bronze.py` (e.g., API pull, file drop, autoloader)

2) Implement transformations and data quality in:
- `notebooks/02_transform_silver_gold.py`
  (or switch to DLT pipelines if you want managed expectations/lineage)

3) Implement training and experiment tracking in:
- `notebooks/03_train_mlflow.py` (log params/metrics/artifacts, tag dataset version, register model)

4) Implement scoring in:
- `notebooks/04_batch_scoring.py` (load model from MLflow Registry, write predictions to Gold)

5) Add monitoring and operational procedures:
- monitoring code under `src/monitoring/` (optional)
- runbooks under `docs/runbook/`

---

## Conventions (recommended)

- **Naming**: keep consistent job/task names, table names, and MLflow tags.
- **MLflow tags**: `dataset_version`, `git_sha`, `owner`, `use_case`, `env`.
- **Data layers**: Bronze (raw), Silver (clean), Gold (consumption/model-ready).
- **Quality gate**: promote model versions only when evaluation + checks pass.

---

## Security

- Do not commit secrets (tokens, keys, credentials).
- Use `.env.example` for local variables.
- Prefer Databricks Secret Scopes / CI secrets for automation.

---

## License

MIT. See `LICENSE`.
