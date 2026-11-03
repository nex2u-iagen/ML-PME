"""Módulo Orquestrador do Modelo Baseline Linear (Versão Adaptativa).

Atua como o controlador central, conectando os dados processados à Fábrica
de Modelos e acionando o Otimizador com Validação Cruzada Dinâmica para
prevenir falhas de volumetria em bases desbalanceadas[cite: 3].
"""

# 'import' carrega o módulo 'sys', permitindo acesso a variáveis e funções do sistema do
# interpretador Python.
# 'import' traz o módulo 'logging' para registrar auditorias operacionais visíveis no
# console.
import logging
import sys

# 'from' acessa a biblioteca nativa 'pathlib' para construir caminhos de arquivos imunes
# ao sistema operacional.
from pathlib import Path

# 'import' traz a biblioteca 'pandas', essencial para carregar as matrizes tabulares em
# memória.
import pandas as pd

# 'from' importa as funções matemáticas oficiais do scikit-learn para avaliar a
# performance do modelo.
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

# Importa a classe Especialista (Regressão Logística) da nossa arquitetura de Fábrica
# Orientada a Objetos.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_regressao_logistica import (  # noqa: E501
    AlgoritmoRegressaoLogistica,
)

# Importa a classe Otimizadora que orquestra o GridSearchCV e o Cross-Validation
# internamente[cite: 3].
from src.etapas.fase_04_modelagem.otimizador_hiperparametros import OtimizadorDeModelos

# Importa o módulo responsável por empacotar e persistir a inteligência artificial
# treinada no disco.
from src.nucleo.aprendizado_maquina.persistencia_artefatos import (
    GerenciadorPersistenciaModelos,
)

# Raiz do repositório calculada a partir da localização deste módulo.
raiz_projeto = Path(__file__).resolve().parents[4]

# 'logging.basicConfig' configura o formato visual (data, nível, mensagem) e o limite de
# captura dos logs.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — [%(levelname)s] — %(message)s"
)


