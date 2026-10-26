# 📈 `relatorios/` — Evidências e relatórios gerados

> **Navegação:** [README raiz](../README.md) · **Produtores:** [fase_02](../src/etapas/fase_02_exploracao/README.md) · [fase_05](../src/etapas/fase_05_avaliacao/README.md)

## 🎯 Objetivo

Concentrar as saídas legíveis por humanos: figuras de diagnóstico, gráficos
comparativos, explicabilidade SHAP e o dossiê de homologação.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Fase 02 (diagnósticos) e Fase 05 (pódio, SHAP e governança). |
| **Processa** | Nada. Apenas armazena artefatos visuais e Markdown. |
| **Entrega para** | Diretoria, auditores, dashboards e dossiês. |
| **Quem consome** | Pessoas e ferramentas de apresentação. |

## 🧩 Estrutura

| Caminho | Origem | Conteúdo |
| :--- | :--- | :--- |
| `figuras/comercial/` | Fase 02 | Pareto de faturamento. |
| `figuras/financeiro/` | Fase 02 | Status de cobrança. |
| `figuras/compras/` | Fase 02 | Concentração de fornecedores. |
| `figuras/estoque/` | Fase 02 | Curva ABC. |
| `figuras/contabil/` | Fase 02 | Composição do resultado. |
| `figuras/fiscal/` | Fase 02 | Carga tributária por UF. |
| `figuras/producao/` | Fase 02 | Refugo/desperdício. |
| `figuras/logistica/` | Fase 02 | Tempo de trânsito. |
| `figuras/pos_venda/` | Fase 02 | Motivos de reclamação. |
| `figuras/recursos_humanos/` | Fase 02 | Custo de folha. |
| `figuras/fase_05_avaliacao/pilar_01_top3/` | Fase 05/P1 | Matrizes, ROC e PR do Top 3. |
| `figuras/fase_05_avaliacao/pilar_03_xai/` | Fase 05/P3 | SHAP global e waterfall. |
| `figuras/fase_05_avaliacao/campeao_solo/` | Fase 05/P4 | Matriz, ROC e PR só do campeão. |
| `governanca/dossie_homologacao_executiva.md` | Fase 05/P4 | Dossiê executivo final. |

## 📥 Entradas e 📤 saídas

| Entrada | Saída |
| :--- | :--- |
| Dados + modelos | `.png` 300 DPI |
| Laudos dos pilares | `.md` de governança |

## 📌 Regras

- Tudo aqui é **gerado**; não edite manualmente.
- Figuras devem ter 300 DPI e nomes descritivos.
- O dossiê referencia as figuras por caminho relativo.
- Relatórios não substituem os artefatos de modelo.
- Ao regerar, preserve a versão anterior se ela sustenta uma auditoria.

## 🔗 Ligações

- Diagnósticos: [fase_02](../src/etapas/fase_02_exploracao/README.md).
- Governança: [fase_05/pilar_04](../src/etapas/fase_05_avaliacao/pilar_04_governanca_homologacao/README.md).
- Dossiê atual: [`governanca/dossie_homologacao_executiva.md`](governanca/dossie_homologacao_executiva.md).
