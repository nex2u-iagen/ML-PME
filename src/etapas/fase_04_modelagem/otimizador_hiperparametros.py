"""Módulo de Otimização e Calibração Fina Universal de Hiperparâmetros.

Este componente implementa o Princípio da Responsabilidade Única (SRP) e Inversão de
Dependência (DIP).
Ele recebe qualquer estimador compatível com o Scikit-Learn ou com o contrato
'ModeloBase',
executando busca em grade exaustiva (GridSearchCV) sob qualquer métrica e estratégia de
partição.
"""

# 'from typing import ...' importa os tipos estáticos para documentar entradas e saídas
# do código.
# 'import logging' importa o módulo padrão do Python para emissão de mensagens de
# auditoria técnica.
import logging
from typing import Any

# 'import numpy as np' importa a biblioteca matricial para manipulação e validação dos
# conjuntos numéricos.
import numpy as np

# 'from sklearn.model_selection import ...' importa os validadores cruzados e o motor de
# busca em grade.
from sklearn.model_selection import (
    BaseCrossValidator,
    GridSearchCV,
    KFold,
    StratifiedKFold,
)

# 'from src...' importa a interface base abstrata para assegurar o cumprimento
# polimórfico da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class OtimizadorHiperparametros' declara o motor universal de ajuste fino de
# parâmetros.
class OtimizadorHiperparametros:
    """Motor de calibração agnóstico capaz de ajustar modelos de classificação ou
    regressão.
    """

    # 'def __init__(...)' é o método construtor responsável por parametrizar as regras
    # da busca.
    def __init__(
        self,
        metrica_alvo: str = "f1",
        estrategia_validacao: int | BaseCrossValidator | None = None,
        tipo_tarefa: str = "classificacao",
        semente_aleatoria: int = 42,
    ) -> None:
        """Inicializa as configurações de métrica, tarefa e partição da validação
        cruzada.

        Args:
            metrica_alvo (str): Nome da métrica oficial do Scikit-Learn (ex: 'f1', 'r2',
            'roc_auc').
            estrategia_validacao (Union[int, BaseCrossValidator], opcional): Divisor de
            dobras customizado.
            tipo_tarefa (str): 'classificacao' ou 'regressao'. Define o divisor padrão
            se for None.
            semente_aleatoria (int): Semente para controlar a reprodutibilidade dos
            sorteios de dobras.
        """
        # Atribui a métrica-alvo informada à propriedade interna da instância.
        self.metrica_alvo = metrica_alvo

        # Converte a descrição da tarefa para letras minúsculas para evitar erros de
        # digitação.
        self.tipo_tarefa = tipo_tarefa.lower()

        # Armazena a semente de aleatoriedade para garantir execuções idênticas no
        # futuro.
        self.semente_aleatoria = semente_aleatoria

        # Verifica se o usuário informou um divisor de dobras customizado
        # explicitamente.
        if estrategia_validacao is not None:
            # Atribui o divisor customizado informado pelo usuário diretamente à
            # propriedade interna.
            self.estrategia_validacao = estrategia_validacao
        # Caso não tenha sido informado e a tarefa seja do tipo classificação.
        elif self.tipo_tarefa == "classificacao":
            # Instancia o StratifiedKFold para manter a proporção exata de classes em
            # cada dobra.
            self.estrategia_validacao = StratifiedKFold(
                n_splits=5, shuffle=True, random_state=self.semente_aleatoria
            )
        # Caso contrário, trata-se de uma tarefa de regressão contínua.
        else:
            # Instancia o KFold clássico, já que dados numéricos contínuos não aceitam
            # estratificação.
            self.estrategia_validacao = KFold(
                n_splits=5, shuffle=True, random_state=self.semente_aleatoria
            )

    # 'def calibrar_especialista(...)' executa o procedimento prático de busca em grade
    # exaustiva.
    def calibrar_especialista(
        self,
        modelo_ou_especialista: ModeloBase | Any,
        matriz_atributos_treino: np.ndarray,
        vetor_alvo_treino: np.ndarray,
        grade_parametros_customizada: dict[str, list] | None = None,
    ) -> tuple[Any, dict[str, Any], float]:
        """Executa o GridSearchCV sobre os dados e devolve o modelo campeão reajustado.

        Args:
            modelo_ou_especialista (Union[ModeloBase, Any]): Instância de ModeloBase ou
            Estimador cru.
            matriz_atributos_treino (np.ndarray): Matriz X contendo os dados de entrada
            de treinamento.
            vetor_alvo_treino (np.ndarray): Vetor y contendo o gabarito ou valores
            contínuos esperados.
            grade_parametros_customizada (Dict[str, list], opcional): Dicionário externo
            de parâmetros.

        Returns:
            Tuple[Any, Dict[str, Any], float]: (Melhor Estimador, Melhores Parâmetros,
            Melhor Score).
        """
        # Emite uma mensagem de log informando o início do ajuste e a métrica de
        # otimização escolhida.
        logging.info(
            "Iniciando calibração genérica sob a métrica: '%s'...", self.metrica_alvo
        )

        # Verifica se o objeto fornecido é um especialista derivado formalmente de
        # ModeloBase.
        if isinstance(modelo_ou_especialista, ModeloBase):
            # Invoca o método da fábrica para construir o estimador cru com a semente
            # configurada.
            estimador_base = modelo_ou_especialista.construir_estimador(
                semente_aleatoria=self.semente_aleatoria
            )
            # Utiliza a grade customizada caso informada; caso contrário, extrai do
            # próprio especialista.
            grade_a_usar = (
                grade_parametros_customizada
                or modelo_ou_especialista.obter_grade_hiperparametros()
            )
        # Se for um estimador puro do Scikit-Learn ou uma Pipeline já montada.
        else:
            # Atribui o estimador diretamente sem passar pelo método de fábrica.
            estimador_base = modelo_ou_especialista
            # Verifica se a grade foi esquecida, pois estimadores crus não possuem o
            # método da fábrica.
            if grade_parametros_customizada is None:
                # Lança uma exceção informativa exigindo a passagem explícita do
                # dicionário de parâmetros.
                raise ValueError(
                    "Para estimadores que não herdam de ModeloBase, forneça a grade"
                    "explicitamente!"
                )
            # Atribui a grade customizada informada pelo usuário.
            grade_a_usar = grade_parametros_customizada

        # Registra no log o catálogo exato de parâmetros e intervalos que serão testados
        # exaustivamente.
        logging.info("Grade de parâmetros submetida à exploração: %s", grade_a_usar)

        # Instancia a máquina de busca exaustiva combinatória do Scikit-Learn.
        busca_grade = GridSearchCV(
            estimator=estimador_base,
            param_grid=grade_a_usar,
            scoring=self.metrica_alvo,
            cv=self.estrategia_validacao,
            n_jobs=-1,
            refit=True,
            verbose=1,
        )

        # Dispara o treinamento combinatório em todas as dobras e reajusta o melhor
        # modelo ao final.
        busca_grade.fit(matriz_atributos_treino, vetor_alvo_treino)

        # Registra a mensagem de sucesso da convergência no terminal.
        logging.info("Calibração finalizada com êxito!")
        # Exibe a combinação exata de hiperparâmetros que obteve a maior pontuação
        # média.
        logging.info("Configuração ótima identificada: %s", busca_grade.best_params_)
        # Exibe a pontuação numérica alcançada pela melhor configuração na métrica de
        # avaliação.
        logging.info(
            "Desempenho médio alcançado (%s): %.4f",
            self.metrica_alvo,
            busca_grade.best_score_,
        )

        # Retorna a tupla contendo o estimador pronto, o dicionário dos parâmetros e a
        # nota obtida.
        return (
            busca_grade.best_estimator_,
            busca_grade.best_params_,
            float(busca_grade.best_score_),
        )
