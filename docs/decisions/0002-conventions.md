# ADR 0002: Convenções do projeto (naming, MLflow tags, Delta layers)

## Status
Accepted

## Objetivo
Padronizar nomes e metadados para que pipelines sejam **reprodutíveis**, **comparáveis** e **fáceis de operar** (principalmente em Databricks + MLflow).

---

## 1) Camadas de dados (Delta / Medallion)
Arquitetura recomendada:

- **Bronze**: dados brutos ingeridos (idealmente append-only)
- **Silver**: dados limpos/normalizados (tipos, dedup, regras de negócio)
- **Gold**: consumo e tabelas prontas para modelagem/BI (features, previsões, agregados)

### Unity Catalog (recomendado)
- Catálogo: `<project_catalog>` (ex.: `finance_mlops`)
- Schemas: `bronze`, `silver`, `gold`

---

## 2) Padrão de nomes para tabelas
### Formato geral
`<camada>_<dominio>_<entidade>`

Sugestões:
- Bronze: `br_<source>_<entity>`
- Silver: `sl_<domain>_<entity>`
- Gold (model-ready): `gd_<domain>_<entity>`
- Predictions: `gd_predictions_<use_case>`
- Monitoring: `gd_monitoring_<use_case>`

Exemplos:
- `br_bcb_ptax_raw`
- `sl_fx_ptax_clean`
- `gd_fx_training_set`
- `gd_predictions_fx_forecast`

### Particionamento
- Preferir particionar por data (`ds`, `event_date`) quando volume for alto
- Evitar particionar por colunas com cardinalidade alta

---

## 3) Convenções de Workflows/Jobs/Tasks (Databricks Workflows)
### Nome do Job/Workflow
`mlops-<use_case>-<env>`

Exemplos:
- `mlops-fx-forecast-dev`
- `mlops-pix-anomaly-prod`

### Task keys (padrão)
- `ingest`
- `transform`
- `features`
- `train`
- `evaluate`
- `gate`
- `register`
- `score`
- `monitor`

---

## 4) MLflow: tags mínimas e rastreabilidade
### Tags obrigatórias em TODO run
- `dataset_version`: versão do dataset usado no treino/validação
- `git_sha`: commit hash do código do treino
- `env`: `dev` | `stg` | `prod`
- `owner`: usuário/time responsável
- `use_case`: nome do caso (ex.: `fx_forecast`)
- `model_family`: ex.: `sklearn`, `xgboost`, `prophet`

### Recomendadas
- `feature_set_version`
- `training_window`: ex.: `2024-01-01..2025-12-31`
- `data_source`: ex.: `bcb_ptax`

---

## 5) Como definir `dataset_version` (escolha 1 e mantenha)
### Opção A — Delta snapshot (Databricks-native)
Usar a versão da tabela Delta:
- Tag `dataset_table`: `gold.gd_fx_training_set`
- Tag `dataset_delta_version`: `123`

Vantagem: reprodução direta com time travel.

### Opção B — Hash portátil (cross-platform)
Gerar um hash estável usando:
- schema + row count + min/max date + checksum amostral

Vantagem: funciona fora do Delta.

Requisito mínimo:
- Sempre registrar **o que foi usado** e **como reproduzir**.

---

## 6) Métricas (padrões por tipo de problema)
### Forecast / séries temporais
- Primária: `sMAPE` (ou `MAPE`)
- Secundárias: `MAE`, `RMSE`
- Sempre registrar: estratégia de split temporal (walk-forward/backtest)

### Classificação / risco / churn
- Primária: `AUC` (ou `F1`, dependendo do caso)
- Secundárias: `precision`, `recall`, `PR-AUC`
- Sempre registrar: threshold escolhido e racional

### Anomalias
- Primária: `precision@k` ou taxa de acerto por alerta
- Secundárias: FPR, tempo até detecção

---

## 7) Quality Gate (promoção no Registry)
Um modelo só deve ser promovido quando:
- métricas ≥ baseline por margem acordada
- checagens de qualidade de dados passaram
- tags obrigatórias presentes (ex.: `dataset_version`, `git_sha`, `env`, `use_case`)
- assinatura do modelo (signature) registrada e estável
- (opcional) validação em dados recentes / “real data”
