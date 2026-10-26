"""Script de Teste Unitário do Algoritmo Naive Bayes Gaussiano.

Verifica a herança da classe abstrata 'ModeloBase', a construção correta do estimador,
a extração da grade de hiperparâmetros e a convergência de ajuste com dados simulados.
"""

# 'import sys' permite a manipulação direta dos caminhos de busca de módulos no sistema.
import sys

# 'from pathlib' importa a ferramenta moderna e portável de manipulação de diretórios do
# sistema.
from pathlib import Path

# Adiciona a raiz do projeto ao 'sys.path' para que o interpretador reconheça o pacote
# 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import numpy as np' importa a biblioteca padrão para cálculos numéricos e criação de
# arrays.
# 'import logging' configura a emissão de mensagens padronizadas no ecrã do terminal.
import logging

import numpy as np

# Importa a interface contratual para validar se o especialista assinou o contrato
# corretamente.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa a classe do especialista desenvolvida para o teste.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_naive_bayes_classificador import (  # noqa: E501
    AlgoritmoNaiveBayes,
)

# Configura o formato da saída de auditoria do teste no ecrã.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' organiza as etapas de verificação e validação do
# especialista.
def executar_teste_unitario() -> None:
    """Executa a verificação funcional do componente AlgoritmoNaiveBayes."""
    # Emite aviso inicial no terminal.
    logging.info("Iniciando bateria de testes do AlgoritmoNaiveBayes...")

    # 1. TESTE DE INSTANCIAÇÃO
    # Instancia a classe do especialista.
    especialista = AlgoritmoNaiveBayes()

    # Valida se a classe é uma subclasse legítima de ModeloBase (Polimorfismo).
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não herda de ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Chama o método que gera o algoritmo puro do Scikit-Learn.
    estimador = especialista.construir_estimador()

    # Confirma se o objeto gerado contém os métodos fundamentais de aprendizado ('fit' e
    # 'predict').
    assert hasattr(estimador, "fit"), (
        "Erro: O estimador retornado não possui o método fit!"
    )
    assert hasattr(estimador, "predict_proba"), (
        "Erro: O estimador não calcula probabilidades!"
    )
    logging.info("Teste 2 Concluído: Estimador Scikit-Learn instanciado com sucesso.")

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Recolhe o dicionário de parâmetros para o otimizador.
    grade = especialista.obter_grade_hiperparametros()

    # Verifica se a chave 'var_smoothing' existe e contém uma lista de valores válidos.
    assert "var_smoothing" in grade, (
        "Erro: A chave 'var_smoothing' está ausente na grade!"
    )
    assert isinstance(grade["var_smoothing"], list), (
        "Erro: Os parâmetros devem ser uma lista!"
    )
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL COM DADOS CONTROLADOS
    # Cria uma matriz pequena de sintomas (X) com 6 observações e 2 características
    # numéricas.
    x_teste = np.array(
        [[1.0, 2.0], [1.1, 2.1], [0.9, 1.9], [5.0, 8.0], [5.2, 8.1], [4.9, 7.9]]
    )

    # Cria o vetor de classes correspondente (y) contendo duas classes (0 e 1).
    y_teste = np.array([0, 0, 0, 1, 1, 1])

    # Executa o treino analítico direto nos dados sintéticos.
    estimador.fit(x_teste, y_teste)

    # Gera a previsão para uma nova amostra claramente pertencente à classe 0.
    previsao = estimador.predict([[1.0, 2.0]])

    # Assegura que o diagnóstico foi correto.
    assert previsao[0] == 0, f"Erro na inferência: Esperado 0, obtido {previsao[0]}"
    logging.info("Teste 4 Concluído: Treino analítico e inferência validados.")

    # Mensagem final de conformidade técnica.
    logging.info("=== TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! ===")


# Bloco de segurança para execução via linha de comandos.
if __name__ == "__main__":
    executar_teste_unitario()
