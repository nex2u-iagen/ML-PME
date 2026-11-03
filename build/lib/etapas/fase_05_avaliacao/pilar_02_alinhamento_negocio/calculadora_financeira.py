"""Módulo Especialista em Cálculo de Impacto Financeiro de Modelos (Pilar 2).

Responsabilidade Única: Extrair os quatro quadrantes da matriz de confusão (VN, FP, FN,
VP)
de um estimador específico e aplicar a aritmética da matriz de custos para apurar
a perda por negligência, o custo de alarmes e o resultado financeiro líquido em
reais[cite: 20].
"""

# 'from typing import ...' provê suporte a tipagem estática rigorosa.
from typing import Any

# 'import numpy as np' fornece suporte à manipulação de matrizes de entrada[cite: 17].
import numpy as np

# 'from sklearn.metrics import confusion_matrix' extrai as contagens de acerto e erro do
# classificador[cite: 20].
from sklearn.metrics import confusion_matrix

# Importa a classe de configuração que encapsula as premissas econômicas do negócio.
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.configuracao_custos import (  # noqa: E501
    ConfiguracaoCustoRisco,
)


# 'class CalculadoraImpactoFinanceiro' isola estritamente as regras de conversão
# contábil[cite: 20].
class CalculadoraImpactoFinanceiro:
    """Motor matemático que traduz matrizes de confusão em balancete contábil
    líquido[cite: 20].
    """

    # 'def __init__(...)' injeta a dependência do contrato de custos na inicialização do
    # serviço[cite: 20].
    def __init__(self, configuracao_custos: ConfiguracaoCustoRisco) -> None:
        """Inicializa a calculadora associando as premissas econômicas ativas[cite: 20].

        Args:
            configuracao_custos (ConfiguracaoCustoRisco): Instância com os valores
            monetários de cada decisão[cite: 20].
        """
        # Armazena a referência das premissas econômicas na propriedade interna da
        # classe[cite: 20].
        self.config = configuracao_custos

    # 'def apurar_balancete_modelo(...)' extrai as decisões e computa o saldo
    # líquido[cite: 20].
    def apurar_balancete_modelo(
        self,
        nome_modelo: str,
        estimador: Any,
        matriz_atributos_teste: np.ndarray,
        vetor_alvo_teste: np.ndarray,
    ) -> dict[str, Any]:
        """Calcula o prejuízo por negligência, custos operacionais e resultado líquido
        de um modelo[cite: 20].

        Args:
            nome_modelo (str): Identificador do algoritmo (ex: 'SVM_Calibrado',
            'XGBoost')[cite: 20, 26].
            estimador (Any): Modelo treinado com o método predict() disponível[cite:
            20].
            matriz_atributos_teste (np.ndarray): Matriz X de teste cego retido[cite:
            20].
            vetor_alvo_teste (np.ndarray): Vetor y real do conjunto de teste[cite: 20].

        Returns:
            Dict[str, Any]: Balancete financeiro auditável consolidado em reais[cite:
            20].
        """
        # Gera as predições de classe discretas sobre o lote de teste retido[cite: 18,
        # 20].
        predicoes = estimador.predict(matriz_atributos_teste)

        # Extrai a matriz de confusão binária oficial do Scikit-Learn[cite: 20].
        matriz_conf = confusion_matrix(vetor_alvo_teste, predicoes)

        # Desempacota os quatro quadrantes absolutos de decisão do modelo[cite: 20].
        verdadeiro_negativo = int(matriz_conf[0, 0])
        falso_positivo = int(matriz_conf[0, 1])
        falso_negativo = int(matriz_conf[1, 0])
        verdadeiro_positivo = int(matriz_conf[1, 1])

        # Calcula o prejuízo financeiro causado pela negligência das omissões (FN *
        # Custo)[cite: 20].
        prejuizo_negligencia = falso_negativo * self.config.custo_fn

        # Calcula o custo operacional provocado pelos alarmes falsos emitidos (FP *
        # Custo)[cite: 20].
        custo_alarmes_falsos = falso_positivo * self.config.custo_fp

        # Calcula o valor econômico retido ao interceptar os riscos reais (VP *
        # Ganho)[cite: 20].
        valor_preservado = verdadeiro_positivo * self.config.ganho_vp

        # Soma os dois prejuízos para quantificar a perda total provocada pelos erros do
        # modelo[cite: 20].
        perda_total_erros = prejuizo_negligencia + custo_alarmes_falsos

        # Calcula o resultado líquido contábil final (Receita Preservada - Perda Total
        # de Erros)[cite: 20].
        resultado_liquido = valor_preservado - perda_total_erros

        # Retorna o dicionário com o balancete discriminado em moeda corrente[cite: 20].
        return {
            "Modelo": nome_modelo,
            "Falsos_Negativos": falso_negativo,
            "Falsos_Positivos": falso_positivo,
            "Verdadeiros_Positivos": verdadeiro_positivo,
            "Verdadeiros_Negativos": verdadeiro_negativo,
            "Prejuizo_Negligencia_R$": round(prejuizo_negligencia, 2),
            "Custo_Alarmes_R$": round(custo_alarmes_falsos, 2),
            "Perda_Total_Erros_R$": round(perda_total_erros, 2),
            "Valor_Preservado_R$": round(valor_preservado, 2),
            "Resultado_Liquido_R$": round(resultado_liquido, 2),
        }
