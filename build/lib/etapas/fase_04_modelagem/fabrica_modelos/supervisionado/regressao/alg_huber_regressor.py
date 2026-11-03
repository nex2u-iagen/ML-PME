"""Especialista em Regressão Robusta de Huber para Variáveis Contínuas.

Este módulo encapsula o estimador HuberRegressor da biblioteca Scikit-Learn[cite: 2].
Ele implementa o contrato 'ModeloBase' e fornece uma estimativa linear resiliente
a valores atípicos (outliers), alternando entre perda quadrática e linear[cite: 2].
"""

# 'from typing' importa os tipos estáticos formais para validar a interface.
from typing import Any

# 'from sklearn.linear_model' importa a implementação da regressão robusta de
# Huber[cite: 2].
from sklearn.linear_model import HuberRegressor

# 'from src...' importa a classe base abstrata para assegurar o baixo acoplamento da
# fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista Huber herdando formalmente de 'ModeloBase'.
class AlgoritmoHuber(ModeloBase):
    """Modelo linear robusto contra outliers via controle por limiar de erro
    residual[cite: 2].
    """

    # 'def construir_estimador' instancia o estimador linear robusto.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador HuberRegressor em seu estado base.

        Nota: O HuberRegressor utiliza otimização baseada em gradiente (L-BFGS-B)[cite:
        2].
        Embora determinístico na maioria dos casos, mantemos o padrão da interface.

        Args:
            semente_aleatoria (int): Mantido para interoperabilidade polimórfica da
            fábrica.

        Returns:
            HuberRegressor: Estimador configurado com margem de iterações
            suficiente[cite: 2].
        """
        # 'fit_intercept=True' assegura a estimação do termo constante (intercepto).
        # 'max_iter=1000' expande o teto de iterações para assegurar convergência
        # numérica.
        # 'alpha=0.0001' aplica regularização L2 padrão para estabilização dos
        # pesos[cite: 2].
        return HuberRegressor(fit_intercept=True, max_iter=1000, alpha=0.0001)

    # 'def obter_grade_hiperparametros' expõe a grade de ajuste para o otimizador[cite:
    # 2].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o HuberRegressor[cite:
        2].

        Returns:
            Dict[str, list]: Dicionário com limiar de tolerância a outliers e penalidade
            L2[cite: 2].
        """
        # 'epsilon': Controla o limiar de transição entre erro quadrático e erro
        # linear[cite: 2].
        # Valores menores tornam o modelo mais cético em relação a resíduos grandes.
        # 'alpha': Intensidade da penalização de regularização L2 sobre os
        # coeficientes[cite: 2].
        return {
            "epsilon": [1.1, 1.25, 1.35, 1.5, 1.75],
            "alpha": [1e-4, 1e-3, 1e-2, 1e-1],
        }
