"""Aplicação Web de Produção do Microserviço REST de Inferência Clínica (Pilar 4 - Fase
6).

Responsabilidade Única: Expor os pontos de terminação (endpoints) HTTP com documentação
interativa Swagger OpenAPI, gerir o ciclo de vida da aplicação através de contexto
assíncrono
(Lifespan), redirecionar acessos da raiz para a documentação técnica, autenticar
requisições
via credencial Bearer Token e entregar a resposta preditiva em frações de
milissegundo[cite: 10, 13].
"""

# 'from contextlib' acede ao módulo da biblioteca padrão para manipulação de
# gerenciadores de contexto.
# 'asynccontextmanager' é o decorador oficial que permite criar funções de ciclo de vida
# assíncronas (Lifespan).
# Este padrão substitui os eventos legados '@app.on_event("startup")' e
# '@app.on_event("shutdown")'.
from contextlib import asynccontextmanager

# 'from pathlib' acede à biblioteca padrão de manipulação de sistemas de ficheiros
# orientada a objetos.
# 'Path' é a classe que representa caminhos de ficheiros e pastas de forma agnóstica ao
# sistema operativo (Linux/Windows)[cite: 5].
from pathlib import Path

# 'from typing' acede ao sistema de anotação de tipos estáticos do Python[cite: 4].
# 'Any' declara que o tipo da variável pode assumir qualquer natureza estrutural[cite:
# 4].
# 'Dict' documenta formalmente estruturas do tipo chave-valor (dicionários
# associativos)[cite: 5].
from typing import Any

# 'from fastapi' carrega os componentes estruturais do ecossistema web assíncrono de
# alto desempenho[cite: 5].
# 'Depends' ativa o motor de injeção de dependências do FastAPI para validar requisitos
# antes da rota principal.
# 'FastAPI' é a classe central que instancia a aplicação web, coordena roteadores e
# compila o OpenAPI.
# 'HTTPException' é a classe de exceção controlada usada para devolver respostas de erro
# padronizadas do protocolo HTTP.
# 'status' é o catálogo de constantes numéricas oficiais do protocolo HTTP (ex:
# HTTP_401_UNAUTHORIZED, HTTP_503).
from fastapi import Depends, FastAPI, HTTPException, status

# 'from fastapi.responses' acede aos tipos de resposta HTTP nativos do framework.
# 'RedirectResponse' permite enviar uma resposta de redirecionamento de URL (HTTP 307)
# para o navegador web.
from fastapi.responses import RedirectResponse

# 'from pydantic' carrega a classe base de validação e modelagem de dados da biblioteca
# Pydantic V2.
# 'BaseModel' é herdada para criar contratos de dados auditáveis e auto-validados para
# cargas úteis JSON.
from pydantic import BaseModel

# Importa o gestor de criptografia e emissão de tokens JWT do Pilar 2 de segurança.
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.gerenciador_token_jwt import (  # noqa: E501
    GerenciadorTokenJWT,
)

# Importa o interceptor HTTPBearer homologado no Pilar 2 para barramento de requisições
# sem crachá digital.
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.guardiao_autorizacao import (  # noqa: E501
    verificar_autorizacao_portador,
)

# Importa o contrato formal de dados com as 10 variáveis preditoras clínicas homologadas
# no Pilar 3.
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_paciente import (  # noqa: E501
    EsquemaEntradaPaciente,
)

# Importa o contrato oficial de saída da predição com os campos de decisão e latência do
# Pilar 3.
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_resposta_predicao import (  # noqa: E501
    EsquemaRespostaPredicao,
)

# Importa o gestor de persistência em memória RAM Singleton do próprio Pilar 4.
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.carregador_modelo_singleton import (  # noqa: E501
    CarregadorModeloSingleton,
)

# Importa o motor de cálculo matricial vetorizado em padrão C-contíguo do Pilar 4[cite:
# 5].
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.motor_predicao_vetorizado import (  # noqa: E501
    MotorPredicaoVetorizado,
)

