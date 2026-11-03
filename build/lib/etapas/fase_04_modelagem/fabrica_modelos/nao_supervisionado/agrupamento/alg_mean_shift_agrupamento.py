"""Especialista em Deslocamento da Média (Mean Shift).

Este módulo encapsula o estimador MeanShift da biblioteca Scikit-Learn.
Ele cumpre o contrato estrutural 'ModeloBase' e descobre centroides organicamente,
deslocando observações em direção aos picos de densidade da distribuição espacial.
"""

# 'from typing' fornece suporte formal a tipagem estática para validar a fábrica.
from typing import Any

# 'from sklearn.cluster' importa o algoritmo de agrupamento baseado em janelas de
# densidade.
from sklearn.cluster import MeanShift

# 'from src...' importa a interface contratual abstrata para garantir a integridade do
# design.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista Mean Shift herdando de 'ModeloBase'.
class AlgoritmoMeanShift(ModeloBase):
    """Modelo não supervisionado baseado em localização de modas por janela
    deslizante.
    """

    # 'def construir_estimador' instancia o algoritmo com semente e paralelismo
    # configurados.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador MeanShift em seu estado base.

        Nota: O Mean Shift é determinístico quando fornecido com um raio fixo.
        O argumento 'semente_aleatoria' é mantido para manter a interface uniforme.

        Args:
            semente_aleatoria (int): Preservado para assegurar o polimorfismo de
            ModeloBase.

        Returns:
            MeanShift: Estimador pronto para localização de modas espaciais.
        """
        # 'bandwidth=None' instrui o Scikit-Learn a estimar o raio ideal automaticamente
        # caso não fornecido.
        # 'bin_seeding=True' calcula uma grade discreta prévia para acelerar a
        # convergência em bases tabulares.
        # 'n_jobs=-1' utiliza todos os núcleos disponíveis para computar distâncias de
        # janela simultaneamente.
        return MeanShift(bandwidth=None, bin_seeding=True, n_jobs=-1)

    # 'def obter_grade_hiperparametros' expõe opções de largura de banda e métodos de
    # semeadura.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca para otimização da largura de banda (raio da janela).

        Returns:
            Dict[str, list]: Dicionário com larguras de banda e opções de aceleração
            matricial.
        """
        # 'bandwidth': O raio da janela circular/esférica que calcula a média local de
        # vizinhos.
        # Valores pequenos geram muitos clusters; valores grandes fundem picos
        # distintos.
        # 'bin_seeding': Avalia o impacto de inicialização por grade discreta na
        # velocidade de ajuste.
        return {"bandwidth": [0.5, 1.0, 1.5, 2.0, None], "bin_seeding": [True, False]}
