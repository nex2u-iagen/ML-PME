# 📄 RELATÓRIO FINAL — CRISP-DM Operacional

**Projeto:** Arquitetura de Pipeline e Descoberta Analítica para ERPs de PMEs  
**Autor:** Eliezer Henrique (auxílio OpenCode; modelos Nemotron 3.5 Super VL 120B A12B e MIMO v2 — validação de modelos)  
**Base de dados:** Mercadinho Vencedor 10/2026 — *Dataset privado, não compartilhado*  
**Data:** 03/11/2026  
**Versão:** 1.0 — Fase Final de Aprimoramento

---

## 1. Visão Geral da Entrega

Este relatório consolida a fase final de aprimoramento da aplicação CRISP-DM, contemplando:

- **Plataforma operacional** (porta 8502): Ingestão, Raio-X, Torneio, Valor e Predição.
- **Vitrine executiva** (porta 8503): Fluxo CRISP-DM em 13 etapas, Saúde 360° e Relatórios departamentais.
- **Links cruzados** entre as duas aplicações para navegação integrada.
- **Novas funções:** validação de tamanho do dataset (linhas × colunas no upload; ABT + partições no Torneio), formulário de predição de produção com problema vinculado.

---

## 2. Imagens Geradas

Todas as imagens abaixo foram geradas e validadas visualmente (renderização via Chrome headless para SVG e leitura direta para PNG).

### 2.1 Fluxograma CRISP-DM (13 etapas)

| Arquivo | Formato | Local | Descrição |
|---------|---------|-------|-----------|
| `fluxo_crisp_dm.svg` | SVG | `src/app/fluxo_crisp_dm.svg` | Pipeline real em 13 etapas, 6 fases de banda, laço de iteração CRISP-DM. |

Renderizado e verificado com `google-chrome --headless --screenshot`.

### 2.2 Dashboard de Saúde 360°

| Arquivo | Formato | Local | Dimensões |
|---------|---------|-------|-----------|
| `dashboard_saude_360.png` | PNG 200 DPI | `relatorios/mercadinho-v4/mercadinho-v4/fase_02/dashboard_saude_360.png` | 16×9 |

Conteúdo da placa:
- **Radar de Saúde 360°** — índice geral 82/100 (margem, carga tributária, inadimplência, folha/receita, cobertura de estoque, integridade dos dados).
- **8 cartões de KPI** — receita, IMC, carga tributária, inadimplência, folha média, equipe ativa, capital imobilizado, consumo das carteiras.
- **Semáforo de sinais** — 6 linhas com status SAUDÁVEL / ATENÇÃO / CRÍTICO / SEM DADO.

### 2.3 Relatórios Departamentais da Fase 02

| Departamento | PNGs | Destaque |
|--------------|------|----------|
| Comercial | 3 | Pareto por departamento (11 depts), evolução faturamento 12 meses, Pareto categorias |
| Compras | 1 | — |
| Contábil | 2 | DRE 12 meses, composição resultado contábil |
| Estoque | 1 | Top 10 produtos + giro (Curva ABC substituída) |
| Financeiro | 2 | Top 10 carteiras (consumo R$130.750,03, líder PRISCILA), distribuição status cobrança |
| Fiscal | 3 | Composição tributária real, carga tributária 12 meses, carga por UF |
| Logística | 1 | — |
| Pós-Venda | 1 | — |
| Produção | 1 | — |
| Recursos Humanos | 2 | Folha salarial 12 meses, custo folha por setor |

Total: **17 PNGs** em 10 departamentos.

---

## 3. Documentos Aprovados e Finalizados

| Documento | Local | Status | Conteúdo |
|-----------|-------|--------|----------|
| Prontuário Executivo | `relatorios/mercadinho-v4/mercadinho-v4/fase_02/prontuario_executivo.json` | ✅ Aprovado | JSON serializado com KPIs dos 10 departamentos + chave `saude_360` (caminho do dashboard) |
| Contrato de Problema | `dados/processados/mercadinho-v4/ml/contrato_problema.json` | ✅ Aprovado | `previsao_demanda_produto` — Regressão, grão produto, alvo `SUM(quantidade_saida)`, métrica R² |
| Registro do Dataset | `dados/registros/mercadinho-v4.json` | ✅ Aprovado | Estado das fases, matching semântico, status CRISP-DM |
| Dashboard 360° | `relatorios/.../fase_02/dashboard_saude_360.png` | ✅ Aprovado | Placa única de saúde da empresa |
| Fluxograma SVG | `src/app/fluxo_crisp_dm.svg` | ✅ Aprovado | 13 etapas, 6 fases |

### Artefatos ML produzidos (mercadinho-v4)

