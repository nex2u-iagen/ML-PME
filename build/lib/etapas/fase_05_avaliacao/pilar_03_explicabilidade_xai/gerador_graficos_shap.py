"""Módulo Especialista em Renderização Gráfica de Explicabilidade SHAP (Pilar 3).

Responsabilidade Única: Gerar e persistir no disco, com resolução de 300 DPI,
o Gráfico de Sumário Global (Beeswarm) e o Gráfico de Cascata Individual (Waterfall
Plot)[cite: 18, 20].
"""

# 'from typing import ...' importa os tipos estáticos formais para validação do
# código[cite: 18].
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from pathlib import Path' disponibiliza a manipulação portável de diretórios no
# sistema operacional.
from pathlib import Path

# 'import matplotlib.pyplot as plt' fornece os recursos de telas e gravação gráfica.
import matplotlib.pyplot as plt

# 'import numpy as np' manipula os tensores de dados observados[cite: 17].
import numpy as np

# 'import pandas as pd' estrutura os dados com nomes de colunas para as legendas dos
# gráficos[cite: 18].
import pandas as pd

# 'import shap' importa o framework oficial de visualizações estatísticas aditivas[cite:
# 20].
import shap


# 'class GeradorGraficosShap' isola exclusivamente a camada visual das figuras de
# XAI[cite: 20].
class GeradorGraficosShap:
    """Especialista responsável pela renderização e salvamento seguro de imagens do
    SHAP em 300 DPI[cite: 18, 20].
    """

    # 'def __init__(...)' instancia o gerador configurando a pasta física de
    # relatórios[cite: 20].
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa o gerador configurando o diretório de destino das figuras de
        XAI[cite: 20].

        Args:
            pasta_relatorios (Path): Diretório onde as imagens serão persistidas no
            disco[cite: 20].
        """
        self.pasta_relatorios = pasta_relatorios
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

    # 'def _salvar_figura_ativa(...)' captura a tela ativa desenhada pelo SHAP, salva e
    # limpa a memória RAM[cite: 18].
    def _salvar_figura_ativa(self, nome_arquivo: str) -> Path:
        """Centraliza o ajuste de margens da figura ativa, persistência em 300 DPI e
        limpeza de memória[cite: 17, 18].

        Args:
            nome_arquivo (str): Nome do arquivo físico no disco com extensão .png.

        Returns:
            Path: Rota física completa da imagem gravada.
        """
        # Captura a tela gráfica ativa onde o SHAP desenhou o gráfico (Get Current
        # Figure)[cite: 18].
        figura_ativa = plt.gcf()

        # Ajusta automaticamente o espaçamento das margens para prevenir cortes de
        # rótulos[cite: 18].
        figura_ativa.tight_layout()

        # Constrói o caminho completo de destino no disco.
        caminho_completo = self.pasta_relatorios / nome_arquivo

        # Grava o arquivo de imagem no disco com resolução de 300 pontos por polegada
        # (DPI)[cite: 18].
        figura_ativa.savefig(caminho_completo, dpi=300, bbox_inches="tight")

        # Fecha todas as telas abertas no matplotlib para blindar contra vazamento de
        # memória[cite: 18].
        plt.close("all")

        logging.info("Gráfico de XAI salvo com sucesso em: %s", nome_arquivo)
        return caminho_completo

    # 'def plotar_sumario_global(...)' gera o gráfico Beeswarm populacional[cite: 18,
    # 20].
    def plotar_sumario_global(
        self,
        valores_shap: np.ndarray,
        dados_avaliacao: np.ndarray,
        nomes_atributos: list[str],
    ) -> Path:
        """Renderiza o gráfico de sumário global ilustrando importância e direção do
        impacto[cite: 18, 20].

        Args:
            valores_shap (np.ndarray): Matriz 2D com as contribuições calculadas[cite:
            20].
            dados_avaliacao (np.ndarray): Matriz X com as observações avaliadas[cite:
            18, 20].
            nomes_atributos (List[str]): Lista com os nomes inteligíveis de cada
            coluna[cite: 18, 20].

        Returns:
            Path: Rota do arquivo PNG gravado em 300 DPI.
        """
        # Limpa qualquer estado residual do matplotlib antes de instanciar o plot.
        plt.clf()

        # Converte a matriz de observações para DataFrame com colunas nomeadas para
        # rotulagem automática[cite: 18].
        df_atributos = pd.DataFrame(dados_avaliacao, columns=nomes_atributos)

        # Abre uma janela de figura com dimensões adequadas para leitura de múltiplos
        # atributos[cite: 18].
        plt.figure(figsize=(10, 6))

        # 'shap.summary_plot' renderiza o gráfico de nuvem de dispersão (beeswarm)[cite:
        # 18, 20].
        shap.summary_plot(
            shap_values=valores_shap,
            features=df_atributos,
            feature_names=nomes_atributos,
            show=False,
        )

        # Adiciona o título descritivo corporativo no topo da visualização[cite: 18].
        plt.title(
            "Impacto Global das Variáveis na Decisão de Risco (SHAP Summary Plot)",
            fontsize=12,
            pad=15,
        )

        # Salva a figura ativa em 300 DPI e limpa o buffer gráfico[cite: 18].
        return self._salvar_figura_ativa("xai_impacto_global_sumario.png")

    # 'def plotar_cascata_individual(...)' gera a auditoria forense de um caso
    # específico[cite: 18, 20].
    def plotar_cascata_individual(
        self,
        valores_shap: np.ndarray,
        dados_avaliacao: np.ndarray,
        valor_base: float,
        nomes_atributos: list[str],
        indice_individuo: int = 0,
    ) -> Path:
        """Renderiza o gráfico de cascata (Waterfall) dissecando a decisão de um
        indivíduo[cite: 18, 20].

        Args:
            valores_shap (np.ndarray): Matriz 2D de contribuições[cite: 20].
            dados_avaliacao (np.ndarray): Matriz X de observações[cite: 18, 20].
            valor_base (float): Probabilidade esperada de partida E[f(x)][cite: 18, 20].
            nomes_atributos (List[str]): Nomes descritivos das colunas[cite: 18, 20].
            indice_individuo (int, opcional): Posição da amostra a ser auditada no lote.
            Padrão: 0[cite: 20].

        Returns:
            Path: Rota do arquivo PNG gravado em 300 DPI.
        """
        # Limpa qualquer estado residual do matplotlib antes da nova plotagem.
        plt.clf()

        plt.figure(figsize=(9, 6))

        # 'shap.Explanation' encapsula a estrutura oficial unindo forças aditivas e
        # valor de base[cite: 20].
        explicacao_individual = shap.Explanation(
            values=valores_shap[indice_individuo],
            base_values=valor_base,
            data=dados_avaliacao[indice_individuo],
            feature_names=nomes_atributos,
        )

        # 'shap.plots.waterfall' renderiza a cascata de empurrões positivos e negativos
        # a partir de E[f(X)][cite: 18, 20].
        shap.plots.waterfall(explicacao_individual, show=False)

        plt.title(
            f"Auditoria Forense Individual — Paciente/Cliente ID #{indice_individuo}",
            fontsize=12,
            pad=15,
        )

        return self._salvar_figura_ativa(
            f"xai_cascata_individual_amostra_{indice_individuo}.png"
        )
