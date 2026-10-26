# 📦 `dados/brutos/` — Fontes imutáveis

> **Navegação:** [README raiz](../../README.md) · [dados](../README.md) · **Subpastas:** [csv](csv/README.md) · [sql](sql/README.md)

## 🎯 Objetivo

Guardar as fontes originais do ERP sem transformação. Esta camada é a **verdade de
entrada** do pipeline e não deve ser editada por scripts.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Exportações do ERP e backups relacionais. |
| **Processa** | Nada. Armazenamento bruto. |
| **Entrega para** | Fase 01 (ingestão), que converte e consolida. |
| **Quem consome** | `OrquestradorIngestao`, `LeitorArquivosTabulares`, `ConectorBancoRelacional`. |

## 🧩 Estrutura

| Pasta | README | Formato | Conteúdo |
| :--- | :--- | :--- | :--- |
| `csv/` | [README](csv/README.md) | `.csv` | Tabelas exportadas do ERP. |
| `sql/` | [README](sql/README.md) | `.sql` | Dumps de banco relacional. |

> As pastas `CSV/` e `SQL/` (maiúsculas) existem vazias e não são usadas pelo código.
> O padrão oficial é minúsculo.

## 📌 Regras

- **Somente leitura**: nenhum script deve alterar arquivos desta árvore.
- Dados sensíveis não podem ser versionados.
- A fase 01 pode gravar CSVs convertidos em `csv/`, mas nunca alterar o dump original.
- Nomes de arquivos devem seguir o padrão `erp_<entidade>.csv`.

## 🔗 Ligações

- Ingestão: [fase_01](../../src/etapas/fase_01_ingestao/README.md).
- Núcleo de I/O: [acesso_dados](../../src/nucleo/acesso_dados/README.md).
- Voltar para [dados](../README.md).
