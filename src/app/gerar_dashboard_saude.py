"""CLI do Dashboard de Saúde 360° da Fase 02 (CRISP-DM).

A implementação pertence à Fase 02 (``src/etapas/fase_02_exploracao/
visao_360_saude.py``) — este módulo é apenas o atalho de linha de comandos
usado pelo app de vitrine e por quem prefere rodar o gerador isolado::

    python -m src.app.gerar_dashboard_saude --dataset mercadinho-v4
"""

# 'import logging' configura o console para acompanhar a geração.
import logging

# Importação da visão agnóstica de saúde (dono do domínio) na Fase 02.
from src.etapas.fase_02_exploracao.visao_360_saude import gerar_dashboard_saude

# Reexporta a função principal para importação direta pelo app Streamlit.
__all__ = ["gerar_dashboard_saude"]


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    # 'argparse' interpreta os parâmetros de linha de comandos do script.
    import argparse

    analisador_cli = argparse.ArgumentParser(
        description="Gera o Dashboard de Saúde 360° da Fase 02."
    )
    analisador_cli.add_argument(
        "--dataset",
        default=None,
        help="Nome do dataset (usa o prontuário mais recente quando omitido).",
    )
    argumentos = analisador_cli.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — [%(levelname)s] — %(message)s",
    )
    gerar_dashboard_saude(dataset=argumentos.dataset)
