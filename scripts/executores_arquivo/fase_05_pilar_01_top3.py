"""Script Executável de Homologação do Pilar 1 (Auditoria Comparativa do Top 3).

Lê os **artefatos reais** produzidos pela Fase 4 (catálogo do pódio + partição de
teste retido) e reexecuta a auditoria comparativa sobre eles, eliminando o
pódio hardcoded (SVM/XGBoost/KNN) e a base sintética clínica do fluxo padrão.

O modo sintético permanece disponível apenas como ``--modo demo``, explicitamente
sinalizado, para Demonstrações sem base carregada.

Exemplos de uso:

    uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3 \\
        --dataset mercado_vencedor --problema previsao_faturamento
    uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3 --modo demo
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'import joblib' desserializa o catálogo de finalistas persistido pela Fase 4.
import joblib

# 'import pandas' lê a partição de teste retido produzida pela Fase 3.
import pandas as pd

# 'import numpy' manipula as matrizes numéricas entregues ao avaliador.
import numpy as np

# Importa a fachada integradora do Pilar 1 da pasta oficial 'fase_05_avaliacao'.
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.orquestrador_podio_top3 import (
    OrquestradorPodioTop3,
)

# Importa o bootstrap parametrizado (G5).
from scripts.bootstrap import (
    RAIZ_PROJETO,
    argumentos_comuns,
    configurar_ambiente,
    resolver_contrato,
    resolver_pastas_dataset,
)

# Importa o gerenciador de datasets para persistir o status da fase no registro.
from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

# Configura o layout das mensagens de log no console corporativo.
configurar_ambiente()


def _marcar_fase_05_concluida(nome_dataset: str) -> None:
    """Persiste no registro do dataset que a Fase 05 foi concluída.

    Falhas de persistência são registradas como aviso e não interrompem o fluxo.

    Args:
        nome_dataset (str): Nome do dataset avaliado.
    """
    try:
        gerenciador = GerenciadorDatasets(diretorio_raiz=RAIZ_PROJETO)
        registro = gerenciador.obter_ou_criar(nome_dataset)
        registro.marcar_fase("05", "concluida")
        gerenciador.salvar(registro)
    except Exception as erro_registro:
        logging.warning("Não foi possível persistir o status da Fase 05: %s", erro_registro)


def _scorecard_regressao(catalogo_top3, matriz_teste, vetor_alvo) -> "pd.DataFrame":
    """Monta o placar comparativo dos regressores sobre a partição de teste retido.

    Args:
        catalogo_top3 (dict): Dicionário nome -> estimador ajustado.
        matriz_teste (pd.DataFrame): Atributos do teste cego (com os nomes das colunas).
        vetor_alvo (np.ndarray): Vetor alvo real do teste cego.

    Returns:
        pd.DataFrame: Placar ordenado por R² decrescente.
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    linhas = []
    for nome, modelo in catalogo_top3.items():
        predicoes = modelo.predict(matriz_teste)
        linhas.append({
            "Modelo": nome,
            "R2_Score": round(float(r2_score(vetor_alvo, predicoes)), 4),
            "RMSE": round(float(np.sqrt(mean_squared_error(vetor_alvo, predicoes))), 4),
            "MAE": round(float(mean_absolute_error(vetor_alvo, predicoes)), 4),
        })

    return pd.DataFrame(linhas).sort_values(by="R2_Score", ascending=False).reset_index(drop=True)


def _scorecard_agrupamento(catalogo_top3, matriz_teste) -> "pd.DataFrame":
    """Monta o placar comparativo dos modelos de agrupamento.

    Args:
        catalogo_top3 (dict): Dicionário nome -> estimador ajustado.
        matriz_teste (pd.DataFrame): Atributos avaliados.

    Returns:
        pd.DataFrame: Placar ordenado por silhueta decrescente.
    """
    from sklearn.metrics import silhouette_score

    linhas = []
    for nome, modelo in catalogo_top3.items():
        rotulos = modelo.predict(matriz_teste)
        try:
            silhueta = round(float(silhouette_score(matriz_teste, rotulos)), 4)
        except ValueError:
            silhueta = -1.0
        linhas.append({
            "Modelo": nome,
            "Silhueta": silhueta,
            "Numero_Grupos": int(modelo.n_clusters),
        })

    return pd.DataFrame(linhas).sort_values(by="Silhueta", ascending=False).reset_index(drop=True)


