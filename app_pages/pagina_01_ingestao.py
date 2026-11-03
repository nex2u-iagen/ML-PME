"""Página 01 — Ingestão (Fase CRISP-DM 01).

Criação de datasets (upload) e execução da Fase 01 de extração.
O dataset ativo é selecionado no sidebar e vale para todas as páginas.
"""

import pandas as pd
from pathlib import Path

import streamlit as st

from ui_comum import (
    garantir_estado,
    invalidar_cache_datasets,
    limpar_job,
    nomes_datasets,
    obter_cliente,
    painel_job,
    resumo_dataset,
    selecionar_dataset,
    submeter_fase,
)


def _estatisticas_csvs_dataset(nome: str) -> tuple[int, int, list[str]]:
    """Conta linhas totais e colunas dos CSVs brutos de um dataset.

    Args:
        nome: Nome do dataset.

    Returns:
        (total_linhas, total_colunas, nomes_arquivos) lidos de
        ``dados/brutos/csv/<nome>/``.
    """
    pasta = Path("dados") / "brutos" / "csv" / nome
    if not pasta.is_dir():
        return 0, 0, []
    total_linhas = 0
    max_colunas = 0
    arquivos = []
    for csv in sorted(pasta.glob("*.csv")):
        try:
            df = pd.read_csv(csv, nrows=0)
            colunas = len(df.columns)
            # Conta linhas de forma leve (apenas o cabeçalho já lido + contagem).
            with csv.open("r", encoding="utf-8", errors="ignore") as f:
                linhas = sum(1 for _ in f) - 1  # desconta cabeçalho
            total_linhas += max(linhas, 0)
            max_colunas = max(max_colunas, colunas)
            arquivos.append(csv.name)
        except Exception:
            arquivos.append(csv.name)
    return total_linhas, max_colunas, arquivos


def exibir_status_dataset(nome: str) -> None:
    """Mostra o cartão de status do dataset selecionado."""
    resumo = resumo_dataset(nome)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        if resumo:
            total_tabelas = resumo.get("total_tabelas", 0)
            matching = resumo.get("matching_semantico") or {}
            encontrados = sum(1 for v in matching.values() if v)
            status_fases = resumo.get("status_fases") or {}

            total_linhas, max_colunas, _ = _estatisticas_csvs_dataset(nome)

            with col1:
                st.metric("Tabelas", total_tabelas)
            with col2:
                st.metric("Linhas (CSVs brutos)", f"{total_linhas:,}".replace(",", "."))
            with col3:
                st.metric("Colunas (máx.)", max_colunas if max_colunas else "—")
            with col4:
                fases_concluidas = sum(
                    1 for s in status_fases.values() if s == "concluida"
                )
                st.metric("Fases concluídas", f"{fases_concluidas}/5")

            # Detalhes do matching em expander.
            if matching:
                with st.expander("Detalhes do matching semântico"):
                    for entidade, caminho in matching.items():
                        marca = "✓" if caminho else "✗"
                        st.write(f"{marca} **{entidade}**: {caminho or 'não encontrado'}")
        else:
            with col1:
                st.metric("Tabelas", "—")
            with col2:
                st.metric("Linhas (CSVs brutos)", "—")
            with col3:
                st.metric("Colunas (máx.)", "—")
            with col4:
                st.metric("Fases concluídas", "—")
            st.caption("Resumo completo disponível após o primeiro upload.")


def exibir_fases(nome: str) -> None:
    """Mostra o status das 5 fases e as ações disponíveis."""
    resumo = resumo_dataset(nome) or {}
    status_fases = resumo.get("status_fases") or {}

    st.markdown("#### Fases CRISP-DM")

    # Trilha das 5 fases.
    cols = st.columns(5)
    rotulos = ["01 · Ingestão", "02 · Raio-X", "03 · Preparação", "04 · Modelagem", "05 · Avaliação"]
    for idx, col in enumerate(cols):
        fase = f"0{idx + 1}"
        status = status_fases.get(fase, "pendente")
        with col:
            if status == "concluida":
                st.success(f"✓ {rotulos[idx]}")
            elif status == "executando":
                st.info(f"⏳ {rotulos[idx]}")
            else:
                st.caption(f"○ {rotulos[idx]}")

    st.divider()

    # Ação da Fase 01.
    fase_01_status = status_fases.get("01", "pendente")
    job_status = painel_job(nome, "01")

    col1, col2 = st.columns([2, 1])

    with col1:
        if fase_01_status == "concluida":
            st.success("Fase 01 concluída — dados extraídos e prontos.")
        elif job_status in ("executando", "pendente"):
            st.info("Fase 01 em execução. Acompanhe o painel acima.")
        else:
            st.caption("A Fase 01 extrai e normaliza as tabelas do ERP.")

    with col2:
        pode_executar = (
            fase_01_status != "concluida"
            and job_status not in ("executando", "pendente")
        )
        if st.button(
            "Executar Fase 01",
            type="primary" if pode_executar else "secondary",
            disabled=not pode_executar,
            width="stretch",
        ):
            with st.spinner("Submetendo a Fase 01..."):
                submeter_fase(nome, "01")
            st.rerun()

    # Navegação para a próxima fase.
    if fase_01_status == "concluida":
        st.divider()
        if st.button(
            "Ir para Raio-X (Fase 02) →",
            type="primary",
            width="stretch",
            icon=":material/arrow_forward:",
        ):
            st.switch_page("app_pages/pagina_02_raiox.py")


