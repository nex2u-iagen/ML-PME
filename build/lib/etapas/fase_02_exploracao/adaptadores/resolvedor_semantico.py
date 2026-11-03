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
    }

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
        """Varre o diretório e encontra o arquivo CSV correspondente priorizando sinônimos corporativos oficiais."""
        # Extrai a lista ordenada de sinônimos conhecidos para a entidade requisitada.
        lista_sinonimos = self.SINONIMOS_TABELAS.get(entidade_canonica, [])

        # Lista todos os arquivos com formato CSV presentes na pasta física indicada.
        arquivos_disco = list(pasta_dados.glob("*.csv"))

        # Prioridade 1: Itera pelos sinônimos oficiais procurando correspondência exata de nomes.
        for alias in lista_sinonimos:
            alias_norm = self.normalizar_texto(alias)
            for arquivo in arquivos_disco:
                if self.normalizar_texto(arquivo.stem) == alias_norm:
                    logging.info("Tabela '%s' identificada via correspondência direta: %s", entidade_canonica, arquivo.name)
                    return arquivo

        # Prioridade 2: Procura por contenção parcial (substring) preservando a prioridade dos sinônimos.
        for alias in lista_sinonimos:
            alias_norm = self.normalizar_texto(alias)
            for arquivo in arquivos_disco:
                if alias_norm in self.normalizar_texto(arquivo.stem):
                    logging.info("Tabela '%s' identificada via correspondência parcial: %s", entidade_canonica, arquivo.name)
                    return arquivo

        # Emite alerta caso a pasta inspecionada não apresente nenhuma tabela condizente.
        logging.warning("Nenhum arquivo CSV correspondente para a entidade '%s' em: %s", entidade_canonica, pasta_dados.name)
        return None

    # 'def' define o método especialista em localizar colunas reais em uma lista de cabeçalhos.
    def resolver_coluna(self, colunas_existentes: List[str], papel_semantico: str) -> Optional[str]:
        """Descobre o nome original exato da coluna na tabela que desempenha o papel semântico indicado."""
        # Extrai a lista de termos aceitos para a função semântica (ex.: 'valor', 'data_emissao').
        sinonimos_papel = self.SINONIMOS_COLUNAS.get(papel_semantico, [])

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