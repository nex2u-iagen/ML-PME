# 📜 Scripts Executores

> **Navegação:** [README raiz](../README.md) · **Código executado:** [src](../src/README.md) · **Fases:** [etapas](../src/etapas/README.md) · **Testes:** [testes](../testes/README.md)

## 🎯 Objetivo

Esta pasta concentra os **pontos de entrada executáveis** do projeto. A lógica de
negócio permanece em `src/`; os scripts aqui apenas orquestram chamadas, imprimem
laudos e gravam artefatos nos diretórios canônicos.

Cada executor aponta para um módulo documentado:

| Executor | Módulo de negócio | README |
| :--- | :--- | :--- |
| `fase_04_ajustar_campeao` | `src.etapas.fase_04_modelagem` | [fase_04](../src/etapas/fase_04_modelagem/README.md) |
| `fase_05_pilar_01_top3` | `pilar_01_podio_top3` | [pilar_01](../src/etapas/fase_05_avaliacao/pilar_01_podio_top3/README.md) |
| `fase_05_pilar_02_custo` | `pilar_02_alinhamento_negocio` | [pilar_02](../src/etapas/fase_05_avaliacao/pilar_02_alinhamento_negocio/README.md) |
| `fase_05_pilar_03_shap` | `pilar_03_explicabilidade_xai` | [pilar_03](../src/etapas/fase_05_avaliacao/pilar_03_explicabilidade_xai/README.md) |
| `fase_05_pilar_04_governanca` | `pilar_04_governanca_homologacao` | [pilar_04](../src/etapas/fase_05_avaliacao/pilar_04_governanca_homologacao/README.md) |
| `fase_06_pilar_01_persistencia` | `pilar_01_persistencia_integridade` | [pilar_01](../src/etapas/fase_06_implantacao/pilar_01_persistencia_integridade/README.md) |
| `fase_06_pilar_02_seguranca` | `pilar_02_seguranca_autenticacao` | [pilar_02](../src/etapas/fase_06_implantacao/pilar_02_seguranca_autenticacao/README.md) |
| `fase_06_pilar_03_contratos` | `pilar_03_contratos_dados` | [pilar_03](../src/etapas/fase_06_implantacao/pilar_03_contratos_dados/README.md) |
| `fase_06_pilar_04_motor_api` | `pilar_04_motor_inferencia_api` | [pilar_04](../src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/README.md) |
| `torneio_classificacao` | `orquestrador_torneio_classificacao` | [fase_04](../src/etapas/fase_04_modelagem/README.md) |
| `torneio_regressao` | `orquestrador_torneio_regressao` | [fase_04](../src/etapas/fase_04_modelagem/README.md) |
| `torneio_agrupamento` | `orquestrador_agrupamento` | [fase_04](../src/etapas/fase_04_modelagem/README.md) |
| `servir_api` | `aplicacao_fastapi` | [pilar_04](../src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/README.md) |

A separação responde a duas necessidades distintas:

| Pasta | README | Escopo | Use quando… |
| :--- | :--- | :--- | :--- |
| [`executores_arquivo/`](executores_arquivo/README.md) | [detalhes](executores_arquivo/README.md) | **Etapa, fase ou pilar isolado** | Você quer homologar um artefato específico (ex.: gerar o dossiê da Fase 5, testar os contratos da Fase 6). |
| [`executores_projeto/`](executores_projeto/README.md) | [detalhes](executores_projeto/README.md) | **Fluxo completo ou serviço** | Você quer rodar um torneio inteiro de modelagem ou subir o microsserviço de inferência. |

---

## 🧭 Regras de Invocação

Os scripts devem ser executados **como módulos**, a partir da raiz do projeto, para
que os imports `scripts.*` e `src.*` funcionem sem ajustes manuais de `sys.path`:

```bash
uv run python -m scripts.executores_arquivo.<nome_do_script>
uv run python -m scripts.executores_projeto.<nome_do_script>
```

O `scripts/bootstrap.py` é o ponto comum de inicialização. Ele fornece:

* `RAIZ_PROJETO` — raiz absoluta do repositório, independente do diretório atual.
* `DIRETORIO_ARTEFATOS` e `DIRETORIO_RELATORIOS` — caminhos canônicos de saída.
* `configurar_ambiente()` — garante a raiz no `sys.path` e padroniza o logging.

> ⚠️ Evite `python scripts/.../arquivo.py`: a execução direta quebra a resolução dos
> pacotes `scripts` e `src`. Use sempre a forma `python -m`.

---

## 🗂️ Executores de Arquivo (`executores_arquivo/`)

Cada script executa **uma unidade de homologação** e grava suas evidências nos
diretórios indicados. A ordem abaixo é a ordem natural do pipeline.

