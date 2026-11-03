# Levantamento de Requisitos — Instalação do Reversa (`npx reversa install`)

**Autor do framework:** Prof. Dr. Sandeco Macedo (IFG / UFG) — [sandeco/reversa](https://github.com/sandeco/reversa)  
**Licença:** MIT  
**Versão do pacote consultada:** 1.3.2  
**Documentação oficial:** https://sandeco.github.io/reversa/instalacao/

---

## 1. Visão Geral

O **Reversa** é um framework de *reverse engineering* de especificações. Instalado dentro de um projeto *legacy*, coordena uma equipe de agentes de IA especializados para analisar o código existente e gerar especificações completas, rastreáveis e prontas para uso por qualquer agente codificador (Claude Code, Codex, Cursor, Gemini CLI, etc.).

A instalação é feita com um único comando, executado na **raiz do projeto legado a ser analisado**:

```bash
npx reversa install
```

O instalador não toca em arquivos originais do projeto; ele apenas adiciona a estrutura própria do Reversa (agentes, arquivos de entrada do engine e diretório de estado).

---

## 2. Requisitos de Ambiente (Pré-requisitos)

| ID | Requisito | Detalhe | Obrigatório |
|----|-----------|---------|-------------|
| REQ-AMB-01 | **Node.js** | Versão **18+** instalada na máquina (o `package.json` do pacote declara `engines: node >= 18.20.2`). | Sim |
| REQ-AMB-02 | **npm / npx** | O `npx` deve estar disponível (vem junto com o Node.js). | Sim |
| REQ-AMB-03 | **Terminal/CLI** | Acesso a linha de comando para executar `npx reversa install`. | Sim |
| REQ-AMB-04 | **Conexão com internet** | Necessária para baixar o pacote `reversa` do npm na primeira execução (`npx` baixa o pacote em tempo real). | Sim (primeira vez) |
| REQ-AMB-05 | **Projeto legado alvo** | Um repositório/projeto existente cujos fontes serão analisados (não é necessário que seja Node.js). | Sim |
| REQ-AMB-06 | **Permissão de gravação** | Permissão para criar arquivos e pastas na raiz do projeto alvo (`.reversa/`, `.agents/skills/`, arquivos de engine). | Sim |

> **Observação:** O Reversa **não exige** que o projeto alvo seja um projeto Node.js. Ele pode ser instalado em projetos de qualquer linguagem/stack.

---

## 3. Requisitos Funcionais da Instalação

| ID | Requisito | Descrição |
|----|-----------|-----------|
| REQ-FUN-01 | Execução por comando único | A instalação deve ser disparada com `npx reversa install` na raiz do projeto. |
| REQ-FUN-02 | Detecção automática de engines | O instalador deve detectar quais engines de IA estão presentes no ambiente (Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Aider, Amazon Q Developer, Kiro). |
| REQ-FUN-03 | Seleção de times de agentes | O instalador deve apresentar um menu interativo para escolher quais *teams* de agentes instalar. |
| REQ-FUN-04 | Times obrigatórios | `Reversa Agents Core` e `Bug Agents` são sempre instalados, não sendo sujeitos à seleção do usuário. |
| REQ-FUN-05 | Times pré-selecionados | Por padrão vêm marcados: `Migration Agents`, `Code Forward Agents`, `Code New Project Agents`, `Documentation Agents` e `Pricing and Size Agents`. |
| REQ-FUN-06 | Time opcional desmarcado | `Translators N8N->Specs->Python` vem desmarcado por padrão (opcional). |
| REQ-FUN-07 | Coleta de preferências | O instalador deve coletar nome do projeto, linguagem e outras preferências do usuário. |
| REQ-FUN-08 | Cópia dos agentes | Deve copiar os agentes para `.agents/skills/` (e `.claude/skills/` quando for Claude Code). |
| REQ-FUN-09 | Criação de arquivo de entrada | Deve criar o arquivo de ativação do engine detectado: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `GEMINI.md`, `CONVENTIONS.md`, `.amazonq/rules/reversa.md`, etc. |
| REQ-FUN-10 | Criação de diretório de estado | Deve criar o diretório `.reversa/` para armazenar checkpoints/estado da análise. |
| REQ-FUN-11 | Resumo final | Deve exibir um resumo da instalação com a contagem de agentes por time (Discovery, Migration, Code Forward, New Project, Documentation, Translators, Pricing). |
| REQ-FUN-12 | Não destrutivo | O instalador não deve modificar ou excluir arquivos originais do projeto alvo. |

---

## 4. Engines de IA Suportados e Arquivos Criados

| Engine | Arquivo de entrada criado | Caminho das skills | Como ativar |
|--------|--------------------------|--------------------|-------------|
| Claude Code | `CLAUDE.md` | `.claude/skills/reversa-*/` e `.agents/skills/reversa-*/` | `/reversa` |
| Codex | `AGENTS.md` | `.agents/skills/reversa-*/` | `reversa` (CLI: `agy`) |
| Cursor | `.cursorrules` | `.agents/skills/reversa-*/` | `/reversa` |
| Gemini CLI | `GEMINI.md` | `.agents/skills/reversa-*/` | `/reversa` |
| Aider | `CONVENTIONS.md` | `.agents/skills/reversa-*/` | `reversa` |
| Amazon Q Developer | `.amazonq/rules/reversa.md` | `.agents/skills/reversa-*/` | `/reversa` |
| Kiro | (descoberta nativa) | `.kiro/skills/` | automático |

---

## 5. Times de Agentes Instalados

| Time | Incluído por padrão? | Obs. |
|------|---------------------|------|
| Reversa Agents Core | **Sempre** (obrigatório) | Orquestrador, Scout, Revisor, etc. |
| Bug Agents | **Sempre** (obrigatório) | — |
| Migration Agents | Pré-selecionado | Pode ser desmarcado |
| Code Forward Agents | Pré-selecionado | Pode ser desmarcado |
| Code New Project Agents | Pré-selecionado | Pode ser desmarcado |
| Documentation Agents | Pré-selecionado | Pode ser desmarcado |
| Pricing and Size Agents | Pré-selecionado | Pode ser desmarcado |
| Translators N8N->Specs->Python | **Não** (desmarcado) | Opcional, input adapter para n8n |

---

## 6. Requisitos Não-Funcionais

| ID | Categoria | Requisito |
|----|-----------|-----------|
| REQ-NF-01 | Segurança | Não cometer segredos/credenciais; o instalador não deve pedir senhas ou tokens do projeto. |
| REQ-NF-02 | Segurança | O `uninstall` remove **apenas** o que o Reversa criou (`.reversa/`, `.agents/skills/reversa-*/`, arquivos de engine). Especificações geradas em `_reversa_sdd/` são preservadas por padrão. |
| REQ-NF-03 | Rastreabilidade | As especificações geradas devem ser rastreáveis ao código fonte analisado. |
| REQ-NF-04 | Operacional | A instalação deve ser executável **uma única vez** por projeto (reinstalações via `npx reversa update`). |
| REQ-NF-05 | Portabilidade | Funciona independentemente da linguagem/stack do projeto alvo. |
| REQ-NF-06 | Observabilidade | O instalador deve exibir logs de progresso e um resumo final ao término. |

---

## 7. Checklist de Instalação (Passo a Passo)

1. [ ] Verificar se o **Node.js 18+** está instalado: `node --version`
2. [ ] Verificar se o **npm/npx** está disponível: `npm --version` / `npx --version`
3. [ ] Entrar na raiz do projeto legado a ser analisado.
4. [ ] (Opcional, recomendado) Fazer backup/commit do estado atual do projeto.
5. [ ] Executar: `npx reversa install`
6. [ ] Aguardar a detecção automática das engines de IA presentes.
7. [ ] Responder ao menu interativo: escolher times de agentes (Core e Bug são obrigatórios).
8. [ ] Informar nome do projeto, linguagem e preferências solicitadas.
9. [ ] Confirmar a criação dos arquivos (`.reversa/`, `.agents/skills/`, arquivo de engine, etc.).
10. [ ] Ler o resumo final da instalação (contagem por time).
11. [ ] Abrir o projeto na engine de IA escolhida e usar o comando de ativação (ex.: `/reversa` no Claude Code).
12. [ ] (Pós-instalação) Verificar o estado com: `npx reversa status`

---

## 8. Comandos CLI Disponíveis Após a Instalação

| Comando | Finalidade |
|---------|------------|
| `npx reversa install` | Instala o Reversa no projeto (execução única recomendada). |
| `npx reversa status` | Mostra o estado atual da análise. |
| `npx reversa update` | Atualiza todos os agentes para a versão mais recente. |
| `npx reversa add-engine` | Adiciona suporte a uma nova engine de IA. |
| `npx reversa uninstall` | Remove o Reversa do projeto (apaga apenas o que ele criou). |

---

## 9. Critérios de Aceitação da Instalação

A instalação será considerada concluída com sucesso quando:

- [ ] `npx reversa install` rodou sem erros na raiz do projeto.
- [ ] Foram detectadas as engines de IA presentes no ambiente.
- [ ] Os times obrigatórios (`Reversa Agents Core`, `Bug Agents`) foram instalados.
- [ ] Os arquivos de entrada do engine foram criados (`CLAUDE.md`, `AGENTS.md`, etc., conforme o engine detectado).
- [ ] A pasta `.agents/skills/` (e `.claude/skills/` se aplicável) contém os agentes do Reversa.
- [ ] O resumo final exibiu a contagem de agentes por time.
- [ ] Nenhum arquivo original do projeto foi modificado ou excluído.
- [ ] O comando de ativação da engine escolhida (`/reversa`, `reversa`, etc.) está disponível no projeto.

---

## 10. Referências

- Documentação de instalação: https://sandeco.github.io/reversa/instalacao/
- CLI: https://sandeco.github.io/reversa/cli/
- Engines suportados: https://sandeco.github.io/reversa/engines/
- Repositório: https://github.com/sandeco/reversa
- Pacote npm: https://www.npmjs.com/package/reversa
- Paper: https://arxiv.org/abs/2605.18684

---

*Documento gerado com base na documentação oficial do Reversa (sandeco). Consulte sempre os links acima para a versão mais recente dos requisitos.*