def _figura_regressao(placar, catalogo_top3, matriz_teste, vetor_alvo, pasta_destino: Path) -> str:
    """Gera a figura comparativa do pódio de regressão (R² e previsto × real).

    Args:
        placar (pd.DataFrame): Placar de métricas já calculado.
        catalogo_top3 (dict): Dicionário nome -> estimador ajustado.
        matriz_teste (np.ndarray): Matriz de atributos do teste cego.
        vetor_alvo (np.ndarray): Vetor alvo real do teste cego.
        pasta_destino (Path): Pasta onde a figura será gravada.

    Returns:
        str: Caminho absoluto da figura gerada.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pasta_destino.mkdir(parents=True, exist_ok=True)
    caminho = pasta_destino / "comparativo_top3_regressao.png"

    figura, eixos = plt.subplots(1, 2, figsize=(14, 5.5))

    eixos[0].bar(placar["Modelo"], placar["R2_Score"], color="#2E86AB")
    eixos[0].set_title("R² no teste retido")
    eixos[0].set_ylabel("R²")
    eixos[0].tick_params(axis="x", rotation=20)
    eixos[0].grid(axis="y", alpha=0.3)

    for nome, modelo in catalogo_top3.items():
        predicoes = modelo.predict(matriz_teste)
        eixos[1].scatter(vetor_alvo, predicoes, alpha=0.55, label=nome, s=18)

    eixos[1].set_xlabel("Valor real")
    eixos[1].set_ylabel("Valor previsto")
    eixos[1].set_title("Previsto × Real")
    eixos[1].legend(fontsize=8)
    eixos[1].grid(alpha=0.3)

    figura.tight_layout()
    figura.savefig(caminho, dpi=300)
    plt.close(figura)

    return str(caminho)


def _executar_modo_demo() -> None:
    """Executa a auditoria sintética de demonstração (base clínica simulada)."""
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_knn_classificador import (
        AlgoritmoKNN,
    )
    from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (
        AlgoritmoSVM,
    )
    from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_xgboost_classificador import (
        AlgoritmoXGBoost,
    )

    from scripts.bootstrap import RAIZ_PROJETO

    logging.info("=== MODO DEMO: auditoria sobre base sintética de demonstração ===")

    x_bruto, y_alvo = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x_bruto, y_alvo, test_size=0.20, stratify=y_alvo, random_state=42
    )

    escalador = StandardScaler()
    x_treino_escalado = escalador.fit_transform(x_treino)
    x_teste_escalado = escalador.transform(x_teste)

    modelo_svm = AlgoritmoSVM().construir_estimador(semente_aleatoria=42)
    modelo_svm.fit(x_treino_escalado, y_treino)
    modelo_xgb = AlgoritmoXGBoost().construir_estimador(semente_aleatoria=42)
    modelo_xgb.fit(x_treino_escalado, y_treino)
    modelo_knn = AlgoritmoKNN().construir_estimador(semente_aleatoria=42)
    modelo_knn.fit(x_treino_escalado, y_treino)

    catalogo_top3 = {
        "SVM_Calibrado": modelo_svm,
        "XGBoost_Classifier": modelo_xgb,
        "KNN_Classifier": modelo_knn,
    }

    pasta_destino = RAIZ_PROJETO / "relatorios" / "figuras" / "fase_05_avaliacao" / "pilar_01_top3"
    orquestrador = OrquestradorPodioTop3(pasta_relatorios=pasta_destino)
    laudo = orquestrador.executar_auditoria_completa(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=x_teste_escalado,
        vetor_alvo_teste=y_teste,
        rotulos_classes=["Saudavel", "Risco"],
    )

    print("\n" + "=" * 105)
    print("🏆 SCORECARD TÉCNICO COMPARATIVO DO PÓDIO (MODO DEMO — TESTE RETIDO)")
    print("=" * 105)
    print(laudo["scorecard_tabular"].to_string(index=False))
    print("=" * 105)


def main() -> None:
    """Executa a auditoria do pódio Top 3 sobre os artefatos reais da Fase 4."""
    parser = argumentos_comuns("Fase 5 — Pilar 1: auditoria comparativa do pódio Top 3")
    argumentos = parser.parse_args()

    logging.info("=== INICIANDO SCRIPT DE HOMOLOGAÇÃO: PILAR 1 (AVALIAÇÃO TOP 3) ===\n")

    if argumentos.modo == "demo":
        _executar_modo_demo()
        return

    # 1. RESOLUÇÃO dos artefatos reais da Fase 4 e do contrato vigente.
    pastas = resolver_pastas_dataset(argumentos.dataset)
    nome_dataset = pastas["nome"]
    pasta_modelos = pastas["modelos"]
    pasta_ml = pastas["ml"]

    contrato = resolver_contrato(nome_dataset, argumentos.problema)
    caminho_top3 = pasta_modelos / "catalogo_top3_modelos.joblib"
    caminho_teste = pasta_ml / "teste_processado.parquet"

    if not caminho_top3.is_file() or not caminho_teste.is_file():
        logging.error(
            "Artefatos da Fase 4 não localizados para o dataset '%s'. "
            "Execute a Fase 4 antes da auditoria do pódio.",
            nome_dataset,
        )
        raise SystemExit(1)

    catalogo_top3 = joblib.load(caminho_top3)
    df_teste = pd.read_parquet(caminho_teste)

    coluna_alvo = "alvo_contratado"
    tipo_tarefa = contrato.tipo_tarefa.value if contrato is not None else "classificacao"
    supervisionado = contrato is not None and contrato.exige_alvo

    if supervisionado:
        if coluna_alvo not in df_teste.columns:
            logging.error("Coluna alvo '%s' ausente na partição de teste.", coluna_alvo)
            raise SystemExit(1)
        atributos_teste = df_teste.drop(columns=[coluna_alvo])
        matriz_teste = atributos_teste.to_numpy(dtype=float)
        vetor_alvo = df_teste[coluna_alvo].to_numpy()
    else:
        atributos_teste = df_teste
        matriz_teste = df_teste.to_numpy(dtype=float)
        vetor_alvo = None

    logging.info(
        "Pódio real carregado — %d finalistas | %d amostras de teste retido | Tarefa: %s",
        len(catalogo_top3),
        len(df_teste),
        tipo_tarefa,
    )

    pasta_figuras = pastas["relatorios"] / "fase_05_avaliacao" / "pilar_01_top3"

    # 2. AUDITORIA conforme a família de tarefa do contrato.
    if tipo_tarefa == "classificacao":
        orquestrador = OrquestradorPodioTop3(pasta_relatorios=pasta_figuras)
        laudo = orquestrador.executar_auditoria_completa(
            catalogo_top3=catalogo_top3,
            matriz_atributos_teste=matriz_teste,
            vetor_alvo_teste=vetor_alvo,
            rotulos_classes=["Sem evento", "Evento"],
        )
        print("\n" + "=" * 105)
        print("🏆 SCORECARD TÉCNICO COMPARATIVO DO PÓDIO (TESTE RETIDO REAL)")
        print("=" * 105)
        print(laudo["scorecard_tabular"].to_string(index=False))
        print("=" * 105)
        print(f"\n📁 Figuras: {pasta_figuras.resolve()}")
        _marcar_fase_05_concluida(nome_dataset)
        return

    if tipo_tarefa == "regressao":
        placar = _scorecard_regressao(catalogo_top3, atributos_teste, vetor_alvo)
        figura = _figura_regressao(placar, catalogo_top3, matriz_teste, vetor_alvo, pasta_figuras)
    else:
        placar = _scorecard_agrupamento(catalogo_top3, atributos_teste)
        figura = ""

    print("\n" + "=" * 105)
    print(f"🏆 SCORECARD TÉCNICO COMPARATIVO DO PÓDIO — {nome_dataset.upper()}")
    print("=" * 105)
    print(placar.to_string(index=False))
    print("=" * 105)
    if figura:
        print(f"\n📁 Figura comparativa: {figura}")

    # 3. PERSISTÊNCIA do scorecard para consumo pelo frontend e pela camada de serviço.
    caminho_scorecard = pasta_modelos / "scorecard_top3.csv"
    placar.to_csv(caminho_scorecard, index=False)
    logging.info("Scorecard do pódio persistido em: %s", caminho_scorecard)

    # 4. REGISTRO do status conclusivo da Fase 05 no dataset.
    _marcar_fase_05_concluida(nome_dataset)


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    main()
