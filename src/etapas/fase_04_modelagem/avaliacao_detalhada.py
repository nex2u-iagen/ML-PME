"""Avaliação Detalhada dos Finalistas da Fase 04 (Torneio de Modelos).

Responsabilidade Única: calcular, para **cada** modelo do pódio Top 3, a
avaliação aprofundada sobre a partição de validação cego (ou de treino, para
tarefas não supervisionadas) e persistir:

- a **matriz de confusão** com as contagens (VP/FP/FN/TN) e as classes;
- as **métricas derivadas** por família de tarefa (classificação, regressão,
  agrupamento e detecção de anomalias);
- o **custo de negócio** dos erros quando o contrato declara ``custos``;
- a **figura individual** do modelo (matriz de confusão, dispersão previsto ×
  real ou distribuição de grupos/anomalias) em 300 DPI;
- o laudo consolidado ``avaliacao_top3.json`` consumido pelo frontend.

O módulo é autocontido: não altera o comparador nem o pódio — apenas enriquece
os artefatos da Fase 04 com a visão por finalista que a tela de decisão humana
exibe.
"""

# 'import math' valida finitude dos valores antes da serialização JSON.
import json
import logging
import math

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos.
from pathlib import Path

# 'from typing' oferece anotações estáticas rigorosas das interfaces públicas.
from typing import Any, Dict, List, Optional

# 'matplotlib.use("Agg")' fixa o backend sem display (obrigatório em servidor).
import matplotlib

matplotlib.use("Agg")

# 'import pyplot' traz a API de figuras do matplotlib após o backend seguro.
import matplotlib.pyplot as plt

# 'import numpy' fornece a manipulação numérica vetorial dos erros e rótulos.
import numpy as np

# 'import pandas' sustenta as séries do vetor-alvo e as tabelas de distribuição.
import pandas as pd

# Métricas formais do Scikit-Learn usadas na avaliação detalhada:
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)


