"""Módulo de Contrato de Dados para Entrada de Inferência de Crédito (Pilar 3 - Fase 6).

Responsabilidade Única: Definir formalmente os atributos preditores exigidos pelo
modelo homologado na Fase 5, com tipagem estrita, limites de negócio coerentes,
descrições humanas e ordenação canônica de vetorização via Pydantic V2.
"""

# 'from pydantic' carrega os componentes centrais de validação de esquemas da biblioteca Pydantic V2.
# - 'BaseModel': classe base que transforma classes Python em esquemas com validação em tempo de execução.
# - 'Field': função declarativa que permite anexar restrições numéricas, descrições e exemplos.
from pydantic import BaseModel, Field


# 'class EsquemaEntradaCliente' herda de 'BaseModel' para atuar como o contrato oficial do corpo da requisição.
class EsquemaEntradaCliente(BaseModel):
    """Contrato formal das variáveis financeiras e cadastrais necessárias para estimativa de risco de crédito."""

    # Atributo 1: Volume financeiro total histórico faturado pelo cliente em reais (R$).
    volume_total_recebido: float = Field(
        ...,
        ge=0.0,
        description="Volume financeiro total já faturado/recebido do cliente em reais (R$).",
        examples=[12500.50],
    )

    # Atributo 2: Ticket médio histórico por título emitido.
    ticket_medio_titulo: float = Field(
        ...,
        ge=0.0,
        description="Valor monetário médio de cada duplicata ou título emitido (R$).",
        examples=[650.00],
    )

    # Atributo 3: Quantidade total de títulos de cobrança emitidos contra o cliente.
    total_titulos_emitidos: int = Field(
        ...,
        ge=1,
        description="Contagem total acumulada de títulos emitidos historicamente.",
        examples=[18],
    )

    # Atributo 4: Máximo de dias de atraso já registrado no histórico financeiro.
    maximo_dias_atraso_historico: float = Field(
        ...,
        ge=0.0,
        description="Maior quantidade de dias de atraso já registrada em liquidações passadas.",
        examples=[5.0],
    )

    # Atributo 5: Unidade Federativa de localização do cliente (Sigla do Estado).
    uf_cliente: str = Field(
        default="SP",
        min_length=2,
        max_length=2,
        description="Sigla do estado da federação do domicílio do cliente (ex: 'SP', 'MG').",
        examples=["SP"],
    )

    # Atributo 6: Município do cliente cadastrado no ERP[cite: 10].
    cidade_cliente: str = Field(
        default="Não Informada",
        description="Nome da cidade do cliente conforme registro cadastral no ERP.",
        examples=["São Paulo"],
    )

    # 'def exportar_dicionario_atributos(...)' converte os campos em formato plano para o pré-processador[cite: 10].
    def exportar_dicionario_atributos(self) -> dict[str, float | int | str]:
        """Converte as variáveis do contrato em dicionário chave-valor compatível com o ColumnTransformer[cite: 10].

        Returns:
            dict: Mapeamento dos nomes de atributos e respectivos valores validados[cite: 10].
        """
        return {
            "volume_total_recebido": float(self.volume_total_recebido),
            "ticket_medio_titulo": float(self.ticket_medio_titulo),
            "total_titulos_emitidos": int(self.total_titulos_emitidos),
            "maximo_dias_atraso_historico": float(self.maximo_dias_atraso_historico),
            "uf_cliente": str(self.uf_cliente).upper(),
            "cidade_cliente": str(self.cidade_cliente),
        }