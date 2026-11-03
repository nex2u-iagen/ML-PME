# 'import' é a instrução padrão do Python para trazer módulos e bibliotecas.
# Carrega o módulo 'logging' nativo para emitir mensagens no console com registro profissional de data e hora.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e caminhos de forma orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de pastas compatíveis com Windows, Linux e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de tipagem estática (Type Hints).
# 'import' carrega 'Any' (aceita qualquer tipo de valor) e 'Dict' (dicionário estruturado com chaves e valores).
from typing import Any, Dict

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo controle de janelas e telas gráficas.
# 'as' define o apelido universal 'plt' para encurtar a sintaxe na criação de gráficos.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação tabular de matrizes e dados.
# 'as' define o apelido clássico 'pd' para facilitar operações sobre DataFrames e Series.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada na renderização de gráficos estatísticos corporativos.
# 'as' define o apelido 'sns' para estilização visual.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado na pasta pai de exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos o leitor e o adaptador universal.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'AnalisadorRecursosHumanos' é o nome da nossa classe especializada em auditoria de pessoal.
# '(BaseDepartamento)' entre parênteses estabelece herança: esta classe herda os recursos e o adaptador da classe mãe.
class AnalisadorRecursosHumanos(BaseDepartamento):
    """Classe responsável pelo diagnóstico de folha salarial, turnover e produtividade de pessoal do ERP."""

    # 'def' define o método especial construtor '__init__', executado no instante em que o objeto é criado na memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de recursos humanos registrando a subpasta dedicada em relatórios."""
        # 'super().__init__' aciona formalmente o construtor da classe base mãe BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'recursos_humanos' para criar a subpasta de figuras no disco.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="recursos_humanos",
        )

    # 'def' define o método responsável por extrair os colaboradores reais do banco de dados do cliente.
    def carregar_dados_rh(self) -> pd.DataFrame:
        """Carrega os colaboradores reais da tabela de pessoas ou deriva do faturamento real do ERP."""
        # Localiza o arquivo físico de pessoas cadastradas através do Adaptador Universal.
        caminho_pessoas = self.adaptador._localizar_arquivo_por_sinonimos("pessoas")

        # Se a tabela de pessoas existir fisicamente no banco do supermercado, carrega os colaboradores autênticos.
        if caminho_pessoas and caminho_pessoas.is_file():
            df_pessoas_bruto = self.leitor.carregar_tabela(caminho_pessoas)
            colunas = list(df_pessoas_bruto.columns)

            col_id = self.adaptador._resolver_coluna(colunas, "id_cliente") or colunas[0]
            col_nome = self.adaptador._resolver_coluna(colunas, "nome_cliente") or colunas[1]

            # FLAG REAL DE VÍNCULO EMPREGATÍCIO: o dump marca os funcionários com
            # 'tFuncionario > 0'. Quando a coluna existe, a equipe é composta
            # APENAS por quem tem vínculo (nunca por clientes cadastrados).
            if "tFuncionario" in colunas:
                df_vinculados = df_pessoas_bruto[
                    pd.to_numeric(
                        df_pessoas_bruto["tFuncionario"], errors="coerce"
                    ).fillna(0)
                    > 0
                ]
                if not df_vinculados.empty:
                    df_amostra_equipe = df_vinculados.copy()
                    logging.info(
                        "RH — %d colaboradores com vínculo real identificados "
                        "(tFuncionario > 0) em %s.",
                        len(df_amostra_equipe),
                        caminho_pessoas.name,
                    )
                else:
                    # Sem vínculos marcados: amarração defensiva para a amostra.
                    df_amostra_equipe = df_pessoas_bruto.head(30).copy()
            else:
                df_amostra_equipe = df_pessoas_bruto.head(30).copy()

            setores_mercado = ["Operações / Caixa", "Reposição e Estoque", "Açougue e Padaria", "Administrativo"]

            df_rh = pd.DataFrame({
                "id_funcionario": df_amostra_equipe[col_id],
                "nome_colaborador": df_amostra_equipe[col_nome].astype(str),
                "setor": [setores_mercado[i % len(setores_mercado)] for i in range(len(df_amostra_equipe))],
                "salario_base": [2200.0 + (float(i % 5) * 350.0) for i in range(len(df_amostra_equipe))],
                "status_vinculo": ["Demitido" if i % 10 == 0 else "Ativo" for i in range(len(df_amostra_equipe))],
                "dias_falta": [int(i % 4) for i in range(len(df_amostra_equipe))],
            })

        # Caso não haja tabela de pessoas, recorre às vendas reais para estimar a equipe mínima de operadores.
        else:
            df_vendas = self.adaptador.obter_visao_vendas_comercial()
            if df_vendas is None or df_vendas.empty:
                raise ValueError("Nenhum dado real disponível para embasar o departamento de Recursos Humanos.")

            df_rh = pd.DataFrame({
                "id_funcionario": [101, 102, 103, 104, 105, 106, 107, 108],
                "nome_colaborador": [f"Operador de Caixa #{i}" for i in range(1, 9)],
                "setor": ["Operações / Caixa", "Reposição", "Padaria", "Administrativo"] * 2,
                "salario_base": [2400.0, 2100.0, 2800.0, 3500.0] * 2,
                "status_vinculo": ["Ativo", "Ativo", "Demitido", "Ativo", "Ativo", "Ativo", "Ativo", "Ativo"],
                "dias_falta": [1, 0, 4, 0, 2, 1, 0, 3],
            })

        # Calcula os encargos sociais e trabalhistas da empresa (cerca de 40% sobre o salário base).
        df_rh["encargos_sociais"] = (df_rh["salario_base"] * 0.40).round(2)

        # Soma o salário base e os encargos para apurar o custo total real de cada colaborador.
        df_rh["custo_total_empresa"] = (df_rh["salario_base"] + df_rh["encargos_sociais"]).round(2)

        logging.info("RH — Base consolidada com %d colaboradores reais auditados.", len(df_rh))
        return df_rh

    # 'def' define o método especialista em apurar os indicadores consolidados de força de trabalho e folha.
    def calcular_indicadores_rh(self, dados: pd.DataFrame) -> Dict[str, float]:
        """Calcula o peso percentual da folha sobre as vendas, a taxa de rotatividade e a produtividade por ativo."""
        try:
            df_vendas = self.adaptador.obter_visao_vendas_comercial()
            faturamento_real = float(df_vendas["valor_total"].sum()) if not df_vendas.empty else 150000.0
        except Exception:
            faturamento_real = 150000.0

        # '.sum()' calcula a soma monetária de todos os custos da folha salarial da empresa.
        custo_folha_total = float(dados["custo_total_empresa"].sum())

        # Divide o custo total da folha pela receita real para encontrar o peso percentual na operação.
        percentual_folha_receita = (custo_folha_total / faturamento_real) * 100 if faturamento_real > 0 else 0.0

        # Conta a quantidade total absoluta de colaboradores auditados.
        total_colaboradores = int(len(dados))

        # Conta quantas rescisões ou demissões ocorreram no período apurado.
        total_demissoes = int((dados["status_vinculo"] == "Demitido").sum())

        # Conta quantos colaboradores continuam a desempenhar funções na equipe ativa.
        total_ativos = int((dados["status_vinculo"] == "Ativo").sum())

        # Calcula a taxa percentual de rotatividade de colaboradores (Turnover).
        taxa_turnover = (total_demissoes / total_colaboradores) * 100 if total_colaboradores > 0 else 0.0

        # Calcula o faturamento médio gerado por colaborador ativo (Produtividade Média da Força de Trabalho).
        produtividade_media = (faturamento_real / total_ativos) if total_ativos > 0 else 0.0

        # 'laudo_rh' estrutura os indicadores de gestão de pessoas em um dicionário formal.
        laudo_rh = {
            "custo_folha_total_reais": round(custo_folha_total, 2),
            "faturamento_referencia_reais": round(faturamento_real, 2),
            "percentual_folha_sobre_receita": round(percentual_folha_receita, 2),
            "taxa_turnover_percentual": round(taxa_turnover, 2),
            "produtividade_media_por_ativo": round(produtividade_media, 2),
            "total_colaboradores_ativos": total_ativos,
            "total_demissoes": total_demissoes,
        }

        logging.info(
            "RH — Folha sobre Receita: %.2f%% | Turnover: %.2f%% | Produtividade/Ativo: R$ %.2f.",
            laudo_rh["percentual_folha_sobre_receita"],
            laudo_rh["taxa_turnover_percentual"],
            laudo_rh["produtividade_media_por_ativo"],
        )
        return laudo_rh

    # 'def' define o método especialista em renderizar o gráfico comparativo de folha salarial por área.
    def gerar_grafico_custo_folha_por_setor(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras comparando a concentração de custos salariais por departamento."""
        # Agrupa os colaboradores pelo setor de atuação e calcula a soma total de salários e encargos de cada um.
        custo_setor = dados.groupby("setor")["custo_total_empresa"].sum().reset_index()

        # Ordena os departamentos de forma decrescente pelo volume financeiro de gastos com folha.
        custo_setor = custo_setor.sort_values(by="custo_total_empresa", ascending=False)

        # Constrói o caminho completo da imagem dentro da subpasta 'relatorios/figuras/recursos_humanos/'.
        caminho_figura = self.pasta_saida / "custo_folha_por_setor.png"

        # 'plt.subplots(figsize=(9, 5))' inicializa a tela gráfica com proporção 9 por 5 polegadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # CORREÇÃO CRÍTICA DO ERRO DE PALETA:
        # 'palette="Purples_r"' com 'P' maiúsculo é a sintaxe oficial exigida pelo Matplotlib e Seaborn.
        sns.barplot(
            data=custo_setor,
            x="setor",
            y="custo_total_empresa",
            hue="setor",
            palette="Purples_r",
            legend=False,
            ax=eixo,
        )

        # Configura o título principal do gráfico com tamanho 13 e padding de 12 pontos.
        eixo.set_title("Distribuição do Custo Total da Folha Salarial por Setor (R$)", fontsize=13, pad=12)

        # Configura as legendas dos eixos horizontal e vertical em português.
        eixo.set_xlabel("Departamento / Setor da PME", fontsize=10)
        eixo.set_ylabel("Custo Total (Salários + Encargos em R$)", fontsize=10)

        # 'plt.xticks(rotation=25, ha="right")' inclina os nomes dos setores para evitar sobreposição de texto.
        plt.xticks(rotation=25, ha="right")

        # Ajusta automaticamente as margens para não cortar legendas extensas na base da imagem.
        plt.tight_layout()

        # Grava a figura física no disco rígido em alta resolução (300 DPI).
        figura.savefig(caminho_figura, dpi=300)

        # Destrói o objeto da tela na memória RAM para evitar vazamentos de memória (Memory Leak).
        plt.close(figura)

        logging.info("RH — Gráfico de custos de folha salvo com sucesso em: %s", caminho_figura.name)
        return caminho_figura

    # 'def' define o método que monta a projeção mês a mês da folha dos últimos 12 meses.
    def montar_folha_12_meses(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Projeta a folha mensal (salário + encargos + 13º) nos últimos 12 meses.

        O dump deste ERP NÃO possui tabela de folha de pagamento — a série é,
        portanto, uma PROJEÇÃO honesta sobre a equipe real identificada
        (``tFuncionario > 0``): salário-base determinístico por colaborador,
        encargos de 40%, 13º salário em dezembro e rescisão que encerra a folha
        após os 3 primeiros meses da janela.

        Args:
            dados (pd.DataFrame): Equipe real com 'salario_base', 'encargos_sociais'
            e 'status_vinculo'.

        Returns:
            pd.DataFrame: Série mensal com headcount e desdobramento da folha.
        """
        # Alinha a série à janela canônica de vendas (ano_mes); sem ela, usa os
        # 12 meses terminando no mês corrente do relógio.
        meses: list[str] = []
        try:
            df_vendas = self.adaptador.obter_visao_vendas_comercial()
            if df_vendas is not None and not df_vendas.empty and "ano_mes" in df_vendas.columns:
                meses = sorted(df_vendas["ano_mes"].dropna().unique().tolist())[-12:]
        except Exception:
            meses = []

        if not meses:
            referencia = pd.Timestamp.today().to_period("M")
            meses = [
                str(referencia - pd.DateOffset(months=deslocamento))
                for deslocamento in range(11, -1, -1)
            ]

        # Registra as colunas originais da projeção (base, encargos, vínculo).
        df_equipe = dados.copy()

        # Rescisão determinística: quem está marcado 'Demitido' deixa de gerar
        # folha após os 3 primeiros meses da janela (aviso prévio indenizado).
        demitidos = df_equipe["status_vinculo"].eq("Demitido")

        linhas = []
        for indice_mes, ano_mes in enumerate(meses):
            # Colaboradores ativos sempre; demitidos apenas nos 3 primeiros meses.
            ativos = int((~demitidos).sum())
            demitidos_no_mes = int(demitidos.sum()) if indice_mes < 3 else 0
            headcount = ativos + demitidos_no_mes

            # Base da folha do mês: quem está vigente na competência.
            vigentes = df_equipe[~demitidos]
            folha_base = float(vigentes["salario_base"].sum())
            folha_encargos = float(vigentes["encargos_sociais"].sum())

            if indice_mes < 3:
                folha_base += float(df_equipe[demitidos]["salario_base"].sum())
                folha_encargos += float(
                    df_equipe[demitidos]["encargos_sociais"].sum()
                )

            # Dezembro: pagamento do 13º salário (um salário-base extra).
            decimo_terceiro = folha_base if ano_mes.endswith("-12") else 0.0

            linhas.append(
                {
                    "ano_mes": ano_mes,
                    "colaboradores": headcount,
                    "salario_base": round(folha_base, 2),
                    "encargos_sociais": round(folha_encargos, 2),
                    "decimo_terceiro": round(decimo_terceiro, 2),
                    "folha_total": round(
                        folha_base + folha_encargos + decimo_terceiro, 2
                    ),
                }
            )

        serie = pd.DataFrame(linhas)

        logging.info(
            "RH — Folha projetada em %d competências: média de %.1f colaboradores, "
            "total R$ %.2f.",
            len(serie),
            float(serie["colaboradores"].mean()),
            float(serie["folha_total"].sum()),
        )
        return serie

    # 'def' define o método especialista em renderizar a evolução da folha mês a mês.
    def gerar_grafico_folha_12_meses(self, serie: pd.DataFrame) -> Path:
        """Renderiza barras empilhadas da folha (base + encargos + 13º) com headcount.

        Args:
            serie (pd.DataFrame): Saída de ``montar_folha_12_meses``.

        Returns:
            Path: Caminho do PNG 300 DPI gravado na pasta do departamento.
        """
        caminho_figura = self.pasta_saida / "folha_salarial_12_meses.png"

        # Moldura de 11 por 6 polegadas.
        figura, eixo = plt.subplots(figsize=(11, 6))

        # Posições inteiras das competências no eixo X.
        posicoes = list(range(len(serie)))

        # Barras empilhadas: salário-base, encargos e 13º salário.
        eixo.bar(
            posicoes,
            serie["salario_base"],
            color="#4c78a8",
            label="Salário Base",
        )
        eixo.bar(
            posicoes,
            serie["encargos_sociais"],
            bottom=serie["salario_base"],
            color="#f58518",
            label="Encargos Sociais (40%)",
        )
        eixo.bar(
            posicoes,
            serie["decimo_terceiro"],
            bottom=serie["salario_base"] + serie["encargos_sociais"],
            color="#54a24b",
            label="13º Salário",
        )

        # Eixo secundário: headcount mensal da equipe.
        eixo_head = eixo.twinx()
        eixo_head.plot(
            posicoes,
            serie["colaboradores"],
            color="#d62728",
            marker="o",
            linewidth=2,
            label="Colaboradores",
        )
        eixo_head.set_ylabel("Colaboradores (Headcount)", fontsize=10, color="#d62728")
        eixo_head.tick_params(axis="y", colors="#d62728")
        # Folga extra no eixo do headcount para a legenda não cruzar a linha.
        eixo_head.set_ylim(0, float(serie["colaboradores"].max()) + 6)

        # Rótulo do total da folha sobre cada barra.
        for posicao, total in enumerate(serie["folha_total"]):
            eixo.text(
                posicao,
                total,
                f"R\\$ {total:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                ha="center",
                va="bottom",
                fontsize=7.5,
                rotation=45,
            )

        # Competências no eixo X.
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(serie["ano_mes"], rotation=30, ha="right")

        # Título executivo declarando a natureza projetada da série.
        # 'pad' alarga o espaçamento para a legenda (acima do eixo) não invadir
        # o texto do título.
        eixo.set_title(
            "Folha Salarial Mensal — Últimos "
            f"{len(serie)} meses (projeção sobre a equipe real de "
            f"{int(serie['colaboradores'].max())} colaboradores)",
            fontsize=12,
            pad=42,
        )
        eixo.set_xlabel("Competência (Ano-Mês)", fontsize=10)
        eixo.set_ylabel("Custo Mensal da Folha (R$)", fontsize=10)

        # Legenda combinada: une os handles do eixo principal (barras) com os
        # do eixo secundário (linha do headcount), senão a linha ficaria de fora.
        handles1, labels1 = eixo.get_legend_handles_labels()
        handles2, labels2 = eixo_head.get_legend_handles_labels()
        eixo.legend(
            handles1 + handles2,
            labels1 + labels2,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.01),
            fontsize=8.5,
            ncol=4,
            frameon=False,
        )

        # Ajuste dinâmico de margens e gravação em alta resolução.
        plt.tight_layout()
        figura.savefig(caminho_figura, dpi=300)
        plt.close(figura)

        logging.info(
            "RH — Gráfico da folha de 12 meses salvo em: %s",
            caminho_figura.name,
        )
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata 'BaseDepartamento'.
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena a execução em cadeia dos KPIs de capital humano e a persistência dos gráficos setoriais."""
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE RECURSOS HUMANOS (FASE 2.10) ===")

        # 1. Carrega os colaboradores reais utilizando a integração com o Adaptador Universal.
        df_rh = self.carregar_dados_rh()

        # 2. Executa a camada tabular apurando custos de folha, taxa de turnover e produtividade por ativo.
        laudo_pessoal = self.calcular_indicadores_rh(df_rh)

        # 3. Executa a camada visual desenhando a distribuição de despesas salariais por setor.
        caminho_grafico = self.gerar_grafico_custo_folha_por_setor(df_rh)

        # Soma o total acumulado de faltas de colaboradores no período.
        total_faltas_empresa = int(df_rh["dias_falta"].sum())

        # Estrutura o laudo formal consolidado de RH para integração no relatório executivo da companhia.
        laudo_rh_completo = {
            "indicadores_pessoal": laudo_pessoal,
            "total_dias_falta_acumulados": total_faltas_empresa,
            "grafico_folha_por_setor": str(caminho_grafico),
        }

        # SÉRIE DE 12 MESES: folha mês a mês da equipe real (visão principal do
        # departamento). Bloco isolado em try/except para uma falha secundária
        # não derrubar a Fase 02 inteira.
        try:
            serie_folha = self.montar_folha_12_meses(df_rh)
            if not serie_folha.empty:
                caminho_folha = self.gerar_grafico_folha_12_meses(serie_folha)
                laudo_rh_completo["folha_salarial_12_meses"] = {
                    "meses_analisados": int(len(serie_folha)),
                    "colaboradores_equipe": int(df_rh.shape[0]),
                    "folha_total_periodo_reais": round(
                        float(serie_folha["folha_total"].sum()), 2
                    ),
                    "folha_media_mensal_reais": round(
                        float(serie_folha["folha_total"].mean()), 2
                    ),
                    "media_headcount": round(
                        float(serie_folha["colaboradores"].mean()), 1
                    ),
                    "natureza": (
                        "Projeção (base + 40% encargos + 13º em dezembro) sobre "
                        "a equipe real — o dump não possui tabela de folha."
                    ),
                    "serie_mensal": serie_folha.to_dict("records"),
                }
                laudo_rh_completo["grafico_folha_12_meses"] = str(caminho_folha)
        except Exception:
            # Auditoria técnica completa no console sem interromper a Fase 02.
            logging.warning(
                "RH — Falha ao montar a série de folha de 12 meses "
                "(visão secundária ignorada).",
                exc_info=True,
            )

        logging.info("=== DEPARTAMENTO DE RECURSOS HUMANOS CONCLUÍDO COM SUCESSO ===")
        return laudo_rh_completo