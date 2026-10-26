# 📥 `src/etapas/fase_01_ingestao/` — Ingestão de dados

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Próxima:** [fase_02](../fase_02_exploracao/README.md)

## 🎯 Objetivo

Conectar-se aos dados brutos do ERP, restaurar dumps SQL, converter tabelas para CSV
e disponibilizar as entidades em memória para a exploração. A fase não interpreta
negócio: ela garante que o dado chegue íntegro e em formato tabular.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `dados/brutos/sql/*.sql` e `dados/brutos/csv/*.csv`. |
| **Processa** | Descoberta de entidades, restauração SQLite, exportação em lotes, leitura CSV e validação de integridade. |
| **Entrega para** | [fase_02_exploracao](../fase_02_exploracao/README.md), em `DataFrame`s e CSVs consolidados. |
| **Quem consome** | `OrquestradorRaioXEmpresarial`, `AuditorSaudeDados` e construtores de Data Marts. |

## 🧩 Arquivos

| Arquivo | Classe / função | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `etapa_01_extracao.py` | `OrquestradorIngestao` | `diretorio_raiz: Path`. | Descobre `.sql`/`.csv`, restaura SQLite, exporta tabelas e carrega entidades. | `dict[str, pd.DataFrame]` + CSVs em `dados/brutos/csv/`. |
| `etapa_01_extracao.py` | `criar_dados_sinteticos_erp()` | Raiz do projeto vazia. | Gera clientes e pedidos de venda sintéticos. | Lista de `Path` dos CSVs criados. |
| `__init__.py` | — | — | Marca o pacote. | — |

## 📥 Entradas

| Origem | Formato | Exemplo |
| :--- | :--- | :--- |
| `dados/brutos/sql/` | Dump SQL (DDL + DML). | `erp_backup.sql` |
| `dados/brutos/csv/` | CSV delimitado por vírgula. | `erp_pedidos_vendas.csv` |

## 📤 Saídas

| Destino | Formato | Consumidor |
| :--- | :--- | :--- |
| Memória | `dict[str, pd.DataFrame]` | Fase 02 |
| `dados/brutos/csv/` | `.csv` convertido do SQL | Fase 02 / auditoria |
| Log | Mensagens de volumetria e integridade | Operação |

## 🔁 Fluxo interno

```text
dados/brutos/sql/*.sql
        │ ConectorBancoRelacional.reconstruir_banco_sqlite()
        ▼
   SQLite temporário
        │ exportar_tabela_para_csv()
        ▼
dados/brutos/csv/*.csv
        │ LeitorArquivosTabulares.carregar_tabela()
        ▼
OrquestradorIngestao.executar_fase_ingestao()
        ▼
dict[str, pd.DataFrame]  ──►  fase_02
```

## ▶️ Como executar

Não há executor dedicado na pasta `scripts/` para a Fase 01. O orquestrador pode ser
acionado diretamente:

```python
from pathlib import Path

from src.etapas.fase_01_ingestao.etapa_01_extracao import OrquestradorIngestao

orquestrador = OrquestradorIngestao(Path(".").resolve())
tabelas = orquestrador.executar_fase_ingestao()
```

## 📌 Regras

- `dados/brutos/sql/` e `dados/brutos/csv/` são **somente leitura** como fonte.
- Arquivos massivos devem ser exportados/consumidos em lotes.
- Se as pastas estiverem vazias, o orquestrador pode gerar uma massa sintética para
  testes; isso não substitui dados reais de produção.
- A fase não altera semanticamente os dados; apenas converte e consolida.

## 🔗 Ligações

- Núcleo de leitura: [acesso_dados](../../nucleo/acesso_dados/README.md).
- Próxima fase: [fase_02_exploracao](../fase_02_exploracao/README.md).
- Índice das fases: [src/etapas](../README.md).
