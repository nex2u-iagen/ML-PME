# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e caminhos de arquivos de forma orientada a objetos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com Windows, Linux e Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para suporte a anotações de tipagem estática.
# 'import' carrega 'Any' e 'Dict' para documentar estruturas de retorno.
from typing import Any, Dict

# 'from' acessa o módulo 'abc' da biblioteca padrão para viabilizar herança abstrata formal na linguagem Python.
# 'import' traz 'ABC' (classe base abstrata) e 'abstractmethod' (decorador de métodos obrigatórios).
from abc import ABC, abstractmethod

# 'import' traz o módulo 'logging' nativo para registrar mensagens operacionais com carimbo de auditoria no terminal.
import logging

# Importação da ferramenta de leitura tolerante a variações estruturais de CSV do núcleo compartilhado.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# Importação da calculadora estatística para testes de hipóteses e medidas descritivas do núcleo.
from src.nucleo.diagnostico_estatistico.testes_hipoteses import CalculadoraEstatistica

# Importação do gerador gráfico padronizado para estilização corporativa uniforme em alta resolução (300 DPI).
from src.nucleo.diagnostico_estatistico.visualizacao_grafica import GeradorVisualizacaoGrafica

# Importação do adaptador universal de ERPs para casamento semântico e recorte temporal de dados reais.
from src.etapas.fase_02_exploracao.adaptador_universal_erp import AdaptadorUniversalERP

# 'logging.basicConfig' parametriza a formatação dos registros no console corporativo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class BaseDepartamento(ABC)' declara a classe base abstrata que injeta infraestrutura em todos os setores.
class BaseDepartamento(ABC):
    """Classe base abstrata com governança de pastas estruturadas por cliente e fase analítica."""

    # 'def __init__(...)' é o construtor responsável por registrar diretórios e instanciar as ferramentas.
    def __init__(
        self,
        pasta_dados_brutos: Path,
        pasta_relatorios: Path,
        nome_departamento: str,
        fase_projeto: str = "fase_02",
    ) -> None:
        """Inicializa o departamento com a nova hierarquia relatorios/<nome_banco>/<fase>/<departamento>/."""
        self.pasta_dados_brutos = pasta_dados_brutos
        self.nome_departamento = nome_departamento
        self.fase_projeto = fase_projeto

        # Instancia o adaptador universal sobre o diretório de dados para descobrir o nome real do banco/cliente.
        self.adaptador = AdaptadorUniversalERP(pasta_dados_erp=self.pasta_dados_brutos)
        self.nome_banco = self.adaptador.nome_banco

        # HIERARQUIA DE DIRETÓRIOS POR CLIENTE E FASE:
        # relatorios/<nome_banco>/<fase_projeto>/<nome_departamento>/
        self.pasta_saida = pasta_relatorios / self.nome_banco / self.fase_projeto / self.nome_departamento
        self.pasta_saida.mkdir(parents=True, exist_ok=True)

        # Injeta as ferramentas do núcleo compartilhado.
        self.leitor = LeitorArquivosTabulares()
        self.calculadora = CalculadoraEstatistica()
        self.visualizador = GeradorVisualizacaoGrafica()

        logging.info(
            "Departamento '%s' pronto. Cliente: '%s' | Fase: '%s' | Destino: %s",
            self.nome_departamento,
            self.nome_banco,
            self.fase_projeto,
            self.pasta_saida,
        )

    # '@abstractmethod' força a implementação executiva concreta nas classes especialistas filhas.
    @abstractmethod
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena a execução de cálculos tabulares e geração de gráficos analíticos do departamento."""
        ...