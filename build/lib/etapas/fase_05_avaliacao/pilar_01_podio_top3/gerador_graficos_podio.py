"""Módulo Especialista em Renderização Gráfica Comparativa do Pódio (Pilar 1).

Responsabilidade Única: Gerar e persistir no disco, com resolução de 300 DPI,
os três laudos visuais do Top 3: Matrizes de Confusão em painel horizontal,
Curvas ROC sobrepostas e Curvas Precision-Recall sobrepostas com ajuste seguro de linha.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros técnicos no console corporativo.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de diretórios.
from pathlib import Path

# 'from' acessa 'typing' da biblioteca padrão para anotação estática rigorosa de interfaces.
from typing import Any, Dict, List

# 'import' traz o submódulo 'pyplot' do 'matplotlib' para controle de telas e figuras gráficas.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'numpy' para manipulação numérica e cálculo de prevalência basal.
import numpy as np

# 'import' traz a biblioteca externa 'seaborn' para aplicação de temas estéticos padronizados.
import seaborn as sns

# 'from' importa as classes de exibição gráfica de alta performance do Scikit-Learn:
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


# 'class' declara o especialista responsável exclusivamente pela geração visual do pódio.
class GeradorGraficosPodio:
    """Especialista responsável pela renderização e persistência de figuras do Top 3 em alta resolução."""

    # 'def __init__(...)' instancia o gerador configurando a pasta física de relatórios.
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa o gerador configurando a pasta de destino das figuras comparativas.

        Args:
            pasta_relatorios (Path): Diretório onde as imagens serão gravadas no disco.
        """
        # Armazena a referência da pasta de destino das imagens no disco.
        self.pasta_relatorios = Path(pasta_relatorios)

        # Garante a criação física da pasta de relatórios caso ela ainda não exista.
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        # Define o tema estético limpo do seaborn para padronização visual corporativa.
        sns.set_theme(style="whitegrid")

    # 'def _salvar_figura(...)' é um método utilitário privado para salvar e desalocar a memória RAM.
    def _salvar_figura(self, figura: plt.Figure, nome_arquivo: str) -> Path:
        """Centraliza o ajuste de margens, salvamento em 300 DPI e limpeza de memória[cite: 9].

        Args:
            figura (plt.Figure): Instância da tela gráfica do matplotlib a ser persistida[cite: 9].
            nome_arquivo (str): Nome do arquivo físico no disco com extensão .png.

        Returns:
            Path: Rota física do arquivo gerado no sistema operacional.
        """
        # Ajusta automaticamente o espaçamento das margens para evitar cortes de legendas.
        figura.tight_layout()

        # Constrói o caminho completo unindo a pasta de relatórios ao nome do arquivo.
        caminho_completo = self.pasta_relatorios / nome_arquivo

        # Salva o arquivo de imagem no disco em resolução industrial de 300 pontos por polegada (DPI)[cite: 9].
        figura.savefig(caminho_completo, dpi=300, bbox_inches="tight")

        # Fecha a figura no matplotlib imediatamente para blindar contra vazamento de memória (Memory Leak).
        plt.close(figura)

        # Confirma no log a persistência do arquivo gráfico.
        logging.info("Artefato gráfico do Top 3 persistido em: %s", nome_arquivo)

        # Retorna a rota física do arquivo gravado.
        return caminho_completo

    # 'def plotar_matrizes_confusao(...)' renderiza o painel de 3 matrizes lado a lado[cite: 9].
    def plotar_matrizes_confusao(
        self,
        catalogo_top3: Dict[str, Any],
        x_teste: Any,
        y_teste: Any,
        rotulos_classes: List[str],
    ) -> Path:
        """Renderiza as 3 matrizes de confusão do pódio em painel horizontal unificado[cite: 9].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos avaliados[cite: 9].
            x_teste: Matriz X de teste cego retido (DataFrame ou ndarray)[cite: 9].
            y_teste: Vetor y real do teste cego[cite: 9].
            rotulos_classes (List[str]): Nomes amigáveis das classes avaliadas[cite: 9].

        Returns:
            Path: Endereço da imagem gravada no disco.
        """
        # Inicializa a moldura gráfica com 1 linha e 3 colunas de eixos independentes.
        figura, eixos = plt.subplots(1, 3, figsize=(15, 4.2))

        # Itera por cada modelo desenhando a matriz diretamente através da API nativa[cite: 9]:
        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # AJUSTE CIRÚRGICO: Parâmetro obrigatório é 'X' maiúsculo (e não 'x')!
            ConfusionMatrixDisplay.from_estimator(
                estimator=estimador,
                X=x_teste,
                y=y_teste,
                display_labels=rotulos_classes,
                cmap="Blues",
                colorbar=False,
                ax=eixos[indice],
            )

            # Define o título destacando a colocação no pódio e o nome do modelo[cite: 9].
            eixos[indice].set_title(
                f"#{indice + 1}: {nome_modelo}", fontsize=11, pad=10
            )
            # Desativa as linhas de grade cinzas de fundo para melhorar a legibilidade dos valores.
            eixos[indice].grid(False)

        # Salva o painel unificado e retorna a rota física do arquivo[cite: 9].
        return self._salvar_figura(figura, "comparativo_top3_matrizes_confusao.png")

    # 'def plotar_curvas_roc(...)' sobrepõe as Curvas ROC dos 3 finalistas de forma segura.
    def plotar_curvas_roc(
        self,
        catalogo_top3: Dict[str, Any],
        x_teste: Any,
        y_teste: Any,
    ) -> Path:
        """Sobrepõe as Curvas ROC dos 3 finalistas com ajuste desacoplado de espessura de linha[cite: 9, 10].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos concorrentes[cite: 9].
            x_teste: Matriz X de teste retido[cite: 9].
            y_teste: Vetor y real do teste[cite: 9].

        Returns:
            Path: Endereço da imagem gravada no disco.
        """
        figura, eixo = plt.subplots(figsize=(7.5, 6.5))

        # Itera pelos modelos sobrepondo as curvas no mesmo eixo gráfico[cite: 9]:
        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # AJUSTE CIRÚRGICO: Parâmetro formal é 'X' maiúsculo[cite: 9, 10]!
            display_roc = RocCurveDisplay.from_estimator(
                estimator=estimador,
                X=x_teste,
                y=y_teste,
                name=f"#{indice + 1}: {nome_modelo}",
                ax=eixo,
            )
            # Configura a espessura diretamente no objeto de linha retornado (Line2D)[cite: 9].
            display_roc.line_.set_linewidth(2.2)

        # Plota a linha diagonal tracejada de referência do classificador puramente aleatório[cite: 9, 10].
        eixo.plot(
            [0, 1],
            [0, 1],
            color="gray",
            linestyle="--",
            lw=1.2,
            label="Aleatório (AUC = 0.50)",
        )

        eixo.set_title("Curvas ROC Sobrepostas: Discriminação do Top 3", fontsize=12, pad=12)
        eixo.set_xlabel("Taxa de Falsos Alarmes (1 - Especificidade / FPR)", fontsize=10)
        eixo.set_ylabel("Sensibilidade na Detecção de Riscos (Recall / TPR)", fontsize=10)
        eixo.legend(loc="lower right", fontsize=9, frameon=True)

        return self._salvar_figura(figura, "comparativo_top3_curvas_roc.png")

    # 'def plotar_curvas_precision_recall(...)' afere o rigor sob classes raras[cite: 9, 10].
    def plotar_curvas_precision_recall(
        self,
        catalogo_top3: Dict[str, Any],
        x_teste: Any,
        y_teste: Any,
    ) -> Path:
        """Sobrepõe as Curvas Precision-Recall com ajuste desacoplado de espessura de linha[cite: 9, 10].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os modelos concorrentes[cite: 9].
            x_teste: Matriz X de teste cego retido[cite: 9].
            y_teste: Vetor y real do teste[cite: 9].

        Returns:
            Path: Endereço da imagem gravada no disco.
        """
        figura, eixo = plt.subplots(figsize=(7.5, 6.5))

        for indice, (nome_modelo, estimador) in enumerate(catalogo_top3.items()):
            # AJUSTE CIRÚRGICO: Parâmetro formal é 'X' maiúsculo[cite: 9, 10]!
            display_pr = PrecisionRecallDisplay.from_estimator(
                estimator=estimador,
                X=x_teste,
                y=y_teste,
                name=f"#{indice + 1}: {nome_modelo}",
                ax=eixo,
            )
            display_pr.line_.set_linewidth(2.2)

        # Adiciona a linha basal com a prevalência natural de casos de risco observada na amostra[cite: 9].
        prevalencia = float(np.mean(y_teste))
        eixo.axhline(
            y=prevalencia,
            color="gray",
            linestyle="--",
            lw=1.2,
            label=f"Taxa Basal ({prevalencia:.1%})",
        )

        eixo.set_title("Curvas Precision-Recall Sobrepostas: Rigor sob Classes Raras", fontsize=12, pad=12)
        eixo.set_xlabel("Sensibilidade na Cobertura dos Riscos (Recall)", fontsize=10)
        eixo.set_ylabel("Precisão nos Alarmes Emitidos (Precision)", fontsize=10)
        eixo.legend(loc="lower left", fontsize=9, frameon=True)

        return self._salvar_figura(figura, "comparativo_top3_curvas_precision_recall.png")