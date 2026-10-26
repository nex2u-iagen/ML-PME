"""Script de Teste Unitário dos Algoritmos Ridge e Lasso (Regressão).

Valida a aderência ao contrato 'ModeloBase' e assegura que ambos executam
a regressão contínua sem quebras estruturais ou vazamento de métodos de
classificação[cite: 1].
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import logging

import numpy as np

from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_lasso_regressao import (  # noqa: E501
    AlgoritmoLasso,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_ridge_regressao import (  # noqa: E501
    AlgoritmoRidge,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


def testar_regressor(nome: str, instancia_especialista: ModeloBase) -> None:
    """Motor genérico de validação para modelos de regressão."""
    logging.info(f"--- Iniciando testes para: {nome} ---")

    # 1. Herança Polimórfica
    assert isinstance(instancia_especialista, ModeloBase), (
        f"Erro: {nome} não herda de ModeloBase!"
    )

    # 2. Construção e Proteção de Domínio
    estimador = instancia_especialista.construir_estimador()
    assert hasattr(estimador, "fit"), f"Erro: {nome} não possui 'fit'."
    assert hasattr(estimador, "predict"), f"Erro: {nome} não possui 'predict'."
    # Modelos de regressão NÃO devem calcular probabilidades!
    assert not hasattr(estimador, "predict_proba"), (
        f"Erro Crítico: {nome} vazou comportamento de classificação!"
    )

    # 3. Integridade da Grade
    grade = instancia_especialista.obter_grade_hiperparametros()
    assert "alpha" in grade, f"Erro: {nome} precisa calibrar 'alpha' obrigatoriamente."

    # 4. Convergência Contínua (Matemática)
    x_teste = np.array([[1.0, 2.0], [2.0, 0.0], [0.0, 1.0], [3.0, 4.0]])
    y_teste = np.array([13.0, 9.0, 8.0, 23.0])  # Grandezas contínuas

    estimador.fit(x_teste, y_teste)
    previsao = estimador.predict([[1.0, 1.0]])

    logging.info(f"{nome} treinado com sucesso. Previsão de teste: {previsao[0]:.2f}")


if __name__ == "__main__":
    testar_regressor("Ridge Regression (L2)", AlgoritmoRidge())
    testar_regressor("Lasso Regression (L1)", AlgoritmoLasso())
    logging.info("=== BATERIA DE TESTES DE REGULARIZAÇÃO CONCLUÍDA COM SUCESSO! ===")
