# Step 01 — Primeira Execução (First Run)

## Objetivo
Esta é a primeira execução do Reversa no projeto. O objetivo é estabelecer a base para toda a análise subsequente.

## Inicialização do Contexto

1. **Executar o Scout**
   - O agente `Scout` deve ser o primeiro a ser ativado.
   - Ele mapeia a estrutura do projeto, identificando:
     - Linguagens e frameworks utilizados
     - Dependências e gerenciadores de pacotes
     - Points of entry (entry points)
     - Configurações de CI/CD
     - Arquitetura geral do sistema
   
2. **Resultado Esperado do Scout**
   - Lista de módulos identificados
   - Linguagem principal
   - Integrações externas detectadas (ou: nenhuma)
   - Tipo de banco de dados: presente/ausente
   - Tecnologias de deployment identificadas

2. **Nível de Documentação**
   Após o Scout concluir, o usuário deve escolher o nível de documentação desejado:
   
   > "[Nome], o Scout concluiu o mapeamento. Aqui está o que encontrei:
> - **[N] módulos** identificados: [lista resumida]
> - **Linguagem principal:** [linguagem]
> - **[N] integrações externas** detectadas (ou: nenhuma)
> - **Banco de dados:** [presente/ausente]
>
> Qual nível de documentação você quer para este projeto?
>
> ◉ **1. Essencial** ← padrão
> &nbsp;&nbsp;&nbsp;&nbsp;Artefatos principais (code-analysis, domain, architecture, specs SDD). Ideal para projetos simples.
>
> ○ **2. Completo**
> &nbsp;&nbsp;&nbsp;&nbsp;Documentação completa com diagramas C4, ERD, ADRs, OpenAPI e matrizes de rastreabilidade. Recomendado para a maioria dos projetos.
>
> ○ **3. Detalhado**
> &nbsp;&nbsp;&nbsp;&nbsp;Máxima profundidade: flowcharts por função, ADRs expandidos, deployment, revisão cruzada obrigatória. Para sistemas enterprise.
>
> Digite 1, 2 ou 3 — ou pressione Enter para confirmar **Essencial**."

   - Aceite também o nome por extenso: `essencial`/`completo`/`detalhado`
   - O valor escolhido deve ser salvo em `.reversa/state.json` → campo `doc_level`

3. **Organização de Specs**
   Após a definição do nível de documentação, executar o passo de organização de specs:
   
   > "Escolha o nível de organização das specs:
   > 
   > 1. **Por módulo** ← padrão
   > &nbsp;&nbsp;&nbsp;&nbsp;Cada módulo do sistema tem suas specs SDD independentes.
   > 
   > 2. **Por caso de uso**
   > &nbsp;&nbsp;&nbsp;&nbsp;As specs são organizadas por casos de uso do sistema.
   > 
   > 3. **Por endpoint**
   > &nbsp;&nbsp;&nbsp;&nbsp;As specs focam nos endpoints da API.
   > 
   > 4. **Híbrida**
   > &nbsp;&nbsp;&nbsp;&nbsp;Combinação de organização por módulo e por caso de uso.
   > 
   > 5. **Por features**
   > &nbsp;&nbsp;&nbsp;&nbsp;Organização baseada nas features do produto.
   > 
   > 6. **Customizada**
   > &nbsp;&nbsp;&nbsp;&nbsp;Definição personalizada pelo usuário.
   
   - A escolha do usuário deve ser persistida em `.reversa/config.toml`, seção `[specs]`
   - Em re-execuções com a seção já decidida, o passo é pulado automaticamente

4. **Prossiga para o Archaeologist**
   Apenas após:
   - ✅ Scout concluído e documentação nivel escolhida
   - ✅ Organização de specs decidida e persistida
   
   Então ative o agente Archaeologist para analisar os módulos identificados.

## Checkpoint Preventivo

Após a configuração inicial, salve um checkpoint em `.reversa/state.json` com:
- `phase` atualizado para o próximo estágio
- `completed` com as etapas finalizadas
- `checkpoints` registrados para cada agente que já rodou

## Próximo Marco

Após o Archaeologist concluir, a próxima etapa é a fase de interpretação com os agentes Detective e Architect.

