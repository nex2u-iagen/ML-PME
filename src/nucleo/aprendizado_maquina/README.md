# 🤖 `src/nucleo/aprendizado_maquina/` — Transformadores e persistência

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [nucleo](../README.md)

## 🎯 Objetivo

Oferecer componentes de engenharia de atributos compatíveis com o Scikit-Learn e
uma camada única de persistência de modelos com manifesto de governança. É a ponte
entre a preparação dos dados e o ciclo de vida dos artefatos.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Fase 03 (matrizes de treino/teste), Fase 04 (modelos ajustados) e Fase 06 (pipeline campeão). |
| **Processa** | Truncamento IQR sem data leakage, serialização `.joblib`, leitura de manifesto `.json`. |
| **Entrega para** | Pipelines de ML, artefatos de produção e validadores de integridade. |
| **Quem consome** | `OrquestradorDadosML`, `OrquestradorIngestao`, `etapa_04_01_orquestrador_baseline`, Fase 06 e testes. |

## 🧩 Arquivos

| Arquivo | Classe principal | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `transformadores_dados.py` | `TruncadorDeValoresExtremos` | `X` numérico (treino no `fit`, teste no `transform`). | Aprende limites Q1/Q3 ± 1,5·IQR e aplica clipping. | `np.ndarray` truncado; nomes de features preservados. |
| `persistencia_artefatos.py` | `GerenciadorPersistenciaModelos` | Pipeline treinado, `Path` de destino e `dict` de metadados. | Serializa com `joblib`, grava manifesto JSON e relê o artefato. | `.joblib` + `.json`; modelo carregado em memória. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Matriz de atributos | `pd.DataFrame` / `np.ndarray` | Fase 03 |
| Alvo | `np.ndarray` | Fase 03/04 |
| Modelo/pipeline | objeto Scikit-Learn | Fase 04/05 |
| Metadados | `dict` (versão, autor, métricas, features) | Fase 04/05/06 |

## 📤 Saídas

| Saída | Formato | Consumidor |
| :--- | :--- | :--- |
| Matriz truncada | `np.ndarray` | `Pipeline` de treino/inferência |
| Modelo serializado | `.joblib` | Fase 05/06 e API |
| Manifesto | `.json` | Auditoria e `CarregadorModeloSingleton` |
| Modelo carregado | objeto Python | Inferência e reavaliação |

## 🔁 Fluxo de persistência

```text
Pipeline ajustado (fase 04/05)
        │
        ▼
GerenciadorPersistenciaModelos.salvar_modelo_com_metadados()
        ├──► modelos/*.joblib            (experimento)
        └──► modelos/*.json              (metadados)
        │
        ▼
Fase 06: EmpacotadorPipelineProducao
        ├──► artefatos/modelos_producao/*.joblib
        └──► artefatos/modelos_producao/*_manifesto.json
```

## 📌 Regras

- `fit()` só pode ver dados de treino; `transform()` nunca aprende.
- O truncador não cria nem remove colunas: `get_feature_names_out()` devolve os
  mesmos nomes recebidos.
- Todo artefato persistido deve ter manifesto correspondente.
- O manifesto é a fonte de verdade para versão, autor, limiar e hash.

## 🔗 Ligações

- Consumidor principal: [fase_03_preparacao](../../etapas/fase_03_preparacao/README.md).
- Persistência de produção: [fase_06/pilar_01](../../etapas/fase_06_implantacao/pilar_01_persistencia_integridade/README.md).
- Voltar para [nucleo](../README.md).
