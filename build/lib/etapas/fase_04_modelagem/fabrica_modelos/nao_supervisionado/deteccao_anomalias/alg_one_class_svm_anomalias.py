"""Especialista em Máquina de Vetores de Suporte de Uma Classe (One-Class SVM).

Este módulo encapsula o estimador OneClassSVM da biblioteca Scikit-Learn.
Ele cumpre o contrato 'ModeloBase' e aprende uma fronteira suave delimitando a região
de maior densidade dos dados com auxílio do Truque do Kernel RBF[cite: 2, 15].
"""

# 'from typing' provê suporte a tipagem estática rigorosa para assegurar a interface da
# fábrica.
from typing import Any

# 'from sklearn.svm' importa a implementação clássica de SVM para fronteiras de suporte
# de classe única[cite: 2, 15].
from sklearn.svm import OneClassSVM

# 'from src...' importa a classe base abstrata para assegurar polimorfismo arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista One-Class SVM herdando de 'ModeloBase'.
class AlgoritmoOneClassSVM(ModeloBase):
    """Modelo discriminativo de fronteira suave focado em delimitação de suporte de
    densidade[cite: 2, 15].
    """

    # 'def construir_estimador' instancia a máquina com Kernel RBF calibrado.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador OneClassSVM configurado[cite: 2, 15].

        Nota: O One-Class SVM resolve uma otimização convexa quadrática
        determinística[cite: 2, 15].
        O parâmetro 'gamma="auto"' (1 / n_caracteristicas) alarga suavemente a campânula
        radial, prevenindo o esvaziamento de densidade no centro da distribuição[cite:
        2, 15].

        Args:
            semente_aleatoria (int): Mantido para conformidade polimórfica com
            ModeloBase.

        Returns:
            OneClassSVM: Estimador pronto para aprender o contorno de suporte dos
            dados[cite: 2, 15].
        """
        # 'kernel="rbf"' molda contornos não-lineares flexíveis ao redor dos dados
        # saudáveis[cite: 2, 15].
        # 'nu=0.05' estabelece o teto estatístico de tolerância para amostras na margem
        # de suporte.
        # 'gamma="auto"' utiliza 1 / n_features para garantir sobreposição suave das
        # campânulas[cite: 2, 15].
        return OneClassSVM(kernel="rbf", nu=0.05, gamma="auto")

    # 'def obter_grade_hiperparametros' expõe frações nu e coeficientes gamma[cite: 2,
    # 15].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para o OneClassSVM[cite: 2, 15].

        Returns:
            Dict[str, list]: Dicionário com tolerâncias nu, funções de kernel e fatores
            gamma[cite: 2, 15].
        """
        # 'nu': Fração esperada de outliers e limite inferior de vetores de
        # suporte[cite: 2, 15].
        # 'kernel': Função de transformação espacial ('rbf' para curvas fechadas e
        # 'linear' para semiplanos)[cite: 2, 15].
        # 'gamma': O alcance da curvatura da fronteira de suporte ao redor de cada
        # ponto[cite: 2, 15].
        return {
            "nu": [0.01, 0.05, 0.1, 0.2],
            "kernel": ["rbf", "linear"],
            "gamma": ["auto", "scale", 0.05, 0.1],
        }
