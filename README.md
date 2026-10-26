# 🧠 Arquitetura de Pipeline e Descoberta Analítica para ERPs de PMEs

Este projeto implementa uma arquitetura modular de ponta a ponta voltada para a ingestão, diagnóstico estatístico, descoberta de hipóteses e modelagem preditiva a partir de backups e dados transacionais de ERPs (Enterprise Resource Planning - Sistemas Integrados de Gestão Empresarial) de Pequenas e Médias Empresas (PMEs).

O projeto é guiado pelos princípios de **Alta Coesão** (módulos focados em um único propósito) e **Baixo Acoplamento** (independência funcional entre componentes), seguindo a metodologia CRISP-DM e conformidade estrita com padrões industriais de engenharia de software.

---

## 🏛️ Diretrizes de Engenharia e Governança

### 1. Filosofia de Governança
> *"Modelos não tomam decisões, eles reduzem a incerteza. Sem dados limpos, arquitetura organizada, explicabilidade e impacto no negócio, a IA é apenas um experimento de laboratório."*

### 2. Imutabilidade e Blindagem de Dados
* `dados/brutos/sql/`: **Somente leitura**. Destinado a *dumps* brutos e arquivos `.sql` de bancos relacionais (Postgres, MySQL, Firebird, SQL Server).
* `dados/brutos/csv/`: **Somente leitura**. Destinado a arquivos delimitados exportados originalmente ou fatiados a partir do SQL.
* `dados/processados/`: Destinado exclusivamente a conjuntos transformados, tratados e prontos para treinamento analítico.
* **Segurança da Informação:** Dados protegidos por sigilo industrial e conformidade com LGPD/GDPR não devem ser versionados em repositórios remotos (bloqueio estrito via `.gitignore`).

### 3. Padrão de Qualidade de Código (Ruff)
Todo o código Python deste projeto adere às convenções da PEP 8 e documentação no estilo Google através do **Ruff**:
* **Linter (Analisador Estático):** Fiscalização de variáveis não utilizadas, conformidade semântica e ausência de dead code.
* **Formatter (Formatador Automático):** Quebra padronizada de linhas (88 caracteres), indentação uniforme e ordenação semântica de importações (`isort`).
* **Idioma:** Variáveis, nomes de classes, funções e *docstrings* exclusivamente em Português do Brasil (pt-br).

---

## 🛠️ Ecossistema Tecnológico e Padrões de Uso

| Ferramenta / Biblioteca | Categoria | Finalidade e Padrão de Uso |
| :--- | :--- | :--- |
| **`uv`** | Gerenciador de Pacotes | Substitui `pip`, `venv` e `poetry`. Gerencia dependências em milissegundos com resolução determinística de versões. |
| **`Ruff`** | Qualidade de Código | Linter e formatador escrito em Rust. Executado antes de qualquer consolidação de código para garantir conformidade estrita. |
| **`SQLAlchemy`** | Ingestão e Conexão | *Database Engine* (Motor de Banco de Dados) e abstração SQL. Utilizado com cursores e fracionamento em lotes (*chunking*) para ler transações massivas sem saturar a memória RAM. |
| **`pandas`** | Manipulação Tabular | Criação e agregação de *DataFrames* (tabelas bidimensionais em memória). Padrão de uso: operações vetorizadas, sem laços de repetição lentos (*no for loops*). |
| **`numpy`** | Computação Numérica | Operações de álgebra linear e manipulação de matrizes multidimensionais de alta performance. |
| **`statsmodels`** | Rigor Estatístico | Módulo Python focado na estimativa de modelos estatísticos, exploração e condução de testes de hipóteses formais[cite: 2]. |
| **`seaborn` & `matplotlib`**| Visualização de Dados | Geração de diagnósticos gráficos (distribuições de probabilidade, gráficos de dispersão e matrizes de correlação). |
| **`scikit-learn`** | Engenharia e Modelagem | Padrão-ouro para algoritmos clássicos de aprendizado supervisionado e não supervisionado, pré-processamento e construção de *Pipelines* robustos[cite: 6]. |
| **`AutoGluon`** | AutoML de Alta Performance| Ferramenta de AutoML que automatiza o treinamento de múltiplos modelos de ponta com poucas linhas de código[cite: 4]. |

