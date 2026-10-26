# 🧭 Mapa Estratégico de Exploração e Descoberta Analítica (ERP PME)

Este diretório contém os módulos orientados a objetos responsáveis pela ingestão, diagnóstico exploratório e formulação científica de hipóteses de negócio.

Em Pequenas e Médias Empresas (PMEs), os bancos de dados de ERPs não são apenas registros de notas fiscais; são o reflexo digital da saúde operacional, financeira e comercial da companhia. Cada arquivo `.py` a ser criado nesta pasta atacará uma hipótese isolada ou executará uma etapa bem delineada do ciclo CRISP-DM.

---

## 🗺️ Matriz de Domínios, Hipóteses e Oportunidades em PMEs

Abaixo estão organizadas as principais visões analíticas que podem ser extraídas das entidades relacionais típicas de um ERP (`clientes`, `pedidos`, `itens_pedido`, `produtos`, `contas_a_receber`, `contas_a_pagar`, `fornecedores`).

                              DADOS BRUTOS DO ERP
                                      │
        ┌──────────────┬──────────────┴──────────────┬──────────────┐
        ▼              ▼                             ▼              ▼
   FINANCEIRO      COMERCIAL                      ESTOQUE       OPERAÇÕES
 (Inadimplência,  (Segmentação RFV,              (Giro, Ruptura, (Lead Time,
 Fluxo de Caixa) Previsão de Churn)                Curva ABC)    Fornecedores)

---

### 1. Módulo Financeiro e Fluxo de Caixa

As PMEs frequentemente operam com margens apertadas e dependem fortemente de capital de giro. As maiores dores costumam ser a inadimplência e o descompasso entre contas a pagar e receber.

| Arquivo Planejado | Pergunta de Negócio / Hipótese | Técnica Analítica / Algoritmo | Valor Gerado para a PME (ROI) |
| :--- | :--- | :--- | :--- |
| `02_hipotese_inadimplencia.py` | **Hipótese:** Clientes com atrasos superiores a 5 dias no primeiro título tendem a apresentar taxa de inadimplência 4x maior no histórico seguinte? | Regressão Logística, *Credit Scoring* e Teste Qui-Quadrado de Independência. | Redução de perdas com calotes (*Bad Debt*) e parametrização segura de limite de crédito. |
| `02_hipotese_fluxo_caixa.py` | **Hipótese:** O descasamento entre o Prazo Médio de Pagamento (PMP) e o Prazo Médio de Recebimento (PMR) cria vales de caixa previsíveis a cada 60 dias? | Decomposição de Séries Temporais (Sazonalidade, Tendência e Resíduos via `statsmodels`). | Prevenção de tomada de empréstimos bancários emergenciais com juros elevados. |
| `02_hipotese_custo_bancario.py`| **Hipótese:** Pequenos títulos emitidos com boleto bancário consomem mais de 15% do lucro líquido da venda em taxas administrativas? | Análise Descritiva de Custos Operacionais e Distribuição de Frequência. | Renegociação de tarifas ou exclusão de meios de pagamento ineficientes para tickets baixos. |

---

### 2. Módulo Comercial, Vendas e Clientes

Geralmente, 20% dos clientes representam 80% do faturamento da empresa (Princípio de Pareto). Entender o ciclo de vida do cliente é vital para o crescimento da operação.

| Arquivo Planejado | Pergunta de Negócio / Hipótese | Técnica Analítica / Algoritmo | Valor Gerado para a PME (ROI) |
| :--- | :--- | :--- | :--- |
| `02_hipotese_segmentacao_rfv.py` | **Hipótese:** Existem grupos homogêneos de clientes com base em Recência, Frequência e Valor Monetário (RFV / *RFM*)? | Clusterização Não Supervisionada (*K-Means*, *DBSCAN*) e Análise de Silhueta. | Campanhas de retenção customizadas; alocação do time comercial nos clientes "Campeões". |
| `02_hipotese_previsao_churn.py` | **Hipótese:** O aumento no intervalo de tempo entre compras consecutivas é um indicador antecedente de abandono (*Churn*)? | Análise de Sobrevivência (*Survival Analysis*) e Modelos Lineares Generalizados (GLM). | Ações de recuperação preventiva antes que o cliente mude para o concorrente. |
| `02_hipotese_cesta_compras.py` | **Hipótese:** Determinados produtos possuem alta taxa de venda casada (*Market Basket Analysis*) que não é explorada pela equipe de vendas? | Regras de Associação (Algoritmo *Apriori* / *FP-Growth*), métricas de Suporte, Confiança e *Lift*. | Criação de kits promocionais, aumento do Ticket Médio e cross-selling qualificado. |

---

### 3. Módulo de Estoque, Compras e Logística

O estoque em uma PME costuma representar a maior parcela do capital imobilizado. Mercadoria parada na prateleira corrói a liquidez da empresa.

| Arquivo Planejado | Pergunta de Negócio / Hipótese | Técnica Analítica / Algoritmo | Valor Gerado para a PME (ROI) |
| :--- | :--- | :--- | :--- |
| `02_hipotese_curva_abc_estoque.py`| **Hipótese:** Menos de 10% do catálogo de produtos ativos responde por 70% da margem bruta de contribuição da companhia? | Classificação Paramétrica ABC/XYZ (Faturamento vs. Previsibilidade de Demanda). | Otimização do espaço físico e priorização de compras para itens críticos. |
| `02_hipotese_risco_ruptura.py` | **Hipótese:** A variabilidade no tempo de entrega dos fornecedores (*Lead Time*) provoca rupturas de estoque (*Stockout*) em períodos de pico de venda? | Testes de Normalidade e Cálculo Estocástico de Estoque de Segurança (*Safety Stock*). | Redução de vendas perdidas por indisponibilidade imediata de mercadoria. |
| `02_hipotese_obsolescencia.py` | **Hipótese:** Existem itens sem movimentação há mais de 180 dias gerando custo de oportunidade e desvalorização patrimonial? | Detecção de Anomalias Univariadas e Análise de Envelhecimento de Estoque (*Aging*). | Liquidações estratégicas para oxigenação e recuperação de liquidez de caixa. |

---

### 4. Padrão Estrutural dos Módulos Python em `src/`

Para manter a conformidade com as diretrizes do **Ruff** e garantir modularidade, cada arquivo de hipótese implementará o seguinte ciclo interno de execução:

1. **Leitura e Extração:** Consumo desacoplado a partir de instâncias de `01_carregador.py`.
2. **Formulação Matemática da Hipótese:** Declaração explícita da Hipótese Nula ($H_0$) e da Hipótese Alternativa ($H_1$).
3. **Execução Estatística:** Testes formais (p-valor, intervalos de confiança, métricas de separabilidade).
4. **Relatório em Linguagem Executiva:** Emissão de diagnósticos claros voltados para a tomada de decisão do comitê executivo e diretores da PME.