# 🗣️ `src/etapas/fase_04_modelagem/fabrica_modelos/nlp/` — Reservado para NLP

> **Navegação:** [README raiz](../../../../../README.md) · [fabrica](../README.md) · [fase_04](../../README.md)

## 🎯 Objetivo

Reservar o espaço para algoritmos de Processamento de Linguagem Natural (NLP), como
vetorização de texto, classificação de sentimentos e extração de entidades.

## 🔄 Estado atual

| Item | Situação |
| :--- | :--- |
| Implementações | Nenhuma. |
| Conteúdo | `__init__.py` e este README. |
| Uso no fluxo | Nenhum. |

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Nada no estado atual. |
| **Processa** | Nada; pasta reservada. |
| **Entrega para** | Nada; pasta reservada. |
| **Quem consome** | Ninguém até a primeira implementação. |

## 📌 Regras para implementação futura

- Todo algoritmo deve herdar de [`ModeloBase`](../base_modelo.py).
- A entrada deve ser texto ou matriz de features textuais.
- O pipeline deve ser serializável com `joblib`.
- Crie teste em `testes/` e documente o modelo aqui.

## 🔗 Ligações

- Fábrica: [fabrica_modelos](../README.md).
- Contrato: [ModeloBase](../base_modelo.py).
- Voltar para [fase_04](../../README.md).
