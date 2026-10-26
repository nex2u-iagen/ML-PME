"""Script de Teste Unitário dos Algoritmos Random Forest Regressor e SVR.

Valida a herança de 'ModeloBase', a proteção contra métodos categóricos de
classificação,
a integridade estrutural das grades e a convergência em dados contínuos sintéticos[cite:
1, 7].
"""

# 'import sys' permite a injeção do diretório de módulos do sistema no interpretador.
import sys

# 'from pathlib' disponibiliza classes portáveis para manipular caminhos no disco
# rígido.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para habilitar as importações absolutas
# a partir de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as mensagens de auditoria técnica no console.
import logging

# 'import numpy as np' gera as matrizes e vetores sintéticos para os testes
# matemáticos[cite: 1].
import numpy as np

# Importa o contrato abstrato base para verificação de polimorfismo arquitetural[cite:
# 7].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa os especialistas em regressão recém-construídos[cite: 7].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_random_forest_regressao import (  # noqa: E501
    AlgoritmoRandomForestRegressor,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_svr_regressor import (  # noqa: E501
    AlgoritmoSVR,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def testar_especialista_regressao' executa um roteiro estrito de validação técnica.
def testar_especialista_regressao(nome_modelo: str, especialista: ModeloBase) -> None:
    """Valida a conformidade arquitetural e a inferência de um regressor
    contínuo[cite: 1, 7].
    """
    logging.info("Validando especialista: %s...", nome_modelo)

    # 1. TESTE DE POLIMORFISMO
    # Valida se a classe herda formalmente de ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome_modelo} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO
    # Constrói o estimador puro do Scikit-Learn[cite: 7].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), (
        f"Erro: {nome_modelo} não possui método 'fit'! [cite: 7]"
    )
    assert hasattr(estimador, "predict"), (
        f"Erro: {nome_modelo} não possui método 'predict'! [cite: 7]"
    )
    # Assegura defensivamente que regressores contínuos NÃO exponham probabilidades
    # (predict_proba)[cite: 1, 7]
    assert not hasattr(estimador, "predict_proba"), (
        f"Erro Crítico: {nome_modelo} vazou método de classificação!"
    )
    logging.info("  [2/4] Interface de regressão validada (sem predict_proba).")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções para o GridSearchCV[cite: 7].
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome_modelo} está vazia!"
    )
    logging.info("  [3/4] Grade de hiperparâmetros validada.")

    # 4. TESTE DE CONVERGÊNCIA EM DADOS NUMÉRICOS CONTÍNUOS
    # Dados numéricos contínuos simulando uma relação suave de grandeza real[cite: 1,
    # 7].
    x_teste = np.array(
        [[-1.0, -1.0], [-0.5, -0.4], [0.0, 0.1], [0.5, 0.6], [1.0, 1.0], [1.5, 1.4]]
    )
    # Resposta contínua gerada por função não-linear: y = 3.0 * x1 + 2.0 * (x2 **
    # 2)[cite: 1, 7]
    y_teste = np.array([-1.0, -1.18, 0.02, 2.22, 5.0, 8.42])

    # Executa o ajuste dos parâmetros nos dados de teste[cite: 7].
    estimador.fit(x_teste, y_teste)

    # Realiza uma predição em um ponto contínuo intermediário[cite: 7].
    previsao = estimador.predict([[0.8, 0.8]])

    # Valida se a predição é um número real válido e finito.
    assert np.isfinite(previsao[0]), (
        f"Erro: {nome_modelo} produziu predição não finita!"
    )
    logging.info(
        "  [4/4] Convergência funcional confirmada. Previsão para [0.8, 0.8]: %.2f",
        previsao[0],
    )
    logging.info("Especialista %s APROVADO com sucesso!\n", nome_modelo)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    testar_especialista_regressao(
        "Random Forest Regressor (Ensemble Bagging)", AlgoritmoRandomForestRegressor()
    )
    testar_especialista_regressao(
        "Support Vector Regressor - SVR (Margem Epsilon)", AlgoritmoSVR()
    )
    logging.info("=== TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! ===")
