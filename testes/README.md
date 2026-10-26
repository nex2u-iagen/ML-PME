# 🧪 `testes/` — Scripts de teste e homologação

> **Navegação:** [README raiz](../README.md) · **Relacionados:** [src](../src/README.md) · [scripts](../scripts/README.md)

## 🎯 Objetivo

Validar arquitetura e comportamento dos componentes sem depender de um framework de
testes externo. Cada arquivo é um **script executável** com `if __name__ == "__main__":`,
que imprime o que está validando e termina com código de saída 0 em caso de sucesso.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Dados sintéticos gerados dentro do próprio teste. |
| **Processa** | Instancia algoritmos, treina, prediz e compara resultados esperados. |
| **Entrega para** | Terminal (logs) e código de saída para CI. |
| **Quem consome** | Desenvolvedores, CI e revisão de PR. |

## 🧩 Arquivos

### Classificação

| Arquivo | Alvo testado | O que valida |
| :--- | :--- | :--- |
| `testar_alg_adaboost.py` | `AlgoritmoAdaBoost` | Construção, treino, predição e probabilidade. |
| `testar_alg_naive_bayes.py` | `AlgoritmoNaiveBayes` | Conformidade e inferência probabilística. |
| `testar_alg_qda.py` | `AlgoritmoQDA` | Fronteiras e predição. |
| `testar_alg_sgd.py` | `AlgoritmoSGD` | Treino, predição e calibração. |

### Regressão

| Arquivo | Alvos testados | O que valida |
| :--- | :--- | :--- |
| `testar_alg_regressao_linear.py` | `AlgoritmoRegressaoLinear` | OLS, coeficientes e predição. |
| `testar_elasticnet_sgd_regressao.py` | `AlgoritmoElasticNet`, `AlgoritmoSGDRegressor` | Regularização híbrida e SGD. |
| `testar_huber_arvore_regressao.py` | `AlgoritmoHuber`, `AlgoritmoArvoreRegressao` | Robustez e árvore. |
| `testar_regularizacao_regressao.py` | `AlgoritmoRidge`, `AlgoritmoLasso` | L1/L2 e seleção. |
| `testar_rf_svr_regressao.py` | `AlgoritmoRandomForestRegressor`, `AlgoritmoSVR` | Ensemble e margem. |
| `testar_xgboost_regressao.py` | `AlgoritmoXGBoostRegressor` | Boosting e predição. |

### Não supervisionado

| Arquivo | Alvos testados | O que valida |
| :--- | :--- | :--- |
| `testar_agrupamento_nao_supervisionado.py` | Agrupadores | Polimorfismo e labels. |
| `testar_alg_dbscan.py` | `AlgoritmoDBSCAN` | Densidade e ruído. |
| `testar_alg_kmeans.py` | `AlgoritmoKMeans` | Centroides e inércia. |
| `testar_deteccao_anomalias.py` | Detectores | Convenção `+1`/`-1`. |
| `testar_reducao_dimensionalidade.py` | Redutores | Transformação e dimensionalidade. |

### Integração

| Arquivo | Alvo | Pré-requisito |
| :--- | :--- | :--- |
| `testar_cliente_inferencia.py` | API FastAPI | Servidor ativo em `http://127.0.0.1:8000`. |

## ▶️ Como executar

Um teste individual:

```bash
uv run python testes/testar_alg_kmeans.py
```

Todos os testes de algoritmos:

```bash
for arquivo in testes/testar_alg_*.py; do
  uv run python "$arquivo" || exit 1
done
```

Suíte completa (exceto integração):

```bash
for arquivo in testes/*.py; do
  case "$arquivo" in
    *testar_cliente_inferencia.py) continue ;;
  esac
  uv run python "$arquivo" || exit 1
done
```

Teste de integração:

```bash
# terminal 1
uv run python -m scripts.executores_projeto.servir_api

# terminal 2
uv run python testes/testar_cliente_inferencia.py
```

## 📌 Regras

- Todo teste deve ser determinístico (`random_state=42`).
- Não dependa de dados reais ou serviços externos, exceto o teste de integração.
- Um teste deve falhar com `assert` claro e mensagem em português.
- Ao criar um algoritmo novo na fábrica, crie o teste correspondente.
- Os testes atuais são scripts; uma migração futura para `pytest` é possível sem
  alterar a lógica de validação.

## 🔗 Ligações

- Fábrica de modelos: [src/etapas/fase_04_modelagem/fabrica_modelos](../src/etapas/fase_04_modelagem/fabrica_modelos/README.md).
- API: [src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api](../src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/README.md).
- Executores: [scripts/README.md](../scripts/README.md).
