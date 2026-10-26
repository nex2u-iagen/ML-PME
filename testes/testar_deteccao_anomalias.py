"""Script de Teste Unitário da Ala de Detecção de Anomalias Não Supervisionada.

Valida a herança de 'ModeloBase', a conformidade das interfaces de inferência e a
discriminação funcional (+1 para inlier, -1 para outlier) para todos os 5
especialistas[cite: 15].
"""

# 'import sys' viabiliza a inclusão do diretório do projeto nas buscas de módulos do
# interpretador Python.
import sys

# 'from pathlib' disponibiliza classes portáveis para manipular rotas no sistema
# operacional.
from pathlib import Path

# Registra a pasta principal do projeto no 'sys.path' para habilitar as importações
# absolutas a partir de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as mensagens de auditoria técnica exibidas no console.
import logging

# 'import numpy as np' gera as matrizes sintéticas de calibração espacial e os pontos
# anômalos[cite: 1].
import numpy as np

# Importa o contrato abstrato universal da fábrica para assegurar o design
# polimórfico[cite: 1].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.deteccao_anomalias.alg_envelope_eliptico_anomalias import (  # noqa: E501
    AlgoritmoEnvelopeEliptico,
)

# Importa os 5 especialistas em detecção de anomalias da fábrica[cite: 15].
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.deteccao_anomalias.alg_isolation_forest_anomalias import (  # noqa: E501
    AlgoritmoIsolationForest,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.deteccao_anomalias.alg_lof_anomalias import (  # noqa: E501
    AlgoritmoLOF,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.deteccao_anomalias.alg_one_class_svm_anomalias import (  # noqa: E501
    AlgoritmoOneClassSVM,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.deteccao_anomalias.alg_sgd_one_class_svm_anomalias import (  # noqa: E501
    AlgoritmoSGDOneClassSVM,
)

# Configura o layout textual das saídas de auditoria no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def auditar_especialista_anomalia' centraliza a bateria formal de validação de cada
# detector.
def auditar_especialista_anomalia(
    nome: str,
    especialista: ModeloBase,
    x_treino_normal: np.ndarray,
    x_teste_inlier: np.ndarray,
    x_teste_outlier: np.ndarray,
) -> None:
    """Valida o polimorfismo, a construção e a capacidade de discriminação (+1 vs -1)
    do especialista[cite: 15].
    """
    logging.info("--- Iniciando auditoria técnica: %s ---", nome)

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Valida se a classe implementa formalmente o contrato universal ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR E PROTEÇÃO DE DOMÍNIO
    # Instancia o estimador puro ou a Pipeline do Scikit-Learn[cite: 1, 8].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), (
        f"Erro: {nome} não possui o método fundamental 'fit'! [cite: 1]"
    )
    assert hasattr(estimador, "predict"), (
        f"Erro: {nome} não possui o método de inferência 'predict'! [cite: 15]"
    )
    logging.info(
        "  [2/4] Interface de detecção de anomalias validada (possui fit e predict)."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções de afinação do algoritmo.
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome} está vazia!"
    )
    logging.info(
        "  [3/4] Grade de hiperparâmetros validada (%d chaves configuradas).",
        len(grade),
    )

    # 4. TESTE FUNCIONAL DE AJUSTE E DISCRIMINAÇÃO (+1 PARA INLIER, -1 PARA OUTLIER)
    # Treina o modelo estritamente nos dados normais, sem qualquer vetor 'y' de
    # gabarito[cite: 11, 12, 15].
    estimador.fit(x_treino_normal)

    # Gera a predição para o ponto legítimo posicionado no centro da distribuição[cite:
    # 15].
    pred_inlier = estimador.predict(x_teste_inlier)
    # Gera a predição para o ponto anômalo situado deliberadamente a quilômetros de
    # distância[cite: 15].
    pred_outlier = estimador.predict(x_teste_outlier)

    # Validações dos rótulos segundo a convenção Scikit-Learn (+1 inlier, -1
    # outlier)[cite: 15]:
    assert pred_inlier[0] == 1, (
        f"Erro em {nome}: Ponto legítimo central classificado incorretamente como"
        f"{pred_inlier[0]}!"
    )
    assert pred_outlier[0] == -1, (
        f"Erro em {nome}: Ponto anômalo distante classificado incorretamente como"
        f"{pred_outlier[0]}!"
    )

    logging.info(
        "  [4/4] Discriminação funcional confirmada: Inlier -> [%d], Outlier -> [%d].",
        pred_inlier[0],
        pred_outlier[0],
    )
    logging.info("Especialista %s APROVADO com sucesso!\n", nome)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info("=== INICIANDO BATERIA DE AUDITORIA DE DETECÇÃO DE ANOMALIAS ===\n")

    # Fixamos a semente aleatória para gerar dados sintéticos homogêneos e
    # estáveis[cite: 1].
    np.random.seed(42)

    # Geramos uma população representativa com N=200 amostras normais centradas em (0,
    # 0)[cite: 1, 15].
    x_treino_saudavel = np.random.normal(loc=0.0, scale=0.8, size=(200, 2))

    # Amostra de teste inlier: ponto representativo no centro da nuvem saudável[cite:
    # 15].
    ponto_teste_inlier = np.array([[0.1, -0.1]])

    # Amostra de teste outlier: anomalia distante situada no deserto espacial (+25,
    # +25)[cite: 15].
    ponto_teste_outlier = np.array([[25.0, 25.0]])

    # Dicionário contendo os 5 especialistas da ala de detecção de anomalias[cite: 15].
    especialistas_anomalias = {
        "Isolation Forest (Particionamento por Árvores)": AlgoritmoIsolationForest(),
        "Local Outlier Factor - LOF (Densidade Local)": AlgoritmoLOF(),
        "One-Class SVM (Fronteira com Kernel RBF)": AlgoritmoOneClassSVM(),
        "Envelope Elíptico (FastMCD e Distância de Mahalanobis)": AlgoritmoEnvelopeEliptico(),  # noqa: E501
        "SGD One-Class SVM (Aproximação RBF Nystroem para Grandes Volumes)": AlgoritmoSGDOneClassSVM(),  # noqa: E501
    }

    # Itera por cada especialista e executa a auditoria completa.
    for nome_algoritmo, instancia in especialistas_anomalias.items():
        auditar_especialista_anomalia(
            nome_algoritmo,
            instancia,
            x_treino_saudavel,
            ponto_teste_inlier,
            ponto_teste_outlier,
        )

    logging.info(
        "=== TODOS OS 5 ALGORITMOS DE DETECÇÃO DE ANOMALIAS FORAM AUDITADOS E"
        "APROVADOS! ==="
    )
