"""Especialista em Regressão Logística para Classificação Binária.

Este módulo encapsula o algoritmo linear probabilístico do Scikit-Learn.
Ele assina o contrato 'ModeloBase' e define as grades de hiperparâmetros
recomendadas para calibração fina e prevenção de sobreajuste[cite: 1].
"""

# 'from' acessa o módulo 'typing' da biblioteca padrão.
# 'Any' e 'Dict' garantem que a nossa classe obedece à mesma assinatura de tipos exigida
# na interface ModeloBase.
from typing import Any

# 'from' acessa os modelos lineares do scikit-learn.
# 'LogisticRegression' é o estimador de classificação que utiliza a função logística em
# formato de "S"[cite: 1].
from sklearn.linear_model import LogisticRegression

# 'from' importa a classe abstrata (contrato) que criamos anteriormente.
# Isso garante o Baixo Acoplamento: o orquestrador não interage com a Regressão
# Logística, interage com o ModeloBase.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o nosso algoritmo especialista.
# '(ModeloBase)' indica que esta classe herda obrigatoriamente as regras do contrato
# abstrato.
class AlgoritmoRegressaoLogistica(ModeloBase):
    """Modelo linear base para problemas de classificação binária com foco em
    explicabilidade[cite: 1].
    """

    # 'def' implementa o primeiro método obrigatório do contrato.
    # 'semente_aleatoria' garante que as inicializações matemáticas convirjam sempre
    # para o mesmo resultado.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e configura o estado inicial do estimador de Regressão Logística.

        Args:
            semente_aleatoria (int, opcional): Semente para controle de aleatoriedade
            estatística. Padrão: 42.

        Returns:
            LogisticRegression: Modelo linear com pesos balanceados pronto para a Sala
            de Calibração.
        """
        # Retorna a instância do modelo estatístico configurado.
        # 'class_weight="balanced"' força a matemática a dar pesos maiores aos raros
        # casos da classe minoritária[cite: 1].
        # 'solver="saga"' é o otimizador recomendado para suportar simultaneamente
        # penalidades L1, L2 e Elastic-Net em grandes bases[cite: 1].
        # 'max_iter=1500' expande o limite de épocas para garantir a convergência
        # matemática sem erros de interrupção[cite: 1].
        # 'random_state=semente_aleatoria' fixa a reprodutibilidade.
        return LogisticRegression(
            class_weight="balanced",
            solver="saga",
            max_iter=1500,
            random_state=semente_aleatoria,
        )

    # 'def' implementa o segundo método obrigatório do contrato.
    # Não recebe argumentos externos além do próprio objeto (self), retornando as chaves
    # de calibração.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o otimizador cruzar com
        os dados.

        Returns:
            Dict[str, list]: Dicionário mapeando os hiperparâmetros oficiais do
            scikit-learn
                             aos valores numéricos que o otimizador testará.
        """
        # Retorna o dicionário de opções paramétricas.
        # 'penalty': testa a ausência de penalidade ('none'), o encolhimento de
        # coeficientes ('l2' / Ridge)
        # e a seleção rigorosa de variáveis zerando as irrelevantes ('l1' / Lasso)[cite:
        # 1].
        # 'C': é o inverso da força de regularização. Valores menores (ex: 0.01) aplicam
        # punições mais fortes,
        # forçando o modelo a ser mais simples e combater o overfitting[cite: 1].
        return {"penalty": ["l1", "l2"], "C": [0.01, 0.1, 1.0, 10.0]}
