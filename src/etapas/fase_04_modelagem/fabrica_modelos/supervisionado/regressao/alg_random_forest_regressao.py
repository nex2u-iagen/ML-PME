"""Especialista em Floresta Aleatória para Regressão Contínua (Random Forest Regressor).

Este módulo encapsula o estimador RandomForestRegressor da biblioteca Scikit-Learn.
Ele implementa o contrato 'ModeloBase' e opera combinando dezenas de árvores
de regressão em paralelo via Bagging, calculando a média das previsões contínuas.
"""

# 'from typing' provê suporte a tipagem estática para validar a interface da fábrica.
from typing import Any

# 'from sklearn.ensemble' importa o estimador de conjunto baseado em florestas
# paralelas.
from sklearn.ensemble import RandomForestRegressor

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista em Random Forest Regressor herdando de 'ModeloBase'.
class AlgoritmoRandomForestRegressor(ModeloBase):
    """Modelo Ensemble de agregação paralela (Bagging) para estimação de variáveis
    contínuas[cite: 7].
    """

    # 'def construir_estimador' instancia o modelo com controle de paralelismo e
    # reprodutibilidade.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador RandomForestRegressor em seu estado
        inicial[cite: 7].

        Args:
            semente_aleatoria (int): Semente para determinar o sorteio das amostras de
            bootstrap[cite: 7].

        Returns:
            RandomForestRegressor: Estimador pronto para calibração com dados numéricos
            contínuos[cite: 7].
        """
        # 'n_estimators=100' estabelece a quantidade base de árvores a serem
        # combinadas[cite: 7].
        # 'n_jobs=-1' orienta o algoritmo a utilizar todos os núcleos do processador
        # para acelerar o treino.
        # 'random_state=semente_aleatoria' garante convergência idêntica em execuções
        # repetidas[cite: 7].
        return RandomForestRegressor(
            n_estimators=100, n_jobs=-1, random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe os limitadores de variância para o
    # otimizador[cite: 7].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o
        RandomForestRegressor[cite: 7].

        Returns:
            Dict[str, list]: Dicionário com número de árvores, profundidade e divisão
            mínima[cite: 7].
        """
        # 'n_estimators': Volume de árvores independentes a serem combinadas na junta
        # pericial[cite: 7].
        # 'max_depth': Limite vertical de ramificações para prevenir decoreba de dados
        # (overfitting)[cite: 7].
        # 'min_samples_split': Menor quantidade de observações exigida para dividir um
        # nó interno[cite: 7].
        # 'min_samples_leaf': Menor quantidade de dados admitida em cada folha de
        # predição contínua[cite: 7].
        return {
            "n_estimators": [100, 200, 300],
            "max_depth": [5, 10, 15, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        }
