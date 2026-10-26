# 📐 `src/nucleo/contratos/` — Contratos estruturais

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [nucleo](../README.md)

## 🎯 Objetivo

Definir as **assinaturas mínimas** que os componentes do projeto devem cumprir,
usando `typing.Protocol` (tipagem estrutural). O contrato não obriga herança
nominal: qualquer classe que implemente os métodos com a assinatura correta é
aceita.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Nada em tempo de execução. É um módulo de definições. |
| **Processa** | Nenhum dado. Apenas declara interfaces e tipos. |
| **Entrega para** | Leitores de arquivo, visualizadores e qualquer componente que precise programar contra uma abstração. |
| **Quem consome** | `acesso_dados`, `diagnostico_estatistico` e fases que injetam dependências. |

## 🧩 Arquivos

| Arquivo | Conteúdo | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `protocolos.py` | `ProtocoloLeitorArquivos` e `ProtocoloVisualizador`. | Nenhum dado. | Declara métodos obrigatórios. | Contratos usados em type hints e injeção de dependência. |

### `protocolos.py` em detalhe

| Protocolo | Métodos | Assinatura esperada | Implementações típicas |
| :--- | :--- | :--- | :--- |
| `ProtocoloLeitorArquivos` | `carregar_tabela` | `(caminho_arquivo: Path, **kwargs: Any) -> pd.DataFrame` | `LeitorArquivosTabulares` |
| `ProtocoloLeitorArquivos` | `carregar_em_lotes` | `(caminho_arquivo: Path, tamanho_lote: int, **kwargs: Any) -> Generator[pd.DataFrame, None, None]` | `LeitorArquivosTabulares` |
| `ProtocoloVisualizador` | `salvar_figura` | `(figura: Any, caminho_saida: Path) -> Path` | `GeradorVisualizacaoGrafica` |

## 📥 Entradas e 📤 saídas

- **Entrada:** nenhuma. O módulo só é importado.
- **Saída:** classes `Protocol` utilizáveis em anotações de tipo e em `isinstance`
  apenas quando marcadas com `@runtime_checkable` (quando aplicável).

## 🔗 Ligações

- Implementação de leitura: [acesso_dados](../acesso_dados/README.md).
- Implementação de gráficos: [diagnostico_estatistico](../diagnostico_estatistico/README.md).
- Voltar para [nucleo](../README.md).
