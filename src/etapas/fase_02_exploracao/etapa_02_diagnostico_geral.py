# 'from' indica a biblioteca ou módulo de onde extrairemos uma ferramenta específica.
# 'pathlib' é o módulo padrão do Python para manipulação orientada a objetos de caminhos no sistema de arquivos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com Windows, Linux e Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para anotações de tipagem estática (Type Hints).
# 'import' carrega 'Any' e 'Dict' para documentação estrutural e formal dos tipos de retorno.
from typing import Any, Dict

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro profissional de eventos e auditoria.
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação, cálculo de nulos e dimensões tabulares em memória RAM.
# 'as' define o apelido universal 'pd', padrão absoluto na Ciência de Dados.
import pandas as pd

# 'from' navega até a camada fundamental de acesso a dados do núcleo compartilhado do projeto.
# 'import' reaproveita a classe 'LeitorArquivosTabulares' para leitura defensiva com tolerância a codificações.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# 'logging.basicConfig' parametriza a formatação dos registros no console corporativo.
# 'level=logging.INFO' assegura que avisos de progresso, relatórios e resumos sejam exibidos.
# 'format' dita o molde visual com carimbo de data/hora atual, gravidade do alerta e descrição do evento.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o novo molde estrutural orientado a objetos na linguagem Python.
# 'AuditorSaudeDados' centraliza a responsabilidade da triagem mecânica e tipológica macro de todas as tabelas.
class AuditorSaudeDados:
    """Classe responsável por auditar a qualidade mecânica e estatística inicial das tabelas do ERP."""

    # 'def' define o método especial construtor '__init__', acionado no momento em que a classe é instanciada na memória.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_dados_brutos: Path' exige receber o caminho onde estão armazenados os arquivos CSV do ERP.
    # '-> None' atesta formalmente que o método inicializador não retorna dados para quem o chamou.
    def __init__(self, pasta_dados_brutos: Path) -> None:
        """Inicializa o auditor configurando o diretório com resolução automática de subpastas de bancos."""
        # 'self.pasta_dados_brutos' armazena o caminho recebido internamente no objeto.
        self.pasta_dados_brutos = pasta_dados_brutos

        # RESOLUÇÃO DEFENSIVA DE SUBPASTAS:
        # Verifica se o diretório recebido contém uma subpasta isolada de banco de dados (ex: 'mercado_vencedor/').
        subpastas_detectadas = [
            p for p in self.pasta_dados_brutos.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "mocks"
        ]

        # Se houver uma subpasta de banco de dados isolada, ancora a busca diretamente nela.
        if subpastas_detectadas:
            self.pasta_dados_brutos = subpastas_detectadas[0]
            logging.info("Auditor de Saúde reposicionado para a subpasta isolada: %s", self.pasta_dados_brutos.name)

        # Aplicamos o padrão de Composição de Objetos: instanciamos a ferramenta de leitura do núcleo compartilhado.
        self.leitor = LeitorArquivosTabulares()

        # Emite log no console confirmando a pasta física final em que a perícia será executada.
        logging.info("Auditor de Saúde de Dados configurado para: %s", self.pasta_dados_brutos.resolve())

    # 'def' define o método que audita uma tabela isolada a partir do seu endereço físico no disco.
    def auditar_tabela(self, caminho_arquivo_csv: Path) -> Dict[str, Any]:
        """Realiza um diagnóstico completo da integridade física e tipológica de uma tabela específica."""
        # 'caminho_arquivo_csv.name' extrai apenas o nome final do arquivo para fins de exibição limpa.
        nome_tabela = caminho_arquivo_csv.name

        # Emite log informando o início da perícia estrutural na tabela atual.
        logging.info("Iniciando auditoria estrutural na tabela: %s", nome_tabela)

        # Utiliza o leitor do núcleo para carregar a tabela na memória RAM de forma segura e defensiva.
        dados_tabela = self.leitor.carregar_tabela(caminho_arquivo_csv)

        # 'dados_tabela.shape[0]' retorna a contagem inteira de linhas (registros) da matriz tabular.
        total_linhas = int(dados_tabela.shape[0])

        # 'dados_tabela.shape[1]' retorna a contagem inteira de colunas (atributos) da matriz tabular.
        total_colunas = int(dados_tabela.shape[1])

        # 'dados_tabela.duplicated().sum()' identifica linhas perfeitamente repetidas em todas as colunas.
        total_duplicadas = int(dados_tabela.duplicated().sum())

        # 'dados_tabela.isnull().sum()' calcula a quantidade de valores vazios (NaN/None) por coluna.
        contagem_nulos = dados_tabela.isnull().sum()

        # Calcula o impacto percentual de ausência para cada coluna da tabela.
        percentual_nulos = (contagem_nulos / total_linhas) * 100 if total_linhas > 0 else contagem_nulos

        # 'pd.concat' une a contagem absoluta e o percentual lado a lado em um novo DataFrame de relatório.
        tabela_nulos = pd.concat([contagem_nulos, percentual_nulos], axis=1)

        # Define rótulos claros para as colunas do relatório de valores faltantes.
        tabela_nulos.columns = ["total_ausentes", "percentual_ausente"]

        # Filtra apenas atributos que possuem pelo menos 1 valor faltante para evitar relatórios poluídos.
        colunas_com_nulos = tabela_nulos[tabela_nulos["total_ausentes"] > 0].to_dict(orient="index")

        # Lista Python para consolidar tipos primitivos e cardinalidade por coluna.
        lista_detalhes_colunas = []

        # Itera por cada nome de coluna contido na matriz tabular.
        for nome_coluna in dados_tabela.columns:
            serie_coluna = dados_tabela[nome_coluna]
            tipo_dado = str(serie_coluna.dtype)
            cardinalidade = int(serie_coluna.nunique())

            lista_detalhes_colunas.append({
                "nome_coluna": nome_coluna,
                "tipo_primitivo": tipo_dado,
                "valores_unicos": cardinalidade,
                "provavel_identificador": bool(cardinalidade == total_linhas and total_linhas > 0),
            })

        # 'laudo_tabela' é o dicionário que reúne todas as descobertas da auditoria estrutural da tabela.
        laudo_tabela: Dict[str, Any] = {
            "nome_arquivo": nome_tabela,
            "total_linhas": total_linhas,
            "total_colunas": total_colunas,
            "linhas_duplicadas": total_duplicadas,
            "colunas_com_valores_nulos": colunas_com_nulos,
            "resumo_atributos": lista_detalhes_colunas,
        }

        # Emite log resumindo as conclusões da auditoria estrutural da tabela.
        logging.info(
            "Laudo de '%s': %d linhas | %d colunas | %d duplicadas | %d colunas com nulos.",
            nome_tabela,
            total_linhas,
            total_colunas,
            total_duplicadas,
            len(colunas_com_nulos),
        )

        return laudo_tabela

    # 'def' define o método orquestrador que executa a varredura completa em todas as tabelas do diretório.
    def executar_diagnostico_completo(self) -> Dict[str, Dict[str, Any]]:
        """Executa a auditoria geral em todos os arquivos CSV presentes na pasta oficial sob perícia."""
        logging.info("=== INICIANDO FASE 02: DIAGNÓSTICO GERAL DE SAÚDE DOS DADOS ===")

        # Pesquisa todos os arquivos com extensão '.csv' no diretório oficial ativo.
        arquivos_csv = sorted(list(self.pasta_dados_brutos.glob("*.csv")))

        # Fallback defensivo: se a pasta não tiver arquivos CSV diretos, faz a busca recursiva em subníveis.
        if not arquivos_csv:
            arquivos_csv = sorted(list(self.pasta_dados_brutos.rglob("*.csv")))

        # Checagem defensiva: alerta caso não existam arquivos CSV no local.
        if not arquivos_csv:
            logging.error("Nenhum arquivo CSV encontrado para auditoria em: %s", self.pasta_dados_brutos)
            raise FileNotFoundError(f"Diretório sem arquivos CSV: {self.pasta_dados_brutos.resolve()}")

        # Dicionário consolidado que armazenará os laudos de todas as tabelas periciadas.
        relatorio_consolidado: Dict[str, Dict[str, Any]] = {}

        # Itera ordenadamente por cada arquivo CSV localizado.
        for caminho_csv in arquivos_csv:
            chave_tabela = caminho_csv.stem
            laudo_individual = self.auditar_tabela(caminho_csv)
            relatorio_consolidado[chave_tabela] = laudo_individual

        # Emite log confirmando a conclusão bem-sucedida do diagnóstico macro.
        logging.info(
            "=== FASE 02 (DIAGNÓSTICO GERAL) CONCLUÍDA: %d TABELAS AUDITADAS ===",
            len(relatorio_consolidado),
        )

        return relatorio_consolidado