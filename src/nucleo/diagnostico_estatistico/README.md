# 📊 `src/nucleo/diagnostico_estatistico/` — Estatística e visualização

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [nucleo](../README.md)

## 🎯 Objetivo

Fornecer rigor matemático e padronização visual para a análise exploratória:
medidas de forma, testes de normalidade, correlação, multicolinearidade e gráficos
prontos para relatório.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Fase 02 (tabelas brutas) e Fase 05 (resíduos e métricas). |
| **Processa** | Estatística descritiva/inferencial e renderização de figuras. |
| **Entrega para** | Laudos da Fase 02 e evidências visuais em `relatorios/figuras/`. |
| **Quem consome** | `BaseDepartamento`, `AuditorSaudeDados`, `OrquestradorRaioXEmpresarial` e análises da Fase 05. |

## 🧩 Arquivos

| Arquivo | Classe principal | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `testes_hipoteses.py` | `CalculadoraEstatistica` | `pd.Series` ou `pd.DataFrame` numérico. | Média, desvio, assimetria, curtose, Jarque-Bera, Pearson/Spearman e VIF. | `dict` de métricas ou `pd.DataFrame` de correlação/VIF. |
| `visualizacao_grafica.py` | `GeradorVisualizacaoGrafica` | `DataFrame`, nomes de colunas e caminho de saída. | Histograma+KDE, boxplot, heatmap e dispersão com regressão. | Arquivo `.png` em 300 DPI e `Path` de destino. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Série contínua | `pd.Series` | Coluna de tabela da Fase 01/02 |
| Tabela numérica | `pd.DataFrame` | Entidades do ERP |
| Matriz de correlação | `pd.DataFrame` | Calculada pelo próprio módulo |
| Caminho de saída | `Path` | `relatorios/figuras/<departamento>/` |

## 📤 Saídas

| Saída | Formato | Consumidor |
| :--- | :--- | :--- |
| Laudo de distribuição | `dict` com média, desvio, assimetria, curtose e p-valor | Laudo departamental |
| Matriz de correlação | `pd.DataFrame` | Heatmap / relatório |
| VIF | `pd.DataFrame` ordenado | Diagnóstico de multicolinearidade |
| Figura | `.png` 300 DPI | Dossiês e dashboards |

## 📌 Regras

- O módulo não decide regras de negócio; apenas calcula e desenha.
- Figuras devem ser salvas com `bbox_inches="tight"` e resolução 300 DPI.
- O VIF só deve ser calculado sobre variáveis numéricas contínuas.
- Correlação não implica causalidade; a interpretação pertence à fase de negócio.

## 🔗 Ligações

- Consumidor principal: [fase_02_exploracao](../../etapas/fase_02_exploracao/README.md).
- Contrato de visualização: [contratos](../contratos/README.md).
- Voltar para [nucleo](../README.md).
