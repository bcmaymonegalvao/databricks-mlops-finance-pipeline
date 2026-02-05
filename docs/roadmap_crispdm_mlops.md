# Roadmap (CRISP-DM + MLOps) — Databricks MLOps Finance Pipeline

Este documento define o **kickoff** do projeto, o **objetivo de negócio**, **KPIs**, **escopo**, **riscos** e o **roadmap** seguindo **CRISP-DM**, traduzido para entregáveis e evidências de **MLOps** em Databricks + MLflow.

---

## 1) Visão geral

### 1.1 Contexto
O projeto implementa um pipeline ponta a ponta em Databricks para um caso realista de finanças/logística/comportamento de clientes, com ênfase em:
- ingestão e curadoria de dados (Bronze/Silver/Gold)
- experimentação e rastreabilidade (MLflow)
- automação (Workflows/Jobs)
- monitoramento (qualidade + drift)
- governança (convenções, CI, evidências, runbooks)

### 1.2 Caso de uso (MVP)
**Previsão de câmbio USD/BRL (PTAX)** para apoiar decisão operacional (ex.: tesouraria, precificação, risco) com atualização periódica de dados.

> Extensão opcional futura: detecção de anomalias (ex.: volume de transações, atrasos logísticos, comportamento de clientes).

---

## 2) Problema de negócio

### 2.1 Pergunta de negócio
“Conseguimos prever a taxa PTAX (USD/BRL) para o próximo dia/semana com qualidade suficiente para apoiar decisões e reduzir incerteza operacional?”

### 2.2 Valor esperado
- Melhor previsibilidade para planejamento (hedge, precificação, alocação).
- Processo reprodutível e auditável (MLflow + versionamento).
- Operação automatizada com monitoramento e retreino quando necessário.

### 2.3 Stakeholders (simulados)
- **Product/Business Owner**: define objetivos e KPIs
- **Data/ML Tech Lead**: arquitetura, MLOps, governança
- **Analytics/Finance**: valida métricas, interpreta previsões
- **Ops/Engineering**: integrações, jobs, confiabilidade

---

## 3) KPIs e critérios de sucesso

### 3.1 Métrica de modelo (MVP)
- Primária: **sMAPE** (ou MAPE, se aplicável)
- Secundárias: **MAE**, **RMSE**

### 3.2 Critérios de sucesso (exemplo)
- sMAPE <= **X%** em janela de validação temporal (definir após baseline)
- Melhora de **Y%** sobre baseline simples (ex.: “último valor” / média móvel)
- Pipeline executando automaticamente (DAG) e registrando runs no MLflow
- Evidência reprodutível: dataset_version + git_sha em todos os runs

> Observação: X e Y serão definidos após o baseline (Sprint 2/3).

---

## 4) Escopo e não-escopo

### 4.1 Escopo (incluído)
- Ingestão periódica de dados e camadas Bronze/Silver/Gold
- Feature engineering e datasets de treino/validação
- Treinamento e rastreabilidade de experimentos no MLflow
- Quality gate para promover modelo no Registry
- Batch scoring e escrita de previsões na camada Gold
- Monitoramento (qualidade de dados + drift) e gatilhos para retreino
- Documentação: ADRs, runbooks, evidências e roadmap

### 4.2 Não-escopo (MVP)
- Serving online em tempo real (API low-latency)
- Feature Store avançada (pode ser adicionada depois)
- Estratégias sofisticadas de hedge/portfólio
- Observabilidade enterprise completa (ferramentas pagas)

---

## 5) Dados (MVP)

### 5.1 Fonte e periodicidade
- Série temporal de câmbio **PTAX** com atualização periódica (diária).
- Dados auxiliares (opcional): calendário, feriados, indicadores simples, etc.

### 5.2 Estrutura (alto nível)
- **Bronze**: dados brutos da fonte (append-only quando possível)
- **Silver**: limpeza (tipos, dedup, regras)
- **Gold**: dataset model-ready (features + target) e tabela de previsões

### 5.3 Validação
- Split temporal (ex.: treino até T, validação T+1…T+n)
- Backtest / walk-forward (na medida do possível)

---

## 6) CRISP-DM mapeado para entregáveis de MLOps

### 6.1 Business Understanding (Entendimento do negócio)
**Atividades**
- Definir objetivo, stakeholders, KPIs e DoD
- Definir escopo / não-escopo
- Definir riscos e plano de mitigação

**Entregáveis**
- Este documento atualizado
- Definição de KPIs e baseline
- DoD do projeto e por sprint

