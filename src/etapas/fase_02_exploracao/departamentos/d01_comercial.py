# 'import' é a palavra-chave reservada do Python para importar módulos e bibliotecas.
# Carrega o módulo 'logging' nativo da biblioteca padrão para registrar eventos
# técnicos no terminal.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e caminhos de
# arquivos de forma orientada a objetos.
# 'import' traz a classe 'Path' para representar diretórios compatíveis com Linux,
# Windows e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' traz 'Any' (que aceita qualquer tipo de valor) e 'Dict' (dicionário
# estruturado de chave e valor).
from typing import Any, Dict

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo
# controle de janelas e telas gráficas.
# 'as' cria o apelido abreviado 'plt' para simplificar as chamadas de funções no
# código.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação de
# tabelas bidimensionais.
# 'as' define o apelido oficial 'pd'.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada em gráficos estatísticos
# corporativos elegantes.
# 'as' define o apelido 'sns'.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' para carregar a classe base
# abstrata.
# 'import' traz a classe 'BaseDepartamento' para herdarmos a infraestrutura
# compartilhada e o adaptador universal.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento

# Importação do extrator de lançamentos reais de PDV (nome do produto, quantidade e
# valor), única fonte capaz de quebrar o faturamento por departamento de varejo.
from src.etapas.fase_02_exploracao.adaptadores.extrator_pdv import (
    carregar_itens_pdv,
)


