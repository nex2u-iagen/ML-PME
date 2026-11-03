"""Script Executor Oficial da Fase 04 do CRISP-DM: Modelagem (Treinamento e Pódio Top 3).

Responsabilidade Única: Ponto de entrada CLI que carrega as partições Parquet limpas
da Fase 3, dispara o comparador de modelos correspondente à **família de tarefa
declarada no contrato de problema**, imprime o placar do torneio e persiste o
modelo campeão, o leaderboard e o catálogo do Top 3 para a Fase 5.

Exemplos de uso:

    uv run python -m scripts.executores_arquivo.executar_fase_04_modelagem \\
        --dataset mercado_vencedor --problema previsao_faturamento --semente 42
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro estruturado no console[cite: 8].
import logging
import os

# 'import math' valida finitude das métricas (descarta NaN/inf do pódio).
import math

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'import' traz a biblioteca externa 'joblib' para persistência serializada do catálogo de estimadores.
import joblib

# 'import' traz a biblioteca externa 'pandas' para leitura dos Parquets particionados[cite: 8, 12].
import pandas as pd

# Importa os comparadores de modelos por família de tarefa[cite: 9, 10, 12].
from src.etapas.fase_04_modelagem.comparador_modelos import criar_comparador

# Importa o gerenciador de persistência do núcleo para gravação com manifesto de metadados[cite: 8, 12].
from src.nucleo.aprendizado_maquina.persistencia_artefatos import (
    GerenciadorPersistenciaModelos,
)

# Importa o bootstrap parametrizado (G5) para_unificar dataset, semente e problema.
from scripts.bootstrap import argumentos_comuns, configurar_ambiente, resolver_contrato, resolver_pastas_dataset

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Executa o torneio de modelos da Fase 4 conforme o contrato de problema vigente."""
    parser = argumentos_comuns("Fase 04 — Modelagem (torneio de modelos e pódio Top 3)")
    argumentos = parser.parse_args()

    print("\n" + "=" * 95)
    print("🚀 INICIANDO FASE 04: MODELAGEM (TORNEIO DE MODELOS E PÓDIO TOP 3)")
    print("=" * 95 + "\n")

    # 1. RESOLUÇÃO PARAMETRIZADA do dataset, do contrato e das pastas de artefatos.
    pastas = resolver_pastas_dataset(argumentos.dataset)
    nome_dataset = pastas["nome"]
    pasta_ml = pastas["ml"]
    pasta_modelos = pastas["modelos"]
    pasta_modelos.mkdir(parents=True, exist_ok=True)

    contrato = resolver_contrato(nome_dataset, argumentos.problema)
    if contrato is None:
        logging.error(
            "Nenhum contrato de problema definido para o dataset '%s'. "
            "Execute a Fase 3 com --problema ou informe --problema na linha de comando.",
            nome_dataset,
        )
        raise SystemExit(1)

    logging.info(
        "Dataset: '%s' | Problema: '%s' | Tarefa: %s | Semente: %d",
        nome_dataset,
        contrato.id,
        contrato.tipo_tarefa.value,
        argumentos.semente,
    )

    # 2. CARREGAMENTO das partições Parquet preparadas na Fase 3.
    caminho_treino = pasta_ml / "treino_processado.parquet"
    caminho_val = pasta_ml / "validacao_processada.parquet"
    caminho_teste = pasta_ml / "teste_processado.parquet"

    if not caminho_treino.is_file() or not caminho_val.is_file():
        logging.error("Partições de treino ou validação não localizadas em: %s", pasta_ml)
        raise SystemExit(1)

    df_treino = pd.read_parquet(caminho_treino)
    df_val = pd.read_parquet(caminho_val)

    supervisionado = contrato.exige_alvo
    coluna_alvo = "alvo_contratado"

    if supervisionado:
        if coluna_alvo not in df_treino.columns:
            logging.error("Coluna alvo '%s' ausente na partição de treino.", coluna_alvo)
            raise SystemExit(1)
        X_treino = df_treino.drop(columns=[coluna_alvo])
        y_treino = df_treino[coluna_alvo]
        X_val = df_val.drop(columns=[coluna_alvo])
        y_val = df_val[coluna_alvo]
    else:
        X_treino = df_treino
        y_treino = None
        X_val = df_val
        y_val = None

    logging.info(
        "Amostras carregadas — Treino: %d linhas | Validação: %d linhas | Features: %d colunas.",
        len(X_treino),
        len(X_val),
        X_treino.shape[1],
    )

    # 3. SELEÇÃO DO COMPARADOR conforme a família de tarefa do contrato.
    comparador = criar_comparador(
        tipo_tarefa=contrato.tipo_tarefa.value,
        semente_aleatoria=argumentos.semente,
        parametros=contrato.parametros,
    )

    df_placar, modelo_campeao, nome_campeao = comparador.executar_treinamento_e_benchmark(
        X_treino=X_treino, y_treino=y_treino, X_val=X_val, y_val=y_val
    )

    # 4. EXIBIÇÃO do placar comparativo no terminal.
    print("\n" + "=" * 95)
    print(f"🏆 PLACAR DO TORNEIO — {contrato.nome} ({contrato.tipo_tarefa.value.upper()})")
    print("=" * 95)
    print(df_placar.to_string(index=False))
    print("=" * 95 + "\n")

    # 5. PERSISTÊNCIA dos artefatos do pódio (Etapa 5 — G3: nada de Top 3 hardcoded).
    nomes_top3 = list(df_placar.head(3)["modelo"])
    catalogo_top3 = {nome: comparador.modelos_treinados[nome] for nome in nomes_top3}

    caminho_leaderboard = pasta_modelos / "leaderboard.csv"
    df_placar.to_csv(caminho_leaderboard, index=False)

    caminho_top3 = pasta_modelos / "catalogo_top3_modelos.joblib"
    joblib.dump(catalogo_top3, caminho_top3)

    caminho_top3_json = pasta_modelos / "top3.json"

    # Sanitiza as métricas: remove valores não-finitos (NaN/inf/None), que o
    # JSON serializa como 'null' e invalidam o registro (schema exige float).
    def _metrica_finita(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return False
        return math.isfinite(float(valor))

    metricas_top3 = {
        str(linha["modelo"]): {
            chave: float(valor)
            for chave, valor in linha.items()
            if chave != "modelo" and _metrica_finita(valor)
        }
        for _, linha in df_placar.head(3).iterrows()
    }
    caminho_top3_json.write_text(
        __import__("json").dumps(
            {
                "dataset": nome_dataset,
                "problema": contrato.id,
                "tipo_tarefa": contrato.tipo_tarefa.value,
                "metrica_otimizacao": contrato.metrica_effective,
                "top3": nomes_top3,
                "metricas": metricas_top3,
                "campeao_tecnico": nome_campeao,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # 5.5. AVALIAÇÃO DETALHADA dos finalistas (matriz de confusão, métricas por
    # família de tarefa, custos de negócio e figura individual de cada um do Top 3).
    # Não supervisionados são avaliados sobre o próprio treino (não há alvo/holdout).
    try:
        from src.etapas.fase_04_modelagem.avaliacao_detalhada import gerar_avaliacao_detalhada

        if supervisionado:
            x_avaliacao, y_avaliacao, particao = X_val, y_val, "validacao"
        else:
            x_avaliacao, y_avaliacao, particao = X_treino, None, "treino"

        gerar_avaliacao_detalhada(
            catalogo_top3=catalogo_top3,
            tipo_tarefa=contrato.tipo_tarefa.value,
            x=x_avaliacao,
            y=y_avaliacao,
            pasta_relatorios=pastas["relatorios"],
            pasta_modelos=pasta_modelos,
            dataset=nome_dataset,
            problema=contrato.id,
            metrica_otimizacao=contrato.metrica_effective,
            contrato=contrato,
            particao=particao,
        )
    except Exception as erro_avaliacao:
        logging.warning(
            "Avaliação detalhada do pódio não foi gerada (a fase segue): %s", erro_avaliacao
        )

    # 6. PERSISTÊNCIA do modelo campeão com manifesto de governança.
    caminho_salvamento = pasta_modelos / "modelo_campeao.joblib"
    metadados_governanca = {
        "etapa": "Fase 04 - Modelagem",
        "dataset": nome_dataset,
        "problema": contrato.id,
        "pergunta_negocio": contrato.pergunta_negocio,
        "tipo_tarefa": contrato.tipo_tarefa.value,
        "algoritmo_campeao": nome_campeao,
        "criterio_selecao": f"Maior {contrato.metrica_effective} no conjunto de validação cego",
        "modelos_no_podio_top3": nomes_top3,
        "metricas_validacao": df_placar.iloc[0].to_dict(),
        "total_amostras_treinadas": int(len(X_treino)),
        "total_atributos_entrada": int(X_treino.shape[1]),
        "atributos_utilizados": list(X_treino.columns),
        "semente": int(argumentos.semente),
    }

    GerenciadorPersistenciaModelos.salvar_modelo_com_metadados(
        objeto_modelo=modelo_campeao,
        caminho_artefato=caminho_salvamento,
        metadados_governanca=metadados_governanca,
    )

    # 7. ATUALIZAÇÃO do registro do dataset com o pódio e o campeão técnico.
    try:
        from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

        gerenciador = GerenciadorDatasets(diretorio_raiz=Path(__file__).resolve().parents[2])
        registro = gerenciador.obter_ou_criar(nome_dataset)
        registro.top3 = nomes_top3
        registro.metricas_top3 = metricas_top3
        registro.campeao = registro.campeao or nome_campeao
        registro.contrato_problema = contrato
        registro.marcar_fase("04", "concluida")
        registro.registrar_observacao(
            f"Fase 04 concluída: campeão técnico '{nome_campeao}' "
            f"({contrato.metrica_effective}={df_placar.iloc[0][contrato.metrica_effective] if contrato.metrica_effective in df_placar.columns else 'n/d'})."
        )
        gerenciador.salvar(registro)
    except Exception as erro_registro:
        logging.warning("Não foi possível atualizar o registro do dataset: %s", erro_registro)

    print("\n" + "=" * 95)
    print(f"✅ FASE 04 CONCLUÍDA: CAMPEÃO TÉCNICO '{nome_campeao}' E PÓDIO TOP 3 PERSISTIDOS!")
    print(f"📁 Leaderboard: {caminho_leaderboard.resolve()}")
    print(f"📁 Catálogo Top 3: {caminho_top3.resolve()}")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    main()
