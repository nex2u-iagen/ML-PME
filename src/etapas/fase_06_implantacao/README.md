# 🚀 `src/etapas/fase_06_implantacao/` — Implantação e produção

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Anterior:** [fase_05](../fase_05_avaliacao/README.md)

## 🎯 Objetivo

Levar o modelo homologado da Fase 05 para produção com quatro garantias:
**persistência íntegra**, **segurança**, **contratos de dados** e **serviço de
inferência**.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Pipeline campeão, metadados de governança e regras de negócio da [fase_05](../fase_05_avaliacao/README.md). |
| **Processa** | Serialização comprimida, hash SHA-256, JWT, validação Pydantic e inferência vetorizada. |
| **Entrega para** | Clientes HTTP, sensores de infraestrutura e equipe de operações. |
| **Quem consome** | `scripts.executores_projeto.servir_api`, `testes/testar_cliente_inferencia.py` e consumidores externos. |

## 🧩 Pilares

| Pilar | README | Entrada | Saída | Consumidor |
| :--- | :--- | :--- | :--- | :--- |
| **1 — Persistência e integridade** | [README](pilar_01_persistencia_integridade/README.md) | Pipeline ajustado + metadados. | `.joblib` + manifesto `.json` + hash. | Pilar 4 / operações |
| **2 — Segurança e autenticação** | [README](pilar_02_seguranca_autenticacao/README.md) | Credenciais e segredo. | Token JWT e guarda Bearer. | Pilar 4 / clientes |
| **3 — Contratos de dados** | [README](pilar_03_contratos_dados/README.md) | JSON de entrada e saída. | Esquemas Pydantic válidos. | Pilar 4 / Swagger |
| **4 — Motor e API** | [README](pilar_04_motor_inferencia_api/README.md) | Artefato + manifesto + requisições. | Resposta JSON de inferência. | Clientes HTTP |

## 🔁 Fluxo interno

```text
Fase 05 (campeão homologado + metadados)
        │
        ▼
Pilar 1: EmpacotadorPipelineProducao
        ├──► pipeline_svm_calibrado_v1.joblib
        └──► pipeline_svm_calibrado_v1_manifesto.json (SHA-256)
        │
        ▼
Pilar 4: CarregadorModeloSingleton
        ├── valida hash contra o manifesto
        └── carrega o Pipeline na RAM (uma vez)
        │
        ▼
Pilar 3: EsquemaEntradaPaciente  ──►  MotorPredicaoVetorizado
        │                                      │
        ▼                                      ▼
Pilar 2: Bearer/JWT  ────────────────►  EsquemaRespostaPredicao
                                               │
                                               ▼
                                        Cliente HTTP
```

## 📥 Entradas

| Entrada | Origem | Formato |
| :--- | :--- | :--- |
| Pipeline campeão | Fase 04/05 | objeto Scikit-Learn |
| Metadados | Fase 05 | `MetadadosModeloProducao` |
| Credenciais | Cliente | JSON `usuario`/`senha` |
| Features clínicas | Cliente | JSON com 10 campos |
| Segredo JWT | Ambiente | string ≥ 32 bytes |

## 📤 Saídas

| Saída | Destino | Consumidor |
| :--- | :--- | :--- |
| Binário de produção | `artefatos/modelos_producao/*.joblib` | API |
| Manifesto | `artefatos/modelos_producao/*_manifesto.json` | API / auditoria |
| Token | Resposta HTTP | Cliente |
| Predição | Resposta HTTP | Cliente |
| Saúde | `/saude/prontidao` | Docker/Kubernetes |

## ▶️ Como executar

```bash
# 1. Persistir o campeão
uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia

# 2. Homologar segurança, contratos e motor
uv run python -m scripts.executores_arquivo.fase_06_pilar_02_seguranca
uv run python -m scripts.executores_arquivo.fase_06_pilar_03_contratos
uv run python -m scripts.executores_arquivo.fase_06_pilar_04_motor_api

# 3. Subir o serviço
uv run python -m scripts.executores_projeto.servir_api
```

## 📌 Regras

- O binário de produção nunca é editado manualmente.
- O hash do manifesto deve bater com o binário antes de carregar.
- A chave JWT deve vir de variável de ambiente em produção.
- O modelo é carregado uma única vez (Singleton) e reutilizado.
- Toda entrada passa pelo contrato Pydantic antes de chegar ao motor.

## 🔗 Ligações

- Persistência: [pilar_01](pilar_01_persistencia_integridade/README.md).
- Segurança: [pilar_02](pilar_02_seguranca_autenticacao/README.md).
- Contratos: [pilar_03](pilar_03_contratos_dados/README.md).
- API: [pilar_04](pilar_04_motor_inferencia_api/README.md).
- Voltar para [etapas](../README.md).
