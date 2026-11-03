# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Usuário primário: o analista responsável pelo dado de uma PME.** Ele chega com um dump do ERP (ou um conjunto de CSVs) e uma pergunta de negócio formulada em linguagem de negócio — não em linguagem de modelagem. Precisa sair de "tenho um banco" para "tenho um modelo homologado que responde à minha pergunta, com número, rastro e risco".

**Público secundário: o gestor que aprova a decisão.** Não opera a ferramenta, mas consome o dossiê do ato Valor: impacto financeiro esperado, desempenho do campeão e as ressalvas de governança.

O analista atua em ambiente corporativo local (máquina da PME / servidor interno), geralmente sozinho, em janelas curtas de trabalho. Ele não éritymo de machine learning: entende o negócio da própria empresa e precisa que a ferramenta traduza o resto.

## Product Purpose

A plataforma executa o ciclo CRISP-DM inteiro sobre **qualquer** base transacional de PME e **qualquer** pergunta de negócio, usando o mesmo motor. Sucesso significa: a mesma esteira que responde "quem vai atrasar" responde "quanto vamos vender" ou "quais clientes formam cada perfil de consumo", sem reescrita de código e sem depender do nome de uma tabela específica do ERP.

O diferencial não é o algoritmo: é a **decoupling explícita entre o dado e a pergunta**, formalizada em dois artefatos declarativos — o `RegistroDataset` (qual base está em análise) e o `ContratoProblema` (o que o humano quer saber) — mais um catálogo semântico editável que ensina o motor a reconhecer papéis de negócio ("cliente", "data de emissão", "valor") em nomenclaturas de ERP desconhecidas.

## Positioning

O diferencial mecanístico é a **declaratividade do grão e da receita**: o analista não escreve SQL, escolhe um dos 15 problemas pré-desenhados ou declara um contrato próprio, e a plataforma resolve tabela base, junções encadeadas com pré-agregação (sem fan-out 1:N), granularidade temporal, grão composto e deslocamento do vetor-alvo para o período seguinte (sem vazamento de informação). Um vizinho poderia copiar a lista de algoritmos; não poderia copiar a combinação de catálogo semântico editável + contrato de problema validado + registro persistente de dataset.

## Operating Context

- **Ciclo CRISP-DM de 6 fases**, dirigido pelo mesmo motor: 01 Ingestão (SQL→CSV isolado por PME), 02 Raio-X (macro + 10 departamentos), 03 Preparação (ABT + partição 70/15/15 + pipeline), 04 Modelagem (torneio → pódio Top 3), 05 Avaliação (pódio, XAI, governança), 06 Implantação (API de inferência).
- **Fases 01–05** executam por CLI (`scripts/executores_arquivo/`) com os mesmos parâmetros (`--dataset`, `--problema`, `--semente`, `--modo`) para qualquer dataset e qualquer problema.
- **Fase 06** é servida por API REST FastAPI com autenticação Bearer JWT e integridade SHA-256 do artefato de produção.
- **Jobs assíncronos persistidos** em JSON (`dados/registros/jobs/`) capturam stdout/stderr incremental, permitindo acompanhar a execução sem bloquear a interface.
- **Ambiente de execução**: Python 3.11+, DuckDB para SQL analítico sobre CSV, pandas/numpy para a engenharia de atributos, Scikit-Learn para modelagem, Streamlit para a interface, FastAPI/uvicorn para o serviço.
- **Fluxo do analista em 4 atos**: Base (upload + diagnóstico) → Pergunta (declarar o problema) → Torneio (rodar modelos, ver Top 3) → Valor (impacto + inferência + governança). Dois pontos de decisão humana são inegociáveis: **declarar a pergunta** e **eleger o campeão entre os três finalistas**.
- **Isolamento é lei**: cada PME tem pasta própria de dados brutos, artefatos, modelos e relatórios; a extração de um dump nunca toca a base de outra empresa.
- **Nenhum arquivo preexistente é apagado ou sobrescrito** por engano; a documentação de engenharia reversa vive em `_reversa_sdd/`.

## Capabilities and Constraints

- **Upload** de `.sql` (dump) ou `.csv` (tabelas) para pasta nomeada pela PME/dataset, com routing por extensão e rejeição explícita de formatos não suportados.
- **Catálogo de 15 problemas de negócio** em 4 famílias de tarefa: 5 classificação, 5 regressão, 3 agrupamento, 2 detecção de anomalias. Cada template define entidade base, grão, agregações, regra de alvo, métrica de otimização e custos de negócio.
- **Contrato de problema validado por Pydantic v2**: exige `alvo` para tarefas supervisionadas, proíbe `alvo` para não supervisionadas, normaliza o identificador em snake_case.
- **Catálogo semântico editável** (`src/nucleo/contratos/catalogo_semantico.json`) com override por dataset (`dados/registros/<dataset>/catalogo_semantico.json`): entidades e papéis de negócio.
- **CSVs sem linhas de dados são ignorados** pelo resolvedor — exportações parciais de ERP não podem produzir ABT vazia sem diagnóstico.
- **Joins declarativos encadeados** com CTEs pré-agregados por chave; a chave de base de uma junção posterior pode vir da junção anterior.
- **Granularidade temporal** (`dia|semana|mes|ano`) via CTE intermediário; grão composto = dimensões × bucket temporal; deslocamento do alvo usa `LEAD()`.
- **REST da plataforma**: `/datasets`, `/datasets/{nome}/upload`, `/datasets/{nome}/problema`, `/problemas`, `/datasets/{nome}/fases/{fase}/executar`, `/jobs/{id}`, `/datasets/{nome}/top3`, `/datasets/{nome}/campeao`.
- **Sem portão de login no frontend analítico.** O login JWT permanece na API para inferência de produção; o fluxo de 4 atos é acessível sem autenticação.
- **Idioma da interface e das specs**: português do Brasil.
- **Contratos de código**: Pydantic para fronteira de dados, tipagem estática nas assinaturas públicas, docstrings Google-style em toda função pública, `ruff` como linter.
- **Fatos em aberto**: o número de grupos default e o limiar de contagem de anomalias são parâmetros livres do contrato, ainda não fixados como política oficial da plataforma.