---

## 🚀 Guia de Inicialização do Ambiente

Quando autorizado o início das operações de terminal, execute a sequência abaixo para preparar a sala limpa de desenvolvimento:

```bash
# 1. Inicializar o ecossistema com uv
uv init pipeline_ml
cd pipeline_ml

# 2. Criar e ativar o ambiente virtual isolado
uv venv ambiente_virtual

# No Linux / macOS:
source ambiente_virtual/bin/activate
# No Windows (PowerShell):
.\ambiente_virtual\Scripts\Activate.ps1

# 3. Sincronizar as dependências científicas e de banco
uv pip install pandas numpy sqlalchemy seaborn statsmodels scikit-learn autogluon

# 4. Adicionar ferramentas de desenvolvimento e qualidade
uv add --dev ruff

# 5. Comandos de validação de qualidade (Ruff)
uv run ruff check .       # Inspeciona conformidade e más práticas
uv run ruff format .      # Aplica a formatação automática
```

---

## 🗂️ Estrutura de Diretórios

```text
projeto_ml/
├── src/
│   ├── etapas/                  # Lógica das fases CRISP-DM (01 a 06)
│   │   ├── fase_01_ingestao/
│   │   ├── fase_02_exploracao/
│   │   ├── fase_03_preparacao/
│   │   ├── fase_04_modelagem/
│   │   ├── fase_05_avaliacao/
│   │   └── fase_06_implantacao/
│   └── nucleo/                  # Componentes reutilizáveis (dados, ML, contratos)
├── scripts/
│   ├── bootstrap.py             # Raiz do projeto, logging e diretórios canônicos
│   ├── executores_arquivo/      # Executores de etapa, fase ou pilar isolado
│   └── executores_projeto/      # Torneios completos e servidor FastAPI
├── testes/                      # Scripts de teste e homologação
├── artefatos/                   # Modelos serializados (.joblib) e manifestos
├── relatorios/                  # Figuras, dossiês e laudos de governança
├── dados/                       # Brutos (somente leitura) e processados
├── modelos/                     # Experimentos e modelos auxiliares
├── Dockerfile                   # Imagem de produção do microsserviço
├── docker-compose.yml           # Orquestração local do contêiner
├── pyproject.toml               # Dependências e configuração do Ruff
└── uv.lock                      # Resolução determinística de versões
```

A lógica de negócio vive em `src/`. Os arquivos em `scripts/` são apenas pontos de
entrada: orquestram chamadas, imprimem laudos e gravam evidências nos diretórios
canônicos.

---

## 🗺️ Mapa de Documentação (READMEs por pasta)

Cada pasta relevante possui um README próprio, interligado ao pai, aos filhos e às
fases vizinhas. O template comum responde: **objetivo**, **o que recebe**, **o que
processa**, **o que entrega**, **de quem para quem** e **quais arquivos** compõem o
módulo.

