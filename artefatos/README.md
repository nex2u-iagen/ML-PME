# 🏺 `artefatos/` — Artefatos oficiais de modelo

> **Navegação:** [README raiz](../README.md) · **Produtores:** [fase_04](../src/etapas/fase_04_modelagem/README.md) · [fase_06](../src/etapas/fase_06_implantacao/README.md)

## 🎯 Objetivo

Guardar os artefatos que fazem parte do **caminho oficial de produção**: o modelo
campeão da Fase 04 e o pacote versionado da Fase 06 com manifesto e hash.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Fase 04 (campeão) e Fase 06/Pilar 1 (pacote de produção). |
| **Processa** | Nada. É um diretório de persistência. |
| **Entrega para** | API FastAPI, scripts de avaliação e auditoria. |
| **Quem consome** | `CarregadorModeloSingleton`, `scripts` e testes. |

## 🧩 Estrutura

| Caminho | Origem | Papel | Consumidor |
| :--- | :--- | :--- | :--- |
| `modelos/modelo_campeao_svm.joblib` | `fase_04_ajustar_campeao.py` | Pipeline SVM calibrado da Fase 04. | Fase 05 / avaliação |
| `modelos_producao/pipeline_svm_calibrado_v1.joblib` | `fase_06_pilar_01_persistencia.py` | Binário comprimido oficial de produção. | API |
| `modelos_producao/pipeline_svm_calibrado_v1_manifesto.json` | `fase_06_pilar_01_persistencia.py` | Versão, autor, features, limiar e SHA-256. | API / auditoria |

## 📥 Entradas e 📤 saídas

| Entrada | Saída |
| :--- | :--- |
| Pipeline treinado + metadados | `.joblib` + `_manifesto.json` |
| Nome base versionado | Caminhos confirmados |

## 🔁 Ciclo de vida

```text
Fase 04 (calibração)
      └──► artefatos/modelos/modelo_campeao_svm.joblib
                    │
                    ▼
Fase 05 (avaliação/homologação)
                    │
                    ▼
Fase 06/Pilar 1
      ├──► artefatos/modelos_producao/pipeline_svm_calibrado_v1.joblib
      └──► artefatos/modelos_producao/pipeline_svm_calibrado_v1_manifesto.json
                    │
                    ▼
API FastAPI (carrega e valida hash)
```

## 📌 Regras

- Não edite binários manualmente.
- Todo `.joblib` de produção deve ter manifesto correspondente.
- O hash do manifesto deve ser validado antes de qualquer carga.
- Novas versões devem usar novo nome base; não sobrescreva a versão em uso.
- Estes arquivos são **artefatos**, não código-fonte.

## 🔗 Ligações

- Persistência: [fase_06/pilar_01](../src/etapas/fase_06_implantacao/pilar_01_persistencia_integridade/README.md).
- API: [fase_06/pilar_04](../src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/README.md).
- Modelos experimentais: [modelos/README.md](../modelos/README.md).
