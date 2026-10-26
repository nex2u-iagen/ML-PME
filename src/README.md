# 🧱 `src/` — Código-fonte do projeto

> **Navegação:** [README raiz](../README.md) · **Subpastas:** [nucleo](nucleo/README.md) · [etapas](etapas/README.md)

## 🎯 Objetivo

Concentrar todo o código Python do projeto em duas camadas com responsabilidades
bem separadas:

| Camada | Pasta | Papel |
| :--- | :--- | :--- |
| **Núcleo reutilizável** | [`nucleo/`](nucleo/README.md) | Ferramentas genéricas de I/O, estatística, visualização, transformação e persistência. Não conhece regras de uma fase específica. |
| **Esteira CRISP-DM** | [`etapas/`](etapas/README.md) | Orquestra as fases 01 a 06, aplicando as ferramentas do núcleo ao negócio da PME. |

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `dados/brutos/` (arquivos CSV/SQL), configurações e artefatos de fases anteriores. |
| **Processa** | Ingestão, diagnóstico, preparação, modelagem, avaliação, explicabilidade, implantação e inferência. |
| **Entrega para** | `dados/processados/`, `artefatos/`, `relatorios/` e o microsserviço HTTP. |
| **Quem consome** | Scripts em [`scripts/`](../scripts/README.md), testes em [`testes/`](../testes/README.md) e clientes da API. |

```text
dados/brutos ──► etapas/fase_01 ──► etapas/fase_02 ──► etapas/fase_03
                                                         │
                                      ┌──────────────────┴──────────────────┐
                                      ▼                                     ▼
                          dados/processados/bi                 dados/processados/ml
                          (dashboards)                                   │
                                                                          ▼
                                          etapas/fase_04 ──► etapas/fase_05 ──► etapas/fase_06
                                                                                  │
                                                                                  ▼
                                                                  artefatos/modelos_producao
                                                                  + API FastAPI
```

## 🧩 Estrutura

| Pasta | README | Responsabilidade |
| :--- | :--- | :--- |
| `nucleo/` | [nucleo/README.md](nucleo/README.md) | Camada de infraestrutura compartilhada. |
| `nucleo/contratos/` | [contratos/README.md](nucleo/contratos/README.md) | Protocolos estruturais (`typing.Protocol`). |
| `nucleo/acesso_dados/` | [acesso_dados/README.md](nucleo/acesso_dados/README.md) | Leitura de CSV, dumps SQL e simulação tributária. |
| `nucleo/diagnostico_estatistico/` | [diagnostico_estatistico/README.md](nucleo/diagnostico_estatistico/README.md) | Testes estatísticos e gráficos padronizados. |
| `nucleo/aprendizado_maquina/` | [aprendizado_maquina/README.md](nucleo/aprendizado_maquina/README.md) | Transformadores e persistência de modelos. |
| `etapas/` | [etapas/README.md](etapas/README.md) | Orquestração das fases CRISP-DM. |
| `etapas/fase_01_ingestao/` | [README](etapas/fase_01_ingestao/README.md) | Ingestão de dados brutos. |
| `etapas/fase_02_exploracao/` | [README](etapas/fase_02_exploracao/README.md) | EDA e diagnósticos departamentais. |
| `etapas/fase_03_preparacao/` | [README](etapas/fase_03_preparacao/README.md) | Data Marts de BI e matrizes de ML. |
| `etapas/fase_04_modelagem/` | [README](etapas/fase_04_modelagem/README.md) | Fábrica de modelos e torneios. |
| `etapas/fase_05_avaliacao/` | [README](etapas/fase_05_avaliacao/README.md) | Métricas, custo, SHAP e governança. |
| `etapas/fase_06_implantacao/` | [README](etapas/fase_06_implantacao/README.md) | Persistência, segurança, contratos e API. |

## 🔗 Regra de dependência

```text
etapas/  ──depende de──►  nucleo/  ──depende de──►  bibliotecas externas
```

O caminho inverso é proibido: o núcleo **não importa** nada de `etapas/`. Quando uma
ferramenta nasce em uma fase e passa a ser usada por outra, ela deve ser promovida
para o núcleo.

## 📌 Convenções

- Type hints modernos (`X | None`, `list[str]`).
- Docstrings no estilo Google.
- Nomes de identificadores em português.
- Nenhum segredo ou dado sensível versionado.
- Validação obrigatória com `ruff check .` e `ruff format --check .`.

## 🔗 Ligações

- Núcleo reutilizável: [nucleo/README.md](nucleo/README.md).
- Esteira de fases: [etapas/README.md](etapas/README.md).
- Executores: [scripts/README.md](../scripts/README.md).
- Testes: [testes/README.md](../testes/README.md).
- Voltar para o [README raiz](../README.md).
