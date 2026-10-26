"""Script Executável para Lançamento do Servidor FastAPI de Produção (Fase 6).

Responsabilidade Única: Iniciar o servidor assíncrono Uvicorn escutando na porta 8000,
conectar a aplicação FastAPI com gestão de ciclo de vida Lifespan e disponibilizar
a documentação OpenAPI/Swagger interativa no endereço local
http://127.0.0.1:8000/docs[cite: 7].
"""

# 'import uvicorn' carrega o servidor ASGI de alta performance em Python para execução
# assíncrona[cite: 7].
import uvicorn

from scripts.bootstrap import configurar_ambiente

# '__name__ == "__main__"' garante que o servidor só seja iniciado se o script for
# executado diretamente no terminal[cite: 7].
if __name__ == "__main__":
    configurar_ambiente()
    print("\n" + "=" * 100)
    print("🌐 INICIALIZANDO MICROSERVIÇO FASTAPI DE INFERÊNCIA — PADRÃO OURO (FASE 6)")
    print("=" * 100)
    print(
        "📍 Bula Interativa Swagger (Onde estão documentadas as 10 Features): http://127.0.0.1:8000/docs"
    )
    print(
        "🔍 Sonda de Prontidão (Health Readiness Probe): http://127.0.0.1:8000/saude/prontidao"
    )
    print(
        "🔑 Rota de Emissão de Token Bearer JWT: http://127.0.0.1:8000/autenticacao/token"
    )
    print(
        "🎯 Rota de Inferência Protegida (Body JSON): http://127.0.0.1:8000/predicao/risco_cardiovascular"
    )
    print("=" * 100 + "\n")

    # 'uvicorn.run(...)' dispara o loop de eventos assíncrono do servidor ASGI[cite: 7]:
    # - Primeiro argumento: string no formato 'módulo:objeto_aplicacao' para permitir o
    # gerenciamento de processos[cite: 7].
    # - 'host="127.0.0.1"': escuta na interface de loopback local segura[cite: 7].
    # - 'port=8000': porta padrão de serviços web de Machine Learning[cite: 7].
    # - 'reload=False': desativa o recarregamento contínuo em produção para garantir
    # estabilidade e economia de CPU[cite: 7].
    # - 'log_level="info"': nível de verbosidade dos registros de tráfego HTTP no
    # terminal[cite: 7].
    uvicorn.run(
        "src.etapas.fase_06_implantacao.pilar_04_motor_inferencia_api.aplicacao_fastapi:aplicacao_api",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
