"""Script de Teste Unitário da Ala de Agrupamento Não Supervisionado.

Valida a herança de 'ModeloBase', a correta instanciação, a integridade das grades
de hiperparâmetros e a convergência funcional em dados sintéticos 2D para:
KMeans, DBSCAN, Agrupamento Hierárquico, GMM e Mean Shift.
"""

# 'import sys' permite a manipulação de rotas do sistema para carregamento de módulos.
import sys

# 'from pathlib' disponibiliza classes portáveis para manipulação de caminhos no sistema
# operacional.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para que o interpretador reconheça o
# pacote 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as notificações e relatórios de auditoria exibidos no
# terminal.
import logging

# 'import numpy as np' gera as matrizes e conjuntos espaciais sintéticos para testes
# matemáticos.
import numpy as np

# 'from sklearn.metrics' importa a medição de coesão e separação espacial entre
# clusters.
from sklearn.metrics import silhouette_score

# Importa a classe abstrata universal para assegurar o cumprimento estrito do contrato
# da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_dbscan_agrupamento import (  # noqa: E501
    AlgoritmoDBSCAN,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_gmm_agrupamento import (  # noqa: E501
    AlgoritmoGMM,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_hierarquico_agrupamento import (  # noqa: E501
    AlgoritmoHierarquico,
)

# Importa todos os 5 especialistas da ala de agrupamento não supervisionado.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_kmeans_agrupamento import (  # noqa: E501
    AlgoritmoKMeans,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_mean_shift_agrupamento import (  # noqa: E501
    AlgoritmoMeanShift,
)

# Configura o layout das mensagens de log no console.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def auditar_especialista_agrupamento' centraliza o roteiro formal de testes para
# qualquer clusterizador.
def auditar_especialista_agrupamento(
    nome: str, especialista: ModeloBase, x_dados: np.ndarray
) -> None:
    """Valida a conformidade arquitetural e a inferência não supervisionada de um
    agrupador.
    """
    logging.info("--- Iniciando auditoria técnica: %s ---", nome)

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Valida se o especialista implementa formalmente o contrato universal ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR E PROTEÇÃO DE DOMÍNIO
    # Instancia o estimador puro da biblioteca.
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), f"Erro: {nome} não possui o método 'fit'!"

    # Assegura que o estimador contenha método de inferência ou rotulagem não
    # supervisionada.
    possui_metodo_predicao = hasattr(estimador, "predict") or hasattr(
        estimador, "fit_predict"
    )
    assert possui_metodo_predicao, (
        f"Erro: {nome} não possui mecanismo de inferência de grupos!"
    )
    logging.info("  [2/4] Interface de estimador não supervisionado validada.")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções para otimização sistemática.
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome} está vazia!"
    )
    logging.info(
        "  [3/4] Grade de hiperparâmetros validada (%d chaves configuradas).",
        len(grade),
    )

    # 4. TESTE DE AJUSTE FUNCIONAL NÃO SUPERVISIONADO (SEM GABARITO 'y')
    # O ajuste deve ocorrer estritamente sobre a matriz explicativa X_dados.
    if hasattr(estimador, "fit_predict"):
        rotulos = estimador.fit_predict(x_dados)
    else:
        # No caso do GMM, executamos fit e depois predict dos componentes gaussianos.
        estimador.fit(x_dados)
        rotulos = estimador.predict(x_dados)

    # Valida se o vetor de rótulos possui a mesma quantidade de linhas da matriz de
    # entrada.
    assert len(rotulos) == len(x_dados), (
        f"Erro: Dimensão dos rótulos divergente em {nome}!"
    )

    # Filtra ruídos (-1 do DBSCAN) para avaliar a formação de grupos legítimos.
    rotulos_validos = rotulos[rotulos != -1]
    grupos_distintos = np.unique(rotulos_validos)

    # Confirma se o algoritmo conseguiu formar pelo menos um agrupamento válido.
    assert len(grupos_distintos) >= 1, f"Erro: {nome} não formou nenhum grupo válido!"
    logging.info(
        "  [4/4] Convergência confirmada. Grupos distintos identificados: %s",
        list(grupos_distintos),
    )

    # Avaliação de qualidade geométrica: se houver 2 ou mais grupos, calculamos o
    # Coeficiente de Silhueta.
    if len(grupos_distintos) >= 2:
        # Calculamos a silhueta considerando apenas os pontos atribuídos a clusters
        # válidos.
        indices_validos = np.where(rotulos != -1)[0]
        if len(indices_validos) > len(grupos_distintos):
            pontuacao_silhueta = silhouette_score(
                x_dados[indices_validos], rotulos[indices_validos]
            )
            logging.info(
                "        Qualidade geométrica (Silhueta): %.4f", pontuacao_silhueta
            )

    logging.info("Especialista %s APROVADO com sucesso!\n", nome)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info("=== INICIANDO BATERIA DE AUDITORIA DA ALA DE AGRUPAMENTO ===\n")

    # Criamos uma base sintética 2D com 12 observações distribuídas em 2 regiões
    # distantes no espaço.
    # Região 1 centralizada em torno de (-10, -10) e Região 2 em torno de (+10, +10).
    x_sintetico = np.array(
        [
            [-10.0, -10.2],
            [-9.8, -10.0],
            [-10.1, -9.9],
            [-10.2, -10.1],
            [-9.9, -10.3],
            [-10.0, -9.8],
            [10.0, 10.2],
            [9.8, 10.0],
            [10.1, 9.9],
            [10.2, 10.1],
            [9.9, 10.3],
            [10.0, 9.8],
        ]
    )

    # Dicionário contendo os 5 especialistas da ala de agrupamento.
    especialistas_agrupamento = {
        "K-Means (Centroides Globais)": AlgoritmoKMeans(),
        "DBSCAN (Densidade Espacial com Ruído)": AlgoritmoDBSCAN(),
        "Hierárquico Aglomerativo (Ward/Dendrograma)": AlgoritmoHierarquico(),
        "GMM (Modelos de Misturas Gaussianas)": AlgoritmoGMM(),
        "Mean Shift (Deslocamento de Médias)": AlgoritmoMeanShift(),
    }

    # Itera por cada especialista e executa a auditoria completa.
    for nome_algoritmo, instancia in especialistas_agrupamento.items():
        auditar_especialista_agrupamento(nome_algoritmo, instancia, x_sintetico)

    logging.info(
        "=== TODOS OS 5 ALGORITMOS DE AGRUPAMENTO FORAM AUDITADOS E APROVADOS! ==="
    )