def exibir_criacao() -> None:
    """Formulário de criação de um novo dataset via upload."""
    st.markdown("#### Novo dataset")
    st.caption(
        "Envie o dump do ERP (`.sql`) ou as tabelas em CSV. "
        "Os arquivos são isolados em pasta própria do dataset."
    )

    with st.form("form_novo_dataset", clear_on_submit=False):
        nome_novo = st.text_input(
            "Nome do dataset (PME)",
            placeholder="ex.: mercadinho, rede_vencedora",
            help="Será usado como nome da pasta que isola os arquivos.",
        )
        col1, col2 = st.columns(2)
        with col1:
            arquivo_sql = st.file_uploader("Dump SQL (.sql)", type=["sql"])
        with col2:
            arquivos_csv = st.file_uploader(
                "Tabelas CSV (.csv)", type=["csv"], accept_multiple_files=True
            )

        enviar = st.form_submit_button(
            "Criar dataset", type="primary", width="stretch"
        )

    if enviar:
        if not nome_novo or not nome_novo.strip():
            st.error("Informe o nome do dataset.")
            return
        if not arquivo_sql and not arquivos_csv:
            st.error("Selecione ao menos um arquivo .sql ou .csv.")
            return

        nome = nome_novo.strip().lower()
        cliente = obter_cliente()

        arquivos = []
        if arquivo_sql:
            arquivos.append((arquivo_sql.name, arquivo_sql.read()))
        if arquivos_csv:
            for csv in arquivos_csv:
                arquivos.append((csv.name, csv.read()))

        try:
            with st.spinner(f"Enviando {len(arquivos)} arquivo(s)..."):
                cliente.registrar_upload(nome, arquivos)

            # Atualiza caches e seleciona o novo dataset.
            invalidar_cache_datasets()
            selecionar_dataset(nome)
            limpar_job("01")
            st.success(f"Dataset `{nome}` criado com sucesso.")
            st.rerun()
        except Exception as erro:
            st.error(f"Falha no upload: {erro}")


def exibir_reenvio(nome: str) -> None:
    """Reenvio opcional de arquivos de um dataset já existente."""
    with st.expander("Reenviar/substituir arquivos deste dataset"):
        st.caption(
            "Use apenas se precisar atualizar os dados brutos de um dataset já criado."
        )
        with st.form(f"form_reenvio_{nome}"):
            col1, col2 = st.columns(2)
            with col1:
                arquivo_sql = st.file_uploader("Dump SQL (.sql)", type=["sql"])
            with col2:
                arquivos_csv = st.file_uploader(
                    "Tabelas CSV (.csv)", type=["csv"], accept_multiple_files=True
                )
            enviar = st.form_submit_button("Reenviar arquivos", width="stretch")

        if enviar:
            if not arquivo_sql and not arquivos_csv:
                st.error("Selecione ao menos um arquivo.")
                return

            cliente = obter_cliente()
            arquivos = []
            if arquivo_sql:
                arquivos.append((arquivo_sql.name, arquivo_sql.read()))
            if arquivos_csv:
                for csv in arquivos_csv:
                    arquivos.append((csv.name, csv.read()))

            try:
                with st.spinner(f"Enviando {len(arquivos)} arquivo(s)..."):
                    cliente.registrar_upload(nome, arquivos)
                invalidar_cache_datasets()
                st.success("Arquivos atualizados. Execute a Fase 01 novamente.")
                st.rerun()
            except Exception as erro:
                st.error(f"Falha no reenvio: {erro}")


def main() -> None:
    """Corpo principal da página."""
    garantir_estado()
    st.caption("Upload de dados brutos e extração inicial")

    nome = st.session_state.dataset_nome

    if nome:
        st.info(f"Dataset ativo: **{nome}** (selecionado no sidebar)")
        exibir_status_dataset(nome)
        st.divider()
        exibir_fases(nome)
        st.divider()
        exibir_reenvio(nome)
    else:
        st.warning(
            "Nenhum dataset ativo. Selecione um no sidebar ou crie um novo abaixo."
        )
        st.divider()
        exibir_criacao()


if __name__ == "__main__":
    main()
