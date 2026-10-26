# 🚨 `src/etapas/fase_04_modelagem/fabrica_modelos/nao_supervisionado/deteccao_anomalias/` — Detecção de anomalias

> **Navegação:** [README raiz](../../../../../../README.md) · [src](../../../../../README.md) · [etapas](../../../../README.md) · [fase_04](../../../README.md) · [fabrica](../../README.md) · [nao_supervisionado](../README.md)

## 🎯 Objetivo

Identificar transações, clientes ou registros fora do padrão. Todos os algoritmos
seguem a convenção do Scikit-Learn: `+1` para normal e `-1` para anomalia.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Scripts/testes de anomalias e análises exploratórias, com `X` padronizado. |
| **Processa** | Ajuste da fronteira de normalidade e score de anomalia. |
| **Entrega para** | Rótulos `+1`/`-1` e scores para auditoria. |
| **Quem consome** | Testes, investigação de fraude/erro e relatórios. |

## 🧩 Arquivos

| Arquivo | Classe | Método | Característica |
| :--- | :--- | :--- | :--- |
| `alg_isolation_forest_anomalias.py` | `AlgoritmoIsolationForest` | Ensemble de isolamento | Eficiente em alta dimensão. |
| `alg_lof_anomalias.py` | `AlgoritmoLOF` | Densidade local | Detecta anomalias locais. |
| `alg_one_class_svm_anomalias.py` | `AlgoritmoOneClassSVM` | Fronteira de suporte | Bom em bases pequenas/médias. |
| `alg_sgd_one_class_svm_anomalias.py` | `AlgoritmoSGDOneClassSVM` | SGD + kernel RBF | Escalável para bases grandes. |
| `alg_envelope_eliptico_anomalias.py` | `AlgoritmoEnvelopeEliptico` | Covariância robusta | Assume distribuição aproximadamente gaussiana. |

## 📥 Entradas e 📤 saídas

| Método | Entrada | Saída |
| :--- | :--- | :--- |
| `construir_estimador(42)` | Semente | Detector não treinado |
| `fit(X)` | Matriz padronizada | Fronteira aprendida |
| `predict(X)` | Matriz padronizada | `+1` normal / `-1` anomalia |
| `decision_function(X)` | Matriz padronizada | Score contínuo de anormalidade |

## 📌 Regras

- A taxa de contaminação (`contamination`) deve ser definida com o negócio.
- Padronização é obrigatória para LOF, One-Class SVM e Envelope Elíptico.
- `-1` não significa fraude automaticamente; significa desvio do padrão aprendido.
- Avalie com dados rotulados quando existirem; caso contrário, faça inspeção manual.

## 🔗 Ligações

- Teste da ala: [`testes/testar_deteccao_anomalias.py`](../../../../../../testes/testar_deteccao_anomalias.py).
- Voltar para [nao_supervisionado](../README.md).
