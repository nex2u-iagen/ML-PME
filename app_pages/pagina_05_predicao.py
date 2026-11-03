"""Página 05 — Predição de Risco de Crédito (Fase CRISP-DM 06, Pilar 4).

Formulário de entrada de dados de produção para previsão/classificação.
Consome o endpoint POST /predicao/risco_credito da API de inferência (porta 8000),
autenticando via Bearer JWT em POST /autenticacao/token.
"""

from pathlib import Path

import requests
import streamlit as st

from ui_comum import (
    API_URL,
    garantir_estado,
    nomes_datasets,
    selecionar_dataset,
    resumo_dataset,
    obter_cliente,
)

# Endpoints da API de inferência (Fase 06).
ENDPOINT_TOKEN = f"{API_URL}/autenticacao/token"
ENDPOINT_PREDICAO = f"{API_URL}/predicao/risco_credito"
ENDPOINT_PRONTIDAO = f"{API_URL}/saude/prontidao"

# Dados padrão de autenticação (mesmos da API).
USUARIO_PADRAO = "analista_credito"
SENHA_PADRAO = "senha_segura_mercado_2026"


# 'def _obter_token(...)' autentica na API e devolve o Bearer JWT.
def _obter_token() -> str | None:
    """Autentica na API e retorna o token JWT ou None em caso de falha."""
    try:
        resposta = requests.post(
            ENDPOINT_TOKEN,
            json={"usuario": USUARIO_PADRAO, "senha": SENHA_PADRAO},
            timeout=10,
        )
        if resposta.status_code == 200:
            return resposta.json().get("access_token")
        st.warning(f"Falha na autenticação (HTTP {resposta.status_code}).")
    except Exception as erro:
        st.error(f"Não foi possível autenticar na API: {erro}")
    return None


