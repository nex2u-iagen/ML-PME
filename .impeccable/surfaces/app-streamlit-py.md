---
version: 1
slug: "app-streamlit-py"
primary_target: "app_streamlit.py"
related_targets: []
---

# Surface Brief — Console CRISP-DM Operacional

## Scope and visitor mode

- **Surface:** `app_streamlit.py` — o console de análise em 4 atos (Base → Pergunta → Torneio → Valor) que substitui o painel de 8 abas.
- **Visitor mode:** **Operate**. O analista completa uma tarefa: transformar um dump de ERP + uma pergunta de negócio em um modelo homologado com número, rastro e decisão humana registrada.
- **Platform:** web (Streamlit local/corporativo), viewport-alvo 1366×768 até 1600×900.

## Audience, job, action, proof, constraints

- **Audience:** analista responsável pelo dado de uma PME; entende o negócio, não modelagem estatística. Secondary: o gestor que aprova a decisão e lê o dossiê do ato Valor.
- **Job:** sair de "tenho um banco" para "tenho um modelo homologado que responde à minha pergunta".
- **Action:** declarar a pergunta de negócio (ponto de decisão humano nº 1) e eleger o campeão entre o Top 3 (ponto de decisão humano nº 2).
- **Proof/content:** números reais do dataset em análise (contagens de tabelas, linhas, cobertura do matching semântico, métricas do torneio, custo do job). Estados reais: base sem tabela canônica mapeada, CSVs vazios, fase em execução, job com erro.
- **Constraints:** sem portão de login no frontend; rótulos em pt-BR; nenhuma informação transmitida só por cor; o stepwise nunca marca uma etapa como concluída sem o artefato em disco; densidade de BI, não de landing page.

## Chosen direction and memorable moment

- **Direction:** o **padrão da categoria**, executado com ofício — console de analista em mescla declarada: densidade e filtros de Metabase/Power BI, shell nativo de app Streamlit, execução orientada a tarefa com log de dbt/Airflow, e disciplina tipográfica de Linear/Vercel. Sem figurino: nenhum mundo visual emprestado de outro ofício.
- **Memorable moment:** o **trilho de atos** na lateral esquerda. Ele não é um menu: é a máquina de estados real da esteira. Cada ato mostra o estado verdadeiro (lido do disco, não de um flag otimista), a duração real, o artefato produzido e, nos dois pontos de decisão humana, a etiqueta `DECISÃO DO ANALISTA`. O analista clica numa etapa já concluída e volta a ela sem perder contexto; a etapa ativa nunca é ambígua.

## Direction contract

### THESIS

Um console de analista onde **nada é decorativo e nada é metafórico**: a arquitetura do CRISP-DM é a própria navegação, a honestidade dos dados é a personalidade do produto, e a familiaridade do arranjo (sidebar, filtros no topo, cartões de métrica, tabela densa, painel de execução) é o que compra a confiança do analista da PME. Recusa: a grade de cartões de dashboard genérico com acento único e métricas inventadas.

### OWN-WORLD

Sem mundo emprestado. O sistema é o de um console operacional de dados: fundo `#F5F7F9`, superfícies `#FFFFFF`, hairlines `#E4E8ED`/`#D0D7DE` como único separador (zero sombra como divisória), tinta `#0B1220` com secundária `#4A5568` e rótulos `#7A8699`. Quatro papéis cromáticos e nenhum outro: **primária `#0E6BA8`** (ação, estado ativo, link), **sucesso `#0E7C4A`** (concluído, campeão), **alerta `#9A6208`** (executando, degradado), **crítico `#C0261C`** (erro, anulado). Tipografia: grotesque de trabalho (Public Sans com fallback `system-ui`) em escala 11/12/13/14/22/26px, numerais tabulares; monoespaçada (JetBrains Mono com fallback `ui-monospace`) só em log, identificador, semente e duração. Raio 8px em cartão, 6px em controle, pílula em estado. Ritmo de espaçamento em múltiplo de 4px, separação entre seções por regra de 1px e respiro de 24px, nunca por sombra.

### STORY

O analista chega, vê no topo a cadeia viva `dataset → contrato → semente` e na lateral a esteira de 4 atos com o estado real de cada uma. Ele sobe o dump (Ato Base), declara a pergunta a partir dos 15 templates ou escreve a sua (Ato Pergunta), assiste ao torneio e recebe o pódio (Ato Torneio), elege o campeão e vê o impacto financeiro, a inferência e o dossiê (Ato Valor). Cada passo deixa artefato, log e observação datada. Nenhuma tela pede algo que o motor não execute.

### FIRST VIEWPORT

Sidebar de 264px à esquerda: bloco de marca (nome do produto + versão + estado da API), seletor persistente de dataset, e o **trilho de atos** com 4 entradas — número, título, estado (ponto + palavra), duração e artefato —, com as duas entradas de decisão marcadas; no rodapé, o motor e o último job. No topo da área principal, a faixa de contexto: título do ato à esquerda e a cadeia `dataset · contrato · semente` à direita, em chips pequenos e rotulados. Abaixo, uma linha de 4 cartões de métrica com números reais (amostras, features, duração, métrica-alvo) e, logo abaixo, o painel de execução (`Run console`) com o log incremental do job quando há execução em curso; no estado ocioso, o painel explica o que será feito e o que será produzido. Abaixo do console, a área de trabalho do ato — tabela densa do pódio com cabeçalho ordenável, barras de métrica e a faixa de decisão do analista. Em 1366×768 a tabela do pódio e a faixa de decisão já aparecem acima da dobra.

### FORM

- **Posição na lista:** escolha do usuário (canon) sobre as alternativas fundamentadas e os challengers do catálogo — registrada em 30/10/2026.
- **SEED REFERENCE:** `seed:8a356d03b6dda171`
- **Assinatura:** o trilho de atos como máquina de estados lida do disco; a cadeia de contexto persistente; a faixa de decisão com o estado real do humano.

### FINISH

unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved decisions

- Número de grupos default para problemas de agrupamento e limiar de contagem de anomalias ainda não são política oficial da plataforma (parametros livres do contrato).
- O serviço de API pode ou não estar em execução quando o Streamlit sobe; o app precisa operar nos dois casos.
- A escoreação em lote da carteira (CSV) continua sem endpoint de serviço; o ato Valor entrega apenas escoreação individual.
