# =================================================================================================
# ESTÁGIO 1: CONSTRUTOR (BUILDER) — INSTALAÇÃO DE DEPENDÊNCIAS VIA UV
# =================================================================================================
# Utiliza a imagem oficial do UV sobre Python 3.12 Debian Bookworm Slim como base de compilação
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS construtor

# Configura variáveis de ambiente do compilador UV e do interpretador Python
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    UV_HTTP_TIMEOUT=600 \
    UV_CONCURRENT_DOWNLOADS=4

# Define o diretório de trabalho onde os manifestos serão processados
WORKDIR /app

# Copia os manifestos de dependências do projeto para aproveitar o cache de camadas do Docker
COPY pyproject.toml uv.lock* ./

# Instala as dependências de produção de forma congelada no ambiente virtual '/app/.venv'
# (o Streamlit já está listado em pyproject.toml, não é preciso instalá-lo à parte)
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

# Copia o frontend operacional Streamlit
COPY --chown=appuser:appuser app_streamlit.py /app/app_streamlit.py

# Garante que o usuário da aplicação possa criar pastas de dados/logs em tempo de execução
RUN mkdir -p /app/dados /app/logs && chown -R appuser:appuser /app

# Assume a identidade do usuário não-root
USER appuser

# Documenta as portas de rede TCP utilizadas pelo microserviço e frontend
EXPOSE 8000
EXPOSE 8501

# Comando padrão: inicia apenas a API de inferência (serviço api-predicao-risco)
CMD ["uvicorn", "src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.aplicacao_fastapi:aplicacao_api", "--host", "0.0.0.0", "--port", "8000"]