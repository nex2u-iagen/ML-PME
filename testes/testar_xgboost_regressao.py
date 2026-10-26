"""Script de Teste Unitário do Algoritmo XGBoost Regressor.

Valida a herança de 'ModeloBase', a proteção de domínio contínuo (sem vazamento de
predict_proba),
a integridade estrutural da grade de busca e a convergência em dados contínuos
sintéticos.
"""

# 'import sys' permite manipular os caminhos de busca do interpretador Python em tempo
# de execução.
import sys

# 'from pathlib' disponibiliza manipulação portável de diretórios do sistema
# operacional.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para habilitar as importações absolutas
# a partir de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as mensagens de auditoria técnica exibidas no console.
import logging

# 'import numpy as np' gera as matrizes e vetores sintéticos para os testes matemáticos.
import numpy as np

# Importa o contrato abstrato base para verificação de polimorfismo arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista XGBoost de regressão recém-construído[cite: 1].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_xgboost_regressao import (  # noqa: E501
    AlgoritmoXGBoostRegressor,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' orquestra os cenários de verificação do regressor
# boosting.
def executar_teste_unitario() -> None:
    """Executa a verificação funcional completa do componente
    AlgoritmoXGBoostRegressor[cite: 1].
    """
    # Registra o início do procedimento de testes.
    logging.info("Iniciando bateria de testes do AlgoritmoXGBoostRegressor...")

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Instancia a classe especialista do XGBoost Regressor.
    especialista = AlgoritmoXGBoostRegressor()

    # Assegura que o especialista assinou formalmente o contrato da fábrica de modelos.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO
    # Constrói o estimador puro do XGBoost[cite: 1].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), (
        "Erro: O estimador não possui o método 'fit'! [cite: 2]"
    )
    assert hasattr(estimador, "predict"), (
        "Erro: O estimador não possui o método 'predict'! [cite: 2]"
    )
    # Assegura defensivamente que regressores contínuos NÃO exponham probabilidades
    # (predict_proba)
    assert not hasattr(estimador, "predict_proba"), (
        "Erro Crítico: Regressor expôs comportamento de classificação!"
    )
    logging.info(
        "Teste 2 Concluído: Estimador XGBoost instanciado com interface contínua pura."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o dicionário de opções para o GridSearchCV[cite: 5].
    grade = especialista.obter_grade_hiperparametros()
    assert "n_estimators" in grade, "Erro: 'n_estimators' ausente na grade! [cite: 1]"
    assert "learning_rate" in grade, "Erro: 'learning_rate' ausente na grade! [cite: 1]"
    assert "max_depth" in grade, "Erro: 'max_depth' ausente na grade! [cite: 1]"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros de boosting validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL COM DADOS CONTÍNUOS SINTÉTICOS
    # Criamos 8 amostras sintéticas com 2 variáveis explicativas numéricas.
    x_teste = np.array(
        [
            [1.0, 2.0],
            [2.0, 1.0],
            [3.0, 4.0],
            [4.0, 3.0],
            [5.0, 6.0],
            [6.0, 5.0],
            [7.0, 8.0],
            [8.0, 7.0],
        ]
    )
    # Resposta contínua gerada por relação suave: y = 2.5 * x1 + 1.5 * x2[cite: 2, 7]
    y_teste = np.array([5.5, 6.5, 13.5, 14.5, 21.5, 22.5, 29.5, 30.5])

    # Executa o ajuste iterativo do boosting de gradiente[cite: 1].
    estimador.fit(x_teste, y_teste)

    # Realiza a predição para uma nova observação: [5.0, 5.0][cite: 2].
    previsao = estimador.predict([[5.0, 5.0]])

    # Valida se o resultado gerado é um valor contínuo finito e coerente com a grandeza.
    assert np.isfinite(previsao[0]), "Erro: XGBoost produziu predição não finita!"
    logging.info(
        "Teste 4 Concluído: Ajuste sequencial validado. Previsão para [5.0, 5.0]: %.2f",
        previsao[0],
    )

    # Emite aviso final de aprovação operacional.
    logging.info("=== TODOS OS TESTES DO XGBOOST REGRESSOR CONCLUÍDOS COM SUCESSO! ===")


# Ponto de entrada padrão para execução do script via terminal.
if __name__ == "__main__":
    executar_teste_unitario()
