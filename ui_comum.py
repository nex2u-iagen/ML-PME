"""Helpers compartilhados do frontend Streamlit (CRISP-DM operacional).

Centraliza a criação do ClientePlataforma (cacheada entre reruns), a listagem
de datasets e o painel de acompanhamento de jobs com atualização automática
sem bloquear a interface.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Raiz do projeto ancorada no arquivo, independente do diretório de trabalho.
RAIZ_PROJETO = Path(__file__).resolve().parent

# Endereço da API (compatível com variável de ambiente API_URL).
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


@st.cache_resource
def obter_cliente():
    """Retorna (singleton) o ClientePlataforma compartilhado entre reruns.

    Usa ``st.cache_resource`` para não recriar o cliente — e não refazer a
    detecção de modo — a cada interação do usuário.
    """
    from src.nucleo.orquestracao.cliente_plataforma import ClientePlataforma

    return ClientePlataforma(diretorio_raiz=RAIZ_PROJETO, url_base=API_URL)


@st.cache_data(ttl=30, show_spinner=False)
def listar_datasets_cacheado() -> List[Dict[str, Any]]:
    """Lista os datasets registrados, com cache curto entre reruns."""
    cliente = obter_cliente()
    try:
        cliente.detectar_modo()
        return cliente.listar_datasets()
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def listar_problemas_cacheado() -> List[Dict[str, Any]]:
    """Lista os 15 problemas de negócio do catálogo, com cache entre reruns."""
    try:
        return obter_cliente().listar_problemas()
    except Exception:
        return []


def invalidar_cache_datasets() -> None:
    """Limpa o cache de listagem (usar após upload/novo dataset)."""
    listar_datasets_cacheado.clear()


def nomes_datasets() -> List[str]:
    """Retorna apenas os nomes dos datasets registrados, ordenados."""
    try:
        return sorted(
            d.get("nome", "") for d in listar_datasets_cacheado() if d.get("nome")
        )
    except Exception:
        return []


def resumo_dataset(nome: str) -> Optional[Dict[str, Any]]:
    """Retorna o resumo de um dataset específico ou ``None``."""
    for resumo in listar_datasets_cacheado():
        if resumo.get("nome") == nome:
            return resumo
    return None


def garantir_estado() -> None:
    """Inicializa as chaves de estado usadas por todas as páginas."""
    if "dataset_nome" not in st.session_state:
        st.session_state.dataset_nome = None
    if "job_fase" not in st.session_state:
        st.session_state.job_fase = {}


def selecionar_dataset(nome: Optional[str]) -> None:
    """Grava o dataset selecionado no estado compartilhado.

    Aceita ``None`` para limpar a seleção (volta ao estado sem dataset).
    """
    nome = nome or None
    if nome != st.session_state.dataset_nome:
        st.session_state.dataset_nome = nome
        # Seleção mudou: descarta jobs do dataset anterior.
        st.session_state.job_fase = {}


# ----------------------------------------------------------------------------------
# PAINEL DE JOBS (não-bloqueante, com auto-refresh via fragmento)
# ----------------------------------------------------------------------------------
def submeter_fase(
    dataset: str,
    fase: str,
    semente: int = 42,
    problema: Optional[str] = None,
) -> Optional[str]:
    """Submete a execução de uma fase e registra o job no estado.

    Args:
        dataset (str): nome do dataset alvo.
        fase (str): identificador da fase ('01'..'05').
        semente (int): semente matemática para reprodutibilidade.
        problema (Optional[str]): identificador do problema de negócio
            (obrigatório para as Fases 03/04/05 quando ainda não há
            contrato persistido).

    Returns:
        Optional[str]: identificador do job ou ``None`` em caso de falha.
    """
    cliente = obter_cliente()
    try:
        job = cliente.executar_fase(dataset, fase, semente=semente, problema=problema)
        id_job = job.get("id")
        # Reseta o acompanhamento: novo job em execução (limpa flag de fim).
        st.session_state.job_fase[fase] = id_job
        st.session_state.job_fase.pop(f"{fase}_final", None)
        return id_job
    except Exception as erro:
        st.error(f"Falha ao submeter a fase {fase}: {erro}")
        return None


@st.fragment(run_every="3s")
def _painel_job_auto(id_job: str, chave: str) -> None:
    """Fragmento com auto-refresh: consulta o job até ele terminar.

    Quando o job finaliza, força um rerun da página para que os botões e
    relatórios sejam atualizados — e o auto-refresh cesse.
    """
    cliente = obter_cliente()
    job = cliente.consultar_job(id_job)
    if job is None:
        st.warning("Job não encontrado. Reexecute a fase.")
        st.session_state.job_fase.pop(chave, None)
        return

    status = job.get("status", "desconhecido")
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        col1.markdown(f"**Fase {chave}** — job `{id_job}`: **{status}**")
        col2.write("")

    if status in ("concluido", "erro", "falha"):
        st.session_state.job_fase[f"{chave}_final"] = True
        st.rerun()


def painel_job(dataset: str, fase: str) -> Optional[str]:
    """Exibe o painel de acompanhamento do job da fase informada.

    Enquanto o job roda, atualiza sozinho a cada 3s (sem travar a UI).
    Quando termina, devolve o status final para a página reagir.

    Args:
        dataset (str): nome do dataset (para validar se o job ainda vale).
        fase (str): identificador da fase ('01'..'05').

    Returns:
        Optional[str]: status final do job ou ``None`` se não há job.
    """
    cliente = obter_cliente()
    id_job = st.session_state.job_fase.get(fase)
    if not id_job:
        return None

    # Job já finalizado: mostra o resultado sem auto-refresh.
    if st.session_state.job_fase.get(f"{fase}_final"):
        job = cliente.consultar_job(id_job)
        if job is None:
            st.session_state.job_fase.pop(f"{fase}", None)
            st.session_state.job_fase.pop(f"{fase}_final", None)
            return None
        status = job.get("status", "desconhecido")
        _exibir_log(job, chave=fase)
        if status == "concluido":
            st.success(f"Fase {fase} concluída com sucesso.")
        elif status in ("erro", "falha"):
            st.error(f"Fase {fase} terminou com status: {status}.")
        return status

    # Job em execução: fragmento com atualização automática.
    _painel_job_auto(id_job, fase)
    job = cliente.consultar_job(id_job)
    return job.get("status") if job else None


def _exibir_log(job: Dict[str, Any], chave: str) -> None:
    """Mostra as últimas linhas de log do job em um expander."""
    linhas = job.get("ultimas_linhas_log") or []
    if linhas:
        with st.expander("Log de execução"):
            for linha in linhas[-20:]:
                st.text(linha)
            # Aponta o arquivo de log completo (tee gravado pelo GerenciadorJobs),
            # já que o stdout do job acontece dentro do processo da API.
            caminho_log = RAIZ_PROJETO / "logs" / "fases" / f"{job.get('id', chave)}.log"
            if caminho_log.is_file():
                st.caption(
                    f"Log completo ({job.get('total_linhas_log', len(linhas))} linhas): "
                    f"`{caminho_log.relative_to(RAIZ_PROJETO)}` — acompanhe ao vivo com "
                    f"`tail -f`."
                )


def limpar_job(fase: str) -> None:
    """Remove o registro do job da fase (para permitir reexecução)."""
    st.session_state.job_fase.pop(fase, None)
    st.session_state.job_fase.pop(f"{fase}_final", None)
