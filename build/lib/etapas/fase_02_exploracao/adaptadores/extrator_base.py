# 'from' indica a biblioteca de origem; 'abc' gerencia contratos abstratos no Python.
# 'import' traz 'ABC' (classe base abstrata) e 'abstractmethod' (forçador de implementação).
from abc import ABC, abstractmethod

# 'from' acessa a biblioteca padrão 'pathlib' para navegação orientada a objetos no disco.
# 'import' traz a classe 'Path' para manipulação uniforme de diretórios.
from pathlib import Path

# 'import' traz a biblioteca 'pandas' para tipagem de DataFrames nas assinaturas abstratas[cite: 10].
import pandas as pd

# Importação da ferramenta de leitura tolerante a variações estruturais de CSV do núcleo[cite: 4].
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# Importação do resolvedor léxico construído no passo anterior.
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico


# 'class ExtratorBase(ABC)' define o contrato arquitetural abstrato para todos os extratores de domínio.
class ExtratorBase(ABC):
    """Contrato base abstrato que injeta o resolvedor semântico e o leitor de arquivos nos especialistas."""

    # 'def __init__(...)' instancia a fundação do extrator vinculando a pasta física dos dados.
    def __init__(self, pasta_dados: Path, resolvedor: ResolvedorSemantico) -> None:
        """Inicializa o extrator de domínio com o repositório de arquivos e o tradutor de esquemas."""
        # Armazena a pasta de dados do banco de dados inspecionado.
        self.pasta_dados = pasta_dados
        # Injeta a instância única compartilhada do resolvedor léxico[cite: 8].
        self.resolvedor = resolvedor
        # Injeta o leitor seguro e defensivo de tabelas[cite: 4].
        self.leitor = LeitorArquivosTabulares()

    # '@abstractmethod' obriga toda classe especialista filha a implementar o método de extração canônica.
    @abstractmethod
    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Executa a extração, filtros de período e consolidação da visão canônica de negócio."""
        ...