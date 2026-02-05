# Evidence checklist (MLOps)

Este documento é um checklist vivo de evidências que comprovam o funcionamento ponta a ponta do pipeline
(dados, MLflow, Workflows do Databricks, scoring, monitoramento e operação).

> Sempre que concluir algo, adicione links/prints e referência ao run/artefato correspondente.

---

## Sprint 0 — Setup
- [ ] Board Scrum (GitHub Projects) configurado (campos, iterações, automations)
- [ ] README atualizado (descrição profissional do projeto)
- [ ] CI passando (ruff + pytest)
- [ ] ADR de convenções publicado (naming, MLflow tags, Delta layers)

**Evidências**
- Links para PRs/merges:  
  - [ ] PR Issue 3: <link>
  - [ ] PR Issue 5: <link>
  - [ ] PR Issue 4: <link>
- [ ] Print/Link do Actions (CI verde): <link>

---

## Sprint 1 — Pipeline de dados (Bronze/Silver/Gold)
- [ ] Fonte de dados definida + forma de atualização (batch/stream)
- [ ] Bronze criada (Delta) + esquema registrado
- [ ] Silver criada + limpeza, tipos, dedup
- [ ] Gold criada (model-ready) + tabela de treino

**Evidências**
- [ ] Link/print de tabelas UC: Bronze/Silver/Gold
- [ ] Contagens e checagens de qualidade (ex.: expectations): <link/print>
- [ ] Latência/freshness (quando atualiza): <nota/print>

---

## Sprint 2 — Features + Experimentos (MLflow)
- [ ] EDA com insights principais (missingness, outliers, sazonalidade)
- [ ] Feature set gerado (tabela/artefato) + versão
- [ ] Experimentos no MLflow:
  - [ ] Baseline
  - [ ] Modelo 1
  - [ ] Modelo 2

**Evidências**
- [ ] Link do MLflow Experiment + runs comparados
- [ ] Tags presentes (dataset_version, git_sha, env, use_case)
- [ ] Artefatos (plots, relatório de métricas): <links>

---

## Sprint 3 — Avaliação + Quality Gate + Registry
- [ ] Validação temporal/backtest implementada
- [ ] Quality gate com critérios objetivos (pass/fail)
- [ ] Modelo registrado no MLflow Registry (Staging)
- [ ] Critério de promoção documentado (ADR/roadmap)

**Evidências**
- [ ] Link do model registry (versão e estágio)
- [ ] Relatório de avaliação (métricas + comparação com baseline)
- [ ] Evidência do gate (ex.: notebook output/log)

---

## Sprint 4 — Scoring + Monitoramento + Operação
- [ ] Workflows (DAG) executando ponta a ponta no Databricks
- [ ] Batch scoring escrevendo previsões em Gold
- [ ] Consumo das previsões (SQL/BI) demonstrado
- [ ] Monitoramento:
  - [ ] Data drift / data quality
  - [ ] Model drift (se aplicável)
  - [ ] Alertas (exemplo de acionamento)
- [ ] Runbook de resposta operacional publicado

**Evidências**
- [ ] Print/Link do Workflow run + logs
- [ ] Link/print da tabela `gd_predictions_<use_case>`
- [ ] Exemplo de alerta disparado + ação tomada
- [ ] Link do runbook: `docs/runbook/`

---

## Sprint 5 — Hardening + FinOps
- [ ] Testes ampliados (smoke + críticos)
- [ ] CI como gate obrigatório no merge
- [ ] Controle de custos documentado (job clusters, autoscaling, policy)
- [ ] “Demo script” (roteiro de apresentação do projeto)

**Evidências**
- [ ] Configuração de cluster/job (print/link)
- [ ] Documento de FinOps (custos e otimizações)
- [ ] Demo script (passo a passo)
