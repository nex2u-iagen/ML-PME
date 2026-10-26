# 📦 `src/etapas/fase_06_implantacao/pilar_01_persistencia_integridade/` — Persistência e integridade

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_06](../README.md)

## 🎯 Objetivo

Congelar o pipeline campeão em um artefato de produção comprimido, acompanhado de um
manifesto de governança com assinatura SHA-256, e garantir que o arquivo possa ser
relido sem corrupção.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Pipeline ajustado da Fase 05 e `MetadadosModeloProducao`. |
| **Processa** | Compressão `joblib`, cálculo de hash, emissão de manifesto e validação. |
| **Entrega para** | Pilar 4 (carregamento na API) e auditoria. |
| **Quem consome** | `CarregadorModeloSingleton`, operações e scripts de homologação. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `empacotador_pipeline.py` | `EmpacotadorPipelineProducao` | Pipeline, metadados e nome base. | Serializa com compressão e emite manifesto. | `dict` com caminhos `.joblib` e `.json`. |
| `metadados_modelo.py` | `MetadadosModeloProducao` | Versão, autor, features, métricas e limiar. | Valida limiar e monta o manifesto JSON. | Arquivo `.json` de governança. |
| `validador_integridade.py` | `ValidadorIntegridadeArtefato` | Caminho do `.joblib` e do manifesto. | Calcula SHA-256 e compara com o hash gravado. | `bool` de conformidade. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Pipeline campeão | objeto Scikit-Learn | Fase 05 |
| Versão | `str` semântica | Governança |
| Autor | `str` | Governança |
| Limiar | `float` entre 0 e 1 | Fase 05 |
| Features | `list[str]` | Fase 03 |
| Métricas | `dict` | Fase 05 |

## 📤 Saídas

| Saída | Caminho padrão | Consumidor |
| :--- | :--- | :--- |
| Binário comprimido | `artefatos/modelos_producao/pipeline_svm_calibrado_v1.joblib` | API |
| Manifesto | `artefatos/modelos_producao/pipeline_svm_calibrado_v1_manifesto.json` | API / auditoria |
| Hash SHA-256 | Campo `hash_sha256` do manifesto | Validador |

## 🔐 Manifesto (conteúdo conceitual)

```json
{
  "versao": "SVM_Calibrado_Producao_v1.0.0",
  "autor": "Dr. Arthur - Líder de ML",
  "features_entrada": ["idade_paciente", "..."],
  "limiar_decisao_homologado": 0.5,
  "hash_sha256": "...64 caracteres...",
  "timestamp_utc": "..."
}
```

## 🔁 Validação

```text
Pipeline + metadados
        │ salvar_pipeline_com_manifesto()
        ├──► .joblib comprimido
        └──► .json com hash
                 │
                 ▼
        ValidadorIntegridadeArtefato
                 │ recalcula SHA-256
                 ▼
        hash calculado == hash do manifesto?
                 ├── sim → artefato íntegro
                 └── não → erro / não carregar
```

## 📌 Regras

- O manifesto é imutável após a publicação.
- O hash deve ser recalculado a cada leitura em produção.
- O limiar precisa estar estritamente entre 0 e 1.
- Nunca sobrescreva um artefato em uso sem versionar o nome.

## 🔗 Ligações

- API que consome: [pilar_04](../pilar_04_motor_inferencia_api/README.md).
- Núcleo de persistência: [aprendizado_maquina](../../../nucleo/aprendizado_maquina/README.md).
- Artefatos gerados: [artefatos/README.md](../../../../artefatos/README.md).
- Voltar para [fase_06](../README.md).
