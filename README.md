# Databricks MLOps Finance Pipeline (Template)

An end-to-end **MLOps** template for a **finance/logistics/customer-behavior** use case using **Databricks** and **MLflow**:
**ingest → Bronze/Silver/Gold → features → train → quality gate → register → batch scoring → monitoring → retrain**.

This repository is designed to be:
- **Public & interview-friendly** (clean structure + clear evidence)
- **Tooling-first** (CI, tests, lint, docs)
- **Databricks-native** via **Databricks Asset Bundles (DAB)**

---

## What you can show to interviewers
- Architecture diagrams: `docs/architecture/`
- Roadmap (CRISP-DM + MLOps): `docs/roadmap_crispdm_mlops.md`
- Notebooks: `notebooks/`
- Source code: `src/`
- Tests & CI: `tests/` and `.github/workflows/`

---

## Directory structure

```
.
├─ databricks.yml                  # Databricks Asset Bundle (DAB) entrypoint
├─ resources/                      # DAB resources (workflows, jobs, pipelines)
├─ notebooks/                      # Databricks notebooks (exported .py)
├─ src/                            # Python package (reusable logic)
├─ tests/                          # Unit/smoke tests
├─ docs/
│  ├─ roadmap_crispdm_mlops.md     # CRISP-DM mapped to MLOps deliverables
│  ├─ architecture/                # Diagrams and architecture evidence
│  ├─ decisions/                   # ADRs (architecture decision records)
│  └─ runbook/                     # Operational runbooks
└─ .github/                        # CI, issue templates, PR template, label sync
```

---

## Quickstart (local dev)

1) Create a virtual environment and install dev deps:
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

## Databricks (DAB) workflow

This template uses **Databricks Asset Bundles** (`databricks.yml`). Typical commands:

```bash
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run -t dev main_pipeline
```

> You must have the Databricks CLI configured and authenticated for your workspace.

---

## Scrum planning on GitHub
Use **GitHub Projects (Scrum)** with iterations (Sprint 0..5) and map issues to sprints.
See `docs/roadmap_crispdm_mlops.md` for the recommended sprint plan and acceptance criteria.

---

## License
MIT. See `LICENSE`.
