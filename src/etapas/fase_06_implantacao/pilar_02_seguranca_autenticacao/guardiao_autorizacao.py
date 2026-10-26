"""Módulo de Interceptação e Guardião de Acesso HTTP Bearer (Pilar 2 - Fase 6).

Responsabilidade Única: Extrair o token do cabeçalho 'Authorization: Bearer <token>'
em rotas protegidas da API FastAPI, acionar o GerenciadorTokenJWT e levantar uma
exceção HTTP 401 Unauthorized imediata caso a credencial esteja ausente, corrompida ou
expirada[cite: 7].
"""

# 'from typing import ...' importa os tipos estáticos formais da biblioteca padrão do
# Python[cite: 7].
from typing import Any

# 'from fastapi import ...' traz os recursos de injeção de dependência e controle de
# erros web do framework FastAPI.
# - 'Depends': mecanismo que instrui o FastAPI a executar esta função validadora antes
# de liberar a rota principal.
# - 'HTTPException': classe oficial para emissão de respostas de erro padronizadas do
# protocolo HTTP.
# - 'status': catálogo numérico oficial com códigos padronizados do protocolo HTTP (ex:
# 401, 403, 500)[cite: 7].
from fastapi import Depends, HTTPException, status

# 'from fastapi.security import ...' importa os componentes visuais e normativos da
# documentação OpenAPI/Swagger.
# - 'HTTPAuthorizationCredentials': classe que empacota o tipo de esquema ('Bearer') e a
# string do token decifrada.
# - 'HTTPBearer': classe de segurança que injeta o botão verde 'Authorize' no Swagger em
# '/docs' para testes visuais[cite: 7].
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Importa o especialista criptográfico que acabamos de validar no módulo anterior[cite:
# 7, 17].
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.gerenciador_token_jwt import (  # noqa: E501
    GerenciadorTokenJWT,
)

# 'esquema_bearer = HTTPBearer(...)' instancia o contrato oficial de segurança do
# FastAPI:
# - 'scheme_name="BearerToken"': rótulo descritivo exibido na janela de autenticação do
# Swagger.
# - 'description': texto de orientação para desenvolvedores e integradores de sistemas
# externos.
# - 'auto_error=False': impede o FastAPI de disparar mensagens genéricas em inglês; nós
# assumimos o controle total da resposta[cite: 7].
esquema_bearer = HTTPBearer(
    scheme_name="BearerToken",
    description="Insira a sua credencial JWT emitida (Formato: Bearer <seu_token_jwt>)",
    auto_error=False,
)

# 'gerenciador_jwt_global' cria uma única instância do gestor criptográfico
# compartilhada por todas as requisições[cite: 7, 17].
gerenciador_jwt_global = GerenciadorTokenJWT()


# 'async def' define uma função assíncrona orientada a eventos para execução em alto
# desempenho pelo servidor Uvicorn[cite: 4, 7].
# 'verificar_autorizacao_portador' é o middleware de guarda que valida quem tem direito
# de chamar a inferência preditiva[cite: 7].
# 'credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer)': diz ao FastAPI
# para extrair o cabeçalho Authorization[cite: 7].
# '-> Dict[str, Any]': anotação que garante que a função devolve os dados autenticados
# do usuário em caso de sucesso[cite: 7].
async def verificar_autorizacao_portador(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
) -> dict[str, Any]:
    """Intercepta a requisição HTTP, valida a posse da credencial e homologa a
    inferência[cite: 7].

    Args:
        credenciais (HTTPAuthorizationCredentials): Credencial capturada no cabeçalho
        Authorization[cite: 7].

    Returns:
        Dict[str, Any]: Informações do usuário decodificadas e autorizadas[cite: 7].

    Raises:
        HTTPException: Erro HTTP 401 Unauthorized se a credencial for omitida, forjada
        ou estiver caducada[cite: 7].
    """
    # 'if credenciais is None' avalia se a requisição foi enviada sem o cabeçalho
    # 'Authorization'.
    # 'or not credenciais.credentials' valida se o cabeçalho foi enviado vazio ou com
    # espaços em branco[cite: 7].
    if credenciais is None or not credenciais.credentials:
        # 'raise HTTPException(...)' encerra a requisição na catraca, sem onerar o
        # processador nem o modelo de Machine Learning[cite: 7].
        # - 'status_code=status.HTTP_401_UNAUTHORIZED': código padronizado 401 para
        # ausência de credenciais válidas.
        # - 'detail': mensagem auditável em português explicando a razão do bloqueio
        # imediato.
        # - 'headers={"WWW-Authenticate": "Bearer"}': cabeçalho normativo da RFC 6750
        # indicando o padrão exigido[cite: 7].
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Acesso negado: Cabeçalho 'Authorization: Bearer <token>' ausente ou"
                "vazio."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 'str(credenciais.credentials)' extrai estritamente a sequência alfanumérica do
    # token recebido (sem o prefixo 'Bearer ')[cite: 7].
    token_bruto = str(credenciais.credentials)

    # Aciona o método do motor criptográfico para verificar o HMAC-SHA256 e a data de
    # expiração[cite: 7, 17].
    dados_usuario = gerenciador_jwt_global.validar_token_acesso(token_bruto)

    # 'if dados_usuario is None' avalia se a validação falhou (token forjado, adulterado
    # ou com prazo caducado)[cite: 7].
    if dados_usuario is None:
        # Rejeita sumariamente o acesso com código 401 e detalha a violação de segurança
        # do token[cite: 7].
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Credencial inválida: Token expirado, corrompido ou com assinatura"
                "forjada."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 'return dados_usuario' libera a requisição e entrega o dicionário com os dados do
    # usuário para os controladores da API[cite: 7].
    return dados_usuario
