# 🔍 `src/etapas/fase_05_avaliacao/pilar_03_explicabilidade_xai/` — Explicabilidade com SHAP

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_05](../README.md)

## 🎯 Objetivo

Abrir a caixa-preta do modelo campeão: medir a contribuição de cada atributo para a
probabilidade prevista, globalmente (população) e localmente (um paciente/cliente).

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Função de probabilidade do pipeline, `X_treino` (referência) e `X_avaliacao` (indivíduos). |
| **Processa** | `shap.Explainer`, valores de Shapley, ranking de importância e gráficos. |
| **Entrega para** | Pilar 4 (dossiê) e explicabilidade para o negócio/auditoria. |
| **Quem consome** | `OrquestradorGovernanca`, scripts e relatórios executivos. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `configuracao_shap.py` | `ConfiguracaoShap` | Nomes das features, nº de amostras de fundo, semente. | Valida e encapsula parâmetros. | Objeto de configuração. |
| `calculadora_shap.py` | `CalculadoraValoresShap` | Função de probabilidade, `X_treino`, `X_avaliacao`. | Calcula valores SHAP e importância média. | Matriz SHAP + tabela de impacto. |
| `gerador_graficos_shap.py` | `GeradorGraficosShap` | Valores SHAP e metadados. | Beeswarm global e waterfall individual. | 2+ `.png` em `relatorios/figuras/fase_05_avaliacao/pilar_03_xai/`. |
| `orquestrador_explicabilidade.py` | `OrquestradorExplicabilidadeShap` | Função de probabilidade + dados. | Coordena cálculo e renderização. | `dict` com tabela e caminhos das figuras. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Função de probabilidade | `Callable[[np.ndarray], np.ndarray]` | Pipeline campeão |
| Base de referência | `np.ndarray` (treino) | Fase 03/04 |
| Indivíduos avaliados | `np.ndarray` (teste) | Fase 03 |
| Nomes das features | `list[str]` | Fase 03 |

## 📤 Saídas

| Saída | Formato | Destino |
| :--- | :--- | :--- |
| Valores SHAP | `np.ndarray` | Memória / tabela |
| Ranking de importância | `pd.DataFrame` | Pilar 4 |
| Impacto global | `.png` | `xai_impacto_global_sumario.png` |
| Cascata individual | `.png` | `xai_cascata_individual_amostra_<i>.png` |

## 📌 Regras

- A função de probabilidade deve devolver a probabilidade da **classe positiva**.
- A base de fundo deve vir do treino, nunca do teste.
- SHAP explica o modelo, não prova causalidade.
- O número de amostras de fundo deve equilibrar fidelidade e custo computacional.
- Cada figura deve ser salva em 300 DPI.

## 🔗 Ligações

- Pilar financeiro: [pilar_02](../pilar_02_alinhamento_negocio/README.md).
- Governança: [pilar_04](../pilar_04_governanca_homologacao/README.md).
- Script executor: [scripts/README.md](../../../../scripts/README.md).
- Voltar para [fase_05](../README.md).
