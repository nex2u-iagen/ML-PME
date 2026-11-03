# 🧠 Arquitetura de Pipeline e Descoberta Analítica para ERPs de PMEs

> **Base de dados:** Mercadinho Vencedor 10/2026 — **Dataset privado, não compartilhado.**  
> **Autor:** Eliezer Henrique

Este projeto implementa uma arquitetura modular de ponta a ponta para ingestão, diagnóstico estatístico, descoberta de hipóteses e modelagem preditiva a partir de backups e dados transacionais de ERPs de Pequenas e Médias Empresas (PMEs).

Seguindo a metodologia **CRISP-DM**, com princípios de **Alta Coesão** e **Baixo Acoplamento**.

---

## 🏛️ Arquitetura

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Streamlit)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Ingestão    │  │   Raio-X     │  │   Torneio    │  │    Valor     │   │
│  │  (Fase 01)   │  │  (Fase 02)   │  │ (Fases 03-05)│  │  (Fase 05)   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │           │
│         └─────────────────┴─────────────────┴─────────────────┘           │
│                              └──────────┬──────────────┘                │
│                                         │                               │
│  ┌─────────────────────────────────────▼───────────────────────────────┐ │
│  │                   VITRINE EXECUTIVA (porta 8503)                    │ │
│  │  Fluxo CRISP-DM (SVG 13 etapas) · Saúde 360° · Relatórios dept.    │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE SERVIÇO REST (API :8000)                  │
│  Datasets · Upload · Problemas · Fases assíncronas · Jobs · Top 3 · Campeão │
│  Predição de risco de crédito (Pilar 4 - Fase 06, com Bearer JWT)           │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE DADOS (somente leitura)                   │
│  dados/brutos/csv/<ds>/   dados/brutos/sql/<ds>.sql                         │
│  dados/processados/<ds>/ml/  (ABT, treino, validação, teste)                │
│  artefatos/modelos_producao/  (pipeline, manifesto SHA-256)                 │
│  relatorios/<ds>/  (laudos Fase 02, avaliações Fase 05)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Portas em execução:**
- `8502` — Plataforma operacional (4 atos + Predição)
- `8503` — Vitrine executiva (fluxo, saúde 360°, relatórios)
- `8000` — API FastAPI de inferência (obrigatória para Predição)

---

## 🏛️ Diretrizes de Engenharia e Governança

### 1. Filosofia de Governança
> *"Modelos não tomam decisões, eles reduzem a incerteza. Sem dados limpos, arquitetura organizada, explicabilidade e impacto no negócio, a IA é apenas um experimento de laboratório."*

### 2. Imutabilidade e Blindagem de Dados
* `dados/brutos/sql/`: somente leitura (dumps `.sql` de Postgres, MySQL, Firebird, SQL Server).
* `dados/brutos/csv/`: somente leitura (arquivos delimitados exportados do ERP).
* `dados/processados/`: conjuntos transformados, tratados e prontos para treinamento analítico.
* **Segurança da Informação:** dados protegidos por sigilo industrial e LGPD/GDPR não devem ser versionados (bloqueio via `.gitignore`).

### 3. Padrão de Qualidade de Código (Ruff)
Todo o código Python adere a PEP 8 e documentação no estilo Google via **Ruff**:
* Linter: variáveis não utilizadas, conformidade semântica, ausência de dead code.
* Formatter: quebra de 88 caracteres, indentação uniforme, ordenação de imports (`isort`).
* Idioma: variáveis, classes, funções e docstrings exclusivamente em Português do Brasil (pt-br).

---

## 🛠️ Ecossistema Tecnológico

| Ferramenta | Categoria | Uso |
|:---|:---|:---|
| `uv` | Gerenciador de pacotes | Substitui `pip`, `venv`, `poetry`. Resolução determinística via `uv.lock`. |
| `Ruff` | Qualidade de código | Linter e formatador em Rust. |
| `SQLAlchemy` | Ingestão e conexão | Motor de banco de dados e abstração SQL com *chunking*. |
| `pandas` | Manipulação tabular | DataFrames, operações vetorizadas. |
| `numpy` | Computação numérica | Álgebra linear e matrizes multidimensionais. |
| `statsmodels` | Rigor estatístico | Estimativa de modelos estatísticos e testes de hipóteses. |
| `seaborn` & `matplotlib` | Visualização | Diagnósticos gráficos, dispersão, correlação. |
| `scikit-learn` | Modelagem | Algoritmos supervisionados e não supervisionados, pré-processamento, Pipelines. |
| `AutoGluon` | AutoML | Treinamento automatizado de múltiplos modelos de ponta. |

