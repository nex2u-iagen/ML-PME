# 🌐 `src/etapas/fase_06_implantacao/pilar_04_motor_inferencia_api/` — Motor e API

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_06](../README.md)

## 🎯 Objetivo

Expor o modelo como microsserviço HTTP: carregar o artefato uma única vez na RAM,
validar o hash, autenticar a requisição, vetorizar as 10 features, aplicar o limiar e
devolver a resposta em poucos milissegundos.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `.joblib` + manifesto (Pilar 1), token Bearer (Pilar 2) e JSON validado (Pilar 3). |
| **Processa** | Singleton, checagem SHA-256, vetorização NumPy, predição e limiar. |
| **Entrega para** | Clientes HTTP, Swagger e sondas de infraestrutura. |
| **Quem consome** | `scripts.executores_projeto.servir_api`, `testes/testar_cliente_inferencia.py`, Docker/Kubernetes. |

## 🧩 Arquivos

| Arquivo | Classe / função | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `carregador_modelo_singleton.py` | `CarregadorModeloSingleton` | Caminho do `.joblib` e do manifesto. | Valida SHA-256 e carrega o pipeline uma vez. | Pipeline ativo em RAM. |
| `motor_predicao_vetorizado.py` | `MotorPredicaoVetorizado` | `EsquemaEntradaPaciente` + pipeline. | Matriz C-contígua `float64`, `predict_proba`, limiar e latência. | `(classe, probabilidade, ms)`. |
| `aplicacao_fastapi.py` | `aplicacao_api` | Requisições HTTP. | Lifespan, rotas, autenticação e resposta Pydantic. | JSON HTTP. |

## 🔌 Rotas

| Método | Rota | Autenticação | Entrada | Saída |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Não | — | Redireciona para `/docs` |
| `GET` | `/docs` | Não | — | Swagger UI |
| `GET` | `/openapi.json` | Não | — | Especificação OpenAPI |
| `POST` | `/autenticacao/token` | Não | `usuario`, `senha` | `access_token`, `token_type`, `expira_em_minutos` |
| `GET` | `/saude/prontidao` | Não | — | Status + `modelo_carregado_ram` |
| `POST` | `/predicao/risco_cardiovascular` | Bearer JWT | 10 features clínicas | `EsquemaRespostaPredicao` |

## 🔁 Ciclo de vida (Lifespan)

```text
Startup
  └── CarregadorModeloSingleton.carregar_modelo_producao()
          ├── valida SHA-256 contra o manifesto
          └── Pipeline na RAM (uma única instância)

Requisição
  └── Bearer → valida token
  └── Pydantic → valida 10 features
  └── MotorPredicaoVetorizado → probabilidade + limiar
  └── EsquemaRespostaPredicao → JSON

Shutdown
  └── liberar_memoria()
```

## 📥 Entradas

| Entrada | Formato | Validação |
| :--- | :--- | :--- |
| Artefato | `.joblib` | Hash SHA-256 contra manifesto |
| Manifesto | `.json` | Versão, limiar, features |
| Login | JSON | Credenciais |
| Predição | JSON | `EsquemaEntradaPaciente` |
| Token | Header Bearer | Assinatura e expiração |

## 📤 Saídas

| Saída | Formato | Consumidor |
| :--- | :--- | :--- |
| Token | JSON | Cliente |
| Prontidão | JSON | Docker/Kubernetes |
| Predição | JSON | Cliente |
| Erros | `401`, `422`, `503` | Cliente |

## ▶️ Como executar

```bash
uv run python -m scripts.executores_projeto.servir_api
```

O servidor sobe em `http://127.0.0.1:8000`, com Swagger em `/docs`.

## 📌 Regras

- O modelo não pode ser recarregado a cada requisição.
- Se o hash não bater, a API não deve iniciar.
- A matriz de entrada deve ser `float64` e C-contígua.
- O limiar vem do manifesto, não do código.
- A rota de predição exige Bearer válido.
- A rota de saúde não exige autenticação e deve ser leve.

## 🔗 Ligações

- Persistência: [pilar_01](../pilar_01_persistencia_integridade/README.md).
- Segurança: [pilar_02](../pilar_02_seguranca_autenticacao/README.md).
- Contratos: [pilar_03](../pilar_03_contratos_dados/README.md).
- Cliente de teste: [`testes/testar_cliente_inferencia.py`](../../../../testes/testar_cliente_inferencia.py).
- Voltar para [fase_06](../README.md).
