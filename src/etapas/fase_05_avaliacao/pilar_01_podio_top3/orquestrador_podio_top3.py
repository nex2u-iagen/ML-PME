"""Módulo de Orquestração do Pódio Top 3 (Fachada / Facade Pattern - Pilar 1).

Responsabilidade Única: Ponto de entrada unificado para a auditoria do pódio,
coordenando o AvaliadorMetricasTabulares e o GeradorGraficosPodio para
produzir o laudo pericial completo dos 3 melhores modelos em uma única chamada[cite:
20].
"""

# 'from typing import ...' importa os tipos estáticos formais.
# 'import logging' gerencia as mensagens de auditoria técnica no console.
import logging

# 'from pathlib import Path' manipula caminhos e pastas no disco.
from pathlib import Path
from typing import Any

# 'import numpy as np' manipula arrays numéricos de teste.
import numpy as np

# Importa o especialista em cálculos métricos e latência do pacote oficial
# 'fase_05_avaliacao'[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.avaliador_metricas import (
    AvaliadorMetricasTabulares,
)

# Importa o especialista em renderização gráfica do pacote oficial
# 'fase_05_avaliacao'[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.gerador_graficos_podio import (
    GeradorGraficosPodio,
)


# 'class OrquestradorPodioTop3' implementa o padrão Fachada unificando os
# especialistas[cite: 20].
class OrquestradorPodioTop3:
    """Fachada unificada que coordena o scorecard tabular e os gráficos do pódio Top
    3[cite: 20].
    """

    # 'def __init__(...)' compõe as instâncias dos especialistas por injeção de
    # dependência[cite: 20].
    def __init__(self, pasta_relatorios: Path) -> None:
        """Inicializa a fachada compondo o avaliador métrico e o gerador gráfico[cite:
        20].

        Args:
            pasta_relatorios (Path): Diretório onde os laudos visuais serão
            gravados[cite: 20].
        """
        # Armazena o diretório de destino e instancia os especialistas por
        # composição[cite: 20].
        self.pasta_relatorios = pasta_relatorios
        self.avaliador_metricas = AvaliadorMetricasTabulares()
        self.gerador_graficos = GeradorGraficosPodio(
            pasta_relatorios=self.pasta_relatorios
        )

    # 'def executar_auditoria_completa(...)' executa os dois especialistas e compila o
    # laudo final[cite: 20].
    def executar_auditoria_completa(
        self,
        catalogo_top3: dict[str, Any],
        matriz_atributos_teste: np.ndarray,
        vetor_alvo_teste: np.ndarray,
        rotulos_classes: list[str] = ["Saudavel", "Risco"],
    ) -> dict[str, Any]:
        """Coordena a execução completa da sabatina técnica do Top 3 (Tabelas e
        Figuras)[cite: 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos finalistas
            treinados[cite: 20].
            matriz_atributos_teste (np.ndarray): Matriz X de teste cego retido
            (Holdout)[cite: 20].
            vetor_alvo_teste (np.ndarray): Vetor y real do teste[cite: 20].
            rotulos_classes (List[str], opcional): Nomes amigáveis das classes
            avaliadas[cite: 20].

        Returns:
            Dict[str, Any]: Laudo técnico consolidado com scorecard tabular e rotas das
            figuras salvas[cite: 20].
        """
        # Registra no log de auditoria o início da orquestração unificada do pódio.
        logging.info(
            "=== EXECUTANDO AUDITORIA TÉCNICA E VISUAL DO PÓDIO (PILAR 1 - FASE 5) ==="
        )

        # 1. Aciona o Especialista de Métricas Tabulares e Latência[cite: 18, 20].
        scorecard = self.avaliador_metricas.comparar_modelos(
            catalogo_top3, matriz_atributos_teste, vetor_alvo_teste
        )

        # 2. Aciona o Especialista Gráfico para gerar as Matrizes de Confusão em painel
        # horizontal[cite: 18, 20].
        rota_matrizes = self.gerador_graficos.plotar_matrizes_confusao(
            catalogo_top3, matriz_atributos_teste, vetor_alvo_teste, rotulos_classes
        )

        # 3. Aciona o Especialista Gráfico para sobrepor as Curvas ROC[cite: 18, 20].
        rota_roc = self.gerador_graficos.plotar_curvas_roc(
            catalogo_top3, matriz_atributos_teste, vetor_alvo_teste
        )

        # 4. Aciona o Especialista Gráfico para sobrepor as Curvas
        # Precision-Recall[cite: 18, 20].
        rota_pr = self.gerador_graficos.plotar_curvas_precision_recall(
            catalogo_top3, matriz_atributos_teste, vetor_alvo_teste
        )

        # Emite log confirmando a conclusão limpa da auditoria.
        logging.info("=== AUDITORIA DO PILAR 1 CONCLUÍDA COM SUCESSO ===")

        # Retorna o laudo compilado com o DataFrame e os caminhos físicos das 3 figuras
        # geradas[cite: 20].
        return {
            "scorecard_tabular": scorecard,
            "figura_matrizes_confusao": str(rota_matrizes),
            "figura_curvas_roc": str(rota_roc),
            "figura_curvas_pr": str(rota_pr),
        }
