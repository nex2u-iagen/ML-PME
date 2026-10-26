# 🏢 `src/etapas/fase_02_exploracao/departamentos/` — Diagnósticos departamentais

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_02](../README.md)

## 🎯 Objetivo

Cada arquivo implementa um especialista de negócio. Todos herdam de
[`BaseDepartamento`](../base_departamento.py) e expõem o mesmo contrato:
`executar_diagnostico_completo() -> dict[str, Any]`.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | CSVs brutos do ERP (um ou dois por departamento). |
| **Processa** | KPIs, agregações, curvas e um gráfico executivo por departamento. |
| **Entrega para** | `OrquestradorRaioXEmpresarial`, que consolida o prontuário 360°. |
| **Quem consome** | Fase 03 (referência de negócio) e relatórios executivos. |

## 🧩 Arquivos

| Arquivo | Classe | Fonte(s) | Indicadores principais | Figura gerada |
| :--- | :--- | :--- | :--- | :--- |
| `d01_comercial.py` | `AnalisadorComercial` | `erp_pedidos_vendas.csv`, `erp_clientes.csv` | Faturamento, ticket médio, concentração (Pareto). | `pareto_faturamento_clientes.png` |
| `d02_financeiro.py` | `AnalisadorFinanceiro` | `erp_pedidos_vendas.csv` | Liquidez, solvência, inadimplência. | `distribuicao_status_cobranca.png` |
| `d03_compras.py` | `AnalisadorCompras` | `erp_pedidos_compras.csv` | Prazos, concentração de fornecedores. | `concentracao_compras_fornecedores.png` |
| `d04_estoque.py` | `AnalisadorEstoque` | `erp_saldos_estoque.csv` | Giro, cobertura, curva ABC. | `curva_abc_valor_imobilizado.png` |
| `d05_contabil.py` | `AnalisadorContabil` | `erp_pedidos_vendas.csv` | Custos, margens, ponto de equilíbrio. | `composicao_resultado_contabil.png` |
| `d06_fiscal.py` | `AnalisadorFiscal` | `erp_notas_fiscais.csv` | Carga tributária, alíquotas efetivas. | `carga_tributaria_por_uf.png` |
| `d07_producao.py` | `AnalisadorProducao` | `erp_ordens_producao.csv` | OEE, refugo, eficiência fabril. | `desperdicio_refugo_produtos.png` |
| `d08_logistica.py` | `AnalisadorLogistica` | `erp_expedicao_logistica.csv` | Frete, prazo, nível de serviço. | `tempo_medio_transito_transportadora.png` |
| `d09_pos_venda.py` | `AnalisadorPosVenda` | `erp_sac_chamados.csv` | MTTR, reincidência, atrito. | `motivos_reclamacao_sac.png` |
| `d10_recursos_humanos.py` | `AnalisadorRecursosHumanos` | `erp_funcionarios_folha.csv` | Folha, turnover, custo por setor. | `custo_folha_por_setor.png` |
| `__init__.py` | — | — | Marca o pacote. | — |

## 📥 Entradas e 📤 saídas

Cada especialista:

1. **Recebe** o caminho da pasta de dados brutos e a pasta de relatórios (injetados
   pela base).
2. **Processa** as tabelas com pandas e o núcleo estatístico/visual.
3. **Entrega** um dicionário com métricas, tabelas intermediárias e o `Path` da figura.

```python
{
    "departamento": "Comercial",
    "metricas": {...},
    "figura": Path("relatorios/figuras/comercial/pareto_faturamento_clientes.png"),
}
```

## 🔗 Ligações

- Base comum: [`../base_departamento.py`](../base_departamento.py).
- Orquestrador: [`../etapa_02_raio_x_empresarial.py`](../etapa_02_raio_x_empresarial.py).
- Núcleo de visualização: [diagnostico_estatistico](../../../nucleo/diagnostico_estatistico/README.md).
- Voltar para [fase_02](../README.md).
