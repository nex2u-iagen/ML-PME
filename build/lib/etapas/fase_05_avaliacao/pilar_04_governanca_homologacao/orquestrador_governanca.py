"""Módulo de Orquestração de Governança e Dossiê Executivo (Fachada - Pilar 4).

Responsabilidade Única: Ponto de entrada unificado para a homologação executiva,
coordenando compilador, emissor de parecer, gerador gráfico solo do campeão e formatador
para produzir o Dossiê Formal com imagens limpas e exclusivas do vencedor[cite: 17, 18,
20, 22].
"""

# 'from typing import ...' importa os tipos estáticos formais[cite: 18].
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from pathlib import Path' disponibiliza caminhos portáveis de arquivos.
from pathlib import Path
from typing import Any

# 'import numpy as np' manipula arrays numéricos de teste[cite: 17].
import numpy as np

# 'import pandas as pd' manipula estruturas tabulares[cite: 18].
import pandas as pd

# Importa a equipe de especialistas do Pilar 4[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.compilador_scorecard_geral import (  # noqa: E501
    CompiladorScorecardGeral,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.emissor_parecer_tecnico import (  # noqa: E501
    EmissorParecerTecnico,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.formatador_dossie_markdown import (  # noqa: E501
    FormatadorDossieMarkdown,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.gerador_graficos_campeao import (  # noqa: E501
    GeradorGraficosCampeao,
)


# 'class OrquestradorGovernanca' implementa a fachada executiva de aprovação[cite: 17,
# 20].
class OrquestradorGovernanca:
    """Fachada unificada que coordena o scorecard, as regras de aceite e o dossiê
    limpo do campeão[cite: 17, 20].
    """

    # 'def __init__(...)' instancia os componentes especializados por injeção de
    # dependência[cite: 20].
    def __init__(
        self,
        pasta_relatorios: Path,
        emissor_regras: EmissorParecerTecnico | None = None,
    ) -> None:
        """Inicializa a fachada compondo compilador, parecerista, gerador gráfico e
        formatador[cite: 20].

        Args:
            pasta_relatorios (Path): Diretório onde o Dossiê Oficial e imagens serão
            gravados no disco[cite: 20].
            emissor_regras (EmissorParecerTecnico, opcional): Motor customizado de
            regras de aceite[cite: 20].
        """
        self.pasta_relatorios = pasta_relatorios
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        # Subpasta dedicada exclusivamente para os gráficos limpos do modelo
        # campeão[cite: 20].
        self.pasta_figuras_campeao = (
            self.pasta_relatorios.parent
            / "figuras"
            / "fase_05_avaliacao"
            / "campeao_solo"
        )
        self.pasta_figuras_campeao.mkdir(parents=True, exist_ok=True)

        self.compilador = CompiladorScorecardGeral()
        self.emissor = emissor_regras or EmissorParecerTecnico()
        self.gerador_campeao = GeradorGraficosCampeao(
            pasta_relatorios=self.pasta_figuras_campeao
        )
        self.formatador = FormatadorDossieMarkdown()

    # 'def gerar_dossie_executivo(...)' coordena a certificação oficial e grava o laudo
    # limpo[cite: 18, 20].
    def gerar_dossie_executivo(
        self,
        scorecard_tecnico: pd.DataFrame,
        leaderboard_financeiro: pd.DataFrame,
        laudo_explicabilidade: dict[str, Any],
        estimador_campeao: Any,
        x_teste: np.ndarray,
        y_teste: np.ndarray,
        rotulos_classes: list[str] = ["Saudavel", "Risco"],
    ) -> dict[str, Any]:
        """Gera a justificativa tabular do pódio e telemetria visual exclusiva do
        campeão[cite: 18, 20].

        Args:
            scorecard_tecnico (pd.DataFrame): Métricas técnicas e latência do Pilar
            1[cite: 18, 20].
            leaderboard_financeiro (pd.DataFrame): Balancete em reais do Pilar 2[cite:
            20].
            laudo_explicabilidade (Dict[str, Any]): Destaques causais e SHAP do Pilar
            3[cite: 18, 20].
            estimador_campeao (Any): Pipeline ajustado do modelo vencedor
            homologado[cite: 20].
            x_teste (np.ndarray): Matriz X de teste cego retido[cite: 20].
            y_teste (np.ndarray): Vetor y real do conjunto de teste[cite: 20].
            rotulos_classes (List[str], opcional): Nomes amigáveis das classes[cite:
            20].

        Returns:
            Dict[str, Any]: Dossiê consolidado com parecer, scorecard e caminho do
            arquivo salvo[cite: 20].
        """
        logging.info(
            "=== EMITINDO DOSSIÊ DE HOMOLOGAÇÃO COM DADOS LIMPOS DO CAMPEÃO ==="
        )

        # 1. Compilação do Scorecard Geral Integrado (Arbitragem do Pódio Top 3)[cite:
        # 20].
        scorecard_geral = self.compilador.unificar_laudos(
            scorecard_tecnico=scorecard_tecnico,
            leaderboard_financeiro=leaderboard_financeiro,
            laudo_explicabilidade=laudo_explicabilidade,
        )

        # 2. Avaliação formal do modelo campeão pelo motor de regras de negócio[cite:
        # 20].
        registro_campeao = scorecard_geral.iloc[0]
        nome_campeao = str(registro_campeao["Modelo"])
        parecer = self.emissor.avaliar_modelo_campeao(registro_campeao)

        # 3. Geração das evidências visuais limpas e individuais EXCLUSIVAS do
        # campeão[cite: 18, 20].
        rota_matriz_solo = self.gerador_campeao.plotar_matriz_confusao_solo(
            estimador_campeao=estimador_campeao,
            x_teste=x_teste,
            y_teste=y_teste,
            rotulos_classes=rotulos_classes,
            nome_modelo=nome_campeao,
        )
        rota_roc_solo = self.gerador_campeao.plotar_curva_roc_solo(
            estimador_campeao=estimador_campeao,
            x_teste=x_teste,
            y_teste=y_teste,
            nome_modelo=nome_campeao,
        )
        rota_pr_solo = self.gerador_campeao.plotar_curva_precision_recall_solo(
            estimador_campeao=estimador_campeao,
            x_teste=x_teste,
            y_teste=y_teste,
            nome_modelo=nome_campeao,
        )

        # 4. Catálogo consolidado de rotas com evidências exclusivas do vencedor[cite:
        # 18, 20].
        catalogo_figuras_campeao = {
            "matriz_solo": str(rota_matriz_solo),
            "roc_solo": str(rota_roc_solo),
            "pr_solo": str(rota_pr_solo),
            "shap_global": str(laudo_explicabilidade["figura_sumario_global"]),
            "shap_local": str(laudo_explicabilidade["figura_cascata_individual"]),
        }

        # 5. Formatação visual do documento Markdown executivo estruturado[cite: 17, 18,
        # 20].
        conteudo_markdown = self.formatador.compilar_markdown_completo(
            registro_campeao=registro_campeao,
            parecer_homologacao=parecer,
            scorecard_geral=scorecard_geral,
            catalogo_rotas_figuras=catalogo_figuras_campeao,
            pasta_destino_dossie=self.pasta_relatorios,
        )

        # 6. Gravação física do documento oficial no disco[cite: 20].
        caminho_dossie = self.pasta_relatorios / "dossie_homologacao_executiva.md"
        with open(caminho_dossie, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo_markdown)

        logging.info(
            "Dossiê Executivo Oficial gravado com sucesso em: %s", caminho_dossie
        )
        logging.info("=== MODELO HOMOLOGADO COM TELEMETRIA LIMPA EXCLUSIVA! ===")

        return {
            "scorecard_geral": scorecard_geral,
            "parecer_homologacao": parecer,
            "caminho_dossie_arquivo": str(caminho_dossie),
        }
