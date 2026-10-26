# 🏟️ `scripts/executores_projeto/` — Executores de fluxo completo e serviço

> **Navegação:** [README raiz](../../README.md) · [scripts](../README.md) · [src](../../src/README.md)

## 🎯 Objetivo

Executar fluxos maiores que uma etapa isolada: torneios completos de modelagem e o
servidor de inferência.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Dados sintéticos (torneios) ou artefato de produção (API). |
| **Processa** | Competição entre modelos ou inicialização do servidor Uvicorn. |
| **Entrega para** | Terminal (leaderboards) ou clientes HTTP. |
| **Quem consome** | Cientistas de dados, operações e testes de integração. |

## 🧩 Arquivos

| Script | Módulo acionado | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `torneio_classificacao.py` | `OrquestradorTorneioClassificacao` | Base sintética + 11 classificadores. | K-Fold estratificado e 5 métricas. | Leaderboard no terminal. |
| `torneio_regressao.py` | `OrquestradorTorneioRegressao` | Base sintética + 10 regressores. | K-Fold e R²/RMSE/MAE. | Leaderboard no terminal. |
| `torneio_agrupamento.py` | `OrquestradorAgrupamento` | Blobs sintéticos + 5 agrupadores. | Silhueta, Davies-Bouldin e Calinski-Harabasz. | Leaderboard no terminal. |
| `servir_api.py` | `aplicacao_fastapi` | `.joblib` + manifesto de produção. | Carrega o modelo e sobe Uvicorn na porta 8000. | API HTTP + Swagger. |

## ▶️ Como executar

```bash
uv run python -m scripts.executores_projeto.torneio_classificacao
uv run python -m scripts.executores_projeto.torneio_regressao
uv run python -m scripts.executores_projeto.torneio_agrupamento

# Servidor (exige o artefato da Fase 06/Pilar 1)
uv run python -m scripts.executores_projeto.servir_api
```

## 📌 Regras

- Os torneios usam dados sintéticos para comparar algoritmos em condições iguais;
  eles não substituem o treino com dados reais.
- O servidor não inicia se o hash do artefato não conferir.
- A porta padrão é `8000`; em produção, use variável de ambiente/configuração.
- O processo do servidor é bloqueante; rode em terminal separado.

## 🔗 Ligações

- Índice dos executores: [scripts/README.md](../README.md).
- Executores de etapa: [executores_arquivo](../executores_arquivo/README.md).
- Modelagem: [fase_04](../../src/etapas/fase_04_modelagem/README.md).
- API: [fase_06/pilar_04](../../src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/README.md).
