# 🏛️ `src/nucleo/` — Camada de infraestrutura compartilhada

> **Navegação:** [README raiz](../../README.md) · [src](../README.md) · **Subpastas:** [contratos](contratos/README.md) · [acesso_dados](acesso_dados/README.md) · [diagnostico_estatistico](diagnostico_estatistico/README.md) · [aprendizado_maquina](aprendizado_maquina/README.md)

## 🎯 Objetivo

Fornecer componentes reutilizáveis, coesos e desacoplados para todas as fases do
CRISP-DM. O núcleo **não conhece o negócio da fase**: ele recebe dados, caminhos e
parâmetros, executa uma responsabilidade técnica e devolve um resultado reutilizável.

> *"Modelos não tomam decisões, eles reduzem a incerteza. Sem dados limpos,
> arquitetura organizada, explicabilidade e impacto no negócio, a IA é apenas um
> experimento de laboratório."*

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Fases 01–06, scripts e testes: caminhos de arquivo, `DataFrame`, `Series`, matrizes NumPy, modelos treinados e metadados. |
| **Processa** | Leitura/escrita, restauração SQL, cálculos estatísticos, gráficos, transformação de atributos e serialização. |
| **Entrega para** | As próprias fases: `DataFrame`, métricas, figuras `.png`, matrizes transformadas, `.joblib` e manifestos `.json`. |
| **Quem consome** | `src/etapas/`, [`scripts/`](../../scripts/README.md) e [`testes/`](../../testes/README.md). |

```text
                         ┌──────────────────────────────┐
                         │          src/nucleo          │
                         ├──────────────────────────────┤
 dados/brutos ──────────►│ acesso_dados                 │──► DataFrames / CSV
 modelos/*.joblib ──────►│ aprendizado_maquina          │──► arrays / artefatos
 relatorios/*.png ◄──────│ diagnostico_estatistico      │◄── métricas / tabelas
 contratos ◄─────────────│ contratos                    │◄── assinaturas estáticas
                         └──────────────────────────────┘
                                      ▲
                                      │ usado por
                               src/etapas/fase_01..06
```

## 🧩 Submódulos

| Submódulo | README | Finalidade | Consumidores principais |
| :--- | :--- | :--- | :--- |
| `contratos/` | [README](contratos/README.md) | Contratos estruturais com `typing.Protocol`. | Todas as fases (especialmente 01, 03 e 06). |
| `acesso_dados/` | [README](acesso_dados/README.md) | Leitura de CSV, dumps SQL e simulação tributária. | Fases 01, 02, 03 e 06. |
| `diagnostico_estatistico/` | [README](diagnostico_estatistico/README.md) | Estatística formal e gráficos padronizados. | Fase 02 (primário) e Fase 05 (secundário). |
| `aprendizado_maquina/` | [README](aprendizado_maquina/README.md) | Transformadores Scikit-Learn e persistência. | Fases 03, 04, 05 e 06. |

## 📥 O que o núcleo recebe

- **Caminhos** (`pathlib.Path`) para arquivos CSV, dumps SQL, imagens e artefatos.
- **Tabelas** (`pandas.DataFrame`) e **séries** (`pandas.Series`).
- **Matrizes** NumPy (`X`, `y`) já separadas pelas fases.
- **Estimadores** compatíveis com Scikit-Learn.
- **Metadados** de governança (versão, autor, limiar, hash).

## ⚙️ O que o núcleo processa

1. Lê arquivos completos ou em lotes (`chunksize`) sem estourar a RAM.
2. Restaura dumps `.sql` em SQLite e exporta tabelas fatiadas.
3. Calcula média, desvio, assimetria, curtose, Jarque-Bera, correlação e VIF.
4. Renderiza histogramas, boxplots, heatmaps e dispersões em 300 DPI.
5. Trunca outliers por IQR dentro do `Pipeline`, sem data leakage.
6. Serializa pipelines em `.joblib` com manifesto `.json` e hash.
7. Projeta CBS/IBS da reforma tributária para cenários fiscais.

## 📤 O que o núcleo entrega

| Saída | Formato | Quem usa |
| :--- | :--- | :--- |
| Tabela carregada | `pd.DataFrame` | Fases 01–03 |
| Lotes de leitura | gerador de `pd.DataFrame` | Ingestão de bases massivas |
| Banco restaurado | `sqlalchemy.Engine` / `.db` | Fase 01 |
| Tabela exportada | `.csv` | Fase 01 |
| Laudo estatístico | `dict` / `pd.DataFrame` | Fase 02 |
| Figura | `.png` 300 DPI | Fase 02 / relatórios |
| Matriz transformada | `np.ndarray` | Fases 03–06 |
| Modelo persistido | `.joblib` + `.json` | Fases 04–06 |

## 🧱 Princípios de engenharia

1. **Responsabilidade única:** cada arquivo resolve um domínio técnico.
2. **Baixo acoplamento:** as fases dependem de contratos e classes do núcleo, não o
   contrário.
3. **Sem data leakage:** transformadores aprendem apenas no treino (`fit`) e
   reaplicam no teste/inferência (`transform`).
4. **Auditabilidade:** artefatos persistidos sempre acompanhados de manifesto.
5. **Streaming:** bases grandes são lidas em lotes, nunca integralmente sem
   necessidade.

## 🧭 Matriz de reutilização

| Submódulo | Fase 01 | Fase 02 | Fase 03 | Fase 04 | Fase 05 | Fase 06 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `contratos/` | Primário | Secundário | Primário | Secundário | Secundário | Primário |
| `acesso_dados/` | Primário | Primário | Primário | — | — | Primário |
| `diagnostico_estatistico/` | — | Primário | Secundário | — | Primário | — |
| `aprendizado_maquina/` | — | — | Primário | Primário | Primário | Primário |

## 🔗 Ligações

- Voltar para [src](../README.md).
- Ver a esteira de fases em [src/etapas](../etapas/README.md).
- Ver os executores em [scripts](../../scripts/README.md).
