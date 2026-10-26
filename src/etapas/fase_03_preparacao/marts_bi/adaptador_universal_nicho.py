"""Módulo Adaptador Universal de Esquema de Negócios para Data Marts de BI.

Permite que a esteira de preparação de BI processe dados de qualquer nicho
(comércio, indústria, clínicas, serviços) através de um dicionário dinâmico
de mapeamento de colunas, garantindo Alta Coesão e Baixo Acoplamento.
"""

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos de
# forma orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de pastas compatíveis com
# Windows, Linux e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotação estática de tipos
# (Type Hints).
# 'Any' indica múltiplos tipos aceitos; 'Dict' documenta estruturas de chave e valor.
# 'import' traz a biblioteca externa 'pandas', padrão mundial para manipulação de
# tabelas em memória.
# 'as' define o apelido clássico 'pd' para encurtar comandos de manipulação de
# DataFrames.
import pandas as pd

# 'from' navega até o submódulo de acesso a dados do nosso núcleo compartilhado.
# 'import' traz a ferramenta desacoplada de leitura tabular de arquivos.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' declara o adaptador universal orientado a objetos.
class AdaptadorUniversalBI:
    """Classe responsável por padronizar esquemas de ERPs de qualquer nicho para o
    modelo canônico de BI.
    """

    # 'def' define o método construtor '__init__'.
    # 'self' referencia a própria instância construída em memória RAM.
    # 'mapa_colunas_nicho: Dict[str, str]' recebe o dicionário de equivalência de campos
    # do cliente específico.
    def __init__(self, mapa_colunas_nicho: dict[str, str]) -> None:
        """Inicializa o adaptador configurando o de-para de campos do nicho atendido.

        Args:
            mapa_colunas_nicho (Dict[str, str]): Dicionário mapeando
            {coluna_original_erp: coluna_padrao_bi}.
        """
        # Armazena o mapa semântico específico daquele nicho no atributo do objeto.
        self.mapa_colunas = mapa_colunas_nicho

        # Instancia o leitor seguro do núcleo compartilhado por Composição de Objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método que carrega a tabela bruta do nicho e entrega a matriz
    # padronizada para o Data Mart.
    # 'caminho_arquivo: Path' exige o caminho do arquivo CSV original da empresa.
    # '-> pd.DataFrame' documenta formalmente o retorno da tabela com o vocabulário
    # unificado.
    def padronizar_tabela_transacional(self, caminho_arquivo: Path) -> pd.DataFrame:
        """Lê o arquivo do ERP do cliente, aplica a tradução semântica de colunas e
        valida campos mandatórios.

        Args:
            caminho_arquivo (Path): Endereço físico do arquivo delimitado bruto.

        Returns:
            pd.DataFrame: Tabela normalizada com cabeçalhos canônicos universais prontos
            para BI.
        """
        # Carrega a matriz do cliente para a memória utilizando a ferramenta protegida
        # do núcleo.
        df_bruto = self.leitor.carregar_tabela(caminho_arquivo)

        # '.copy()' isola uma cópia em memória RAM para não violar a imutabilidade dos
        # dados brutos.
        df_padronizado = df_bruto.copy()

        # '.rename(columns=self.mapa_colunas)' traduz automaticamente as colunas do
        # nicho para os nomes padrão.
        # Exemplo: 'id_paciente' vira 'codigo_cliente' | 'valor_diaria' vira
        # 'valor_faturado_reais'.
        df_padronizado = df_padronizado.rename(columns=self.mapa_colunas)

        # 'return' devolve a matriz com a taxonomia universal de negócios pronta para os
        # cálculos dos Data Marts.
        return df_padronizado


# Bloco demonstrativo de uso prático para dois nichos totalmente distintos
if __name__ == "__main__":
    # CENÁRIO A: Configuração para uma Clínica Médica / Hospital Privado
    mapa_clinica_saude = {
        "id_atendimento": "codigo_pedido",
        "id_paciente": "codigo_cliente",
        "nome_paciente": "razao_social_cliente",
        "data_consulta": "data_transacao",
        "valor_honorario": "valor_faturado_reais",
        "convenio_plano": "segmento_mercado",
    }

    # CENÁRIO B: Configuração para uma Empresa de Software por Assinatura (SaaS)
    mapa_empresa_saas = {
        "id_fatura_stripe": "codigo_pedido",
        "id_organizacao": "codigo_cliente",
        "razao_social": "razao_social_cliente",
        "data_cobranca": "data_transacao",
        "valor_mensalidade_mrr": "valor_faturado_reais",
        "plano_contratado": "segmento_mercado",
    }

    # Ambos os nichos, ao passarem pelo AdaptadorUniversalBI, geram a EXATA mesma tabela
    # final
    # com: codigo_pedido, codigo_cliente, razao_social_cliente, data_transacao,
    # valor_faturado_reais.
    # Resultado: os mesmos gráficos do Metabase funcionam para a clínica e para o
    # software sem alterar código!
