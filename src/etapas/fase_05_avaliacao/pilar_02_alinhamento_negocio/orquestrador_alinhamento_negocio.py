"""Módulo Orquestrador de Impacto no Negócio (Fachada / Facade Pattern - Pilar 2).

Responsabilidade Única: Ponto de entrada unificado para a avaliação financeira do Top 3,
coordenando a CalculadoraImpactoFinanceiro sobre todo o catálogo de concorrentes
e compilando o Leaderboard financeiro ordenado pelo maior saldo líquido em reais[cite:
20].
"""

# 'from typing import ...' importa os tipos estáticos formais.
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging
from typing import Any

# 'import numpy as np' manipula arrays numéricos de teste[cite: 17].
import numpy as np

# 'import pandas as pd' estrutura os balancetes em DataFrames comparativos[cite: 18].
import pandas as pd

# Importa o especialista de apuração contábil matemática[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.calculadora_financeira import (  # noqa: E501
    CalculadoraImpactoFinanceiro,
)

# Importa o objeto de configuração de premissas econômicas do negócio.
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.configuracao_custos import (  # noqa: E501
    ConfiguracaoCustoRisco,
)


# 'class OrquestradorAlinhamentoNegocio' implementa a fachada executiva do Pilar 2[cite:
# 20].
class OrquestradorAlinhamentoNegocio:
    """Fachada unificada que coordena o ranqueamento financeiro dos modelos do
    pódio[cite: 20].
    """

    # 'def __init__(...)' compõe os especialistas e define as premissas monetárias
    # ativas[cite: 20].
    def __init__(
        self, configuracao_custos: ConfiguracaoCustoRisco | None = None
    ) -> None:
        """Inicializa a fachada compondo a calculadora contábil com as premissas
        informadas[cite: 20].

        Args:
            configuracao_custos (ConfiguracaoCustoRisco, opcional): Contrato de custos
            do comitê[cite: 20].
        """
        # Caso nenhuma configuração seja repassada, adota as premissas corporativas
        # padrão[cite: 20].
        self.configuracao = configuracao_custos or ConfiguracaoCustoRisco()

        # Instancia a calculadora matemática injetando as regras econômicas ativas[cite:
        # 20].
        self.calculadora = CalculadoraImpactoFinanceiro(
            configuracao_custos=self.configuracao
        )

    # 'def gerar_leaderboard_financeiro(...)' processa o catálogo e compila a tabela
    # ranqueada[cite: 20].
    def gerar_leaderboard_financeiro(
        self,
        catalogo_top3: dict[str, Any],
        matriz_atributos_teste: np.ndarray,
        vetor_alvo_teste: np.ndarray,
    ) -> pd.DataFrame:
        """Executa a apuração contábil de cada finalista e devolve o pódio financeiro
        classificado[cite: 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos
            concorrentes[cite: 20].
            matriz_atributos_teste (np.ndarray): Matriz X de teste cego retido
            (Holdout)[cite: 20].
            vetor_alvo_teste (np.ndarray): Vetor y real do conjunto de teste[cite: 20].

        Returns:
            pd.DataFrame: Leaderboard de impacto financeiro classificado pelo maior
            retorno líquido[cite: 20].
        """
        # Emite notificação no log informando o início da compilação contábil do Top 3.
        logging.info(
            "Compilando balancetes monetários e avaliando negligência para o pódio..."
        )

        # Inicializa a lista que acumulará os balancetes individuais de cada
        # concorrente.
        balancetes_compilados: list[dict[str, Any]] = []

        # Itera sobre cada modelo finalista acionando a calculadora especialista[cite:
        # 20].
        for nome_modelo, estimador in catalogo_top3.items():
            extrato_modelo = self.calculadora.apurar_balancete_modelo(
                nome_modelo=nome_modelo,
                estimador=estimador,
                matriz_atributos_teste=matriz_atributos_teste,
                vetor_alvo_teste=vetor_alvo_teste,
            )
            balancetes_compilados.append(extrato_modelo)

        # Converte a lista em um DataFrame do pandas para estruturação tabular[cite:
        # 18].
        tabela_financeira = pd.DataFrame(balancetes_compilados)

        # Ordena os modelos decrescentemente pelo saldo líquido contábil (maior retorno
        # financeiro no topo)[cite: 20].
        tabela_ranqueada = tabela_financeira.sort_values(
            by="Resultado_Liquido_R$", ascending=False
        ).reset_index(drop=True)

        # Retorna o Leaderboard de negócios pronto para apreciação executiva[cite: 20].
        return tabela_ranqueada