# --------------------------------------------------------------------------------------
# RESOLUÇÃO ANCORADA DA RAIZ DO REPOSITÓRIO (SISTEMA DE FICHEIROS DO SERVIDOR)
# --------------------------------------------------------------------------------------
# '__file__' extrai a localização física absoluta do ficheiro de código atual
# (aplicacao_fastapi.py)[cite: 3].
# '.resolve()' converte o caminho eliminando eventuais ligações simbólicas no
# Linux[cite: 5].
# '.parents[n]' sobe 'n' degraus na hierarquia de pastas do projeto:
#   - parents[0] = pilar_04_motor_inferencia_api/ (pasta local)
#   - parents[1] = fase_06_implantacao/ (pasta da fase)
#   - parents[2] = etapas/ (pasta de etapas)
#   - parents[3] = src/ (pasta de código-fonte)[cite: 5]
# - parents[4] = projeto_ml/ (a raiz absoluta do repositório onde reside a pasta
# 'artefatos/')[cite: 5]
DIRETORIO_RAIZ = Path(__file__).resolve().parents[4]

# Monta a rota física absoluta até ao binário serializado (.joblib) do Pipeline
# campeão[cite: 3].
CAMINHO_ARTEFATO_BINARIO = (
    DIRETORIO_RAIZ
    / "artefatos"
    / "modelos_producao"
    / "pipeline_svm_calibrado_v1.joblib"
)

# Monta a rota física absoluta até à ficha técnica de governação (.json) com o hash
# criptográfico[cite: 3].
CAMINHO_MANIFESTO_JSON = (
    DIRETORIO_RAIZ
    / "artefatos"
    / "modelos_producao"
    / "pipeline_svm_calibrado_v1_manifesto.json"
)

# Instancia o motor de inferência matemático, injetando o ponto de corte ótimo de
# probabilidade (0.50).
motor_predicao_ativo = MotorPredicaoVetorizado(limiar_corte=0.50)


# --------------------------------------------------------------------------------------
# GESTOR DE CICLO DE VIDA ASSÍNCRONO DA APLICAÇÃO (LIFESPAN MANAGEMENT)
# --------------------------------------------------------------------------------------
# '@asynccontextmanager' decora a função geradora assíncrona para atuar como gestor de
# contexto de rede.
# 'aplicacao: FastAPI': parâmetro tipado que recebe a instância do servidor web em
# inicialização.
@asynccontextmanager
async def gerenciar_ciclo_vida_servico(aplicacao: FastAPI):
    """Gere a carga única do modelo na memória RAM na partida e liberta recursos no
    desligamento.
    """
    # Bloco executado exclusivamente durante o arranque da aplicação web (Startup):
    print(
        "🚀 [LIFESPAN] Inicializando microserviço: auditando integridade e aquecendo"
        "modelo na RAM..."
    )

    # Aciona o Singleton para auditar o hash SHA-256 e alocar o pipeline na memória RAM
    # partilhada.
    CarregadorModeloSingleton.carregar_modelo_producao(
        caminho_artefato=CAMINHO_ARTEFATO_BINARIO,
        caminho_manifesto=CAMINHO_MANIFESTO_JSON,
    )
    print(
        "✅ [LIFESPAN] Pipeline de Machine Learning ativo na memória RAM. Servidor"
        "pronto para atender."
    )

    # 'yield' transfere o controlo do fluxo: o servidor começa a aceitar conexões e
    # requisições HTTP externas.
    yield

    # Bloco executado durante o encerramento gracioso do processo do servidor
    # (Shutdown):
    print(
        "🛑 [LIFESPAN] Encerrando servidor: liberando recursos de memória"
        "compartilhada..."
    )
    CarregadorModeloSingleton.liberar_memoria()


# --------------------------------------------------------------------------------------
# INSTANCIAÇÃO DA APLICAÇÃO FASTAPI COM METADADOS SWAGGER OPENAPI
# --------------------------------------------------------------------------------------
# 'FastAPI(...)' cria o núcleo da aplicação web, compilando os esquemas para a norma
# OpenAPI 3.1:
aplicacao_api = FastAPI(
    # 'title': nome corporativo exibido no cabeçalho do Swagger em '/docs'.
    title="API de Predição de Risco Cardiovascular — Fase 6 (CRISP-DM)",
    # 'description': texto de governação explicativa com instruções de acesso e
    # arquitetura técnica[cite: 3].
    description=(
        "Microserviço corporativo de alta disponibilidade e baixa latência para"
        "inferência clínica em tempo real.\n\n"
        "- **Autenticação:** Exige cabeçalho `Authorization: Bearer <token_jwt>` em"
        "rotas de predição.\n"
        "- **Entrada de Dados:** Recebe os 10 atributos clínicos exatos via JSON no"
        "Body validados por Pydantic V2[cite: 3].\n"
        "- **Governança:** Pipeline auditado com assinatura criptográfica SHA-256 e"
        "homologado na Fase 5."
    ),
    # 'version': identificador semântico de release do serviço web.
    version="1.0.0",
    # 'lifespan': conecta a rotina assíncrona de inicialização de memória à aplicação
    # web.
    lifespan=gerenciar_ciclo_vida_servico,
)


