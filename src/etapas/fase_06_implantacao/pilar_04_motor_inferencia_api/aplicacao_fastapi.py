"""Aplicação Web de Produção do Microsserviço REST de Inferência Financeira (Pilar 4 - Fase 6).

Responsabilidade Única: Expor endpoints HTTP com documentação interativa Swagger OpenAPI 3.1,
gerir o ciclo de vida da aplicação (Lifespan), autenticar requisições via Bearer Token JWT
e entregar predições de risco de crédito com validação Pydantic em frações de milissegundo[cite: 10].

Além do microsserviço de inferência, a aplicação expõe a **camada de serviço da
plataforma agnóstica (G6)**: catálogo de datasets, upload de arquivos, vínculo de
problemas de negócio, execução assíncrona de fases, consulta de jobs, pódio Top 3
e registro da escolha humana do campeão.
"""

# 'from contextlib' provê suporte ao gerenciador de ciclo de vida assíncrono (Lifespan)[cite: 10].
from contextlib import asynccontextmanager

# 'import os' acessa as variáveis de ambiente do servidor (segredos e credenciais).
import os

# 'from pathlib' manipula caminhos orientados a objetos de forma agnóstica ao sistema operacional[cite: 10].
from pathlib import Path

# 'from typing' provê suporte a tipagem estática[cite: 10].
from typing import Any, Optional

# 'from pydantic' traz o motor de validação com tipagem forte dos contratos da API.
from pydantic import BaseModel, Field

# 'from fastapi' carrega os componentes web assíncronos de alto desempenho[cite: 10].
# from fastapi carrega os componentes web assíncronos de alto desempenho[cite: 10].
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse

# Importa a camada de serviço da plataforma agnóstica (G6) e o gerenciador de jobs.
from src.nucleo.orquestracao.servico_plataforma import ServicoPlataforma

# Importação dos módulos especialistas dos Pilares 1, 2, 3 e 4 da Fase 6[cite: 10]:
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.gerenciador_token_jwt import (
    GerenciadorTokenJWT,
)
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.guardiao_autorizacao import (
    verificar_autorizacao_portador,
)
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_cliente import (
    EsquemaEntradaCliente,
)
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_resposta_predicao import (
    EsquemaRespostaPredicao,
)
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.carregador_modelo_singleton import (
    CarregadorModeloSingleton,
)
from src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.motor_predicao_vetorizado import (
    MotorPredicaoVetorizado,
)

# --------------------------------------------------------------------------------------
# RESOLUÇÃO CANÔNICA DE CAMINHOS NO SERVIDOR
# --------------------------------------------------------------------------------------
DIRETORIO_RAIZ = Path(__file__).resolve().parents[4]

# Rota dos artefatos oficiais serializados no repositório[cite: 10]:
PASTA_PRODUCAO = DIRETORIO_RAIZ / "artefatos" / "modelos_producao"
CAMINHO_ARTEFATO_BINARIO = PASTA_PRODUCAO / "pipeline_campeao_producao.joblib"
CAMINHO_MANIFESTO_JSON = PASTA_PRODUCAO / "pipeline_campeao_producao_manifesto.json"

# Instancia o motor de inferência matemático com o limiar de corte homologado (0.50)[cite: 10]:
motor_predicao_ativo = MotorPredicaoVetorizado(limiar_corte=0.50)

# Instancia a camada de serviço da plataforma agnóstica (G6): registro de datasets,
# catálogo de problemas de negócio e gerenciador de jobs assíncronos.
servico_plataforma = ServicoPlataforma(diretorio_raiz=DIRETORIO_RAIZ)


# --------------------------------------------------------------------------------------
# GESTOR DE CICLO DE VIDA ASSÍNCRONO DA APLICAÇÃO (LIFESPAN MANAGEMENT)
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def gerenciar_ciclo_vida_servico(aplicacao: FastAPI):
    """Carrega o modelo uma única vez na memória RAM na partida e libera recursos no encerramento[cite: 10]."""
    print("🚀 [LIFESPAN] Inicializando microsserviço: auditando integridade SHA-256 e alocando modelo na RAM...")

    # Se os artefatos de produção ainda não tiverem sido empacotados, alerta o administrador[cite: 10]:
    if not CAMINHO_ARTEFATO_BINARIO.is_file():
        print(f"⚠️ [AVISO] Artefato '{CAMINHO_ARTEFATO_BINARIO.name}' não localizado.")
        print("Execute o empacotamento ou o script executor da Fase 6 para gerar a release de produção.")
    else:
        CarregadorModeloSingleton.carregar_modelo_producao(
            caminho_artefato=CAMINHO_ARTEFATO_BINARIO,
            caminho_manifesto=CAMINHO_MANIFESTO_JSON,
        )
        print("✅ [LIFESPAN] Pipeline completo ativo na memória RAM compartilhada.")

    yield

    print("🛑 [LIFESPAN] Encerrando microsserviço: liberando recursos de memória...")
    CarregadorModeloSingleton.liberar_memoria()


