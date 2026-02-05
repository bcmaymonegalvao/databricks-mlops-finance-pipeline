# ADR 0001: Use Databricks Asset Bundles (DAB) for deployment

## Status
Accepted

## Context
We need a reproducible, environment-aware way to deploy Databricks workflows, jobs, and related resources.

## Decision
Use **Databricks Asset Bundles (DAB)** and the Databricks CLI to define, validate, deploy, and run resources through a `databricks.yml` bundle configuration.

## Consequences
- Single source-of-truth for workflow definitions in version control
- Easier CI/CD automation and multi-environment deployment
- Developers must be comfortable with the Databricks CLI and bundle configuration
