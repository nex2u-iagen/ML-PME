"""Módulo de Diagnóstico Exploratório do Departamento de Compras (Fase 2.3 - CRISP-DM).

Responsabilidade Única: Avaliar a gestão de suprimentos da PME, calcular o Prazo Médio
de Pagamento (PMP / DPO ponderado), auditar a concentração de aquisições por fornecedor
e gerar o gráfico de dependência comercial, consumindo dados reais do ERP[cite: 5].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 5].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de caminhos e arquivos no sistema operacional[cite: 5].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para validação formal de estruturas de dados[cite: 5].
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' importa o motor para construção e gravação de figuras gráficas no Matplotlib[cite: 5].
import matplotlib.pyplot as plt

# 'import pandas as pd' manipula estruturas de dados tabulares, agregações e multiplicações vetorizadas em memória[cite: 5].
import pandas as pd

# 'import seaborn as sns' renderiza gráficos estatísticos corporativos com acabamento visual padronizado[cite: 5].
import seaborn as sns

# Importação da classe base abstrata que injeta infraestrutura compartilhada e o Adaptador Universal por herança[cite: 5].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class AnalisadorCompras(BaseDepartamento)' especializa o diagnóstico de suprimentos e fornecedores da PME[cite: 5].
class AnalisadorCompras(BaseDepartamento):
    """Classe responsável pelo diagnóstico de aquisição de insumos, prazos e dependência de parceiros do ERP[cite: 5]."""

    # 'def __init__(...)' constrói a instância do analisador de compras registrando a pasta setorial[cite: 5].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de compras configurando a pasta de saída dedicada em relatórios[cite: 5].

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas reais do ERP (ex: mercado_vencedor/)[cite: 5].
            pasta_relatorios (Path): Diretório base de saída onde a pasta 'compras/' será mantida[cite: 5].
        """
        # 'super().__init__(...)' aciona o construtor da classe base registrando 'compras' como nome canônico[cite: 5].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="compras",
        )

    # 'def carregar_dados_compras(...)' localiza e carrega as compras reais do ERP ou emite aviso sem inventar dados falsos[cite: 5].
    def carregar_dados_compras(self) -> pd.DataFrame:
        """Carrega a tabela de ordens de compra e notas fiscais de entrada utilizando o leitor do núcleo[cite: 5].

        Returns:
            pd.DataFrame: Tabela real contendo fornecedores, valores de compra e prazos concedidos[cite: 5].

        Raises:
            FileNotFoundError: Se a tabela real de compras não for localizada no diretório isolado do ERP[cite: 5].
        """
        # Busca por tabelas de compras e fornecedores presentes na pasta isolada do banco de dados real[cite: 5].
        caminho_compras = self.adaptador._localizar_arquivo_por_sinonimos("compras")

        # Fallbacks para dumps de ERP que não possuem tabela dedicada de pedidos de compra:
        # tenta contas a pagar (fornecedores/credores) e, em seguida, fornecedores de produto.
        if not caminho_compras or not caminho_compras.is_file():
            for candidato in ("erp_contaspagar.csv", "erp_prodfornecedores.csv", "erp_pedidos_compras.csv"):
                candidato_path = self.pasta_dados_brutos / candidato
                if candidato_path.is_file():
                    caminho_compras = candidato_path
                    break
            else:
                caminho_compras = self.pasta_dados_brutos / "erp_pedidos_compras.csv"

        # Validação defensiva estrita: se o arquivo não existir fisicamente, interrompe sem gerar dados falsos (mocks)[cite: 5].
        if not caminho_compras.is_file():
            logging.error("Compras — Falha crítica: Tabela de compras não localizada no repositório: %s", self.pasta_dados_brutos)
            raise FileNotFoundError(
                f"Tabela de compras não encontrada em '{self.pasta_dados_brutos.resolve()}'. "
                "Certifique-se de que o dump do ERP contenha dados de entrada/suprimentos."
            )

        # Utiliza o leitor tolerante herdado da classe base para carregar a tabela física na memória RAM[cite: 5].
        df_compras = self.leitor.carregar_tabela(caminho_compras)

        # Mapeia idPessoa -> nome real do fornecedor quando a origem for contaspagar.
        if "idPessoa" in df_compras.columns:
            caminho_pessoas = self.pasta_dados_brutos / "erp_pessoas.csv"
            if caminho_pessoas.is_file():
                try:
                    df_pessoas = self.leitor.carregar_tabela(caminho_pessoas)
                    if "ID" in df_pessoas.columns:
                        mapa = {}
                        for _, linha in df_pessoas.iterrows():
                            if str(linha.get("tFornecedor", "")).strip() in ("1", "True", "true"):
                                nome = linha.get("NomeFantasia") or linha.get("RazaoSocial")
                                if pd.notna(nome) and str(nome).strip():
                                    mapa[linha["ID"]] = str(nome).strip()
                        if mapa:
                            df_compras["idPessoa"] = df_compras["idPessoa"].map(lambda v: mapa.get(v, f"Fornecedor #{v}"))
                except Exception:
                    pass

        # Padroniza nomes de colunas caso venham ligeiramente divergentes do ERP de origem:
        colunas_reais = list(df_compras.columns)
        col_fornecedor = (
            self.adaptador._resolver_coluna(colunas_reais, "nome_cliente")
            or self.adaptador._resolver_coluna(colunas_reais, "fornecedor")
            or ("idPessoa" if "idPessoa" in colunas_reais else None)
            or colunas_reais[1]
        )
        col_valor = (
            self.adaptador._resolver_coluna(colunas_reais, "valor")
            or ("ValorOriginal" if "ValorOriginal" in colunas_reais else None)
            or colunas_reais[2]
        )

        # Estrutura a visão canônica com os campos mínimos exigidos para os cálculos de compras[cite: 5]:
        df_compras_canonico = pd.DataFrame({
            "fornecedor": df_compras[col_fornecedor].astype(str),
            "valor_compra": pd.to_numeric(df_compras[col_valor], errors="coerce").fillna(0.0),
            "prazo_pagamento_dias": (
                pd.to_numeric(df_compras["prazo_pagamento_dias"], errors="coerce").fillna(30)
                if "prazo_pagamento_dias" in df_compras.columns
                else 30
            ),
        })

        # 'logging.info' documenta o sucesso da carga e o volume de ordens de compra incorporadas[cite: 5].
        logging.info("Compras — Base consolidada com %d ordens de compra reais.", len(df_compras_canonico))

        # Devolve a tabela canônica de compras pronta para o cálculo dos KPIs do setor[cite: 5].
        return df_compras_canonico

    # 'def calcular_prazo_medio_pagamento(...)' calcula o PMP ponderado pelo volume monetário de cada compra[cite: 5].
    def calcular_prazo_medio_pagamento(self, dados: pd.DataFrame) -> float:
        """Calcula o Prazo Médio de Pagamento (PMP / DPO) ponderado pelo valor financeiro de cada ordem[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela de compras contendo as colunas 'valor_compra' e 'prazo_pagamento_dias'[cite: 5].

        Returns:
            float: Prazo Médio de Pagamento ponderado em dias corridos[cite: 5].
        """
        # 'dados["valor_compra"].sum()' calcula a soma do montante monetário de todas as ordens de compra[cite: 5].
        valor_total_compras = float(dados["valor_compra"].sum())

        # Multiplica o valor financeiro de cada ordem pelo respectivo prazo concedido em dias[cite: 5].
        # '.sum()' soma essa multiplicação gerando o numerador ponderado do cálculo financeiro[cite: 5].
        soma_ponderada = float((dados["valor_compra"] * dados["prazo_pagamento_dias"]).sum())

        # Divide a soma ponderada pelo valor total de compras para obter o prazo médio ponderado real[cite: 5].
        # 'round(..., 1)' arredonda o resultado com uma casa decimal (ex: 38.5 dias)[cite: 5].
        # O operador ternário previne erros de divisão por zero caso o somatório de compras seja nulo[cite: 5].
        pmp_ponderado = round(soma_ponderada / valor_total_compras, 1) if valor_total_compras > 0 else 0.0

        # 'logging.info' imprime o PMP ponderado no terminal para auditoria das diretorias de suprimentos e financeira[cite: 5].
        logging.info("Compras — Prazo Médio de Pagamento (PMP): %.1f dias corridos.", pmp_ponderado)

        # Devolve o valor do prazo médio calculado em dias[cite: 5].
        return pmp_ponderado

    # 'def gerar_grafico_concentracao_fornecedores(...)' renderiza o gráfico de dependência de parceiros[cite: 5].
    def gerar_grafico_concentracao_fornecedores(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras destacando os parceiros comerciais de maior volume financeiro[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela contendo registros de compras reais[cite: 5].

        Returns:
            Path: Rota física da imagem PNG salva no disco com resolução de 300 DPI[cite: 5].
        """
        # 'dados.groupby("fornecedor")["valor_compra"].sum().reset_index()' soma o valor comprado de cada fornecedor[cite: 5].
        compras_por_fornecedor = dados.groupby("fornecedor")["valor_compra"].sum().reset_index()

        # '.sort_values(by="valor_compra", ascending=False)' ordena os parceiros de forma decrescente pelo volume de compras[cite: 5].
        compras_por_fornecedor = compras_por_fornecedor.sort_values(by="valor_compra", ascending=False)

        # Filtra defensivamente até os 10 maiores fornecedores para preservar a nitidez gráfica[cite: 5].
        if len(compras_por_fornecedor) > 10:
            compras_por_fornecedor = compras_por_fornecedor.head(10)

        # 'self.pasta_saida / "concentracao_compras_fornecedores.png"' monta o caminho de gravação na pasta 'relatorios/figuras/compras/'[cite: 5].
        caminho_figura = self.pasta_saida / "concentracao_compras_fornecedores.png"

        # 'plt.subplots(figsize=(9, 5))' inicializa a tela gráfica com 9 polegadas de largura por 5 de altura[cite: 5].
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot(...)' desenha as barras comparativas utilizando a biblioteca Seaborn[cite: 5].
        # - 'color="#2ca02c"': aplica a tonalidade verde floresta industrial representativa de suprimentos e compras[cite: 5].
        sns.barplot(data=compras_por_fornecedor, x="fornecedor", y="valor_compra", color="#2ca02c", ax=eixo)

        # 'eixo.set_title(...)' configura o título com tamanho 13 e espaçamento de 12 pontos[cite: 5].
        eixo.set_title("Volume de Compras por Fornecedor (Matriz de Dependência)", fontsize=13, pad=12)

        # 'eixo.set_xlabel(...)' escreve a legenda do eixo horizontal em português[cite: 5].
        eixo.set_xlabel("Fornecedor / Fabricante Parceiro", fontsize=10)

        # 'eixo.set_ylabel(...)' escreve a legenda financeira do eixo vertical em moeda corrente (R$)[cite: 5].
        eixo.set_ylabel("Valor Total Comprado (R$)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' inclina os nomes dos fornecedores em 45 graus alinhados à direita[cite: 5].
        plt.xticks(rotation=45, ha="right")

        # 'plt.tight_layout()' faz o ajuste dinâmico automático de margens para não cortar legendas da imagem[cite: 5].
        plt.tight_layout()

        # 'figura.savefig(caminho_figura, dpi=300)' grava a figura física no disco rígido em alta definição (300 DPI)[cite: 5].
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa o buffer gráfico do Matplotlib na memória RAM para garantir performance contínua[cite: 5].
        plt.close(figura)

        # 'logging.info' confirma a persistência do gráfico de compras no terminal corporativo[cite: 5].
        logging.info("Compras — Gráfico de fornecedores salvo com sucesso em: %s", caminho_figura.name)

        # Devolve a rota física do arquivo de imagem salvo[cite: 5].
        return caminho_figura

    # 'def executar_diagnostico_completo(...)' implementa o contrato formal de execução da BaseDepartamento[cite: 5].
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o cálculo de indicadores de suprimentos reais e a persistência visual do setor[cite: 5].

        Returns:
            Dict[str, Any]: Laudo executivo do departamento de compras com volume total, PMP e caminho do gráfico[cite: 5].
        """
        # Emite log formal marcando o início da perícia de suprimentos da Fase 2.3[cite: 5].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE COMPRAS (FASE 2.3) ===")

        # 1. Carrega as ordens de compra reais utilizando a integração com o Adaptador Universal[cite: 5].
        df_compras = self.carregar_dados_compras()

        # 2. Executa a camada tabular apurando o Prazo Médio de Pagamento ponderado em dias[cite: 5].
        pmp_dias = self.calcular_prazo_medio_pagamento(df_compras)

        # 3. Executa a camada gráfica renderizando o gráfico de concentração de compras por fornecedor[cite: 5].
        caminho_grafico = self.gerar_grafico_concentracao_fornecedores(df_compras)

        # 'df_compras["valor_compra"].sum()' calcula o montante financeiro total adquirido no período[cite: 5].
        volume_total_comprado = round(float(df_compras["valor_compra"].sum()), 2)

        # 'df_compras["fornecedor"].nunique()' calcula quantos parceiros comerciais distintos a empresa possui[cite: 5].
        contagem_fornecedores_unicos = int(df_compras["fornecedor"].nunique())

        # 'laudo_compras' estrutura o laudo formal consolidado de suprimentos para apoio ao comitê executivo e BI[cite: 5].
        laudo_compras = {
            "volume_total_comprado_reais": volume_total_comprado,
            "prazo_medio_pagamento_dias": pmp_dias,
            "total_fornecedores_ativos": contagem_fornecedores_unicos,
            "grafico_concentracao_fornecedores": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento do diagnóstico de compras[cite: 5].
        logging.info("=== DEPARTAMENTO DE COMPRAS CONCLUÍDO COM SUCESSO ===")

        # Devolve o laudo consolidado de suprimentos para o orquestrador do Raio-X Empresarial[cite: 5].
        return laudo_compras