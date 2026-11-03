"""Módulo de Diagnóstico Exploratório do Departamento Contábil (Fase 2.5 - CRISP-DM).

Responsabilidade Única: Avaliar a apuração de Custo de Mercadorias Vendidas (CMV),
índice de margem de contribuição (IMC) e cálculo do Break-Even Point (Ponto de Equilíbrio),
utilizando exclusivamente os dados canônicos reais entregues pelo Adaptador Universal[cite: 10].
"""

# 'import logging' habilita o registro padronizado de alertas e progressos na interface do terminal[cite: 10].
import logging

# 'from pathlib import Path' gerencia de forma robusta e tipada as rotas lógicas e físicas de gravação no disco[cite: 10].
from pathlib import Path

# 'from typing import Any, Dict' incorpora os artefatos formais para anotação estática e documentação de métodos[cite: 10].
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' fornece os módulos de baixo nível para construção das janelas e eixos do gráfico[cite: 10].
import matplotlib.pyplot as plt

# 'import pandas as pd' viabiliza a execução massiva e vetorizada das equações financeiras na memória RAM[cite: 10].
import pandas as pd

# 'import seaborn as sns' renderiza de forma declarativa e esteticamente requintada o gráfico DRE (Demonstração de Resultados)[cite: 10].
import seaborn as sns

