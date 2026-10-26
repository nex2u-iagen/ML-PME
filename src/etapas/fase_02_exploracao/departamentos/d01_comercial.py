"""Módulo de Diagnóstico Exploratório do Departamento Comercial (Fase 2.1).

Implementa os indicadores fundamentais de vendas, concentração de receita
(Curva de Pareto de Clientes), ticket médio por segmento e identificação
de dependência comercial para Pequenas e Médias Empresas (PMEs).
"""

# 'import' traz o módulo 'logging' da biblioteca padrão do Python para registro de
# auditoria e mensagens no console.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' lida com caminhos e pastas no sistema
# operacional de forma orientada a objetos.
# 'import' traz especificamente a classe 'Path' para representar diretórios e arquivos
# em Windows, Linux ou Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para suporte a
# anotações de tipos estáticos (Type Hints).
# 'import' carrega 'Any' (qualquer tipo permitido) e 'Dict' (estrutura de dados de
# dicionário com chave e valor).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca externa de gráficos 'matplotlib'.
# 'as' define o apelido universal 'plt' para encurtar as chamadas de funções gráficas no
# código.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão mundial para criação e manipulação
# de tabelas de dados bidimensionais.
# 'as' define o apelido oficial 'pd' para economizar digitação na manipulação de
# DataFrames.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', construída sobre o matplotlib para
# visualizações estatísticas elegantes.
# 'as' define o apelido clássico 'sns' para estilização visual corporativa.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado no diretório pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos a infraestrutura
# pronta do núcleo.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo modelo estrutural orientado a objetos.
# 'AnalisadorComercial' é o nome da nossa classe em estilo PascalCase (iniciais
# maiúsculas).
# '(BaseDepartamento)' entre parênteses estabelece herança: esta classe herda os
# atributos e ferramentas da classe mãe.
class AnalisadorComercial(BaseDepartamento):
    """Classe responsável pelo diagnóstico de vendas, clientes e produtos do ERP."""

    # 'def' define o método especial construtor '__init__', acionado no momento em que a
    # classe é instanciada na memória.
    # 'self' representa a própria instância acessando seus atributos internos.
    # 'pasta_dados_brutos: Path' é um parâmetro com anotação de tipo que exige o caminho
    # da pasta de dados CSV.
    # 'pasta_relatorios: Path' é o caminho onde os relatórios e imagens deste
    # departamento serão salvos.
    # '-> None' indica que o método construtor não retorna nenhum dado.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento comercial registrando seu nome canônico.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos visuais.
        """
        # 'super().__init__' aciona formalmente o construtor da classe base (mãe)
        # BaseDepartamento.
        # Passamos os diretórios e registramos o nome canônico 'comercial' para criar a
        # subpasta de figuras.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="comercial",
        )

    # 'def' define o método responsável por carregar e cruzar pedidos com a base
    # cadastral de clientes.
    # '-> pd.DataFrame' documenta que o retorno desta função DEVE ser um DataFrame
    # tabular do pandas.
    def carregar_dados_vendas(self) -> pd.DataFrame:
        """Carrega e cruza as transações de pedidos com a base cadastral de clientes.

        Returns:
            pd.DataFrame: Tabela unificada com o histórico comercial do ERP.
        """
        # O operador '/' une os caminhos de diretório de forma nativa e segura para
        # qualquer sistema operacional.
        # 'caminho_pedidos' armazena o caminho do arquivo de pedidos de venda extraído
        # na Fase 01.
        caminho_pedidos = self.pasta_dados_brutos / "erp_pedidos_vendas.csv"

        # 'caminho_clientes' armazena o caminho do arquivo cadastral de clientes da
        # empresa.
        caminho_clientes = self.pasta_dados_brutos / "erp_clientes.csv"

        # 'self.leitor' é a ferramenta herdada da classe base; 'carregar_tabela' lê o
        # arquivo CSV e devolve um DataFrame.
        # 'df_pedidos' recebe a matriz de pedidos em memória RAM.
        df_pedidos = self.leitor.carregar_tabela(caminho_pedidos)

        # 'df_clientes' recebe a matriz cadastral de clientes em memória RAM.
        df_clientes = self.leitor.carregar_tabela(caminho_clientes)

        # 'pd.to_datetime' converte a coluna de texto 'data_pedido' em formato oficial
        # de data e hora do pandas.
        # Isso viabiliza ordenações cronológicas e extrações de ano, mês e dia da
        # semana.
        df_pedidos["data_pedido"] = pd.to_datetime(df_pedidos["data_pedido"])

        # 'pd.merge' realiza a junção relacional (o equivalente ao comando INNER JOIN do
        # SQL) entre as duas tabelas.
        # 'on="id_cliente"' especifica que a chave de ligação de dados é o identificador
        # único do cliente.
        # 'how="inner"' garante que apenas pedidos associados a clientes devidamente
        # cadastrados permaneçam na tabela.
        df_comercial = pd.merge(df_pedidos, df_clientes, on="id_cliente", how="inner")

        # 'logging.info' emite uma mensagem formatada no terminal registrando o sucesso
        # da integração.
        # 'len(df_comercial)' calcula a contagem total inteira de linhas resultantes da
        # junção.
        logging.info(
            "Comercial — Base consolidada com %d transações mapeadas.",
            len(df_comercial),
        )

        # 'return' devolve a tabela unificada pronta para a extração dos indicadores de
        # vendas.
        return df_comercial

    # 'def' define o método responsável por calcular o Ticket Médio (valor médio por
    # pedido) em cada segmento.
    # 'dados: pd.DataFrame' recebe a tabela comercial que acabou de ser consolidada pelo
    # método anterior.
    # '-> Dict[str, float]' indica que o retorno é um dicionário onde a chave é o nome
    # do segmento e o valor é o valor monetário.
    def calcular_ticket_medio_segmento(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula o valor médio desembolsado por pedido em cada segmento da carteira.

        Args:
            dados (pd.DataFrame): Tabela comercial consolidada com pedidos e segmentos.

        Returns:
            Dict[str, float]: Dicionário com os segmentos e seus respectivos tickets
            médios em reais.
        """
        # '.groupby("segmento")' agrupa as linhas da tabela pelo nicho de atuação do
        # cliente (ex.: Varejo, Saúde).
        # '["valor_total"]' seleciona a coluna numérica de faturamento da transação para
        # o cálculo.
        # '.mean()' calcula a Média Aritmética somando os valores e dividindo pelo total
        # de pedidos do grupo.
        # '.round(2)' arredonda o resultado decimal para duas casas após a vírgula
        # (formato monetário em R$).
        # '.to_dict()' converte o resultado do pandas em um dicionário nativo do Python
        # (chave: valor).
        ticket_medio = (
            dados.groupby("segmento")["valor_total"].mean().round(2).to_dict()
        )

        # 'for' cria um laço de repetição percorrendo cada item do dicionário gerado.
        # '.items()' devolve simultaneamente a chave ('segmento') e o valor numérico
        # ('valor').
        for segmento, valor in ticket_medio.items():
            # 'logging.info' imprime no console o ticket médio calculado para cada um
            # dos segmentos.
            logging.info("Comercial — Ticket Médio ['%s']: R$ %.2f", segmento, valor)

        # 'return' entrega o dicionário com os tickets médios calculados para compor o
        # laudo final.
        return ticket_medio

    # 'def' define o método especialista em gerar a Curva de Pareto de Clientes (Regra
    # 80/20).
    # 'caminho_figura' será devolvido como um objeto Path indicando o endereço exato do
    # arquivo PNG gerado.
    def gerar_grafico_pareto_clientes(self, dados: pd.DataFrame) -> Path:
        """Renderiza o gráfico de Pareto demonstrando a concentração de receita nos
        clientes.

        Args:
            dados (pd.DataFrame): Tabela comercial consolidada.

        Returns:
            Path: Caminho físico da imagem exportada no disco em alta resolução (300
            DPI).
        """
        # Agrupa pelo nome fantasia do cliente e soma a coluna 'valor_total' para saber
        # o gasto total de cada um.
        # '.reset_index()' converte o resultado agrupado de volta em um DataFrame com
        # colunas comuns.
        vendas_cliente = (
            dados.groupby("nome_fantasia")["valor_total"].sum().reset_index()
        )

        # '.sort_values()' ordena as linhas de forma decrescente pelo faturamento total
        # (do maior cliente para o menor).
        # 'ascending=False' garante que os maiores clientes fiquem posicionados no topo
        # da lista.
        vendas_cliente = vendas_cliente.sort_values(by="valor_total", ascending=False)

        # 'self.pasta_saida' é o caminho da pasta de figuras do departamento comercial,
        # herdada da classe base.
        # O operador '/' define o nome final do arquivo de imagem que será gravado no
        # disco rígido.
        caminho_figura = self.pasta_saida / "pareto_faturamento_clientes.png"

        # 'plt.subplots()' inicializa uma tela de desenho gráfica; 'figsize=(10, 5)'
        # define 10 polegadas de largura por 5 de altura.
        # 'figura' representa a tela inteira; 'eixo' representa a área interna onde o
        # gráfico de barras será desenhado.
        figura, eixo = plt.subplots(figsize=(10, 5))

        # 'sns.barplot' renderiza o gráfico de barras verticais utilizando a biblioteca
        # Seaborn.
        # 'data=vendas_cliente' informa a tabela de dados que alimenta as barras.
        # 'x="nome_fantasia"' posiciona os nomes dos clientes no eixo horizontal X.
        # 'y="valor_total"' projeta a altura das barras correspondente ao faturamento no
        # eixo vertical Y.
        # 'color="#1f77b4"' aplica a tonalidade azul clássica industrial de alta
        # legibilidade corporativa.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura que configuramos no
        # matplotlib.
        sns.barplot(
            data=vendas_cliente,
            x="nome_fantasia",
            y="valor_total",
            color="#1f77b4",
            ax=eixo,
        )

        # 'eixo.set_title' define o texto do título no topo da imagem com fonte tamanho
        # 13 e espaçamento de 12 pontos.
        eixo.set_title(
            "Concentração de Receita por Cliente (Análise de Pareto 80/20)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo descritivo no eixo horizontal X.
        eixo.set_xlabel("Cliente (Nome Fantasia)", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo financeiro no eixo vertical Y.
        eixo.set_ylabel("Faturamento Total (R$)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' rotaciona os nomes dos clientes em 45
        # graus e alinha à direita.
        # Isso impede que os nomes dos clientes fiquem encavalados ou ilegíveis no
        # rodapé do gráfico.
        plt.xticks(rotation=45, ha="right")

        # 'plt.tight_layout()' faz o ajuste dinâmico automático de margens para não
        # cortar nenhum texto da imagem.
        plt.tight_layout()

        # 'figura.savefig' salva a imagem fisicamente no disco no formato PNG.
        # 'dpi=300' (Dots Per Inch / Pontos por Polegada) garante resolução industrial
        # nítida para impressão e telas 4K.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' destrói o objeto gráfico da memória RAM do computador
        # imediatamente após a gravação.
        # Essa instrução é vital para evitar vazamentos de memória (Memory Leak) em
        # pipelines de dados contínuos.
        plt.close(figura)

        # 'logging.info' confirma no terminal que o gráfico foi renderizado e persistido
        # com sucesso.
        logging.info(
            "Comercial — Gráfico de Pareto exportado para: %s", caminho_figura.name
        )

        # 'return' devolve o caminho físico do arquivo salvo para fins de
        # rastreabilidade e governança.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução de todos os KPIs do departamento comercial em
    # sequência lógica.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo de todos os KPIs comerciais e a geração de figuras
        analíticas.

        Returns:
            Dict[str, Any]: Laudo comercial consolidado com faturamento e tickets
            médios.
        """
        # Emite log marcando o início da perícia comercial da Fase 2.1.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO COMERCIAL (FASE 2.1) ===")

        # Invoca o método interno que carrega e funde pedidos e clientes na memória RAM
        # uma única vez.
        df_vendas = self.carregar_dados_vendas()

        # Dispara o método especialista que calcula o Ticket Médio por segmento de
        # atuação.
        ticket_segmentos = self.calcular_ticket_medio_segmento(df_vendas)

        # Dispara o método especialista que desenha e salva o gráfico de Pareto no
        # disco.
        caminho_grafico = self.gerar_grafico_pareto_clientes(df_vendas)

        # 'float(df_vendas["valor_total"].sum())' calcula o somatório total bruto
        # vendido pela companhia.
        # 'round(..., 2)' arredonda o faturamento total em centavos.
        faturamento_total_bruto = round(float(df_vendas["valor_total"].sum()), 2)

        # 'int(len(df_vendas))' calcula a contagem total inteira de transações
        # registradas no sistema.
        total_pedidos_contados = int(len(df_vendas))

        # 'laudo_comercial' é um dicionário estruturado criado para reunir todos os
        # achados do departamento.
        laudo_comercial = {
            "faturamento_bruto_total": faturamento_total_bruto,
            "total_pedidos_faturados": total_pedidos_contados,
            "ticket_medio_por_segmento": ticket_segmentos,
            "grafico_pareto_clientes": str(caminho_grafico),
        }

        # Emite log registrando o encerramento bem-sucedido do departamento comercial.
        logging.info("=== DEPARTAMENTO COMERCIAL CONCLUÍDO COM SUCESSO ===")

        # 'return' entrega o dicionário com os indicadores para o orquestrador geral do
        # projeto.
        return laudo_comercial
