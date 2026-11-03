# 'from' indica a biblioteca ou módulo de onde extrairemos uma ferramenta específica.
# 'pathlib' é o módulo padrão do Python para manipulação orientada a objetos de caminhos no sistema de arquivos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com Windows, Linux e Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para anotações de tipagem estática (Type Hints).
# 'import' carrega 'Dict', 'List' e 'Optional' para documentar parâmetros e retornos de funções.
from typing import Dict, List, Optional

# 'import' traz o módulo 'logging' da biblioteca padrão do Python para registro rastreável de eventos e auditoria técnica.
import logging

# 'import' traz o módulo 're' da biblioteca padrão do Python para manipulação de expressões regulares e padrões de texto.
import re

# 'import' traz o módulo 'unicodedata' da biblioteca padrão para normalização e remoção de acentos diacríticos.
import unicodedata


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos na linguagem Python.
# 'ResolvedorSemantico' centraliza exclusivamente a inteligência léxica de correspondência de nomes de arquivos e colunas.
class ResolvedorSemantico:
    """Especialista responsável pela normalização léxica e casamento semântico de tabelas e atributos do ERP."""

    # 'SINONIMOS_TABELAS' armazena o catálogo de apelidos aceitos para cada entidade canônica com prioridade estrita de busca.
    SINONIMOS_TABELAS: Dict[str, List[str]] = {
        "vendas": [
            "nfetotal",
            "nfe_total",
            "faturamento",
            "vendas",
            "cupons",
            "cupom",
            "movimento_venda",
            "pedidos_vendas",
            "pedidos",
        ],
        "pessoas": [
            "pessoas",
            "pessoa",
            "clientes",
            "cliente",
            "nfedest",
            "participantes",
            "parceiros",
        ],
        "contas_receber": [
            "contasreceber",
            "contas_receber",
            "titulos_receber",
            "cr_titulos",
            "cobrancas",
        ],
        "contas_pagar": [
            "contaspagar",
            "contas_pagar",
            "titulos_pagar",
            "cp_titulos",
            "pagamentos",
            "despesas",
        ],
        "estoque": [
            "prodestoque",
            "prod_estoque",
            "produtos_saldo",
            "posicao_estoque",
            "estoque",
        ],
        "departamentos": [
            "departamentos",
            "departamento",
            "setores",
            "setor",
            "prodsubgrupo",
            "prodfamilia",
        ],
    }

    # 'SINONIMOS_COLUNAS' mapeia os termos equivalentes nos bancos legados para os conceitos padronizados do negócio.
    SINONIMOS_COLUNAS: Dict[str, List[str]] = {
        "valor": [
            "vnf",
            "valortotal",
            "valor_total",
            "valororiginal",
            "valor",
            "vltotal",
            "valorfaturado",
        ],
        "data_emissao": [
            "dhemi",
            "dataemissao",
            "data_emissao",
            "datapedido",
            "data_pedido",
            "dtemissao",
            "emissao",
            "data",
        ],
        "data_vencimento": [
            "datavencimento",
            "data_vencimento",
            "dtvencimento",
            "dt_vencimento",
            "vencimento",
            "dtvenc",
        ],
        "data_pagamento": [
            "datapagamento",
            "data_pagamento",
            "dtpagamento",
            "dt_pagamento",
            "liquidacao",
            "datapago",
        ],
        "id_transacao": [
            "id",
            "id_pedido",
            "id_nfe",
            "numnf",
            "numero_nf",
            "chave_acesso",
            "codigo",
        ],
        "id_cliente": [
            "idpessoa",
            "id_pessoa",
            "idcliente",
            "id_cliente",
            "cod_cliente",
            "cpf_cnpj",
        ],
        "nome_entidade": [
            "nomerazao",
            "nome_razao",
            "nomefantasia",
            "nome_fantasia",
            "nome",
            "razao_social",
            "fornecedor",
        ],
        "quantidade_estoque": [
            "estoqueatual",
            "estoque_atual",
            "saldo",
            "quantidadesaldo",
            "quantidade_saldo",
            "quantidade",
        ],
        "custo_unitario": [
            "precocusto",
            "preco_custo",
            "custounitario",
            "custo_unitario",
            "custo_medio",
        ],
        "descricao_item": [
            "descricao",
            "descricaoproduto",
            "descricao_produto",
            "nomeproduto",
            "xprod",
            "nome",
        ],
        "codigo_sku": [
            "codigobarras",
            "codigo_barras",
            "cprodanp",
            "idproduto",
            "id_produto",
            "codigo",
            "sku",
        ],
        "status_cobranca": [
            "statuscobranca",
            "status_cobranca",
            "status",
            "situacao",
            "status_pagamento",
        ],
        "id_nfe": [
            "idnfe",
            "id_nfe",
            "numeronf",
            "num_nf",
        ],
        "id_nfe_detalhe": [
            "idnfedet",
            "id_nfedet",
            "idnfedetsubitem",
        ],
        "quantidade_entrada": [
            "entrada",
            "qtdentrada",
            "quantidade_entrada",
        ],
        "quantidade_saida": [
            "saida",
            "qtdsaida",
            "quantidade_saida",
        ],
        "uf_cliente": [
            "uf",
            "estado",
            "sigla_uf",
            "siglauf",
        ],
        "cidade_cliente": [
            "cidade",
            "municipio",
            "nomecidade",
            "cidade_cliente",
            "xmun",
        ],
        "documento_fiscal": [
            "cnpj",
            "cpf",
            "cnpjcpf",
        ],
    }

    # 'DIRETORIO_CATALOGO_PADRAO' aponta para o catálogo semanticamente editável que acompanha o projeto.
    DIRETORIO_CATALOGO_PADRAO = Path(__file__).resolve().parents[3] / "nucleo" / "contratos" / "catalogo_semantico.json"

    # '__init__' carrega o catálogo padrão e permite a mescla de um catálogo aprendido por dataset.
    def __init__(self, catalogo_personalizado: Dict[str, Dict[str, List[str]]] | None = None) -> None:
        """Inicializa o resolvedor com o catálogo padrão do projeto mesclado ao personalizado.

        Args:
            catalogo_personalizado (Dict[str, Dict[str, List[str]]] | None): Mapa opcional
                com as chaves 'entidades' e 'papeis' que estendem o catálogo padrão.
                Permite que o humano ensine mapeamentos específicos de um ERP sem
                alterar o código-fonte.
        """
        self.sinonimos_tabelas: Dict[str, List[str]] = {
            chave: list(valores) for chave, valores in self.SINONIMOS_TABELAS.items()
        }
        self.sinonimos_colunas: Dict[str, List[str]] = {
            chave: list(valores) for chave, valores in self.SINONIMOS_COLUNAS.items()
        }

        # Carrega o catálogo padrão shipped com o projeto (fonte editável da verdade).
        self.carregar_catalogo_padrao()

        # Mescla o catálogo aprendido por dataset (ensinado pelo humano no frontend).
        if catalogo_personalizado:
            self.aplicar_catalogo(catalogo_personalizado)

        logging.info(
            "Resolvedor semântico ativo: %d entidades e %d papéis canônicos mapeados.",
            len(self.sinonimos_tabelas),
            len(self.sinonimos_colunas),
        )

    def aplicar_catalogo(self, catalogo: Dict[str, Dict[str, List[str]]]) -> None:
        """Mescla um catálogo semântico sobre o catálogo já carregado.

        Args:
            catalogo (Dict[str, Dict[str, List[str]]]): Mapa com 'entidades' e/ou 'papeis'.
        """
        for chave, valores in (catalogo.get("entidades") or {}).items():
            existentes = self.sinonimos_tabelas.setdefault(chave, [])
            for sinonimo in valores:
                if sinonimo not in existentes:
                    existentes.append(sinonimo)

        for chave, valores in (catalogo.get("papeis") or {}).items():
            existentes = self.sinonimos_colunas.setdefault(chave, [])
            for sinonimo in valores:
                if sinonimo not in existentes:
                    existentes.append(sinonimo)

    def carregar_catalogo_padrao(self) -> bool:
        """Carrega o catálogo semântico editável que acompanha o projeto.

        Returns:
            bool: ``True`` quando o arquivo foi lido com sucesso, ``False`` caso ausente.
        """
        if not self.DIRETORIO_CATALOGO_PADRAO.is_file():
            logging.warning(
                "Catálogo semântico padrão não localizado em: %s. Usando dicionários internos.",
                self.DIRETORIO_CATALOGO_PADRAO,
            )
            return False

        try:
            import json

            dados = json.loads(self.DIRETORIO_CATALOGO_PADRAO.read_text(encoding="utf-8"))
            self.aplicar_catalogo(
                {
                    "entidades": dados.get("entidades", {}),
                    "papeis": dados.get("papeis", {}),
                }
            )
            logging.info("Catálogo semântico padrão carregado de: %s", self.DIRETORIO_CATALOGO_PADRAO.name)
            return True
        except Exception as erro_carga:
            logging.error("Falha ao carregar o catálogo semântico padrão: %s", erro_carga)
            return False

    @classmethod
    def para_dataset(cls, pasta_registro_dataset: Path) -> "ResolvedorSemantico":
        """Constrói o resolvedor com o catálogo aprendido especificamente por um dataset.

        Args:
            pasta_registro_dataset (Path): Pasta do registro do dataset, onde pode residir
                um arquivo 'catalogo_semantico.json' com os mapeamentos ensinados.

        Returns:
            ResolvedorSemantico: Instância configurada com o catálogo específico.
        """
        import json

        caminho_personalizado = Path(pasta_registro_dataset) / "catalogo_semantico.json"
        catalogo: Dict[str, Dict[str, List[str]]] | None = None

        if caminho_personalizado.is_file():
            try:
                catalogo = json.loads(caminho_personalizado.read_text(encoding="utf-8"))
                logging.info(
                    "Catálogo semântico personalizado carregado para o dataset: %s",
                    caminho_personalizado.name,
                )
            except Exception as erro_carga:
                logging.error("Catálogo semântico personalizado inválido: %s", erro_carga)

        return cls(catalogo_personalizado=catalogo)

    # '@staticmethod' dispensa a necessidade de instanciar o objeto para usar funções utilitárias puras.
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Limpa e normaliza caracteres, suprimindo prefixos 'erp_', acentuações e pontuações."""
        # Avalia defensivamente se a string fornecida possui conteúdo real.
        if not texto:
            return ""

        # Converte a sequência para minúsculas e remove espaços residuais nas bordas.
        texto_limpo = str(texto).strip().lower()

        # Descarta o prefixo técnico 'erp_' inserido automaticamente durante a extração da Fase 1[cite: 1].
        if texto_limpo.startswith("erp_"):
            texto_limpo = texto_limpo[4:]

        # Normaliza a codificação Unicode decompondo os glifos acentuados de suas letras-base.
        texto_normalizado = unicodedata.normalize("NFKD", texto_limpo)

        # Reconstrói a cadeia filtrando apenas os caracteres que não sejam marcas de acento diacrítico.
        texto_sem_acentos = "".join(caractere for caractere in texto_normalizado if not unicodedata.combining(caractere))

        # Remove pontuações, caracteres especiais e espaços, mantendo apenas letras de 'a' a 'z' e números.
        return re.sub(r"[^a-z0-9]", "", texto_sem_acentos)

    # 'def' define o método especialista em encontrar o caminho do arquivo físico usando a ordem de prioridade.
    def localizar_arquivo_tabela(self, pasta_dados: Path, entidade_canonica: str) -> Optional[Path]:
        """Varre o diretório e encontra o arquivo CSV correspondente priorizando sinônimos corporativos oficiais.

        Arquivos presentes no disco mas **sem nenhuma linha de dados** são ignorados:
        exportações parciais de ERPs frequentemente carregam a tabela apenas com o
        cabeçalho, eercasear esse arquivo produziria uma ABT vazia sem diagnóstico.

        Args:
            pasta_dados (Path): Pasta contendo os CSVs do dataset.
            entidade_canonica (str): Entidade canônica desejada.

        Returns:
            Optional[Path]: Caminho do CSV populado ou ``None`` quando inexistente.
        """
        # Extrai a lista ordenada de sinônimos conhecidos para a entidade requisitada.
        lista_sinonimos = self.sinonimos_tabelas.get(entidade_canonica, [])

        # Lista todos os arquivos com formato CSV presentes na pasta física indicada.
        arquivos_disco = list(pasta_dados.glob("*.csv"))

        # Prioridade 1: Itera pelos sinônimos oficiais procurando correspondência exata de nomes.
        for alias in lista_sinonimos:
            alias_norm = self.normalizar_texto(alias)
            for arquivo in arquivos_disco:
                if self.normalizar_texto(arquivo.stem) == alias_norm and self._arquivo_tem_dados(arquivo):
                    logging.info("Tabela '%s' identificada via correspondência direta: %s", entidade_canonica, arquivo.name)
                    return arquivo

        # Prioridade 2: Procura por contenção parcial (substring) preservando a prioridade dos sinônimos.
        for alias in lista_sinonimos:
            alias_norm = self.normalizar_texto(alias)
            for arquivo in arquivos_disco:
                if alias_norm in self.normalizar_texto(arquivo.stem) and self._arquivo_tem_dados(arquivo):
                    logging.info("Tabela '%s' identificada via correspondência parcial: %s", entidade_canonica, arquivo.name)
                    return arquivo

        # Emite alerta caso a pasta inspecionada não apresente nenhuma tabela condizente.
        logging.warning("Nenhum arquivo CSV populado correspondente para a entidade '%s' em: %s", entidade_canonica, pasta_dados.name)
        return None

    @staticmethod
    def _arquivo_tem_dados(caminho_csv: Path) -> bool:
        """Verifica se um CSV possui ao menos uma linha de dados além do cabeçalho.

        Args:
            caminho_csv (Path): Caminho absoluto do arquivo CSV.

        Returns:
            bool: ``True`` quando existe ao menos um registro utilizável.
        """
        try:
            with open(caminho_csv, "r", encoding="utf-8", errors="ignore", newline="") as manipulador:
                linhas = 0
                for _ in manipulador:
                    linhas += 1
                    if linhas > 1:
                        return True
                return False
        except OSError:
            return False

    # 'def' define o método especialista em localizar colunas reais em uma lista de cabeçalhos.
    def resolver_coluna(self, colunas_existentes: List[str], papel_semantico: str) -> Optional[str]:
        """Descobre o nome original exato da coluna na tabela que desempenha o papel semântico indicado."""
        # Extrai a lista de termos aceitos para a função semântica (ex.: 'valor', 'data_emissao').
        sinonimos_papel = self.sinonimos_colunas.get(papel_semantico, [])

        # Prioridade 1: Casamento exato normalizado entre o cabeçalho real e os sinônimos.
        for alias in sinonimos_papel:
            alias_norm = self.normalizar_texto(alias)
            for coluna_real in colunas_existentes:
                if self.normalizar_texto(coluna_real) == alias_norm:
                    return coluna_real

        # Prioridade 2: Contenção de substring entre o cabeçalho real e os sinônimos.
        for alias in sinonimos_papel:
            alias_norm = self.normalizar_texto(alias)
            for coluna_real in colunas_existentes:
                if alias_norm in self.normalizar_texto(coluna_real):
                    return coluna_real

        # Retorna None caso a coluna não pertença ao dicionário semântico.
        return None