# --------------------------------------------------------------------------------------
# INSTANCIAÇÃO DA APLICAÇÃO FASTAPI COM METADADOS SWAGGER OPENAPI
# --------------------------------------------------------------------------------------
aplicacao_api = FastAPI(
    title="API de Inferência e Risco de Crédito — Mercado Vencedor (CRISP-DM Fase 6)",
    description=(
        "Microsserviço corporativo de alta disponibilidade para escoragem de risco de inadimplência em tempo real[cite: 10].\n\n"
        "- **Autenticação:** Exige cabeçalho `Authorization: Bearer <token_jwt>` em rotas de predição[cite: 10].\n"
        "- **Entrada de Dados:** Recebe os atributos de crédito do ERP validados via Pydantic V2[cite: 10].\n"
        "- **Governança:** Integridade auditada via SHA-256 e homologada pelo comitê de risco[cite: 10]."
    ),
    version="1.0.0",
    lifespan=gerenciar_ciclo_vida_servico,
)


class EsquemaRequisicaoLogin(BaseModel):
    """Contrato simples para autenticação e emissão de tokens[cite: 10]."""
    usuario: str = "analista_credito"
    senha: str = os.getenv("API_SENHA_PADRAO", "senha_segura_mercado_2026")


@aplicacao_api.get("/", tags=["Navegação"], summary="Redireciona para o Swagger UI")
async def rota_raiz():
    """Redireciona o acesso da raiz automaticamente para o painel Swagger em /docs[cite: 10]."""
    return RedirectResponse(url="/docs")


@aplicacao_api.post(
    "/autenticacao/token",
    tags=["Autenticação & Segurança"],
    summary="Emite Bearer Token JWT para acesso às rotas de inferência[cite: 10]",
)
async def emitir_token_acesso(dados_login: EsquemaRequisicaoLogin):
    """Autentica as credenciais institucionais e devolve o token assinado[cite: 10]."""
    if dados_login.senha != os.getenv("API_SENHA_PADRAO", "senha_segura_mercado_2026"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas: Usuário ou senha não conferem no cadastro corporativo.",
        )

    gerenciador_jwt = GerenciadorTokenJWT()
    token = gerenciador_jwt.gerar_token_acesso(identificador_usuario=dados_login.usuario)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expira_em_minutos": 480,
    }


@aplicacao_api.get(
    "/saude/prontidao",
    tags=["Monitoramento & Infraestrutura"],
    summary="Verifica se o modelo está carregado e operacional na memória RAM[cite: 10]",
)
async def checar_prontidao():
    """Sonda utilizada por balanceadores e orquestradores (Docker/K8s)[cite: 10]."""
    modelo_ativo = CarregadorModeloSingleton.obter_pipeline_ativo() is not None
    return {
        "status": "OPERACIONAL" if modelo_ativo else "AGUARDANDO_MODELO",
        "modelo_carregado_ram": modelo_ativo,
        "versao": "Random_Forest_Producao_v1.0.0",
    }


@aplicacao_api.post(
    "/predicao/risco_credito",
    response_model=EsquemaRespostaPredicao,
    tags=["Inferência Operacional"],
    summary="Executa a inferência de risco de crédito com autenticação Bearer e Pydantic[cite: 10]",
)
async def predizer_risco_cliente(
    cliente: EsquemaEntradaCliente,
    usuario_autenticado: dict[str, Any] = Depends(verificar_autorizacao_portador),
):
    """Recebe as variáveis financeiras do cliente e emite o parecer com ação recomendada[cite: 10]."""
    pipeline_ativo = CarregadorModeloSingleton.obter_pipeline_ativo()

    if pipeline_ativo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível: O Pipeline de Machine Learning ainda não foi alocado na memória.",
        )

    # Executa a inferência vetorizada computando o tempo de resposta[cite: 10]:
    classe, rotulo, probabilidade, faixa, acao, latencia = (
        motor_predicao_ativo.executar_predicao_rapida(
            cliente=cliente,
            pipeline_modelo=pipeline_ativo,
        )
    )

    return EsquemaRespostaPredicao(
        classe_predita=classe,
        decisao_rotulo=rotulo,
        probabilidade_risco=round(probabilidade, 4),
        limiar_decisao_aplicado=motor_predicao_ativo.limiar_corte,
        faixa_risco=faixa,
        acao_recomendada=acao,
        versao_modelo_producao="Random_Forest_Producao_v1.0.0",
        tempo_processamento_ms=round(latencia, 3),
    )


# ======================================================================================
# CAMADA DE SERVIÇO DA PLATAFORMA AGNÓSTICA (G6)
# ======================================================================================
class EsquemaVinculoProblema(BaseModel):
    """Contrato de entrada para vincular um problema de negócio a um dataset."""

    problema: str = Field(
        ...,
        description="Identificador do template no catálogo (ex.: previsao_faturamento).",
    )
    pergunta_negocio: Optional[str] = Field(
        default=None,
        description="Pergunta customizada pelo humano (opcional).",
    )


class EsquemaExecucaoFase(BaseModel):
    """Contrato de entrada para disparar uma fase CRISP-DM de forma assíncrona."""

    semente: int = Field(default=42, ge=0, description="Semente matemática para reprodutibilidade.")
    problema: Optional[str] = Field(
        default=None,
        description="Problema de negócio a aplicar (usa o vinculado quando omitido).",
    )


