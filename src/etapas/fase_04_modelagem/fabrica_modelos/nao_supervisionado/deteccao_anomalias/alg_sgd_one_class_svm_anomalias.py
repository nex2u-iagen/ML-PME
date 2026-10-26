"""Especialista em SGD One-Class SVM com Aproximação de Kernel RBF para Grande Escala.

Este módulo implementa o estimador SGDOneClassSVM acoplado ao transformador Nystroem
por meio de uma Pipeline do Scikit-Learn, permitindo delimitar fronteiras não-lineares
fechadas em tempo linear e streaming, conforme indicado na documentação oficial[cite: 8,
15].
"""

# 'from typing' provê suporte a tipagem estática rigorosa para a interface da fábrica.
from typing import Any

# 'from sklearn.kernel_approximation' importa o mapeamento eficiente de Kernel RBF[cite:
# 15].
from sklearn.kernel_approximation import Nystroem

# 'from sklearn.linear_model' importa o estimador linear estocástico de classe
# única[cite: 15].
from sklearn.linear_model import SGDOneClassSVM

# 'from sklearn.pipeline' importa a infraestrutura de encadeamento reproduzível[cite: 1,
# 8].
from sklearn.pipeline import Pipeline

# 'from src...' importa a interface contratual universal da fábrica[cite: 1].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista SGD One-Class SVM com aproximação de kernel.
class AlgoritmoSGDOneClassSVM(ModeloBase):
    """Modelo não-linear de classe única otimizado por gradiente estocástico com
    suporte RBF[cite: 15].
    """

    # 'def construir_estimador' monta a esteira Nystroem + SGDOneClassSVM.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia o Pipeline com Nystroem e SGDOneClassSVM[cite: 8, 15].

        Args:
            semente_aleatoria (int): Semente para controlar a amostragem de Nystroem e o
            SGD[cite: 15].

        Returns:
            Pipeline: Esteira composta capaz de traçar fronteiras não-lineares
            fechadas[cite: 8, 15].
        """
        # 'Nystroem' mapeia os dados em um subespaço de Fourier/Kernel RBF de dimensão
        # controlada[cite: 15].
        # 'SGDOneClassSVM' ajusta o hiperplano separador com custo O(n) sobre o espaço
        # projetado[cite: 15].
        return Pipeline(
            [
                (
                    "aproximador_kernel",
                    Nystroem(
                        kernel="rbf",
                        gamma=0.1,
                        n_components=50,
                        random_state=semente_aleatoria,
                    ),
                ),
                (
                    "sgd_svm",
                    SGDOneClassSVM(
                        nu=0.05, max_iter=1000, random_state=semente_aleatoria
                    ),
                ),
            ]
        )

    # 'def obter_grade_hiperparametros' expõe os parâmetros prefixados da Pipeline[cite:
    # 1, 8].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática para os componentes da Pipeline[cite: 8,
        15].

        Returns:
            Dict[str, list]: Dicionário com hiperparâmetros de kernel e taxa de
            aprendizado[cite: 15].
        """
        return {
            "aproximador_kernel__gamma": [0.01, 0.05, 0.1, 0.2],
            "sgd_svm__nu": [0.01, 0.05, 0.1],
            "sgd_svm__learning_rate": ["optimal", "adaptive"],
            "sgd_svm__eta0": [0.001, 0.01],
        }
