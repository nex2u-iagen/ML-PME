# 💰 `src/etapas/fase_05_avaliacao/pilar_02_alinhamento_negocio/` — Impacto financeiro

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_05](../README.md)

## 🎯 Objetivo

Traduzir a matriz de confusão de cada finalista em um balancete em reais: prejuízo
por omissão (falso negativo), custo de alarme falso, valor preservado (verdadeiro
positivo) e resultado líquido.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Top 3, `X_teste`, `y_teste` e premissas de custo do negócio. |
| **Processa** | Contagem de TP/FP/FN/TN e aplicação dos valores monetários. |
| **Entrega para** | Pilar 4 e decisão executiva do campeão financeiro. |
| **Quem consome** | `OrquestradorGovernanca`, scripts e diretoria. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `configuracao_custos.py` | `ConfiguracaoCustoRisco` | Custos unitários de FN/FP, ganho de VP e custo de VN. | Valida e encapsula as premissas. | Objeto de configuração + resumo. |
| `calculadora_financeira.py` | `CalculadoraImpactoFinanceiro` | Modelo, `X_teste`, `y_teste` e configuração. | Matriz de confusão → valores em R$. | Linha de balancete (`dict`). |
| `orquestrador_alinhamento_negocio.py` | `OrquestradorAlinhamentoNegocio` | Catálogo Top 3 + teste + configuração. | Executa a calculadora para cada modelo e ordena. | Leaderboard financeiro (`pd.DataFrame`). |

## 💵 Premissas (`ConfiguracaoCustoRisco`)

| Campo | Significado | Exemplo usado no projeto |
| :--- | :--- | :--- |
| `custo_falso_negativo` | Perda por não identificar um caso de risco. | R$ 12.000,00 |
| `custo_falso_positivo` | Custo operacional de um alarme falso. | R$ 600,00 |
| `ganho_verdadeiro_positivo` | Valor preservado ao identificar corretamente. | R$ 4.000,00 |
| `custo_verdadeiro_negativo` | Custo de um acerto negativo. | R$ 0,00 |

## 📊 Fórmulas

```text
prejuizo_negligencia = FN × custo_falso_negativo
custo_alarmes        = FP × custo_falso_positivo
valor_preservado     = TP × ganho_verdadeiro_positivo
perda_total_erros    = prejuizo_negligencia + custo_alarmes
resultado_liquido    = valor_preservado - perda_total_erros
```

## 📥 Entradas e 📤 saídas

| Entrada | Formato | Saída | Formato |
| :--- | :--- | :--- | :--- |
| Top 3 + teste | objetos + arrays | Leaderboard financeiro | `pd.DataFrame` |
| Premissas | `ConfiguracaoCustoRisco` | Colunas em R$ | `float` |

Colunas do leaderboard: `Modelo`, `Prejuizo_Negligencia_R$`, `Custo_Alarmes_R$`,
`Perda_Total_Erros_R$`, `Valor_Preservado_R$`, `Resultado_Liquido_R$`.

## 📌 Regras

- O resultado financeiro depende das premissas; documente a origem de cada valor.
- O campeão financeiro pode diferir do campeão técnico. O Pilar 4 decide com ambos.
- Nunca use o teste para escolher premissas.
- O balancete é uma estimativa de cenário, não uma promessa contábil.

## 🔗 Ligações

- Pilar técnico: [pilar_01](../pilar_01_podio_top3/README.md).
- Governança: [pilar_04](../pilar_04_governanca_homologacao/README.md).
- Voltar para [fase_05](../README.md).
