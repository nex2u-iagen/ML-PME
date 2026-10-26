"""Especialista em Regressão Linear por Mínimos Quadrados Ordinários (OLS).

Este módulo encapsula o estimador LinearRegression da biblioteca Scikit-Learn.
Ele cumpre o contrato estrutural 'ModeloBase' e ajusta hiperplanos em problemas onde
o valor numérico contínuo é estimado por combinação linear dos atributos[cite: 1, 6, 7].
"""

# 'from typing' fornece anotações estáticas para assegurar conformidade com a interface
# base.
from typing import Any

# 'from sklearn.linear_model' importa a implementação clássica de mínimos quadrados
# ordinários.
from sklearn.linear_model import LinearRegression

# 'from src...' importa o contrato universal da fábrica para assegurar polimorfismo
# arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista em regressão linear herdando de 'ModeloBase'.
class AlgoritmoRegressaoLinear(ModeloBase):
    """Modelo linear clássico para estimação de variáveis numéricas contínuas
    (OLS)[cite: 1, 6].
    """

    # 'def construir_estimador' instancia a máquina matemática de regressão.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador LinearRegression em seu estado fundamental.

        Nota: A regressão linear OLS calcula os coeficientes analiticamente resolvendo
        as equações normais via Decomposição em Valores Singulares (SVD)[cite: 1, 7].
        Dessa forma, ela é determinística e dispensa sementes aleatórias[cite: 1].

        Args:
            semente_aleatoria (int): Mantido na assinatura para manter o polimorfismo do
            ModeloBase.

        Returns:
            LinearRegression: Estimador pronto para ajuste e cálculo dos coeficientes
            beta[cite: 1, 7].
        """
        # Retorna o estimador clássico de mínimos quadrados ordinários[cite: 1].
        # 'fit_intercept=True' instrui o cálculo do termo constante beta0
        # (intercepto)[cite: 1, 6, 7].
        # 'copy_X=True' preserva a matriz de atributos original em memória sem
        # sobrescrevê-la.
        # 'n_jobs=-1' acelera os cálculos matriciais utilizando todos os núcleos do
        # processador.
        return LinearRegression(fit_intercept=True, copy_X=True, n_jobs=-1)

    # 'def obter_grade_hiperparametros' expõe os pontos de variação para busca em
    # grade[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para o otimizador[cite: 1].

        Returns:
            Dict[str, list]: Dicionário com parâmetros estruturais de ajuste da
            reta/hiperplano[cite: 1, 6].
        """
        # 'fit_intercept': Avalia se a reta deve ser forçada a passar pela origem (0, 0)
        # ou se deve calcular o intercepto livremente (recomendado na maioria dos
        # casos)[cite: 1, 7].
        # 'positive': Força todos os coeficientes a serem estritamente não-negativos
        # quando True[cite: 1].
        return {"fit_intercept": [True, False], "positive": [False, True]}
