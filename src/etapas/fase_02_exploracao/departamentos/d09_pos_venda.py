"""Módulo de Diagnóstico Exploratório do Departamento de Pós-Venda (Fase 2.9).

Implementa a apuração do Tempo Médio de Resolução de Chamados (MTTR),
a taxa de resolução de tickets, o índice de satisfação do cliente (CSAT)
e a distribuição de motivos de reclamações e atritos para PMEs.
"""

# 'import' é a instrução padrão do Python para trazer bibliotecas e recursos de código
# externos ou nativos.
# Importa o módulo 'logging' nativo para emitir mensagens no console com registro
# profissional de data e hora.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos de
# forma orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de pastas compatíveis com
# Windows, Linux e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' carrega 'Any' (aceita qualquer tipo de objeto) e 'Dict' (dicionário
# estruturado com chaves e valores).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo
# controle de telas e figuras gráficas.
# 'as' define o atalho universal 'plt' para encurtar a sintaxe na criação de gráficos.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação
# tabular de matrizes e dados.
# 'as' define o atalho clássico 'pd' para facilitar operações sobre DataFrames e Series.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada na renderização de
# gráficos estatísticos corporativos.
# 'as' define o atalho 'sns' para estilização visual.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado na pasta pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos o leitor e
# ferramentas do núcleo compartilhado.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'AnalisadorPosVenda' é o nome da nossa classe especializada em auditoria de
# atendimento, em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses define herança: esta classe herda os recursos e
# o leitor da classe mãe.
class AnalisadorPosVenda(BaseDepartamento):
    """Classe responsável pelo diagnóstico de chamados de suporte, MTTR e atrito de
    clientes no ERP.
    """

    # 'def' define o método especial construtor '__init__', executado no instante em que
    # o objeto é criado na memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_dados_brutos: Path' é o parâmetro com anotação de tipo que exige o caminho
    # da pasta de dados CSV.
    # 'pasta_relatorios: Path' é o caminho raiz onde os laudos e imagens deste
    # departamento serão gravados.
    # '-> None' documenta formalmente que o método inicializador não retorna dados.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de pós-venda registrando a subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona formalmente o construtor da classe base mãe
        # BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'pos_venda' para criar a
        # subpasta de figuras no disco.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="pos_venda",
        )

    # 'def' define o método responsável por carregar tickets de suporte e chamados do
    # SAC a partir do disco rígido.
    # '-> pd.DataFrame' documenta que a função devolverá uma matriz tabular
    # bidimensional do pandas.
    def carregar_dados_pos_venda(self) -> pd.DataFrame:
        """Carrega ou simula a tabela de tickets de atendimento, motivos de chamados e
        tempos de solução.

        Returns:
            pd.DataFrame: Tabela contendo chamado, cliente, motivo, horas para
            resolução, status e satisfação.
        """
        # O operador '/' une os caminhos de forma nativa via Pathlib, gerando o endereço
        # exato do arquivo CSV de SAC.
        caminho_sac = self.pasta_dados_brutos / "erp_sac_chamados.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo existe.
        # 'if not' faz a checagem defensiva: se o arquivo não existir, geramos uma base
        # didática representativa da PME.
        if not caminho_sac.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência do pós-venda foi iniciada.
            logging.info(
                "Pós-Venda — Base não localizada. Gerando histórico de chamados de"
                "suporte sintéticos..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') contendo listas
            # estruturadas com chamados de atendimento.
            dados_simulados = {
                # Lista de códigos numéricos de identificação única de cada chamado ou
                # ticket aberto no SAC.
                "id_chamado": [
                    701,
                    702,
                    703,
                    704,
                    705,
                    706,
                    707,
                    708,
                    709,
                    710,
                ],
                # Código de identificação do cliente que abriu a solicitação de suporte.
                "id_cliente": [
                    101,
                    103,
                    104,
                    102,
                    105,
                    108,
                    106,
                    101,
                    107,
                    104,
                ],
                # Categoria ou motivo primário que motivou o contato do cliente com o
                # suporte da PME.
                "motivo_chamado": [
                    "Atraso na Entrega",
                    "Produto com Avaria",
                    "Divergência na Nota Fiscal",
                    "Dúvida Operacional",
                    "Produto com Avaria",
                    "Atraso na Entrega",
                    "Divergência na Nota Fiscal",
                    "Dúvida Operacional",
                    "Atraso na Entrega",
                    "Cobrança Indevida",
                ],
                # Tempo total decorrido entre a abertura do chamado e a sua conclusão
                # final medido em horas corridas.
                "tempo_resolucao_horas": [
                    48.0,
                    72.0,
                    12.0,
                    4.0,
                    96.0,
                    52.0,
                    18.0,
                    6.0,
                    64.0,
                    24.0,
                ],
                # Situação atual do chamado no fluxo de suporte (Resolvido ou Em
                # Aberto).
                "status_chamado": [
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Em Aberto",
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Em Aberto",
                    "Resolvido",
                ],
                # Nota de satisfação atribuída pelo cliente ao atendimento em escala de
                # 1 a 5 (CSAT).
                "nota_satisfacao_csat": [
                    3,
                    2,
                    4,
                    5,
                    1,
                    3,
                    4,
                    5,
                    2,
                    4,
                ],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_sac = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores do atendimento.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_sac.to_csv(caminho_sac, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_sac = self.leitor.carregar_tabela(caminho_sac)

        # 'logging.info' imprime no console o total de tickets consolidados para a
        # auditoria de pós-venda.
        logging.info(
            "Pós-Venda — Base consolidada com %d chamados auditados.",
            len(df_sac),
        )

        # 'return' devolve a matriz tabular pronta para os cálculos de indicadores de
        # atendimento.
        return df_sac

    # KPI 84: Tempo Médio de Resolução de Chamados (MTTR — Mean Time to Resolution em
    # Horas).
    # 'def' define o método especialista em calcular a agilidade e a taxa de resolução
    # de problemas do suporte.
    def calcular_metricas_atendimento(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula o MTTR, a taxa de resolução de chamados e a média de satisfação do
        cliente (CSAT).

        MTTR (horas) = Média do tempo de resolução de chamados encerrados.
        Taxa de Resolução (%) = (Chamados com Status 'Resolvido' / Total de Chamados) *
        100.
        CSAT Médio = Média aritmética das notas de satisfação atribuídas pelos clientes
        (escala 1 a 5).

        Args:
            dados (pd.DataFrame): Tabela contendo histórico de chamados, tempos e notas
            de satisfação.

        Returns:
            Dict[str, float]: Dicionário contendo MTTR em horas, taxa de resolução e
            nota média CSAT.
        """
        # Filtra os chamados que já foram concluídos para calcular o tempo de
        # atendimento real da equipe.
        chamados_resolvidos = dados[dados["status_chamado"] == "Resolvido"]

        # '.mean()' calcula a média aritmética de horas para resolver um problema;
        # 'float()' garante formato numérico.
        # O operador ternário 'if len(chamados_resolvidos) > 0 else 0.0' previne erros
        # de divisão em bases vazias.
        mttr_horas = (
            float(chamados_resolvidos["tempo_resolucao_horas"].mean())
            if len(chamados_resolvidos) > 0
            else 0.0
        )

        # 'int(len(dados))' conta a quantidade total de tickets abertos no período.
        total_chamados = int(len(dados))

        # 'int(len(chamados_resolvidos))' conta quantos tickets foram solucionados com
        # sucesso.
        total_resolvidos = int(len(chamados_resolvidos))

        # Calcula a taxa percentual de chamados resolvidos dividindo os solucionados
        # pelo total recebido.
        taxa_resolucao = (
            (total_resolvidos / total_chamados) * 100 if total_chamados > 0 else 0.0
        )

        # '.mean()' calcula a nota média de satisfação do cliente na escala de 1 a 5
        # (CSAT).
        csat_medio = (
            float(dados["nota_satisfacao_csat"].mean()) if total_chamados > 0 else 0.0
        )

        # 'laudo_atendimento' organiza os indicadores vitais de atendimento para o
        # relatório executivo.
        laudo_atendimento = {
            # 'round(..., 1)' arredonda o tempo médio de resolução (MTTR) em horas.
            "mttr_horas": round(mttr_horas, 1),
            # 'round(..., 2)' arredonda a taxa percentual de resolução da equipe de
            # pós-venda (%).
            "taxa_resolucao_percentual": round(taxa_resolucao, 2),
            # 'round(..., 2)' arredonda a média da nota de satisfação CSAT (1 a 5).
            "csat_medio_escala_5": round(csat_medio, 2),
            # Registra o volume total de chamados avaliados na auditoria.
            "total_chamados_auditados": total_chamados,
        }

        # 'logging.info' imprime as métricas no console para auditoria operacional de
        # qualidade e suporte.
        logging.info(
            "Pós-Venda — MTTR: %.1f horas | Resolução: %.2f%% | CSAT Médio: %.2f/5.0.",
            laudo_atendimento["mttr_horas"],
            laudo_atendimento["taxa_resolucao_percentual"],
            laudo_atendimento["csat_medio_escala_5"],
        )

        # 'return' devolve o dicionário estruturado com as métricas de qualidade do
        # suporte.
        return laudo_atendimento

    # KPI 83: Distribuição dos Motivos de Reclamações e Causas-Raiz de Atrito.
    # 'def' define o método especialista em renderizar o gráfico de barras horizontais
    # com os maiores motivos de atrito.
    def gerar_grafico_motivos_chamados(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras destacando a incidência de cada motivo de
        reclamação no suporte.

        Args:
            dados (pd.DataFrame): Tabela contendo histórico de chamados e motivos de
            abertura.

        Returns:
            Path: Endereço físico do arquivo de imagem exportado em alta resolução (300
            DPI).
        """
        # '.groupby("motivo_chamado")' agrupa os tickets pela categoria do problema
        # relatado pelo cliente.
        # '["id_chamado"].count()' conta a frequência absoluta de ocorrências
        # registradas para cada motivo.
        # '.reset_index()' converte o resultado em um DataFrame com colunas
        # convencionais do pandas.
        motivos_agrupados = (
            dados.groupby("motivo_chamado")["id_chamado"].count().reset_index()
        )

        # Renomeia a coluna agregada para 'total_ocorrencias' para manter clareza
        # semântica no gráfico.
        motivos_agrupados.columns = ["motivo_chamado", "total_ocorrencias"]

        # '.sort_values()' ordena os motivos de forma decrescente (o problema mais
        # frequente fica no topo).
        motivos_agrupados = motivos_agrupados.sort_values(
            by="total_ocorrencias", ascending=False
        )

        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/pos_venda/', criada
        # pelo construtor base.
        caminho_figura = self.pasta_saida / "motivos_reclamacao_sac.png"

        # 'plt.subplots()' inicializa uma moldura gráfica com 9 polegadas de largura por
        # 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras horizontais no Seaborn representando o volume
        # de queixas por motivo.
        # 'data=motivos_agrupados' fornece a tabela com as contagens consolidadas.
        # 'y="motivo_chamado"' posiciona os nomes dos problemas no eixo vertical para
        # facilitar a leitura dos textos.
        # 'x="total_ocorrencias"' projeta o comprimento das barras correspondente à
        # quantidade de chamados.
        # 'color="#e377c2"' aplica uma tonalidade rosa/magenta suave para indicar áreas
        # de relacionamento e acolhimento.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura configurada no
        # matplotlib.
        sns.barplot(
            data=motivos_agrupados,
            y="motivo_chamado",
            x="total_ocorrencias",
            color="#e377c2",
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Principais Motivos de Chamados e Atrito no Pós-Venda (SAC)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo descritivo no eixo horizontal X em contagem
        # física de chamados.
        eixo.set_xlabel("Quantidade de Chamados Abertos", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo descritivo no eixo vertical Y em português.
        eixo.set_ylabel("Motivo da Reclamação / Dúvida", fontsize=10)

        # 'plt.tight_layout()' faz o ajuste dinâmico automático de margens para não
        # cortar legendas da imagem.
        plt.tight_layout()

        # 'figura.savefig' grava o arquivo físico no disco rígido em resolução
        # industrial de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa e destrói o objeto gráfico da memória RAM para
        # prevenir vazamentos de memória.
        plt.close(figura)

        # 'logging.info' confirma no terminal que o gráfico foi renderizado e persistido
        # com sucesso.
        logging.info("Pós-Venda — Gráfico de motivos salvo em: %s", caminho_figura.name)

        # 'return' devolve o caminho físico do arquivo gravado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todas as rotinas periciais de
    # atendimento e suporte.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo do MTTR, do CSAT e a persistência dos gráficos do
        pós-venda.

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento de pós-venda.
        """
        # Emite log anunciando o início oficial da perícia de pós-venda da Fase 2.9.
        logging.info(
            "=== INICIANDO PERÍCIA DO DEPARTAMENTO DE PÓS-VENDA (FASE 2.9) ==="
        )

        # Invoca o método interno que carrega e valida os chamados na memória RAM uma
        # única vez.
        df_sac = self.carregar_dados_pos_venda()

        # Executa o cálculo das métricas de atendimento (MTTR, taxa de resolução e nota
        # CSAT).
        laudo_metricas = self.calcular_metricas_atendimento(df_sac)

        # Renderiza e salva o gráfico com os principais motivos de reclamação no disco.
        caminho_grafico = self.gerar_grafico_motivos_chamados(df_sac)

        # 'int(df_sac["id_cliente"].nunique())' conta a quantidade de clientes distintos
        # que abriram chamados.
        total_clientes_reclamantes = int(df_sac["id_cliente"].nunique())

        # 'laudo_pos_venda' é o dicionário estruturado que consolida o laudo de
        # atendimento da PME.
        laudo_pos_venda = {
            # Incorpora as métricas de tempo de resposta, resolução e satisfação
            # calculadas.
            "metricas_atendimento": laudo_metricas,
            # Registra o número de clientes distintos atendidos no período.
            "total_clientes_com_chamados": total_clientes_reclamantes,
            # Registra o caminho do arquivo de imagem exportado para visualização em
            # relatórios ou BI.
            "grafico_motivos_chamados": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento da auditoria de pós-venda.
        logging.info("=== DEPARTAMENTO DE PÓS-VENDA CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de pós-venda para o orquestrador geral do
        # projeto.
        return laudo_pos_venda
