"""Módulo Especialista em Renderização Gráfica Comparativa do Pódio (Pilar 1).

Responsabilidade Única: Gerar e persistir no disco, com resolução de 300 DPI,
os três laudos visuais do Top 3: Matrizes de Confusão em painel horizontal,
Curvas ROC sobrepostas e Curvas Precision-Recall sobrepostas com ajuste seguro de linha.
"""

# 'from typing import ...' importa os tipos estáticos formais para o contrato da classe.
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from pathlib import Path' disponibiliza a manipulação portável de diretórios no
# sistema de arquivos.
from pathlib import Path
from typing import Any

# 'import matplotlib.pyplot as plt' fornece os recursos visuais de telas e eixos[cite:
# 17, 18].
import matplotlib.pyplot as plt

# 'import numpy as np' manipula arrays e cálculos de médias para taxa basal.
import numpy as np

# 'import seaborn as sns' aplica temas visuais padronizados sobre os eixos[cite: 18].
import seaborn as sns

# 'from sklearn.metrics import ...' importa as classes de exibição gráfica de alta
# performance.
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
)


# 'class GeradorGraficosPodio' isola a manipulação visual gráfica.
class GeradorGraficosPodio:
    """Especialista responsável pela renderização e persistência de figuras em alta
    definição[cite: 18, 20].
    """

    # 'def __init__(...)' instancia o especialista configurando a pasta de saída[cite:
    # 20].
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa o gerador configurando a pasta de destino das figuras[cite: 20].

        Args:
            pasta_relatorios (Path): Diretório onde as imagens serão gravadas no
            disco[cite: 20].
        """
        # Armazena a referência da pasta de destino das imagens no disco.
        self.pasta_relatorios = pasta_relatorios

        # Garante a criação física da pasta de relatórios caso ela ainda não exista.
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        # Define o tema estético limpo do seaborn para padronização visual corporativa.
        sns.set_theme(style="whitegrid")

    # 'def _salvar_figura(...)' é um método utilitário privado para salvar e desalocar a
    # memória RAM[cite: 18].
    def _salvar_figura(self, figura: plt.Figure, nome_arquivo: str) -> Path:
        """Centraliza o ajuste de margens, salvamento em 300 DPI e limpeza de
        memória[cite: 17, 18].

        Args:
            figura (plt.Figure): Instância da figura do matplotlib a ser
            persistida[cite: 17, 18].
            nome_arquivo (str): Nome do arquivo físico no disco.

        Returns:
            Path: Rota física do arquivo gerado no sistema operacional.
        """
        # Ajusta automaticamente o espaçamento das margens para evitar cortes de
        # legendas[cite: 18].
        figura.tight_layout()

        # Constrói o caminho completo unindo a pasta de relatórios ao nome do arquivo.
        caminho_completo = self.pasta_relatorios / nome_arquivo

        # Salva o arquivo de imagem no disco em resolução industrial de 300 pontos por
        # polegada (DPI)[cite: 18].
        figura.savefig(caminho_completo, dpi=300, bbox_inches="tight")

        # Fecha a figura no matplotlib imediatamente para blindar contra vazamento de
        # memória[cite: 18].
        plt.close(figura)

        # Confirma no log a persistência do arquivo gráfico.
        logging.info("Artefato gráfico persistido em: %s", nome_arquivo)

        # Retorna a rota do arquivo físico gravado.
        return caminho_completo

    # 'def plotar_matrizes_confusao(...)' renderiza o painel de 3 matrizes lado a
    # lado[cite: 20].
    def plotar_matrizes_confusao(
        self,
        catalogo_top3: dict[str, Any],
        x_teste: np.ndarray,
        y_teste: np.ndarray,
        rotulos_classes: list[str],
    ) -> Path:
        """Renderiza as 3 matrizes de confusão do pódio em painel horizontal
        unificado[cite: 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os estimadores
            avaliados[cite: 20].
            x_teste (np.ndarray): Matriz X de teste cego retido[cite: 20].
            y_teste (np.ndarray): Vetor y real do teste[cite: 20].
            rotulos_classes (List[str]): Nomes amigáveis das classes avaliadas[cite:
            20].

        Returns:
            Path: Endereço da imagem gravada.
        """
        # Inicializa a moldura gráfica com 1 linha e 3 colunas de eixos independentes.
        figura, eixos = plt.subplots(1, 3, figsize=(15, 4.2))

        # Itera por cada modelo desenhando a matriz diretamente através da API
        # nativa[cite: 18, 20].
        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # 'ConfusionMatrixDisplay.from_estimator' gera o mapa térmico com uma única
            # chamada nativa[cite: 18, 20].
            ConfusionMatrixDisplay.from_estimator(
                estimator=estimador,
                x=x_teste,
                y=y_teste,
                display_labels=rotulos_classes,
                cmap="Blues",
                colorbar=False,
                ax=eixos[indice],
            )
            # Define o título destacando a colocação no pódio e o nome do modelo[cite:
            # 20].
            eixos[indice].set_title(
                f"#{indice + 1}: {nome_modelo}", fontsize=11, pad=10
            )
            # Desativa as linhas de grade cinzas de fundo para melhorar a legibilidade
            # dos valores.
            eixos[indice].grid(False)

        # Salva o painel unificado e retorna a rota física do arquivo[cite: 18].
        return self._salvar_figura(figura, "comparativo_top3_matrizes_confusao.png")

    # 'def plotar_curvas_roc(...)' sobrepõe as Curvas ROC dos 3 finalistas de forma
    # segura[cite: 18, 20].
    def plotar_curvas_roc(
        self,
        catalogo_top3: dict[str, Any],
        x_teste: np.ndarray,
        y_teste: np.ndarray,
    ) -> Path:
        """Sobrepõe as Curvas ROC dos 3 finalistas com ajuste desacoplado de espessura
        de linha[cite: 18, 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos
            concorrentes[cite: 20].
            x_teste (np.ndarray): Matriz X de teste retido[cite: 20].
            y_teste (np.ndarray): Vetor y real do teste[cite: 20].

        Returns:
            Path: Endereço da imagem gravada.
        """
        # Inicializa a moldura gráfica proporcional para análise da separabilidade[cite:
        # 18].
        figura, eixo = plt.subplots(figsize=(7.5, 6.5))

        # Itera pelos modelos sobrepondo as curvas no mesmo eixo[cite: 18, 20].
        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # 'from_estimator' calcula as taxas e plota sem argumentos inesperados de
            # linha[cite: 18, 20].
            display_roc = RocCurveDisplay.from_estimator(
                estimator=estimador,
                x=x_teste,
                y=y_teste,
                name=f"#{indice + 1}: {nome_modelo}",
                ax=eixo,
            )
            # AJUSTE CIRÚRGICO: Configura a espessura diretamente no objeto de linha
            # retornado (Line2D)[cite: 18].
            display_roc.line_.set_linewidth(2.2)

        # Plota a linha diagonal tracejada de referência do classificador puramente
        # aleatório[cite: 18].
        eixo.plot(
            [0, 1],
            [0, 1],
            color="gray",
            linestyle="--",
            lw=1.2,
            label="Aleatório (AUC = 0.50)",
        )

        # Configura os títulos técnicos dos eixos e legendas[cite: 18].
        eixo.set_title(
            "Curvas ROC Sobrepostas: Discriminação do Top 3", fontsize=12, pad=12
        )
        eixo.set_xlabel(
            "Taxa de Falsos Alarmes (1 - Especificidade / FPR)", fontsize=10
        )
        eixo.set_ylabel(
            "Sensibilidade na Detecção de Riscos (Recall / TPR)", fontsize=10
        )
        eixo.legend(loc="lower right", fontsize=9, frameon=True)

        # Salva o arquivo de imagem e retorna o caminho físico[cite: 18].
        return self._salvar_figura(figura, "comparativo_top3_curvas_roc.png")

    # 'def plotar_curvas_precision_recall(...)' afere o rigor sob classes raras de forma
    # segura[cite: 18, 20].
    def plotar_curvas_precision_recall(
        self,
        catalogo_top3: dict[str, Any],
        x_teste: np.ndarray,
        y_teste: np.ndarray,
    ) -> Path:
        """Sobrepõe as Curvas Precision-Recall com ajuste desacoplado de espessura de
        linha[cite: 18, 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os modelos concorrentes[cite:
            20].
            x_teste (np.ndarray): Matriz X de teste cego retido[cite: 20].
            y_teste (np.ndarray): Vetor y real do teste[cite: 20].

        Returns:
            Path: Endereço da imagem gravada.
        """
        # Inicializa a moldura gráfica para avaliação de precisão[cite: 18].
        figura, eixo = plt.subplots(figsize=(7.5, 6.5))

        # Itera pelos concorrentes sobrepondo as curvas de pureza[cite: 18, 20].
        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # 'from_estimator' calcula a precisão e sensibilidade sem argumentos
            # cosméticos inválidos[cite: 18, 20].
            display_pr = PrecisionRecallDisplay.from_estimator(
                estimator=estimador,
                x=x_teste,
                y=y_teste,
                name=f"#{indice + 1}: {nome_modelo}",
                ax=eixo,
            )
            # AJUSTE CIRÚRGICO: Configura a espessura diretamente no objeto de linha
            # retornado (Line2D)[cite: 18].
            display_pr.line_.set_linewidth(2.2)

        # Adiciona a linha basal com a prevalência natural de casos de risco observada
        # na amostra[cite: 18].
        prevalencia = float(np.mean(y_teste))
        eixo.axhline(
            y=prevalencia,
            color="gray",
            linestyle="--",
            lw=1.2,
            label=f"Taxa Basal ({prevalencia:.1%})",
        )

        # Configura os títulos dos eixos e legendas[cite: 18].
        eixo.set_title(
            "Curvas Precision-Recall Sobrepostas: Rigor sob Classes Raras",
            fontsize=12,
            pad=12,
        )
        eixo.set_xlabel("Sensibilidade na Cobertura dos Riscos (Recall)", fontsize=10)
        eixo.set_ylabel("Precisão nos Alarmes Emitidos (Precision)", fontsize=10)
        eixo.legend(loc="lower left", fontsize=9, frameon=True)

        # Salva o arquivo de imagem e retorna o caminho físico[cite: 18].
        return self._salvar_figura(
            figura, "comparativo_top3_curvas_precision_recall.png"
        )
