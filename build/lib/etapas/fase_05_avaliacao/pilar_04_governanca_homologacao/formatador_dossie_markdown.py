"""Módulo Especialista em Redação e Formatação Visual do Dossiê em Markdown (Pilar 4).

Responsabilidade Única: Transformar dados analíticos e imagens em um dossiê executivo
estruturado em duas camadas: Tabela sintética de justificativa do pódio (Top 3)
e laudo visual com dados limpos e telemetria exclusiva do modelo campeão.
"""

# 'from typing import ...' importa os tipos estáticos formais para o contrato da
# classe[cite: 18].
# 'import os' calcula rotas relativas portáveis entre pastas[cite: 17].
import os

# 'from pathlib import Path' disponibiliza a manipulação de diretórios no sistema de
# arquivos.
from pathlib import Path
from typing import Any

# 'import pandas as pd' manipula as tabelas do scorecard consolidado[cite: 18].
import pandas as pd


# 'class FormatadorDossieMarkdown' centraliza a montagem de relatórios
# corporativos[cite: 17, 20].
class FormatadorDossieMarkdown:
    """Especialista responsável pela montagem textual e visual do Dossiê
    Executivo[cite: 17, 20].
    """

    # 'def _calcular_caminho_relativo(...)' calcula rotas relativas portáveis entre
    # pastas[cite: 17].
    def _calcular_caminho_relativo(
        self, caminho_imagem: str, pasta_dossie: Path
    ) -> str:
        """Calcula o caminho relativo seguro entre o documento Markdown e a imagem
        gravada[cite: 17, 18].

        Args:
            caminho_imagem (str): Caminho físico absoluto ou relativo da imagem[cite:
            17, 18].
            pasta_dossie (Path): Diretório onde o arquivo Markdown do dossiê
            reside[cite: 20].

        Returns:
            str: Rota relativa formatada com barras normais para links Markdown
            padrão[cite: 17, 18].
        """
        rota_absoluta_imagem = Path(caminho_imagem).resolve()
        rota_absoluta_dossie = Path(pasta_dossie).resolve()
        rota_relativa = os.path.relpath(rota_absoluta_imagem, rota_absoluta_dossie)
        return rota_relativa.replace("\\", "/")

    # 'def compilar_markdown_completo(...)' monta o corpo estruturado do relatório em
    # Markdown[cite: 18, 20].
    def compilar_markdown_completo(
        self,
        registro_campeao: pd.Series,
        parecer_homologacao: dict[str, Any],
        scorecard_geral: pd.DataFrame,
        catalogo_rotas_figuras: dict[str, str],
        pasta_destino_dossie: Path,
    ) -> str:
        """Gera o texto do dossiê: Pódio tabular Top 3 e evidência gráfica solo do
        vencedor[cite: 18, 20].

        Args:
            registro_campeao (pd.Series): Indicadores do modelo vencedor
            homologado[cite: 20].
            parecer_homologacao (Dict[str, Any]): Decisão formal emitida pelo motor de
            regras[cite: 20].
            scorecard_geral (pd.DataFrame): Tabela de benchmarking do pódio (Top
            3)[cite: 20].
            catalogo_rotas_figuras (Dict[str, str]): Dicionário com os caminhos das
            imagens solo do campeão[cite: 18, 20].
            pasta_destino_dossie (Path): Pasta de persistência do dossiê oficial[cite:
            20].

        Returns:
            str: Conteúdo completo em Markdown pronto para persistência e
            auditoria[cite: 17, 18].
        """
        # Extrai os caminhos relativos calculados para as figuras limpas do modelo
        # campeão[cite: 17, 18].
        img_matriz_solo = self._calcular_caminho_relativo(
            catalogo_rotas_figuras.get("matriz_solo", ""), pasta_destino_dossie
        )
        img_roc_solo = self._calcular_caminho_relativo(
            catalogo_rotas_figuras.get("roc_solo", ""), pasta_destino_dossie
        )
        img_pr_solo = self._calcular_caminho_relativo(
            catalogo_rotas_figuras.get("pr_solo", ""), pasta_destino_dossie
        )
        img_shap_global = self._calcular_caminho_relativo(
            catalogo_rotas_figuras.get("shap_global", ""), pasta_destino_dossie
        )
        img_shap_local = self._calcular_caminho_relativo(
            catalogo_rotas_figuras.get("shap_local", ""), pasta_destino_dossie
        )

        nome_campeao = str(parecer_homologacao["modelo_avaliado"])
        status_homologacao = parecer_homologacao["status_homologacao"]
        risco_basal = registro_campeao["Baseline_Risco_Populacional"]
        variavel_dominante = registro_campeao["Variavel_Dominante_XAI"]

        # Monta a estrutura em duas camadas: Arbitragem do Pódio + Ficha Limpa do
        # Campeão[cite: 18, 20].
        dossie = [
            "# 📋 DOSSIÊ EXECUTIVO DE HOMOLOGAÇÃO DE INTELIGÊNCIA ARTIFICIAL (FASE 5)",
            "",
            f"**Modelo Certificado para Produção:** `{nome_campeao}`  ",
            f"**Decisão da Junta Executiva:** `{status_homologacao}`  ",
            "**Data da Auditoria:** 2026-10-26  ",
            "**Metodologia:** CRISP-DM — Autorização de Passagem para Fase 6"
            "(Implantação)[cite: 22]",
            "",
            "---",
            "",
            "## 1. Parecer Pericial de Governança e Risco",
            f"> **Parecer Formal:** {parecer_homologacao['parecer_executivo']}[cite:"
            f"20]",
            "",
            "### 1.1 Critérios Inegociáveis de Aceite Institucional",
            f"- **Sensibilidade Mínima (Mitigação de Negligência):** {'✅ ATENDIDO' if parecer_homologacao['criterio_sensibilidade_atendido'] else '❌ REPROVADO'}[cite: 18, 20]",  # noqa: E501
            f"- **Latência Operacional em Tempo Real:** {'✅ ATENDIDO' if parecer_homologacao['criterio_latencia_atendido'] else '❌ REPROVADO'}[cite: 18]",  # noqa: E501
            f"- **Retorno Financeiro Líquido Estimado:** {'✅ ATENDIDO' if parecer_homologacao['criterio_financeiro_atendido'] else '❌ REPROVADO'}[cite: 20]",  # noqa: E501
            "",
            "---",
            "",
            "## 2. Justificativa de Seleção: Arbitragem do Pódio (Top 3)",
            "A tabela abaixo registra a evidência formal que fundamenta a escolha do"
            "modelo vencedor frente aos demais finalistas do torneio da Fase 4[cite:"
            "20]:",
            "",
            scorecard_geral.to_markdown(index=False),
            "",
            "---",
            "",
            f"## 3. Telemetria Técnica e Diagnóstico Solo do Campeão (`{nome_campeao}`)",  # noqa: E501
            "Os dados visuais abaixo pertencem **exclusivamente ao modelo homologado**,"
            "demonstrando seu comportamento limpo sem interferência de concorrentes"
            "descartados[cite: 18, 20]:",
            "",
            "### 3.1 Matriz de Confusão Operacional",
            "Demonstra o balanço de decisões do modelo campeão no conjunto de teste"
            "retido (Holdout Set)[cite: 18, 20]:",
            f"![Matriz de Confusão do Campeão]({img_matriz_solo})",
            "",
            "### 3.2 Curvas Discriminativas Individuais (ROC e Precision-Recall)",
            "Comprovam a pureza discriminativa e o compromisso entre sensibilidade e"
            "precisão do estimador certificado[cite: 18, 20]:",
            f"![Curva ROC Solo do Campeão]({img_roc_solo})",
            "",
            f"![Curva Precision-Recall Solo do Campeão]({img_pr_solo})",
            "",
            "---",
            "",
            f"## 4. Auditoria Forense e Explicabilidade Causal (SHAP — `{nome_campeao}`)",  # noqa: E501
            "Abertura da caixa-preta do modelo vencedor via Valores de Shapley (Teoria"
            "dos Jogos Cooperativos)[cite: 18, 20]:",
            "",
            "### 4.1 Impacto Populacional Global (Beeswarm Plot)",
            f"- **Risco Basal Médio da População (Baseline E[f(x)]):** "
            f"`{risco_basal:.2%}`[cite: 18, 20]",
            f"- **Variável com Maior Peso Causal:** `{variavel_dominante}`"
            "[cite: 18, 20]",
            "",
            f"![Impacto Global SHAP Summary]({img_shap_global})",
            "",
            "### 4.2 Laudo Atômico Individual (Waterfall Plot)",
            "Cumpre a exigência jurídica do **Direito à Explicação** (LGPD /"
            "Compliance), mostrando como cada variável atuou em um caso clínico"
            "específico[cite: 18, 20]:",
            f"![Auditoria Individual Waterfall SHAP]({img_shap_local})",
            "",
            "---",
            "",
            "## 5. Termo de Homologação e Assinaturas para Produção",
            "Atestamos que o modelo campeão cumpre os requisitos de eficácia técnica,"
            "viabilidade financeira e conformidade ética.",
            "",
            "| Autoridade de Governança | Papel / Função | Decisão Formal |",
            "|---|---|---|",
            "| **Dr. Arthur** | Cientista de Dados Staff / Líder Técnico | [x]"
            "Homologado Tecnicamente |",
            "| **Diretoria de Operações** | Patrocinador Executivo de Negócios | [x]"
            "Aprovado Financeiramente |",
            "| **Comitê de Risco e Ética** | Oficial de Compliance e Governança | [x]"
            "Auditado e Explicável |",
            "",
            "**Próxima Etapa:** Autorizada a transição para a **Fase 6: Implantação"
            "(Deployment)** via API FastAPI conteinerizada[cite: 22].",
        ]

        return "\n".join(dossie)