# 'def _executar_predicao(...)' envia os campos para a API e devolve o resultado.
def _executar_predicao(
    token: str,
    volume_total_recebido: float,
    ticket_medio_titulo: float,
    total_titulos_emitidos: int,
    maximo_dias_atraso_historico: float,
    uf_cliente: str,
    cidade_cliente: str,
) -> dict | None:
    """Chama /predicao/risco_credito com Bearer JWT e retorna o JSON da predição."""
    payload = {
        "volume_total_recebido": volume_total_recebido,
        "ticket_medio_titulo": ticket_medio_titulo,
        "total_titulos_emitidos": total_titulos_emitidos,
        "maximo_dias_atraso_historico": maximo_dias_atraso_historico,
        "uf_cliente": uf_cliente.upper(),
        "cidade_cliente": cidade_cliente,
    }
    try:
        resposta = requests.post(
            ENDPOINT_PREDICAO,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if resposta.status_code == 200:
            return resposta.json()
        if resposta.status_code == 503:
            st.error("O modelo de ML ainda não está carregado na API. "
                     "Execute o empacotamento da Fase 06 e reinicie a API.")
        elif resposta.status_code == 401:
            st.error("Token expirado ou inválido. Tente novamente.")
        else:
            st.error(f"Falha na predição (HTTP {resposta.status_code}).")
    except Exception as erro:
        st.error(f"Erro ao consultar a API de predição: {erro}")
    return None


# 'def _status_api(...)' verifica se o serviço de inferência está operacional.
def _status_api() -> bool:
    """Verifica /saude/prontidao e retorna True se o modelo estiver carregado."""
    try:
        resposta = requests.get(ENDPOINT_PRONTIDAO, timeout=8)
        if resposta.status_code == 200:
            return resposta.json().get("modelo_carregado_ram", False)
    except Exception:
        pass
    return False


def main() -> None:
    """Corpo principal da página de predição."""
    garantir_estado()
    st.caption("Inserção manual de dados de produção para predição/classificação")

    nome = st.session_state.dataset_nome

    # --- Problema/pergunta de negócio vinculada ao dataset ativo ---
    problema_info = None
    if nome:
        try:
            resumo = resumo_dataset(nome) or {}
            contrato = resumo.get("contrato")
            if contrato:
                problema_info = {
                    "id": contrato.get("id", "—"),
                    "nome": contrato.get("nome", "—"),
                    "tipo": contrato.get("tipo_tarefa", "—"),
                    "pergunta": contrato.get("pergunta_negocio"),
                }
        except Exception:
            pass

    if problema_info:
        with st.container(border=True):
            st.markdown("#### Problema de negócio treinado")
            colp1, colp2 = st.columns([3, 1])
            with colp1:
                st.markdown(
                    f"**{problema_info['nome']}** "
                    f"(`{problema_info['id']}`) — {problema_info['tipo']}"
                )
                if problema_info["pergunta"]:
                    st.caption(f"Pergunta: {problema_info['pergunta']}")
            with colp2:
                st.metric("Tarefa", problema_info["tipo"])
            st.divider()
    elif nome:
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.info(
                f"Nenhum problema de negócio vinculado ao dataset **{nome}**. "
                "Vá à página **Torneio** e vincule um problema antes de prever.",
                icon=":material/info:",
            )
        with col_btn:
            if st.button(
                "Ir para Torneio →",
                icon=":material/arrow_forward:",
                width="stretch",
            ):
                st.switch_page("app_pages/pagina_03_torneio.py")

    # Verifica se a API está no ar.
    pronta = _status_api()
    if not pronta:
        st.warning(
            "A API de inferência não respondeu ou o modelo não está carregado "
            "(verifique se o serviço está rodando em :8000). "
            "O formulário fica bloqueado até que a API esteja pronta.",
            icon=":material/wifi_off:",
        )

    # Formulário de entrada (bloqueado se a API não estiver pronta).
    with st.form("form_predicao_credito", clear_on_submit=False):
        st.markdown("#### Dados do cliente (entrada de produção)")

        col1, col2, col3 = st.columns(3)
        with col1:
            volume_total_recebido = st.number_input(
                "Volume total recebido (R$)",
                min_value=0.0,
                value=12500.50,
                step=100.0,
                help="Volume financeiro total já faturado/recebido do cliente.",
            )
            total_titulos_emitidos = st.number_input(
                "Total de títulos emitidos",
                min_value=1,
                value=18,
                step=1,
                help="Contagem acumulada de títulos de cobrança emitidos.",
            )
        with col2:
            ticket_medio_titulo = st.number_input(
                "Ticket médio por título (R$)",
                min_value=0.0,
                value=650.00,
                step=10.0,
                help="Valor médio de cada duplicata/título emitido.",
            )
            maximo_dias_atraso = st.number_input(
                "Máximo de dias de atraso (histórico)",
                min_value=0.0,
                value=5.0,
                step=1.0,
                help="Maior atraso já registrado em liquidações passadas.",
            )
        with col3:
            uf_cliente = st.text_input(
                "UF do cliente",
                value="SP",
                max_chars=2,
                help="Sigla do estado (ex: SP, MG).",
            )
            cidade_cliente = st.text_input(
                "Cidade do cliente",
                value="São Paulo",
                help="Nome do município cadastrado no ERP.",
            )

        predizer = st.form_submit_button(
            "Prever risco de crédito",
            type="primary",
            disabled=not pronta,
            width="stretch",
        )

    # Quando o form é submetido, o script reroda inteiro e 'predizer' fica True aqui.
    if predizer:
        with st.spinner("Autenticando e consultando a API de inferência..."):
            token = _obter_token()
            if token:
                resultado = _executar_predicao(
                    token=token,
                    volume_total_recebido=volume_total_recebido,
                    ticket_medio_titulo=ticket_medio_titulo,
                    total_titulos_emitidos=int(total_titulos_emitidos),
                    maximo_dias_atraso_historico=maximo_dias_atraso,
                    uf_cliente=uf_cliente,
                    cidade_cliente=cidade_cliente,
                )
                if resultado:
                    st.session_state["resultado_predicao"] = resultado
                st.rerun()

    # Exibe o resultado persistido no session_state (sobrevive ao rerun).
    if st.session_state.get("resultado_predicao"):
        st.divider()
        st.markdown("#### Resultado da predição")
        r = st.session_state["resultado_predicao"]

        colA, colB, colC = st.columns(3)
        with colA:
            classe = r.get("classe_predita")
            rotulo = r.get("decisao_rotulo", "—")
            cor_classe = "🔴" if classe == 1 else "🟢"
            st.metric("Decisão", f"{cor_classe} {rotulo}")
            st.caption(f"Classe binária: {classe} (0 = Em Dia, 1 = Risco)")
        with colB:
            prob = r.get("probabilidade_risco")
            st.metric(
                "Probabilidade de risco",
                f"{prob:.2%}" if prob is not None else "—",
            )
            st.caption(f"Limiar aplicado: {r.get('limiar_decisao_aplicado', '—')}")
        with colC:
            st.metric("Faixa de risco", r.get("faixa_risco", "—"))
            st.caption(f"Versão: {r.get('versao_modelo_producao', '—')}")

        st.markdown("**Ação recomendada:**")
        st.info(r.get("acao_recomendada", "—"))

        latencia = r.get("tempo_processamento_ms")
        st.caption(
            f"Latência de inferência: {latencia} ms · "
            f"API {API_URL}"
        )

        if st.button("Limpar resultado", icon=":material/delete:"):
            st.session_state["resultado_predicao"] = None
            st.rerun()


if __name__ == "__main__":
    main()
