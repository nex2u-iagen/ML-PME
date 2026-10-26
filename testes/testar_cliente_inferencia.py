"""Script Cliente de Integração e Teste em Produção da API de Inferência (Fase 6).

Responsabilidade Única: Simular um sistema hospitalar externo consumindo o microserviço:
1. Conecta-se à rota pública '/autenticacao/token' via POST e extrai o Bearer Token
JWT[cite: 7, 10].
2. Monta o payload JSON com as 10 features clínicas validadas pelo Pydantic V2[cite: 7,
8].
3. Dispara a inferência em '/predicao/risco_cardiovascular' e exibe o laudo pericial.
"""

# 'import json' manipula e formata as mensagens de resposta da API no padrão
# legível[cite: 4].
import json

# 'import time' cronometra o tempo de resposta da rede de ponta a ponta (Round-Trip
# Time).
import time
import urllib.error

# 'import urllib.request' e 'import urllib.error' realizam chamadas HTTP nativas sem
# exigir novas bibliotecas[cite: 4].
import urllib.request

# '__name__ == "__main__"' garante que o teste só seja disparado quando invocado
# diretamente[cite: 7].
if __name__ == "__main__":
    print("\n" + "=" * 95)
    print("🏥 SIMULADOR DE CLIENTE HOSPITALAR — TESTE DE INFERÊNCIA EM TEMPO REAL")
    print("=" * 95)

    URL_BASE = "http://127.0.0.1:8000"

    # ----------------------------------------------------------------------------------
    # ETAPA 1: OBTENÇÃO DA CREDENCIAL DE ACESSO (BEARER TOKEN JWT)
    # ----------------------------------------------------------------------------------
    print("1. Solicitando credencial eletrônica de plantonista na portaria central...")

    # Dados de autenticação corporativa enviados no corpo da requisição POST[cite: 7].
    dados_login = json.dumps(
        {"usuario": "dr_arthur_plantonista", "senha": "senha_segura_hospital_2026"}
    ).encode("utf-8")

    # Monta a requisição HTTP POST para emissão da chave de acesso[cite: 7, 10].
    requisicao_token = urllib.request.Request(
        url=f"{URL_BASE}/autenticacao/token",
        data=dados_login,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        # Envia a requisição pela rede e extrai o token JWT da resposta[cite: 7].
        with urllib.request.urlopen(requisicao_token) as resposta_login:
            corpo_login = json.loads(resposta_login.read().decode("utf-8"))
            token_jwt = corpo_login["access_token"]
            print(
                f"✅ Token Bearer JWT obtido com sucesso! Validade:"
                f"{corpo_login['expira_em_minutos']} minutos."
            )
    except urllib.error.URLError as erro_conexao:
        print(f"❌ Erro de conexão com o servidor na porta 8000: {erro_conexao}")
        print(
            "Certifique-se de que o comando 'uv run python -m"
            " scripts.executores_projeto.servir_api' está rodando!"
        )
        exit(1)

    # ----------------------------------------------------------------------------------
    # ETAPA 2: ENVIO DAS 10 FEATURES CLÍNICAS NO BODY COM AUTENTICAÇÃO NO HEADER
    # ----------------------------------------------------------------------------------
    print(
        "\n2. Encaminhando dados de paciente crítico para triagem preditiva"
        "cardiovascular..."
    )

    # As 10 variáveis preditoras homologadas rigorosamente formatadas em JSON[cite: 7,
    # 8]:
    paciente_emergencia = {
        "idade_paciente": 67,
        "pressao_sistolica": 175.0,
        "colesterol_total": 290.0,
        "frequencia_cardiaca": 95.0,
        "glicemia_jejum": 160.0,
        "indice_massa_corporal": 34.8,
        "infradesnivel_st": 3.2,
        "historico_familiar": 1,
        "nivel_sedentarismo": 4,
        "tempo_internacao_previo": 12.0,
    }

    # Codifica o dicionário clínico em bytes UTF-8 para transmissão de rede[cite: 4].
    corpo_paciente = json.dumps(paciente_emergencia).encode("utf-8")

    # Monta a requisição HTTP protegida injetando o Bearer Token no cabeçalho
    # Authorization[cite: 7].
    requisicao_inferencia = urllib.request.Request(
        url=f"{URL_BASE}/predicao/risco_cardiovascular",
        data=corpo_paciente,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token_jwt}",
        },
        method="POST",
    )

    # Cronometra o tempo de resposta da rede de ponta a ponta[cite: 7].
    tempo_inicio_rede = time.perf_counter()

    # Dispara a chamada de inferência contra o microserviço FastAPI[cite: 7].
    with urllib.request.urlopen(requisicao_inferencia) as resposta_predicao:
        tempo_total_rede_ms = (time.perf_counter() - tempo_inicio_rede) * 1000.0
        resultado_clinico = json.loads(resposta_predicao.read().decode("utf-8"))

    # ----------------------------------------------------------------------------------
    # ETAPA 3: EXIBIÇÃO FORMATADA DO LAUDO PERICIAL RECEBIDO
    # ----------------------------------------------------------------------------------
    print("=" * 95)
    print("📋 LAUDO DE DECISÃO CLÍNICA EMITIDO PELA INTELIGÊNCIA ARTIFICIAL (FASE 6)")
    print("=" * 95)
    print(
        f"🎯 Decisão da Máquina (Classe Binária): {resultado_clinico['classe_predita']}"
    )
    print(f"🏷️ Diagnóstico Formal: {resultado_clinico['diagnostico_rotulo']}")
    print(
        f"📈 Probabilidade de Risco Calibrada:"
        f"{resultado_clinico['probabilidade_risco'] * 100.0:.2f}%"
    )
    print(
        f"⚖️ Limiar de Decisão Homologado:"
        f"{resultado_clinico['limiar_decisao_aplicado']:.2f}"
    )
    print(f"🚨 Grau de Severidade Hospitalar: {resultado_clinico['grau_severidade']}")
    print(
        f"📦 Versão do Modelo Ativo na RAM:"
        f"{resultado_clinico['versao_modelo_producao']}"
    )
    print(
        f"⚡ Tempo de Inferência Pura do Modelo:"
        f"{resultado_clinico['tempo_processamento_ms']:.3f} ms"
    )
    print(f"🌐 Tempo de Resposta da Rede (Round-Trip): {tempo_total_rede_ms:.3f} ms")
    print("=" * 95 + "\n")
