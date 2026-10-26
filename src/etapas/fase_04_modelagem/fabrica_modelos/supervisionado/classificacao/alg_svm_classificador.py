"""Especialista em Máquina de Vetores de Suporte (SVM) para Classificação.

Este módulo encapsula o estimador SVC do Scikit-Learn calibrado com probabilidades
via CalibratedClassifierCV, em conformidade com as diretrizes do Scikit-Learn 1.9+.
"""

# 'from typing' fornece anotações estáticas para validar a interface da fábrica.
from typing import Any

# 'from sklearn.calibration' importa o calibrador de probabilidades explícito[cite: 1].
from sklearn.calibration import CalibratedClassifierCV

# 'from sklearn.svm' importa o classificador clássico de suporte vetorial[cite: 1, 9].
from sklearn.svm import SVC

# 'from src...' importa a classe base abstrata para assegurar polimorfismo
# arquitetural[cite: 4].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista SVM moderno herdando de 'ModeloBase'.
class AlgoritmoSVM(ModeloBase):
    """Modelo discriminativo de margem máxima com calibração explícita de
    probabilidades[cite: 1, 9].
    """

    # 'def construir_estimador' monta a máquina de vetores de suporte calibrada.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia o SVC calibrado com CalibratedClassifierCV[cite: 1].

        Nota: Em conformidade com o Scikit-Learn 1.9+, o uso de 'probability=True' no
        SVC
        foi descontinuado. Empregamos 'CalibratedClassifierCV(estimator=SVC(),
        ensemble=False)'
        para fornecer o cálculo de probabilidades contínuas com alta estabilidade e sem
        avisos[cite: 1].

        Args:
            semente_aleatoria (int): Semente para controlar a reprodutibilidade dos
            pesos[cite: 1].

        Returns:
            CalibratedClassifierCV: Estimador calibrado pronto para predição
            probabilística pura[cite: 1].
        """
        # Estimador base do SVM configurado com pesos balanceados para classes
        # raras[cite: 1, 6].
        svm_base = SVC(class_weight="balanced", random_state=semente_aleatoria)

        # 'ensemble=False' calibra as probabilidades sobre uma única instância sem criar
        # submodelos extras[cite: 1].
        return CalibratedClassifierCV(estimator=svm_base, ensemble=False)

    # 'def obter_grade_hiperparametros' expõe os botões do estimador interno para o
    # GridSearchCV[cite: 1, 6].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática com notação prefixada para estimador
        calibrado[cite: 1, 6].

        Returns:
            Dict[str, list]: Dicionário com regularização C, tipos de kernel e fatores
            gamma[cite: 1, 9].
        """
        # Como o estimador está dentro de CalibratedClassifierCV, prefixamos com
        # 'estimator__'[cite: 1, 4].
        return {
            "estimator__C": [0.1, 1.0, 10.0],
            "estimator__kernel": ["linear", "rbf"],
            "estimator__gamma": ["scale"],
        }
