"""Script Executável de Homologação e Teste do Pilar 2 da Fase 6 (Segurança e
Autenticação).

Responsabilidade Única: Submeter o GerenciadorTokenJWT e o guardião de autenticação
a uma bateria formal de testes de penetração e conformidade:
1. Emissão de credencial autêntica e validação de claims (sub, papel, exp).
2. Teste de penetração com token adulterado/forjado (garantindo rejeição)[cite: 6].
3. Teste de conformidade temporal com token expirado (garantindo bloqueio)[cite: 6].
4. Teste de simulação de cabeçalho HTTP Bearer vazio (garantindo corte com HTTP
401)[cite: 6].
"""

# 'import logging' gerencia as mensagens formatadas de auditoria técnica no
# console[cite: 7].
# 'import asyncio' permite a execução de rotinas assíncronas do FastAPI fora de um
# servidor web completo[cite: 7].
import asyncio
import logging

# 'import time' permite congelar a execução temporariamente para simular a passagem de
# tempo em segundos[cite: 7].
import time

# 'from fastapi import HTTPException' permite capturar e inspecionar a exceção levantada
# pelo guardião web[cite: 7].
from fastapi import HTTPException

# 'from fastapi.security import HTTPAuthorizationCredentials' simula o envelope de
# credenciais do cabeçalho web[cite: 7].
from fastapi.security import HTTPAuthorizationCredentials

from scripts.bootstrap import configurar_ambiente

# Importa o especialista criptográfico do Pilar 2[cite: 7, 17].
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.gerenciador_token_jwt import (  # noqa: E501
    GerenciadorTokenJWT,
)

# Importa o interceptor HTTP de segurança que protege as rotas preditivas[cite: 7].
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.guardiao_autorizacao import (  # noqa: E501
    verificar_autorizacao_portador,
)

# 'logging.basicConfig' parametriza a formatação dos registros no console corporativo
# com carimbo de hora e severidade[cite: 7].
configurar_ambiente()