def _finito(valor: Any) -> Optional[float]:
    """Converte para ``float`` finito; devolve ``None`` para NaN/inf/inválidos.

    Args:
        valor (Any): Valor bruto vindo das métricas ou da predição.

    Returns:
        Optional[float]: Número serializável ou ``None`` quando não é finito.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if math.isfinite(numero) else None


def _rotulo_json(classe: Any) -> Any:
    """Normaliza o rótulo de classe para um tipo JSON amigável.

    Args:
        classe (Any): Rótulo original (int, float ou string).

    Returns:
        Any: ``int`` quando o valor é inteiro, caso contrário o valor original.
    """
    try:
        numero = float(classe)
        if math.isfinite(numero) and numero.is_integer():
            return int(numero)
        return _finito(numero)
    except (TypeError, ValueError):
        return str(classe)


def _salvar_figura(figura: plt.Figure, pasta: Path, nome_arquivo: str) -> Optional[str]:
    """Persiste a figura em 300 DPI, fecha a janela e devolve o caminho.

    Args:
        figura (plt.Figure): Instância da tela gráfica do matplotlib.
        pasta (Path): Diretório de destino das figuras.
        nome_arquivo (str): Nome físico do arquivo (extensão ``.png``).

    Returns:
        Optional[str]: Caminho absoluto gravado ou ``None`` em caso de falha.
    """
    try:
        pasta.mkdir(parents=True, exist_ok=True)
        figura.tight_layout()
        caminho = pasta / nome_arquivo
        figura.savefig(caminho, dpi=300, bbox_inches="tight")
        return str(caminho.resolve())
    except Exception as erro_figura:  # pragma: no cover - defensivo de I/O
        logging.warning("Não foi possível gravar a figura '%s': %s", nome_arquivo, erro_figura)
        return None
    finally:
        plt.close(figura)


def _avaliar_classificacao(
    estimador: Any,
    x: Any,
    y: pd.Series,
    info: Dict[str, Any],
    pasta_figuras: Path,
    nome_modelo: str,
    contrato: Optional[Any],
) -> None:
    """Avalia um finalista de classificação: matriz de confusão + métricas + custos.

    Args:
        estimador: Modelo treinado do pódio.
        x: Matriz de atributos da partição de avaliação.
        y (pd.Series): Vetor-alvo real da partição de avaliação.
        info (Dict[str, Any]): Dicionário do modelo ser preenchido in place.
        pasta_figuras (Path): Pasta de destino da figura.
        nome_modelo (str): Nome canônico do finalista.
        contrato: Contrato de problema (para os custos de negócio), se houver.
    """
    y_pred = estimador.predict(x)

    classes: List[Any] = sorted(set(_rotulo_json(c) for c in set(y) | set(y_pred)), key=str)
    matriz = confusion_matrix(y, y_pred, labels=classes)

    info["matriz_confusao"] = {
        "classes": classes,
        "matriz": [[int(v) for v in linha] for linha in matriz.tolist()],
    }

    metricas: Dict[str, Any] = {
        "acuracia": _finito(accuracy_score(y, y_pred)),
    }

    binario = len(classes) == 2
    if binario:
        # Com labels ordenadas, a matriz é [[TN, FP], [FN, TP]].
        tn, fp, fn, tp = (int(v) for v in matriz.ravel())
        pos_label = classes[1]
        metricas.update(
            {
                "precisao": _finito(precision_score(y, y_pred, pos_label=pos_label, zero_division=0)),
                "recall": _finito(recall_score(y, y_pred, pos_label=pos_label, zero_division=0)),
                "f1_score": _finito(f1_score(y, y_pred, pos_label=pos_label, zero_division=0)),
                "especificidade": _finito(tn / (tn + fp)) if (tn + fp) > 0 else None,
            }
        )
        info["matriz_confusao"].update(
            {"verdadeiro_positivo": tp, "falso_positivo": fp, "falso_negativo": fn, "verdadeiro_negativo": tn}
        )

        # ROC-AUC exige ambas as classes presentes na partição de avaliação.
        if hasattr(estimador, "predict_proba"):
            try:
                probas = estimador.predict_proba(x)
                coluna_positiva = classes.index(pos_label)
                metricas["roc_auc"] = _finito(roc_auc_score(y, probas[:, coluna_positiva]))
            except Exception:  # pragma: no cover - defensivo de partição degenerada
                metricas["roc_auc"] = None

        # CUSTO DE NEGÓCIO: traduz a matriz de confusão em moeda corrente.
        custos = getattr(contrato, "custos", None) if contrato is not None else None
        if custos is not None:
            info["custos_negocio"] = {
                "custo_falso_negativo_unit": _finito(custos.falso_negativo),
                "custo_falso_positivo_unit": _finito(custos.falso_positivo),
                "ganho_verdadeiro_positivo_unit": _finito(custos.verdadeiro_positivo),
                "perda_falsos_negativos": _finito(fn * custos.falso_negativo),
                "perda_falsos_positivos": _finito(fp * custos.falso_positivo),
                "ganho_verdadeiros_positivos": _finito(tp * custos.verdadeiro_positivo),
                "custo_liquido": _finito(custos.custo_total(fn, fp, tp)),
            }
    else:
        metricas.update(
            {
                "precisao": _finito(precision_score(y, y_pred, average="macro", zero_division=0)),
                "recall": _finito(recall_score(y, y_pred, average="macro", zero_division=0)),
                "f1_score": _finito(f1_score(y, y_pred, average="macro", zero_division=0)),
            }
        )

    info["metricas"] = {k: v for k, v in metricas.items() if v is not None}

    # FIGURA: matriz de confusão individual do finalista.
    figura, eixo = plt.subplots(figsize=(5.6, 4.6))
    ConfusionMatrixDisplay.from_predictions(
        y,
        y_pred,
        display_labels=[str(c) for c in classes],
        cmap="Blues",
        colorbar=False,
        ax=eixo,
        values_format="d",
    )
    eixo.set_title(f"Matriz de Confusão — {nome_modelo}", fontsize=11, pad=10)
    info["figura"] = _salvar_figura(figura, pasta_figuras, f"matriz_confusao_{nome_modelo}.png")


def _avaliar_regressao(
    estimador: Any,
    x: Any,
    y: pd.Series,
    info: Dict[str, Any],
    pasta_figuras: Path,
    nome_modelo: str,
) -> None:
    """Avalia um finalista de regressão: R², RMSE, MAE, MAPE + dispersão.

    Args:
        estimador: Modelo treinado do pódio.
        x: Matriz de atributos da partição de avaliação.
        y (pd.Series): Vetor-alvo real da partição de avaliação.
        info (Dict[str, Any]): Dicionário do modelo ser preenchido in place.
        pasta_figuras (Path): Pasta de destino da figura.
        nome_modelo (str): Nome canônico do finalista.
    """
    y_pred = np.asarray(estimador.predict(x), dtype=float)
    y_real = pd.Series(np.asarray(y, dtype=float))

    mae = float(mean_absolute_error(y_real, y_pred))
    metricas: Dict[str, Any] = {
        "r2": _finito(r2_score(y_real, y_pred)),
        "rmse": _finito(np.sqrt(mean_squared_error(y_real, y_pred))),
        "mae": _finito(mae),
    }

    # MAPE é indefinido quando o alvo real é zero: considera apenas não nulos.
    mascara_nao_zero = y_real.to_numpy() != 0
    if mascara_nao_zero.any():
        metricas["mape"] = _finito(
            float(np.mean(np.abs((y_real.to_numpy()[mascara_nao_zero] - y_pred[mascara_nao_zero]) / y_real.to_numpy()[mascara_nao_zero])) * 100)
        )
    else:
        metricas["mape"] = None

    info["metricas"] = {k: v for k, v in metricas.items() if v is not None}

    # FIGURA: dispersão previsto × real com a reta de perfeição.
    figura, eixo = plt.subplots(figsize=(6.2, 5.2))
    eixo.scatter(y_real, y_pred, alpha=0.55, edgecolors="k", linewidths=0.3, s=28)
    limite_min = float(min(y_real.min(), y_pred.min()))
    limite_max = float(max(y_real.max(), y_pred.max()))
    margem = (limite_max - limite_min) * 0.05 or 1.0
    eixo.plot(
        [limite_min - margem, limite_max + margem],
        [limite_min - margem, limite_max + margem],
        color="gray",
        linestyle="--",
        lw=1.4,
        label="Previsão perfeita",
    )
    eixo.set_xlabel("Valor real", fontsize=10)
    eixo.set_ylabel("Valor previsto", fontsize=10)
    eixo.set_title(f"Previsto × Real — {nome_modelo}", fontsize=11, pad=10)
    eixo.legend(fontsize=9, frameon=True)
    info["figura"] = _salvar_figura(figura, pasta_figuras, f"dispersao_previsto_vs_real_{nome_modelo}.png")


def _avaliar_agrupamento(
    estimador: Any,
    x: Any,
    info: Dict[str, Any],
    pasta_figuras: Path,
    nome_modelo: str,
) -> None:
    """Avalia um finalista de agrupamento: silhueta, inércia e distribuição.

    Args:
        estimador: Modelo treinado do pódio.
        x: Matriz de atributos da partição de avaliação.
        info (Dict[str, Any]): Dicionário do modelo ser preenchido in place.
        pasta_figuras (Path): Pasta de destino da figura.
        nome_modelo (str): Nome canônico do finalista.
    """
    rotulos = np.asarray(estimador.predict(x))
    unicos, contagens = np.unique(rotulos, return_counts=True)

    silhueta = None
    if len(unicos) > 1 and len(rotulos) > len(unicos):
        try:
            silhueta = _finito(silhouette_score(x, rotulos))
        except Exception:  # pragma: no cover - defensivo
            silhueta = None

    info["metricas"] = {
        k: v
        for k, v in {
            "silhueta": silhueta,
            "inercia": _finito(getattr(estimador, "inertia_", None)),
            "numero_grupos": int(len(unicos)),
        }.items()
        if v is not None
    }
    info["distribuicao_grupos"] = {str(_rotulo_json(u)): int(c) for u, c in zip(unicos, contagens)}

    # FIGURA: barras com o tamanho de cada grupo no holdout.
    figura, eixo = plt.subplots(figsize=(6.2, 4.4))
    eixo.bar([str(_rotulo_json(u)) for u in unicos], contagens, color="steelblue", edgecolor="k", linewidth=0.4)
    eixo.set_xlabel("Grupo", fontsize=10)
    eixo.set_ylabel("Amostras", fontsize=10)
    eixo.set_title(f"Distribuição dos Grupos — {nome_modelo}", fontsize=11, pad=10)
    info["figura"] = _salvar_figura(figura, pasta_figuras, f"distribuicao_grupos_{nome_modelo}.png")


def _avaliar_anomalias(
    estimador: Any,
    x: Any,
    info: Dict[str, Any],
    pasta_figuras: Path,
    nome_modelo: str,
) -> None:
    """Avalia um finalista de detecção de anomalias: taxa, separação e contagens.

    O LOF sem ``novelty=True`` não expõe ``predict``; nesse caso os rótulos são
    reconstruídos a partir de ``negative_outlier_factor_`` vs ``offset_``
    (critério equivalente ao ``fit_predict`` oficial do Scikit-Learn).

    Args:
        estimador: Detector treinado do pódio.
        x: Matriz de atributos usada na avaliação.
        info (Dict[str, Any]): Dicionário do modelo ser preenchido in place.
        pasta_figuras (Path): Pasta de destino da figura.
        nome_modelo (str): Nome canônico do finalista.
    """
    rotulos = None
    if hasattr(estimador, "predict"):
        try:
            rotulos = np.asarray(estimador.predict(x))
        except Exception:  # pragma: no cover - defensivo
            rotulos = None

    fatores = getattr(estimador, "negative_outlier_factor_", None)
    if rotulos is None:
        if fatores is None or len(fatores) != len(x):
            raise RuntimeError(
                "Detector sem 'predict' e sem scores alinhados à partição de avaliação."
            )
        rotulos = np.where(np.asarray(fatores) < float(estimador.offset_), -1, 1)

    scores = None
    if hasattr(estimador, "decision_function"):
        try:
            scores = np.asarray(estimador.decision_function(x), dtype=float)
        except Exception:  # pragma: no cover - defensivo
            scores = None
    if scores is None and fatores is not None and len(fatores) == len(x):
        scores = np.asarray(fatores, dtype=float)

    anomalias = int(np.sum(rotulos == -1))
    normais = int(np.sum(rotulos == 1))

    info["metricas"] = {
        k: v
        for k, v in {
            "taxa_anomalia": _finito(anomalias / len(rotulos)) if len(rotulos) else None,
            "separacao": _finito(np.std(scores)) if scores is not None else None,
        }.items()
        if v is not None
    }
    info["distribuicao_anomalias"] = {"normais": normais, "anomalias": anomalias}

    # FIGURA: barras com a fatia de registros normais × anômalos.
    figura, eixo = plt.subplots(figsize=(5.6, 4.4))
    eixo.bar(["Normais", "Anomalias"], [normais, anomalias], color=["steelblue", "indianred"], edgecolor="k", linewidth=0.4)
    eixo.set_ylabel("Registros", fontsize=10)
    eixo.set_title(f"Distribuição de Anomalias — {nome_modelo}", fontsize=11, pad=10)
    info["figura"] = _salvar_figura(figura, pasta_figuras, f"distribuicao_anomalias_{nome_modelo}.png")


def gerar_avaliacao_detalhada(
    catalogo_top3: Dict[str, Any],
    tipo_tarefa: str,
    x: Any,
    y: Optional[pd.Series],
    pasta_relatorios: Path,
    pasta_modelos: Path,
    dataset: str,
    problema: str,
    metrica_otimizacao: str,
    contrato: Optional[Any] = None,
    particao: str = "validacao",
) -> Dict[str, Any]:
    """Avalia cada finalista do Top 3 em detalhe e persiste JSON + figuras.

    Args:
        catalogo_top3 (Dict[str, Any]): Dicionário nome → estimador ajustado.
        tipo_tarefa (str): Família de tarefa ('classificacao', 'regressao',
            'agrupamento' ou 'deteccao_anomalias').
        x: Matriz de atributos da partição de avaliação.
        y (Optional[pd.Series]): Vetor-alvo (None para tarefas não supervisionadas).
        pasta_relatorios (Path): Pasta raiz de relatórios do dataset.
        pasta_modelos (Path): Pasta de artefatos do pódio do dataset.
        dataset (str): Nome do dataset.
        problema (str): Identificador do contrato de problema.
        metrica_otimizacao (str): Métrica de otimização do contrato.
        contrato (Optional[Any]): Contrato de problema (leva os custos de negócio).
        particao (str): Partição usada na avaliação ('validacao' ou 'treino').

    Returns:
        Dict[str, Any]: Laudo consolidado (também persistido em
        ``avaliacao_top3.json`` dentro da pasta de modelos).
    """
    pasta_figuras = Path(pasta_relatorios) / "fase_04_modelagem"
    pasta_figuras.mkdir(parents=True, exist_ok=True)

    tarefa = str(tipo_tarefa).strip().lower()
    modelos_info: Dict[str, Any] = {}

    for nome_modelo, estimador in catalogo_top3.items():
        info: Dict[str, Any] = {}
        try:
            if tarefa == "classificacao":
                if y is None:
                    raise RuntimeError("Tarefa de classificação exige vetor-alvo.")
                _avaliar_classificacao(estimador, x, y, info, pasta_figuras, nome_modelo, contrato)
            elif tarefa == "regressao":
                if y is None:
                    raise RuntimeError("Tarefa de regressão exige vetor-alvo.")
                _avaliar_regressao(estimador, x, y, info, pasta_figuras, nome_modelo)
            elif tarefa == "agrupamento":
                _avaliar_agrupamento(estimador, x, info, pasta_figuras, nome_modelo)
            elif tarefa == "deteccao_anomalias":
                _avaliar_anomalias(estimador, x, info, pasta_figuras, nome_modelo)
            else:
                raise ValueError(f"Família de tarefa '{tipo_tarefa}' não suportada.")
        except Exception as erro_modelo:
            logging.warning(
                "Avaliação detalhada do finalista '%s' falhou: %s", nome_modelo, erro_modelo
            )
            info.setdefault("erro", str(erro_modelo))
        modelos_info[nome_modelo] = info

    laudo: Dict[str, Any] = {
        "dataset": dataset,
        "problema": problema,
        "tipo_tarefa": tarefa,
        "metrica_otimizacao": metrica_otimizacao,
        "particao": particao,
        "total_amostras": int(len(x)) if x is not None else 0,
        "modelos": modelos_info,
    }

    caminho_laudo = Path(pasta_modelos) / "avaliacao_top3.json"
    caminho_laudo.parent.mkdir(parents=True, exist_ok=True)
    caminho_laudo.write_text(
        json.dumps(laudo, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    logging.info("Avaliação detalhada do pódio persistida em: %s", caminho_laudo)
    return laudo