# 'def' inicia a declaração da função orquestradora central que comandará todo o fluxo.
def executar_triagem_baseline() -> None:
    """Carrega dados, ajusta hiperparâmetros dinamicamente e avalia o baseline."""
    # 'logging.info' imprime os cabeçalhos para facilitar o rastreio visual durante a
    # execução.
    logging.info("=================================================================")
    logging.info("=== INICIANDO FASE 4.1: ORQUESTRADOR DO BASELINE LINEAR       ===")
    logging.info("=================================================================")

    # 1. MAPEAMENTO ESTRUTURAL DOS DIRETÓRIOS
    # Concatena a raiz do projeto com o caminho relativo onde os dados processados
    # residem.
    pasta_ml = raiz_projeto / "dados" / "processados" / "ml"

    # Concatena a raiz do projeto com a pasta de destino dos artefatos (modelos).
    pasta_modelos = raiz_projeto / "modelos"

    # 'mkdir' cria o diretório de destino fisicamente, ignorando caso já exista
    # (exist_ok=True).
    pasta_modelos.mkdir(parents=True, exist_ok=True)

    # 2. CARREGAMENTO ISOLADO DOS DADOS (PREVENÇÃO DE DATA LEAKAGE)
    # 'pd.read_parquet' carrega a partição de Treinamento, usada exclusivamente para
    # ensino.
    df_treino = pd.read_parquet(pasta_ml / "treino_processado.parquet")

    # 'pd.read_parquet' carrega a partição de Validação, usada para testar
    # generalização[cite: 3].
    df_val = pd.read_parquet(pasta_ml / "validacao_processada.parquet")

    # 'drop' isola a matriz de características (X) removendo a coluna que contém o
    # gabarito.
    x_treino = df_treino.drop(columns=["alvo_inadimplente"])

    # Isola o vetor alvo (y) extraindo unicamente a coluna gabarito.
    y_treino = df_treino["alvo_inadimplente"]

    # Replica a separação de X para o conjunto invisível de validação.
    x_val = df_val.drop(columns=["alvo_inadimplente"])

    # Replica a separação de y para o conjunto invisível de validação.
    y_val = df_val["alvo_inadimplente"]

    # Registra no log a volumetria exata carregada para análise.
    logging.info(
        "Dados carregados. Treino: %d amostras | Validação: %d amostras",
        len(x_treino),
        len(x_val),
    )

    # 3. DEFESA MATEMÁTICA CONTRA BASES DESBALANCEADAS (MOCK DATA)
    # 'value_counts().min()' identifica quantas amostras a classe mais rara possui no
    # treinamento.
    min_amostras_classe = y_treino.value_counts().min()

    # 'max(2, min(5, ...))' trava o número de dobras (folds). O máximo ideal é 5, mas
    # reduz até 2 se necessário[cite: 3].
    kfold_seguro = int(max(2, min(5, min_amostras_classe)))

    # 'if' verifica defensivamente se há volume estatístico mínimo para uma única
    # divisão.
    if min_amostras_classe < 2:
        # Registra erros críticos explicando a impossibilidade matemática.
        logging.error(
            "FALHA: A base de Treino possui apenas %d amostra(s) na classe minoritária.",  # noqa: E501
            min_amostras_classe,
        )
        logging.error(
            "A Validação Cruzada exige no mínimo 2 amostras de cada classe para"
            "funcionar[cite: 3]."
        )

        # Encerra o script (código 1) prevenindo a quebra abrupta do interpretador.
        sys.exit(1)

    # Confirma o cálculo matemático de segurança no terminal.
    logging.info(
        "Volumetria auditada. K-Fold ajustado dinamicamente para: %d dobras",
        kfold_seguro,
    )

    # 4. INSTANCIAÇÃO POLIMÓRFICA VIA FÁBRICA
    # Aciona a classe especialista, mantendo o Orquestrador ignorante sobre a matemática
    # interna.
    especialista = AlgoritmoRegressaoLogistica()

    # Puxa o objeto bruto (Estimator) contendo os parâmetros iniciais padrão[cite: 2].
    modelo_bruto = especialista.construir_estimador()

    # Puxa o dicionário contendo as combinações numéricas que devem ser testadas no
    # ajuste.
    grade_parametros = especialista.obter_grade_hiperparametros()

    # 5. CALIBRAÇÃO COMPUTACIONAL E AJUSTE MATEMÁTICO
    # Aciona o motor passando a volumetria segura e mirando o máximo F1-Score[cite: 3].
    otimizador = OtimizadorDeModelos(particoes_kfold=kfold_seguro, metrica_alvo="f1")

    # O motor cruza dados exaustivamente e devolve o objeto calibrado perfeitamente.
    modelo_calibrado = otimizador.otimizar_estimador(
        estimador_bruto=modelo_bruto,
        grade_parametros=grade_parametros,
        x_treino=x_treino,
        y_treino=y_treino,
    )

    # 6. AVALIAÇÃO OFICIAL NA PARTIÇÃO CEGA DE VALIDAÇÃO
    # '.predict()' compele a matemática a fornecer uma decisão final categórica (0 ou
    # 1).
    predicoes_classes = modelo_calibrado.predict(x_val)

    # '.predict_proba()' expõe a probabilidade contínua gerada pela função sigmoide
    # (somente a Classe 1).
    predicoes_probabilidades = modelo_calibrado.predict_proba(x_val)[:, 1]

    # 'accuracy_score' extrai a proporção bruta de acertos, perigosa em classes
    # desbalanceadas.
    acuracia = accuracy_score(y_val, predicoes_classes)

    # 'f1_score' tira a média harmônica penalizando a falsa percepção de acerto.
    f1 = f1_score(y_val, predicoes_classes, zero_division=0)

    # 'try' protege a tentativa de calcular o ROC-AUC em bases de simulação extremamente
    # pequenas.
    try:
        # 'roc_auc_score' afere a área sob a curva de sensibilidade (1.0 = perfeição).
        roc_auc = roc_auc_score(y_val, predicoes_probabilidades)
    except ValueError:
        # Caso a validação possua apenas 1 classe, zera a métrica e avisa o usuário
        # (Mock Protection).
        roc_auc = 0.0
        logging.warning(
            "ROC-AUC zerada preventivamente: a partição de validação possui apenas 1"
            "classe."
        )

    # 'confusion_matrix' gera o cruzamento estrito de Falsos Positivos e Verdadeiros
    # Negativos.
    matriz_conf = confusion_matrix(y_val, predicoes_classes)

    # Emite os sinais vitais definitivos do modelo na tela para tomada de decisão.
    logging.info("--- MÉTRICAS FINAIS NA VALIDAÇÃO ---")
    logging.info("Acurácia Geral : %.2f%%", acuracia * 100)
    logging.info("F1-Score       : %.4f", f1)
    logging.info("ROC-AUC        : %.4f", roc_auc)
    logging.info("Matriz de Confusão:\n%s", matriz_conf)

    # 7. EMPACOTAMENTO DA INTELIGÊNCIA E PERSISTÊNCIA FÍSICA
    # Cria o dicionário de governança exigido pelo núcleo, documentando performance e
    # colunas.
    metadados = {
        "algoritmo": "LogisticRegression (Calibrada)",
        "f1_score_validacao": round(f1, 4),
        "roc_auc_validacao": round(roc_auc, 4),
        "features_utilizadas": list(x_treino.columns),
    }

    # Delega a tarefa de serialização binária ao método centralizado da arquitetura.
    GerenciadorPersistenciaModelos.salvar_modelo_com_metadados(
        objeto_modelo=modelo_calibrado,
        caminho_artefato=pasta_modelos / "modelo_baseline_logreg_calibrado.joblib",
        metadados_governanca=metadados,
    )

    # Finaliza a execução emitindo o status de sucesso.
    logging.info("=== FASE 4.1 CONCLUÍDA COM SUCESSO ===")


# 'if __name__ == "__main__":' assegura que o script atue como orquestrador somente se
# chamado diretamente.
if __name__ == "__main__":
    executar_triagem_baseline()
