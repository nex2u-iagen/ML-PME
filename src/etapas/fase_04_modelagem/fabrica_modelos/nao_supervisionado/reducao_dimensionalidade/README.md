# 🧊 `src/etapas/fase_04_modelagem/fabrica_modelos/nao_supervisionado/reducao_dimensionalidade/` — Redução de dimensionalidade

> **Navegação:** [README raiz](../../../../../../README.md) · [src](../../../../../README.md) · [etapas](../../../../README.md) · [fase_04](../../../README.md) · [fabrica](../../README.md) · [nao_supervisionado](../README.md)

## 🎯 Objetivo

Projetar `X` de alta dimensão em um espaço menor, preservando estrutura, variância
ou vizinhança. Útil para visualização, compressão e mitigação da maldição da
dimensionalidade.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Scripts/testes de redução e análises exploratórias, com `X` numérico. |
| **Processa** | Ajuste da projeção e transformação das amostras. |
| **Entrega para** | Matriz `X` reduzida (2D ou `n_components`). |
| **Quem consome** | Visualizações, clustering e experimentos. |

## 🧩 Arquivos

| Arquivo | Classe | Tipo | Linear? | Uso típico |
| :--- | :--- | :--- | :---: | :--- |
| `alg_pca_reducao.py` | `AlgoritmoPCA` | Variância | Sim | Compressão e visualização. |
| `alg_kernel_pca_reducao.py` | `AlgoritmoKernelPCA` | Kernel | Não | Estruturas não lineares. |
| `alg_truncated_svd_reducao.py` | `AlgoritmoTruncatedSVD` | Fatoração | Sim | Matrizes esparsas/texto. |
| `alg_tsne_reducao.py` | `AlgoritmoTSNE` | Vizinho estocástico | Não | Visualização 2D/3D. |
| `alg_umap_reducao.py` | `AlgoritmoUMAP` | Topologia | Não | Visualização e preservação global/local. |

## 📥 Entradas e 📤 saídas

| Método | Entrada | Saída |
| :--- | :--- | :--- |
| `construir_estimador(42)` | Semente | Redutor não treinado |
| `fit(X)` | Matriz de alta dimensão | Projeção aprendida |
| `transform(X)` | Matriz de alta dimensão | Matriz `n × n_components` |
| `fit_transform(X)` | Matriz de alta dimensão | Matriz reduzida diretamente |

## 📌 Regras

- PCA e SVD exigem `X` numérico e, idealmente, padronizado.
- t-SNE e UMAP são para **visualização**; não use a projeção como feature de
  produção sem validação.
- O número de componentes deve ser justificado (variância explicada ou objetivo).
- A projeção aprendida no treino deve ser reaplicada no teste.

## 🔗 Ligações

- Teste da ala: [`testes/testar_reducao_dimensionalidade.py`](../../../../../../testes/testar_reducao_dimensionalidade.py).
- Voltar para [nao_supervisionado](../README.md).
