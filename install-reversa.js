#!/usr/bin/env node
/**
 * Instalação automática (não-interativa) do Reversa.
 * Replica o que `npx reversa install` faria, mas sem requerer TTY/inquirer.
 *
 * Respostas usadas (defaults do instalador):
 *  - engines: ['opencode']   (engine detectado no ambiente)
 *  - project_name: nome da pasta atual
 *  - user_name: 'Usuário'
 *  - chat_language: 'pt-br'
 *  - doc_language: 'Português'
 *  - output_folder: '_reversa_sdd'
 *  - git_strategy: 'commit'
 *  - answer_mode: 'chat'
 *
 * Uso: node install-reversa.js
 */

import { existsSync, mkdirSync, writeFileSync, readFileSync, cpSync, readdirSync, statSync, chmodSync } from 'fs';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Caminho raiz do pacote reversa instalado via npx (ajuste se necessário)
const REVERSA_ROOT = resolve(
  process.env.HOME,
  '.npm',
  '_npx',
  'dd2a966412d4052b',
  'node_modules',
  'reversa',
);

const AGENTS_DIR = join(REVERSA_ROOT, 'agents');
const TEMPLATES_DIR = join(REVERSA_ROOT, 'templates');
const PROJECT_ROOT = resolve(process.cwd());

const VERSION = '1.3.6';

const ANSWERS = {
  engines: ['opencode'],
  project_name: PROJECT_ROOT.split(/[\\/]/).pop(),
  user_name: 'Usuário',
  chat_language: 'pt-br',
  doc_language: 'Português',
  output_folder: '_reversa_sdd',
  git_strategy: 'commit',
  answer_mode: 'chat',
};

const createdFiles = [];
const manifestPaths = [];

function _rel(absPath) {
  return absPath.replace(PROJECT_ROOT + '\\', '').replace(PROJECT_ROOT + '/', '');
}

function _register(absPath) {
  const rel = _rel(absPath);
  if (!createdFiles.includes(rel)) createdFiles.push(rel);
  try {
    if (!statSync(absPath).isDirectory()) {
      if (!manifestPaths.includes(rel)) manifestPaths.push(rel);
    }
  } catch { /* ignore */ }
}

function _registerFilesInDir(dirPath) {
  try {
    const entries = readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      const full = join(dirPath, entry.name);
      if (entry.isDirectory()) {
        _registerFilesInDir(full);
      } else {
        const rel = _rel(full);
        if (!manifestPaths.includes(rel)) manifestPaths.push(rel);
      }
    }
  } catch { /* ignore */ }
}

function _mkdir(dir) {
  mkdirSync(dir, { recursive: true });
}

function _writeNew(filePath, content) {
  if (existsSync(filePath)) return false;
  _mkdir(dirname(filePath));
  writeFileSync(filePath, content, 'utf8');
  _register(filePath);
  return true;
}