| Arquivo | Local | Descrição |
|---------|-------|-----------|
| ABT bruta | `dados/processados/mercadinho-v4/ml/abt_cliente_bruta.parquet` | Tabela analítica base |
| Treino | `dados/processados/mercadinho-v4/ml/treino_processado.parquet` | Partição 70% |
| Validação | `dados/processados/mercadinho-v4/ml/validacao_processado.parquet` | Partição 15% |
| Teste | `dados/processados/mercadinho-v4/ml/teste_processado.parquet` | Partição 15% |

> Os artefatos serializados de produção (`.joblib`, manifesto SHA-256) ainda não foram empacotados para mercadinho-v4; a página de Predição exibe aviso quando a API `:8000` não tem modelo carregado (HTTP 503).

---

## 4. Resultados de Predição — Um de Cada Cenário

A seguir, um resultado representativo para cada tipo de tarefa de aprendizado de máquina suportado pela plataforma.

> **Nota:** Como o artefato de produção para `mercadinho-v4` ainda não foi empacotado (Fase 06, Pilar 01), os exemplos abaixo ilustram a estrutura de saída esperada pela API `/predicao/risco_credito` e os campos do contrato de entrada. Para obter valores reais, execute `fase_06_pilar_01_persistencia` e suba a API em `:8000`.

### 4.1 Classificação — Supervisionado (Risco de Crédito)

**Contrato de entrada:** `EsquemaEntradaCliente` (Pilar 3 — Fase 06)  
**Campos:** `volume_total_recebido`, `ticket_medio_titulo`, `total_titulos_emitidos`, `maximo_dias_atraso_historico`, `uf_cliente`, `cidade_cliente`

| Campo | Valor de exemplo |
|-------|------------------|
| Volume total recebido (R$) | 12.500,50 |
| Ticket médio por título (R$) | 650,00 |
| Total de títulos emitidos | 18 |
| Máx. dias atraso (histórico) | 5,0 |
| UF | SP |
| Cidade | São Paulo |

**Saída da API (`EsquemaRespostaPredicao`):**

```json
{
  "classe_predita": 0,
  "decisao_rotulo": "BOM_PAGADOR_EM_DIA",
  "probabilidade_risco": 0.0412,
  "limiar_decisao_aplicado": 0.50,
  "faixa_risco": "BAIXO RISCO",
  "acao_recomendada": "Liberar Faturamento / Manter Crédito Automático",
  "versao_modelo_producao": "Random_Forest_Producao_v1.0.0",
  "tempo_processamento_ms": 0.85
}
```

**Interpretação:** cliente classificado como baixo risco (probabilidade 4,12% < limiar 50%), ação de liberar faturamento e manter crédito automático.

---

### 4.2 Regressão — Supervisionado (Previsão de Demanda por Produto)

**Contrato de problema vinculado:** `previsao_demanda_produto` (`dados/processados/mercadinho-v4/ml/contrato_problema.json`)  
**Tipo de tarefa:** Regressão  
**Alvo:** `SUM(quantidade_saida)` (regra SQL)  
**Métrica de otimização:** R²  
**Granularidade:** produto (código SKU) × mês  
**Deslocamento do alvo:** +1 período (próximo ciclo de compra)

| Parâmetro | Valor |
|-----------|-------|
| ID do problema | `previsao_demanda_produto` |
| Nome | Previsão de Demanda por Produto |
| Pergunta de negócio | Quanto de cada produto precisamos repor no próximo ciclo de compra? |
| Tipo | Regressão (supervisionado) |
| Alvo | Quantidade saída (soma) |
| Granularidade temporal | Mensal |
| Períodos de treino/val/teste | 70% / 15% / 15% |

**Saída esperada (estrutura de regressão):**

| SKU | Previsão qtde saída (próximo mês) | Intervalo de confiança | Ação de estoque |
|-----|-----------------------------------|------------------------|-----------------|
| SKU-001 | 420 un | [380, 460] | Repor 420 un |
| SKU-002 | 180 un | [150, 210] | Repor 180 un |
| SKU-003 | 950 un | [880, 1020] | Repor 950 un |

**Interpretação:** modelo de regressão supervisionado prevê a demanda futura por produto para planejamento de compras.

---

### 4.3 Previsão — Supervisionado (Faturamento / Receita)

**Cenário:** previsão de faturamento mensal por departamento (Comercial)  
**Tipo de tarefa:** Regressão / Previsão de série temporal (supervisionado)  
**Base:** `pareto_faturamento_por_departamento.png` + `evolucao_faturamento_ultimos_12_meses.png`

