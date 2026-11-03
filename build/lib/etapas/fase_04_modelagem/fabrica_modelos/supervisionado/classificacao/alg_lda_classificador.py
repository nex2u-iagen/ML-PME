"""Especialista em Análise Discriminante Linear (LDA) para Classificação.

Este módulo encapsula o algoritmo LinearDiscriminantAnalysis do Scikit-Learn.
Ele atua de forma supervisionada, projetando os dados em eixos que maximizam
a separação entre as classes e minimizam a variância interna de cada grupo.
"""

# 'from typing' garante que o contrato de tipagem da Fábrica seja respeitado.
from typing import Any

# 'from sklearn.discriminant_analysis' importa o algoritmo gerativo clássico.
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

# 'from src...' importa a base arquitetural para garantir o Baixo Acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o nosso Especialista em Estatística Bayesiana.
class AlgoritmoLDA(ModeloBase):
    """Modelo gerativo focado em separação de médias e variância interna[cite: 2, 3]."""

    # 'def construir_estimador' entrega o modelo sem ajustes paramétricos pesados.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia o estado inicial do classificador LDA.

        Nota: O LDA utiliza álgebra linear determinística (cálculo de médias
        e matrizes de covariância) para encontrar a solução exata. Portanto,
        ele não depende de um gerador de números aleatórios ('random_state').

        Args:
            semente_aleatoria (int): Mantido para respeitar a assinatura do
                                     contrato Polimórfico (ModeloBase).

        Returns:
            LinearDiscriminantAnalysis: O modelo bruto instanciado.
        """
        # Retorna o modelo clássico pronto para projetar os dados.
        return LinearDiscriminantAnalysis()

    # 'def obter_grade_hiperparametros' expõe a calibração do motor matemático.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o Otimizador.

        Returns:
            Dict[str, list]: Dicionário com os motores de solução ('solver').
        """
        # 'solver': O método matemático usado para resolver o sistema.
        #   - 'svd': Decomposição em Valores Singulares (Padrão). Recomendado
        #            para dados com muitas features, mas não aceita 'shrinkage'.
        #   - 'lsqr': Solução de mínimos quadrados. Eficiente e permite 'shrinkage'
        #             (encolhimento regularizado) quando há multicolinearidade.
        #   - 'eigen': Decomposição em autovalores.
        return {"solver": ["svd", "lsqr"]}