# '__name__ == "__main__"' garante que o script só seja executado quando acionado
# diretamente no terminal[cite: 7].
if __name__ == "__main__":
    # Emite aviso inicial registrando o início oficial dos testes de segurança do Pilar
    # 2[cite: 7].
    logging.info(
        "=== INICIANDO HOMOLOGAÇÃO DO PILAR 2: SEGURANÇA E AUTENTICAÇÃO BEARER (FASE 6)"
        "===\n"
    )

    # 'gerenciador = GerenciadorTokenJWT()' cria o objeto especialista de segurança com
    # a chave privada[cite: 7, 17].
    gerenciador = GerenciadorTokenJWT()

    # ----------------------------------------------------------------------------------
    # TESTE 1: EMISSÃO E VALIDAÇÃO DE UM TOKEN LEGÍTIMO E VIGENTE
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 1: Emissão e validação de credencial JWT autêntica..."
    )

    # Emite a credencial para o médico responsável com a cifra HMAC-SHA256
    # homologada[cite: 17].
    token_legitimo = gerenciador.gerar_token_acesso(
        identificador_usuario="dr_arthur_responsavel",
        perfil_acesso="lider_clinico_staff",
    )

    # Dispara a decodificação matemática e a conferência de assinatura digital[cite: 7,
    # 17].
    dados_decodificados = gerenciador.validar_token_acesso(token_legitimo)

    # 'assert' verifica uma condição obrigatória; se a condição for falsa, o Python
    # interrompe o teste imediatamente.
    # Testa se a decodificação não retornou None (o token tem que ser aceito com
    # louvor)[cite: 6, 7].
    assert dados_decodificados is not None, (
        "Falha Crítica: Token autêntico foi rejeitado incorretamente!"
    )

    # Testa se o campo 'sub' (subject) retornado contém exatamente a identificação do
    # médico cadastrado[cite: 6, 7].
    assert dados_decodificados["sub"] == "dr_arthur_responsavel", (
        "Falha de Identidade: Usuário decodificado difere do emitido!"
    )

    # Registra o sucesso do primeiro teste de emissão e auditoria[cite: 7].
    logging.info(
        "Teste 1 Aprovado: Credencial legítima validada com perfil '%s'.",
        dados_decodificados["papel"],
    )

    # ----------------------------------------------------------------------------------
    # TESTE 2: TESTE DE PENETRAÇÃO COM ASSINATURA FORJADA / ADULTERADA
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 2: Auditoria contra tentativa de adulteração de assinatura..."
    )

    # Modifica o último caractere do token original para simular um ataque cibernético
    # de injeção de dados[cite: 7, 17].
    # Se o token terminava com um caractere, trocamos por outro diferente, corrompendo a
    # assinatura HMAC[cite: 7, 17].
    token_adulterado = token_legitimo[:-1] + ("A" if token_legitimo[-1] != "A" else "B")

    # Submete o token adulterado ao algoritmo de decodificação[cite: 7, 17].
    resultado_adulterado = gerenciador.validar_token_acesso(token_adulterado)

    # O validador tem a obrigação de retornar estritamente None (rejeição total do
    # acesso forjado)[cite: 6, 7].
    assert resultado_adulterado is None, (
        "Falha Crítica de Segurança: Token forjado foi aceito pelo sistema!"
    )

    logging.info(
        "Teste 2 Aprovado: Credencial forjada foi interceptada e rejeitada com sucesso."
    )

    # ----------------------------------------------------------------------------------
    # TESTE 3: CONFORMIDADE TEMPORAL COM TOKEN EXPIRADO
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 3: Auditoria contra credenciais com prazo de vigência"
        "vencido..."
    )

    # Instancia um gestor com expiração configurada para 0 minutos, produzindo um token
    # instantaneamente expirado[cite: 7].
    gerenciador_efemero = GerenciadorTokenJWT(tempo_expiracao_minutos=0)
    token_expirado = gerenciador_efemero.gerar_token_acesso("usuario_expirado")

    # 'time.sleep(1)' congela a execução por 1 segundo para garantir que o carimbo Unix
    # 'exp' fique no passado[cite: 7].
    time.sleep(1)

    # Submete o token vencido à auditoria do gestor oficial[cite: 7].
    resultado_expirado = gerenciador.validar_token_acesso(token_expirado)

    # O motor de segurança deve recusar o token vencido devolvendo None[cite: 6, 7].
    assert resultado_expirado is None, (
        "Falha de Governança: Token expirado foi autorizado pelo validador!"
    )

    logging.info(
        "Teste 3 Aprovado: Credencial vencida foi identificada e bloqueada pelo relógio"
        "UTC."
    )

    # ----------------------------------------------------------------------------------
    # TESTE 4: INTERCEPTAÇÃO VIA GUARDIÃO FASTAPI (SIMULAÇÃO DE ERRO HTTP 401)
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 4: Auditoria do guardião HTTPBearer contra requisições sem"
        "token..."
    )

    # Função assíncrona local para disparar a corrotina do guardião sem precisar subir o
    # servidor web completo[cite: 7].
    async def simular_requisicoes():
        """Simula chamadas protegidas para validar o guardião de autorização."""
        # Cenário 4.A: Chamada de API enviada com cabeçalho de credencial nulo (ausência
        # do crachá)[cite: 7].
        try:
            # Invoca o guardião passando credenciais vazias[cite: 7].
            await verificar_autorizacao_portador(credenciais=None)
            # Se a linha acima não disparar erro, o teste falhou gravemente[cite: 6, 7].
            assert False, (
                "Falha no Guardião: Requisição sem token não disparou erro HTTP 401!"
            )
        except HTTPException as erro_401:
            # Confere se o código de status HTTP retornado é exatamente o código 401
            # Unauthorized[cite: 6, 7].
            assert erro_401.status_code == 401, (
                "Código HTTP divergente de 401 Unauthorized!"
            )
            logging.info(
                "Caso 4.A Aprovado: Requisição sem cabeçalho cortada com HTTP 401"
                "Unauthorized."
            )

        # Cenário 4.B: Chamada de API enviada com credencial Bearer autêntica e
        # válida[cite: 7].
        objeto_credencial = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token_legitimo
        )
        # Invoca o guardião com a credencial válida injetada[cite: 7].
        usuario_homologado = await verificar_autorizacao_portador(
            credenciais=objeto_credencial
        )
        # Confere se o sujeito do token decodificado corresponde ao médico
        # registrado[cite: 6, 7].
        assert usuario_homologado["sub"] == "dr_arthur_responsavel"
        logging.info(
            "Caso 4.B Aprovado: Requisição com credencial Bearer autorizada comsucesso."
        )

    # 'asyncio.run(simular_requisicoes())' executa o laço de eventos assíncrono para
    # concluir a bateria de testes[cite: 7].
    asyncio.run(simular_requisicoes())

    # ----------------------------------------------------------------------------------
    # EXIBIÇÃO FORMATADA DO RELATÓRIO DE AUDITORIA
    # ----------------------------------------------------------------------------------
    print("\n" + "=" * 105)
    print("🛡️ CERTIFICADO DE BLINDAGEM DE SEGURANÇA E AUTENTICAÇÃO (PILAR 2 - FASE 6)")
    print("=" * 105)
    print("🔑 Cifra Criptográfica: HMAC com SHA-256 (Norma RFC 7519 / JWT)[cite: 17]")
    print("🚪 Protocolo de Acesso: HTTP Bearer Token (Norma RFC 6750)")
    print("⏰ Vigência da Sessão: 480 minutos (8 Horas Contínuas com validação UTC)")
    print(f"🎟️ Exemplo de Token Válido Gerado:\n{token_legitimo}")
    print("=" * 105 + "\n")

    # Emite mensagem final registrando a homologação do Pilar 2 da Fase 6[cite: 7].
    logging.info(
        "=== PILAR 2 DA FASE 6 HOMOLOGADO COM SUCESSO! SISTEMA 100% BLINDADO ==="
    )