| Departamento | Faturamento médio 12 meses (R$) | Tendência | Previsão próximo mês (R$) |
|--------------|---------------------------------|-----------|---------------------------|
| Comercial | 130.750,03 | Estável | 132.000,00 |
| Financeiro | — | — | — |
| Outros 9 depts | — | — | — |

**Interpretação:** previsão supervisionada de receita com base na série histórica de 12 competências (2025-08 → 2026-07).

---

### 4.4 Não Supervisionado (Agrupamento / Detecção de Anomalias)

**Algoritmos disponíveis na fábrica de modelos:** K-Means, DBSCAN, Detecção de Anomalias, Redução de Dimensionalidade.

| Cenário | Algoritmo | Objetivo | Saída |
|---------|-----------|----------|-------|
| Segmentação de clientes | K-Means (não supervisionado) | Agrupar clientes por perfil de compra | Rótulos de cluster (0, 1, 2, …) |
| Detecção de fraudes/anomalias | Isolation Forest / DBSCAN | Identificar títulos fora do padrão | Sinal de anomalia (inlier/outlier) |
| Redução de dimensionalidade | PCA / t-SNE | Visualizar ABT em 2D/3D | Componentes principais |

**Exemplo de saída (clusterização não supervisionada):**

| Cliente ID | Cluster | Perfil | Ação sugerida |
|------------|---------|--------|---------------|
| C-001 | 0 | Alto volume, baixo atraso | Carteira VIP — crédito automático |
| C-002 | 1 | Médio volume, atraso ocasional | Monitorar |
| C-003 | 2 | Baixo volume, atraso alto | Revisar liberação |

---

## 5. Matriz de Rastreabilidade — Supervisionado vs Não Supervisionado

| Tipo de Aprendizado | Tarefa | Exemplo no Relatórios | Modelo | Métrica |
|---------------------|--------|----------------------|--------|---------|
| Supervisionado | Classificação | Risco de crédito do cliente | Random Forest | Acurácia / F1 / AUC |
| Supervisionado | Regressão | Previsão de demanda por produto | Regressão / Torneio | R² / RMSE / MAE |
| Supervisionado | Previsão | Faturamento 12 meses | Série temporal | MAPE / RMSE |
| Não Supervisionado | Agrupamento | Segmentação de clientes | K-Means | Silhueta / Inercia |
| Não Supervisionado | Detecção de Anomalias | Títulos fora do padrão | Isolation Forest | Taxa de anomalia |

---

## 6. Ambientes em Execução

| Porta | Aplicação | URL | Principal uso |
|-------|-----------|-----|---------------|
| 8502 | Plataforma Operacional | `http://localhost:8502` | Ingestão, Raio-X, Torneio, Valor, Predição |
| 8503 | Vitrine Executiva | `http://localhost:8503` | Fluxo CRISP-DM, Saúde 360°, Relatórios |
| 8000 | API de Inferência (Fase 06) | `http://localhost:8000` | Predição via Bearer JWT |

Links cruzados no sidebar de ambos permitem navegar entre operacional e vitrine.

---

## 7. Como Reproduzir

```bash
# 1. Ambiente
uv sync --dev

# 2. Ingestão dos dados (mercadinho-v4 já está em dados/brutos/csv/mercadinho-v4/)
# 3. Fase 02 — Raio-X (gera prontuario_executivo.json + dashboard_saude_360.png)
uv run python -m scripts.executores_arquivo.executar_fase_02_raio_x --dataset mercadinho-v4

# 4. Fase 03 — ABT + partições (via página Torneio ou API)
# 5. Fase 04 — Torneio de modelos
# 6. Fase 05 — Avaliação e escolha do campeão
# 7. Fase 06 — Persistência do artefato de produção
uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia

# 8. Subir API e consumir predição
uv run python -m scripts.executores_projeto.servir_api
# Em outro terminal:
uv run streamlit run app_streamlit.py --server.port 8502
uv run streamlit run src/app/app.py --server.port 8503
```

---

## 8. Créditos e Governança

- **Desenvolvido por:** Eliezer Henrique  
- **Auxílio de IA:** OpenCode  
- **Modelos utilizados para validação:** Nemotron 3.5 Super VL 120B A12B e MIMO v2  
- **Base de dados:** Mercadinho Vencedor 10/2026 — *Dataset privado, não compartilhado*  
- **Metodologia:** CRISP-DM (6 fases, 13 etapas executáveis)  
- **Interface:** Streamlit nativo, sem CSS customizado; SVG para fluxograma; matplotlib 200 DPI para dashboard.

---

*Relatório gerado automaticamente a partir dos artefatos persistidos pela Fase 02 e pela página de Predição da plataforma operacional.*
