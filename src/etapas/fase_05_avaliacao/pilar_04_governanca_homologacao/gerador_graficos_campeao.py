"""Módulo Especialista em Renderização Gráfica Exclusiva do Modelo Campeão (Pilar 4).

Responsabilidade Única: Gerar e persistir no disco, com resolução de 300 DPI,
os laudos visuais limpos e individuais do modelo homologado para produção:
Matriz de Confusão detalhada, Curva ROC individual e Curva Precision-Recall individual.
"""

# 'from typing import ...' importa os tipos estáticos formais para o contrato da classe.
# 'import logging' gerencia as notificações no console corporativo.
import logging

# 'from pathlib import Path' viabiliza a manipulação de caminhos no sistema de arquivos.
from pathlib import Path
from typing import Any

# 'import matplotlib.pyplot as plt' fornece os recursos visuais de telas e eixos.
import matplotlib.pyplot as plt

# 'import numpy as np' manipula arrays e cálculos de médias para taxa basal.
import numpy as np

# 'import seaborn as sns' aplica temas visuais padronizados sobre os eixos.
import seaborn as sns

# 'from sklearn.metrics import ...' importa as classes de exibição gráfica de alta
# performance.
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
)


# 'class GeradorGraficosCampeao' isola a renderização exclusiva do modelo vencedor.
class GeradorGraficosCampeao:
    """Especialista responsável pela telemetria visual solo do modelo homologado."""

    # 'def __init__(...)' instancia o gerador configurando a pasta de saída.
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa o gerador configurando a pasta de destino das figuras do campeão.

        Args:
            pasta_relatorios (Path): Diretório onde as imagens solo serão gravadas no
            disco.
        """
        self.pasta_relatorios = pasta_relatorios
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")

    # 'def _salvar_figura(...)' é um método utilitário privado para salvar e desalocar a
    # memória RAM.
    def _salvar_figura(self, figura: plt.Figure, nome_arquivo: str) -> Path:
        """Centraliza o ajuste de margens, persistência em 300 DPI e limpeza de memória.

        Args:
            figura (plt.Figure): Instância da figura gráfica a ser persistida.
            nome_arquivo (str): Nome do arquivo físico no disco com extensão .png.

        Returns:
            Path: Rota física do arquivo gerado no disco.
        """
        figura.tight_layout()
        caminho_completo = self.pasta_relatorios / nome_arquivo
        figura.savefig(caminho_completo, dpi=300, bbox_inches="tight")
        plt.close(figura)
        logging.info("Telemetria visual do campeão persistida em: %s", nome_arquivo)
        return caminho_completo

    # 'def plotar_matriz_confusao_solo(...)' plota a matriz isolada do vencedor.
    def plotar_matriz_confusao_solo(
        self,
        estimador_campeao: Any,
        x_teste: np.ndarray,
        y_teste: np.ndarray,
        rotulos_classes: list[str],
        nome_modelo: str,
    ) -> Path:
        """Renderiza a matriz de confusão individual e limpa do modelo campeão.

        Args:
            estimador_campeao (Any): Pipeline ou estimador vencedor ajustado.
            x_teste (np.ndarray): Matriz X de teste cego retido.
            y_teste (np.ndarray): Vetor y real do conjunto de teste.
            rotulos_classes (List[str]): Nomes amigáveis das classes avaliadas.
            nome_modelo (str): Identificador amigável do modelo vencedor.

        Returns:
            Path: Endereço do arquivo PNG exportado em alta definição.
        """
        figura, eixo = plt.subplots(figsize=(6, 5))

        ConfusionMatrixDisplay.from_estimator(
            estimator=estimador_campeao,
            x=x_teste,
            y=y_teste,
            display_labels=rotulos_classes,
            cmap="Blues",
            colorbar=True,
            ax=eixo,
        )

        eixo.set_title(
            f"Matriz de Confusão Homologada — {nome_modelo}", fontsize=12, pad=12
        )
        eixo.set_xlabel("Classificação Predita pela Máquina", fontsize=10)
        eixo.set_ylabel("Condição Real Observada (Gabarito)", fontsize=10)
        eixo.grid(False)

        return self._salvar_figura(figura, "campeao_matriz_confusao_solo.png")

    # 'def plotar_curva_roc_solo(...)' plota a Curva ROC individual do vencedor.
    def plotar_curva_roc_solo(
        self,
        estimador_campeao: Any,
        x_teste: np.ndarray,
        y_teste: np.ndarray,
        nome_modelo: str,
    ) -> Path:
        """Renderiza a Curva ROC individual desacoplando a configuração de cor e
        espessura.

        Args:
            estimador_campeao (Any): Estimador vencedor ajustado.
            x_teste (np.ndarray): Matriz X de teste retido.
            y_teste (np.ndarray): Vetor y real do conjunto de teste.
            nome_modelo (str): Nome amigável do modelo campeão.

        Returns:
            Path: Endereço do arquivo gráfico salvo no disco.
        """
        figura, eixo = plt.subplots(figsize=(7, 6))

        # Invocação limpa sem passar argumentos cosméticos inválidos para o
        # from_estimator.
        display_roc = RocCurveDisplay.from_estimator(
            estimator=estimador_campeao,
            x=x_teste,
            y=y_teste,
            name=nome_modelo,
            ax=eixo,
        )

        # AJUSTE CIRÚRGICO: Configura cor e espessura diretamente no objeto Line2D
        # retornado.
        display_roc.line_.set_color("#1f77b4")
        display_roc.line_.set_linewidth(2.5)

        eixo.plot(
            [0, 1],
            [0, 1],
            color="gray",
            linestyle="--",
            lw=1.2,
            label="Aleatório (AUC = 0.50)",
        )
        eixo.set_title(
            f"Capacidade Discriminativa Solo (ROC) — {nome_modelo}", fontsize=12, pad=12
        )
        eixo.set_xlabel(
            "Taxa de Falsos Alarmes (1 - Especificidade / FPR)", fontsize=10
        )
        eixo.set_ylabel(
            "Sensibilidade na Detecção de Riscos (Recall / TPR)", fontsize=10
        )
        eixo.legend(loc="lower right", fontsize=10, frameon=True)

        return self._salvar_figura(figura, "campeao_curva_roc_solo.png")

    # 'def plotar_curva_precision_recall_solo(...)' plota a Curva PR individual do
    # vencedor.
    def plotar_curva_precision_recall_solo(
        self,
        estimador_campeao: Any,
        x_teste: np.ndarray,
        y_teste: np.ndarray,
        nome_modelo: str,
    ) -> Path:
        """Renderiza a Curva Precision-Recall individual com estilização direta de
        linha.

        Args:
            estimador_campeao (Any): Estimador vencedor ajustado.
            x_teste (np.ndarray): Matriz X de teste cego retido.
            y_teste (np.ndarray): Vetor y real do conjunto de teste.
            nome_modelo (str): Nome amigável do modelo campeão.

        Returns:
            Path: Endereço do arquivo gráfico salvo no disco.
        """
        figura, eixo = plt.subplots(figsize=(7, 6))

        # Invocação limpa sem argumentos cosméticos diretos.
        display_pr = PrecisionRecallDisplay.from_estimator(
            estimator=estimador_campeao,
            x=x_teste,
            y=y_teste,
            name=nome_modelo,
            ax=eixo,
        )

        # AJUSTE CIRÚRGICO: Configura cor e espessura diretamente no traço da linha.
        display_pr.line_.set_color("#2ca02c")
        display_pr.line_.set_linewidth(2.5)

        prevalencia = float(np.mean(y_teste))
        eixo.axhline(
            y=prevalencia,
            color="gray",
            linestyle="--",
            lw=1.2,
            label=f"Taxa Basal ({prevalencia:.1%})",
        )
        eixo.set_title(
            f"Compromisso Precisão vs Sensibilidade (PR) — {nome_modelo}",
            fontsize=12,
            pad=12,
        )
        eixo.set_xlabel("Sensibilidade na Cobertura dos Riscos (Recall)", fontsize=10)
        eixo.set_ylabel("Precisão nos Alarmes Emitidos (Precision)", fontsize=10)
        eixo.legend(loc="lower left", fontsize=10, frameon=True)

        return self._salvar_figura(figura, "campeao_curva_precision_recall_solo.png")