```text
README.md                                   # Visão geral + este índice
│
├── src/README.md                           # Camada de código-fonte
│   ├── nucleo/README.md                    # Infraestrutura compartilhada
│   │   ├── contratos/README.md             # Protocolos estruturais
│   │   ├── acesso_dados/README.md          # CSV, SQL e tributos
│   │   ├── diagnostico_estatistico/README.md
│   │   └── aprendizado_maquina/README.md
│   │
│   └── etapas/README.md                    # Esteira CRISP-DM
│       ├── fase_01_ingestao/README.md
│       ├── fase_02_exploracao/README.md
│       │   └── departamentos/README.md
│       ├── fase_03_preparacao/README.md
│       │   ├── marts_bi/README.md
│       │   └── engenharia_ml/README.md
│       ├── fase_04_modelagem/README.md
│       │   └── fabrica_modelos/README.md
│       │       ├── supervisionado/README.md
│       │       │   ├── classificacao/README.md
│       │       │   └── regressao/README.md
│       │       ├── nao_supervisionado/README.md
│       │       │   ├── agrupamento/README.md
│       │       │   ├── deteccao_anomalias/README.md
│       │       │   └── reducao_dimensionalidade/README.md
│       │       ├── nlp/README.md
│       │       └── redes_neurais/README.md
│       ├── fase_05_avaliacao/README.md
│       │   ├── pilar_01_podio_top3/README.md
│       │   ├── pilar_02_alinhamento_negocio/README.md
│       │   ├── pilar_03_explicabilidade_xai/README.md
│       │   └── pilar_04_governanca_homologacao/README.md
│       └── fase_06_implantacao/README.md
│           ├── pilar_01_persistencia_integridade/README.md
│           ├── pilar_02_seguranca_autenticacao/README.md
│           ├── pilar_03_contratos_dados/README.md
│           └── pilar_04_motor_inferencia_api/README.md
│
├── scripts/README.md                       # Executores de arquivo e de projeto
│   ├── executores_arquivo/README.md        # Etapa, fase ou pilar isolado
│   └── executores_projeto/README.md        # Torneios e servidor
├── testes/README.md                        # Testes e homologação
├── dados/README.md                         # Brutos e processados
│   ├── brutos/README.md                    # Fontes imutáveis
│   │   ├── csv/README.md                   # Tabelas exportadas do ERP
│   │   └── sql/README.md                   # Dumps relacionais
│   └── processados/README.md               # Produtos analíticos
│       ├── bi/README.md                    # Data Marts para dashboards
│       └── ml/README.md                    # ABT e partições de ML
├── artefatos/README.md                     # Artefatos oficiais de produção
├── modelos/README.md                       # Artefatos experimentais
├── relatorios/README.md                    # Figuras e dossiês
├── logs/README.md                          # Logs operacionais
└── notebooks/README.md                     # Exploração e prototipagem
```

### Atalhos por camada

| Camada | Entrada | O que documenta |
| :--- | :--- | :--- |
| **Código** | [src/README.md](src/README.md) | Núcleo reutilizável + etapas CRISP-DM. |
| **Núcleo** | [src/nucleo/README.md](src/nucleo/README.md) | I/O, estatística, transformação e persistência. |
| **Etapas** | [src/etapas/README.md](src/etapas/README.md) | Fluxo completo da Fase 01 à 06. |
| **Execução** | [scripts/README.md](scripts/README.md) | Comandos `python -m` e mapa de cada executor. |
| **Validação** | [testes/README.md](testes/README.md) | Testes por algoritmo e teste de integração. |
| **Dados** | [dados/README.md](dados/README.md) | Entradas brutas e produtos processados. |
| **Artefatos** | [artefatos/README.md](artefatos/README.md) | Modelo oficial, manifesto e hash. |
| **Saídas** | [relatorios/README.md](relatorios/README.md) | Figuras, SHAP e dossiê executivo. |

---

## ▶️ Execução dos Scripts

Os executores são divididos em duas categorias:

* **`scripts/executores_arquivo/`** — rodam uma etapa, fase ou pilar isolado
  (ex.: `fase_05_pilar_04_governanca`, `fase_06_pilar_03_contratos`).
* **`scripts/executores_projeto/`** — rodam um fluxo maior
  (ex.: `torneio_classificacao`, `servir_api`).

Sempre invoque **como módulo**, a partir da raiz do projeto:

```bash
# Exemplo de executor de arquivo (Fase 4)
uv run python -m scripts.executores_arquivo.fase_04_ajustar_campeao

# Exemplo de executor de projeto (torneio completo)
uv run python -m scripts.executores_projeto.torneio_classificacao

# Servidor FastAPI de produção
uv run python -m scripts.executores_projeto.servir_api
```

> ⚠️ Não execute `python scripts/.../arquivo.py` diretamente: a forma `-m` preserva a
> resolução dos pacotes `scripts` e `src`.

O mapa completo de scripts, saídas geradas e ordem recomendada de execução está em
[`scripts/README.md`](scripts/README.md).

---

## ✅ Validação de Qualidade

Antes de consolidar qualquer alteração, execute:

```bash
uv run ruff check .          # Lint (PEP 8, imports, docstrings, nomes)
uv run ruff format --check . # Confere a formatação de 88 colunas
uv run python -m compileall -q src scripts testes
```

Testes de algoritmos podem ser executados individualmente:

```bash
uv run python testes/testar_alg_kmeans.py
```# ML-PME
