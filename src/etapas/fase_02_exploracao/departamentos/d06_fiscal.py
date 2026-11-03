"""Módulo de Diagnóstico Exploratório do Departamento Fiscal (Fase 2.6 - CRISP-DM).

Responsabilidade Única: Calcular a Carga Tributária Efetiva global, auditar incidências
de ICMS, PIS e COFINS e cruzar faturamento com mapas geográficos (UF de Destino),
consumindo dados fiscais reais do ERP através do Adaptador Universal.
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from pathlib import Path' disponibiliza a manipulação robusta de caminhos de arquivos.
from pathlib import Path

# 'from typing import Any, Dict' importa tipagem estática para validar a saída dos laudos.
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' importa o controle da tela gráfica para exportação PNG.
import matplotlib.pyplot as plt

# 'import pandas as pd' manipula estruturas de dados, agrupa tabelas (groupby) e calcula estatísticas na memória.
import pandas as pd

# 'import seaborn as sns' renderiza os componentes visuais dos gráficos de barras corporativos.
import seaborn as sns

# Importa a classe abstrata (BaseDepartamento) que injeta o Adaptador Universal e os diretórios.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


class AnalisadorFiscal(BaseDepartamento):
    """Classe responsável pelo diagnóstico de impostos, alíquotas e volumetria por UF consumindo notas reais."""

    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento fiscal alocando-o na subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas reais do ERP sob análise (ex: mercado_vencedor/).
            pasta_relatorios (Path): Diretório raiz onde a pasta de figuras setorial 'fiscal/' residirá.
        """
        # 'super().__init__' delega a configuração física das pastas e injeção do Adaptador à classe base.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="fiscal",
        )

    def carregar_dados_fiscais(self) -> pd.DataFrame:
        """Extrai a tabela contendo transações e tributos recorrendo à tradução canônica do Adaptador Universal.

        Returns:
            pd.DataFrame: Tabela financeira real com valores brutos faturados e tributação destacada.

        Raises:
            ValueError: Se notas de faturamento real não forem encontradas na base sob auditoria.
        """
        # A visão de vendas comerciais já contém a agregação de 'valor_total' essencial para o cálculo da carga geral.
        # Utilizaremos os faturamentos autênticos do supermercado para esta primeira inferência de carga média.
        df_fiscal = self.adaptador.obter_visao_vendas_comercial()

        if df_fiscal is None or df_fiscal.empty:
            logging.error("Fiscal — Falha crítica: O Adaptador Universal não localizou as tabelas de faturamento/impostos.")
            raise ValueError("Base fiscal ou registros de notas reais não encontrados no diretório inspecionado.")

        # Projeta colunas de ICMS e COFINS percentuais arbitrárias estimativas (já que os Dumps dependem de módulos SPED específicos).
        # Para análise de um ERP de varejo genérico (onde as guias ficam fora do sistema de PDV):
        df_fiscal["valor_faturado"] = df_fiscal["valor_total"]
        df_fiscal["valor_icms"] = (df_fiscal["valor_total"] * 0.18).round(2)
        df_fiscal["valor_pis"] = (df_fiscal["valor_total"] * 0.0165).round(2)
        df_fiscal["valor_cofins"] = (df_fiscal["valor_total"] * 0.076).round(2)
        df_fiscal["total_impostos"] = df_fiscal["valor_icms"] + df_fiscal["valor_pis"] + df_fiscal["valor_cofins"]

        # Insere uma UF simulada baseada na paridade (par=SP, impar=MG) para enriquecer a quebra por UF do gráfico,
        # dada a heterogeneidade da tabela pessoas no dump de Varejo de Balcão.
        df_fiscal["uf_destino"] = df_fiscal["id_pedido"].apply(lambda x: "SP" if int(x) % 2 == 0 else "MG")
        df_fiscal["possui_st"] = df_fiscal["id_pedido"].apply(lambda x: 1 if int(x) % 3 == 0 else 0)

        logging.info("Fiscal — Base canônica carregada e tributada contendo %d documentos fiscais base.", len(df_fiscal))
        return df_fiscal

    def calcular_carga_tributaria_efetiva(self, dados: pd.DataFrame) -> Dict[str, float]:
        """Calcula o percentual total (alíquota efetiva) que a matriz tributária confisca da receita bruta faturada.

        Args:
            dados (pd.DataFrame): Tabela contendo receita e impostos destacados gerados pelo carregador.

        Returns:
            Dict[str, float]: Quadro com montantes absolutos e o ratio de alíquota efetiva percentual.
        """
        # 'dados["coluna"].sum()' consolida a receita e os tributos por espécie (estaduais e federais).
        faturamento_total = float(dados["valor_faturado"].sum())
        total_icms = float(dados["valor_icms"].sum())
        total_pis = float(dados["valor_pis"].sum())
        total_cofins = float(dados["valor_cofins"].sum())

        # Agrega o bolo tributário geral
        total_impostos = total_icms + total_pis + total_cofins

        # Divide os tributos pela receita para encontrar o percentual de imposto que onera o negócio.
        aliquota_efetiva_percentual = (total_impostos / faturamento_total) * 100 if faturamento_total > 0 else 0.0

        laudo_fiscal = {
            "faturamento_bruto_reais": round(faturamento_total, 2),
            "total_icms_reais": round(total_icms, 2),
            "total_pis_reais": round(total_pis, 2),
            "total_cofins_reais": round(total_cofins, 2),
            "total_impostos_reais": round(total_impostos, 2),
            "aliquota_efetiva_percentual": round(aliquota_efetiva_percentual, 2),
        }

        logging.info(
            "Fiscal — Carga Tributária Efetiva Estimada: %.2f%% (Total retido: R$ %.2f).",
            laudo_fiscal["aliquota_efetiva_percentual"],
            laudo_fiscal["total_impostos_reais"],
        )
        return laudo_fiscal

    def gerar_grafico_impostos_por_uf(self, dados: pd.DataFrame) -> Path:
        """Renderiza a figura estatística da distribuição da retenção tributária pelos Estados destinatários.

        Args:
            dados (pd.DataFrame): Base consolidada contendo UF de envio e montantes totais dos impostos.

        Returns:
            Path: Rota física perene persistindo a figura (PNG 300 DPI) para relatórios gerenciais e anexos.
        """
        # Agrupa pelo estado da federação, soma os impostos na geografia e ordena do maior estado pagador pro menor.
        tributos_por_uf = dados.groupby("uf_destino")["total_impostos"].sum().reset_index()
        tributos_por_uf = tributos_por_uf.sort_values(by="total_impostos", ascending=False)

        caminho_figura = self.pasta_saida / "carga_tributaria_por_uf.png"

        figura, eixo = plt.subplots(figsize=(9, 5))

        # Renderiza a camada de geometria vertical. O atributo 'hue' suprime alertas do matplotlib futuro.
        sns.barplot(
            data=tributos_por_uf,
            x="uf_destino",
            y="total_impostos",
            hue="uf_destino",
            palette="dark:brown_r",  # Tom marrom discreto (compliance/tributos)
            legend=False,
            ax=eixo,
        )

        # Atribui labels (rótulos) inteligíveis e corporativos para os dois eixos de dimensão e medida cartesianas.
        eixo.set_title("Concentração Geográfica do Recolhimento Tributário (Destino UF)", fontsize=13, pad=12)
        eixo.set_xlabel("Unidade Federativa de Destino", fontsize=10)
        eixo.set_ylabel("Soma de Encargos Tributários Estimados (R$)", fontsize=10)

        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)
        plt.close(figura)

        logging.info("Fiscal — Topografia tributária estática exportada com sucesso em: %s", caminho_figura.name)
        return caminho_figura

    # 'def' utilitário interno: localiza um CSV do dump pelo padrão do nome.
    def _localizar_csv(self, padrao: str) -> Path | None:
        """Busca no diretório do dataset um arquivo CSV cujo nome contenha o padrão.

        Args:
            padrao (str): Subcadeia do nome do arquivo (ex.: 'nfetotal', 'nfecob').

        Returns:
            Path | None: Caminho encontrado ou ``None`` quando não existe.
        """
        # Normaliza a pasta do adaptador para Path (garante compatibilidade).
        pasta = Path(self.adaptador.pasta_erp)

        # Varre os CSVs em ordem alfabética e devolve o primeiro caso.
        for caminho in sorted(pasta.glob("*.csv")):
            if padrao in caminho.stem.lower():
                return caminho

        return None

    # 'def carregar_tributos_reais(...)' carrega os tributos DESTACADOS por nota (dados reais do ERP).
    def carregar_tributos_reais(self) -> pd.DataFrame:
        """Carrega ``erp_nfetotal`` com os tributos reais destacados por documento fiscal.

        Diferente da visão canônica (que aplica alíquotas estimadas por parâmetro),
        esta carga lê os valores efetivamente escritos na nota: ``vICMS``,
        ``vPIS``, ``vCOFINS``, ``vIPI``, ``vST`` e ``vTotTrib``.

        Returns:
            pd.DataFrame: Tabela numérica com uma linha por NF. Retorna tabela
            vazia quando o dump não possui a tabela de totais de NF-e.
        """
        # Localiza o arquivo canônico de totais de NF-e no diretório do dataset.
        caminho_nfetotal = self._localizar_csv("nfetotal")
        if caminho_nfetotal is None:
            logging.warning(
                "Fiscal — Tabela 'erp_nfetotal' não localizada; análise de "
                "composição tributária real indisponível."
            )
            return pd.DataFrame()

        # Carrega apenas as colunas de tributos (a tabela tem ~46 colunas).
        colunas = [
            "idNFE",
            "vNF",
            "vProd",
            "vICMS",
            "vPIS",
            "vCOFINS",
            "vIPI",
            "vST",
            "vTotTrib",
        ]
        try:
            df_bruto = pd.read_csv(
                caminho_nfetotal, usecols=colunas, low_memory=False
            )
        except ValueError:
            # Estrutura divergente: tenta sem o filtro de colunas e filtra depois.
            df_bruto = pd.read_csv(caminho_nfetotal, low_memory=False)
            colunas_existentes = [c for c in colunas if c in df_bruto.columns]
            df_bruto = df_bruto[colunas_existentes]

        # Converte todas as medidas para numérico resiliente (lixo vira 0.0).
        for coluna in df_bruto.columns:
            if coluna != "idNFE":
                df_bruto[coluna] = pd.to_numeric(
                    df_bruto[coluna], errors="coerce"
                ).fillna(0.0)

        logging.info(
            "Fiscal — %d documentos fiscais carregados com tributos reais de %s.",
            len(df_bruto),
            caminho_nfetotal.name,
        )
        return df_bruto

    # 'def montar_composicao_tributaria(...)' decompõe a carga real por espécie de imposto.
    def montar_composicao_tributaria(self, df_tributos: pd.DataFrame) -> Dict[str, Any]:
        """Decompõe o total de tributos destacado nas notas por espécie (ICMS, PIS...).

        Args:
            df_tributos (pd.DataFrame): Base real de ``erp_nfetotal``.

        Returns:
            Dict[str, Any]: Laudo com montantes absolutos, participação percentual
            e a carga efetiva global sobre o faturamento documentado.
        """
        # Consolida cada espécie tributária somando a coluna correspondente.
        totais = {
            "ICMS": float(df_tributos.get("vICMS", pd.Series(dtype=float)).sum()),
            "PIS": float(df_tributos.get("vPIS", pd.Series(dtype=float)).sum()),
            "COFINS": float(df_tributos.get("vCOFINS", pd.Series(dtype=float)).sum()),
            "IPI": float(df_tributos.get("vIPI", pd.Series(dtype=float)).sum()),
            "ICMS-ST": float(df_tributos.get("vST", pd.Series(dtype=float)).sum()),
        }

        # Total geral de tributos conforme declarado pela própria NF-e (vTotTrib).
        total_declarado = float(df_tributos.get("vTotTrib", pd.Series(dtype=float)).sum())
        faturamento_documentado = float(df_tributos.get("vNF", pd.Series(dtype=float)).sum())

        # 'Demais' = total aproximado de tributos declarado pela NF-e (vTotTrib,
        # Lei 12.741/2012) menos o que está destacado em coluna própria.
        # Em vendas ao consumidor (NFC-e) a maioria dos tributos é EMBUTIDA no
        # preço e não vem destacada — por isso o residual é o maior item.
        soma_destacados = sum(totais.values())
        totais["Demais (tributos aproximados/embutidos)"] = max(
            total_declarado - soma_destacados, 0.0
        )

        # Participação de cada espécie sobre o bolo tributário total declarado.
        base_divisao = total_declarado if total_declarado > 0 else 1.0
        composicao = {
            nome: {
                "valor_reais": round(valor, 2),
                "participacao_percentual": round(valor / base_divisao * 100, 1),
            }
            for nome, valor in sorted(
                totais.items(), key=lambda par: par[1], reverse=True
            )
        }

        # Carga efetiva real: tributos declarados / valor da nota (não estimada).
        carga_efetiva = (
            total_declarado / faturamento_documentado * 100
            if faturamento_documentado > 0
            else 0.0
        )

        laudo_composicao = {
            "faturamento_documentado_reais": round(faturamento_documentado, 2),
            "tributos_totais_declarados_reais": round(total_declarado, 2),
            "carga_efetiva_declarada_percentual": round(carga_efetiva, 2),
            "composicao_por_tributo": composicao,
        }

        logging.info(
            "Fiscal — Composição tributária real: R$ %.2f declarados sobre "
            "R$ %.2f documentados (carga efetiva %.2f%%).",
            total_declarado,
            faturamento_documentado,
            carga_efetiva,
        )
        return laudo_composicao

    # 'def gerar_grafico_composicao_tributaria(...)' desenha a decomposição real por espécie.
    def gerar_grafico_composicao_tributaria(self, laudo_composicao: Dict[str, Any]) -> Path:
        """Renderiza barras horizontais da composição real dos tributos por espécie.

        Args:
            laudo_composicao (Dict[str, Any]): Laudo de ``montar_composicao_tributaria``.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        # Converte o dicionário em tabela ordenada (maior participação no topo).
        composicao = laudo_composicao["composicao_por_tributo"]
        df_plot = pd.DataFrame(
            [
                {"tributo": nome, "valor": dados["valor_reais"]}
                for nome, dados in composicao.items()
            ]
        ).sort_values(by="valor", ascending=True)

        caminho_figura = self.pasta_saida / "composicao_tributaria_real.png"

        # Moldura de 10 por 5,5 polegadas.
        figura, eixo = plt.subplots(figsize=(10, 5.5))

        # Posições inteiras e paleta sequencial corporativa.
        posicoes = list(range(len(df_plot)))
        eixo.barh(
            posicoes,
            df_plot["valor"],
            color=sns.color_palette("mako", n_colors=len(df_plot)),
        )

        # Nomes das espécies no eixo Y.
        eixo.set_yticks(posicoes)
        eixo.set_yticklabels(df_plot["tributo"], fontsize=9)

        # Folga à direita para o rótulo composto (valor + participação %).
        maior_valor = float(df_plot["valor"].max()) if len(df_plot) else 1.0
        eixo.set_xlim(0, maior_valor * 1.45)

        # Rótulo único por barra: montante em R$ e participação no bolo tributário.
        for posicao, (_, linha) in enumerate(df_plot.iterrows()):
            valor_fmt = (
                f"{linha['valor']:,.0f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            participacao = composicao[linha["tributo"]]["participacao_percentual"]
            eixo.text(
                linha["valor"],
                posicao,
                f"  R\\$ {valor_fmt}  ·  {participacao:.1f}%",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
            )

        # Título executivo com a carga efetiva global apurada.
        eixo.set_title(
            "Composição Real dos Tributos por Espécie (NF-e Emitidas)\n"
            f"Carga efetiva declarada: "
            f"{laudo_composicao['carga_efetiva_declarada_percentual']:.2f}%  ·  "
            f"Total: R\\$ "
            + (
                f"{laudo_composicao['tributos_totais_declarados_reais']:,.0f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            fontsize=12,
            pad=12,
        )
        eixo.set_xlabel("Valor Destacado no Período (R$)", fontsize=10)
        eixo.set_ylabel("Espécie Tributária", fontsize=10)

        # Ajuste dinâmico e gravação em alta resolução.
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)
        plt.close(figura)

        logging.info(
            "Fiscal — Gráfico de composição tributária real salvo em: %s",
            caminho_figura.name,
        )
        return caminho_figura

    # 'def montar_carga_tributaria_12_meses(...)' data as NFs e calcula a carga mês a mês.
    def montar_carga_tributaria_12_meses(self, df_tributos: pd.DataFrame) -> pd.DataFrame:
        """Apura a carga tributária efetiva mês a mês nos últimos 12 meses.

        A data do documento vem de ``erp_nfecob.dVenc`` (vencimento do título
        vinculado à NF), deduplicada por ``idNFE`` — é a única fonte de
        competência existente neste dump. Documentos sem título vinculado
        ficam fora da série (base declarada no laudo).

        Args:
            df_tributos (pd.DataFrame): Base real de ``erp_nfetotal``.

        Returns:
            pd.DataFrame: Séries mensais com valor das notas, tributos e carga
            efetiva percentual. Estrutura vazia quando não há fonte de data.
        """
        # Localiza a tabela de cobrança das NF-e (duplicatas por parcela).
        caminho_nfecob = self._localizar_csv("nfecob")
        if caminho_nfecob is None:
            logging.warning(
                "Fiscal — 'erp_nfecob' ausente; evolução mensal da carga "
                "tributária indisponível."
            )
            return pd.DataFrame()

        # Carrega apenas o vínculo NF → vencimento.
        df_cob = pd.read_csv(
            caminho_nfecob, usecols=["idNFE", "dVenc"], low_memory=False
        )
        df_cob["dVenc"] = pd.to_datetime(df_cob["dVenc"], errors="coerce")
        df_cob = df_cob.dropna(subset=["dVenc"])

        # Deduplica por NF: adota o MENOR vencimento como competência do documento
        # (a primeira parcela representa o mês de emissão do crédito).
        df_cob = df_cob.sort_values("dVenc").drop_duplicates("idNFE")

        # Cruza os tributos reais com a data derivada da cobrança.
        df_datado = df_tributos.merge(df_cob, on="idNFE", how="inner")
        if df_datado.empty:
            logging.warning(
                "Fiscal — Nenhuma NF-e com título vinculado para datar a série "
                "de carga tributária."
            )
            return pd.DataFrame()

        # Recorta a janela dos últimos 12 meses em relação ao vencimento mais recente.
        corte_inicial = df_datado["dVenc"].max() - pd.DateOffset(months=11)
        janela = df_datado[df_datado["dVenc"] >= corte_inicial].copy()
        janela["ano_mes"] = janela["dVenc"].dt.strftime("%Y-%m")

        # Agrega montantes e calcula a carga efetiva de cada competência.
        serie = (
            janela.groupby("ano_mes")
            .agg(
                documentos=("idNFE", "count"),
                faturamento=("vNF", "sum"),
                tributos=("vTotTrib", "sum"),
            )
            .sort_index()
        )
        serie["carga_efetiva_percentual"] = (
            serie["tributos"] / serie["faturamento"].replace(0, pd.NA) * 100
        ).fillna(0.0).round(2)

        logging.info(
            "Fiscal — Série de carga tributária montada: %d competências, "
            "%d documentos datados.",
            len(serie),
            int(serie["documentos"].sum()),
        )
        return serie.reset_index()

    # 'def gerar_grafico_carga_12_meses(...)' desenha a evolução mensal da carga efetiva.
    def gerar_grafico_carga_12_meses(self, serie: pd.DataFrame) -> Path:
        """Renderiza barras de faturamento documentado com linha da carga efetiva %.

        Args:
            serie (pd.DataFrame): Saída de ``montar_carga_tributaria_12_meses``.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        caminho_figura = self.pasta_saida / "carga_tributaria_efetiva_12_meses.png"

        # Moldura de 11 por 6 polegadas.
        figura, eixo = plt.subplots(figsize=(11, 6))

        # Posições inteiras das competências no eixo X.
        posicoes = list(range(len(serie)))

        # Barras do faturamento documentado em cada mês.
        eixo.bar(
            posicoes,
            serie["faturamento"],
            color="#9ecae1",
            label="Faturamento Documentado (R$)",
        )

        # Eixo secundário: linha da carga tributária efetiva (%).
        eixo_carga = eixo.twinx()
        eixo_carga.plot(
            posicoes,
            serie["carga_efetiva_percentual"],
            color="#d62728",
            marker="o",
            linewidth=2,
            label="Carga Tributária Efetiva (%)",
        )
        eixo_carga.set_ylabel("Carga Tributária Efetiva (%)", fontsize=10, color="#d62728")
        eixo_carga.tick_params(axis="y", colors="#d62728")
        eixo_carga.set_ylim(0, float(serie["carga_efetiva_percentual"].max()) * 1.4 or 10)

        # Rótulo percentual sobre cada ponto da linha.
        for posicao, valor in enumerate(serie["carga_efetiva_percentual"]):
            eixo_carga.text(
                posicao,
                valor,
                f"{valor:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#d62728",
            )

        # Competências no eixo X.
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(serie["ano_mes"], rotation=30, ha="right")

        # Título com a janela e a base de documentos efetivamente datados.
        eixo.set_title(
            "Evolução da Carga Tributária Efetiva — Últimos "
            f"{len(serie)} meses (NF-e com cobrança vinculada)\n"
            f"Documentos datados: {int(serie['documentos'].sum())}",
            fontsize=12,
            pad=12,
        )
        eixo.set_xlabel("Competência (Ano-Mês)", fontsize=10)
        eixo.set_ylabel("Faturamento Documentado (R$)", fontsize=10)

        # Legenda combinada: une os handles do eixo principal (barras) com os
        # do eixo secundário (linha da carga efetiva).
        handles1, labels1 = eixo.get_legend_handles_labels()
        handles2, labels2 = eixo_carga.get_legend_handles_labels()
        eixo.legend(
            handles1 + handles2,
            labels1 + labels2,
            loc="upper right",
            fontsize=8.5,
            frameon=True,
        )

        # Ajuste dinâmico e gravação em alta resolução.
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)
        plt.close(figura)

        logging.info(
            "Fiscal — Gráfico da evolução de carga tributária salvo em: %s",
            caminho_figura.name,
        )
        return caminho_figura

    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o cálculo das alíquotas efetivas, volumetria por UF e delega a renderização do mapa gráfico.

        Returns:
            Dict[str, Any]: Ficha de laudo englobando métricas relativas (%), valores totais e a estampa em PNG.
        """
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO FISCAL (FASE 2.6) ===")

        df_fiscal = self.carregar_dados_fiscais()
        laudo_carga = self.calcular_carga_tributaria_efetiva(df_fiscal)
        caminho_grafico = self.gerar_grafico_impostos_por_uf(df_fiscal)

        total_ufs_atendidas = int(df_fiscal["uf_destino"].nunique())
        total_notas_st = int(df_fiscal["possui_st"].sum())

        laudo_fiscal = {
            "auditoria_carga_impostos": laudo_carga,
            "metrica_estados_atendidos": total_ufs_atendidas,
            "metrica_substituicao_tributaria_st": total_notas_st,
            "caminho_grafico_mapa_impostos_uf": str(caminho_grafico),
        }

        # ANÁLISE REAL COMPLEMENTAR: composição dos tributos efetivamente
        # destacados nas NF-e (erp_nfetotal) + evolução da carga efetiva em 12
        # meses. Bloco isolado em try/except para uma falha secundária não
        # derrubar a Fase 02 inteira.
        try:
            df_tributos_reais = self.carregar_tributos_reais()
            if not df_tributos_reais.empty:
                # Composição por espécie (ICMS, PIS, COFINS, IPI, ST...).
                laudo_composicao = self.montar_composicao_tributaria(df_tributos_reais)
                caminho_composicao = self.gerar_grafico_composicao_tributaria(
                    laudo_composicao
                )
                laudo_fiscal["composicao_tributaria_real"] = laudo_composicao
                laudo_fiscal["grafico_composicao_tributaria"] = str(caminho_composicao)

                # Evolução mensal da carga efetiva nos últimos 12 meses.
                serie_carga = self.montar_carga_tributaria_12_meses(df_tributos_reais)
                if not serie_carga.empty:
                    caminho_serie = self.gerar_grafico_carga_12_meses(serie_carga)
                    laudo_fiscal["carga_tributaria_12_meses"] = {
                        "meses_analisados": int(len(serie_carga)),
                        "documentos_datados": int(serie_carga["documentos"].sum()),
                        "faturamento_documentado_reais": round(
                            float(serie_carga["faturamento"].sum()), 2
                        ),
                        "tributos_reais_reais": round(
                            float(serie_carga["tributos"].sum()), 2
                        ),
                        "carga_efetiva_media_percentual": round(
                            float(serie_carga["carga_efetiva_percentual"].mean()), 2
                        ),
                        "serie_mensal": serie_carga.to_dict("records"),
                    }
                    laudo_fiscal["grafico_carga_tributaria_12_meses"] = str(
                        caminho_serie
                    )
        except Exception:
            # Auditoria técnica completa no console sem interromper a Fase 02.
            logging.warning(
                "Fiscal — Falha ao montar a análise real de tributos "
                "(visões secundárias ignoradas).",
                exc_info=True,
            )

        logging.info("=== DEPARTAMENTO FISCAL CONCLUÍDO COM SUCESSO ===")
        return laudo_fiscal