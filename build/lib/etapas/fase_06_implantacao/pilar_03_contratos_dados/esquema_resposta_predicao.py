"""Módulo de Contrato de Dados para Saída da Predição de Crédito (Pilar 3 - Fase 6).

Responsabilidade Única: Estruturar a resposta oficial emitida pelo microserviço,
devolvendo a decisão binária, a probabilidade calibrada de calote, o limiar aplicado,
a faixa de risco, a ação prescritiva de cobrança, a versão do modelo e a latência em ms[cite: 10].
"""

# 'from pydantic import ...' importa os recursos de validação declarativa da saída da API[cite: 10].
from pydantic import BaseModel, Field


# 'class EsquemaRespostaPredicao' herda de 'BaseModel' para padronizar o payload JSON[cite: 10].
class EsquemaRespostaPredicao(BaseModel):
    """Contrato oficial de saída com a decisão preditiva e indicadores de governança financeira[cite: 10]."""

    # Decisão final discreta (0 = Em Dia, 1 = Risco Inadimplente)[cite: 10].
    classe_predita: int = Field(
        ...,
        description="Decisão binária da IA (0: Bom Pagador / Em Dia, 1: Risco de Inadimplência)[cite: 10].",
        examples=[0],
    )

    # Rótulo em linguagem natural legível pelo comitê de crédito e caixas[cite: 10].
    decisao_rotulo: str = Field(
        ...,
        description="Descrição nominal em texto claro da decisão emitida[cite: 10].",
        examples=["RISCO_INADIMPLENCIA_MITIGADO"],
    )

    # Escore de probabilidade contínua P(y=1) entre 0.0 e 1.0[cite: 10, 11].
    probabilidade_risco: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Escore de probabilidade calibrada de atraso superior a 30 dias[cite: 10, 11].",
        examples=[0.0412],
    )

    # Limiar ótimo de decisão homologado no comitê da Fase 5[cite: 10].
    limiar_decisao_aplicado: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ponto de corte ótimo de probabilidade homologado na Fase 5[cite: 10].",
        examples=[0.50],
    )

    # Faixa de classificação de crédito do cliente[cite: 10].
    faixa_risco: str = Field(
        ...,
        description="Classificação de apetite a risco (BAIXO RISCO, MÉDIO RISCO ou ALTO RISCO)[cite: 10].",
        examples=["BAIXO RISCO"],
    )

    # Ação prescritiva recomendada para a esteira operacional do supermercado[cite: 10].
    acao_recomendada: str = Field(
        ...,
        description="Diretriz prescritiva para o setor financeiro e frente de caixa[cite: 10].",
        examples=["Liberar Faturamento / Manter Crédito Automático"],
    )

    # Versão semântica oficial do modelo serializado ativo na memória[cite: 10].
    versao_modelo_producao: str = Field(
        ...,
        description="Versão e assinatura do artefato homologado em execução[cite: 10].",
        examples=["Random_Forest_Producao_v1.0.0"],
    )

    # Tempo computacional de inferência aferido em milissegundos[cite: 10].
    tempo_processamento_ms: float = Field(
        ...,
        ge=0.0,
        description="Latência computacional de inferência pura em milissegundos[cite: 10].",
        examples=[0.85],
    )