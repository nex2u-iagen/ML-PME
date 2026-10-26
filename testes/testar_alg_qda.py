"""Script de Teste Unitário do Algoritmo Análise Discriminante Quadrática (QDA).

Verifica a herança da classe abstrata 'ModeloBase', a construção correta do estimador,
a extração da grade de hiperparâmetros e a convergência de ajuste em dados sintéticos
não-lineares.
"""

# 'import sys' permite a manipulação de variáveis e rotas de carregamento do
# interpretador Python.
import sys

# 'from pathlib' importa o recurso padrão e multiplataforma de gestão de diretórios.
from pathlib import Path

# Adiciona a raiz do projeto ao 'sys.path' para permitir importações absolutas a partir
# de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import numpy as np' importa a biblioteca padrão para manipulação de matrizes e arrays
# numéricos.
# 'import logging' configura a emissão padronizada de mensagens de auditoria no
# terminal.
import logging

import numpy as np

# Importa o contrato abstrato base para validar o cumprimento da arquitetura.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o componente especialista desenvolvido para o teste unitário.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_qda_classificador import (  # noqa: E501
    AlgoritmoQDA,
)

# Configura o layout visual das saídas de log no ecrã.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' organiza os testes de validação técnica do especialista.
def executar_teste_unitario() -> None:
    """Executa a verificação funcional do componente AlgoritmoQDA."""
    # Emite aviso inicial no terminal.
    logging.info("Iniciando bateria de testes do AlgoritmoQDA...")

    # 1. TESTE DE INSTANCIAÇÃO E POLIMORFISMO
    # Instancia a classe do especialista QDA.
    especialista = AlgoritmoQDA()

    # Assegura que a classe respeita o contrato base da fábrica de modelos.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não herda de ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Cria o estimador analítico através do método contratual.
    estimador = especialista.construir_estimador()

    # Verifica a existência dos métodos essenciais de ajuste e predição de
    # probabilidades.
    assert hasattr(estimador, "fit"), (
        "Erro: O estimador retornado não possui o método fit!"
    )
    assert hasattr(estimador, "predict_proba"), (
        "Erro: O estimador não calcula probabilidades!"
    )
    logging.info(
        "Teste 2 Concluído: Estimador QDA do Scikit-Learn instanciado com sucesso."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém o catálogo de opções de hiperparâmetros configurado.
    grade = especialista.obter_grade_hiperparametros()

    # Valida a presença do parâmetro chave 'reg_param'.
    assert "reg_param" in grade, "Erro: A chave 'reg_param' está ausente na grade!"
    assert isinstance(grade["reg_param"], list), (
        "Erro: 'reg_param' deve ser fornecido em formato de lista!"
    )
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL COM DADOS CONTROLADOS
    # Constrói uma matriz sintética com 8 registos e 2 variáveis explicativas numéricas.
    # O QDA exige amostras suficientes em cada classe para estimar matrizes de
    # covariância independentes.
    x_teste = np.array(
        [
            [1.0, 1.0],
            [1.2, 0.9],
            [0.8, 1.1],
            [1.1, 1.3],
            [5.0, 5.0],
            [5.2, 4.8],
            [4.9, 5.1],
            [5.1, 5.3],
        ]
    )

    # Define o vetor de alvos binários com 4 amostras por grupo (balanceado).
    y_teste = np.array([0, 0, 0, 0, 1, 1, 1, 1])

    # Executa o ajuste das matrizes de covariância independentes.
    estimador.fit(x_teste, y_teste)

    # Gera uma previsão para uma nova observação posicionada no grupo 1.
    previsao = estimador.predict([[5.0, 5.0]])

    # Valida se o diagnóstico inferido corresponde ao valor esperado.
    assert previsao[0] == 1, f"Erro na inferência: Esperado 1, obtido {previsao[0]}"
    logging.info(
        "Teste 4 Concluído: Ajuste das covariâncias e inferência validados com sucesso."
    )

    # Mensagem conclusiva de sucesso operacional.
    logging.info("=== TODOS OS TESTES DO QDA FORAM CONCLUÍDOS COM SUCESSO! ===")


# Bloco de execução via terminal.
if __name__ == "__main__":
    executar_teste_unitario()
