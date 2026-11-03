"""Módulo de Configuração de Amostragem e Metadados para XAI (Pilar 3).

Responsabilidade Única: Encapsular parâmetros de amostragem de fundo (background),
nomes de colunas e controle de reprodutibilidade estocástica para o cálculo SHAP[cite:
18, 20].
"""

# 'from typing import ...' importa os tipos estáticos formais para documentação de
# contratos[cite: 18].
from typing import Any


# 'class ConfiguracaoShap' atua como Objeto de Configuração para o framework de
# explicabilidade[cite: 20].
class ConfiguracaoShap:
    """Encapsula metadados e parâmetros da base de referência para Valores de
    Shapley[cite: 20].
    """

    # 'def __init__(...)' instancia a configuração com validação defensiva de
    # parâmetros[cite: 20].
    def __init__(
        self,
        nomes_atributos: list[str],
        quantidade_amostras_fundo: int = 30,
        semente_aleatoria: int = 42,
    ) -> None:
        """Inicializa os parâmetros operacionais da explicabilidade agnóstica[cite: 20].

        Args:
            nomes_atributos (List[str]): Rótulos inteligíveis de cada coluna
            preditora[cite: 18, 20].
            quantidade_amostras_fundo (int): Tamanho da amostra basal para integração de
            fundo[cite: 20].
            semente_aleatoria (int): Semente para sorteio determinístico das
            observações[cite: 20].
        """
        # Checagem defensiva: a lista de atributos não pode estar vazia.
        if not nomes_atributos or len(nomes_atributos) == 0:
            raise ValueError("A lista de nomes de atributos não pode ser vazia!")

        # Armazena os rótulos de colunas amigáveis de negócios[cite: 18, 20].
        self.nomes_atributos = nomes_atributos

        # Armazena o volume de observações de referência (baseline populacional)[cite:
        # 20].
        self.quantidade_fundo = max(10, int(quantidade_amostras_fundo))

        # Armazena a semente de controle estocástico[cite: 20].
        self.semente_aleatoria = int(semente_aleatoria)

    # 'def exportar_resumo(...)' devolve metadados operacionais para auditoria de
    # governança de dados.
    def exportar_resumo(self) -> dict[str, Any]:
        """Exporta os parâmetros de configuração da explicabilidade em formato de
        dicionário[cite: 20].
        """
        return {
            "total_atributos_mapeados": len(self.nomes_atributos),
            "amostras_fundo_baseline": self.quantidade_fundo,
            "semente_reprodutibilidade": self.semente_aleatoria,
        }
