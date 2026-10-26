"""Módulo de Contrato de Dados para Saída da Predição Clínica (Pilar 3 - Fase 6).

Responsabilidade Única: Estruturar a resposta oficial emitida pelo microserviço,
devolvendo a decisão binária, o escore contínuo de probabilidade, o limiar de corte,
o rótulo de severidade clínica, a versão do modelo e a latência de processamento em
milissegundos[cite: 18].
"""

# 'from pydantic import ...' importa os recursos de validação e anotação declarativa da
# saída.
from pydantic import BaseModel, Field


# 'class EsquemaRespostaPredicao' herda de 'BaseModel' para padronizar o payload JSON de
# resposta da API.
class EsquemaRespostaPredicao(BaseModel):
    """Contrato oficial de saída com a decisão preditiva e indicadores de auditoria
    de governança[cite: 18].
    """

    # Decisão final discreta (0 ou 1) calculada após o corte do limiar homologado[cite:
    # 18].
    classe_predita: int = Field(
        ...,
        description=(
            "Decisão binária da máquina (0: Sem Risco Cardiovascular Imediato, 1: Risco"
            "Crítico)."
        ),
        examples=[1],
    )

    # Rótulo em linguagem natural para leitura imediata pela equipa médica no
    # prontuário.
    diagnostico_rotulo: str = Field(
        ...,
        description="Descrição nominal em texto claro da decisão clínica emitida.",
        examples=["ALTO_RISCO_CARDIOVASCULAR"],
    )

    # Probabilidade contínua estimada P(y = 1 | X) entre 0.0 e 1.0 gerada pelo SVM
    # Calibrado[cite: 18].
    probabilidade_risco: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Escore de probabilidade calibrada de evento cardiovascular (entre 0.0 e"
            "1.0)[cite: 18]."
        ),
        examples=[0.8425],
    )

    # Limiar de corte de probabilidade utilizado para classificar a amostra como
    # risco[cite: 18].
    limiar_decisao_aplicado: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Ponto de corte ótimo probabilístico homologado para prevenção de"
            "negligência[cite: 18]."
        ),
        examples=[0.50],
    )

    # Categoria semântica de gravidade para priorização na fila de atendimento (Triage).
    grau_severidade: str = Field(
        ...,
        description=(
            "Classificação de triagem do paciente (BAIXO, MODERADO, ELEVADO ouCRÍTICO)."
        ),
        examples=["CRÍTICO"],
    )

    # Identificador semântico da versão do modelo em execução na memória RAM do
    # servidor.
    versao_modelo_producao: str = Field(
        ...,
        description=(
            "Versão e assinatura do artefato homologado em execução no microserviço."
        ),
        examples=["SVM_Calibrado_Producao_v1.0.0"],
    )

    # Tempo computacional puro de inferência medido em frações de milissegundo[cite:
    # 18].
    tempo_processamento_ms: float = Field(
        ...,
        ge=0.0,
        description=(
            "Latência computacional de inferência pura aferida em milissegundos[cite:"
            "18]."
        ),
        examples=[1.42],
    )
