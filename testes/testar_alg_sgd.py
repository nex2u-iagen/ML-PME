"""Script de Teste Unitário do Algoritmo SGDClassifier.

Verifica a conformidade com a interface abstrata 'ModeloBase', a habilitação correta
do cálculo de probabilidades, a integridade da grade e a convergência com dados
sintéticos[cite: 1, 9].
"""

# 'import sys' permite a manipulação dos diretórios de busca de módulos do Python.
import sys

# 'from pathlib' viabiliza a manipulação segura e portável de caminhos de arquivos.
from pathlib import Path

# Adiciona a raiz do projeto ao 'sys.path' para reconhecer as importações do pacote
# 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' padroniza os registros de eventos no terminal de auditoria.
import logging

# 'import numpy as np' gera matrizes numéricas para simulação controlada dos dados[cite:
# 9].
import numpy as np

# Importa a classe abstrata base para validar o cumprimento do contrato da fábrica[cite:
# 7].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista SGD recém-construído[cite: 1].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_sgd_classificador import (  # noqa: E501
    AlgoritmoSGD,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' orquestra os cenários de verificação do especialista.
def executar_teste_unitario() -> None:
    """Executa a verificação funcional completa do componente AlgoritmoSGD[cite: 1]."""
    # Registra o início do procedimento de testes.
    logging.info("Iniciando bateria de testes do AlgoritmoSGD...")

    # 1. TESTE DE INSTANCIAÇÃO E HERANÇA POLIMÓRFICA
    # Instancia a classe especialista do SGD.
    especialista = AlgoritmoSGD()

    # Assegura que o especialista assinou o contrato universal da fábrica.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO DO ESTIMADOR
    # Cria a instância padrão do algoritmo Scikit-Learn[cite: 1].
    estimador = especialista.construir_estimador()

    # Valida a presença dos métodos essenciais para a esteira de classificação
    # supervisionada[cite: 1, 9].
    assert hasattr(estimador, "fit"), (
        "Erro: O estimador não possui o método 'fit'! [cite: 7]"
    )
    assert hasattr(estimador, "predict_proba"), (
        "Erro: O estimador não fornece 'predict_proba'! [cite: 1]"
    )
    logging.info(
        "Teste 2 Concluído: Estimador SGDClassifier instanciado com suporte a"
        "probabilidade."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Carrega a grade de parâmetros de busca em grade[cite: 1, 9].
    grade = especialista.obter_grade_hiperparametros()

    # Valida os hiperparâmetros essenciais de controle do gradiente[cite: 1].
    assert "penalty" in grade, "Erro: 'penalty' ausente na grade! [cite: 1]"
    assert "alpha" in grade, "Erro: 'alpha' ausente na grade! [cite: 1]"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE CONVERGÊNCIA COM DADOS MATRICIAIS CONTÍNUOS
    # Dados para SGD requerem escala numérica compatível para convergência rápida do
    # gradiente[cite: 1].
    x_teste = np.array(
        [[-1.0, -1.2], [-0.9, -1.0], [-1.1, -1.1], [1.0, 1.2], [0.9, 1.0], [1.1, 1.1]]
    )

    # Vetor de rótulos binários balanceado (3 amostras classe 0 e 3 classe 1)[cite: 4,
    # 9].
    y_teste = np.array([0, 0, 0, 1, 1, 1])

    # Executa o ajuste estocástico iterativo sobre os dados sintéticos[cite: 1, 7].
    estimador.fit(x_teste, y_teste)

    # Realiza a predição pontual sobre um vetor com perfil característico da classe
    # 1[cite: 1].
    previsao = estimador.predict([[1.0, 1.1]])

    # Assegura que o diagnóstico inferido confere com a lógica aprendida[cite: 4, 9].
    assert previsao[0] == 1, (
        f"Erro na inferência estocástica: Esperado 1, obtido {previsao[0]}"
    )
    logging.info(
        "Teste 4 Concluído: Ajuste estocástico e inferência validados com sucesso."
    )

    # Emite aviso final de integridade do componente.
    logging.info("=== TODOS OS TESTES DO SGD FORAM CONCLUÍDOS COM SUCESSO! ===")


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    executar_teste_unitario()
