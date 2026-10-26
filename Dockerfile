# =================================================================================================
# ESTÁGIO 1: CONSTRUTOR (BUILDER) — INSTALAÇÃO DE DEPENDÊNCIAS VIA UV
# =================================================================================================
# Utiliza a imagem oficial do UV sobre Python 3.12 Debian Bookworm Slim como base de compilação
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS construtor

# Configura variáveis de ambiente do compilador UV e do interpretador Python
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Define o diretório de trabalho onde os manifestos serão processados
WORKDIR /app

# Copia os manifestos de dependências do projeto para aproveitar o cache de camadas do Docker
COPY pyproject.toml uv.lock* ./

# Instala as dependências de produção de forma congelada no ambiente virtual '/app/.venv'
RUN uv sync --frozen --no-dev --no-install-project

# =================================================================================================
# ESTÁGIO 2: IMAGEM FINAL DE PRODUÇÃO (ENXUTA, SEGURA E IMUTÁVEL)
# =================================================================================================
# Utiliza a imagem limpa e mínima do Python 3.12 Slim sem compiladores extras
FROM python:3.12-slim-bookworm AS producao

# Configurações de execução enxuta do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Cria um usuário não-root (appuser) para execução segura sem privilégios de superusuário
RUN useradd -m -u 1000 appuser

# Define a pasta oficial da aplicação
WORKDIR /app

# Copia o ambiente virtual compilado do estágio anterior (construtor)
COPY --from=construtor /app/.venv /app/.venv

# Copia os artefatos serializados do modelo (.joblib e .json) necessários para a inferência
COPY --chown=appuser:appuser artefatos/ /app/artefatos/

# Copia o código-fonte modular em Python
COPY --chown=appuser:appuser src/ /app/src/

# Assume a identidade do usuário não-root
USER appuser

# Documenta a porta de rede TCP utilizada pelo microserviço
EXPOSE 8000

# Comando de inicialização do servidor Uvicorn escutando em todas as interfaces de rede (0.0.0.0)
CMD ["uvicorn", "src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.aplicacao_fastapi:aplicacao_api", "--host", "0.0.0.0", "--port", "8000"]