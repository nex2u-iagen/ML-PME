"""Módulo de Diagnóstico Exploratório do Departamento de Estoque (Fase 2.4 - CRISP-DM).

Responsabilidade Única: Avaliar a alocação de capital físico do almoxarifado,
calcular a cobertura de estoque e gerar a classificação da Curva ABC, consumindo
exclusivamente os dados reais (saldos e custos) mapeados pelo Adaptador Universal.
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 5].
import logging

# 'from pathlib import Path' provê a manipulação orientada a objetos de pastas no sistema operacional[cite: 5].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para estruturas de dicionários[cite: 5].
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' inicializa o motor de baixo nível para criação de telas e eixos gráficos[cite: 5].
import matplotlib.pyplot as plt

# 'import pandas as pd' carrega a biblioteca estrutural para agregações, ordenações e matemática tabular[cite: 5].
import pandas as pd

# 'import seaborn as sns' importa o framework gráfico para visualizações estéticas corporativas (Curva ABC)[cite: 5].
import seaborn as sns

# Importação da classe base abstrata que injeta ferramentas e o Adaptador Universal por herança[cite: 5].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento

# Importação do extrator de lançamentos reais de PDV — única fonte com nome de
# produto por item vendido (o dump não exporta a tabela de itens de nota).
from src.etapas.fase_02_exploracao.adaptadores.extrator_pdv import carregar_itens_pdv


# 'class AnalisadorEstoque(BaseDepartamento)' especializa o diagnóstico do almoxarifado herdando a infraestrutura[cite: 5].
class AnalisadorEstoque(BaseDepartamento):
    """Classe responsável pelo diagnóstico de armazenagem, capital imobilizado e Curva ABC do ERP[cite: 5]."""

    # 'def __init__(...)' constrói a instância do analisador de estoque registrando a pasta setorial de destino[cite: 5].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de estoque registrando seu nome canônico para criação de diretórios[cite: 5].

        Args:
            pasta_dados_brutos (Path): Diretório isolado contendo as tabelas reais do ERP (ex: mercado_vencedor/)[cite: 5].
            pasta_relatorios (Path): Diretório base de saída onde a subpasta 'estoque/' será criada e mantida[cite: 5].
        """
        # 'super().__init__(...)' aciona o construtor da classe base registrando 'estoque' como identificador canônico[cite: 5].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="estoque",
        )

    # 'def carregar_dados_estoque(...)' delega a busca dos saldos de inventário para o Adaptador Universal[cite: 5].
    def carregar_dados_estoque(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal a tabela canônica contendo o inventário físico e financeiro real[cite: 5].

        Returns:
            pd.DataFrame: Tabela real unificada com id_produto, saldo físico, custo unitário e valor imobilizado[cite: 5].

        Raises:
            ValueError: Se o adaptador não conseguir localizar dados de estoque na base sob perícia[cite: 5].
        """
        # 'self.adaptador.obter_visao_estoque_materiais()' aciona a tradução semântica herdada da classe mãe[cite: 5].
        # O adaptador localizará tabelas como 'erp_prodestoque.csv' e estruturará os dados canônicos[cite: 5].
        df_estoque = self.adaptador.obter_visao_estoque_materiais()

        # Validação defensiva: se o DataFrame retornar vazio, bloqueia a esteira e emite erro crítico no console[cite: 5].
        if df_estoque is None or df_estoque.empty:
            logging.error("Estoque — Falha crítica: Nenhum saldo de materiais real foi retornado pelo Adaptador Universal.")
            raise ValueError("Dados de estoque reais não encontrados na base de dados (dump) sob perícia.")

        # 'logging.info' documenta o sucesso da operação reportando o volume de SKUs carregados no almoxarifado[cite: 5].
        logging.info("Estoque — Base canônica carregada com sucesso contendo %d SKUs físicos reais.", len(df_estoque))

        # Devolve a matriz de inventário pronta para os cálculos de cobertura e Pareto[cite: 5].
        return df_estoque

    # 'def calcular_dias_cobertura(...)' afere o tempo de autonomia da PME considerando o consumo histórico[cite: 5].
    def calcular_dias_cobertura(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Calcula quantos dias o saldo atual do almoxarifado suporta a operação antes de uma ruptura de estoque[cite: 5].

        Dias de Cobertura = Quantidade em Saldo / Consumo Diário Médio.

        Args:
            dados (pd.DataFrame): Tabela de materiais reais com as colunas de saldo e consumo médio[cite: 5].

        Returns:
            pd.DataFrame: Tabela enriquecida com a nova métrica 'dias_cobertura' projetada[cite: 5].
        """
        # '.copy()' isola as alterações em uma cópia independente, prevenindo o erro SettingWithCopyWarning do pandas[cite: 5].
        dados_processados = dados.copy()

        # Calcula a taxa diária dividindo o consumo mensal (30 dias) pela base de projeção[cite: 5].
        consumo_diario = dados_processados["consumo_mensal_medio"] / 30.0

        # Divide o saldo físico pelo consumo projetado. '.round(1)' limita o resultado a uma casa decimal (ex: 15.2 dias)[cite: 5].
        dados_processados["dias_cobertura"] = (dados_processados["quantidade_saldo"] / consumo_diario).round(1)

        # Emite log confirmando que a autonomia operacional de todos os materiais foi aferida com sucesso[cite: 5].
        logging.info("Estoque — Indicador de Dias de Cobertura projetado com sucesso.")

        # Retorna o DataFrame com a coluna de dias de cobertura pronta para análises subsequentes[cite: 5].
        return dados_processados

    # 'def calcular_curva_abc(...)' executa a classificação de Pareto sobre o capital retido em mercadorias[cite: 5].
    def calcular_curva_abc(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Classifica os produtos do armazém em classes A (80%), B (15%) e C (5%) baseando-se no valor imobilizado[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela de posições de estoque com o 'valor_imobilizado' previamente calculado[cite: 5].

        Returns:
            pd.DataFrame: Tabela contendo os produtos ordenados e rotulados matematicamente na coluna 'classe_abc'[cite: 5].
        """
        # '.sort_values(..., ascending=False)' ordena as linhas de forma decrescente pelo capital investido[cite: 5].
        # Garante que as mercadorias mais valiosas da empresa liderem o cálculo cumulativo[cite: 5].
        df_ordenado = dados.sort_values(by="valor_imobilizado", ascending=False).copy()

        # '.cumsum()' (Cumulative Sum) executa a soma cumulativa progressiva dos valores imobilizados linha a linha[cite: 5].
        df_ordenado["valor_acumulado"] = df_ordenado["valor_imobilizado"].cumsum()

        # '.sum()' calcula o total financeiro (100%) retido em todo o estoque da organização[cite: 5].
        total_estoque = float(df_ordenado["valor_imobilizado"].sum())

        # Projeta a soma cumulativa em escala percentual (0 a 100%) dividindo pelo valor total da fábrica[cite: 5].
        df_ordenado["percentual_acumulado"] = (df_ordenado["valor_acumulado"] / total_estoque) * 100

        # Função de roteamento interno: mapeia o percentual acumulado para as letras da Matriz de Pareto[cite: 5].
        def classificar_faixa(percentual: float) -> str:
            # Produtos cuja soma representa até os primeiros 80% do capital retido são a Classe A (Gargalos/Estratégicos)[cite: 5].
            if percentual <= 80.0:
                return "A"
            # Produtos que elevam a soma de 80.01% até 95% do capital recebem a Classe B (Atenção Intermediária)[cite: 5].
            elif percentual <= 95.0:
                return "B"
            # Os produtos restantes, que compõem apenas os 5% finais do valor (mas grande volume físico), são Classe C[cite: 5].
            return "C"

        # '.apply(...)' aciona a função de roteamento linha por linha sobre a coluna de proporção acumulada[cite: 5].
        df_ordenado["classe_abc"] = df_ordenado["percentual_acumulado"].apply(classificar_faixa)

        # Documenta a distribuição da curva de criticidade no console para auditoria do controlador financeiro[cite: 5].
        logging.info(
            "Estoque — Curva ABC concluída. Itens Classe A: %d | Classe B: %d | Classe C: %d.",
            (df_ordenado["classe_abc"] == "A").sum(),
            (df_ordenado["classe_abc"] == "B").sum(),
            (df_ordenado["classe_abc"] == "C").sum(),
        )

        # Devolve a tabela devidamente estratificada pelas faixas de criticidade gerenciais[cite: 5].
        return df_ordenado

    # 'def gerar_grafico_curva_abc(...)' renderiza o diagrama visual de capital por classe de criticidade[cite: 5].
    def gerar_grafico_curva_abc(self, dados: pd.DataFrame) -> Path:
        """Renderiza o gráfico de barras categorizado pela classificação ABC de retenção financeira[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela contendo os materiais reais, os valores imobilizados e as classes (A/B/C)[cite: 5].

        Returns:
            Path: Endereço do arquivo PNG persistido em alta resolução geométrica (300 DPI) no disco[cite: 5].
        """
        # Limita visualmente o gráfico aos 25 produtos mais valiosos para impedir poluição ou quebra de escala no eixo X[cite: 5].
        if len(dados) > 25:
            dados = dados.head(25)

        # Monta a rota de destino do gráfico concatenando o nome do arquivo ao diretório setorial 'estoque/'[cite: 5].
        caminho_figura = self.pasta_saida / "curva_abc_valor_imobilizado.png"

        # 'plt.subplots(figsize=(10, 5))' dimensiona a tela do Matplotlib para 10 polegadas de largura por 5 de altura[cite: 5].
        figura, eixo = plt.subplots(figsize=(10, 5))

        # Define um dicionário cromático rígido: Vermelho crítico para A, Laranja alerta para B, Azul padrão para C[cite: 5].
        paleta_cores = {"A": "#d62728", "B": "#ff7f0e", "C": "#1f77b4"}

        # 'sns.barplot(...)' delega ao Seaborn o desenho das barras verticais utilizando os dados da Curva ABC[cite: 5].
        # - 'hue="classe_abc"' e 'palette=paleta_cores': garante que cada barra respeite a cor estipulada no dicionário[cite: 5].
        # - 'dodge=False': impede deslocamentos laterais indesejados nas barras por efeito de agrupamento[cite: 5].
        sns.barplot(
            data=dados,
            x="descricao_produto",
            y="valor_imobilizado",
            hue="classe_abc",
            palette=paleta_cores,
            dodge=False,
            ax=eixo,
        )

        # 'eixo.set_title(...)' crava o cabeçalho executivo no topo da imagem com tamanho 13 e padding 12[cite: 5].
        eixo.set_title("Curva ABC de Estoque por Valor Financeiro Imobilizado (R$)", fontsize=13, pad=12)

        # Rótulos textuais em português do Brasil parametrizando os eixos cartesiano horizontal e vertical[cite: 5].
        eixo.set_xlabel("Produto Cadastrado (Descrição / SKU)", fontsize=10)
        eixo.set_ylabel("Capital Retido (R$)", fontsize=10)

        # 'plt.xticks(...)' executa rotação ortogonal leve (45 graus) e alinhamento à direita nos nomes dos produtos[cite: 5].
        # Essa prática impede sobreposição de texto em nomes longos de SKUs do supermercado[cite: 5].
        plt.xticks(rotation=45, ha="right")

        # 'plt.tight_layout()' instrui o motor a espremer/expandir as margens dinamicamente para preservar todo o texto[cite: 5].
        plt.tight_layout()

        # '.savefig(caminho, dpi=300)' serializa a imagem em pixels na unidade de armazenamento com qualidade para impressão gráfica[cite: 5].
        figura.savefig(caminho_figura, dpi=300)

        # '.close(figura)' emite o comando de expurgo da memória RAM, vital para prevenir Memory Leaks no servidor[cite: 5].
        plt.close(figura)

        # 'logging.info' consolida a auditoria registrando o salvamento bem-sucedido da peça visual no log de execução[cite: 5].
        logging.info("Estoque — Gráfico da Curva ABC exportado com sucesso para: %s", caminho_figura.name)

        # Retorna o ponteiro físico para incorporação da imagem em relatórios subsequentes[cite: 5].
        return caminho_figura

    # 'def' define o método responsável por carregar os lançamentos reais de PDV
    # (nome do produto, quantidade, unidade e valor) para a análise de giro.
    def carregar_itens_pdv(self) -> pd.DataFrame:
        """Recupera os itens reais lançados no caixa para a análise de produtos.

        Returns:
            pd.DataFrame: Tabela de itens do PDV (produto, quantidade, unidade,
            valor). Retorna tabela vazia quando o dataset não possui log de
            auditoria — o chamador aciona então o plano B (Curva ABC).
        """
        # Delega a extração ao extrator especialista apontando para a pasta bruta
        # do dataset ativo (resolvida pelo adaptador universal).
        df_itens = carregar_itens_pdv(self.adaptador.pasta_erp)

        # Confirma no log a volumetria efetivamente disponível para o giro.
        if df_itens.empty:
            logging.warning(
                "Estoque — Sem lançamentos de PDV; a análise de produtos usará "
                "o plano de Curva ABC (valor imobilizado)."
            )
        else:
            logging.info(
                "Estoque — %d itens reais de PDV carregados para a análise de "
                "giro por produto.",
                len(df_itens),
            )

        return df_itens

    # 'def calcular_top_10_produtos(...)' apura o giro dos produtos mais vendidos[cite: 5].
    def calcular_top_10_produtos(
        self, itens: pd.DataFrame
    ) -> tuple[Dict[str, Any], pd.DataFrame]:
        """Ranqueia os 10 produtos que mais faturaram no período de log do PDV.

        Args:
            itens (pd.DataFrame): Itens reais do PDV com produto, quantidade,
            unidade, valor e ano_mes.

        Returns:
            tuple: dicionário-resumo (período, totais, top_10) e o DataFrame do
            Top 10 pronto para plotagem.
        """
        # Base vazia devolve resumo vazio (o chamador aciona o plano B).
        if itens.empty:
            return {}, pd.DataFrame()

        # Agrupa por produto SOMENTE (nomes já normalizados pelo extrator).
        agrupado = itens.groupby("produto").agg(
            faturamento=("valor", "sum"),
            lancamentos=("valor", "count"),
        )

        # Volume físico: soma a quantidade por unidade e assume a unidade
        # dominante do produto (um SKU é vendido em uma única unidade de
        # comercialização — KG, UN, LT etc.).
        por_unidade = (
            itens.groupby(["produto", "unidade"])["quantidade"].sum().reset_index()
        )
        por_unidade = por_unidade.sort_values(
            "quantidade", ascending=False
        ).drop_duplicates("produto")
        por_unidade = por_unidade.set_index("produto")

        agrupado["quantidade"] = por_unidade["quantidade"]
        agrupado["unidade"] = por_unidade["unidade"]
        agrupado["quantidade"] = agrupado["quantidade"].fillna(0.0)

        # Ordena do maior para o menor faturamento e recorta os 10 primeiros.
        agrupado = agrupado.sort_values("faturamento", ascending=False)
        df_top_10 = agrupado.head(10).copy()

        # Participação percentual de cada produto no faturamento total do período.
        total_periodo = float(agrupado["faturamento"].sum())
        df_top_10["participacao_percentual"] = (
            (df_top_10["faturamento"] / total_periodo * 100).round(1)
            if total_periodo > 0
            else 0.0
        )

        # Resumo executivo do giro de produtos no período de log.
        resumo = {
            "periodo_analise": (
                f"{itens['data'].min():%Y-%m-%d} a {itens['data'].max():%Y-%m-%d}"
            ),
            "faturamento_periodo_reais": round(total_periodo, 2),
            "produtos_distintos_vendidos": int(len(agrupado)),
            "top_10_produtos": [
                {
                    "produto": str(produto),
                    "faturamento_reais": round(float(linha["faturamento"]), 2),
                    "volume": round(float(linha["quantidade"]), 2),
                    "unidade": str(linha["unidade"]),
                    "participacao_percentual": float(
                        linha["participacao_percentual"]
                    ),
                }
                for produto, linha in df_top_10.iterrows()
            ],
        }

        logging.info(
            "Estoque — Giro apurado: %d produtos distintos, R$ %.2f no período "
            "%s. Líder: %s.",
            resumo["produtos_distintos_vendidos"],
            resumo["faturamento_periodo_reais"],
            resumo["periodo_analise"],
            resumo["top_10_produtos"][0]["produto"],
        )
        return resumo, df_top_10

    # 'def gerar_grafico_top_10_produtos(...)' desenha o ranking de giro dos produtos[cite: 5].
    def gerar_grafico_top_10_produtos(
        self, df_top: pd.DataFrame, resumo: Dict[str, Any]
    ) -> Path:
        """Renderiza barras horizontais dos 10 produtos que mais faturaram.

        Args:
            df_top (pd.DataFrame): Top 10 com faturamento, quantidade, unidade
            e participação percentual.
            resumo (Dict[str, Any]): Resumo com período e totais consolidados.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        # Prepara a tabela em ordem crescente (maior faturamento fica no topo).
        df_plot = df_top.reset_index().sort_values(by="faturamento", ascending=True)

        # Constrói o caminho do arquivo dentro da subpasta 'estoque/'.
        caminho_figura = self.pasta_saida / "top_10_produtos_giro.png"

        # Remove a Curva ABC antiga quando ela existir: a visão de produto passa
        # a ser a principal e uma figura obsoleta confundiria o leitor.
        figura_abc_antiga = self.pasta_saida / "curva_abc_valor_imobilizado.png"
        if figura_abc_antiga.exists():
            figura_abc_antiga.unlink()
            logging.info(
                "Estoque — Figura obsoleta da Curva ABC removida (%s).",
                figura_abc_antiga.name,
            )

        # Moldura de 10 por 6 polegadas para nomes de produto extensos.
        figura, eixo = plt.subplots(figsize=(10, 6))

        # Posições inteiras: item 0 na base, maior faturamento no topo.
        posicoes = list(range(len(df_plot)))

        # Barras do faturamento por produto na paleta corporativa padrão.
        eixo.barh(
            posicoes,
            df_plot["faturamento"],
            color=sns.color_palette("mako", n_colors=len(df_plot)),
        )

        # Rótulos dos produtos no eixo Y (nomes reais lançados no PDV).
        eixo.set_yticks(posicoes)
        eixo.set_yticklabels(df_plot["produto"], fontsize=9)

        # Folga à direita para o rótulo composto (valor, volume e participação).
        maior_faturamento = (
            float(df_plot["faturamento"].max()) if len(df_plot) else 1.0
        )
        eixo.set_xlim(0, maior_faturamento * 1.75)

        # Rótulo único por linha: faturamento · volume · participação percentual.
        for posicao, (_, linha) in enumerate(df_plot.iterrows()):
            faturamento = (
                f"{linha['faturamento']:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            volume = (
                f"{linha['quantidade']:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            rotulo = (
                f"  R\\$ {faturamento}  ·  {volume} {linha['unidade']}"
                f"  ·  {linha['participacao_percentual']:.1f}%"
            )
            eixo.text(
                linha["faturamento"],
                posicao,
                rotulo,
                ha="left",
                va="center",
                fontsize=8.5,
                fontweight="bold",
            )

        # Título com período e consolidação do faturamento analisado.
        eixo.set_title(
            "Top 10 Produtos por Faturamento — Giro Real do PDV\n"
            f"Período {resumo['periodo_analise']}  ·  "
            f"Faturamento total: R\\$ "
            + (
                f"{resumo['faturamento_periodo_reais']:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            fontsize=12,
            pad=12,
        )

        # Rótulos executivos dos eixos.
        eixo.set_xlabel(
            "Faturamento do Período (R$) — rótulo: volume e participação %",
            fontsize=10,
        )
        eixo.set_ylabel("Produto (nome real do PDV)", fontsize=10)

        # Ajuste dinâmico de margens e gravação em alta resolução (300 DPI).
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)

        # Liberação imediata do buffer gráfico na memória RAM.
        plt.close(figura)

        logging.info(
            "Estoque — Gráfico Top 10 de produtos (giro) salvo em: %s",
            caminho_figura.name,
        )
        return caminho_figura

    # 'def executar_diagnostico_completo(...)' honra a obrigação arquitetural exigida pela BaseDepartamento[cite: 5].
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena em sequência a classificação ABC, o cálculo de dias de autonomia e as plotagens visuais[cite: 5].

        Returns:
            Dict[str, Any]: Prontuário executivo da gestão de almoxarifado contendo as métricas de capital e caminho da imagem[cite: 5].
        """
        # Emite log formal informando ao orquestrador geral o engajamento operacional do analista de suprimentos[cite: 5].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE ESTOQUE (FASE 2.4) ===")

        # 1. Carrega as posições financeiras e físicas de estoque, delegando a leitura ao Adaptador Universal de ERPs[cite: 5].
        df_bruto = self.carregar_dados_estoque()

        # 2. Executa a camada matemática tabular para projetar a autonomia operacional (dias de cobertura)[cite: 5].
        df_cobertura = self.calcular_dias_cobertura(df_bruto)

        # 3. Executa a camada estatística para estratificação de retenção de caixa (Curva ABC Financeira)[cite: 5].
        df_abc = self.calcular_curva_abc(df_cobertura)

        # 4. Executa a camada visual renderizando a Curva ABC colorida e persistindo no disco[cite: 5].
        caminho_grafico = self.gerar_grafico_curva_abc(df_abc)

        # 'df_abc["valor_imobilizado"].sum()' soma a montanha total de dinheiro alocada no estoque da PME[cite: 5].
        # 'round(..., 2)' formata em precisão de duas casas monetárias padrão (R$)[cite: 5].
        total_capital = round(float(df_abc["valor_imobilizado"].sum()), 2)

        # 'len(df_abc)' apura a cardinalidade de SKUs (Stock Keeping Units) mantidos sob a gestão do armazém[cite: 5].
        total_skus = int(len(df_abc))

        # 'df_abc["dias_cobertura"].mean()' traça a médica aritmética simples da autonomia geral de produtos da empresa[cite: 5].
        media_cobertura = round(float(df_abc["dias_cobertura"].mean()), 1)

        # Dicionário serializável em JSON reunindo todos os indicadores estratégicos de saúde logística da companhia[cite: 5].
        laudo_estoque = {
            "capital_total_imobilizado_reais": total_capital,
            "total_skus_cadastrados": total_skus,
            "media_dias_cobertura_geral": media_cobertura,
            "grafico_curva_abc": str(caminho_grafico),
        }

        # 5. VISÃO PRINCIPAL: análise de produtos (giro real do PDV). Quando o
        # dataset possui log de caixa, ela SUBSTITUI a Curva ABC como gráfico
        # principal do departamento; sem log, a ABC permanece como plano B.
        # Bloco isolado em try/except para uma falha secundária não derrubar a
        # Fase 02 inteira.
        try:
            itens_pdv = self.carregar_itens_pdv()
            if not itens_pdv.empty:
                resumo_produtos, df_top_produtos = self.calcular_top_10_produtos(
                    itens_pdv
                )
                if not df_top_produtos.empty:
                    caminho_produtos = self.gerar_grafico_top_10_produtos(
                        df_top_produtos, resumo_produtos
                    )
                    # A figura da Curva ABC deixa de ser a principal do laudo.
                    laudo_estoque.pop("grafico_curva_abc", None)
                    laudo_estoque["top_10_produtos"] = resumo_produtos
                    laudo_estoque["grafico_top_10_produtos"] = str(caminho_produtos)
        except Exception:
            # Auditoria técnica completa no console sem interromper a Fase 02.
            logging.warning(
                "Estoque — Falha ao montar a análise de produtos do PDV "
                "(mantida a Curva ABC como plano B).",
                exc_info=True,
            )

        # Emite sinalização no console confirmando o sucesso de todas as etapas estatísticas e gráficas[cite: 5].
        logging.info("=== DEPARTAMENTO DE ESTOQUE CONCLUÍDO COM SUCESSO ===")

        # Retorna o laudo compilado para integração no prontuário 360 Graus do Orquestrador Raio-X[cite: 5].
        return laudo_estoque