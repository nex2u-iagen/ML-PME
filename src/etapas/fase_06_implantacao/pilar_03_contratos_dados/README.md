# 🧾 `src/etapas/fase_06_implantacao/pilar_03_contratos_dados/` — Contratos de dados

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_06](../README.md)

## 🎯 Objetivo

Definir, com Pydantic V2, o contrato exato de entrada (10 variáveis clínicas) e de
saída (resposta da predição). O contrato impede que dados inválidos cheguem ao
modelo e garante que a resposta seja consumível por sistemas externos.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | JSON do cliente (entrada) e resultado do motor (saída). |
| **Processa** | Validação de tipos, limites biológicos, campos obrigatórios e ordenação. |
| **Entrega para** | Pilar 4 (motor e API) e Swagger/OpenAPI. |
| **Quem consome** | `MotorPredicaoVetorizado`, `aplicacao_fastapi` e clientes. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `esquema_entrada_paciente.py` | `EsquemaEntradaPaciente` | 10 campos clínicos. | Valida tipos/limites e exporta vetor ordenado. | `list[float]` na ordem de treino. |
| `esquema_resposta_predicao.py` | `EsquemaRespostaPredicao` | Decisão, probabilidade, limiar, severidade e latência. | Serializa e valida a resposta. | JSON de saída. |

## 📥 Contrato de entrada (10 features)

| # | Campo | Tipo | Papel |
| :-: | :--- | :--- | :--- |
| 1 | `idade_paciente` | `int` | Idade em anos |
| 2 | `pressao_sistolica` | `float` | Pressão arterial sistólica |
| 3 | `colesterol_total` | `float` | Colesterol total |
| 4 | `frequencia_cardiaca` | `float` | Frequência cardíaca |
| 5 | `glicemia_jejum` | `float` | Glicemia em jejum |
| 6 | `indice_massa_corporal` | `float` | IMC |
| 7 | `infradesnivel_st` | `float` | Infradesnível do segmento ST |
| 8 | `historico_familiar` | `int` | Histórico familiar (0/1) |
| 9 | `nivel_sedentarismo` | `int` | Nível de sedentarismo |
| 10 | `tempo_internacao_previo` | `float` | Tempo de internação prévio |

O método `exportar_vetor_ordenado()` devolve os valores **na ordem canônica** usada
no treino do pipeline.

## 📤 Contrato de saída

| Campo | Tipo | Significado |
| :--- | :--- | :--- |
| `classe_predita` | `int` | 0 ou 1 |
| `diagnostico_rotulo` | `str` | Rótulo legível |
| `probabilidade_risco` | `float` | Probabilidade da classe positiva |
| `limiar_decisao_aplicado` | `float` | Limiar homologado |
| `grau_severidade` | `str` | `BAIXO`, `MODERADO`, `ELEVADO`, `CRÍTICO` |
| `versao_modelo_producao` | `str` | Versão do artefato |
| `tempo_processamento_ms` | `float` | Latência da inferência |

## 🔁 Fluxo de validação

```text
JSON do cliente
      │
      ▼
EsquemaEntradaPaciente (Pydantic)
      │ válido
      ▼
exportar_vetor_ordenado() ──► [10 floats]
      │
      ▼
MotorPredicaoVetorizado
      │
      ▼
EsquemaRespostaPredicao (Pydantic)
      │
      ▼
JSON de resposta
```

## 📌 Regras

- Campo ausente ou fora dos limites biológicos → `422 Unprocessable Entity`.
- A ordem do vetor é parte do contrato: não altere sem versionar o modelo.
- A resposta deve sempre informar a versão do modelo e o limiar aplicado.
- Novos campos exigem atualização do esquema, do motor e dos testes.

## 🔗 Ligações

- Motor que consome: [pilar_04](../pilar_04_motor_inferencia_api/README.md).
- Teste de contratos: [`scripts/executores_arquivo/fase_06_pilar_03_contratos.py`](../../../../scripts/executores_arquivo/fase_06_pilar_03_contratos.py).
- Voltar para [fase_06](../README.md).
