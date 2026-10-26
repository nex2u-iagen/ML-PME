"""Script de Teste Unitário da Ala de Redução de Dimensionalidade Não Supervisionada.

Valida a herança de 'ModeloBase', a conformidade da interface transformadora
(fit_transform),
a integridade das grades de hiperparâmetros e a contração efetiva de 4 dimensões para 2
para os 5 especialistas: PCA, Truncated SVD, Kernel PCA, t-SNE e UMAP.
"""

# 'import sys' viabiliza a inclusão dinâmica do diretório raiz nas buscas do
# interpretador Python.
import sys

# 'from pathlib' disponibiliza classes portáveis para manipular rotas no sistema
# operacional.
from pathlib import Path

# Registra a pasta principal do projeto no 'sys.path' para habilitar as importações
# absolutas a partir de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as mensagens e notificações de auditoria exibidas no
# console.
import logging

# 'import numpy as np' gera as matrizes sintéticas de alta dimensão para simulação
# matemática[cite: 2].
import numpy as np

# Importa o contrato abstrato universal da fábrica para assegurar a consistência do
# design.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.reducao_dimensionalidade.alg_kernel_pca_reducao import (  # noqa: E501
    AlgoritmoKernelPCA,
)

# Importa os 5 especialistas em redução de dimensionalidade construídos na fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.reducao_dimensionalidade.alg_pca_reducao import (  # noqa: E501
    AlgoritmoPCA,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.reducao_dimensionalidade.alg_truncated_svd_reducao import (  # noqa: E501
    AlgoritmoTruncatedSVD,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.reducao_dimensionalidade.alg_tsne_reducao import (  # noqa: E501
    AlgoritmoTSNE,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.reducao_dimensionalidade.alg_umap_reducao import (  # noqa: E501
    AlgoritmoUMAP,
)

# Configura o layout textual dos registros de log no terminal de auditoria.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def auditar_especialista_reducao' centraliza a bateria formal de validação de
# qualquer redutor.
def auditar_especialista_reducao(
    nome: str, especialista: ModeloBase, x_alta_dim: np.ndarray
) -> None:
    """Valida o polimorfismo, a construção e a transformação dimensional de um
    redutor.
    """
    logging.info("--- Iniciando auditoria técnica: %s ---", nome)

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Valida se a classe implementa formalmente o contrato abstrato universal
    # ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Tenta construir o estimador, tratando graciosamente dependências opcionais.
    try:
        estimador = especialista.construir_estimador()
    except ImportError as aviso_lib:
        logging.warning("  [PULADO] %s não pôde ser instanciado: %s", nome, aviso_lib)
        return

    # Redutores de dimensionalidade devem implementar 'fit' e a interface de
    # transformação 'fit_transform'[cite: 2, 6].
    assert hasattr(estimador, "fit"), (
        f"Erro: {nome} não possui o método fundamental 'fit'! [cite: 6]"
    )
    assert hasattr(estimador, "fit_transform"), (
        f"Erro: {nome} não possui o método 'fit_transform'!"
    )
    logging.info("  [2/4] Interface de transformação dimensional validada.")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções estruturais para ajuste fino[cite: 6].
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome} está vazia!"
    )
    logging.info(
        "  [3/4] Grade de hiperparâmetros validada (%d chaves configuradas).",
        len(grade),
    )

    # 4. TESTE DE COMPACTAÇÃO DIMENSIONAL FUNCIONAL (SEM GABARITO 'y')
    # Aplicamos a transformação diretamente na matriz X de 4 dimensões, projetando-a
    # para 2 dimensões[cite: 2, 5].
    x_reduzido = estimador.fit_transform(x_alta_dim)

    # Validações matemáticas da compressão:
    # A) A quantidade de linhas da matriz final deve ser rigorosamente preservada.
    assert x_reduzido.shape[0] == x_alta_dim.shape[0], (
        f"Erro: Quantidade de amostras alterada! Esperado {x_alta_dim.shape[0]}, obtido"
        f"{x_reduzido.shape[0]}"
    )
    # B) A dimensão de colunas deve ter sido reduzida de 4 para exatamente 2
    # componentes[cite: 2, 5].
    assert x_reduzido.shape[1] == 2, (
        f"Erro: Dimensionalidade incorreta! Esperado 2 eixos, obtido"
        f"{x_reduzido.shape[1]}"
    )
    # C) Nenhuma posição pode conter valores nulos (NaN) ou infinitos.
    assert np.all(np.isfinite(x_reduzido)), (
        f"Erro: {nome} gerou coordenadas não finitas ou NaN!"
    )

    logging.info(
        "  [4/4] Compressão funcional confirmada: Matriz original (%dx%d) -> Projetada"
        "(%dx%d).",
        x_alta_dim.shape[0],
        x_alta_dim.shape[1],
        x_reduzido.shape[0],
        x_reduzido.shape[1],
    )
    logging.info("Especialista %s APROVADO com sucesso!\n", nome)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info(
        "=== INICIANDO BATERIA DE AUDITORIA DA REDUÇÃO DE DIMENSIONALIDADE ===\n"
    )

    # Fixamos uma semente para gerar dados sintéticos estáveis[cite: 6].
    np.random.seed(42)

    # Criamos 40 amostras em 4 dimensões divididas em 4 grupos de 10 observações[cite:
    # 2, 5]:
    # Grupo 1 centrado em (0, 0, 0, 0)
    g1 = np.random.normal(loc=0.0, scale=0.5, size=(10, 4))
    # Grupo 2 centrado em (10, 10, 10, 10)
    g2 = np.random.normal(loc=10.0, scale=0.5, size=(10, 4))
    # Grupo 3 centrado em (-10, -10, 5, 5)
    g3 = np.random.normal(loc=[-10.0, -10.0, 5.0, 5.0], scale=0.5, size=(10, 4))
    # Grupo 4 centrado em (5, -5, 10, -10)
    g4 = np.random.normal(loc=[5.0, -5.0, 10.0, -10.0], scale=0.5, size=(10, 4))

    # Concatena os 4 grupos resultando em uma matriz (40, 4) com N=40 observações[cite:
    # 2, 5].
    # Isso satisfaz perfeitamente a condição: perplexity (30) < n_samples (40)[cite: 2,
    # 7].
    x_sintetico_4d = np.vstack([g1, g2, g3, g4])

    # Dicionário contendo os 5 especialistas da ala de redução de dimensionalidade[cite:
    # 2, 7].
    especialistas_reducao = {
        "PCA (Componentes Principais Globais)": AlgoritmoPCA(),
        "Truncated SVD (Fatoração para Esparsas)": AlgoritmoTruncatedSVD(),
        "Kernel PCA (Projeção Não-Linear RBF)": AlgoritmoKernelPCA(),
        "t-SNE (Afinidade Probabilística 2D)": AlgoritmoTSNE(),
        "UMAP (Variedades Topológicas)": AlgoritmoUMAP(),
    }

    # Itera por cada especialista e executa a auditoria completa.
    for nome_algoritmo, instancia in especialistas_reducao.items():
        auditar_especialista_reducao(nome_algoritmo, instancia, x_sintetico_4d)

    logging.info("=== TODOS OS ALGORITMOS DE REDUÇÃO FORAM AUDITADOS COM SUCESSO! ===")