---

## 🌐 Plataforma Agnóstica

A plataforma é desenhada para ser agnóstica a qualquer dataset e a qualquer pergunta de negócio, usando o motor CRISP-DM parametrizado por artefatos declarativos.

Princípios-chave:
* **Contrato de Problema** (`ContratoProblema`): o que o humano quer saber, validado por Pydantic v2.
* **Registro de Dataset** (`RegistroDataset`): base em análise, persistido em JSON com estado das fases, pódio Top 3 e campeão escolhido.
* **Catálogo semântico editável**: mapeia entidades canônicas (vendas, recebedor, data de venda, estoque) para colunas reais do ERP.
* **Joins declarativos** em `ReceitaABT.juncoes` com CTEs pré-agregados (evita fan-out 1:N).
* **Granularidade temporal** (`dia|semana|mes|ano`) via CTE `com_grupo`.
* **15 problemas de negócio** (5 classificação, 5 regressão, 3 agrupamento, 2 anomalias).
* **Frontend em 4 atos:** Base → Pergunta → Torneio → Valor.
* **Jobs assíncronos persistidos** com status `pendente|executando|concluido|erro` e log linha a linha.
* **CAMADA DE SERVIÇO REST (G6):** 8 endpoints para datasets, upload, problemas, fases, jobs, Top 3 e campeão.
* **Sem portão de login JWT no frontend:** o fluxo de 4 atos é acessível sem autenticação. O JWT é exigido apenas na API de inferência de produção.
* **Isolamento por dataset:** cada PME tem pasta própria de dados brutos, artefatos, modelos e relatórios.
* **Idioma da interface e das specs:** português do Brasil.

### Artefatos por dataset

| Tipo | Caminho |
|:---|:---|
| Dados brutos (CSV) | `dados/brutos/csv/<ds>/*.csv` |
| Dumps SQL | `dados/brutos/sql/<ds>.sql` |
| Registro do dataset | `dados/registros/<ds>.json` |
| Artefatos ML (Parquet) | `dados/processados/<ds>/ml/{treino,validacao,teste}_processado.parquet` |
| Contrato de problema | `dados/processados/<ds>/ml/contrato_problema.json` |
| Modelos serializados | `modelos/<ds>/` |
| Relatórios | `relatorios/<ds>/` |

### Endpoints da Camada de Serviço (G6)

| Método | Endpoint | Descrição |
|:---|:---|:---|
| `GET` | `/datasets` | Lista datasets com estado de cada fase |
| `POST` | `/datasets/{nome}/upload` | Recebe upload de `.sql`/`.csv` |
| `GET` | `/problemas` | Lista 15 templates de problema de negócio |
| `POST` | `/datasets/{nome}/problema` | Vincula contrato de problema ao dataset |
| `POST` | `/datasets/{nome}/fases/{fase}/executar` | Dispara execução assíncrona de fase CRISP-DM |
| `GET` | `/jobs/{id}` | Consulta estado, log e resultado de job |
| `GET` | `/datasets/{nome}/top3` | Retorna pódio Top 3 com métricas |
| `POST` | `/datasets/{nome}/campeao` | Registra escolha humana do campeão |

---

## 🚀 Como Usar

### 0. Configuração de Variáveis de Ambiente

Crie `.env` na raiz do projeto:

```bash
cd projeto_ml
cp .env.example .env  # ou crie manualmente
```

| Variável | Descrição | Padrão |
|:---|:---|:---|
| `JWT_SECRET_KEY` | Chave secreta para JWT (API de inferência) | `CHAVE_MESTRE_SUPER_SECRETA_PRODUCAO_MINIMO_32_BYTES_2026` |
| `API_SENHA_PADRAO` | Senha padrão de login na API | `senha_segura_mercado_2026` |
| `ENVIRONMENT` | Ambiente ('dev' ou 'producao') | `dev` |

