"""Script de Teste Unitário do Algoritmo Regressão Linear (OLS).

Valida a aderência ao contrato abstrato 'ModeloBase', a correta instanciação
do estimador analítico, a extração dos hiperparâmetros e a convergência em dados
contínuos[cite: 1, 6].
"""

# 'import sys' permite manipular os caminhos de carregamento de módulos do interpretador
# Python.
import sys

# 'from pathlib' manipula pastas e arquivos com segurança entre diferentes sistemas
# operacionais.
from pathlib import Path

# Injeta a pasta raiz do projeto no 'sys.path' para habilitar as importações absolutas a
# partir de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia o envio padronizado de relatórios e auditorias para o
# console.
import logging

# 'import numpy as np' gera e manipula as matrizes numéricas sintéticas para o teste
# unitário.
import numpy as np

# Importa a classe abstrata base para validar se a interface foi respeitada.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista de regressão linear recém-construído[cite: 1].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_regressao_linear import (  # noqa: E501
    AlgoritmoRegressaoLinear,
)

# Configura o padrão de formatação das mensagens exibidas na tela.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' organiza os passos de verificação funcional do algoritmo
# de regressão.
def executar_teste_unitario() -> None:
    """Executa os testes estruturais e matemáticos do componente
    AlgoritmoRegressaoLinear[cite: 1].
    """
    # Emite aviso de inicialização do teste.
    logging.info("Iniciando bateria de testes do AlgoritmoRegressaoLinear (OLS)...")

    # 1. TESTE DE INSTANCIAÇÃO E POLIMORFISMO
    # Instancia a classe especialista da regressão linear.
    especialista = AlgoritmoRegressaoLinear()

    # Assegura que o especialista assinou o contrato universal da fábrica.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Cria a instância pura do algoritmo Scikit-Learn[cite: 1].
    estimador = especialista.construir_estimador()

    # Em problemas de regressão contínua, o modelo deve possuir 'fit' e 'predict',
    # mas não deve possuir 'predict_proba', pois estima grandezas contínuas e não
    # probabilidades[cite: 1, 3, 4].
    assert hasattr(estimador, "fit"), "Erro: O estimador não possui o método 'fit'!"
    assert hasattr(estimador, "predict"), (
        "Erro: O estimador não possui o método 'predict'!"
    )
    logging.info(
        "Teste 2 Concluído: Estimador LinearRegression instanciado com sucesso."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o dicionário de opções de busca em grade[cite: 1].
    grade = especialista.obter_grade_hiperparametros()

    # Valida a presença dos parâmetros essenciais de controle estrutural da reta[cite:
    # 1].
    assert "fit_intercept" in grade, (
        "Erro: Parâmetro 'fit_intercept' ausente na grade! [cite: 1]"
    )
    assert "positive" in grade, "Erro: Parâmetro 'positive' ausente na grade! [cite: 1]"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL COM DADOS CONTÍNUOS SINTÉTICOS
    # Criamos uma relação linear perfeita: y = 2.0 * x1 + 3.0 * x2 + 5.0 (sem
    # ruído)[cite: 1, 6, 7].
    x_teste = np.array([[1.0, 2.0], [2.0, 0.0], [0.0, 1.0], [3.0, 4.0], [5.0, 2.0]])
    # Vetor de respostas numéricas contínuas calculadas pela função geradora[cite: 3, 6,
    # 7].
    y_teste = np.array([13.0, 9.0, 8.0, 23.0, 21.0])

    # Executa o ajuste analítico dos mínimos quadrados ordinários[cite: 1, 6, 7].
    estimador.fit(x_teste, y_teste)

    # Realiza a predição para um novo vetor: x = [1.0, 1.0] -> y_esperado = 2(1) + 3(1)
    # + 5 = 10.0[cite: 1, 6, 7].
    previsao = estimador.predict([[1.0, 1.0]])

    # Verifica a convergência matemática com tolerância para arredondamentos de ponto
    # flutuante[cite: 1].
    assert np.isclose(previsao[0], 10.0, atol=1e-5), (
        f"Erro na inferência: Esperado 10.0, obtido {previsao[0]}"
    )
    logging.info(
        "Teste 4 Concluído: Ajuste analítico e inferência contínua validados com"
        "precisão."
    )

    # Emite mensagem final de aprovação do especialista.
    logging.info(
        "=== TODOS OS TESTES DA REGRESSÃO LINEAR FORAM CONCLUÍDOS COM SUCESSO! ==="
    )


# Ponto de entrada padrão para execução do script via terminal.
if __name__ == "__main__":
    executar_teste_unitario()
