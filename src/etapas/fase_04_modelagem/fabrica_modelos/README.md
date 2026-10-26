# 🏭 `src/etapas/fase_04_modelagem/fabrica_modelos/` — Fábrica de modelos

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_04](../README.md)

## 🎯 Objetivo

Oferecer um catálogo homogêneo de algoritmos. Cada especialista herda de
[`ModeloBase`](base_modelo.py) e implementa dois métodos:

```python
construir_estimador(semente_aleatoria=42) -> estimador
obter_grade_hiperparametros() -> dict[str, list]
```

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Nenhum dado no import. Recebe apenas a semente ao construir. |
| **Processa** | Instancia o algoritmo e declara a grade de hiperparâmetros. |
| **Entrega para** | Orquestradores de torneio, otimizador, scripts e testes. |
| **Quem consome** | `OrquestradorTorneioClassificacao`, `OrquestradorTorneioRegressao`, `OrquestradorAgrupamento`, `OtimizadorHiperparametros`. |

## 🧩 Estrutura

| Caminho | README | Conteúdo |
| :--- | :--- | :--- |
| `base_modelo.py` | — | Contrato abstrato `ModeloBase`. |
| `supervisionado/` | [README](supervisionado/README.md) | Classificação e regressão. |
| `supervisionado/classificacao/` | [README](supervisionado/classificacao/README.md) | 11 classificadores. |
| `supervisionado/regressao/` | [README](supervisionado/regressao/README.md) | 10 regressores. |
| `nao_supervisionado/` | [README](nao_supervisionado/README.md) | Agrupamento, anomalias e redução. |
| `nao_supervisionado/agrupamento/` | [README](nao_supervisionado/agrupamento/README.md) | 5 agrupadores. |
| `nao_supervisionado/deteccao_anomalias/` | [README](nao_supervisionado/deteccao_anomalias/README.md) | 5 detectores. |
| `nao_supervisionado/reducao_dimensionalidade/` | [README](nao_supervisionado/reducao_dimensionalidade/README.md) | 5 redutores. |
| `nlp/` | [README](nlp/README.md) | Reservado; contém `__init__.py` e README, sem algoritmos. |
| `redes_neurais/` | [README](redes_neurais/README.md) | Reservado; contém README, sem `__init__.py` nem algoritmos. |

## 🧱 Contrato `ModeloBase`

| Método | Entrada | Processamento | Saída |
| :--- | :--- | :--- | :--- |
| `construir_estimador(semente_aleatoria=42)` | Semente inteira. | Instancia o algoritmo com configuração padrão. | Estimador Scikit-Learn não treinado. |
| `obter_grade_hiperparametros()` | Nenhuma. | Declara parâmetros e valores a testar. | `dict[str, list]`. |

## 📥 Entradas e 📤 saídas

| Momento | Entrada | Saída |
| :--- | :--- | :--- |
| Construção | Semente | Estimador não treinado |
| Calibração | `X_treino`, `y_treino` | Melhor estimador ajustado |
| Avaliação | `X_teste` | Predições / probabilidades |

## 📌 Regras

- Todo novo algoritmo deve herdar de `ModeloBase`.
- Nenhuma classe da fábrica lê arquivo ou grava artefato; isso é papel dos
  orquestradores e do núcleo.
- A grade deve conter apenas parâmetros válidos do estimador.
- Pastas reservadas (`nlp`, `redes_neurais`) não são carregadas pelo fluxo atual.

## 🔗 Ligações

- Torneios: [fase_04](../README.md).
- Testes: [testes/README.md](../../../../testes/README.md).
- Voltar para [src/etapas](../../README.md).
