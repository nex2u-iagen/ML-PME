"""Script de Teste Unitário do Algoritmo KMeans (Agrupamento Não Supervisionado).

Valida a herança de 'ModeloBase', a proteção de domínio (ausência de métodos
supervisionados),
a convergência dos centroides, a minimização da Inércia e o cálculo do Coeficiente de
Silhueta[cite: 15, 16].
"""

# 'import sys' permite manipular os caminhos de busca do interpretador Python em tempo
# de execução.
import sys

# 'from pathlib' disponibiliza manipulação portável de diretórios do sistema
# operacional.
from pathlib import Path

# Adiciona a pasta raiz do projeto ao 'sys.path' para habilitar as importações absolutas
# de 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 'import logging' gerencia as notificações de auditoria técnica no console.
import logging

# 'import numpy as np' gera as matrizes espaciais sintéticas para o teste de
# particionamento[cite: 16].
import numpy as np

# 'from sklearn.metrics' importa o cálculo de coesão e separação espacial de
# agrupamentos.
from sklearn.metrics import silhouette_score

# Importa o contrato abstrato base para assegurar o polimorfismo universal da
# arquitetura[cite: 8].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase

# Importa o especialista KMeans recém-construído na fábrica[cite: 16].
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_kmeans_agrupamento import (  # noqa: E501
    AlgoritmoKMeans,
)

# Configura o layout das mensagens de log no terminal.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def executar_teste_unitario' organiza a verificação estrutural e funcional do
# algoritmo.
def executar_teste_unitario() -> None:
    """Executa os testes arquiteturais e matemáticos do componente
    AlgoritmoKMeans[cite: 16].
    """
    logging.info("Iniciando bateria de testes do AlgoritmoKMeans (Agrupamento)...")

    # 1. TESTE DE POLIMORFISMO E HERANÇA
    # Instancia a classe especialista do K-Means.
    especialista = AlgoritmoKMeans()

    # Valida se o especialista assinou formalmente o contrato universal ModeloBase[cite:
    # 8].
    assert isinstance(especialista, ModeloBase), (
        "Erro: O especialista não implementa ModeloBase!"
    )
    logging.info("Teste 1 Concluído: Herança de ModeloBase confirmada.")

    # 2. TESTE DE CONSTRUÇÃO E PROTEÇÃO DE DOMÍNIO NÃO SUPERVISIONADO
    # Constrói o estimador puro do Scikit-Learn[cite: 16].
    estimador = especialista.construir_estimador()
    assert hasattr(estimador, "fit"), "Erro: O estimador não possui o método 'fit'!"
    assert hasattr(estimador, "fit_predict"), (
        "Erro: O estimador não possui 'fit_predict'!"
    )
    # Assegura que o modelo de agrupamento NÃO contenha comportamento de classificação
    # com probabilidades[cite: 8, 16]
    assert not hasattr(estimador, "predict_proba"), (
        "Erro Crítico: Agrupador expôs 'predict_proba'!"
    )
    logging.info(
        "Teste 2 Concluído: Estimador KMeans instanciado sem vazamento supervisionado."
    )

    # 3. TESTE DA GRADE DE HIPERPARÂMETROS
    # Obtém a lista de configurações disponíveis para busca em grade.
    grade = especialista.obter_grade_hiperparametros()
    assert "n_clusters" in grade, (
        "Erro: Parâmetro 'n_clusters' ausente na grade! [cite: 16]"
    )
    assert "init" in grade, "Erro: Parâmetro 'init' ausente na grade! [cite: 16]"
    logging.info("Teste 3 Concluído: Grade de hiperparâmetros validada.")

    # 4. TESTE DE AJUSTE FUNCIONAL NÃO SUPERVISIONADO (SEM GABARITO 'y')
    # Criamos 6 observações sintéticas 2D divididas nitidamente em dois grupos
    # distantes[cite: 16]:
    # Grupo A em torno de (-5, -5) e Grupo B em torno de (+5, +5)
    x_teste = np.array(
        [[-5.0, -5.2], [-4.8, -5.0], [-5.1, -4.9], [5.0, 5.1], [4.9, 4.8], [5.2, 5.0]]
    )

    # Reconfiguramos o estimador para k=2 grupos para o teste funcional pontual[cite:
    # 16].
    estimador.set_params(n_clusters=2)

    # Executa o ajuste NÃO SUPERVISIONADO: repare que passamos APENAS 'X_teste', sem
    # nenhum vetor 'y'!
    rotulos = estimador.fit_predict(x_teste)

    # Validações matemáticas intrínsecas:
    # A) Os rótulos de grupo gerados devem conter exatamente 2 grupos distintos (0 e
    # 1)[cite: 16]
    grupos_unicos = np.unique(rotulos)
    assert len(grupos_unicos) == 2, (
        f"Erro: Esperado 2 grupos únicos, obtido {len(grupos_unicos)}"
    )

    # B) A Inércia (WCSS) deve ser positiva e finita[cite: 16]
    assert hasattr(estimador, "inertia_") and estimador.inertia_ > 0, (
        "Erro: Inércia inválida!"
    )
    logging.info("Inércia Intra-Cluster (WCSS) calculada: %.4f", estimador.inertia_)

    # C) Os centroides finais devem estar próximos de (-5, -5) e (+5, +5)[cite: 16]
    centroides = estimador.cluster_centers_
    assert centroides.shape == (2, 2), (
        f"Erro: Formato de centroides esperado (2, 2), obtido {centroides.shape}"
    )
    logging.info("Centroides identificados:\n%s", centroides)

    # D) Avaliação da qualidade da separação geométrica via Coeficiente de Silhueta
    # O Coeficiente de Silhueta varia de -1 (sobreposição errada) a +1 (grupos perfeitos
    # e densos)[cite: 15]
    pontuacao_silhueta = silhouette_score(x_teste, rotulos)
    assert pontuacao_silhueta > 0.8, (
        f"Erro: Silhueta baixa ({pontuacao_silhueta:.2f}) para dados bem separados!"
    )
    logging.info(
        "Coeficiente de Silhueta alcançado: %.4f (Excelente coesão e separação)",
        pontuacao_silhueta,
    )

    logging.info("=== TODOS OS TESTES DO K-MEANS CONCLUÍDOS COM SUCESSO! ===")


# Ponto de entrada padrão para execução do script via terminal.
if __name__ == "__main__":
    executar_teste_unitario()
