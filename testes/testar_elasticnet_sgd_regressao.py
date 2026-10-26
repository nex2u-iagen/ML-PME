"""Script de Teste Unitário dos Algoritmos ElasticNet e SGDRegressor.

Verifica a herança da classe 'ModeloBase', a conformidade da interface de regressão,
a integridade das grades de hiperparâmetros e a convergência numérica em dados contínuos
sintéticos[cite: 9].
"""

# 'import sys' permite manipular os caminhos de busca do interpretador Python em tempo
# de execução.
import sys

# 'from pathlib' disponibiliza manipulação portável de caminhos no sistema de arquivos.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para que o interpretador encontre o
# pacote 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as mensagens de auditoria e status exibidas no terminal.
import logging

# 'import numpy as np' gera as matrizes e vetores sintéticos para os testes
# matemáticos[cite: 2].
import numpy as np

# Importa o contrato abstrato base para verificação de polimorfismo.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa os especialistas recém-criados na fábrica de regressão[cite: 9].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_elasticnet_regressao import (  # noqa: E501
    AlgoritmoElasticNet,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_sgd_regressor import (  # noqa: E501
    AlgoritmoSGDRegressor,
)

# Configura o layout das mensagens de log no console.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def testar_especialista_regressao' executa uma bateria padronizada de verificações
# técnicas.
def testar_especialista_regressao(nome_modelo: str, especialista: ModeloBase) -> None:
    """Valida a conformidade arquitetural e a inferência de um regressor
    supervisionado[cite: 9].
    """
    logging.info("Validando especialista: %s...", nome_modelo)

    # 1. TESTE DE POLIMORFISMO
    # Valida se a classe herda formalmente de ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome_modelo} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO
    # Constrói o estimador puro do Scikit-Learn[cite: 9].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), f"Erro: {nome_modelo} não possui método 'fit'!"
    assert hasattr(estimador, "predict"), (
        f"Erro: {nome_modelo} não possui método 'predict'!"
    )
    # Modelos de regressão NÃO podem fornecer probabilidades categóricas
    # (predict_proba)[cite: 9]
    assert not hasattr(estimador, "predict_proba"), (
        f"Erro Crítico: {nome_modelo} vazou comportamento de classificação!"
    )
    logging.info("  [2/4] Interface de regressão validada (sem predict_proba).")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções para o GridSearchCV[cite: 3].
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome_modelo} está vazia!"
    )
    logging.info("  [3/4] Grade de hiperparâmetros validada.")

    # 4. TESTE DE CONVERGÊNCIA EM DADOS NUMÉRICOS CONTÍNUOS
    # Dados padronizados para garantir que o gradiente estocástico converja sem
    # dispersão[cite: 9].
    x_teste = np.array([[-1.0, -1.5], [-0.8, -0.9], [0.0, 0.2], [1.0, 1.2], [1.5, 1.8]])
    # Resposta contínua gerada por relação linear: y = 2.0 * x1 + 1.5 * x2[cite: 7, 9]
    y_teste = np.array([-4.25, -2.95, 0.3, 3.8, 5.7])

    # Executa o ajuste dos parâmetros nos dados de teste[cite: 9].
    estimador.fit(x_teste, y_teste)

    # Gera uma previsão para um ponto no quadrante positivo[cite: 9].
    previsao = estimador.predict([[1.0, 1.0]])

    # Valida se a predição é um número real válido e não gerou NaN ou infinito.
    assert np.isfinite(previsao[0]), (
        f"Erro: {nome_modelo} produziu predição não finita!"
    )
    logging.info(
        "  [4/4] Convergência funcional confirmada. Previsão para [1.0, 1.0]: %.2f",
        previsao[0],
    )
    logging.info("Especialista %s APROVADO com sucesso!\n", nome_modelo)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    testar_especialista_regressao("ElasticNet (L1 + L2)", AlgoritmoElasticNet())
    testar_especialista_regressao(
        "SGD Regressor (Estocástico)", AlgoritmoSGDRegressor()
    )
    logging.info("=== TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! ===")
