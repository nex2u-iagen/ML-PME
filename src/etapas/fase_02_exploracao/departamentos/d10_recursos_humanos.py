"""Módulo de Diagnóstico Exploratório do Departamento de RH (Fase 2.10).

Implementa a apuração da relação Custo da Folha sobre a Receita Bruta,
a Taxa de Rotatividade de Pessoal (Turnover), a Produtividade Média
por Colaborador e a distribuição de despesas salariais por setor para PMEs.
"""

# 'import' é a palavra-chave reservada do Python para carregar bibliotecas e módulos
# nativos ou externos.
# Carrega o módulo 'logging' da biblioteca padrão para exibir mensagens com carimbo de
# auditoria no terminal.
import logging

# 'from' indica o módulo de origem; 'pathlib' manipula diretórios e arquivos de forma
# orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de disco de modo compatível
# entre sistemas operacionais.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' carrega 'Any' (aceita qualquer tipo de valor) e 'Dict' (dicionário
# estruturado com chaves e valores).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo
# controle de janelas e telas gráficas.
# 'as' define o apelido universal 'plt' para encurtar a sintaxe na criação de gráficos.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão mundial para criação e manipulação
# de tabelas de dados.
# 'as' define o apelido clássico 'pd' para facilitar operações sobre matrizes e
# DataFrames.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada na renderização de
# gráficos estatísticos corporativos.
# 'as' define o apelido 'sns'.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado na pasta pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos a infraestrutura
# pronta do núcleo compartilhado.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'AnalisadorRecursosHumanos' é o nome da nossa classe especializada em auditoria de
# pessoal, em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses estabelece herança: esta classe herda os
# recursos e o leitor da classe mãe.
class AnalisadorRecursosHumanos(BaseDepartamento):
    """Classe responsável pelo diagnóstico de folha salarial, turnover e
    produtividade de pessoas no ERP.
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
        """Inicializa o departamento de recursos humanos registrando a subpasta
        dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona formalmente o construtor da classe base mãe
        # BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'recursos_humanos' para criar
        # a subpasta de figuras.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="recursos_humanos",
        )

    # 'def' define o método responsável por carregar colaboradores e folhas de pagamento
    # do disco rígido.
    # '-> pd.DataFrame' documenta que a função devolverá uma matriz tabular
    # bidimensional do pandas.
    def carregar_dados_rh(self) -> pd.DataFrame:
        """Carrega ou simula a tabela de colaboradores, salários, setores e status de
        vínculo empregatício.

        Returns:
            pd.DataFrame: Tabela contendo matrícula, cargo, setor, salário base,
            encargos e status ativo/demitido.
        """
        # O operador '/' une os caminhos de forma nativa via Pathlib, gerando o endereço
        # exato do arquivo CSV de RH.
        caminho_rh = self.pasta_dados_brutos / "erp_funcionarios_folha.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo existe.
        # 'if not' faz a checagem defensiva: se o arquivo não existir, geramos uma base
        # didática representativa da PME.
        if not caminho_rh.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência de RH foi iniciada.
            logging.info(
                "RH — Base não localizada. Gerando registros de colaboradores e folha"
                "sintéticos..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') contendo listas
            # estruturadas com colaboradores e salários.
            dados_simulados = {
                # Lista de matrículas numéricas de identificação única de cada
                # colaborador da PME.
                "id_funcionario": [
                    301,
                    302,
                    303,
                    304,
                    305,
                    306,
                    307,
                    308,
                    309,
                    310,
                ],
                # Nome do colaborador registrado no livro de registro de empregados do
                # departamento pessoal.
                "nome_colaborador": [
                    "Carlos Silva",
                    "Mariana Souza",
                    "Roberto Dias",
                    "Fernanda Lima",
                    "Lucas Mendes",
                    "Beatriz Costa",
                    "João Ferreira",
                    "Aline Prado",
                    "Gabriel Torres",
                    "Juliana Rocha",
                ],
                # Departamento ou setor da empresa onde o colaborador atua diariamente.
                "setor": [
                    "Comercial",
                    "Financeiro",
                    "Produção",
                    "Produção",
                    "Estoque",
                    "Comercial",
                    "Produção",
                    "Administrativo",
                    "Logística",
                    "Pós-Venda",
                ],
                # Salário base nominal contratual registrado na carteira de trabalho em
                # reais (R$).
                "salario_base": [
                    3800.0,
                    4500.0,
                    2400.0,
                    2600.0,
                    2100.0,
                    4200.0,
                    2500.0,
                    3500.0,
                    2300.0,
                    2800.0,
                ],
                # Encargos sociais e trabalhistas obrigatórios da empresa (FGTS, INSS
                # patronal, provisões) em reais.
                "encargos_sociais": [
                    1520.0,
                    1800.0,
                    960.0,
                    1040.0,
                    840.0,
                    1680.0,
                    1000.0,
                    1400.0,
                    920.0,
                    1120.0,
                ],
                # Situação cadastral do colaborador no período apurado (Ativo ou
                # Demitido).
                "status_vinculo": [
                    "Ativo",
                    "Ativo",
                    "Ativo",
                    "Demitido",
                    "Ativo",
                    "Ativo",
                    "Demitido",
                    "Ativo",
                    "Ativo",
                    "Ativo",
                ],
                # Quantidade total de faltas injustificadas registradas no ponto
                # eletrônico durante o ano.
                "dias_falta": [
                    1,
                    0,
                    4,
                    8,
                    2,
                    0,
                    6,
                    1,
                    3,
                    2,
                ],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_rh = pd.DataFrame(dados_simulados)

            # Soma o salário base com os encargos sociais para derivar o custo total
            # real do colaborador para a empresa.
            df_rh["custo_total_empresa"] = (
                df_rh["salario_base"] + df_rh["encargos_sociais"]
            ).round(2)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores do RH.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_rh.to_csv(caminho_rh, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_rh = self.leitor.carregar_tabela(caminho_rh)

        # 'logging.info' imprime no console o total de colaboradores consolidados para a
        # auditoria de pessoal.
        logging.info(
            "RH — Base consolidada com %d colaboradores auditados.", len(df_rh)
        )

        # 'return' devolve a matriz tabular pronta para os cálculos de indicadores de
        # pessoas.
        return df_rh

    # KPI 91: Percentual da Folha de Pagamento sobre a Receita Bruta (Payroll-to-Revenue
    # Ratio).
    # KPI 92: Taxa de Rotatividade de Pessoal (Turnover Rate).
    # KPI 95: Produtividade Média por Colaborador (Revenue per Employee).
    # 'def' define a função especializada em apurar as métricas consolidadas de força de
    # trabalho e folha.
    def calcular_indicadores_rh(
        self, dados: pd.DataFrame, faturamento_total_reais: float = 180000.0
    ) -> dict[str, float]:
        """Calcula o peso da folha sobre a receita, a taxa de turnover e a produtividade
        por colaborador.

        Folha sobre Receita (%) = (Custo Total da Folha / Faturamento Bruto) * 100.
        Turnover (%) = (Total de Demissões / Total de Colaboradores Avaliados) * 100.
        Produtividade Média = Faturamento Bruto / Total de Colaboradores Ativos.

        Args:
            dados (pd.DataFrame): Tabela de colaboradores com salários, encargos e
            status de vínculo.
            faturamento_total_reais (float, opcional): Faturamento bruto da empresa para
            base de cálculo. Padrão: 180.000,00.

        Returns:
            Dict[str, float]: Dicionário contendo custo de folha, peso percentual,
            turnover e produtividade média.
        """
        # '.sum()' calcula a soma do custo total de todos os colaboradores ativos e
        # desligados no período.
        custo_folha_total = float(dados["custo_total_empresa"].sum())

        # Divide o custo total da folha pelo faturamento bruto para encontrar o peso
        # percentual da equipe na receita.
        # O operador ternário 'if faturamento_total_reais > 0 else 0.0' previne divisão
        # por zero em bases zeradas.
        percentual_folha_receita = (
            (custo_folha_total / faturamento_total_reais) * 100
            if faturamento_total_reais > 0
            else 0.0
        )

        # 'int(len(dados))' conta o total absoluto de registros cadastrais de
        # colaboradores avaliados.
        total_colaboradores = int(len(dados))

        # '(dados["status_vinculo"] == "Demitido").sum()' soma quantas rescisões ou
        # demissões ocorreram no período.
        total_demissoes = int((dados["status_vinculo"] == "Demitido").sum())

        # '(dados["status_vinculo"] == "Ativo").sum()' conta quantos colaboradores
        # continuam na equipe ativa da PME.
        total_ativos = int((dados["status_vinculo"] == "Ativo").sum())

        # Calcula a taxa percentual de rotatividade (Turnover) dividindo os
        # desligamentos pela base total.
        taxa_turnover = (
            (total_demissoes / total_colaboradores) * 100
            if total_colaboradores > 0
            else 0.0
        )

        # Calcula o Faturamento Médio gerado por cada funcionário ativo (Produtividade
        # Média da Força de Trabalho).
        produtividade_media = (
            faturamento_total_reais / total_ativos if total_ativos > 0 else 0.0
        )

        # 'laudo_rh' organiza os indicadores vitais de gestão de pessoas para o
        # relatório executivo e comitê.
        laudo_rh = {
            # 'round(..., 2)' arredonda o custo total consolidado da folha salarial com
            # encargos em reais.
            "custo_folha_total_reais": round(custo_folha_total, 2),
            # 'round(..., 2)' arredonda o faturamento bruto tomado como referência
            # analítica.
            "faturamento_referencia_reais": round(faturamento_total_reais, 2),
            # 'round(..., 2)' arredonda o peso percentual da folha salarial sobre a
            # receita bruta (%).
            "percentual_folha_sobre_receita": round(percentual_folha_receita, 2),
            # 'round(..., 2)' arredonda a taxa percentual de turnover da equipe (%).
            "taxa_turnover_percentual": round(taxa_turnover, 2),
            # 'round(..., 2)' arredonda a produtividade média por colaborador ativo em
            # reais.
            "produtividade_media_por_ativo": round(produtividade_media, 2),
            # Registra o número total de funcionários com contrato ativo no momento.
            "total_colaboradores_ativos": total_ativos,
            # Registra o número total de rescisões e demissões no período.
            "total_demissoes": total_demissoes,
        }

        # 'logging.info' imprime os indicadores no console para auditoria operacional de
        # recursos humanos.
        logging.info(
            "RH — Folha sobre Receita: %.2f%% | Turnover: %.2f%% | Produtividade/Ativo:"
            "R$ %.2f.",
            laudo_rh["percentual_folha_sobre_receita"],
            laudo_rh["taxa_turnover_percentual"],
            laudo_rh["produtividade_media_por_ativo"],
        )

        # 'return' devolve o dicionário estruturado com as métricas de capital humano.
        return laudo_rh

    # 'def' define o método especialista em renderizar o gráfico comparativo de custos
    # da folha por setor.
    # 'caminho_figura' será devolvido como um objeto Path com o endereço da imagem
    # exportada no disco.
    def gerar_grafico_custo_folha_por_setor(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras comparando o custo financeiro total da folha
        salarial por setor.

        Args:
            dados (pd.DataFrame): Tabela contendo colaboradores, setores e custo total
            da empresa.

        Returns:
            Path: Endereço físico do arquivo de imagem exportado em alta resolução (300
            DPI).
        """
        # '.groupby("setor")' agrupa os colaboradores pelo departamento de trabalho
        # (ex.: Produção, Comercial).
        # '["custo_total_empresa"].sum()' calcula o total gasto com salários e encargos
        # em cada departamento.
        # '.reset_index()' converte o resultado agrupado em uma tabela tabular com
        # colunas convencionais.
        custo_setor = dados.groupby("setor")["custo_total_empresa"].sum().reset_index()

        # '.sort_values()' ordena os setores de forma decrescente pelo montante gasto (o
        # setor mais oneroso no topo).
        custo_setor = custo_setor.sort_values(by="custo_total_empresa", ascending=False)

        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/recursos_humanos/',
        # criada pelo construtor base.
        caminho_figura = self.pasta_saida / "custo_folha_por_setor.png"

        # 'plt.subplots()' inicializa uma moldura gráfica com 9 polegadas de largura por
        # 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras verticais no Seaborn representando a
        # concentração de gastos com folha.
        # 'data=custo_setor' fornece a tabela de dados que alimenta a visualização.
        # 'x="setor"' posiciona os nomes dos departamentos no eixo horizontal.
        # 'y="custo_total_empresa"' projeta a altura das barras correspondente ao valor
        # em reais no eixo vertical.
        # 'color="#9467bd"' aplica uma tonalidade roxa executiva para indicar gestão de
        # pessoas e liderança.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura configurada no
        # matplotlib.
        sns.barplot(
            data=custo_setor,
            x="setor",
            y="custo_total_empresa",
            color="#9467bd",
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Distribuição do Custo Total da Folha Salarial por Setor (R$)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo descritivo no eixo horizontal X em
        # português.
        eixo.set_xlabel("Departamento / Setor da PME", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo financeiro no eixo vertical Y em moeda
        # corrente (R$).
        eixo.set_ylabel("Custo da Folha + Encargos (R$)", fontsize=10)

        # 'plt.xticks(rotation=30, ha="right")' inclina levemente os textos para evitar
        # corte de palavras compridas.
        plt.xticks(rotation=30, ha="right")

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
        logging.info(
            "RH — Gráfico de custos de folha salvo em: %s", caminho_figura.name
        )

        # 'return' devolve o caminho físico do arquivo gravado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todas as rotinas periciais de
    # recursos humanos e pessoal.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo do turnover, custo da folha e persistência dos gráficos de
        pessoal.

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento de recursos
            humanos.
        """
        # Emite log anunciando o início oficial da perícia de recursos humanos da Fase
        # 2.10.
        logging.info(
            "=== INICIANDO PERÍCIA DO DEPARTAMENTO DE RECURSOS HUMANOS (FASE 2.10) ==="
        )

        # Invoca o método interno que carrega e valida os registros de colaboradores na
        # memória RAM uma única vez.
        df_rh = self.carregar_dados_rh()

        # Executa o cálculo dos indicadores de pessoal (folha sobre receita, turnover e
        # produtividade).
        laudo_pessoal = self.calcular_indicadores_rh(df_rh)

        # Renderiza e salva o gráfico da folha salarial distribuída por setor no disco.
        caminho_grafico = self.gerar_grafico_custo_folha_por_setor(df_rh)

        # 'int(df_rh["dias_falta"].sum())' soma o total de faltas injustificadas
        # registradas em toda a empresa.
        total_faltas_empresa = int(df_rh["dias_falta"].sum())

        # 'laudo_rh_completo' é o dicionário estruturado que consolida o laudo de gestão
        # de pessoas da PME.
        laudo_rh_completo = {
            # Incorpora os indicadores de custos de folha, taxa de turnover e
            # produtividade média calculados.
            "indicadores_pessoal": laudo_pessoal,
            # Registra o total acumulado de faltas e absenteísmo computado na folha de
            # ponto.
            "total_dias_falta_acumulados": total_faltas_empresa,
            # Registra o caminho do arquivo de imagem exportado para visualização em
            # relatórios ou BI.
            "grafico_folha_por_setor": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento da auditoria de recursos humanos.
        logging.info("=== DEPARTAMENTO DE RECURSOS HUMANOS CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de recursos humanos para o orquestrador
        # geral do projeto.
        return laudo_rh_completo
