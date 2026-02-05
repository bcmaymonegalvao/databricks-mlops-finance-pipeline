# **Databricks MLOps Finance Pipeline — Projeto Profissional**

Este repositório implementa um projeto profissional de **Data + Machine Learning** em **Databricks**, utilizando **MLflow** e boas práticas de engenharia para construir e operar pipelines ponta a ponta em cenários de **finanças / logística / comportamento de clientes**.

O fluxo do projeto segue um ciclo repetível e operacional:
**ingestão → Bronze/Silver/Gold → features → treino → avaliação → quality gate → registro → batch scoring → monitoramento → retreino**

---

## Objetivos de design

- **Nativo de Databricks**: padrões com **Delta Lake / Unity Catalog** e deploy via **Databricks Asset Bundles (DAB)**.
- **Padrão profissional**: estrutura limpa, documentação, convenções, testes e CI.
- **Reprodutível e rastreável**: tracking no MLflow, versionamento/tagging do dataset e logging de artefatos.
- **Pronto para operação**: monitoramento, ganchos para alertas e runbooks para resposta a incidentes.
- **Amigável ao GitHub**: repositório público, GitHub Actions e ferramentas open-source de lint/test.

---

## O que está incluído

- Entry point de **Databricks Asset Bundles (DAB)** (`databricks.yml`)
- Definições de **Workflows/Jobs** em `resources/`
- Notebooks exportados como `.py` (boa rastreabilidade no Git) em `notebooks/`
- Pacote Python reutilizável em `src/`
- Testes em `tests/` (smoke/unit)
- CI e templates de Issues/PR em `.github/`

---

## Documentos

- Roadmap CRISP-DM + MLOps: `docs/roadmap_crispdm_mlops.md`
- Decisões de arquitetura (ADRs): `docs/decisions/`
- Runbooks operacionais: `docs/runbook/`
- Evidências e diagramas de arquitetura (opcional): `docs/architecture/`
- Checklist de evidências (se existir no repo): `docs/evidence_checklist.md`

---

## Estrutura do repositório

```
.
├─ databricks.yml                  # Entry point do Databricks Asset Bundle (DAB)
├─ resources/                      # Recursos do DAB (workflows/jobs/pipelines)
├─ notebooks/                      # Notebooks do Databricks (exportados como .py)
├─ src/                            # Pacote Python (lógica reutilizável)
├─ tests/                          # Testes unitários e smoke tests
├─ docs/
│  ├─ roadmap_crispdm_mlops.md     # CRISP-DM mapeado para entregáveis de MLOps
│  ├─ architecture/                # Diagramas e evidências de arquitetura (opcional)
│  ├─ decisions/                   # ADRs (Architecture Decision Records)
│  └─ runbook/                     # Runbooks operacionais
└─ .github/                        # CI, issue templates, PR template, sync de labels
```

---

## Desenvolvimento local (gratuito)

1) Crie um ambiente virtual e instale dependências de desenvolvimento:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

2) Rode lint + testes:

```bash
ruff check .
pytest -q
```

---

## Deploy no Databricks (DAB)

Este projeto é organizado para **Databricks Asset Bundles**.

Comandos típicos:

```bash
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run -t dev main_pipeline
```

Pré-requisitos:
- Databricks CLI configurado e autenticado no seu workspace.
- Recomendação: armazenar credenciais de forma segura (nunca commitar tokens).

---

## Como evoluir o projeto (próximos passos técnicos)

1) Implementar ingestão em:
- `notebooks/01_ingest_bronze.py` (ex.: API, drop de arquivos, autoloader)

2) Implementar transformações e qualidade em:
- `notebooks/02_transform_silver_gold.py`
  (ou migrar para DLT se desejar expectations/lineage gerenciados)

3) Implementar treino e tracking de experimentos em:
- `notebooks/03_train_mlflow.py` (log de params/métricas/artefatos, tag de versão do dataset, registro de modelo)

4) Implementar scoring em batch em:
- `notebooks/04_batch_scoring.py` (carregar modelo do MLflow Registry e gravar previsões na camada Gold)

5) Adicionar monitoramento e rotinas operacionais:
- código de monitoramento em `src/monitoring/` (opcional)
- procedimentos e resposta a incidentes em `docs/runbook/`

---

## Convenções (recomendadas)

- **Naming**: manter consistência nos nomes de jobs/tasks, tabelas e tags do MLflow.
- **Tags MLflow**: `dataset_version`, `git_sha`, `owner`, `use_case`, `env`.
- **Camadas de dados**: Bronze (bruto), Silver (limpo), Gold (consumo/model-ready).
- **Quality gate**: promover versões de modelo apenas quando avaliação e checks passarem.

---

## Segurança

- Não commitar segredos (tokens, chaves, credenciais).
- Usar `.env.example` para variáveis locais.
- Preferir Databricks Secret Scopes / GitHub Secrets para automação.

---

## Licença

MIT. Veja `LICENSE`.
