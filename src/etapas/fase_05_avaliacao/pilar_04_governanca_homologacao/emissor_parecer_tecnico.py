"""Módulo Especialista em Aplicação de Regras de Aceite e Governança (Pilar 4).

Responsabilidade Única: Avaliar o modelo campeão contra as réguas inegociáveis
de tolerância a risco (sensibilidade mínima, latência máxima e resultado financeiro
positivo),
emitindo o parecer pericial formal de homologação para produção[cite: 18, 20].
"""

# 'from typing import ...' provê suporte a tipagem estática rigorosa[cite: 18].
# 'import logging' gerencia as mensagens de auditoria técnica no console.
import logging
from typing import Any

# 'import pandas as pd' fornece manipulação de séries tabulares para leitura de
# métricas[cite: 18].
import pandas as pd


# 'class EmissorParecerTecnico' isola o motor de regras de negócio e governança de
# IA[cite: 20].
class EmissorParecerTecnico:
    """Motor de avaliação de conformidade que emite a decisão formal de
    Sign-off[cite: 20].
    """

    # 'def __init__(...)' parametriza os critérios mínimos inegociáveis de aceite
    # institucional[cite: 20].
    def __init__(
        self,
        sensibilidade_minima: float = 0.70,
        latencia_maxima_ms: float = 10.0,
        exigir_saldo_positivo: bool = True,
    ) -> None:
        """Inicializa os limites de governança estabelecidos pelo comitê de risco[cite:
        20].

        Args:
            sensibilidade_minima (float): Limiar mínimo de Recall para mitigar
            negligência[cite: 18, 20].
            latencia_maxima_ms (float): Limite superior aceitável de tempo de resposta
            em ms[cite: 18].
            exigir_saldo_positivo (bool): Obrigatoriedade de retorno contábil líquido
            maior que zero[cite: 20].
        """
        self.sensibilidade_minima = sensibilidade_minima
        self.latencia_maxima_ms = latencia_maxima_ms
        self.exigir_saldo_positivo = exigir_saldo_positivo

    # 'def avaliar_modelo_campeao(...)' submete o primeiro colocado à régua de
    # aceite[cite: 20].
    def avaliar_modelo_campeao(self, registro_campeao: pd.Series) -> dict[str, Any]:
        """Aplica os critérios de conformidade e redige o parecer técnico formal[cite:
        20].

        Args:
            registro_campeao (pd.Series): Linha número 1 do Scorecard Geral
            Integrado[cite: 20].

        Returns:
            Dict[str, Any]: Laudo pericial com status ('HOMOLOGADO' ou 'REJEITADO') e
            justificativas[cite: 20].
        """
        nome_modelo = str(registro_campeao["Modelo"])
        recall = float(registro_campeao["Sensibilidade_Recall"])
        latencia = float(registro_campeao["Latencia_Unit_ms"])
        saldo_liquido = float(registro_campeao["Resultado_Liquido_R$"])

        logging.info(
            "Auditando conformidade e critérios de aceite para: %s...", nome_modelo
        )

        # Avaliação das três condições inegociáveis de homologação[cite: 18, 20].
        aprovado_sensibilidade = recall >= self.sensibilidade_minima
        aprovado_latencia = latencia <= self.latencia_maxima_ms
        aprovado_financeiro = (
            (saldo_liquido > 0.0) if self.exigir_saldo_positivo else True
        )

        # Decisão final binária: deve cumprir todos os requisitos simultaneamente[cite:
        # 20].
        status_final = (
            "HOMOLOGADO PARA PRODUÇÃO"
            if (aprovado_sensibilidade and aprovado_latencia and aprovado_financeiro)
            else "REJEITADO PELO COMITÊ DE RISCO"
        )

        # Monta a justificativa executiva formal detalhada[cite: 20].
        parecer_descritivo = (
            f"O estimador '{nome_modelo}' obteve sensibilidade de {recall:.2%} "
            f"(mínimo: {self.sensibilidade_minima:.2%}), latência de {latencia:.4f} ms "
            f"(máximo: {self.latencia_maxima_ms:.1f} ms) e retorno líquido de "
            f"R$ {saldo_liquido:,.2f}. Modelo aprovado por todos os critérios de "
            f"governança e alinhado ao apetite a risco."
            if status_final == "HOMOLOGADO PARA PRODUÇÃO"
            else (
                f"O estimador '{nome_modelo}' violou critérios mínimos de governança ou"
                f"viabilidade financeira."
            )
        )

        return {
            "modelo_avaliado": nome_modelo,
            "status_homologacao": status_final,
            "criterio_sensibilidade_atendido": aprovado_sensibilidade,
            "criterio_latencia_atendido": aprovado_latencia,
            "criterio_financeiro_atendido": aprovado_financeiro,
            "parecer_executivo": parecer_descritivo,
        }