# Importação da classe abstrata que atua como contrato arquitetural, injetando a infraestrutura e as ferramentas universais[cite: 10].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class AnalisadorContabil(BaseDepartamento)' especializa o diagnóstico de custos e margens absorvendo as rotinas-base[cite: 10].
class AnalisadorContabil(BaseDepartamento):
    """Classe responsável pelo diagnóstico gerencial de custos diretos, margens operacionais e ponto de equilíbrio real[cite: 10]."""

    # 'def __init__(...)' invoca a fase de inicialização, amarrando a análise contábil às pastas de relatórios e de dados isolados[cite: 10].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento contábil configurando a nomenclatura canônica de saída[cite: 10].

        Args:
            pasta_dados_brutos (Path): Diretório enclausurado contendo o dump de tabelas CSV reais da empresa (ex: mercado_vencedor/)[cite: 10].
            pasta_relatorios (Path): Diretório alvo universal, onde a subpasta 'contabil/' será instanciada[cite: 10].
        """
        # 'super().__init__(...)' efetiva o setup na classe mãe registrando 'contabil' como apelido canônico de pastas e arquivos[cite: 10].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="contabil",
        )

    # 'def carregar_dados_contabeis(...)' abstrai a extração delegando a requisição para o adaptador semântico[cite: 10].
    def carregar_dados_contabeis(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal o faturamento de vendas real para projeção contábil do DRE[cite: 10].

        Returns:
            pd.DataFrame: Tabela financeira contendo faturamento total por pedido consolidado[cite: 10].

        Raises:
            ValueError: Caso o adaptador não detecte arquivos de notas de venda na base em análise[cite: 10].
        """
        # O Adaptador Universal (herdado na BaseDepartamento) traduz as faturas reais (ex: 'erp_nfetotal.csv') para a visão comercial[cite: 10].
        df_pedidos = self.adaptador.obter_visao_vendas_comercial()

        # Validação defensiva absoluta: impede falhas silenciosas ou prosseguimento caso a base seja inócua ou viciada[cite: 10].
        if df_pedidos is None or df_pedidos.empty:
            logging.error("Contábil — Falha crítica: Nenhum faturamento real foi entregue pelo Adaptador Universal.")
            raise ValueError("Dados comerciais reais imprescindíveis para o módulo contábil não foram localizados na base.")

        # '.copy()' cinde e blinda os dados: isolamos as mutações deste módulo para evitar corromper o cache global[cite: 10].
        df_contabil = df_pedidos.copy()

        # Cálculo Estimativo 1: Emprego de taxa mercadológica média do varejo PME (55%) para a extração do Custo da Mercadoria Vendida[cite: 10].
        df_contabil["custo_cmv"] = (df_contabil["valor_total"] * 0.55).round(2)

        # Cálculo Estimativo 2: Projeta a alíquota padrão de despesas comerciais variáveis como tarifas bancárias, simples nacional e comissões (12%)[cite: 10].
        df_contabil["despesas_variaveis"] = (df_contabil["valor_total"] * 0.12).round(2)

        # Loga no console o carregamento bem-sucedido atestando o número exato de notas/transações que passarão pelas equações[cite: 10].
        logging.info("Contábil — Visão DRE carregada com %d transações para apuração técnica de margem.", len(df_contabil))

        # Restitui a tabela tabular provida de novas colunas contábeis para prosseguimento do funil pericial[cite: 10].
        return df_contabil

    # 'def calcular_margem_contribuicao(...)' condensa as variáveis transacionais para emitir o sinal vital da operação[cite: 10].
    def calcular_margem_contribuicao(self, dados: pd.DataFrame) -> Dict[str, float]:
        """Calcula a Margem de Contribuição gerencial (Receita - Custos - Despesas) e a ratio percentual[cite: 10].

        Args:
            dados (pd.DataFrame): Tabela contendo as séries tabulares de faturamento e custos parametrizados[cite: 10].

        Returns:
            Dict[str, float]: Ficha executiva com faturamento, subtrações escalonadas, margem absoluta (R$) e IMC (%)[cite: 10].
        """
        # '.sum()' condensa toda a massa financeira em montantes globais; 'float()' adequa à precisão flutuante exigida no Python[cite: 10].
        receita_total = float(dados["valor_total"].sum())
        cmv_total = float(dados["custo_cmv"].sum())
        despesas_var_total = float(dados["despesas_variaveis"].sum())

        # Equação formal da contabilidade gerencial: Subtração linear simples dos gastos atrelados à venda da receita direta[cite: 10].
        margem_contribuicao_reais = receita_total - cmv_total - despesas_var_total

        # Projeta a massa de dinheiro gerada (margem_contribuicao_reais) sobre a base macro da receita apurando a representação percentual[cite: 10].
        # Previne o division_by_zero do interpretador condicionando a execução via operador ternário em uma via linha só[cite: 10].
        indice_margem_percentual = (margem_contribuicao_reais / receita_total) * 100 if receita_total > 0 else 0.0

        # Envelopa os escalões do DRE Simplificado dentro do Dicionário, empregando o 'round(..., 2)' para asseverar rigor monetário (centavos)[cite: 10].
        laudo_margem = {
            "receita_bruta_reais": round(receita_total, 2),
            "custo_cmv_total_reais": round(cmv_total, 2),
            "despesas_variaveis_reais": round(despesas_var_total, 2),
            "margem_contribuicao_reais": round(margem_contribuicao_reais, 2),
            "indice_margem_percentual": round(indice_margem_percentual, 2),
        }

        # Expede o sinal vital essencial à saúde da PME no log para leitura limpa por auditor ou conselho de direção[cite: 10].
        logging.info(
            "Contábil — Margem de Contribuição: R$ %.2f (Índice IMC: %.2f%%).",
            laudo_margem["margem_contribuicao_reais"],
            laudo_margem["indice_margem_percentual"],
        )

        return laudo_margem

    # 'def calcular_ponto_equilibrio(...)' cruza as margens da tesouraria com o burn rate de gastos imobilizados projetados[cite: 10].
    def calcular_ponto_equilibrio(
        self,
        laudo_margem: Dict[str, float],
        custos_fixos_mensais: float = 25000.0,
    ) -> Dict[str, float]:
        """Calcula o Break-Even Point, revelando a régua mínima mensal de faturamento para anular perdas operacionais[cite: 10].

        Args:
            laudo_margem (Dict[str, float]): Estrutura com a Margem de Contribuição Percentual e faturamento consolidados[cite: 10].
            custos_fixos_mensais (float, opcional): Custos e despesas indiretas inelásticas fixas estipuladas. Padrão: 25.000,00[cite: 10].

        Returns:
            Dict[str, float]: Quadro resumo de viabilidade explicitando a meta nula (break-even) e a lacuna de conforto da empresa[cite: 10].
        """
        # Converte a visualização percentual (ex: 35.5%) para sua contrapartida matricial fracionária real (0.355)[cite: 10].
        indice_decimal = laudo_margem["indice_margem_percentual"] / 100.0

        # Divisão matemática fundamental: Ponto de Equilíbrio = Gastos Fixos / Percentual da Margem de Contribuição (Fração)[cite: 10].
        faturamento_equilibrio = custos_fixos_mensais / indice_decimal if indice_decimal > 0 else 0.0

        # Apura o lastro e gordura de sobrevivência caso as vendas despenquem, retraindo o equilíbrio da atual régua de faturamento[cite: 10].
        margem_seguranca_reais = laudo_margem["receita_bruta_reais"] - faturamento_equilibrio

        # Comprime a arquitetura analítica do módulo do ponto nulo financeiro[cite: 10].
        laudo_equilibrio = {
            "custos_fixos_reais": round(custos_fixos_mensais, 2),
            "ponto_equilibrio_reais": round(faturamento_equilibrio, 2),
            "margem_seguranca_reais": round(margem_seguranca_reais, 2),
        }

        # Extrato informativo formatado em Reais direcionado a interface do orquestrador central e do usuário[cite: 10].
        logging.info(
            "Contábil — Ponto de Equilíbrio (Break-Even): R$ %.2f (Margem de Segurança Operacional: R$ %.2f).",
            laudo_equilibrio["ponto_equilibrio_reais"],
            laudo_equilibrio["margem_seguranca_reais"],
        )

        return laudo_equilibrio

    # 'def gerar_grafico_composicao_resultado(...)' modela e orquestra a decomposição em mosaico barplot visual da margem[cite: 10].
    def gerar_grafico_composicao_resultado(self, laudo_margem: Dict[str, float]) -> Path:
        """Renderiza a cascata de perdas e sobrevivência financeira num painel de barras estático para relatoria[cite: 10].

        Args:
            laudo_margem (Dict[str, float]): Massa de dicionário condensando toda a demonstração simplificada[cite: 10].

        Returns:
            Path: Carimbo físico e definitivo na forma de Path persistido universalmente na árvore /relatorios/figuras[cite: 10].
        """
        # Assentamento físico na pasta dedicada (relatorios/figuras/contabil/composicao_resultado_contabil.png)[cite: 10].
        caminho_figura = self.pasta_saida / "composicao_resultado_contabil.png"

        # Vetorização textual das divisas operacionais apresentadas ao comitê analítico[cite: 10].
        categorias = ["Receita Bruta Total", "Custo Direto (CMV)", "Despesas Variáveis", "Margem Contribuição Livre"]
        valores = [
            laudo_margem["receita_bruta_reais"],
            laudo_margem["custo_cmv_total_reais"],
            laudo_margem["despesas_variaveis_reais"],
            laudo_margem["margem_contribuicao_reais"],
        ]

        # Consagra uma instância relacional provisória DataFrame a partir das séries listas forjadas manualmente[cite: 10].
        df_plot = pd.DataFrame({"Componente do DRE": categorias, "Valor Consolidado (R$)": valores})

        # Evoca a interface fig e axis com o molde físico 9 polegadas por 5, assegurando proporção horizontal padronizada[cite: 10].
        figura, eixo = plt.subplots(figsize=(9, 5))

        # Adota um semáforo cromático cognitivo: Azul neutro base, duplo Vermelho/Laranja de atenção para gastos, Verde farol p/ resultado[cite: 10].
        cores = ["#1f77b4", "#d62728", "#ff7f0e", "#2ca02c"]

        # Parametriza os nós de conexão declarativa via Seaborn. Usa explicitamente "hue" e legend=False blindando warnings do Matplotlib[cite: 10].
        sns.barplot(
            data=df_plot,
            x="Componente do DRE",
            y="Valor Consolidado (R$)",
            hue="Componente do DRE",
            palette=cores,
            legend=False,
            ax=eixo,
        )

        # Prega o crachá executivo informativo na abóbada superior da visualização cartográfica de lucros[cite: 10].
        eixo.set_title("Decomposição Simplificada de DRE: Receita vs. Custos Diretos vs. Margem de Contribuição", fontsize=12, pad=12)

        # Etiquetagem explicativa e contextual inferior dos vetores do abcesso e ordenada gráfica[cite: 10].
        eixo.set_xlabel("Categoria Demonstrativa Gerencial", fontsize=10)
        eixo.set_ylabel("Massa Financeira Consolidada (R$)", fontsize=10)

        # Torce ligeiramente os textos longos subjacentes evitando sobreposição aglomerada que danificaria a percepção do usuário[cite: 10].
        plt.xticks(rotation=15, ha="right")

        # Refina a alocação de polígonos eliminando faixas brancas fúteis de borda[cite: 10].
        plt.tight_layout()

        # Dispara os ciclos da máquina gráfica local persistindo a imagem com profundidade alta industrial (300dpi)[cite: 10].
        figura.savefig(caminho_figura, dpi=300)

        # Decreta aniquilação e coleta de destroços (*Garbage Collection*) da instância plotter da memória RAM, esvaziando o cachê da tela gráfica[cite: 10].
        plt.close(figura)

        # Submete nota de arquivamento confirmando a gênese da ferramenta visual fotográfica e sua localização geográfica[cite: 10].
        logging.info("Contábil — Gráfico estático de decomposição financeira lavrado em: %s", caminho_figura.name)

        return caminho_figura

    # 'def executar_diagnostico_completo(...)' encapsula o design pattern (Decorator) que a interface abstrata Base exige em cada ramo de herança[cite: 10].
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o desdobramento pericial em série, englobando cargas contábeis, equações marginais, breaks evens e persistência gráfica[cite: 10].

        Returns:
            Dict[str, Any]: Ficha-prontuário analítica contábil reunindo laudos matriciais estruturados e rastreio nominal das figuras atreladas[cite: 10].
        """
        # Exara comunicação informando à sala de comando matriz a intersecção analítica na fase fiscal contábil[cite: 10].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO CONTÁBIL (FASE 2.5) ===")

        # Camada de Ingestão Modular (Delegation Method): Dispara requisição delegada e recebe notas e faturas reais validadas sem falhas silenciosas[cite: 10].
        df_contabil = self.carregar_dados_contabeis()

        # Dispara e apreende os blocos lógicos apurando as massas monetárias atreladas à demonstração marginal dos gastos da PME[cite: 10].
        laudo_margem = self.calcular_margem_contribuicao(df_contabil)

        # Avalia riscos contra meta nula invocando o ponto crítico (Burn rate operacional e gap de saúde/segurança financeira da entidade)[cite: 10].
        laudo_equilibrio = self.calcular_ponto_equilibrio(laudo_margem)

        # Aciona os protocolos de traçado SVG/PNG materializando os números no disco e aprisionando o registro referencial (Path Object)[cite: 10].
        caminho_grafico = self.gerar_grafico_composicao_resultado(laudo_margem)

        # Sintetiza, engaveta e nomeia categoricamente as partes diagnósticas em uma estrutura dict formatada e limpa (Data DTO / Contract Format)[cite: 10].
        laudo_contabil = {
            "analise_margem_operacional": laudo_margem,
            "analise_ponto_critico_equilibrio": laudo_equilibrio,
            "grafico_composicao_dre_gerencial": str(caminho_grafico),
        }

        # Formaliza encerramento chancelando que não houveram exceptions intercorrentes no fluxo e todo pipeline gerencial foi exaurido com maestria[cite: 10].
        logging.info("=== DEPARTAMENTO CONTÁBIL CONCLUÍDO COM SUCESSO ===")

        return laudo_contabil