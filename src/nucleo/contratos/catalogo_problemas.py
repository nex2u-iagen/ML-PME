"""Módulo do Catálogo de Problemas de Negócio (Núcleo de Contratos).

Responsabilidade Única: Fornecer os 15 problemas de negócio pré-desenhados que a
plataforma resolve com o mesmo motor CRISP-DM. Cada entrada é um template completo
do :class:`ContratoProblema` que o frontend oferece ao humano como ponto de partida,
reduzindo o esforço de declaração da pergunta e acelerando o primeiro resultado.

O catálogo cobre as quatro famílias de tarefa suportadas (classificação, regressão,
agrupamento e detecção de anomalias) sobre as entidades canônicas do ERP.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.
import logging

# 'from typing' oferece anotações de tipagem estática para coleções.
from typing import Dict, List, Optional

# Importa as estruturas do contrato de problema que definem o formato de cada template.
from src.nucleo.contratos.contrato_problema import (
    AgregacaoABT,
    ContratoProblema,
    CustosNegocio,
    DefinicaoAlvo,
    FuncaoAgregacao,
    JuncaoReceita,
    ReceitaABT,
    TipoTarefa,
)


def _agregacao(
    nome: str,
    funcao: FuncaoAgregacao,
    coluna: Optional[str] = None,
    expressao_sql: Optional[str] = None,
) -> AgregacaoABT:
    """Atalho interno para construir agregações de forma enxuta e legível no catálogo."""
    return AgregacaoABT(nome=nome, funcao=funcao, coluna=coluna, expressao_sql=expressao_sql)


def _juncao_vendas() -> JuncaoReceita:
    """Atalho que descreve a ligação entre a venda e o destinatário (cliente) da NFe."""
    return JuncaoReceita(
        entidade="vendas_recebedor",
        chave_base="id_nfe",
        chave_join="id_nfe",
        tipo="left",
        colunas=["id_cliente", "nome_entidade", "uf_cliente", "cidade_cliente"],
    )


def _juncao_vendas_data() -> JuncaoReceita:
    """Atalho que descreve a ligação entre a venda e o registro que carrega a data.

    A entidade canônica cobre tanto o histórico de eventos da NFe quanto a
    transmissão para a SEFAZ — o resolvedor escolhe a primeira que possua dados.
    """
    return JuncaoReceita(
        entidade="vendas_transmissao",
        chave_base="id_nfe",
        chave_join="id_nfe",
        tipo="left",
        colunas=["data_emissao"],
    )


def _juncao_vendas_itens() -> JuncaoReceita:
    """Atalho que descreve a ligação entre a venda e os itens faturados (produto, qtd, valor)."""
    return JuncaoReceita(
        entidade="vendas_itens",
        chave_base="id_nfe_detalhe",
        chave_join="id_nfe_detalhe",
        tipo="left",
        colunas=["codigo_sku", "descricao_item", "quantidade_vendida", "valor_unitario"],
    )


# 'CATALOGO_PROBLEMAS' é a fonte única da verdade dos problemas suportados pela plataforma.
CATALOGO_PROBLEMAS: List[ContratoProblema] = [
    # ----------------------------------------------------------------------------------
    # FAMÍLIA 1 — CLASSIFICAÇÃO SUPERVISIONADA (5 problemas)
    # ----------------------------------------------------------------------------------
    ContratoProblema(
        id="inadimplencia_clientes",
        nome="Inadimplência de Clientes",
        pergunta_negocio="Quais clientes apresentam risco de inadimplência acima de 30 dias?",
        tipo_tarefa=TipoTarefa.CLASSIFICACAO,
        grao_analise="cliente",
        metrica_otimizacao="f1",
        receita=ReceitaABT(
            entidade_base="contas_receber",
            chave_grupo="id_cliente",
            agregacoes=[
                _agregacao("volume_total_recebido", FuncaoAgregacao.SUM, "valor"),
                _agregacao("ticket_medio_titulo", FuncaoAgregacao.AVG, "valor"),
                _agregacao("total_titulos_emitidos", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao(
                    "maximo_dias_atraso_historico",
                    FuncaoAgregacao.MAX,
                    expressao_sql=(
                        "MAX(CASE WHEN data_pagamento IS NOT NULL AND data_vencimento IS NOT NULL "
                        "THEN (data_pagamento - data_vencimento) "
                        "WHEN data_vencimento IS NOT NULL THEN (CURRENT_DATE - data_vencimento) "
                        "ELSE 0 END)"
                    ),
                ),
            ],
            colunas_diretas=["uf_cliente", "cidade_cliente"],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "MAX(CASE WHEN data_vencimento IS NOT NULL "
                "AND (CURRENT_DATE - data_vencimento) > 30 "
                "AND data_pagamento IS NULL THEN 1 ELSE 0 END)"
            ),
        ),
        custos=CustosNegocio(falso_negativo=12000, falso_positivo=600, verdadeiro_positivo=4000),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="churn_clientes",
        nome="Churn de Clientes",
        pergunta_negocio="Quais clientes estão prestes a parar de comprar (180 dias sem pedido)?",
        tipo_tarefa=TipoTarefa.CLASSIFICACAO,
        grao_analise="cliente",
        metrica_otimizacao="f1",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_cliente",
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao("total_compras_historicas", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao("valor_total_comprado", FuncaoAgregacao.SUM, "valor"),
                _agregacao("ticket_medio_historico", FuncaoAgregacao.AVG, "valor"),
                _agregacao(
                    "dias_sem_comprar",
                    FuncaoAgregacao.MAX,
                    expressao_sql=(
                        "MAX(CURRENT_DATE - TRY_CAST(data_emissao AS DATE))"
                    ),
                ),
            ],
            colunas_diretas=["uf_cliente"],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "MAX(CASE WHEN CURRENT_DATE - TRY_CAST(data_emissao AS DATE) > 180 THEN 1 ELSE 0 END)"
            ),
        ),
        custos=CustosNegocio(falso_negativo=2500, falso_positivo=150, verdadeiro_positivo=1800),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="concentracao_receita",
        nome="Concentração de Receita",
        pergunta_negocio="Quais clientes concentram risco de caixa por depender de poucos pedidos?",
        tipo_tarefa=TipoTarefa.CLASSIFICACAO,
        grao_analise="cliente",
        metrica_otimizacao="f1",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_cliente",
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao("receita_total_cliente", FuncaoAgregacao.SUM, "valor"),
                _agregacao("numero_vendas_cliente", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao(
                    "valor_maximo_venda",
                    FuncaoAgregacao.MAX,
                    "valor",
                ),
            ],
            colunas_diretas=["uf_cliente"],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "CASE WHEN MAX(valor_item) > 0.5 * SUM(valor_item) THEN 1 ELSE 0 END"
            ),
        ),
        custos=CustosNegocio(falso_negativo=9000, falso_positivo=400, verdadeiro_positivo=3000),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="curva_abc_produtos",
        nome="Curva ABC de Produtos",
        pergunta_negocio="Quais produtos são de alta relevância (curva A) e quais podem ser descontinuados?",
        tipo_tarefa=TipoTarefa.CLASSIFICACAO,
        grao_analise="produto",
        metrica_otimizacao="f1",
        receita=ReceitaABT(
            entidade_base="estoque",
            chave_grupo="codigo_sku",
            agregacoes=[
                _agregacao(
                    "saldo_atual_estoque",
                    FuncaoAgregacao.SUM,
                    expressao_sql="SUM(quantidade_entrada) - SUM(quantidade_saida)",
                ),
                _agregacao("quantidade_entrada_total", FuncaoAgregacao.SUM, "quantidade_entrada"),
                _agregacao("quantidade_saida_total", FuncaoAgregacao.SUM, "quantidade_saida"),
                _agregacao("numero_movimentacoes", FuncaoAgregacao.COUNT, "id_transacao"),
            ],
            colunas_diretas=["descricao_item"],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "CASE WHEN PERCENT_RANK() OVER (ORDER BY SUM(quantidade_saida)) >= 0.8 "
                "THEN 1 ELSE 0 END"
            ),
        ),
        custos=CustosNegocio(falso_negativo=5000, falso_positivo=300, verdadeiro_positivo=3500),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="aging_titulos",
        nome="Risco de Aging de Títulos",
        pergunta_negocio="Quais títulos a receber têm alto risco de não serem recebidos?",
        tipo_tarefa=TipoTarefa.CLASSIFICACAO,
        grao_analise="titulo",
        metrica_otimizacao="f1",
        receita=ReceitaABT(
            entidade_base="contas_receber",
            chave_grupo="id_transacao",
            agregacoes=[
                _agregacao("valor_titulo", FuncaoAgregacao.MAX, "valor"),
                _agregacao(
                    "dias_de_atraso_titulo",
                    FuncaoAgregacao.MAX,
                    expressao_sql=(
                        "MAX(CASE WHEN data_vencimento IS NOT NULL "
                        "THEN (CURRENT_DATE - data_vencimento) ELSE 0 END)"
                    ),
                ),
            ],
            colunas_diretas=["status_cobranca"],
        ),        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "MAX(CASE WHEN data_vencimento IS NOT NULL "
                "AND (CURRENT_DATE - data_vencimento) > 30 "
                "AND data_pagamento IS NULL THEN 1 ELSE 0 END)"
            ),
        ),
        custos=CustosNegocio(falso_negativo=8000, falso_positivo=500, verdadeiro_positivo=3500),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    # ----------------------------------------------------------------------------------
    # FAMÍLIA 2 — REGRESSÃO SUPERVISIONADA (5 problemas)
    # ----------------------------------------------------------------------------------
    ContratoProblema(
        id="previsao_faturamento",
        nome="Previsão de Faturamento",
        pergunta_negocio="Quanto faturaremos no próximo mês?",
        tipo_tarefa=TipoTarefa.REGRESSAO,
        grao_analise="mes",
        metrica_otimizacao="r2",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_transacao",
            granularidade_temporal="mes",
            coluna_data="data_emissao",
            deslocamento_alvo_periodos=1,
            juncoes=[_juncao_vendas_data()],
            agregacoes=[
                _agregacao("faturamento_periodo", FuncaoAgregacao.SUM, "valor"),
                _agregacao("numero_vendas_periodo", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao(
                    "ticket_medio_periodo",
                    FuncaoAgregacao.AVG,
                    "valor",
                ),
            ],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql="SUM(valor_item)",
            tipo_dado="DOUBLE",
        ),
        custos=None,
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="previsao_volume_vendas",
        nome="Previsão de Volume de Vendas",
        pergunta_negocio="Quantas unidades venderemos no próximo período?",
        tipo_tarefa=TipoTarefa.REGRESSAO,
        grao_analise="mes",
        metrica_otimizacao="r2",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_transacao",
            granularidade_temporal="mes",
            coluna_data="data_emissao",
            deslocamento_alvo_periodos=1,
            juncoes=[_juncao_vendas_data()],
            agregacoes=[
                _agregacao("faturamento_periodo", FuncaoAgregacao.SUM, "valor"),
                _agregacao("numero_vendas_periodo", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao(
                    "ticket_medio_periodo",
                    FuncaoAgregacao.AVG,
                    "valor",
                ),
            ],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql='COUNT("id_transacao")',
            tipo_dado="DOUBLE",
        ),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="previsao_demanda_produto",
        nome="Previsão de Demanda por Produto",
        pergunta_negocio="Quanto de cada produto precisamos repor no próximo ciclo de compra?",
        tipo_tarefa=TipoTarefa.REGRESSAO,
        grao_analise="produto",
        metrica_otimizacao="r2",
        receita=ReceitaABT(
            entidade_base="estoque",
            chave_grupo="codigo_sku",
            granularidade_temporal="mes",
            coluna_data="data_emissao",
            dimensoes=["codigo_sku"],
            deslocamento_alvo_periodos=1,
            agregacoes=[
                _agregacao("quantidade_saida_periodo", FuncaoAgregacao.SUM, "quantidade_saida"),
                _agregacao("quantidade_entrada_periodo", FuncaoAgregacao.SUM, "quantidade_entrada"),
                _agregacao("numero_movimentacoes", FuncaoAgregacao.COUNT, "id_transacao"),
            ],
            colunas_diretas=["descricao_item"],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql="SUM(quantidade_saida)",
            tipo_dado="DOUBLE",
        ),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="previsao_ticket_medio",
        nome="Previsão de Ticket Médio",
        pergunta_negocio="Qual será o ticket médio futuro de cada cliente?",
        tipo_tarefa=TipoTarefa.REGRESSAO,
        grao_analise="cliente",
        metrica_otimizacao="r2",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_cliente",
            granularidade_temporal="mes",
            coluna_data="data_emissao",
            dimensoes=["id_cliente"],
            deslocamento_alvo_periodos=1,
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao("ticket_medio_historico", FuncaoAgregacao.AVG, "valor"),
                _agregacao("total_compras_cliente", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao("valor_total_cliente", FuncaoAgregacao.SUM, "valor"),
                _agregacao(
                    "dias_sem_comprar",
                    FuncaoAgregacao.MAX,
                    expressao_sql="MAX(CURRENT_DATE - TRY_CAST(data_emissao AS DATE))",
                ),
            ],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql="AVG(valor_item)",
            tipo_dado="DOUBLE",
        ),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="previsao_dias_atraso",
        nome="Previsão de Dias de Atraso",
        pergunta_negocio="Quantos dias de atraso de pagamento devemos esperar por cliente?",
        tipo_tarefa=TipoTarefa.REGRESSAO,
        grao_analise="cliente",
        metrica_otimizacao="r2",
        receita=ReceitaABT(
            entidade_base="contas_receber",
            chave_grupo="id_cliente",
            granularidade_temporal="mes",
            coluna_data="data_vencimento",
            dimensoes=["id_cliente"],
            deslocamento_alvo_periodos=1,
            agregacoes=[
                _agregacao(
                    "atraso_medio_historico",
                    FuncaoAgregacao.AVG,
                    expressao_sql=(
                        "AVG(CASE WHEN data_pagamento IS NOT NULL AND data_vencimento IS NOT NULL "
                        "THEN (data_pagamento - data_vencimento) ELSE 0 END)"
                    ),
                ),
                _agregacao("volume_total_recebido", FuncaoAgregacao.SUM, "valor"),
                _agregacao("total_titulos_emitidos", FuncaoAgregacao.COUNT, "id_transacao"),
            ],
        ),
        alvo=DefinicaoAlvo(
            tipo="regra_sql",
            expressao_sql=(
                "AVG(CASE WHEN data_pagamento IS NOT NULL AND data_vencimento IS NOT NULL "
                "THEN (data_pagamento - data_vencimento) ELSE 0 END)"
            ),
            tipo_dado="DOUBLE",
        ),
        parametros={"semente": 42, "numero_particoes": 5},
    ),
    # ----------------------------------------------------------------------------------
    # FAMÍLIA 3 — AGRUPAMENTO NÃO SUPERVISIONADO (3 problemas)
    # ----------------------------------------------------------------------------------
    ContratoProblema(
        id="clustering_clientes",
        nome="Clustering de Clientes",
        pergunta_negocio="Que grupos de clientes distintos existem por comportamento de compra?",
        tipo_tarefa=TipoTarefa.AGRUPAMENTO,
        grao_analise="cliente",
        metrica_otimizacao="silhueta",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_cliente",
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao("valor_total_cliente", FuncaoAgregacao.SUM, "valor"),
                _agregacao("numero_compras_cliente", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao("ticket_medio_cliente", FuncaoAgregacao.AVG, "valor"),
                _agregacao(
                    "dias_sem_comprar",
                    FuncaoAgregacao.MAX,
                    expressao_sql="MAX(CURRENT_DATE - TRY_CAST(data_emissao AS DATE))",
                ),
            ],
            colunas_diretas=["uf_cliente"],
        ),
        alvo=None,
        parametros={"semente": 42, "numero_grupos": 4, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="segmentacao_rfm",
        nome="Segmentação RFM",
        pergunta_negocio="Como segmentar a base por Recência, Frequência e Valor Monetário?",
        tipo_tarefa=TipoTarefa.AGRUPAMENTO,
        grao_analise="cliente",
        metrica_otimizacao="silhueta",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_cliente",
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao(
                    "recencia_dias",
                    FuncaoAgregacao.MAX,
                    expressao_sql="MAX(CURRENT_DATE - TRY_CAST(data_emissao AS DATE))",
                ),
                _agregacao("frequencia_compras", FuncaoAgregacao.COUNT, "id_transacao"),
                _agregacao("valor_monetario", FuncaoAgregacao.SUM, "valor"),
                _agregacao("ticket_medio_cliente", FuncaoAgregacao.AVG, "valor"),
            ],
        ),
        alvo=None,
        parametros={"semente": 42, "numero_grupos": 4, "numero_particoes": 5},
    ),
    ContratoProblema(
        id="clustering_produtos",
        nome="Clustering de Produtos",
        pergunta_negocio="Que grupos de produtos compartilham curva de venda e giro?",
        tipo_tarefa=TipoTarefa.AGRUPAMENTO,
        grao_analise="produto",
        metrica_otimizacao="silhueta",
        receita=ReceitaABT(
            entidade_base="estoque",
            chave_grupo="codigo_sku",
            agregacoes=[
                _agregacao(
                    "saldo_atual_estoque",
                    FuncaoAgregacao.SUM,
                    expressao_sql="SUM(quantidade_entrada) - SUM(quantidade_saida)",
                ),
                _agregacao("quantidade_entrada_total", FuncaoAgregacao.SUM, "quantidade_entrada"),
                _agregacao("quantidade_saida_total", FuncaoAgregacao.SUM, "quantidade_saida"),
                _agregacao("numero_movimentacoes", FuncaoAgregacao.COUNT, "id_transacao"),
            ],
            colunas_diretas=["descricao_item"],
        ),
        alvo=None,
        parametros={"semente": 42, "numero_grupos": 4, "numero_particoes": 5},
    ),
    # ----------------------------------------------------------------------------------
    # FAMÍLIA 4 — DETECÇÃO DE ANOMALIAS (2 problemas)
    # ----------------------------------------------------------------------------------
    ContratoProblema(
        id="anomalias_vendas",
        nome="Anomalias em Transações de Venda",
        pergunta_negocio="Quais transações de venda têm padrão atípico e merecem auditoria?",
        tipo_tarefa=TipoTarefa.DETECCAO_ANOMALIAS,
        grao_analise="transacao",
        metrica_otimizacao="auc_anomalia",
        receita=ReceitaABT(
            entidade_base="vendas",
            chave_grupo="id_transacao",
            juncoes=[_juncao_vendas(), _juncao_vendas_data()],
            agregacoes=[
                _agregacao("valor_transacao", FuncaoAgregacao.MAX, "valor"),
                _agregacao(
                    "ticket_medio_transacao",
                    FuncaoAgregacao.AVG,
                    expressao_sql="AVG(valor_item)",
                ),
                _agregacao(
                    "dias_desde_emissao",
                    FuncaoAgregacao.MAX,
                    expressao_sql="MAX(CURRENT_DATE - TRY_CAST(data_emissao AS DATE))",
                ),
            ],
            colunas_diretas=["id_cliente", "uf_cliente", "cidade_cliente"],
        ),
        alvo=None,
        parametros={"semente": 42, "numero_particoes": 5, "fator_contaminacao": 0.05},
    ),
    ContratoProblema(
        id="anomalias_estoque",
        nome="Anomalias de Estoque",
        pergunta_negocio="Quais itens de estoque estão com saldo atípico (ruptura ou sobras)?",
        tipo_tarefa=TipoTarefa.DETECCAO_ANOMALIAS,
        grao_analise="produto",
        metrica_otimizacao="auc_anomalia",
        receita=ReceitaABT(
            entidade_base="estoque",
            chave_grupo="codigo_sku",
            agregacoes=[
                _agregacao(
                    "saldo_atual_estoque",
                    FuncaoAgregacao.SUM,
                    expressao_sql="SUM(quantidade_entrada) - SUM(quantidade_saida)",
                ),
                _agregacao("quantidade_entrada_total", FuncaoAgregacao.SUM, "quantidade_entrada"),
                _agregacao("quantidade_saida_total", FuncaoAgregacao.SUM, "quantidade_saida"),
                _agregacao("numero_movimentacoes", FuncaoAgregacao.COUNT, "id_transacao"),
            ],
            colunas_diretas=["descricao_item"],
        ),
        alvo=None,
        parametros={"semente": 42, "numero_particoes": 5, "fator_contaminacao": 0.05},
    ),
]


class CatalogoProblemas:
    """Fachada de consulta do catálogo de problemas de negócio disponíveis."""

    @staticmethod
    def listar() -> List[ContratoProblema]:
        """Retorna todos os contratos template disponíveis no catálogo."""
        return list(CATALOGO_PROBLEMAS)

    @staticmethod
    def obter(id_problema: str) -> ContratoProblema:
        """Recupera um template pelo identificador único.

        Args:
            id_problema (str): Identificador snake_case do problema.

        Returns:
            ContratoProblema: Cópia do template correspondente.

        Raises:
            KeyError: Quando nenhum template possui o identificador informado.
        """
        alvo = next((p for p in CATALOGO_PROBLEMAS if p.id == id_problema), None)
        if alvo is None:
            disponiveis = ", ".join(p.id for p in CATALOGO_PROBLEMAS)
            raise KeyError(f"Problema '{id_problema}' não existe no catálogo. Disponíveis: {disponiveis}")
        return alvo.model_copy(deep=True)

    @staticmethod
    def filtrar_por_tarefa(tipo_tarefa: TipoTarefa) -> List[ContratoProblema]:
        """Filtra os templates disponíveis para uma família de tarefa específica.

        Args:
            tipo_tarefa (TipoTarefa): Família de aprendizado desejada.

        Returns:
            List[ContratoProblema]: Subconjunto de contratos compatíveis.
        """
        return [p for p in CATALOGO_PROBLEMAS if p.tipo_tarefa is tipo_tarefa]

    @staticmethod
    def resumo_para_frontend() -> List[Dict[str, object]]:
        """Produz a listagem compacta consumida pela API e renderizada no Streamlit."""
        return [
            {
                "id": problema.id,
                "nome": problema.nome,
                "pergunta_negocio": problema.pergunta_negocio,
                "tipo_tarefa": problema.tipo_tarefa.value,
                "grao_analise": problema.grao_analise,
                "metrica_otimizacao": problema.metrica_effective,
                "entidade_base": problema.receita.entidade_base,
                "features": [agregacao.nome for agregacao in problema.receita.agregacoes],
            }
            for problema in CATALOGO_PROBLEMAS
        ]


logging.info(
    "Catálogo de problemas carregado com %d templates (%d classificação, %d regressão, "
    "%d agrupamento, %d anomalias).",
    len(CATALOGO_PROBLEMAS),
    len(CatalogoProblemas.filtrar_por_tarefa(TipoTarefa.CLASSIFICACAO)),
    len(CatalogoProblemas.filtrar_por_tarefa(TipoTarefa.REGRESSAO)),
    len(CatalogoProblemas.filtrar_por_tarefa(TipoTarefa.AGRUPAMENTO)),
    len(CatalogoProblemas.filtrar_por_tarefa(TipoTarefa.DETECCAO_ANOMALIAS)),
)
