"""Módulo Orquestrador de Explicabilidade Forense (Fachada / Facade Pattern - Pilar 3).

Responsabilidade Única: Ponto de entrada unificado para a explicabilidade XAI,
coordenando a CalculadoraValoresShap e o GeradorGraficosShap para
produzir o laudo pericial aditivo (global e local) em uma única instrução limpa[cite:
18, 20].
"""

# 'from typing import ...' importa os tipos estáticos formais para o contrato da
# fachada[cite: 18].
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging
from collections.abc import Callable

# 'from pathlib import Path' disponibiliza a manipulação portável de caminhos e arquivos
# no disco.
from pathlib import Path
from typing import Any

# 'import numpy as np' manipula arrays numéricos de entrada e teste[cite: 17].
import numpy as np

# Importa o especialista de cálculos matemáticos de Shapley[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.calculadora_shap import (
    CalculadoraValoresShap,
)

# Importa o objeto de domínio com os parâmetros de configuração do SHAP[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.configuracao_shap import (  # noqa: E501
    ConfiguracaoShap,
)

# Importa o especialista de renderização gráfica em alta definição[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.gerador_graficos_shap import (  # noqa: E501
    GeradorGraficosShap,
)


# 'class OrquestradorExplicabilidadeShap' implementa a fachada executiva do Pilar
# 3[cite: 20].
class OrquestradorExplicabilidadeShap:
    """Fachada unificada que coordena o motor de explicabilidade causal e os laudos
    visuais do SHAP[cite: 18, 20].
    """

    # 'def __init__(...)' instancia a fachada compondo os especialistas por injeção de
    # dependência[cite: 20].
    def __init__(
        self,
        pasta_relatorios: Path,
        nomes_atributos: list[str],
        quantidade_amostras_fundo: int = 30,
        semente_aleatoria: int = 42,
    ) -> None:
        """Inicializa a fachada compondo a calculadora matemática e o gerador de
        figuras[cite: 20].

        Args:
            pasta_relatorios (Path): Diretório onde as imagens de XAI serão salvas[cite:
            20].
            nomes_atributos (List[str]): Rótulos amigáveis das colunas de entrada[cite:
            18, 20].
            quantidade_amostras_fundo (int): Volume de observações da base de
            referência[cite: 20].
            semente_aleatoria (int): Semente para controle determinístico dos
            sorteios[cite: 20].
        """
        self.pasta_relatorios = pasta_relatorios

        # Instancia o objeto de configuração de domínio do SHAP[cite: 20].
        self.configuracao = ConfiguracaoShap(
            nomes_atributos=nomes_atributos,
            quantidade_amostras_fundo=quantidade_amostras_fundo,
            semente_aleatoria=semente_aleatoria,
        )

        # Instancia a calculadora matemática de valores de Shapley[cite: 20].
        self.calculadora = CalculadoraValoresShap(configuracao=self.configuracao)

        # Instancia o gerador gráfico com persistência em 300 DPI[cite: 18, 20].
        self.gerador_graficos = GeradorGraficosShap(
            pasta_relatorios=self.pasta_relatorios
        )

    # 'def executar_auditoria_explicabilidade(...)' orquestra todos os passos do Pilar
    # 3[cite: 20].
    def executar_auditoria_explicabilidade(
        self,
        funcao_predicao_probabilidade: Callable[[np.ndarray], np.ndarray],
        dados_treinamento: np.ndarray,
        dados_avaliacao: np.ndarray,
        indice_amostra_individual: int = 0,
    ) -> dict[str, Any]:
        """Coordena a extração de valores SHAP, ranking de importância e persistência
        das figuras[cite: 18, 20].

        Args:
            funcao_predicao_probabilidade (Callable): Função que recebe matriz X e
            retorna vetor 1D de probabilidades[cite: 18].
            dados_treinamento (np.ndarray): Matriz X de treino para estimar a população
            de referência[cite: 20].
            dados_avaliacao (np.ndarray): Matriz X de teste contendo os indivíduos a
            serem explicados[cite: 18, 20].
            indice_amostra_individual (int, opcional): Posição da amostra a ser
            dissecada no gráfico de cascata[cite: 20].

        Returns:
            Dict[str, Any]: Dossiê completo de explicabilidade com tabela de impacto e
            caminhos das imagens[cite: 18, 20].
        """
        logging.info(
            "=== INICIANDO AUDITORIA DE INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL (PILAR 3 -"
            "FASE 5) ==="
        )

        # 1. Compila o explicador com a base de referência populacional[cite: 20].
        explicador = self.calculadora.construir_explicador(
            funcao_predicao_probabilidade=funcao_predicao_probabilidade,
            dados_treinamento=dados_treinamento,
        )

        # 2. Computa a matriz de valores de Shapley e o valor de partida esperado
        # E[f(x)][cite: 18, 20].
        valores_shap, valor_base = self.calculadora.calcular_matriz_shap(
            explicador=explicador,
            dados_avaliacao=dados_avaliacao,
        )

        # 3. Compila a tabela de importância global em linguagem de negócios[cite: 18,
        # 20].
        tabela_importancia = self.calculadora.compilar_importancia_global(
            valores_shap=valores_shap
        )

        # 4. Renderiza e grava o gráfico de sumário global (Beeswarm)[cite: 18, 20].
        rota_sumario = self.gerador_graficos.plotar_sumario_global(
            valores_shap=valores_shap,
            dados_avaliacao=dados_avaliacao,
            nomes_atributos=self.configuracao.nomes_atributos,
        )

        # 5. Renderiza e grava o gráfico de cascata individual (Waterfall)[cite: 18,
        # 20].
        rota_cascata = self.gerador_graficos.plotar_cascata_individual(
            valores_shap=valores_shap,
            dados_avaliacao=dados_avaliacao,
            valor_base=valor_base,
            nomes_atributos=self.configuracao.nomes_atributos,
            indice_individuo=indice_amostra_individual,
        )

        logging.info("=== AUDITORIA DO PILAR 3 (XAI) CONCLUÍDA COM SUCESSO ===")

        # Retorna o laudo pericial integrado pronto para apresentação executiva[cite:
        # 18, 20].
        return {
            "tabela_importancia_global": tabela_importancia,
            "valor_base_populacional": valor_base,
            "figura_sumario_global": str(rota_sumario),
            "figura_cascata_individual": str(rota_cascata),
        }