# 'class' declara uma nova classe sob o paradigma de Orientação a Objetos.
# '(BaseDepartamento)' estabelece herança formal: herda leitor, calculadora,
# visualizador e a fachada do adaptador.
class AnalisadorComercial(BaseDepartamento):
    """Classe responsável pelo diagnóstico de vendas reais com recorte de 12 meses e

    Pareto de Categorias.
    """

    # 'def' define o método especial construtor '__init__', acionado no momento da
    # instanciação da classe.
    # 'self' referencia a própria instância acessando seus atributos internos.
    def __init__(
        self, pasta_dados_brutos: Path, pasta_relatorios: Path
    ) -> None:
        """Inicializa o departamento comercial configurando a governança de diretórios

        setoriais.
        """
        # 'super().__init__' aciona o construtor da classe base BaseDepartamento.
        # Passa as pastas e registra 'comercial' como nome canônico para criar o
        # diretório setorial em relatórios.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="comercial",
            fase_projeto="fase_02",
        )

    # 'def' define o método responsável por carregar a massa de vendas reais através da
    # fachada do adaptador.
    # '-> pd.DataFrame' documenta formalmente que a função devolverá uma matriz tabular
    # do pandas.
    def carregar_dados_vendas(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal a tabela canônica com recorte cronológico

        dos últimos 12 meses.
        """
        # Invoca o método canônico na fachada do adaptador universal, que delega ao
        # ExtratorVendas.
        df_vendas = self.adaptador.obter_visao_vendas_comercial()

        # Validação defensiva: se o DataFrame for nulo ou estiver vazio, interrompe o
        # fluxo com erro explicativo.
        if df_vendas is None or df_vendas.empty:
            # Registra no console corporativo o erro de dados ausentes.
            logging.error(
                "Comercial — Falha crítica: Nenhum faturamento real foi retornado na"
                "janela de 12 meses."
            )
            # Lança exceção formal impedindo o avanço de cálculos com base vazia.
            raise ValueError(
                "Dados comerciais reais não encontrados na janela de análise sob"
                "perícia."
            )

        # Emite log confirmando a volumetria exata de transações incorporadas na janela
        # móvel de 12 meses.
        logging.info(
            "Comercial — Base canônica carregada com %d transações na janela de 12"
            "meses.",
            len(df_vendas),
        )

        # Devolve a matriz tabular canônica pronta para a geração dos indicadores e
        # gráficos.
        return df_vendas

    # 'def' define o método especialista em desenhar a evolução cronológica do
    # faturamento mês a mês.
    def gerar_grafico_evolucao_12_meses(self, dados: pd.DataFrame) -> Path:
        """Renderiza a série temporal de faturamento mês a mês ao longo dos últimos 12

        meses de operação.
        """
        # Agrupa as transações pelo atributo temporal 'ano_mes' e calcula o somatório do
        # faturamento bruto.
        # '.reset_index()' converte a série agrupada de volta em um DataFrame tabular
        # comum.
        vendas_mensais = (
            dados.groupby("ano_mes")["valor_total"].sum().reset_index()
        )

        # '.sort_values(by="ano_mes", ascending=True)' garante a ordenação cronológica
        # crescente no eixo horizontal.
        vendas_mensais = vendas_mensais.sort_values(
            by="ano_mes", ascending=True
        )

        # Constrói o caminho completo da imagem PNG dentro da subpasta setorial
        # 'relatorios/<banco>/fase_02/comercial/'.
        caminho_figura = (
            self.pasta_saida / "evolucao_faturamento_ultimos_12_meses.png"
        )

        # 'plt.subplots(figsize=(10, 5))' inicializa a tela de desenho com proporção 10
        # por 5 polegadas.
        figura, eixo = plt.subplots(figsize=(10, 5))

        # 'sns.barplot(...)' delega a renderização gráfica de barras verticais ao
        # Seaborn.
        # - 'hue="ano_mes"' e 'legend=False': atende ao padrão do Seaborn v0.14+
        # eliminando avisos futuros.
        # - 'palette="Blues_r"': aplica gradiente azul corporativo com contraste
        # elegante para séries temporais.
        sns.barplot(
            data=vendas_mensais,
            x="ano_mes",
            y="valor_total",
            hue="ano_mes",
            palette="Blues_r",
            legend=False,
            ax=eixo,
        )

        # Configura o título principal no topo da imagem com tamanho 13 e padding de 12
        # pontos.
        eixo.set_title(
            "Evolução Mensal do Faturamento Real (Recorte Últimos 12 Meses)",
            fontsize=13,
            pad=12,
        )

        # Configura as legendas dos eixos horizontal e vertical em português.
        eixo.set_xlabel("Ano-Mês de Competência", fontsize=10)
        eixo.set_ylabel("Faturamento Total Faturado (R$)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' inclina os rótulos de data em 45 graus
        # para garantir legibilidade.
        plt.xticks(rotation=45, ha="right")

        # Ajusta automaticamente as margens dinâmicas do Matplotlib para não cortar
        # rótulos de texto.
        plt.tight_layout()

        # Grava a figura física no disco rígido em alta resolução industrial (300 DPI).
        figura.savefig(caminho_figura, dpi=300)

        # Destrói o objeto da tela na memória RAM para prevenir vazamentos de memória
        # (Memory Leak).
        plt.close(figura)

        # Registra no log de auditoria a persistência bem-sucedida do gráfico temporal.
        logging.info(
            "Comercial — Gráfico temporal de 12 meses salvo em: %s",
            caminho_figura.name,
        )

        # Devolve o caminho do arquivo PNG gerado.
        return caminho_figura

    # 'def' define o método responsável por carregar os lançamentos reais de PDV,
    # que trazem o nome do produto por item vendido.
    def carregar_itens_pdv(self) -> pd.DataFrame:
        """Recupera os itens reais lançados no caixa (produto, quantidade, valor).

        Returns:
            pd.DataFrame: Tabela de itens do PDV com a coluna 'departamento'
            classificada. Retorna tabela vazia quando o dataset não possui log de
            auditoria — o chamador decide o plano B.
        """
        # Delega a extração ao extrator especialista apontando para a pasta bruta do
        # dataset ativo (o adaptador já resolveu o diretório correto).
        df_itens = carregar_itens_pdv(self.adaptador.pasta_erp)

        # Confirma no log a volumetria efetivamente disponível para o Pareto.
        if df_itens.empty:
            logging.warning(
                "Comercial — Sem lançamentos de PDV disponíveis; o Pareto por "
                "departamento usará o plano de categorias canônico."
            )
        else:
            logging.info(
                "Comercial — %d itens reais de PDV carregados para o Pareto por "
                "departamento.",
                len(df_itens),
            )

        return df_itens

    # 'def' define o método especialista em desenhar a Curva de Pareto por Categorias
    # de Varejo.
    def gerar_grafico_pareto_categorias(self, dados: pd.DataFrame) -> Path:
        """Renderiza a Curva de Pareto por Departamento/Categoria de Varejo (Açougue,

        Hortifrúti, etc.).
        """
        # Agrupa o faturamento pela categoria real de produto e calcula o montante
        # acumulado de vendas.
        vendas_categoria = (
            dados.groupby("categoria_departamento")["valor_total"]
            .sum()
            .reset_index()
        )

        # '.sort_values(by="valor_total", ascending=False)' ordena as categorias da
        # mais faturada para a menor.
        vendas_categoria = vendas_categoria.sort_values(
            by="valor_total", ascending=False
        )

        # Constrói o caminho completo da imagem dentro da subpasta setorial de relatórios
        # do cliente.
        caminho_figura = self.pasta_saida / "pareto_faturamento_categorias.png"

        # Inicializa a moldura gráfica com 10 polegadas de largura por 5 de altura.
        figura, eixo = plt.subplots(figsize=(10, 5))

        # 'sns.barplot(...)' renderiza o gráfico de barras verticais coloridas por
        # categoria de varejo.
        # - 'palette="mako"': aplica paleta contrastante e visualmente moderna para
        # agrupamentos categóricos.
        sns.barplot(
            data=vendas_categoria,
            x="categoria_departamento",
            y="valor_total",
            hue="categoria_departamento",
            palette="mako",
            legend=False,
            ax=eixo,
        )

        # Define o título principal da visualização no topo da tela gráfica.
        eixo.set_title(
            "Concentração de Receita por Categoria de Varejo (Pareto Real)",
            fontsize=13,
            pad=12,
        )

        # Define os rótulos conceituais dos eixos horizontal e vertical em português.
        eixo.set_xlabel("Departamento / Categoria de Produto", fontsize=10)
        eixo.set_ylabel("Faturamento Total Acumulado (R$)", fontsize=10)

        # 'plt.xticks(rotation=30, ha="right")' inclina os nomes dos departamentos em 30
        # graus para evitar cortes.
        plt.xticks(rotation=30, ha="right")

        # Ajusta dinamicamente as margens do gráfico no Matplotlib.
        plt.tight_layout()

        # Salva o arquivo de imagem no disco com resolução de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # Fecha o objeto da figura no Matplotlib para desalocar imediatamente a memória
        # RAM.
        plt.close(figura)

        # Confirma a gravação do gráfico de Pareto no log de auditoria.
        logging.info(
            "Comercial — Gráfico de Pareto de Categorias salvo em: %s",
            caminho_figura.name,
        )

        # Devolve o caminho físico da figura gravada.
        return caminho_figura

    # 'def' define o método especialista em desenhar o Pareto por DEPARTAMENTO de
    # varejo a partir dos lançamentos reais do PDV.
    def gerar_grafico_pareto_departamentos(self, itens: pd.DataFrame) -> Path:
        """Renderiza a Curva de Pareto da receita quebrada por departamento de varejo.

        Ao contrário do plano de categorias canônico (que depende de uma coluna de
        departamento inexistente na visão de notas), esta visão usa o produto real
        lançado no caixa, classificado lexicalmente em departamentos (Padaria,
        Hortifrúti, Açougue, Bebidas etc.).

        Args:
            itens (pd.DataFrame): Itens reais do PDV com 'departamento' e 'valor'.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        # Agrupa a receita do período por departamento e ordena do maior para o menor.
        receita_departamento = (
            itens.groupby("departamento")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

        # Calcula a participação acumulada (curva de Pareto) em percentual.
        total_periodo = float(receita_departamento.sum())
        participacao_acumulada = (
            receita_departamento.cumsum() / total_periodo * 100 if total_periodo > 0
            else receita_departamento * 0
        )

        # Converte a série em DataFrame tabular para alimentar o gráfico.
        df_pareto = receita_departamento.rename("valor").reset_index()
        df_pareto["acumulado"] = participacao_acumulada.values

        # Constrói o caminho da figura dentro da subpasta 'comercial/'.
        caminho_figura = self.pasta_saida / "pareto_faturamento_por_departamento.png"

        # Moldura gráfica de 10 por 6 polegadas (maior altura para nomes longos).
        figura, eixo = plt.subplots(figsize=(10, 6))

        # Posições inteiras no eixo Y: o item 0 (maior faturamento) fica no TOPO,
        # garantindo a ordem clássica do Pareto de cima para baixo.
        posicoes = list(range(len(df_pareto)))

        # Paleta sequencial equivalente à 'mako' do Seaborn (sem dependência de
        # tipagem categórica, o que evita inversão silenciosa de ordem).
        paleta = sns.color_palette("mako", n_colors=len(df_pareto))

        # Barras horizontais: nomes extensos ('Frios e Laticínios') ficam legíveis.
        eixo.barh(
            posicoes,
            df_pareto["valor"],
            color=paleta,
        )

        # Eixo Y com os nomes reais dos departamentos e ordem decrescente no topo.
        eixo.set_yticks(posicoes)
        eixo.set_yticklabels(df_pareto["departamento"])
        eixo.set_ylim(len(df_pareto) - 0.4, -0.4)

        # Folga à direita para que o rótulo monetário do maior barra não seja cortado.
        eixo.set_xlim(0, float(df_pareto["valor"].max()) * 1.22)

        # Rótulo monetário ao final de cada barra para leitura direta do valor.
        for posicao, valor in enumerate(df_pareto["valor"]):
            eixo.text(
                valor,
                posicao,
                f"  R$ {valor:,.0f}".replace(",", "."),
                ha="left",
                va="center",
                fontsize=9,
            )

        # Eixo superior: linha da participação acumulada (a "curva" do Pareto).
        # 'twiny()' compartilha o eixo Y (posições) e cria um X secundário no topo.
        eixo_acumulado = eixo.twiny()
        eixo_acumulado.plot(
            df_pareto["acumulado"],
            posicoes,
            color="#d62728",
            marker="o",
            linewidth=2,
            label="% acumulado",
        )

        # Referência clássica dos 80% de concentração da Curva de Pareto.
        eixo_acumulado.axvline(
            80, color="#d62728", linestyle="--", linewidth=1, label="Linha 80%"
        )
        eixo_acumulado.set_xlabel("% da Receita Acumulada", fontsize=10)
        eixo_acumulado.set_xlim(0, 105)

        # Legenda combinada deslocada para a área livre central-inferior (à
        # direita das barras pequenas, que permanecem visíveis).
        eixo_acumulado.legend(
            loc="lower left", bbox_to_anchor=(0.30, 0.0), fontsize=8
        )

        # Títulos e rótulos executivos em português.
        eixo.set_title(
            "Concentração de Receita por Departamento de Varejo (Pareto Real — PDV)",
            fontsize=13,
            pad=34,
        )
        eixo.set_xlabel("Faturamento no Período (R$)", fontsize=10)
        eixo.set_ylabel("Departamento de Varejo", fontsize=10)

        # Ajusta as margens dinamicamente e grava em alta resolução industrial.
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)

        # Destrói a figura para liberar a memória RAM do servidor.
        plt.close(figura)

        # Confirma a gravação no log de auditoria.
        logging.info(
            "Comercial — Pareto por departamento salvo em: %s (%d departamentos).",
            caminho_figura.name,
            len(df_pareto),
        )

        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o cálculo das métricas de 12 meses e exporta os gráficos temporal e

        de Pareto.
        """
        # Emite log formal registrando o início da perícia comercial da Fase 2.1.
        logging.info(
            "=== INICIANDO PERÍCIA DO DEPARTAMENTO COMERCIAL (FASE 2.1) ==="
        )

        # 1. Carrega os dados reais de vendas com o recorte móvel de 12 meses via
        # Adaptador Universal.
        df_vendas = self.carregar_dados_vendas()

        # 2. Executa a camada gráfica renderizando a evolução temporal de faturamento
        # mês a mês.
        caminho_grafico_12m = self.gerar_grafico_evolucao_12_meses(df_vendas)

        # 3. Executa a camada gráfica do Pareto: prefere a quebra REAL por
        # departamento de varejo (lançamentos do PDV com nome de produto); quando o
        # dataset não possui log de PDV, cai para o plano de categorias canônico.
        itens_pdv = self.carregar_itens_pdv()
        pareto_por_departamento = not itens_pdv.empty

        if pareto_por_departamento:
            caminho_grafico_pareto = self.gerar_grafico_pareto_departamentos(itens_pdv)
        else:
            caminho_grafico_pareto = self.gerar_grafico_pareto_categorias(df_vendas)

        # Calcula o faturamento total acumulado no período de 12 meses.
        faturamento_total_bruto = round(
            float(df_vendas["valor_total"].sum()), 2
        )

        # Conta a quantidade total de cupons e notas fiscais emitidas na janela móvel.
        total_pedidos_contados = int(len(df_vendas))

        # Estrutura o laudo comercial consolidado para integração no prontuário 360
        # Graus da empresa.
        laudo_comercial = {
            "faturamento_bruto_12_meses": faturamento_total_bruto,
            "total_pedidos_faturados_12m": total_pedidos_contados,
            "grafico_evolucao_12_meses": str(caminho_grafico_12m),
            "grafico_pareto_categorias": str(caminho_grafico_pareto),
        }

        # Enriquece o laudo com a visão departamental real quando ela existir.
        if pareto_por_departamento:
            receita_departamento = (
                itens_pdv.groupby("departamento")["valor"].sum().sort_values(ascending=False)
            )
            laudo_comercial["grafico_pareto_departamentos"] = str(caminho_grafico_pareto)
            laudo_comercial["departamentos_identificados"] = int(receita_departamento.size)
            laudo_comercial["faturamento_pdv_periodo_reais"] = round(
                float(receita_departamento.sum()), 2
            )
            laudo_comercial["periodo_analise_pdv"] = (
                f"{itens_pdv['data'].min():%Y-%m-%d} a {itens_pdv['data'].max():%Y-%m-%d}"
            )
            laudo_comercial["departamento_lider"] = str(receita_departamento.index[0])

        # Emite log confirmando a conclusão bem-sucedida do setor comercial.
        logging.info("=== DEPARTAMENTO COMERCIAL CONCLUÍDO COM SUCESSO ===")

        # Devolve o laudo executivo comercial estruturado.
        return laudo_comercial