// ENGINES (mirror do detector.js)
const ENGINES = [
  {
    id: 'claude-code', name: 'Claude Code', star: true,
    entryFile: 'CLAUDE.md', entryTemplate: 'CLAUDE.md',
    skillsDir: '.claude/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'codex', name: 'Codex', star: true,
    entryFile: 'AGENTS.md', entryTemplate: 'AGENTS.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'cursor', name: 'Cursor', star: true,
    entryFile: '.cursorrules', entryTemplate: 'cursorrules',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'gemini-cli', name: 'Gemini CLI', star: false,
    entryFile: 'GEMINI.md', entryTemplate: 'GEMINI.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'windsurf', name: 'Windsurf', star: false,
    entryFile: '.windsurfrules', entryTemplate: 'windsurf',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'antigravity', name: 'Antigravity', star: false,
    entryFile: 'AGENTS.md', entryTemplate: 'AGENTS.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'kiro', name: 'Kiro', star: false,
    entryFile: null, entryTemplate: null,
    skillsDir: '.kiro/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'opencode', name: 'Opencode', star: false,
    entryFile: 'AGENTS.md', entryTemplate: 'AGENTS.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'hermes', name: 'Hermes', star: false,
    entryFile: 'AGENTS.md', entryTemplate: 'AGENTS.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'cline', name: 'Cline', star: false,
    entryFile: '.clinerules', entryTemplate: 'clinerules',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'roo-code', name: 'Roo Code', star: false,
    entryFile: '.roorules', entryTemplate: 'roorules',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'github-copilot', name: 'GitHub Copilot', star: false,
    entryFile: '.github/copilot-instructions.md', entryTemplate: 'copilot-instructions',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'aider', name: 'Aider', star: false,
    entryFile: 'CONVENTIONS.md', entryTemplate: 'CONVENTIONS.md',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
  {
    id: 'amazon-q', name: 'Amazon Q Developer', star: false,
    entryFile: '.amazonq/rules/reversa.md', entryTemplate: 'amazonq',
    skillsDir: '.agents/skills', universalSkillsDir: '.agents/skills',
  },
];

function listAllAgents() {
  return readdirSync(AGENTS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort();
}

function renderPolicyBlock({ outputFolder, forwardFolder }) {
  return `
# Reversa Policy
- Output folder: ${outputFolder}
- Forward folder: ${forwardFolder}
`;
}

function installSkill(agentId, skillsDir) {
  const src = join(AGENTS_DIR, agentId);
  const dest = join(PROJECT_ROOT, skillsDir, agentId);

  if (!existsSync(src)) {
    console.warn(`  Agente não encontrado: ${agentId}`);
    return;
  }
  if (existsSync(dest)) return;

  _mkdir(dirname(dest));
  cpSync(src, dest, { recursive: true });
  _restoreExecutables(join(dest, 'scripts'));
  _register(dest);
  _registerFilesInDir(dest);
}

function _restoreExecutables(scriptsDir) {
  if (process.platform === 'win32' || !existsSync(scriptsDir)) return;
  for (const entry of readdirSync(scriptsDir, { withFileTypes: true })) {
    if (!entry.isFile() || entry.name.includes('.')) continue;
    try { chmodSync(join(scriptsDir, entry.name), 0o755); } catch { /* ignore */ }
  }
}

function installEntryFile(engine, { outputFolder, forwardFolder }) {
  if (!engine.entryFile || !engine.entryTemplate) return;
  const templatePath = join(TEMPLATES_DIR, 'engines', engine.entryTemplate);
  const destPath = join(PROJECT_ROOT, engine.entryFile);
  if (!existsSync(templatePath)) return;

  const content = readFileSync(templatePath, 'utf8')
    .replace('{{REVERSA_POLICY}}', renderPolicyBlock({ outputFolder, forwardFolder }));

  if (!existsSync(destPath)) {
    _mkdir(dirname(destPath));
    writeFileSync(destPath, content, 'utf8');
    _register(destPath);
    return;
  }
  // Arquivo já existe → não sobrescreve (comportamento padrão do instalador)
}

function createReversaDir(answers, version) {
  const reversaDir = join(PROJECT_ROOT, '.reversa');
  const configDir = join(reversaDir, '_config');

  _mkdir(reversaDir);
  _mkdir(configDir);
  _mkdir(join(reversaDir, 'context'));

  // Forward assets
  _installForwardAssets(reversaDir, answers, version);

  // reversa-config.json
  const srcConfig = join(TEMPLATES_DIR, 'reversa-config.json');
  if (existsSync(srcConfig)) {
    _writeNew(join(reversaDir, 'reversa-config.json'), readFileSync(srcConfig, 'utf8'));
  }

  // hooks
  const hooksSrcDir = join(TEMPLATES_DIR, 'hooks');
  if (existsSync(hooksSrcDir)) {
    for (const file of readdirSync(hooksSrcDir)) {
      const srcFile = join(hooksSrcDir, file);
      if (!statSync(srcFile).isFile()) continue;
      _writeNew(join(reversaDir, 'hooks', file), readFileSync(srcFile, 'utf8'));
    }
  }

  // state.json
  const stateTemplate = readFileSync(join(TEMPLATES_DIR, 'state.json'), 'utf8');
  const state = JSON.parse(stateTemplate.replace('{{VERSION}}', version));
  state.project = answers.project_name;
  state.user_name = answers.user_name;
  state.chat_language = answers.chat_language;
  state.doc_language = answers.doc_language;
  state.answer_mode = answers.answer_mode;
  state.output_folder = answers.output_folder;
  state.engines = answers.engines;
  state.agents = listAllAgents();
  _writeNew(join(reversaDir, 'state.json'), JSON.stringify(state, null, 2));

  // config.toml
  const configTemplate = readFileSync(join(TEMPLATES_DIR, 'config.toml'), 'utf8');
  const agentsList = state.agents.map(a => `  "${a}"`).join(',\n');
  const enginesList = answers.engines.map(e => `  "${e}"`).join(',\n');
  let config = configTemplate
    .replace('name = ""', `name = "${answers.project_name}"`)
    .replace('name = ""', `name = "${answers.user_name}"`)
    .replace('chat_language = "pt-br"', `chat_language = "${answers.chat_language}"`)
    .replace('doc_language = "pt-br"', `doc_language = "${answers.doc_language}"`)
    .replace('folder = "_reversa_sdd"', `folder = "${answers.output_folder}"`)
    .replace(
      /\[agents\]\r?\ninstalled = \[[\s\S]*?\]/,
      `[agents]\ninstalled = [\n${agentsList}\n]`
    )
    .replace('installed = []', `installed = [\n${enginesList}\n]`)
    .replace('answer_mode = "chat"', `answer_mode = "${answers.answer_mode}"`);
  _writeNew(join(reversaDir, 'config.toml'), config);

  // config.user.toml
  _writeNew(join(reversaDir, 'config.user.toml'), readFileSync(join(TEMPLATES_DIR, 'config.user.toml'), 'utf8'));

  // plan.md
  const planTemplate = readFileSync(join(TEMPLATES_DIR, 'plan.md'), 'utf8');
  const plan = planTemplate
    .replace('{{PROJECT}}', answers.project_name)
    .replace('{{DATE}}', new Date().toISOString().split('T')[0]);
  _writeNew(join(reversaDir, 'plan.md'), plan);

  // version
  _writeNew(join(reversaDir, 'version'), version);

  // manifest.yaml
  _writeNew(join(configDir, 'manifest.yaml'),
    `installation:\n  version: ${version}\n  installDate: ${new Date().toISOString()}\n  lastUpdated: ${new Date().toISOString()}\n\nengines:\n${answers.engines.map(e => `  - ${e}`).join('\n')}\n\nagents:\n${state.agents.map(a => `  - ${a}`).join('\n')}\n`
  );
}

function _installForwardAssets(reversaDir, answers, version) {
  const forwardSrc = join(TEMPLATES_DIR, 'forward');
  if (!existsSync(forwardSrc)) return;

  const bodySrc = join(forwardSrc, 'body');
  const bodyDest = join(reversaDir, 'templates');
  if (existsSync(bodySrc)) {
    _mkdir(bodyDest);
    for (const file of readdirSync(bodySrc)) {
      const srcFile = join(bodySrc, file);
      const destFile = join(bodyDest, file);
      if (statSync(srcFile).isFile() && !existsSync(destFile)) {
        writeFileSync(destFile, readFileSync(srcFile, 'utf8'), 'utf8');
        _register(destFile);
      }
    }
  }

  for (const flavor of ['sh', 'ps']) {
    const scriptSrc = join(forwardSrc, 'scripts', flavor);
    const scriptDest = join(reversaDir, 'scripts', flavor);
    if (!existsSync(scriptSrc)) continue;
    _mkdir(scriptDest);
    for (const file of readdirSync(scriptSrc)) {
      const srcFile = join(scriptSrc, file);
      const destFile = join(scriptDest, file);
      if (statSync(srcFile).isFile() && !existsSync(destFile)) {
        writeFileSync(destFile, readFileSync(srcFile, 'utf8'), 'utf8');
        _register(destFile);
      }
    }
  }

  const hooksSrc = join(forwardSrc, 'hooks.yml');
  const hooksDest = join(reversaDir, 'hooks.yml');
  if (existsSync(hooksSrc) && !existsSync(hooksDest)) {
    writeFileSync(hooksDest, readFileSync(hooksSrc, 'utf8'), 'utf8');
    _register(hooksDest);
  }

  const setupSrc = join(forwardSrc, 'setup.json');
  const setupDest = join(reversaDir, 'setup.json');
  if (existsSync(setupSrc) && !existsSync(setupDest)) {
    const rendered = readFileSync(setupSrc, 'utf8')
      .replace('{{VERSION}}', version)
      .replace('{{INSTALLED_AT}}', new Date().toISOString())
      .replace('{{PROJECT_NAME}}', answers.project_name ?? '');
    writeFileSync(setupDest, rendered, 'utf8');
    _register(setupDest);
  }
}

function updateGitignore(outputFolder) {
  const gitignorePath = join(PROJECT_ROOT, '.gitignore');
  const lines = [
    '',
    '# Reversa',
    '.reversa/config.user.toml',
    `${outputFolder}/`,
  ].join('\n');

  if (existsSync(gitignorePath)) {
    const existing = readFileSync(gitignorePath, 'utf8');
    if (!existing.includes('# Reversa')) {
      const append = existing.endsWith('\n') ? lines : '\n' + lines;
      writeFileSync(gitignorePath, existing + append, 'utf8');
    }
  } else {
    writeFileSync(gitignorePath, lines.trimStart(), 'utf8');
    _register(gitignorePath);
  }
}

async function main() {
  console.log('  Reversa - Instalação automática (não-interativa)');
  console.log('');

  const selectedEngines = ENGINES.filter(e => ANSWERS.engines.includes(e.id));
  const agents = listAllAgents();

  console.log(`  Engine selecionado: ${selectedEngines.map(e => e.name).join(', ')}`);
  console.log(`  Agentes a instalar: ${agents.length}`);
  console.log('');

  // 1. Instalar skills de cada agente para cada engine selecionada
  for (const agent of agents) {
    for (const engine of selectedEngines) {
      installSkill(agent, engine.skillsDir);
      if (engine.universalSkillsDir && engine.universalSkillsDir !== engine.skillsDir) {
        installSkill(agent, engine.universalSkillsDir);
      }
    }
  }

  // 2. Instalar entry file de cada engine
  for (const engine of selectedEngines) {
    installEntryFile(engine, {
      outputFolder: ANSWERS.output_folder,
      forwardFolder: ANSWERS.output_folder,
    });
  }

  // 3. Criar estrutura .reversa/
  createReversaDir(ANSWERS, VERSION);

  // 4. .gitignore
  if (ANSWERS.git_strategy === 'gitignore') {
    updateGitignore(ANSWERS.output_folder);
  }

  // 5. Salvar created_files no state.json
  const statePath = join(PROJECT_ROOT, '.reversa', 'state.json');
  if (existsSync(statePath)) {
    const state = JSON.parse(readFileSync(statePath, 'utf8'));
    state.created_files = [...new Set([...(state.created_files ?? []), ...createdFiles])];
    writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf8');
  }

  console.log('');
  console.log('  Instalação concluída!');
  console.log(`  Projeto: ${ANSWERS.project_name}`);
  console.log(`  Engine: Opencode (AGENTS.md)`);
  console.log(`  Agentes instalados: ${agents.length}`);
  console.log('');
  console.log('  → Abra o projeto no OpenCode e digite: /reversa');
}

main().catch(err => {
  console.error('Erro durante a instalação:', err);
  process.exit(1);
});
