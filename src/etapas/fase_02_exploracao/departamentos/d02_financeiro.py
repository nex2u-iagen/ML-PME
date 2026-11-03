"""Módulo de Diagnóstico Exploratório do Departamento Financeiro (Fase 2.2 - CRISP-DM).

Responsabilidade Única: Auditar a saúde da tesouraria, calcular o volume e a taxa
percentual de inadimplência de títulos a receber e gerar o gráfico de distribuição
por situação de cobrança (Aging), consumindo dados reais via Adaptador Universal[cite: 5].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 5].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de caminhos e arquivos no disco[cite: 5].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para estruturas heterogêneas de saída[cite: 5].
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' importa o motor de criação e gravação de figuras gráficas[cite: 5].
import matplotlib.pyplot as plt

# 'import pandas as pd' manipula estruturas de dados tabulares, agregações e filtros em memória RAM[cite: 5].
import pandas as pd

# 'import seaborn as sns' renderiza gráficos estatísticos corporativos elegantes e padronizados[cite: 5].
import seaborn as sns

# Importação da classe base abstrata que injeta infraestrutura compartilhada e o Adaptador Universal[cite: 5].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento

# 'import datetime' fornece a data de referência para delimitar o mês corrente da carteira.
from datetime import datetime


# 'def' utilitário interno: localiza uma coluna pelo nome canônico ou variação de caixa.
def _encontrar_coluna(colunas, candidatos):
    """Devolve a primeira coluna da lista que casa com algum candidato (case-insensitive).

    Args:
        colunas (list): Cabeçalhos reais da tabela carregada.
        candidatos (list): Sinônimos aceitos para o papel da coluna.

    Returns:
        str | None: Nome real da coluna ou ``None`` quando nenhuma casa.
    """
    # Normaliza os cabeçalhos uma única vez para comparação sem caixa.
    mapeamento = {str(coluna).strip().lower(): coluna for coluna in colunas}
    for candidato in candidatos:
        if candidato.lower() in mapeamento:
            return mapeamento[candidato.lower()]
    return None


# 'class AnalisadorFinanceiro(BaseDepartamento)' especializa o diagnóstico de tesouraria por herança[cite: 5].
class AnalisadorFinanceiro(BaseDepartamento):
    """Classe responsável pelo diagnóstico de solvência, liquidez e inadimplência real do ERP[cite: 5]."""

    # 'def __init__(...)' constrói a instância do analisador financeiro registrando a pasta setorial[cite: 5].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento financeiro registrando seu nome canônico para criação de pastas[cite: 5].

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas reais do ERP (ex: mercado_vencedor/)[cite: 5].
            pasta_relatorios (Path): Diretório base de saída onde a pasta 'financeiro/' será mantida[cite: 5].
        """
        # 'super().__init__(...)' aciona o construtor da classe base registrando 'financeiro' como nome canônico[cite: 5].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="financeiro",
        )

    # 'def carregar_dados_financeiros(...)' aciona o Adaptador Universal para carregar Contas a Receber[cite: 5].
    def carregar_dados_financeiros(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal a tabela canônica de Contas a Receber reais[cite: 5].

        Returns:
            pd.DataFrame: Tabela financeira real contendo data_pedido, valor_total e status_pagamento[cite: 5].

        Raises:
            ValueError: Se o adaptador não localizar títulos a receber na base de dados do cliente[cite: 5].
        """
        # 'self.adaptador.obter_visao_financeira_receber()' busca e padroniza tabelas como 'erp_contasreceber.csv'.
        df_financeiro = self.adaptador.obter_visao_financeira_receber()

        # Validação defensiva: interrompe a execução caso a base financeira esteja indisponível ou vazia[cite: 5].
        if df_financeiro is None or df_financeiro.empty:
            logging.error("Financeiro — Falha crítica: Nenhum título a receber real localizado pelo Adaptador Universal.")
            raise ValueError("Dados financeiros reais de contas a receber não encontrados na base de dados sob perícia.")

        # 'logging.info' registra a confirmação do carregamento com a contagem exata de títulos auditados[cite: 5].
        logging.info("Financeiro — Base canônica carregada com sucesso contendo %d títulos a receber reais.", len(df_financeiro))

        # Devolve a matriz tabular canônica pronta para a apuração de solvência e risco[cite: 5].
        return df_financeiro

    # 'def calcular_taxa_inadimplencia(...)' calcula os valores monetários em atraso e a taxa percentual de calote[cite: 5].
    def calcular_taxa_inadimplencia(self, dados: pd.DataFrame) -> Dict[str, Any]:
        """Calcula o montante faturado, o volume em aberto e a taxa percentual de inadimplência da carteira[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela financeira contendo as colunas 'valor_total' e 'status_pagamento'[cite: 5].

        Returns:
            Dict[str, Any]: Indicadores consolidando faturamento, valor sob risco e taxa percentual calculada[cite: 5].
        """
        # 'dados["valor_total"].sum()' calcula a soma monetária de todos os títulos emitidos pela empresa[cite: 5].
        faturamento_total = float(dados["valor_total"].sum())

        # 'dados["status_pagamento"].isin([...])' filtra os títulos que possuem pendência de quitação ou atraso[cite: 5].
        titulos_em_risco = dados[dados["status_pagamento"].isin(["Inadimplente", "Atrasado"])]

        # 'titulos_em_risco["valor_total"].sum()' calcula o total em reais exposto a risco de perda financeira[cite: 5].
        valor_em_risco = float(titulos_em_risco["valor_total"].sum())

        # Calcula a taxa percentual de inadimplência dividindo o valor em risco pelo total da carteira[cite: 5].
        # O operador ternário 'if faturamento_total > 0 else 0.0' previne erros de divisão por zero caso o saldo seja nulo[cite: 5].
        taxa_inadimplencia = (valor_em_risco / faturamento_total) * 100 if faturamento_total > 0 else 0.0

        # 'laudo_inadimplencia' consolida os sinais vitais da tesouraria em um dicionário estruturado[cite: 5].
        laudo_inadimplencia = {
            "faturamento_total_reais": round(faturamento_total, 2),
            "valor_em_risco_reais": round(valor_em_risco, 2),
            "taxa_inadimplencia_percentual": round(taxa_inadimplencia, 2),
            "total_titulos_analisados": int(len(dados)),
            "total_titulos_inadimplentes": int(len(titulos_em_risco)),
        }

        # 'logging.info' documenta o indicador de inadimplência no console para acompanhamento executivo[cite: 5].
        logging.info(
            "Financeiro — Taxa de Inadimplência: %.2f%% (R$ %.2f em risco de calote).",
            laudo_inadimplencia["taxa_inadimplencia_percentual"],
            laudo_inadimplencia["valor_em_risco_reais"],
        )

        # Devolve o dicionário com as métricas financeiras de inadimplência apuradas[cite: 5].
        return laudo_inadimplencia

    # 'def gerar_grafico_distribuicao_status(...)' desenha e exporta o gráfico comparativo de cobrança em 300 DPI[cite: 5].
    def gerar_grafico_distribuicao_status(self, dados: pd.DataFrame) -> Path:
        """Renderiza a distribuição gráfica do montante financeiro alocado por situação de liquidação[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela financeira contendo títulos e valores monetários[cite: 5].

        Returns:
            Path: Rota física da imagem PNG salva no disco em alta resolução (300 DPI)[cite: 5].
        """
        # 'dados.groupby("status_pagamento")["valor_total"].sum().reset_index()' agrupa os valores por situação do título[cite: 5].
        valores_por_status = dados.groupby("status_pagamento")["valor_total"].sum().reset_index()

        # 'self.pasta_saida / "distribuicao_status_cobranca.png"' monta o caminho do arquivo PNG dentro de 'relatorios/figuras/financeiro/'[cite: 5].
        caminho_figura = self.pasta_saida / "distribuicao_status_cobranca.png"

        # 'plt.subplots(figsize=(8, 5))' inicializa a tela de desenho com 8 polegadas de largura por 5 de altura[cite: 5].
        figura, eixo = plt.subplots(figsize=(8, 5))

        # 'sns.barplot(...)' renderiza o gráfico de barras comparando o volume de dinheiro em cada situação de liquidação[cite: 5].
        # - 'hue="status_pagamento"' e 'legend=False': atende rigorosamente à diretriz do Seaborn moderno (v0.14+)[cite: 5].
        # - 'palette="mako"': aplica paleta cromática com transições contrastantes e corporativas[cite: 5].
        sns.barplot(
            data=valores_por_status,
            x="status_pagamento",
            y="valor_total",
            hue="status_pagamento",
            palette="mako",
            legend=False,
            ax=eixo,
        )

        # 'eixo.set_title(...)' configura o título principal com fonte 13 e espaçamento de 12 pontos[cite: 5].
        eixo.set_title("Exposição Financeira por Status de Cobrança (Aging)", fontsize=13, pad=12)

        # 'eixo.set_xlabel(...)' escreve a legenda do eixo horizontal em português[cite: 5].
        eixo.set_xlabel("Situação do Título de Cobrança", fontsize=10)

        # 'eixo.set_ylabel(...)' escreve a legenda financeira do eixo vertical em moeda corrente (R$)[cite: 5].
        eixo.set_ylabel("Volume Financeiro Total (R$)", fontsize=10)

        # 'plt.tight_layout()' ajusta automaticamente as margens do Matplotlib para evitar cortes de texto[cite: 5].
        plt.tight_layout()

        # 'figura.savefig(caminho_figura, dpi=300)' grava o arquivo físico no disco com resolução de 300 DPI[cite: 5].
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa o buffer gráfico da memória RAM, blindando o servidor contra vazamentos de memória[cite: 5].
        plt.close(figura)

        # 'logging.info' documenta a persistência da figura no console corporativo[cite: 5].
        logging.info("Financeiro — Gráfico de status de cobrança salvo com sucesso em: %s", caminho_figura.name)

        # Devolve a rota física da figura gravada no disco[cite: 5].
        return caminho_figura

    # 'def carregar_titulos_com_cliente(...)' carrega os títulos brutos identificando o cliente devedor[cite: 5].
    def carregar_titulos_com_cliente(self) -> pd.DataFrame:
        """Carrega contas a receber brutas com cliente, vencimento e saldos reais.

        Diferente da visão canônica de Aging (que descarta o cliente), esta carga
        preserva ``id_cliente``/``nome_cliente`` para ranquear as carteiras.

        Returns:
            pd.DataFrame: Tabela com id_cliente, nome_cliente, vencimento,
            valor_original, valor_pago e situacao. Estrutura vazia quando o dump
            não possui as colunas mínimas exigidas.
        """
        # Localiza o CSV canônico de contas a receber no diretório do dataset ativo.
        caminho_cr = self.adaptador.resolvedor.localizar_arquivo_tabela(
            self.adaptador.pasta_erp, "contas_receber"
        )
        if caminho_cr is None:
            logging.warning(
                "Financeiro — Tabela de contas a receber não localizada; "
                "visão Top 10 de carteiras indisponível."
            )
            return pd.DataFrame()

        # Carrega a massa bruta com o leitor tolerante do núcleo.
        df_cr = self.leitor.carregar_tabela(caminho_cr)
        colunas = list(df_cr.columns)

        # Descobre as colunas de cliente, vencimento, valor original e pagamento.
        col_id_cliente = _encontrar_coluna(
            colunas, ["idCliente", "id_cliente", "idPessoa", "id_pessoa"]
        )
        col_vencimento = _encontrar_coluna(
            colunas, ["Vencimento", "vencimento", "data_vencimento"]
        )
        col_valor = _encontrar_coluna(
            colunas, ["ValorOriginal", "valor_original", "valor"]
        )
        col_pago = _encontrar_coluna(colunas, ["ValorPago", "valor_pago"])
        col_situacao = _encontrar_coluna(colunas, ["Pago", "pago", "statuscobranca"])

        # Sem cliente ou sem vencimento não há como montar a carteira do mês.
        if not col_id_cliente or not col_vencimento or not col_valor:
            logging.warning(
                "Financeiro — Colunas mínimas ausentes em %s (cliente/vencimento/valor).",
                caminho_cr.name,
            )
            return pd.DataFrame()

        # Monta a tabela normalizada com tipagem resiliente em todas as colunas.
        df_titulos = pd.DataFrame(
            {
                "id_cliente": pd.to_numeric(df_cr[col_id_cliente], errors="coerce"),
                "vencimento": pd.to_datetime(
                    df_cr[col_vencimento], errors="coerce", dayfirst=True
                ),
                "valor_original": pd.to_numeric(
                    df_cr[col_valor], errors="coerce"
                ).fillna(0.0),
                "valor_pago": (
                    pd.to_numeric(df_cr[col_pago], errors="coerce").fillna(0.0)
                    if col_pago
                    else 0.0
                ),
                "situacao": (
                    df_cr[col_situacao].astype(str).str.upper()
                    if col_situacao
                    else pd.Series("ABERTO", index=df_cr.index)
                ),
            }
        )

        # Descarta títulos sem vencimento ou sem valor econômico.
        df_titulos = df_titulos.dropna(subset=["vencimento", "id_cliente"])
        df_titulos = df_titulos[df_titulos["valor_original"] > 0].copy()

        # Anexa o nome real do cliente quando a tabela de pessoas estiver disponível.
        caminho_pessoas = self.adaptador.resolvedor.localizar_arquivo_tabela(
            self.adaptador.pasta_erp, "pessoas"
        )
        if caminho_pessoas is not None:
            df_pessoas = self.leitor.carregar_tabela(caminho_pessoas)
            col_id_pessoa = _encontrar_coluna(list(df_pessoas.columns), ["ID", "id"])
            col_nome = _encontrar_coluna(
                list(df_pessoas.columns),
                ["RazaoSocial", "NomeFantasia", "Nome", "razao_social"],
            )
            if col_id_pessoa and col_nome:
                mapa_nomes = df_pessoas[[col_id_pessoa, col_nome]].copy()
                mapa_nomes[col_id_pessoa] = pd.to_numeric(
                    mapa_nomes[col_id_pessoa], errors="coerce"
                )
                mapa_nomes = mapa_nomes.dropna(subset=[col_id_pessoa])
                df_titulos["nome_cliente"] = df_titulos["id_cliente"].map(
                    mapa_nomes.set_index(col_id_pessoa)[col_nome]
                )

        # Rótulo de fallback para clientes sem cadastro nominal correspondente.
        if "nome_cliente" not in df_titulos.columns:
            df_titulos["nome_cliente"] = pd.Series(dtype=str)
        df_titulos["nome_cliente"] = (
            df_titulos["nome_cliente"]
            .fillna("Cliente #" + df_titulos["id_cliente"].astype(int).astype(str))
            .astype(str)
        )

        logging.info(
            "Financeiro — %d títulos reais carregados com identificação de cliente.",
            len(df_titulos),
        )
        return df_titulos

    # 'def calcular_top_10_carteiras_mes(...)' ranqueia as carteiras/cadernetas do mês de referência[cite: 5].
    def calcular_top_10_carteiras_mes(
        self, titulos: pd.DataFrame
    ) -> tuple[Dict[str, Any], pd.DataFrame]:
        """Apura o consumo do mês e o saldo em aberto por cliente (Top 10 carteiras).

        Mês de referência: o último mês **completo** (anterior ao corrente) que
        possui títulos. Consumo = soma dos títulos com vencimento no mês; saldo
        em aberto = saldo devedor acumulado até o fim desse mês.

        Args:
            titulos (pd.DataFrame): Tabela de títulos com cliente (``carregar_titulos_com_cliente``).

        Returns:
            tuple: dicionário-resumo (mes_referencia, totais e top_10) e o
            DataFrame recortado do Top 10 pronto para plotagem.
        """
        # Base vazia devolve resumo vazio (o chamador simplesmente omite a visão).
        if titulos.empty:
            return {}, pd.DataFrame()

        # Delimita a janela de 12 meses terminando no mês corrente do relógio.
        hoje = pd.Timestamp(datetime.now())
        mes_corrente = hoje.to_period("M")
        inicio_janela = hoje - pd.DateOffset(months=12)

        janela = titulos[
            (titulos["vencimento"] >= inicio_janela)
            & (titulos["vencimento"] < hoje)
        ].copy()

        # Sem títulos na janela, usa a base integral (dumps históricos antigos).
        if janela.empty:
            janela = titulos.copy()

        # Mês de referência = último mês completo anterior ao corrente com títulos.
        meses_com_titulos = janela[
            janela["vencimento"].dt.to_period("M") < mes_corrente
        ]["vencimento"].dt.to_period("M")
        if meses_com_titulos.empty:
            return {}, pd.DataFrame()
        mes_referencia = meses_com_titulos.max()

        # Consome os títulos do mês escolhido (caderneta consumida no mês).
        titulos_mes = janela[
            janela["vencimento"].dt.to_period("M") == mes_referencia
        ]
        consumo_mes = titulos_mes.groupby("id_cliente")["valor_original"].sum()

        # Saldo em aberto acumulado até o fim do mês de referência: desconta o que
        # já foi pago e ignora títulos liquidados ou cancelados.
        fim_mes = (mes_referencia + 1).to_timestamp()
        abertos = titulos[
            (titulos["vencimento"] < fim_mes)
            & (~titulos["situacao"].isin(["SIM", "CAN", "PAGO", "QUITADO"]))
        ].copy()
        abertos["saldo"] = (
            abertos["valor_original"] - abertos["valor_pago"]
        ).clip(lower=0)
        saldo_aberto = abertos.groupby("id_cliente")["saldo"].sum()

        # Consolida consumo e saldo por cliente em uma única tabela.
        df_carteiras = consumo_mes.rename("consumo_mes").to_frame()
        df_carteiras = df_carteiras.join(saldo_aberto.rename("saldo_aberto"), how="left")
        df_carteiras["saldo_aberto"] = df_carteiras["saldo_aberto"].fillna(0.0)

        # Mapeia o nome real do cliente a partir do próprio mês de referência.
        mapa_nomes_mes = (
            titulos_mes.drop_duplicates("id_cliente")
            .set_index("id_cliente")["nome_cliente"]
        )
        df_carteiras["nome_cliente"] = df_carteiras.index.map(mapa_nomes_mes)

        # Completa com a base integral de títulos os clientes sem nome no mês.
        mapa_nomes_completo = (
            titulos.drop_duplicates("id_cliente").set_index("id_cliente")["nome_cliente"]
        )
        df_carteiras["nome_cliente"] = [
            nome
            if isinstance(nome, str) and nome and not nome.startswith("nan")
            else str(
                mapa_nomes_completo.get(id_cliente, f"Cliente #{int(id_cliente)}")
            )
            for id_cliente, nome in zip(
                df_carteiras.index, df_carteiras["nome_cliente"]
            )
        ]

        # Ranqueia por consumo do mês e recorta os 10 maiores.
        df_top_10 = df_carteiras.sort_values(
            by="consumo_mes", ascending=False
        ).head(10)

        # Estrutura o resumo executivo da carteira do mês.
        resumo = {
            "mes_referencia": str(mes_referencia),
            "total_clientes_no_mes": int(len(df_carteiras)),
            "consumo_total_mes_reais": round(float(consumo_mes.sum()), 2),
            "saldo_aberto_ate_o_mes_reais": round(float(saldo_aberto.sum()), 2),
            "top_10_carteiras": [
                {
                    "nome_cliente": str(linha["nome_cliente"]),
                    "id_cliente": int(id_cliente),
                    "consumo_mes_reais": round(float(linha["consumo_mes"]), 2),
                    "saldo_aberto_reais": round(float(linha["saldo_aberto"]), 2),
                }
                for id_cliente, linha in df_top_10.iterrows()
            ],
        }

        logging.info(
            "Financeiro — Carteiras do mês %s: %d clientes, consumo R$ %.2f, "
            "saldo em aberto R$ %.2f.",
            resumo["mes_referencia"],
            resumo["total_clientes_no_mes"],
            resumo["consumo_total_mes_reais"],
            resumo["saldo_aberto_ate_o_mes_reais"],
        )
        return resumo, df_top_10

    # 'def gerar_grafico_top_10_carteiras_mes(...)' desenha o ranking das 10 maiores carteiras do mês[cite: 5].
    def gerar_grafico_top_10_carteiras_mes(
        self, df_top: pd.DataFrame, resumo: Dict[str, Any]
    ) -> Path:
        """Renderiza barras horizontais do consumo mensal por cliente com saldo em aberto.

        Args:
            df_top (pd.DataFrame): Top 10 com 'consumo_mes' e 'saldo_aberto'.
            resumo (Dict[str, Any]): Resumo com mês de referência e totais.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        # Prepara a tabela de plotagem em ordem crescente (maior fica no topo).
        df_plot = df_top.reset_index().sort_values(by="consumo_mes", ascending=True)

        # Constrói o caminho do arquivo dentro da subpasta 'financeiro/'.
        caminho_figura = self.pasta_saida / "top_10_carteiras_mes.png"

        # Moldura de 10 por 6 polegadas para acomodar nomes de clientes longos.
        figura, eixo = plt.subplots(figsize=(10, 6))

        # Posições inteiras: item 0 na base, maior consumo no topo.
        posicoes = list(range(len(df_plot)))

        # Barras do consumo do mês na paleta corporativa padrão.
        eixo.barh(
            posicoes,
            df_plot["consumo_mes"],
            color=sns.color_palette("mako", n_colors=len(df_plot)),
        )

        # Rótulos dos clientes no eixo Y.
        eixo.set_yticks(posicoes)
        eixo.set_yticklabels(df_plot["nome_cliente"], fontsize=9)

        # Folga à direita para o rótulo monetário e o saldo em aberto.
        maior_consumo = float(df_plot["consumo_mes"].max()) if len(df_plot) else 1.0
        eixo.set_xlim(0, maior_consumo * 1.70)

        # Rótulo único por linha: consumo do mês + saldo em aberto (evita a
        # sobreposição de dois textos concorrentes na mesma altura).
        for posicao, (_, linha) in enumerate(df_plot.iterrows()):
            consumo = (
                f"{linha['consumo_mes']:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            saldo = (
                f"{linha['saldo_aberto']:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            if float(linha["saldo_aberto"]) > 0:
                # '\$' escapado impede o Matplotlib de interpretar o cifrão
                # como delimitador de fórmula mathtext (dois '$' na mesma string).
                rotulo = f"  R\\$ {consumo}  ·  em aberto R\\$ {saldo}"
            else:
                rotulo = f"  R\\$ {consumo}"

            eixo.text(
                linha["consumo_mes"],
                posicao,
                rotulo,
                ha="left",
                va="center",
                fontsize=8.5,
                fontweight="bold",
            )

        # Título com o mês de referência e os totais consolidados do período.
        # Os cifrões são escapados ('\$') para o Matplotlib não abrir mathtext
        # ao encontrar dois '$' na mesma cadeia.
        consumo_mes_fmt = (
            f"{resumo['consumo_total_mes_reais']:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )
        saldo_mes_fmt = (
            f"{resumo['saldo_aberto_ate_o_mes_reais']:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )
        eixo.set_title(
            "Top 10 Maiores Carteiras/Cadernetas Consumidoras do Mês "
            f"({resumo['mes_referencia']})\n"
            f"Consumo do mês: R\\$ {consumo_mes_fmt}  ·  "
            f"Saldo em aberto acumulado: R\\$ {saldo_mes_fmt}",
            fontsize=12,
            pad=12,
        )

        # Rótulos executivos dos eixos.
        eixo.set_xlabel(
            f"Títulos com vencimento em {resumo['mes_referencia']} — Consumo por Cliente (R$)",
            fontsize=10,
        )
        eixo.set_ylabel("Cliente / Caderneta", fontsize=10)

        # Ajuste dinâmico de margens e gravação em alta resolução (300 DPI).
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)

        # Liberação imediata do buffer gráfico na memória RAM.
        plt.close(figura)

        logging.info(
            "Financeiro — Gráfico Top 10 de carteiras do mês salvo em: %s",
            caminho_figura.name,
        )
        return caminho_figura

    # 'def executar_diagnostico_completo(...)' implementa o contrato formal de execução da BaseDepartamento[cite: 5].
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o cálculo sequencial dos indicadores financeiros e a persistência das visualizações[cite: 5].

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento financeiro com métricas e caminho da imagem[cite: 5].
        """
        # Emite log formal marcando a abertura dos procedimentos do setor financeiro[cite: 5].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO FINANCEIRO (FASE 2.2) ===")

        # 1. Carrega os dados reais de títulos a receber utilizando o Adaptador Universal[cite: 5].
        df_financeiro = self.carregar_dados_financeiros()

        # 2. Executa a camada tabular apurando a taxa de inadimplência e o capital sob risco[cite: 5].
        laudo_inadimplencia = self.calcular_taxa_inadimplencia(df_financeiro)

        # 3. Executa a camada gráfica renderizando o gráfico de situação de cobrança e gravando a imagem[cite: 5].
        caminho_grafico = self.gerar_grafico_distribuicao_status(df_financeiro)

        # 'laudo_financeiro' consolida as métricas tabulares e a imagem gerada no dicionário oficial do setor[cite: 5].
        laudo_financeiro = {
            "analise_inadimplencia": laudo_inadimplencia,
            "grafico_status_cobranca": str(caminho_grafico),
        }

        # 4. Visão exploratória complementar: Top 10 maiores carteiras/cadernetas
        # consumidoras do mês (consumo do mês + saldo em aberto por cliente).
        # O bloco é isolado em try/except para que uma falha nesta visão
        # secundária nunca derrube o diagnóstico principal do Financeiro.
        try:
            titulos_com_cliente = self.carregar_titulos_com_cliente()
            resumo_carteiras, df_top_carteiras = self.calcular_top_10_carteiras_mes(
                titulos_com_cliente
            )
            if not df_top_carteiras.empty:
                caminho_carteiras = self.gerar_grafico_top_10_carteiras_mes(
                    df_top_carteiras, resumo_carteiras
                )
                laudo_financeiro["top_10_carteiras_mes"] = resumo_carteiras
                laudo_financeiro["grafico_top_10_carteiras"] = str(caminho_carteiras)
        except Exception:
            # Auditoria técnica completa no console sem interromper a Fase 02.
            logging.warning(
                "Financeiro — Falha ao montar a visão Top 10 de carteiras do mês "
                "(visão secundária ignorada).",
                exc_info=True,
            )

        # Emite log confirmando o encerramento bem-sucedido da perícia financeira[cite: 5].
        logging.info("=== DEPARTAMENTO FINANCEIRO CONCLUÍDO COM SUCESSO ===")

        # Devolve o laudo executivo financeiro para o orquestrador do Raio-X Empresarial[cite: 5].
        return laudo_financeiro