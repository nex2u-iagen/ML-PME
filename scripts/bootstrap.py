"""Bootstrap compartilhado pelos scripts executores do projeto.

Concentra a descoberta da raiz do repositório, os diretórios canônicos de
artefatos e relatórios, a configuração padronizada de logging e a **camada de
parametrização** que permite ao frontend dirigir o backend por linha de comando.

Os executores devem ser invocados como módulos a partir da raiz do projeto:

    uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3 --dataset mercado_vencedor
    uv run python -m scripts.executores_projeto.servir_api
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from src.nucleo.contratos.contrato_problema import ContratoProblema
from src.nucleo.contratos.catalogo_problemas import CatalogoProblemas
from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
DIRETORIO_ARTEFATOS = RAIZ_PROJETO / "artefatos"
DIRETORIO_RELATORIOS = RAIZ_PROJETO / "relatorios"
FORMATO_LOG = "%(asctime)s — [%(levelname)s] — %(message)s"


def configurar_ambiente(nivel: int = logging.INFO) -> Path:
    """Garante a raiz do projeto no ``sys.path`` e configura o logging.

    Args:
        nivel: Nível mínimo de severidade das mensagens de log.

    Returns:
        Caminho absoluto da raiz do projeto.
    """
    # Garantir logs em tempo real no terminal (sem bufferização do Python)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    os.environ['PYTHONUNBUFFERED'] = '1'

    raiz = str(RAIZ_PROJETO)
    if raiz not in sys.path:
        sys.path.insert(0, raiz)
    logging.basicConfig(level=nivel, format=FORMATO_LOG, stream=sys.stdout)
    return RAIZ_PROJETO


# ----------------------------------------------------------------------------------
# CAMADA DE PARAMETRIZAÇÃO (G5) — o frontend dirige o backend por estes argumentos
# ----------------------------------------------------------------------------------
def argumentos_comuns(descricao: str) -> argparse.ArgumentParser:
    """Cria um parser de argumentos com o conjunto padrão de toda a esteira CRISP-DM.

    Todos os executores de fase compartilham os mesmos quatro parâmetros, o que
    garante que a mesma combinação (dataset + problema + semente) reproduza
    exatamente o mesmo resultado em qualquer etapa.

    Args:
        descricao (str): Texto de ajuda exibido no terminal.

    Returns:
        argparse.ArgumentParser: Parser configurado com os argumentos comuns.
    """
    parser = argparse.ArgumentParser(description=descricao)
    parser.add_argument(
        "--dataset",
        default=None,
        help="Nome do dataset (PME) em análise. Se omitido, usa o dataset mais recente.",
    )
    parser.add_argument(
        "--semente",
        type=int,
        default=42,
        help="Semente matemática para reprodutibilidade dos experimentos.",
    )
    parser.add_argument(
        "--problema",
        default=None,
        help="Identificador do problema de negócio no catálogo (ex.: previsao_faturamento).",
    )
    parser.add_argument(
        "--modo",
        choices=["real", "demo"],
        default="real",
        help="'real' opera sobre os dados do ERP; 'demo' usa a base sintética de demonstração.",
    )
    return parser


def resolver_nome_dataset(nome_dataset: Optional[str]) -> str:
    """Resolve deterministicamente o nome do dataset ativo.

    Args:
        nome_dataset (Optional[str]): Nome informado na linha de comando.

    Returns:
        str: Nome do dataset efetivamente selecionado.
    """
    if nome_dataset:
        return nome_dataset
    gerenciador = GerenciadorDatasets(RAIZ_PROJETO)
    return gerenciador.resolver_pasta_csv(None).name


def resolver_pastas_dataset(nome_dataset: Optional[str]) -> dict[str, Path]:
    """Monta o mapa de pastas canônicas de um dataset específico.

    Args:
        nome_dataset (Optional[str]): Nome do dataset em análise.

    Returns:
        dict[str, Path]: Mapa com as pastas de dados brutos, artefatos ML, modelos e
        relatórios do dataset.
    """
    gerenciador = GerenciadorDatasets(RAIZ_PROJETO)
    nome = resolver_nome_dataset(nome_dataset)
    return {
        "nome": nome,
        "brutos": gerenciador.pasta_csv_base / nome,
        "ml": gerenciador.pasta_ml(nome),
        "modelos": gerenciador.pasta_modelos_dataset(nome),
        "relatorios": gerenciador.pasta_relatorios(nome),
    }


def resolver_contrato(
    nome_dataset: Optional[str] = None,
    id_problema: Optional[str] = None,
) -> Optional[ContratoProblema]:
    """Carrega o contrato de problema ativo do dataset ou do catálogo.

    A ordem de precedência é: argumento explícito (``--problema``), contrato
    persistido pela Fase 3 e, por fim, o template do catálogo.

    Args:
        nome_dataset (Optional[str]): Dataset cujos artefatos serão inspecionados.
        id_problema (Optional[str]): Identificador explícito do problema.

    Returns:
        Optional[ContratoProblema]: Contrato vigente ou ``None`` quando não houver
        contrato definido (modo legado de inadimplência).
    """
    if id_problema:
        return CatalogoProblemas.obter(id_problema)

    if nome_dataset:
        caminho_contrato = RAIZ_PROJETO / "dados" / "processados" / nome_dataset / "ml" / "contrato_problema.json"
        if caminho_contrato.is_file():
            try:
                return ContratoProblema.carregar_de_json(caminho_contrato)
            except Exception as erro_leitura:
                logging.error("Contrato inválido em '%s': %s", caminho_contrato, erro_leitura)

    return None
