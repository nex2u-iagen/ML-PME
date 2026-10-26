"""Script de Teste Unitário do Algoritmo AdaBoostClassifier.

Valida o cumprimento do contrato estrutural 'ModeloBase', a correta instanciação
do estimador com tocos de decisão, a extração dos hiperparâmetros e a convergência de
treino.
"""

# 'import sys' permite manipular os caminhos de busca do interpretador Python em tempo
# de execução.
import sys

# 'from pathlib' disponibiliza manipulação portável de caminhos de arquivos e pastas.
from pathlib import Path

# Injeta a pasta raiz do projeto no 'sys.path' para viabilizar as importações absolutas
# do pacote 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia o envio de mensagens informativas e de auditoria para o
# terminal.
import logging

# 'import numpy as np' fornece manipulação de arrays multidimensionais para os dados de
# teste.
import numpy as np

# Importa o contrato abstrato base para assegurar o polimorfismo arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista AdaBoost recém-construído na fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_adaboost_classificador import (  # noqa: E501
    AlgoritmoAdaBoost,
)

# Padroniza a exibição de logs no console.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' orquestra os cenários de teste técnico do especialista.
def executar_teste_unitario() -> None:
    """Executa os testes unitários estruturais e funcionais no componente
    AlgoritmoAdaBoost.
    """
    # Registra o início do procedimento de testes.
    logging.info("Iniciando bateria de testes do AlgoritmoAdaBoost...")

    # 1. TESTE DE INSTANCIAÇÃO E HERANÇA POLIMÓRFICA
    # Instancia a classe especialista do AdaBoost.
    especialista = AlgoritmoAdaBoost()

    # Assegura que o especialista assinou o contrato da fábrica de modelos.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Constrói a instância crua do algoritmo Scikit-Learn.
    estimador = especialista.construir_estimador()

    # Valida a presença dos métodos indispensáveis para classificação supervisionada.
    assert hasattr(estimador, "fit"), (
        "Erro: O estimador retornado não possui o método 'fit'!"
    )
    assert hasattr(estimador, "predict_proba"), (
        "Erro: O estimador não fornece 'predict_proba'!"
    )
    logging.info("Teste 2 Concluído: Estimador AdaBoost instanciado com sucesso.")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém a lista de configurações disponíveis para busca em grade.
    grade = especialista.obter_grade_hiperparametros()

    # Confirma a presença das variáveis de controle essenciais.
    assert "n_estimators" in grade, "Erro: 'n_estimators' ausente na grade!"
    assert "learning_rate" in grade, "Erro: 'learning_rate' ausente na grade!"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL COM DADOS CONTROLADOS
    # Cria matriz de atributos sintética (6 amostras, 2 variáveis numéricas)[cite: 7].
    x_teste = np.array(
        [[1.0, 1.5], [1.2, 1.3], [0.8, 1.7], [6.0, 8.0], [5.8, 8.2], [6.2, 7.9]]
    )

    # Cria o vetor de classes balanceado (0 e 1)[cite: 7].
    y_teste = np.array([0, 0, 0, 1, 1, 1])

    # Executa o ajuste dos tocos de decisão iterativos sobre os dados sintéticos.
    estimador.fit(x_teste, y_teste)

    # Realiza a predição pontual sobre um vetor com perfil característico da classe 1.
    previsao = estimador.predict([[6.0, 8.0]])

    # Valida se a resposta coincide com a inferência lógica.
    assert previsao[0] == 1, f"Erro na inferência: Esperado 1, obtido {previsao[0]}"
    logging.info(
        "Teste 4 Concluído: Ajuste adaptativo e inferência validados com sucesso."
    )

    # Emite aviso final de integridade do componente.
    logging.info("=== TODOS OS TESTES DO ADABOOST FORAM CONCLUÍDOS COM SUCESSO! ===")


# Bloco de execução via linha de comando.
if __name__ == "__main__":
    executar_teste_unitario()
