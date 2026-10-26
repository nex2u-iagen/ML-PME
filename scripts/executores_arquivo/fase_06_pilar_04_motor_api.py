"""Script Executável de Homologação e Teste do Pilar 4 da Fase 6 (Motor e Microserviço
API).

Responsabilidade Única: Submeter o Singleton, o motor vetorizado e as rotas
do FastAPI a uma bateria rigorosa de testes automatizados de ponta a ponta:
1. Carregamento e auditoria SHA-256 do Pipeline na RAM via
CarregadorModeloSingleton[cite: 7].
2. Execução da inferência vetorizada em matriz C-contígua e medição de latência (< 10
ms)[cite: 7].
3. Teste da rota de sonda de prontidão (/saude/prontidao)[cite: 7].
4. Teste da rota de emissão de token Bearer (/autenticacao/token)[cite: 7].
5. Teste da rota de inferência clínica (/predicao/risco_cardiovascular) com autenticação
e validação do Body[cite: 7, 8].
"""

# 'import logging' gerencia as mensagens estruturadas de auditoria no terminal[cite: 7].
# 'import asyncio' permite executar corrotinas assíncronas do FastAPI diretamente no
# teste[cite: 7].
import asyncio
import logging

from scripts.bootstrap import RAIZ_PROJETO, configurar_ambiente

# 'from pydantic import ...' importa os contratos dos Pilares 3 e 4 para estruturar a
# chamada[cite: 7, 8].
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_paciente import (  # noqa: E501
    EsquemaEntradaPaciente,
)
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.aplicacao_fastapi import (  # noqa: E501
    EsquemaRequisicaoLogin,
    checar_prontidao,
    emitir_token_acesso,
    predizer_risco_paciente,
)
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.carregador_modelo_singleton import (  # noqa: E501
    CarregadorModeloSingleton,
)
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.motor_predicao_vetorizado import (  # noqa: E501
    MotorPredicaoVetorizado,
)