# 'class EsquemaRequisicaoLogin' define o contrato de dados simples para a rota pública
# de login e emissão de tokens.
class EsquemaRequisicaoLogin(BaseModel):
    """Contrato simples para autenticação e emissão de credenciais temporárias de
    portador.
    """

    # 'usuario: str' define o campo do identificador com um valor padrão para facilitar
    # testes no Swagger.
    usuario: str = "medico_auditor"
    # 'senha: str' define o campo de chave secreta com a senha padrão homologada na
    # documentação.
    senha: str = "senha_segura_hospital_2026"


# --------------------------------------------------------------------------------------
# 0. ROTA RAIZ: REDIRECIONAMENTO AMIGÁVEL PARA A DOCUMENTAÇÃO INTERATIVA (/docs)
# --------------------------------------------------------------------------------------
# '@aplicacao_api.get("/")' captura requisições de leitura na raiz do domínio para
# prevenir erros 404[cite: 5].
@aplicacao_api.get(
    "/",
    tags=["Navegação & Boas-Vindas"],
    summary=(
        "Redireciona a raiz da API diretamente para a documentação interativa Swagger"
        "OpenAPI"
    ),
)
async def rota_raiz():
    """Redireciona o utilizador do navegador automaticamente para o painel interativo
    do Swagger.
    """
    # Retorna um redirecionamento HTTP 307 (Temporary Redirect) apontando para a
    # interface gráfica '/docs'.
    return RedirectResponse(url="/docs")


# --------------------------------------------------------------------------------------
# 1. ROTA PÚBLICA: EMISSÃO DE TOKEN BEARER JWT (AUTENTICAÇÃO DE ACESSO)
# --------------------------------------------------------------------------------------
# '@aplicacao_api.post(...)' declara um endpoint que aceita requisições HTTP do tipo
# POST.
@aplicacao_api.post(
    "/autenticacao/token",
    tags=["Autenticação & Segurança"],
    summary=(
        "Emite uma credencial Bearer Token JWT para acesso às rotas protegidas de"
        "inferência"
    ),
)
async def emitir_token_acesso(dados_login: EsquemaRequisicaoLogin):
    """Autentica as credenciais institucionais e devolve um token assinado com
    validade de 8 horas.
    """
    # Validação didática de demonstração das credenciais de acesso do profissional
    # clínico.
    if dados_login.senha != "senha_segura_hospital_2026":
        # Se a senha informada for incorreta, levanta erro HTTP 401 Unauthorized
        # imediato.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Credenciais incorretas: Usuário ou senha não conferem no registro"
                "hospitalar."
            ),
        )

    # Instancia o especialista criptográfico do Pilar 2 para geração da assinatura
    # HMAC-SHA256.
    gerenciador_jwt = GerenciadorTokenJWT()
    # Emite a credencial formatada com data de emissão e expiração calculadas em relógio
    # UTC.
    token = gerenciador_jwt.gerar_token_acesso(
        identificador_usuario=dados_login.usuario
    )

    # Devolve o dicionário JSON em conformidade com o padrão internacional OAuth2 /
    # Bearer RFC 6750.
    return {
        "access_token": token,
        "token_type": "bearer",
        "expira_em_minutos": 480,
    }


