"""Módulo de Orquestração da Ingestão de Dados (Fase 01).

Responsável por orquestrar a carga de dados de ERPs de PMEs,
convertendo dumps estruturais SQL para arquivos tabulares CSV
e validando a integridade das entidades para as etapas seguintes.
"""

# 'import' traz o módulo 'logging' da biblioteca padrão do Python para mensagens
# profissionais no terminal.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' carrega 'Path' para manipular
# pastas e caminhos de arquivos.
from pathlib import Path

# 'from' acessa o módulo 'typing' nativo do Python para documentar tipos de dados de
# variáveis e parâmetros.
# 'Dict' documenta dicionários de chave e valor; 'List' documenta listas ordenadas de
# itens.
# 'import' carrega a biblioteca externa 'pandas', especialista na manipulação de tabelas
# bidimensionais em memória.
# 'as' define o apelido universal 'pd', padrão absoluto adotado na Ciência de Dados.
import pandas as pd

# 'from' importa a classe 'ConectorBancoRelacional' do núcleo, especialista em
# desempacotar arquivos .sql pesados.
from src.nucleo.acesso_dados.conector_banco_relacional import ConectorBancoRelacional

# 'from' navega até o submódulo de acesso a dados do núcleo compartilhado do nosso
# projeto.
# 'import' traz a classe 'LeitorArquivosTabulares' que construímos anteriormente,
# aplicando o reuso de código.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# 'logging.basicConfig' configura a aparência dos avisos no console do sistema
# operacional.
# 'level=logging.INFO' exibe confirmações operacionais, avisos de progresso e eventuais
# falhas.
# 'format' define o molde visual da mensagem: ano-mês-dia hora:minuto:segundo —
# [GRAVIDADE] — texto da ação.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'OrquestradorIngestao' expressa com precisão semântica a responsabilidade única da
# classe: orquestrar a Fase 1.
class OrquestradorIngestao:
    """Classe responsável por coordenar a extração, conversão e auditoria de dados
    brutos.
    """

    # 'def' define o método especial construtor '__init__', executado no momento da
    # instanciação da classe.
    # 'self' referencia a própria instância que está sendo criada na memória RAM.
    # 'diretorio_raiz: Path' exige receber o caminho base onde repousa o nosso projeto.
    # '-> None' atesta formalmente que o método inicializador não retorna nenhum dado
    # para quem o chamou.
    def __init__(self, diretorio_raiz: Path) -> None:
        """Inicializa o orquestrador configurando os ponteiros de diretórios oficiais.

        Args:
            diretorio_raiz (Path): Caminho absoluto da pasta raiz do projeto de dados.
        """
        # 'self.diretorio_raiz' armazena o caminho base na memória interna do próprio
        # objeto.
        self.diretorio_raiz = diretorio_raiz

        # O operador de barra '/' une caminhos de forma segura tanto no Windows quanto
        # no Linux via Pathlib.
        # 'self.pasta_sql' aponta para o diretório de arquivos de backup pesados do ERP.
        self.pasta_sql = self.diretorio_raiz / "dados" / "brutos" / "sql"

        # 'self.pasta_csv' aponta para o diretório de arquivos delimitados e tabelas
        # extraídas.
        self.pasta_csv = self.diretorio_raiz / "dados" / "brutos" / "csv"

        # Aplicamos o padrão de Composição de Objetos: instanciamos os especialistas do
        # núcleo como ferramentas.
        # 'self.leitor_csv' recebe a instância da ferramenta de leitura de arquivos
        # planos.
        self.leitor_csv = LeitorArquivosTabulares()

        # 'self.conector_sql' recebe a ferramenta especialista em bancos de dados
        # relacionais e dumps DDL/DML.
        self.conector_sql = ConectorBancoRelacional(tamanho_lote=50_000)

        # 'mkdir(parents=True, exist_ok=True)' garante a criação física das pastas caso
        # ainda não existam no disco.
        self.pasta_sql.mkdir(parents=True, exist_ok=True)
        self.pasta_csv.mkdir(parents=True, exist_ok=True)

        # Emite um log informativo no console confirmando a prontidão da esteira de
        # ingestão.
        logging.info(
            "Orquestrador de Ingestão ativo. SQL: %s | CSV: %s",
            self.pasta_sql.name,
            self.pasta_csv.name,
        )

    # 'def' define o método para simular e gerar dados sintéticos de teste caso as
    # pastas estejam vazias.
    # '-> List[Path]' avisa que a função devolverá uma lista contendo os caminhos dos
    # arquivos gerados.
    def criar_dados_sinteticos_erp(self) -> list[Path]:
        """Gera bases sintéticas realistas de ERP (clientes, pedidos e financeiro) para
        testes práticos.

        Returns:
            List[Path]: Lista de objetos Path contendo os endereços dos arquivos CSV
            criados.
        """
        # Emite log avisando que o gerador de dados didáticos de ERP foi acionado.
        logging.info(
            "Gerando massa de dados sintética de ERP para viabilizar os testes da"
            "esteira..."
        )

        # 'dados_clientes' é um dicionário Python ('{}') contendo listas ('[]')
        # simulando a tabela 'clientes'.
        dados_clientes: dict[str, list] = {
            "id_cliente": [101, 102, 103, 104, 105, 106, 107, 108],
            "nome_fantasia": [
                "Padaria Estrela",
                "Mercado Bom Preço",
                "Auto Peças Silva",
                "Restaurante Sabor",
                "Farmácia Central",
                "Oficina São Jorge",
                "Lanchonete União",
                "Materiais Construção Real",
            ],
            "segmento": [
                "Alimentação",
                "Varejo",
                "Automotivo",
                "Alimentação",
                "Saúde",
                "Automotivo",
                "Alimentação",
                "Construção",
            ],
            "limite_credito": [
                15000.0,
                50000.0,
                30000.0,
                12000.0,
                45000.0,
                20000.0,
                8000.0,
                60000.0,
            ],
            "dias_prazo_pagamento": [30, 45, 28, 15, 60, 30, 14, 45],
        }

        # 'dados_pedidos' é um dicionário contendo as transações comerciais simuladas de
        # vendas do ERP.
        dados_pedidos: dict[str, list] = {
            "id_pedido": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
            "id_cliente": [101, 102, 101, 103, 104, 105, 102, 106, 107, 108],
            "data_pedido": [
                "2026-01-10",
                "2026-01-12",
                "2026-01-15",
                "2026-01-18",
                "2026-01-20",
                "2026-01-22",
                "2026-01-25",
                "2026-01-28",
                "2026-02-01",
                "2026-02-05",
            ],
            "valor_total": [
                3500.50,
                12800.00,
                4200.00,
                8900.20,
                1500.00,
                22000.00,
                9500.00,
                3100.00,
                980.00,
                45000.00,
            ],
            "status_pagamento": [
                "Pago",
                "Pago",
                "Atrasado",
                "Pago",
                "Atrasado",
                "Pago",
                "Pago",
                "Inadimplente",
                "Pago",
                "Atrasado",
            ],
            # 'inadimplente': variável alvo binária (0 = Bom Pagador, 1 =
            # Calote/Inadimplência).
            "inadimplente": [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        }

        # 'pd.DataFrame' converte as estruturas de dicionário em matrizes tabulares
        # bidimensionais do pandas.
        tabela_clientes = pd.DataFrame(dados_clientes)
        tabela_pedidos = pd.DataFrame(dados_pedidos)

        # Monta os caminhos físicos onde os arquivos didáticos serão gravados dentro da
        # pasta de CSV bruto.
        caminho_csv_clientes = self.pasta_csv / "erp_clientes.csv"
        caminho_csv_pedidos = self.pasta_csv / "erp_pedidos_vendas.csv"

        # '.to_csv' grava as matrizes no disco; 'index=False' impede a criação de
        # colunas de índices desnecessárias.
        tabela_clientes.to_csv(caminho_csv_clientes, index=False)
        tabela_pedidos.to_csv(caminho_csv_pedidos, index=False)

        # Emite log confirmando a gravação dos datasets sintéticos no disco.
        logging.info("Bases de teste gravadas com sucesso em: %s", self.pasta_csv)

        # 'lista_arquivos' reúne os caminhos em uma lista estruturada do Python ('[]').
        lista_arquivos = [caminho_csv_clientes, caminho_csv_pedidos]

        # 'return' devolve a lista com os arquivos criados para o pipeline de execução.
        return lista_arquivos

    # 'def' define o método central de execução de toda a Fase 01.
    # '-> Dict[str, pd.DataFrame]' documenta que o retorno será um dicionário onde cada
    # chave é o nome da tabela
    # e o valor é o DataFrame do pandas carregado e pronto para a Fase 02.
    def executar_fase_ingestao(self) -> dict[str, pd.DataFrame]:
        """Executa o ciclo completo da Fase 01: descobre, converte e carrega as
        entidades do ERP.

        Returns:
            Dict[str, pd.DataFrame]: Dicionário contendo as tabelas do ERP carregadas em
            memória.
        """
        # Emite log marcando o início oficial da execução da Fase 01.
        logging.info("=== INICIANDO EXECUÇÃO DA FASE 01: INGESTÃO DE DADOS ===")

        # 'self.pasta_sql.glob("*.sql")' faz uma varredura buscando qualquer arquivo que
        # termine com '.sql'.
        # 'list()' converte o iterador retornado em uma lista manipulável do Python.
        arquivos_sql_encontrados = list(self.pasta_sql.glob("*.sql"))

        # 'if' avalia se encontramos algum arquivo de backup SQL depositado no
        # diretório.
        if arquivos_sql_encontrados:
            # Pega o primeiro arquivo .sql da lista para processar.
            arquivo_sql = arquivos_sql_encontrados[0]
            # Define o caminho do banco SQLite temporário local que servirá de ponte
            # relacional.
            caminho_banco_temp = self.pasta_sql / "banco_intermediario_erp.db"

            # Utiliza a ferramenta do núcleo para reconstruir a estrutura do banco
            # relacional a partir do dump.
            motor_sql = self.conector_sql.reconstruir_banco_sqlite(
                arquivo_sql, caminho_banco_temp
            )

            # Exporta a tabela transacional de pedidos para a pasta de CSV bruto de
            # forma fatiada (chunks).
            caminho_destino_pedidos = self.pasta_csv / "erp_pedidos_vendas.csv"
            self.conector_sql.exportar_tabela_para_csv(
                motor_sql, "pedidos", caminho_destino_pedidos
            )

        # 'self.pasta_csv.glob("*.csv")' faz uma varredura para localizar todos os
        # arquivos CSV existentes.
        arquivos_csv_encontrados = list(self.pasta_csv.glob("*.csv"))

        # 'if not' verifica defensivamente: se a pasta de CSV estiver completamente
        # vazia, geramos dados de teste.
        if not arquivos_csv_encontrados:
            logging.warning(
                "Nenhum dado encontrado em dados/brutos/. Gerando dados sintéticos"
                "automáticos..."
            )
            # Invoca o método auxiliar de criação sintética para não interromper a
            # esteira analítica.
            arquivos_csv_encontrados = self.criar_dados_sinteticos_erp()

        # 'tabelas_carregadas' é um dicionário vazio que receberá as matrizes prontas
        # para a Fase 02.
        tabelas_carregadas: dict[str, pd.DataFrame] = {}

        # 'for' itera por cada arquivo CSV localizado no diretório de dados brutos.
        for caminho_arquivo in arquivos_csv_encontrados:
            # 'caminho_arquivo.stem' extrai apenas o nome do arquivo sem a extensão
            # (ex.: 'erp_clientes').
            nome_entidade = caminho_arquivo.stem

            # Utiliza o leitor de arquivos do núcleo para realizar a leitura defensiva
            # na memória.
            dataframe_lido = self.leitor_csv.carregar_tabela(caminho_arquivo)

            # Armazena a tabela lida no dicionário sob o nome da entidade
            # correspondente.
            tabelas_carregadas[nome_entidade] = dataframe_lido

            # Emite log detalhando o volume de registros (linhas) e atributos (colunas)
            # incorporados.
            logging.info(
                "Entidade '%s' validada com sucesso: %d registros e %d atributos.",
                nome_entidade,
                dataframe_lido.shape[0],
                dataframe_lido.shape[1],
            )

        # Emite log confirmando a conclusão bem-sucedida da Fase 01.
        logging.info(
            "=== FASE 01 CONCLUÍDA: %d ENTIDADES PRONTAS PARA ANÁLISE EXPLORATÓRIA ===",
            len(tabelas_carregadas),
        )

        # 'return' entrega o dicionário com todas as matrizes para quem disparou o
        # orquestrador.
        return tabelas_carregadas


# '__name__ == "__main__"' é o padrão do Python que permite executar este arquivo
# diretamente via terminal.
if __name__ == "__main__":
    # '__file__' aponta para este arquivo atual; '.resolve()' gera o caminho absoluto no
    # sistema operacional.
    # '.parent' sobe um nível: 'fase_01_ingestao' -> 'etapas' -> 'src' -> raiz do
    # repositório.
    raiz_do_projeto = Path(__file__).resolve().parent.parent.parent.parent

    # Instancia a nossa classe de orquestração passando a raiz física calculada.
    orquestrador = OrquestradorIngestao(diretorio_raiz=raiz_do_projeto)

    # Executa a esteira da Fase 01 e recebe as tabelas prontas.
    dados_ingeridos = orquestrador.executar_fase_ingestao()