class EsquemaEleicaoCampeao(BaseModel):
    """Contrato de entrada para registrar a escolha humana do modelo campeão."""

    modelo: str = Field(..., description="Nome exato do finalist eleito entre o Top 3.")


@aplicacao_api.get(
    "/datasets",
    tags=["Plataforma Agnóstica"],
    summary="Lista os datasets (PMEs) disponíveis com o estado de cada fase CRISP-DM",
)
async def listar_datasets():
    """Retorna o catálogo de datasets registrados e seus indicadores de progresso."""
    return {"datasets": servico_plataforma.listar_datasets()}


@aplicacao_api.post(
    "/datasets/{nome_dataset}/upload",
    tags=["Plataforma Agnóstica"],
    summary="Recebe o upload de dumps .sql ou tabelas .csv de uma PME",
)
async def enviar_dataset(nome_dataset: str, arquivos: list[UploadFile] = File(...)):
    """Isola os arquivos enviados na pasta nomeada pelo dataset e atualiza o registro."""
    if not arquivos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado. Anexe um dump .sql ou tabelas .csv.",
        )

    conteudos: list[tuple[str, bytes]] = []
    for arquivo in arquivos:
        nome = arquivo.filename or "arquivo_sem_nome"
        if Path(nome).suffix.lower() not in {".sql", ".csv"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo '{nome}' não suportado. Envie apenas .sql ou .csv.",
            )
        conteudos.append((nome, await arquivo.read()))

    registro = servico_plataforma.registrar_upload(nome_dataset, conteudos)
    return {
        "dataset": registro.nome,
        "arquivos_recebidos": registro.arquivos_origem,
        "registro": registro.resumo_para_frontend(),
    }


@aplicacao_api.get(
    "/problemas",
    tags=["Plataforma Agnóstica"],
    summary="Lista os 15 problemas de negócio pré-desenhados do motor CRISP-DM",
)
async def listar_problemas():
    """Retorna os templates de contrato disponíveis para escolha do analista."""
    return {"problemas": servico_plataforma.listar_problemas()}


@aplicacao_api.post(
    "/datasets/{nome_dataset}/problema",
    tags=["Plataforma Agnóstica"],
    summary="Vincula um contrato de problema de negócio ao dataset em análise",
)
async def vincular_problema(nome_dataset: str, dados: EsquemaVinculoProblema):
    """Persiste o contrato de problema, habilitando a construção da ABT na Fase 3."""
    try:
        registro = servico_plataforma.vincular_problema(
            nome_dataset=nome_dataset,
            id_problema=dados.problema,
            pergunta_negocio=dados.pergunta_negocio,
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    return {
        "dataset": registro.nome,
        "contrato": registro.contrato_problema.resumo_executivo() if registro.contrato_problema else None,
    }


@aplicacao_api.post(
    "/datasets/{nome_dataset}/fases/{fase}/executar",
    tags=["Plataforma Agnóstica"],
    summary="Dispara a execução assíncrona de uma fase CRISP-DM para o dataset",
)
async def executar_fase(nome_dataset: str, fase: str, dados: EsquemaExecucaoFase):
    """Submete a fase em background e devolve o identificador do job para acompanhamento."""
    try:
        job = servico_plataforma.executar_fase(
            nome_dataset=nome_dataset,
            fase=fase,
            semente=dados.semente,
            problema=dados.problema,
        )
    except FileNotFoundError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro

    return {"job": job.resumo_para_frontend()}


@aplicacao_api.get(
    "/jobs/{id_job}",
    tags=["Plataforma Agnóstica"],
    summary="Consulta o estado, o log e o resultado de um job assíncrono",
)
async def consultar_job(id_job: str):
    """Retorna o retrato atual da execução acompanhada pelo frontend."""
    job = servico_plataforma.gerenciador_jobs.obter(id_job)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{id_job}' não encontrado.",
        )
    return {"job": job.resumo_para_frontend()}


@aplicacao_api.get(
    "/datasets/{nome_dataset}/top3",
    tags=["Plataforma Agnóstica"],
    summary="Retorna o pódio Top 3 com as métricas de avaliação dos finalistas",
)
async def obter_podio(nome_dataset: str):
    """Entrega os finalistas e suas métricas para a tela de decisão humana."""
    return servico_plataforma.obter_top3(nome_dataset)


@aplicacao_api.post(
    "/datasets/{nome_dataset}/campeao",
    tags=["Plataforma Agnóstica"],
    summary="Registra a escolha humana do modelo campeão entre o Top 3",
)
async def eleger_campeao(nome_dataset: str, dados: EsquemaEleicaoCampeao):
    """Formaliza a decisão do analista, selando o modelo que seguirá para implantação."""
    try:
        registro = servico_plataforma.eleger_campeao(nome_dataset, dados.modelo)
    except FileNotFoundError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro

    return {
        "dataset": registro.nome,
        "campeao": registro.campeao,
        "top3": registro.top3,
    }