# --------------------------------------------------------------------------------------
# 2. ROTA DE AUDITORIA DE INFRAESTRUTURA: SONDA DE PRONTIDÃO (READINESS HEALTH PROBE)
# --------------------------------------------------------------------------------------
# '@aplicacao_api.get(...)' disponibiliza uma rota leve consultada periodicamente por
# orquestradores de contentores.
@aplicacao_api.get(
    "/saude/prontidao",
    tags=["Monitoramento & Infraestrutura"],
    summary=(
        "Verifica se o microserviço está operacional e com o modelo preditivo alocado"
        "na memória RAM"
    ),
)
async def checar_prontidao():
    """Sonda utilizada por balanceadores de carga para autorizar o envio de tráfego
    de rede.
    """
    # Consulta o atributo de classe estático do Singleton sem realizar leituras no disco
    # rígido.
    modelo_ativo = CarregadorModeloSingleton.obter_pipeline_ativo() is not None

    # Devolve o parecer operacional com código de estado 200 OK.
    return {
        "status": "OPERACIONAL" if modelo_ativo else "INDISPONIVEL",
        "modelo_carregado_ram": modelo_ativo,
        "versao": "SVM_Calibrado_Producao_v1.0.0",
    }


# --------------------------------------------------------------------------------------
# 3. ROTA DE INFERÊNCIA CLÍNICA PROTEGIDA (CORPO PYDANTIC E CABEÇALHO BEARER)
# --------------------------------------------------------------------------------------
# 'response_model=EsquemaRespostaPredicao': força o FastAPI a validar a saída segundo o
# contrato do Pilar 3.
@aplicacao_api.post(
    "/predicao/risco_cardiovascular",
    response_model=EsquemaRespostaPredicao,
    tags=["Inferência Preditiva"],
    summary=(
        "Executa a inferência clínica com validação de contrato no Body e autenticação"
        "Bearer[cite: 3]"
    ),
)
async def predizer_risco_paciente(
    # 'paciente: EsquemaEntradaPaciente': o FastAPI extrai o JSON do Body e executa as
    # validações do Pydantic[cite: 3].
    paciente: EsquemaEntradaPaciente,
    # 'usuario_autenticado = Depends(verificar_autorizacao_portador)': executa a catraca
    # de segurança Bearer.
    usuario_autenticado: dict[str, Any] = Depends(verificar_autorizacao_portador),
):
    """Recebe as 10 variáveis no Body, audita o Bearer token e emite o parecer de
    risco cardiovascular[cite: 3].
    """
    # Acede ao modelo alocado na memória RAM partilhada sem penalidade de I/O de disco.
    pipeline_ativo = CarregadorModeloSingleton.obter_pipeline_ativo()

    # Checagem defensiva: se o servidor estiver em estado transitório sem o modelo,
    # devolve erro 503.
    if pipeline_ativo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Serviço indisponível: O Pipeline de Machine Learning ainda não foi"
                "carregado na memória."
            ),
        )

    # Dispara o motor de predição vetorizado que executa a matriz em linguagem C e
    # cronometra a latência[cite: 5].
    classe_final, probabilidade_risco, latencia_ms = (
        motor_predicao_ativo.executar_predicao_rapida(
            paciente=paciente,
            pipeline_modelo=pipeline_ativo,
        )
    )

    # Mapeia a decisão binária discreta para um rótulo em português legível por seres
    # humanos:
    rotulo = (
        "ALTO_RISCO_CARDIOVASCULAR" if classe_final == 1 else "BAIXO_RISCO_COMPROVADO"
    )

    # Determina o grau semântico de severidade clínica para apoio aos protocolos de
    # triagem hospitalar:
    if probabilidade_risco >= 0.75:
        severidade = "CRÍTICO"
    elif classe_final == 1:
        severidade = "ELEVADO"
    elif probabilidade_risco >= 0.25:
        severidade = "MODERADO"
    else:
        severidade = "BAIXO"

    # 'return EsquemaRespostaPredicao(...)' compila e entrega o objeto JSON formal
    # estruturado.
    return EsquemaRespostaPredicao(
        classe_predita=classe_final,
        diagnostico_rotulo=rotulo,
        probabilidade_risco=round(probabilidade_risco, 4),
        limiar_decisao_aplicado=motor_predicao_ativo.limiar_corte,
        grau_severidade=severidade,
        versao_modelo_producao="SVM_Calibrado_Producao_v1.0.0",
        tempo_processamento_ms=round(latencia_ms, 3),
    )
