# 📄 `scripts/executores_arquivo/` — Executores de etapa, fase ou pilar

> **Navegação:** [README raiz](../../README.md) · [scripts](../README.md) · [src](../../src/README.md)

## 🎯 Objetivo

Executar **uma unidade de homologação por vez**: calibrar o campeão, rodar um pilar
da Fase 05 ou validar um pilar da Fase 06. Cada script imprime um laudo e grava
apenas as evidências daquela unidade.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Dados sintéticos (quando o script é autossuficiente) ou artefatos das fases anteriores. |
| **Processa** | Treino, avaliação, explicabilidade, persistência, segurança, contratos ou API. |
| **Entrega para** | `artefatos/`, `relatorios/` e terminal. |
| **Quem consome** | Homologação, CI, auditoria e desenvolvedores. |

## 🧩 Arquivos

| Script | Módulo acionado | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `fase_04_ajustar_campeao.py` | `Orquestrador` + SVM calibrado | Base sintética de classificação. | Split holdout, padronização, `GridSearchCV`, métricas. | `artefatos/modelos/modelo_campeao_svm.joblib` + relatório. |
| `fase_05_pilar_01_top3.py` | `OrquestradorPodioTop3` | Base sintética + 3 finalistas. | Scorecard e 3 gráficos comparativos. | `relatorios/figuras/fase_05_avaliacao/pilar_01_top3/*.png`. |
| `fase_05_pilar_02_custo.py` | `OrquestradorAlinhamentoNegocio` | Base sintética + 3 finalistas + custos. | Matriz de confusão → R$. | Leaderboard financeiro no terminal. |
| `fase_05_pilar_03_shap.py` | `OrquestradorExplicabilidadeShap` | Base sintética + pipeline SVM. | SHAP global e local. | `relatorios/figuras/fase_05_avaliacao/pilar_03_xai/*.png`. |
| `fase_05_pilar_04_governanca.py` | `OrquestradorGovernanca` | Executa P1–P3 internamente. | Compila laudos, aplica aceite e monta dossiê. | `relatorios/governanca/dossie_homologacao_executiva.md` + figuras solo. |
| `fase_06_pilar_01_persistencia.py` | `EmpacotadorPipelineProducao` | Pipeline treinado + metadados. | Compressão, manifesto SHA-256 e validação. | `artefatos/modelos_producao/pipeline_svm_calibrado_v1.joblib` + `.json`. |
| `fase_06_pilar_02_seguranca.py` | `GerenciadorTokenJWT` + guardião | Credenciais e tokens de teste. | Emissão, adulteração, expiração e ausência de Bearer. | Certificado de segurança no terminal. |
| `fase_06_pilar_03_contratos.py` | `EsquemaEntradaPaciente` / `EsquemaRespostaPredicao` | Payloads válidos e inválidos. | Validação Pydantic V2 e serialização. | Certificado de contratos no terminal. |
| `fase_06_pilar_04_motor_api.py` | Singleton + motor + rotas | Artefato de produção e requisições simuladas. | Carrega modelo, mede latência e testa rotas. | Certificado do motor/API no terminal. |

## ▶️ Como executar

```bash
# Fase 04
uv run python -m scripts.executores_arquivo.fase_04_ajustar_campeao

# Fase 05 (na ordem)
uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3
uv run python -m scripts.executores_arquivo.fase_05_pilar_02_custo
uv run python -m scripts.executores_arquivo.fase_05_pilar_03_shap
uv run python -m scripts.executores_arquivo.fase_05_pilar_04_governanca

# Fase 06 (persistência antes do motor)
uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia
uv run python -m scripts.executores_arquivo.fase_06_pilar_02_seguranca
uv run python -m scripts.executores_arquivo.fase_06_pilar_03_contratos
uv run python -m scripts.executores_arquivo.fase_06_pilar_04_motor_api
```

## 📌 Regras

- Sempre executar a partir da raiz e via `python -m`.
- O Pilar 4 da Fase 06 depende do artefato gerado pelo Pilar 1.
- Scripts que geram artefatos não devem ser executados em paralelo entre si.
- Cada script deve permanecer idempotente: rodar de novo sobrescreve a mesma saída.

## 🔗 Ligações

- Índice dos executores: [scripts/README.md](../README.md).
- Executores de fluxo completo: [executores_projeto](../executores_projeto/README.md).
- Fases: [src/etapas](../../src/etapas/README.md).
