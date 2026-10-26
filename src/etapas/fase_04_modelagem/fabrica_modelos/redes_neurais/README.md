# 🧠 `src/etapas/fase_04_modelagem/fabrica_modelos/redes_neurais/` — Reservado para redes neurais

> **Navegação:** [README raiz](../../../../../README.md) · [fabrica](../README.md) · [fase_04](../../README.md)

## 🎯 Objetivo

Reservar o espaço para modelos de aprendizado profundo (MLP, CNN, RNN, Transformers)
que venham a ser incorporados ao catálogo.

## 🔄 Estado atual

| Item | Situação |
| :--- | :--- |
| Implementações | Nenhuma. |
| Conteúdo | Este README (sem `__init__.py`). |
| Uso no fluxo | Nenhum. |

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Nada no estado atual. |
| **Processa** | Nada; pasta reservada. |
| **Entrega para** | Nada; pasta reservada. |
| **Quem consome** | Ninguém até a primeira implementação. |

## 📌 Regras para implementação futura

- Todo modelo deve herdar de [`ModeloBase`](../base_modelo.py).
- Exponha `construir_estimador()` e `obter_grade_hiperparametros()`.
- Prefira integração compatível com Scikit-Learn (`fit`/`predict`/`predict_proba`).
- Documente requisitos de GPU e tempo de treino.
- Crie teste em `testes/` e README próprio ao implementar.

## 🔗 Ligações

- Fábrica: [fabrica_modelos](../README.md).
- Contrato: [ModeloBase](../base_modelo.py).
- Voltar para [fase_04](../../README.md).
