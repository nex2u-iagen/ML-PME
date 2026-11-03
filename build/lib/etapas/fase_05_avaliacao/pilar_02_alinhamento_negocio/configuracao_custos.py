"""Módulo de Configuração de Parâmetros Financeiros e Apetite a Risco (Pilar 2).

Responsabilidade Única: Encapsular e validar os custos monetários unitários
de omissão (Falso Negativo), alarme falso (Falso Positivo) e valor preservado
(Verdadeiro Positivo),
disponibilizando perfis econômicos institucionais para auditoria executiva.
"""

# 'from typing import ...' provê suporte a tipagem estática rigorosa para garantir
# interfaces previsíveis.


# 'class ConfiguracaoCustoRisco' atua como Objeto de Domínio imutável para as premissas
# de negócio.
class ConfiguracaoCustoRisco:
    """Encapsula as premissas financeiras de erro e benefício de negócio para a
    avaliação preditiva.
    """

    # 'def __init__(...)' instancia os parâmetros monetários com checagem defensiva de
    # consistência.
    def __init__(
        self,
        custo_falso_negativo: float = 12000.0,
        custo_falso_positivo: float = 600.0,
        ganho_verdadeiro_positivo: float = 4000.0,
        custo_verdadeiro_negativo: float = 0.0,
    ) -> None:
        """Inicializa as premissas financeiras unitárias em moeda corrente (R$).

        Args:
            custo_falso_negativo (float): Prejuízo da negligência por omissão (caso de
            risco liberado)[cite: 20].
            custo_falso_positivo (float): Custo operacional da inspeção por alarme
            falso[cite: 20].
            ganho_verdadeiro_positivo (float): Valor financeiro protegido pela
            intervenção assertiva[cite: 20].
            custo_verdadeiro_negativo (float): Custo basal do processamento padrão do
            caso neutro[cite: 20].
        """
        # Checagem defensiva: custos e receitas financeiras não podem assumir grandezas
        # negativas.
        if (
            custo_falso_negativo < 0
            or custo_falso_positivo < 0
            or ganho_verdadeiro_positivo < 0
        ):
            raise ValueError(
                "Os parâmetros de custos e ganhos monetários devem ser estritamente"
                "positivos!"
            )

        # Armazena a penalidade financeira da omissão/negligência (Falso Negativo)[cite:
        # 20].
        self.custo_fn = float(custo_falso_negativo)

        # Armazena o custo operacional de averiguação do alarme falso (Falso
        # Positivo)[cite: 20].
        self.custo_fp = float(custo_falso_positivo)

        # Armazena o benefício contábil gerado pela interceptação correta (Verdadeiro
        # Positivo)[cite: 20].
        self.ganho_vp = float(ganho_verdadeiro_positivo)

        # Armazena o custo basal do caso padrão legítimo (Verdadeiro Negativo)[cite:
        # 20].
        self.custo_vn = float(custo_verdadeiro_negativo)

    # '@classmethod' disponibiliza um perfil institucional padronizado focado em
    # tolerância zero à negligência[cite: 18].
    @classmethod
    def perfil_conservador_saude_fraude(cls) -> "ConfiguracaoCustoRisco":
        """Cria um perfil econômico com penalidade severa para Falsos Negativos
        (Risco Crítico).
        """
        # Relação assimétrica de 20 para 1: deixar passar um caso grave custa 20 vezes
        # mais que um alarme falso.
        return cls(
            custo_falso_negativo=15000.0,
            custo_falso_positivo=750.0,
            ganho_verdadeiro_positivo=5000.0,
            custo_verdadeiro_negativo=0.0,
        )

    # 'def exportar_resumo_premissas(...)' devolve o dicionário das taxas adotadas para
    # governança de dados.
    def exportar_resumo_premissas(self) -> dict[str, float]:
        """Exporta o resumo das premissas financeiras configuradas para inclusão em
        relatórios e auditorias[cite: 20].
        """
        return {
            "custo_unitario_falso_negativo_reais": self.custo_fn,
            "custo_unitario_falso_positivo_reais": self.custo_fp,
            "ganho_unitario_verdadeiro_positivo_reais": self.ganho_vp,
            "custo_unitario_verdadeiro_negativo_reais": self.custo_vn,
        }