## Brand Commitments

- Nome do produto operacional: **CRISP-DM Operacional** (título da interface), consumido por PMEs.
- Tom: direto, técnico e executivo ao mesmo tempo — sem jargão de CI/CD, sem emoji decorativo no texto corrido, sem promessa de resultado que o laudo não comprove.
- Nenhuma identidade visual anterior está travada. A direção visual foi delegada à plataforma, que a establish nesta entrega.
- **Familiaridade sobre exotismo (preferência permanente registrada em 30/10/2026).** A interface deve parecer uma ferramenta analítica que o analista da PME já sabe usar: navegação lateral, filtros no topo, cartões de métrica, tabelas densas, painel de execução. Metáfora visual exótica, figurino de outro ofício e linguagem de terminal são rejeitados — a personalidade do produto vem da honestidade dos números, dos logs e das limitações visíveis, não de uma metáfora.
- **Barra de ofício (referência permanente registrada em 30/10/2026):** a mescla de quatro referências, nesta ordem de peso — Metabase/Power BI (densidade, filtros, cartões, tabela), apps Streamlit da galeria (sidebar, `st.metric`, `st.dataframe`), dbt Cloud/Airflow (execução orientada a tarefas com log e estado por etapa) e Linear/Vercel (escala tipográfica real, espaçamento disciplinado, estados desenhados). O resultado é um console de analista executado com ofício de produto, sem ironia e sem truque emprestado.
- A interface deve **explicar o motor**, não esconder: o analista vê a receita da ABT, o placar do torneio e o log da execução.

## Evidence on Hand

- **Base real**: `dados/brutos/csv/mercado_vencedor/` — 150 tabelas de ERP real (114.975 NFEs, 60.965 títulos a receber, 55.412 transmissões).
- **Limitações reais e conhecidas da base** (usadas como honestidade do produto, não como falha): `erp_nfedetsubitem.csv` e `erp_nfehistorico.csv` têm 0 linhas; `erp_nfetransmissao.csv` cobre 55.239 NFEs; `erp_prodestoque.csv` tem 66 linhas; `erp_nfedet.csv` não existe.
- **Execuções reais validadas**: `inadimplencia_clientes` (classificação) e `previsao_dias_atraso` (regressão) concluíram F3→F4→F5 com artefatos persistidos em `modelos/mercado_vencedor/`.
- **Figuras e laudos reais** em `relatorios/mercado_vencedor/` (Fase 02 por departamento, Fase 05 comparativo do pódio).
- **Ausências que trabalho futuro não pode fabricar**: sem logotipo, sem depoimentos, sem números de ROI de cliente, sem benchmark externo. O impacto financeiro exibido no ato Valor é **estimativa do modelo**, calculada a partir dos custos de negócio declarados no contrato — nunca resultado auditado de cliente.

## Product Principles

1. **O humano declara a intenção; a máquina propõe o caminho.** A pergunta de negócio e a escolha do campeão são decisões humanas explícitas, registradas no diário de auditoria do dataset. O motor nunca escolhe o objetivo de negócio por conta própria.
2. **Agnosticidade é contrato, não configuração.** Trocar de dataset ou de pergunta não deve exigir tocar em código: quem muda são o `RegistroDataset` e o `ContratoProblema`.
3. **Nenhum resultado sem rastro.** Cada fase produz artefato persistido, cada decisão produz observação datada, cada job produz log recuperável — inclusive após reinício do serviço.
4. **O dado da PME é intocável por padrão.** Isolamento físico por dataset, extração filtrada por nome e upload restrito a `.sql`/`.csv`.
5. **Honestidade sobre o dado antes do brilho do modelo.** O diagnóstico da base vem antes do tournament; limitações da base (tabelas vazias, cobertura parcial) aparecem na interface em vez de sumirem.

## Accessibility & Inclusion

- Idioma da interface: **português do Brasil**, sem jargão sem tradução.
- Contraste de texto e fundo em nível **WCAG AA**; nenhuma informação transmitida exclusivamente por cor (todo estado tem rótulo textual).
- Navegação operável por teclado, com foco visível nos controles interativos e ordem de tabulação natural na leitura do fluxo.
- Rótulos explícitos em todo campo de formulário, com texto de ajuda e valor padrão visível — o analista não deve adivinhar o formato esperado.
- Fontes com escala relativa e interface que permanece legível em telas de notebook de 1366×768 (uso típico de PME).