| Script | Fase / Pilar | O que faz | Saídas principais |
| :--- | :--- | :--- | :--- |
| `fase_04_ajustar_campeao.py` | Fase 4 — Modelagem | Separa treino/teste, calibra o SVM com `GridSearchCV` e serializa o pipeline campeão. | `artefatos/modelos/modelo_campeao_svm.joblib` |
| `fase_05_pilar_01_top3.py` | Fase 5 — Pilar 1 | Executa a auditoria comparativa do Top 3 (SVM, XGBoost e KNN) no teste retido. | `relatorios/figuras/fase_05_avaliacao/pilar_01_top3/` |
| `fase_05_pilar_02_custo.py` | Fase 5 — Pilar 2 | Traduz a matriz de confusão em impacto financeiro (R$) e elege o campeão por custo. | Laudo financeiro no terminal |
| `fase_05_pilar_03_shap.py` | Fase 5 — Pilar 3 | Gera explicabilidade forense com SHAP (Beeswarm global e Waterfall individual). | `relatorios/figuras/fase_05_avaliacao/pilar_03_xai/` |
| `fase_05_pilar_04_governanca.py` | Fase 5 — Pilar 4 | Consolida Pilares 1–3 e emite o dossiê executivo do modelo campeão. | `relatorios/governanca/` |
| `fase_06_pilar_01_persistencia.py` | Fase 6 — Pilar 1 | Empacota o pipeline em produção, grava manifesto e valida o hash SHA-256. | `artefatos/modelos_producao/pipeline_svm_calibrado_v1.joblib` e `.json` |
| `fase_06_pilar_02_seguranca.py` | Fase 6 — Pilar 2 | Testa emissão, adulteração, expiração e ausência de token JWT. | Certificado de segurança no terminal |
| `fase_06_pilar_03_contratos.py` | Fase 6 — Pilar 3 | Valida os contratos Pydantic V2 de entrada e resposta da API. | Certificado de contratos no terminal |
| `fase_06_pilar_04_motor_api.py` | Fase 6 — Pilar 4 | Testa o Singleton, a inferência vetorizada e as rotas FastAPI de ponta a ponta. | Certificado do motor/API no terminal |

### Ordem sugerida de execução

```bash
uv run python -m scripts.executores_arquivo.fase_04_ajustar_campeao

uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3
uv run python -m scripts.executores_arquivo.fase_05_pilar_02_custo
uv run python -m scripts.executores_arquivo.fase_05_pilar_03_shap
uv run python -m scripts.executores_arquivo.fase_05_pilar_04_governanca

uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia
uv run python -m scripts.executores_arquivo.fase_06_pilar_02_seguranca
uv run python -m scripts.executores_arquivo.fase_06_pilar_03_contratos
uv run python -m scripts.executores_arquivo.fase_06_pilar_04_motor_api
```

O Pilar 4 da Fase 6 depende do artefato gerado pelo Pilar 1 da Fase 6. Se o binário
não existir, execute a persistência antes.

---

## 🏟️ Executores de Projeto (`executores_projeto/`)

Esses scripts cobrem fluxos maiores: torneios completos de modelagem e o servidor de
produção.

| Script | Escopo | O que faz | Saídas principais |
| :--- | :--- | :--- | :--- |
| `torneio_classificacao.py` | Fase 4 — Classificação | Instancia todos os classificadores da fábrica e roda validação cruzada de 5 dobras. | Ranking no terminal |
| `torneio_regressao.py` | Fase 4 — Regressão | Instancia os regressores da fábrica e ranqueia o campeão por K-Fold. | Ranking no terminal |
| `torneio_agrupamento.py` | Fase 4 — Agrupamento | Compara os agrupadores não supervisionados (ex.: KMeans, DBSCAN, GMM) por silhueta. | Ranking no terminal |
| `servir_api.py` | Fase 6 — Implantação | Sobe o microsserviço FastAPI com Uvicorn na porta 8000. | Serviço HTTP + Swagger em `/docs` |

### Comandos

```bash
uv run python -m scripts.executores_projeto.torneio_classificacao
uv run python -m scripts.executores_projeto.torneio_regressao
uv run python -m scripts.executores_projeto.torneio_agrupamento

uv run python -m scripts.executores_projeto.servir_api
```

Com o servidor no ar, o teste de integração do cliente pode ser executado em outro
terminal:

```bash
uv run python testes/testar_cliente_inferencia.py
```

---

## 🧪 Testes

Os scripts de teste ficam em `testes/` e são independentes dos executores. Para rodar
um teste específico:

```bash
uv run python testes/testar_alg_kmeans.py
```

Para rodar a suíte completa de algoritmos:

```bash
for arquivo in testes/testar_alg_*.py; do
  uv run python "$arquivo" || exit 1
done
```

O teste `testes/testar_cliente_inferencia.py` exige o servidor ativo
(`scripts.executores_projeto.servir_api`).

---

## ➕ Como adicionar um novo executor

1. Escolha a pasta correta:
   * Etapa, fase ou pilar isolado → `executores_arquivo/`.
   * Torneio, pipeline completo ou serviço → `executores_projeto/`.
2. Importe o bootstrap e chame `configurar_ambiente()` no início.
3. Use `RAIZ_PROJETO` para montar qualquer caminho de entrada ou saída; não dependa
   do diretório de onde o comando foi disparado.
4. Proteja a execução com `if __name__ == "__main__":`.
5. Documente o novo script na tabela correspondente deste README.
6. Valide com:

```bash
uv run ruff check .
uv run ruff format --check .
```
