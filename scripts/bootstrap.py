"""Bootstrap compartilhado pelos scripts executores do projeto.

Concentra a descoberta da raiz do repositório, os diretórios canônicos de
artefatos e relatórios e a configuração padronizada de logging. Os executores
devem ser invocados como módulos a partir da raiz do projeto:

    uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3
    uv run python -m scripts.executores_projeto.servir_api
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

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
    raiz = str(RAIZ_PROJETO)
    if raiz not in sys.path:
        sys.path.insert(0, raiz)
    logging.basicConfig(level=nivel, format=FORMATO_LOG)
    return RAIZ_PROJETO
