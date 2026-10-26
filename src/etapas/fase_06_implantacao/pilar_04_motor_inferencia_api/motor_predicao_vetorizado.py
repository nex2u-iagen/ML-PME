"""Módulo Especialista em Inferência Vetorizada e Aplicação de Limiar (Pilar 4 - Fase
6).

Responsabilidade Única: Extrair os atributos numéricos validados pelo Pydantic,
organizá-los em matrizes bidimensionais contíguas de memória C (NumPy float64),
executar a predição probabilística, medir a latência computacional em milissegundos
e aplicar a regra de corte do limiar homologado na Fase 5[cite: 7, 8].
"""

# 'from typing import ...' importa os tipos formais para documentação estrita de retorno
# de tuplas[cite: 7].
# 'import time' traz o módulo nativo para cronometragem de alta precisão em
# nanossegundos[cite: 7].
import time
from typing import Any

# 'import numpy as np' importa a biblioteca fundamental de computação matricial
# vetorizada em linguagem C[cite: 7].
import numpy as np

# Importa o contrato formal de dados do paciente construído e validado no Pilar 3[cite:
# 7, 8].
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_paciente import (  # noqa: E501
    EsquemaEntradaPaciente,
)


# 'class MotorPredicaoVetorizado' isola as rotinas matemáticas de inferência de alta
# velocidade[cite: 7].
class MotorPredicaoVetorizado:
    """Motor de cálculo que transforma contratos clínicos em decisões probabilísticas
    rápidas[cite: 7, 8].
    """

    # 'def __init__(...)' constrói a instância do motor registrando o limiar de decisão
    # oficial.
    # 'limiar_corte: float = 0.50': o ponto de corte homologado no comitê de risco da
    # Fase 5 (Padrão: 0.50)[cite: 7].
    def __init__(self, limiar_corte: float = 0.50) -> None:
        """Inicializa o motor de inferência com a política de sensibilidade
        homologada[cite: 7].

        Args:
            limiar_corte (float): Ponto de corte ótimo de probabilidade para mitigar
            negligência clínica[cite: 7, 8].
        """
        # 'self.limiar_corte' armazena o ponto de corte decimal como atributo imutável
        # de decisão[cite: 7].
        self.limiar_corte = float(limiar_corte)

    # 'def executar_predicao_rapida(...)' executa a vetorização e a inferência
    # computacional pura[cite: 7].
    # 'paciente: EsquemaEntradaPaciente': objeto validado pelo Pydantic com as 10
    # variáveis clínicas[cite: 7, 8].
    # 'pipeline_modelo: Any': o objeto Pipeline treinado e ativo na memória RAM do
    # servidor[cite: 7].
    # '-> Tuple[int, float, float]': garante que devolve uma tupla com (Classe,
    # Probabilidade, Latência ms)[cite: 7].
    def executar_predicao_rapida(
        self,
        paciente: EsquemaEntradaPaciente,
        pipeline_modelo: Any,
    ) -> tuple[int, float, float]:
        """Vetoriza os dados clínicos, calcula a probabilidade e afere o tempo de
        resposta[cite: 7, 8].

        Args:
            paciente (EsquemaEntradaPaciente): Objeto Pydantic auditado com as 10
            features clínicas[cite: 7, 8].
            pipeline_modelo (Any): Pipeline completo (StandardScaler + SVM Calibrado)
            carregado na RAM[cite: 7].

        Returns:
            Tuple[int, float, float]: Tupla contendo a classe binária, o escore de risco
            e a latência em ms[cite: 7].
        """
        # 'time.perf_counter()' aciona o registrador de tempo de maior resolução do
        # hardware do computador[cite: 7].
        # Marca a estampa de tempo inicial imediatamente antes de qualquer cálculo
        # matemático ser realizado[cite: 7].
        tempo_inicio = time.perf_counter()

        # 'paciente.exportar_vetor_ordenado()' aciona o método do contrato do Pilar
        # 3[cite: 7].
        # Extrai os 10 valores na ordem canônica em que o StandardScaler foi treinado na
        # Fase 5[cite: 3, 7].
        vetor_ordenado = paciente.exportar_vetor_ordenado()

        # 'np.ascontiguousarray(...)' aloca os dados em um bloco contínuo de memória em
        # padrão C[cite: 7].
        # '[vetor_ordenado]' envolve a lista de 10 elementos em colchetes para criar uma
        # matriz bidimensional (shape 1, 10)[cite: 7].
        # 'dtype=np.float64' força a representação em números de ponto flutuante de 64
        # bits de dupla precisão[cite: 7].
        matriz_c_contigua = np.ascontiguousarray([vetor_ordenado], dtype=np.float64)

        # 'pipeline_modelo.predict_proba(...)' alimenta a matriz na entrada do Pipeline
        # de produção[cite: 7].
        # 1. O 'StandardScaler' padroniza os 10 números usando a média e desvio padrão
        # salvos no artefato[cite: 7].
        # 2. O 'AlgoritmoSVM' projeta os dados escalados nos vetores de suporte e aplica
        # a calibração sigmoide[cite: 5, 7].
        # '[0, 1]' extrai a primeira amostra da matriz (linha 0) e a segunda coluna de
        # probabilidade (classe 1 = risco)[cite: 7].
        # 'float(...)' converte o resultado NumPy em tipo nativo float do Python para
        # serialização JSON[cite: 7].
        probabilidade_risco = float(
            pipeline_modelo.predict_proba(matriz_c_contigua)[0, 1]
        )

        # 'time.perf_counter() - tempo_inicio' calcula o intervalo de tempo decorrido em
        # frações de segundo[cite: 7].
        # Multiplica por 1000.0 para converter a grandeza para milissegundos (ms)[cite:
        # 7].
        latencia_ms = (time.perf_counter() - tempo_inicio) * 1000.0

        # Aplica o limiar ótimo homologado no dossiê de governança da Fase 5[cite: 7]:
        # - Se a probabilidade calculada for maior ou igual ao limiar de corte, a classe
        # decidida é 1 (Risco Crítico)[cite: 7].
        # - Caso contrário, o paciente é rotulado como classe 0 (Sem Risco Imediato
        # Comprovado)[cite: 7].
        classe_final = 1 if probabilidade_risco >= self.limiar_corte else 0

        # 'return' devolve a tupla estrita de três elementos pronta para ser consumida
        # pela API web[cite: 7].
        return classe_final, probabilidade_risco, latencia_ms
