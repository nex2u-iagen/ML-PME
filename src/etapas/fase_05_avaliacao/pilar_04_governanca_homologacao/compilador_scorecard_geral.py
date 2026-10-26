"""Módulo Especialista em Consolidação e Cruzamento de Laudos (Pilar 4).

Responsabilidade Única: Integrar os laudos técnicos do Pilar 1 (desempenho e latência),
os balancetes financeiros em reais do Pilar 2 e os destaques de explicabilidade do Pilar
3
em um único Scorecard Executivo tabular[cite: 18, 20].
"""

# 'from typing import ...' importa os tipos estáticos formais para documentação[cite:
# 18].
# 'import logging' gerencia as notificações operacionais no console.
import logging
from typing import Any

# 'import pandas as pd' estrutura os dados em tabelas relacionais consolidadas[cite:
# 18].
import pandas as pd


# 'class CompiladorScorecardGeral' isola unicamente o cruzamento e unificação de
# laudos[cite: 20].
class CompiladorScorecardGeral:
    """Especialista responsável pela unificação relacional dos laudos dos pilares da
    Fase 5[cite: 20].
    """

    # 'def unificar_laudos(...)' funde os resultados técnicos, econômicos e
    # causais[cite: 18, 20].
    def unificar_laudos(
        self,
        scorecard_tecnico: pd.DataFrame,
        leaderboard_financeiro: pd.DataFrame,
        laudo_explicabilidade: dict[str, Any],
    ) -> pd.DataFrame:
        """Cruza as tabelas de métricas e custos, adicionando metadados de XAI[cite: 18,
        20].

        Args:
            scorecard_tecnico (pd.DataFrame): Tabela com F1, Recall, ROC-AUC e Latência
            (Pilar 1)[cite: 18, 20].
            leaderboard_financeiro (pd.DataFrame): Tabela com Perdas e Saldo Líquido em
            R$ (Pilar 2)[cite: 20].
            laudo_explicabilidade (Dict[str, Any]): Dicionário com ranking SHAP e valor
            base (Pilar 3)[cite: 18, 20].

        Returns:
            pd.DataFrame: Scorecard Geral unificado ordenado pelo modelo de maior
            retorno líquido[cite: 20].
        """
        logging.info(
            "Consolidando métricas técnicas, financeiras e explicativas no Scorecard"
            "Geral..."
        )

        # Executa a junção relacional (INNER JOIN) entre as métricas e o impacto
        # contábil pelo nome do 'Modelo'[cite: 20].
        scorecard_integrado = pd.merge(
            scorecard_tecnico,
            leaderboard_financeiro,
            on="Modelo",
            how="inner",
        )

        # Extrai a variável de maior peso causal apurada no Pilar 3 via SHAP[cite: 18,
        # 20].
        tabela_xai = laudo_explicabilidade.get("tabela_importancia_global")
        atributo_dominante = (
            str(tabela_xai.iloc[0]["Atributo_Negocio"])
            if isinstance(tabela_xai, pd.DataFrame) and not tabela_xai.empty
            else "N/A"
        )
        valor_base = float(laudo_explicabilidade.get("valor_base_populacional", 0.0))

        # Enriquece o DataFrame com as colunas contextuais da explicabilidade[cite: 18,
        # 20].
        scorecard_integrado["Variavel_Dominante_XAI"] = atributo_dominante
        scorecard_integrado["Baseline_Risco_Populacional"] = valor_base

        # Retorna o DataFrame completo ordenado decrescentemente pelo saldo contábil
        # líquido em reais[cite: 20].
        return scorecard_integrado.sort_values(
            by="Resultado_Liquido_R$", ascending=False
        ).reset_index(drop=True)
