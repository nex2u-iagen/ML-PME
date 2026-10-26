"""Script de Teste Unitário dos Algoritmos Huber e Árvore de Decisão para Regressão.

Valida a conformidade da interface 'ModeloBase', a proteção contra vazamento de métodos
de classificação, a integridade estrutural das grades e a convergência em dados
sintéticos.
"""

# 'import sys' permite a inclusão das rotas do projeto nas buscas do interpretador
# Python.
import sys

# 'from pathlib' manipula caminhos e diretórios no sistema operacional de forma
# portável.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para habilitar as importações absolutas
# de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as notificações de auditoria exibidas no console.
import logging

# 'import numpy as np' viabiliza a criação de matrizes sintéticas para os testes
# numéricos[cite: 1].
import numpy as np

# Importa o contrato abstrato base para verificação de polimorfismo.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_arvore_regressao import (  # noqa: E501
    AlgoritmoArvoreRegressao,
)

# Importa os especialistas recém-construídos na fábrica de regressão[cite: 2].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_huber_regressor import (  # noqa: E501
    AlgoritmoHuber,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def testar_especialista_regressao' executa um roteiro padronizado de validação
# técnica.
def testar_especialista_regressao(nome_modelo: str, especialista: ModeloBase) -> None:
    """Valida a conformidade arquitetural e a inferência de um regressor
    supervisionado[cite: 1, 2].
    """
    logging.info("Validando especialista: %s...", nome_modelo)

    # 1. TESTE DE POLIMORFISMO
    # Valida se a classe herda formalmente de ModeloBase.
    assert isinstance(especialista, ModeloBase), (
        f"Erro: {nome_modelo} não herda de ModeloBase!"
    )
    logging.info("  [1/4] Herança de ModeloBase verificada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO
    # Constrói o estimador puro do Scikit-Learn[cite: 2].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), f"Erro: {nome_modelo} não possui método 'fit'!"
    assert hasattr(estimador, "predict"), (
        f"Erro: {nome_modelo} não possui método 'predict'!"
    )
    # Assegura que regressores contínuos NÃO exponham probabilidades
    # (predict_proba)[cite: 1, 2]
    assert not hasattr(estimador, "predict_proba"), (
        f"Erro Crítico: {nome_modelo} vazou método de classificação!"
    )
    logging.info("  [2/4] Interface de regressão validada (sem predict_proba).")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções para o GridSearchCV[cite: 2].
    grade = especialista.obter_grade_hiperparametros()
    assert isinstance(grade, dict) and len(grade) > 0, (
        f"Erro: Grade de {nome_modelo} está vazia!"
    )
    logging.info("  [3/4] Grade de hiperparâmetros validada.")

    # 4. TESTE DE CONVERGÊNCIA EM DADOS NUMÉRICOS CONTÍNUOS
    # Criamos um conjunto com 6 observações e inserimos deliberadamente um outlier na
    # última linha[cite: 1, 2].
    x_teste = np.array(
        [
            [1.0, 1.0],
            [2.0, 2.0],
            [3.0, 3.0],
            [4.0, 4.0],
            [5.0, 5.0],
            [10.0, 10.0],  # Outlier extremo
        ]
    )
    # Resposta contínua esperada: y ~ 2 * x1 + 3 * x2, com o último ponto ruidoso[cite:
    # 1, 2, 6]
    y_teste = np.array([5.0, 10.0, 15.0, 20.0, 25.0, 150.0])

    # Executa o ajuste dos parâmetros nos dados de teste[cite: 1, 2].
    estimador.fit(x_teste, y_teste)

    # Realiza uma predição em um ponto intermediário não visto[cite: 1, 2].
    previsao = estimador.predict([[2.5, 2.5]])

    # Valida se a predição é um número real válido e finito.
    assert np.isfinite(previsao[0]), (
        f"Erro: {nome_modelo} produziu predição não finita!"
    )
    logging.info(
        "  [4/4] Convergência funcional confirmada. Previsão para [2.5, 2.5]: %.2f",
        previsao[0],
    )
    logging.info("Especialista %s APROVADO com sucesso!\n", nome_modelo)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    testar_especialista_regressao(
        "Huber Regressor (Robusto a Outliers)", AlgoritmoHuber()
    )
    testar_especialista_regressao(
        "Decision Tree Regressor (Árvore Lógica)", AlgoritmoArvoreRegressao()
    )
    logging.info("=== TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! ===")