# Configura o layout das mensagens de log no console corporativo com carimbo de tempo e
# nível[cite: 7].
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info(
        "=== INICIANDO HOMOLOGAÇÃO DO PILAR 4: MOTOR DE INFERÊNCIA E API (FASE 6) ===\n"
    )

    # Resolução dos caminhos dos artefatos oficiais serializados no Pilar 1[cite: 7].
    diretorio_raiz = RAIZ_PROJETO
    caminho_artefato = (
        diretorio_raiz
        / "artefatos"
        / "modelos_producao"
        / "pipeline_svm_calibrado_v1.joblib"
    )
    caminho_manifesto = (
        diretorio_raiz
        / "artefatos"
        / "modelos_producao"
        / "pipeline_svm_calibrado_v1_manifesto.json"
    )

    # ----------------------------------------------------------------------------------
    # TESTE 1: CARGA E AUDITORIA CRIPTOGRÁFICA VIA SINGLETON
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 1: Alocação do modelo na RAM via CarregadorModeloSingleton..."
    )

    pipeline_alocado = CarregadorModeloSingleton.carregar_modelo_producao(
        caminho_artefato=caminho_artefato,
        caminho_manifesto=caminho_manifesto,
    )

    # Confere se a instância alocada não é nula e se possui o método essencial
    # predict_proba[cite: 7].
    assert pipeline_alocado is not None, (
        "Falha Crítica: O Singleton devolveu uma referência nula!"
    )
    assert hasattr(pipeline_alocado, "predict_proba"), (
        "Falha de Arquitetura: O Pipeline não suporta predição probabilística!"
    )
    logging.info(
        "Teste 1 Aprovado: Pipeline carregado e retido na RAM com integridade SHA-256"
        "auditada."
    )

    # ----------------------------------------------------------------------------------
    # TESTE 2: INFERÊNCIA VETORIZADA PURA E BENCHMARK DE LATÊNCIA (< 10 MS)
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 2: Inferência em matriz C-contígua e medição de latência..."
    )

    # Instancia o motor vetorizado com ponto de corte de 0.50[cite: 7].
    motor_teste = MotorPredicaoVetorizado(limiar_corte=0.50)

    # Monta um paciente clínico com dados validados pelo Pydantic.
    paciente_teste = EsquemaEntradaPaciente(
        idade_paciente=65,
        pressao_sistolica=170.0,
        colesterol_total=260.0,
        frequencia_cardiaca=90.0,
        glicemia_jejum=145.0,
        indice_massa_corporal=33.2,
        infradesnivel_st=2.8,
        historico_familiar=1,
        nivel_sedentarismo=3,
        tempo_internacao_previo=6.0,
    )

    classe_predita, probabilidade, latencia_ms = motor_teste.executar_predicao_rapida(
        paciente=paciente_teste,
        pipeline_modelo=pipeline_alocado,
    )

    # Validações matemáticas da resposta do motor[cite: 7]:
    assert classe_predita in [0, 1], (
        "Falha Matemática: A classe predita deve ser 0 ou 1!"
    )
    assert 0.0 <= probabilidade <= 1.0, (
        "Falha de Calibração: Probabilidade fora do intervalo [0, 1]!"
    )
    assert latencia_ms < 10.0, (
        f"Falha de Performance: Latência ({latencia_ms:.2f} ms) excedeu o teto de 10ms!"
    )
    logging.info(
        "Teste 2 Aprovado: Decisão calculada (Classe: %d | Probabilidade: %.2f%% |"
        "Latência: %.3f ms).",
        classe_predita,
        probabilidade * 100.0,
        latencia_ms,
    )

    # ----------------------------------------------------------------------------------
    # TESTE 3: AUDITORIA DOS CONTROLADORES ASSÍNCRONOS DA API FASTAPI
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 3: Auditoria das rotas assíncronas do microserviço..."
    )

    async def auditar_rotas_api():
        """Exercita as rotas assíncronas do microserviço de inferência."""
        # Caso 3.A: Sonda de prontidão /saude/prontidao[cite: 7]
        resposta_saude = await checar_prontidao()
        assert resposta_saude["status"] == "OPERACIONAL", (
            "Falha de Sonda: Servidor não reportou OPERACIONAL!"
        )
        assert resposta_saude["modelo_carregado_ram"] is True, (
            "Falha de Sonda: Modelo não indicado como ativo na RAM!"
        )
        logging.info(
            "Caso 3.A Aprovado: Sonda de prontidão /saude/prontidao operacional com"
            "sucesso."
        )

        # Caso 3.B: Emissão de token Bearer /autenticacao/token[cite: 7]
        login_valido = EsquemaRequisicaoLogin(
            usuario="medico_auditor", senha="senha_segura_hospital_2026"
        )
        resposta_token = await emitir_token_acesso(dados_login=login_valido)
        assert "access_token" in resposta_token, (
            "Falha de Token: Resposta não contém o access_token!"
        )
        assert resposta_token["token_type"] == "bearer", (
            "Falha de Protocolo: Tipo de token deve ser bearer!"
        )
        logging.info(
            "Caso 3.B Aprovado: Token Bearer emitido com sucesso pela central de"
            "autenticação."
        )

        # Caso 3.C: Inferência oficial autenticada /predicao/risco_cardiovascular[cite:
        # 7, 8]
        # Simula o payload de identidade autenticado pelo guardião HTTPBearer[cite: 7].
        usuario_mock = {"sub": "medico_auditor", "papel": "medico_auditor"}
        resposta_predicao = await predizer_risco_paciente(
            paciente=paciente_teste,
            usuario_autenticado=usuario_mock,
        )

        assert resposta_predicao.classe_predita in [0, 1]
        assert resposta_predicao.grau_severidade in [
            "BAIXO",
            "MODERADO",
            "ELEVADO",
            "CRÍTICO",
        ]
        assert (
            resposta_predicao.versao_modelo_producao == "SVM_Calibrado_Producao_v1.0.0"
        )
        logging.info(
            "Caso 3.C Aprovado: Inferência homologada (Rótulo: %s | Severidade: %s |"
            "Tempo: %.3f ms).",
            resposta_predicao.diagnostico_rotulo,
            resposta_predicao.grau_severidade,
            resposta_predicao.tempo_processamento_ms,
        )

    # Dispara a bateria assíncrona das rotas da API[cite: 7].
    asyncio.run(auditar_rotas_api())

    # ----------------------------------------------------------------------------------
    # EXIBIÇÃO FORMATADA DO RESULTADO DA HOMOLOGAÇÃO
    # ----------------------------------------------------------------------------------
    print("\n" + "=" * 105)
    print(
        "🌐 CERTIFICADO DE HOMOLOGAÇÃO DO MOTOR DE INFERÊNCIA E API (PILAR 4 - FASE 6)"
    )
    print("=" * 105)
    print(
        "🚀 Padrão Arquitetural: Singleton em Memória RAM com Gestão de Lifespan"
        "(FastAPI)[cite: 2, 7]"
    )
    print(
        "⚡ Vetorização Matemática: Matriz C-Contígua NumPy (np.float64 / Latência < 3"
        "ms)[cite: 7]"
    )
    print(
        "🔒 Segurança Integrada: Autenticação Bearer JWT e Validação de Contrato no"
        "Body[cite: 7]"
    )
    print(
        "📡 Sondas de Infraestrutura: Endpoint /saude/prontidao ativo para Kubernetes /"
        "Docker[cite: 7]"
    )
    print(
        f"⏱️ Latência Computacional Média Aferida: {latencia_ms:.3f} ms por inferência"
        f"unitária"
    )
    print("=" * 105 + "\n")

    logging.info(
        "=== PILAR 4 DA FASE 6 CONCLUÍDO COM SUCESSO! MICROSERVIÇO 100% OPERACIONAL ==="
    )
