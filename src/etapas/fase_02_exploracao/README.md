# 🔎 `src/etapas/fase_02_exploracao/` — Exploração e diagnóstico

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Anterior:** [fase_01](../fase_01_ingestao/README.md) · **Próxima:** [fase_03](../fase_03_preparacao/README.md)

## 🎯 Objetivo

Entender os dados antes de transformá-los. A fase combina uma auditoria macro de
saúde dos dados com dez diagnósticos departamentais, produzindo laudos numéricos e
figuras que orientam a preparação e o storytelling executivo.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | CSVs consolidados da [fase_01](../fase_01_ingestao/README.md). |
| **Processa** | Volumetria, nulos, duplicatas, tipos, KPIs de 10 departamentos e gráficos. |
| **Entrega para** | [fase_03_preparacao](../fase_03_preparacao/README.md) e relatórios executivos. |
| **Quem consome** | Construtores de Data Marts, gestores de negócio e dossiês. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `etapa_02_diagnostico_geral.py` | `AuditorSaudeDados` | Pasta de CSVs brutos. | Audita volumetria, nulos, duplicatas e tipos por tabela. | `dict` consolidado de saúde dos dados. |
| `etapa_02_raio_x_empresarial.py` | `OrquestradorRaioXEmpresarial` | `raiz_projeto: Path`. | Executa a triagem macro e os 10 departamentos em sequência. | Prontuário 360° com laudos e caminhos de figuras. |
| `base_departamento.py` | `BaseDepartamento` | `pasta_dados_brutos`, `pasta_relatorios`. | Injeta leitor, calculadora e visualizador; padroniza o contrato. | Laudo departamental (`dict`). |
| `departamentos/` | 10 analisadores | Tabelas brutas específicas. | KPIs e gráficos do departamento. | Laudo + `.png` em `relatorios/figuras/<dept>/`. |
| `__init__.py` | — | — | Marca o pacote. | — |

## 📥 Entradas

| Entidade | Arquivo bruto | Usada por |
| :--- | :--- | :--- |
| Clientes | `erp_clientes.csv` | Comercial |
| Pedidos de venda | `erp_pedidos_vendas.csv` | Comercial, Financeiro, Contábil |
| Pedidos de compra | `erp_pedidos_compras.csv` | Compras |
| Saldos de estoque | `erp_saldos_estoque.csv` | Estoque |
| Notas fiscais | `erp_notas_fiscais.csv` | Fiscal |
| Ordens de produção | `erp_ordens_producao.csv` | Produção |
| Expedição/logística | `erp_expedicao_logistica.csv` | Logística |
| Chamados SAC | `erp_sac_chamados.csv` | Pós-Venda |
| Folha de funcionários | `erp_funcionarios_folha.csv` | RH |

## 📤 Saídas

| Destino | Formato | Conteúdo |
| :--- | :--- | :--- |
| Memória | `dict[str, Any]` | Laudo 360° com métricas e caminhos. |
| `relatorios/figuras/comercial/` | `.png` | Pareto de faturamento. |
| `relatorios/figuras/financeiro/` | `.png` | Distribuição de status de cobrança. |
| `relatorios/figuras/compras/` | `.png` | Concentração de compras por fornecedor. |
| `relatorios/figuras/estoque/` | `.png` | Curva ABC do valor imobilizado. |
| `relatorios/figuras/contabil/` | `.png` | Composição do resultado contábil. |
| `relatorios/figuras/fiscal/` | `.png` | Carga tributária por UF. |
| `relatorios/figuras/producao/` | `.png` | Desperdício/refugo por produto. |
| `relatorios/figuras/logistica/` | `.png` | Tempo médio de trânsito por transportadora. |
| `relatorios/figuras/pos_venda/` | `.png` | Motivos de reclamação no SAC. |
| `relatorios/figuras/recursos_humanos/` | `.png` | Custo de folha por setor. |

## ▶️ Como executar

```python
from pathlib import Path

from src.etapas.fase_02_exploracao.etapa_02_raio_x_empresarial import (
    OrquestradorRaioXEmpresarial,
)

raio_x = OrquestradorRaioXEmpresarial(Path(".").resolve())
prontuario = raio_x.executar_raio_x_completo()
```

## 📌 Regras

- A fase é **read-only** sobre os dados brutos.
- Nenhum KPI deve ser calculado sem antes validar nulos e tipos.
- Cada departamento grava em sua própria pasta de figuras.
- A interpretação de negócio fica nos laudos; o núcleo só calcula.

## 🔗 Ligações

- Departamentos em detalhe: [departamentos/README.md](departamentos/README.md).
- Núcleo estatístico: [diagnostico_estatistico](../../nucleo/diagnostico_estatistico/README.md).
- Próxima fase: [fase_03_preparacao](../fase_03_preparacao/README.md).
