"""Módulo Especialista em Renderização Gráfica Exclusiva do Modelo Campeão (Pilar 4).

Responsabilidade Única: Gerar e persistir no disco, com resolução de 300 DPI,
os laudos visuais limpos e individuais do modelo homologado para produção:
Matriz de Confusão detalhada, Curva ROC individual e Curva Precision-Recall individual[cite: 9, 10].
"""

# 'import' traz o módulo 'logging' da biblioteca padrão para registro de auditoria no terminal.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de rotas.
from pathlib import Path

# 'from' acessa 'typing' da biblioteca padrão para documentação de tipos formais.
from typing import Any, List

# 'import' traz o submódulo 'pyplot' do 'matplotlib' para controle de telas e figuras.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'numpy' para manipulação numérica e prevalência basal.
import numpy as np

# 'import' traz a biblioteca externa 'seaborn' para aplicação de temas visuais padronizados.
import seaborn as sns

# 'from' importa as classes de exibição gráfica de alta performance do Scikit-Learn[cite: 9, 10]:
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
)

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o especialista na telemetria visual solo do modelo campeão homologado[cite: 9].
class GeradorGraficosCampeao:
    """Especialista responsável pela telemetria visual individual do modelo homologado[cite: 9]."""

    # 'def __init__(...)' instancia o gerador configurando a pasta de destino solo[cite: 9].
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa o gerador configurando a pasta de destino das figuras do campeão[cite: 9].

        Args:
            pasta_relatorios (Path): Diretório onde as imagens solo serão gravadas no disco[cite: 9].
        """
        self.pasta_relatorios = Path(pasta_relatorios)
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")

    # 'def _salvar_figura(...)' é o método utilitário para gravação e desalocação de memória RAM[cite: 9].
    def _salvar_figura(self, figura: plt.Figure, nome_arquivo: str) -> Path:
        """Centraliza o ajuste de margens, persistência em 300 DPI e limpeza de memória[cite: 9].

        Args:
            figura (plt.Figure): Instância da tela gráfica do matplotlib a ser persistida[cite: 9].
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

    # 'def plotar_matriz_confusao_solo(...)' plota a matriz isolada do vencedor[cite: 9].
    def plotar_matriz_confusao_solo(
        self,
        estimador_campeao: Any,
        x_teste: Any,
        y_teste: Any,
        rotulos_classes: List[str],
        nome_modelo: str,
    ) -> Path:
        """Renderiza a matriz de confusão individual e limpa do modelo campeão[cite: 9].

        Args:
            estimador_campeao (Any): Estimador ou pipeline vencedor homologado[cite: 9].
            x_teste: Matriz X de teste cego retido[cite: 9].
            y_teste: Vetor y real do conjunto de teste[cite: 9].
            rotulos_classes (List[str]): Nomes amigáveis das classes avaliadas[cite: 9].
            nome_modelo (str): Identificador amigável do modelo vencedor[cite: 9].

        Returns:
            Path: Endereço do arquivo PNG exportado em alta definição.
        """
        figura, eixo = plt.subplots(figsize=(6, 5))

        # AJUSTE CIRÚRGICO: Parâmetro formal é 'X' maiúsculo[cite: 9, 10]!
        ConfusionMatrixDisplay.from_estimator(
            estimator=estimador_campeao,
            X=x_teste,
            y=y_teste,
            display_labels=rotulos_classes,
            cmap="Blues",
            colorbar=True,
            ax=eixo,
        )

        eixo.set_title(f"Matriz de Confusão Homologada — {nome_modelo}", fontsize=12, pad=12)
        eixo.set_xlabel("Classificação Predita pela Máquina", fontsize=10)
        eixo.set_ylabel("Condição Real Observada (Gabarito)", fontsize=10)
        eixo.grid(False)

        return self._salvar_figura(figura, "campeao_matriz_confusao_solo.png")

    # 'def plotar_curva_roc_solo(...)' plota a Curva ROC individual do vencedor[cite: 9, 10].
    def plotar_curva_roc_solo(
        self,
        estimador_campeao: Any,
        x_teste: Any,
        y_teste: Any,
        nome_modelo: str,
    ) -> Path:
        """Renderiza a Curva ROC individual desacoplando a configuração de cor e espessura[cite: 9, 10].

        Args:
            estimador_campeao (Any): Estimador vencedor ajustado[cite: 9].
            x_teste: Matriz X de teste retido[cite: 9].
            y_teste: Vetor y real do conjunto de teste[cite: 9].
            nome_modelo (str): Nome amigável do modelo campeão[cite: 9].

        Returns:
            Path: Endereço do arquivo gráfico salvo no disco.
        """
        figura, eixo = plt.subplots(figsize=(7, 6))

        # AJUSTE CIRÚRGICO: Parâmetro formal é 'X' maiúsculo[cite: 9, 10]!
        display_roc = RocCurveDisplay.from_estimator(
            estimator=estimador_campeao,
            X=x_teste,
            y=y_teste,
            name=nome_modelo,
            ax=eixo,
        )

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

        eixo.set_title(f"Capacidade Discriminativa Solo (ROC) — {nome_modelo}", fontsize=12, pad=12)
        eixo.set_xlabel("Taxa de Falsos Alarmes (1 - Especificidade / FPR)", fontsize=10)
        eixo.set_ylabel("Sensibilidade na Detecção de Riscos (Recall / TPR)", fontsize=10)
        eixo.legend(loc="lower right", fontsize=10, frameon=True)

        return self._salvar_figura(figura, "campeao_curva_roc_solo.png")

    # 'def plotar_curva_precision_recall_solo(...)' plota a Curva PR individual do vencedor[cite: 9, 10].
    def plotar_curva_precision_recall_solo(
        self,
        estimador_campeao: Any,
        x_teste: Any,
        y_teste: Any,
        nome_modelo: str,
    ) -> Path:
        """Renderiza a Curva Precision-Recall individual com estilização direta de linha[cite: 9, 10].

        Args:
            estimador_campeao (Any): Estimador vencedor ajustado[cite: 9].
            x_teste: Matriz X de teste cego retido[cite: 9].
            y_teste: Vetor y real do conjunto de teste[cite: 9].
            nome_modelo (str): Nome amigável do modelo campeão[cite: 9].

        Returns:
            Path: Endereço do arquivo gráfico salvo no disco.
        """
        figura, eixo = plt.subplots(figsize=(7, 6))

        # AJUSTE CIRÚRGICO: Parâmetro formal é 'X' maiúsculo[cite: 9, 10]!
        display_pr = PrecisionRecallDisplay.from_estimator(
            estimator=estimador_campeao,
            X=x_teste,
            y=y_teste,
            name=nome_modelo,
            ax=eixo,
        )

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

        eixo.set_title(f"Compromisso Precisão vs Sensibilidade (PR) — {nome_modelo}", fontsize=12, pad=12)
        eixo.set_xlabel("Sensibilidade na Cobertura dos Riscos (Recall)", fontsize=10)
        eixo.set_ylabel("Precisão nos Alarmes Emitidos (Precision)", fontsize=10)
        eixo.legend(loc="lower left", fontsize=9, frameon=True)

        return self._salvar_figura(figura, "campeao_curva_precision_recall_solo.png")