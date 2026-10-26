"""Script de Teste Unitário do Algoritmo DBSCAN (Agrupamento por Densidade).

Valida a herança de 'ModeloBase', a proteção de domínio contra métodos de classificação,
a identificação de ilhas de alta densidade e a detecção de ruídos espaciais rotulados
como -1.
"""

# 'import sys' permite manipular os diretórios de importação do interpretador Python em
# tempo de execução.
import sys

# 'from pathlib' viabiliza manipulação portável de caminhos no sistema de arquivos.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para habilitar as importações absolutas
# de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as notificações de auditoria técnica no console.
import logging

# 'import numpy as np' gera as matrizes espaciais sintéticas para simular regiões densas
# e pontos isolados.
import numpy as np

# Importa o contrato abstrato base para assegurar o polimorfismo universal da
# arquitetura.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista DBSCAN recém-construído na fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_dbscan_agrupamento import (  # noqa: E501
    AlgoritmoDBSCAN,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' organiza a verificação estrutural e funcional do
# algoritmo.
def executar_teste_unitario() -> None:
    """Executa os testes arquiteturais e matemáticos do componente AlgoritmoDBSCAN."""
    logging.info(
        "Iniciando bateria de testes do AlgoritmoDBSCAN (Agrupamento por Densidade)..."
    )

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Instancia a classe especialista do DBSCAN.
    especialista = AlgoritmoDBSCAN()

    # Assegura que o especialista assinou o contrato universal da fábrica.
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO
    # Constrói o estimador puro do Scikit-Learn.
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), "Erro: O estimador não possui o método 'fit'!"
    assert hasattr(estimador, "fit_predict"), (
        "Erro: O estimador não possui 'fit_predict'!"
    )
    # Assegura defensivamente que agrupadores NÃO exponham métodos de probabilidade
    # supervisionada.
    assert not hasattr(estimador, "predict_proba"), (
        "Erro Crítico: Agrupador expôs 'predict_proba'!"
    )
    logging.info(
        "Teste 2 Concluído: Estimador DBSCAN instanciado sem vazamento supervisionado."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém a lista de configurações disponíveis para busca sistemática.
    grade = especialista.obter_grade_hiperparametros()
    assert "eps" in grade, "Erro: Parâmetro 'eps' ausente na grade!"
    assert "min_samples" in grade, "Erro: Parâmetro 'min_samples' ausente na grade!"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE FUNCIONAL DE DENSIDADE E DETECÇÃO DE RUÍDO (-1)
    # Criamos um cenário com 7 amostras:
    # - 3 pontos extremamente próximos formando a Ilha A
    # - 3 pontos extremamente próximos formando a Ilha B
    # - 1 ponto solitário distante de todos (Ruído / Anomalia deliberada)
    x_teste = np.array(
        [
            [1.0, 1.0],
            [1.1, 1.0],
            [1.0, 1.1],  # Ilha densa A (Cluster 0)
            [10.0, 10.0],
            [10.1, 10.0],
            [10.0, 10.1],  # Ilha densa B (Cluster 1)
            [50.0, 50.0],  # Ponto isolado no deserto espacial (Ruído)
        ]
    )

    # Calibramos os parâmetros pontuais para identificar vizinhanças curtas (eps=0.3,
    # min_samples=3).
    estimador.set_params(eps=0.3, min_samples=3)

    # Executa o ajuste não supervisionado: repare que passamos APENAS 'X_teste', sem
    # rótulo 'y'.
    rotulos = estimador.fit_predict(x_teste)

    # A) O vetor de rótulos deve conter 7 elementos.
    assert len(rotulos) == 7, (
        "Erro: Dimensão dos rótulos divergente da matriz de entrada!"
    )

    # B) O ponto isolado ([50.0, 50.0]) deve receber obrigatoriamente o rótulo -1
    # (Ruído).
    assert rotulos[-1] == -1, (
        f"Erro: Esperado rótulo -1 para ponto isolado, obtido {rotulos[-1]}"
    )
    logging.info(
        "Detecção de Ruído confirmada com sucesso: Amostra anômala classificada como %d",  # noqa: E501
        rotulos[-1],
    )

    # C) Os outros pontos devem estar associados a clusters legítimos (maiores ou iguais
    # a 0).
    clusters_validos = set(rotulos[rotulos != -1])
    assert len(clusters_validos) == 2, (
        f"Erro: Esperado 2 clusters densos, obtido {len(clusters_validos)}"
    )
    logging.info("Clusters identificados nos dados: %s", clusters_validos)

    logging.info("=== TODOS OS TESTES DO DBSCAN FORAM CONCLUÍDOS COM SUCESSO! ===")


# Ponto de entrada padrão para execução do script via terminal.
if __name__ == "__main__":
    executar_teste_unitario()