**Evidências**
- PR/merge desta Issue
- Roadmap no GitHub Project (Timeline)

---

### 6.2 Data Understanding (Entendimento dos dados)
**Atividades**
- Explorar dados (distribuição, missingness, outliers, sazonalidade)
- Identificar limitações (dias sem cotação, feriados, gaps)

**Entregáveis**
- Notebook/relatório EDA
- Dicionário de dados (mínimo)

**Evidências**
- Prints/links do EDA + tabela Gold model-ready

---

### 6.3 Data Preparation (Preparação dos dados)
**Atividades**
- Construção Bronze/Silver/Gold
- Padronização e qualidade (checks)
- Geração do dataset de treino/validação e features

**Entregáveis**
- Notebooks de ingestão e transformações
- Tabelas Silver/Gold + checks documentados
- Estratégia de versionamento do dataset (dataset_version)

**Evidências**
- Logs do workflow + link/print das tabelas no UC
- Evidências no `docs/evidence_checklist.md`

---

### 6.4 Modeling (Modelagem)
**Atividades**
- Definir baseline
- Treinar modelos candidatos (ex.: regressão, XGBoost, Prophet/ARIMA se fizer sentido)
- Logar runs no MLflow (params, metrics, artifacts)

**Entregáveis**
- Pipeline de treino (notebook/script)
- Runs no MLflow com tags obrigatórias

**Evidências**
- Links dos experiments/runs com comparação e artefatos

---

### 6.5 Evaluation (Avaliação)
**Atividades**
- Avaliação temporal/backtest
- Comparação com baseline
- Validar estabilidade e robustez

**Entregáveis**
- Relatório de avaliação
- “Quality Gate” (critério objetivo pass/fail)

**Evidências**
- Logs/artefatos com métricas e decisão do gate

---

### 6.6 Deployment (Implantação/Operação)
**Atividades**
- Registro no MLflow Model Registry
- Batch scoring automatizado (Workflows)
- Monitoramento de dados/drift e gatilhos de retreino
- Runbook de incidentes e operação

**Entregáveis**
- Modelo registrado (staging/prod)
- Tabela Gold de previsões
- Monitoramento + documentação operacional

**Evidências**
- Workflow run, tabela de previsões, alerta simulado, runbook

---

## 7) MLOps: Definition of Done (DoD)

### 7.1 DoD do projeto (alto nível)
- Pipeline Bronze/Silver/Gold funcionando e reprodutível
- Treino/eval com MLflow (tags e artefatos completos)
- Modelo registrado e promovido via quality gate
- Scoring em batch automatizado com escrita em Gold
- Monitoramento (qualidade + drift) com exemplo de acionamento
- Documentação (ADRs, runbooks, checklist de evidências) completa
- CI passando (ruff + pytest) e histórico limpo

### 7.2 DoD por sprint (resumo)
- **Sprint 0**: base (board, CI, docs, convenções)
- **Sprint 1**: dados (Bronze/Silver/Gold)
- **Sprint 2**: features + MLflow experiments
- **Sprint 3**: avaliação + gate + registry
- **Sprint 4**: scoring + monitoramento + runbook
- **Sprint 5**: hardening + finops + demo script

---

## 8) Riscos e mitigação

- **Dados com lacunas/feriados** → tratar calendário e regras no Silver/Gold
- **Overfitting em série temporal** → validação temporal/backtest; baseline forte
- **Drift (mudança de regime)** → monitorar estatísticas/erro, gatilho de retreino
- **Reprodutibilidade fraca** → tags MLflow + dataset_version + git_sha obrigatórios
- **Custos/recursos** → usar configurações econômicas, jobs enxutos e documentação FinOps

---

## 9) Plano de execução por sprint (alto nível)

- **Sprint 0 (Setup)**  
  Board/roadmap, CI, ADR de convenções, checklist de evidências

- **Sprint 1 (Dados)**  
  Ingestão PTAX → Bronze/Silver/Gold + checks de qualidade

- **Sprint 2 (Features + MLflow)**  
  EDA, features, baseline + modelos candidatos, runs rastreáveis no MLflow

- **Sprint 3 (Eval + Gate + Registry)**  
  Backtest temporal, quality gate, registro e promoção controlada

- **Sprint 4 (Scoring + Monitoramento)**  
  Workflow fim-a-fim, tabela de previsões, monitoramento e runbook

- **Sprint 5 (Hardening + Demo + FinOps)**  
  Testes e CI como gate, otimização de custo, roteiro de apresentação (demo)

---