> Em produção, substitua estes valores por segredos seguros.

### 1. Instalação

```bash
git clone <URL_DO_REPOSITORIO> projeto_ml
cd projeto_ml

# Cria o .venv e instala as versões exatas de uv.lock (inclui o Ruff)
uv sync --dev
```

### 2. Verificação rápida

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q src scripts testes
uv run python testes/testar_alg_kmeans.py
```

### 3. Pipeline com seus dados (Fases 1–3)

1. Copie os CSVs do ERP para `dados/brutos/csv/` com padrão `erp_<entidade>.csv`.
   Dumps relacionais vão em `dados/brutos/sql/`.
2. Execute as três fases na ordem:

```bash
uv run python - <<'PY'
from pathlib import Path
from src.etapas.fase_01_ingestao.etapa_01_extracao import OrquestradorIngestao
from src.etapas.fase_02_exploracao.etapa_02_raio_x_empresarial import OrquestradorRaioXEmpresarial
from src.etapas.fase_03_preparacao.etapa_03_01_dados_para_bi import OrquestradorDadosBI
from src.etapas.fase_03_preparacao.etapa_03_02_dados_para_ml import OrquestradorDadosML

raiz = Path.cwd()
OrquestradorIngestao(raiz).executar_fase_ingestao()
OrquestradorRaioXEmpresarial(raiz).executar_raio_x_completo()
OrquestradorDadosBI(
    pasta_dados_brutos=raiz / "dados/brutos/csv",
    pasta_saida_bi=raiz / "dados/processados/bi",
).executar_preparacao_bi_completa()
OrquestradorDadosML(
    pasta_bi=raiz / "dados/processados/bi",
    pasta_saida_ml=raiz / "dados/processados/ml",
    pasta_modelos=raiz / "modelos",
).executar_preparacao_ml_completa()
PY
```

Resultados:
* Data Marts de BI: `dados/processados/bi/*.csv`
* ABT bruta: `dados/processados/ml/abt_cliente_bruta.parquet`
* Partições de ML: `dados/processados/ml/{treino,validacao,teste}_processado.parquet`

### 4. Modelagem com os dados preparados (Fase 4)

```bash
uv run python -m src.etapas.fase_04_modelagem.etapa_04_01_orquestrador_baseline
uv run python -m scripts.executores_projeto.torneio_classificacao
uv run python -m scripts.executores_projeto.torneio_regressao
uv run python -m scripts.executores_projeto.torneio_agrupamento
```

### 5. Subir a API e consumir

```bash
# 1. Gere o artefato de produção
uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia

# 2. Suba o microsserviço
uv run python -m scripts.executores_projeto.servir_api

# 3. Acesse a documentação interativa
# http://127.0.0.1:8000/docs
```

A rota de predição exige `Authorization: Bearer <token>` (JWT). O login permanece na API para inferência de produção; o fluxo de 4 atos no frontend não exige autenticação.

### 6. Executando o Frontend Streamlit

**Opção A: Via Docker (recomendado)**
```bash
docker compose up --build
```

**Opção B: Localmente (sem Docker)**
```bash
# 1. Instale as dependências
uv sync --dev

# 2. Plataforma operacional (porta 8502)
PYTHONPATH=$PWD uv run streamlit run app_streamlit.py --server.port 8502

# 3. Vitrine executiva (porta 8503)
PYTHONPATH=$PWD uv run streamlit run src/app/app.py --server.port 8503

# 4. Acesse:
#    - Plataforma operacional: http://localhost:8502
#    - Vitrine executiva:      http://localhost:8503

# 5. Para a página de Predição, inicie também a API na porta 8000:
uv run python -m scripts.executores_projeto.servir_api
```

### Funcionalidades do Frontend Operacional (porta 8502)

1. **Ingestão** — Upload de CSVs/.sql, criação de dataset, execução da Fase 01. Exibe linhas × colunas dos CSVs brutos (validação de tamanho).
2. **Raio-X** — Fase 02 + 10 relatórios departamentais + Visão 360° — Saúde da empresa (radar, KPIs, semáforo).
3. **Torneio** — Vinculação de problema de negócio, Fase 03 (ABT + partições 70/15/15), Fase 04 (torneio de modelos), Top 3, Fase 05 (avaliação final).
4. **Valor** — Scorecard, contrato de problema, registros de governança e aprovação do campeão.
5. **Predição** — Formulário de entrada de dados de produção para previsão/classificação de risco de crédito (chama a API `:8000` via Bearer JWT).

### Funcionalidades da Vitrine Executiva (porta 8503)

1. **Início — Fluxo CRISP-DM** — Fluxograma SVG do pipeline em 13 etapas, 6 fases, laço de iteração.
2. **Saúde 360°** — Imagem única do dashboard de saúde (radar polar 0–100 + 8 cartões de KPI + semáforo de sinais).
3. **Relatórios** — PNGs e laudos departamentais da Fase 02.

Ambos os aplicativos se ligam por **links cruzados no sidebar**.

---

## ▶️ Execução dos Scripts

* **`scripts/executores_arquivo/`** — executam uma etapa, fase ou pilar isolado.
* **`scripts/executores_projeto/`** — executam um fluxo maior (torneios, servidor).

Sempre invoque como módulo a partir da raiz:

```bash
uv run python -m scripts.executores_arquivo.fase_04_ajustar_campeao
uv run python -m scripts.executores_projeto.torneio_classificacao
uv run python -m scripts.executores_projeto.servir_api
```

> ⚠️ Não execute `python scripts/.../arquivo.py` diretamente: a forma `-m` preserva a resolução dos pacotes `scripts` e `src`.

---

## ✅ Checklist antes de Consolidar Alterações

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q src scripts testes
```

Ou em lote:
```bash
for arquivo in testes/*.py; do
  case "$arquivo" in
    *testar_cliente_inferencia.py) continue ;;
  esac
  uv run python "$arquivo" || exit 1
done
```

---

## 🗂️ Estrutura de Diretórios

```
projeto_ml/
├── src/
│   ├── etapas/           # Lógica das fases CRISP-DM (01 a 06)
│   └── nucleo/           # Componentes reutilizáveis (dados, ML, contratos)
├── scripts/
│   ├── bootstrap.py      # Raiz do projeto, logging e diretórios canônicos
│   ├── executores_arquivo/   # Executores de etapa, fase ou pilar isolado
│   └── executores_projeto/   # Torneios completos e servidor FastAPI
├── testes/               # Scripts de teste e homologação
├── artefatos/            # Modelos serializados (.joblib) e manifestos
├── relatorios/           # Figuras, dossiês e laudos de governança
├── dados/                # Brutos (somente leitura) e processados
├── modelos/              # Experimentos e modelos auxiliares
├── Dockerfile            # Imagem de produção do microsserviço
├── docker-compose.yml    # Orquestração local do contêiner
├── pyproject.toml        # Dependências e configuração do Ruff
└── uv.lock               # Resolução determinística de versões
```

A lógica de negócio vive em `src/`. Os arquivos em `scripts/` são pontos de entrada que orquestram chamadas, imprimem laudos e gravam evidências nos diretórios canônicos.

---

## 🗺️ Mapa de Documentação (READMEs por pasta)

```
README.md                                   # Visão geral + este índice
├── src/README.md                           # Camada de código-fonte
│   ├── nucleo/README.md                    # Infraestrutura compartilhada
│   └── etapas/README.md                    # Esteira CRISP-DM
│       ├── fase_01_ingestao/README.md
│       ├── fase_02_exploracao/README.md
│       ├── fase_03_preparacao/README.md
│       ├── fase_04_modelagem/README.md
│       ├── fase_05_avaliacao/README.md
│       └── fase_06_implantacao/README.md
├── scripts/README.md                       # Executores de arquivo e de projeto
├── testes/README.md                        # Testes e homologação
├── dados/README.md                         # Brutos e processados
├── artefatos/README.md                     # Artefatos oficiais de produção
├── modelos/README.md                       # Artefatos experimentais
├── relatorios/README.md                    # Figuras e dossiês
├── logs/README.md                          # Logs operacionais
└── notebooks/README.md                     # Exploração e prototipagem
```

---
