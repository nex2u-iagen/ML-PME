"""Script Executor Oficial da Fase 06 do CRISP-DM: Implantação e Produção Estável.

Responsabilidade Única: Ponto de entrada (CLI) para orquestrar o comissionamento da Fase 6:
identificar dinamicamente o modelo campeão homologado, fundir pré-processamento e classificador
via Adaptador de Metadados sem estado, serializar com integridade SHA-256 (Pilar 1),
validar credenciais JWT (Pilar 2), testar contratos Pydantic (Pilar 3) e executar a escoragem
operacional em lote com prescrição de crédito para o Metabase[cite: 8, 10, 15, 20].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro estruturado no console[cite: 8].
import logging

# 'import' traz o módulo 'json' para leitura do manifesto de governança gerado na Fase 4/5[cite: 8].
import json
import os

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz a classe 'Path' para manipulação segura de rotas[cite: 8].
from pathlib import Path

# 'import' traz o módulo 'sys' nativo para manipulação e garantia do caminho de busca de módulos no interpretador[cite: 8].
import sys

# RESOLUÇÃO CANÔNICA DA RAIZ DO REPOSITÓRIO:
DIRETORIO_RAIZ = Path(__file__).resolve().parents[2]
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# 'import' traz a biblioteca externa 'joblib' para desserialização atômica de estimadores[cite: 8].
import joblib

# 'import' traz a biblioteca externa 'numpy' para manipulação matemática e vetorização.
import numpy as np

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular e persistência dos dados de produção[cite: 8, 10].
import pandas as pd

# 'from' importa a classe 'Pipeline' do Scikit-Learn para fusão do transformador com o estimador[cite: 9, 10].
from sklearn.pipeline import Pipeline

# IMPORTAÇÃO DO ADAPTADOR TOP-LEVEL DO NÚCLEO (100% SERIALIZÁVEL PELO JOBLIB)[cite: 7, 8]:
from src.nucleo.aprendizado_maquina.transformadores_dados import (
    AdaptadorRotulosDataFrame,
)

# IMPORTAÇÃO DOS ESPECIALISTAS DOS 4 PILARES DA FASE 6[cite: 8]:
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.empacotador_pipeline import (
    EmpacotadorPipelineProducao,
)
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.metadados_modelo import (
    MetadadosModeloProducao,
)
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.validador_integridade import (
    ValidadorIntegridadeArtefato,
)
from src.etapas.fase_06_implantacao.pilar_02_seguranca_autenticacao.gerenciador_token_jwt import (
    GerenciadorTokenJWT,
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

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal[cite: 8].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Função executiva que orquestra a implantação desacoplada e estável da Fase 6."""
    print("\n" + "=" * 105)
    print("🚀 INICIANDO FASE 06: IMPLANTAÇÃO, GOVERNANÇA CRIPTOGRÁFICA E INFERÊNCIA EM PRODUÇÃO")
    print("=" * 105 + "\n")

    # Identificação do cliente e configuração de diretórios oficiais de governança[cite: 8]:
    nome_cliente = "mercado_vencedor"
    pasta_modelos_fase4 = DIRETORIO_RAIZ / "modelos" / nome_cliente
    pasta_ml_fase3 = DIRETORIO_RAIZ / "dados" / "processados" / nome_cliente / "ml"
    
    pasta_artefatos_producao = DIRETORIO_RAIZ / "artefatos" / "modelos_producao"
    pasta_artefatos_producao.mkdir(parents=True, exist_ok=True)

    pasta_saida_producao = DIRETORIO_RAIZ / "dados" / "processados" / nome_cliente / "producao"
    pasta_saida_producao.mkdir(parents=True, exist_ok=True)

    caminho_preparador_fase3 = pasta_modelos_fase4 / "pipeline_preparacao_ml.joblib"
    caminho_campeao_fase4 = pasta_modelos_fase4 / "modelo_campeao_classificacao.joblib"
    caminho_manifesto_fase4 = pasta_modelos_fase4 / "modelo_campeao_classificacao.json"
    caminho_abt_bruta = pasta_ml_fase3 / "abt_cliente_bruta.parquet"

    if not caminho_preparador_fase3.is_file() or not caminho_campeao_fase4.is_file():
        logging.error("Artefatos das Fases 3 e 4 não localizados em: %s", pasta_modelos_fase4)
        sys.exit(1)

    # ---------------------------------------------------------------------------------------------
    # PASSO 1: FUSÃO ROBUSTA DO PIPELINE VIA ADAPTADOR FORMAL (ZERO WARNINGS E 100% SERIALIZÁVEL)
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PASSO 1/5] IDENTIFICANDO O MODELO CAMPEÃO E CONSTRUINDO O PIPELINE FINAL ---")
    preparador_ajustado = joblib.load(caminho_preparador_fase3)
    modelo_ajustado = joblib.load(caminho_campeao_fase4)

    # Identificação dinâmica do algoritmo campeão via manifesto de governança[cite: 8]:
    nome_algoritmo_campeao = modelo_ajustado.__class__.__name__
    if caminho_manifesto_fase4.is_file():
        with open(caminho_manifesto_fase4, mode="r", encoding="utf-8") as f_json:
            manifesto_fase4 = json.load(f_json)
            nome_algoritmo_campeao = manifesto_fase4.get("algoritmo_campeao", nome_algoritmo_campeao)

    logging.info("Algoritmo campeão homologado: '%s'", nome_algoritmo_campeao)

    # Captura a lista oficial de nomes de colunas geradas pelo pré-processador da Fase 3[cite: 8, 9]:
    colunas_saida_preparador = list(preparador_ajustado.get_feature_names_out())

    # Instancia a classe oficial importada do módulo (permite ao Joblib/Pickle salvar sem PicklingError)[cite: 7, 8]:
    adaptador_dataframe = AdaptadorRotulosDataFrame(nomes_colunas=colunas_saida_preparador)

    # Encadeia o pré-processador, o adaptador serializável e o classificador campeão[cite: 7, 8, 10]:
    pipeline_producao_completo = Pipeline(
        steps=[
            ("pre_processamento", preparador_ajustado),
            ("adaptador_colunas", adaptador_dataframe),
            ("classificador_campeao", modelo_ajustado),
        ]
    )
    logging.info("Pipeline unificado montado com sucesso (Zero advertências e serialização atômica).")

    # ---------------------------------------------------------------------------------------------
    # PASSO 2: PILAR 1 — PERSISTÊNCIA COMPRIMIDA E ASSINATURA SHA-256 (SERIALIZAÇÃO SEGURA)[cite: 8]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PASSO 2/5] PILAR 1: PERSISTÊNCIA COMPRIMIDA E ASSINATURA CRIPTOGRÁFICA ---")
    nomes_features_entrada = [
        "volume_total_recebido",
        "ticket_medio_titulo",
        "total_titulos_emitidos",
        "maximo_dias_atraso_historico",
        "uf_cliente",
        "cidade_cliente",
    ]

    metadados_producao = MetadadosModeloProducao(
        nome_modelo=f"{nome_algoritmo_campeao}_Supermercado_Producao",
        versao="v1.0.0",
        nomes_atributos=nomes_features_entrada,
        limiar_decisao_homologado=0.50,
        responsavel_tecnico="Dr. Arthur & Equipe de Dados",
    )

    empacotador = EmpacotadorPipelineProducao(pasta_destino_modelos=pasta_artefatos_producao)
    rotas_geradas = empacotador.salvar_pipeline_com_manifesto(
        pipeline_campeao=pipeline_producao_completo,
        metadados=metadados_producao,
        nome_arquivo_base="pipeline_campeao_producao",
    )
    caminho_binario = rotas_geradas["caminho_artefato_joblib"]
    caminho_manifesto = rotas_geradas["caminho_manifesto_json"]

    # Validação rigorosa de integridade física no disco rígido[cite: 8]:
    validador_sha = ValidadorIntegridadeArtefato()
    validador_sha.validar_artefato_contra_manifesto(
        caminho_artefato=caminho_binario,
        caminho_manifesto=caminho_manifesto,
    )

    # ---------------------------------------------------------------------------------------------
    # PASSO 3: PILAR 2 — AUDITORIA DE SEGURANÇA E EMISSÃO DE TOKEN JWT[cite: 8]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PASSO 3/5] PILAR 2: AUDITORIA DE SEGURANÇA E EMISSÃO DE TOKEN JWT ---")
    gerenciador_jwt = GerenciadorTokenJWT()
    token_operador = gerenciador_jwt.gerar_token_acesso(
        identificador_usuario="operador_faturamento",
        perfil_acesso="analista_credito_senior",
    )
    dados_token_validados = gerenciador_jwt.validar_token_acesso(token_operador)

    if dados_token_validados is None:
        logging.error("Falha na auditoria de segurança do token JWT!")
        sys.exit(1)
    logging.info("Token JWT autenticado para o operador: '%s'.", dados_token_validados["sub"])

    # ---------------------------------------------------------------------------------------------
    # PASSO 4: PILARES 3 E 4 — CARGA EM MEMÓRIA RAM SINGLETON E TESTE UNITÁRIO[cite: 8]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PASSO 4/5] PILARES 3 E 4: CARGA EM MEMÓRIA SINGLETON E TESTE UNITÁRIO ---")
    CarregadorModeloSingleton.liberar_memoria()
    pipeline_ativo_ram = CarregadorModeloSingleton.carregar_modelo_producao(
        caminho_artefato=caminho_binario,
        caminho_manifesto=caminho_manifesto,
    )

    motor_inferencia = MotorPredicaoVetorizado(limiar_corte=0.50)

    # Amostra de teste unitário validada via contrato Pydantic V2[cite: 8]:
    cliente_teste = EsquemaEntradaCliente(
        volume_total_recebido=18500.00,
        ticket_medio_titulo=920.00,
        total_titulos_emitidos=22,
        maximo_dias_atraso_historico=2.0,
        uf_cliente="SP",
        cidade_cliente="Mogi Guaçu",
    )

    classe, rotulo, prob, faixa, acao, latencia_ms = motor_inferencia.executar_predicao_rapida(
        cliente=cliente_teste,
        pipeline_modelo=pipeline_ativo_ram,
    )

    resposta_api = EsquemaRespostaPredicao(
        classe_predita=classe,
        decisao_rotulo=rotulo,
        probabilidade_risco=round(prob, 4),
        limiar_decisao_aplicado=motor_inferencia.limiar_corte,
        faixa_risco=faixa,
        acao_recomendada=acao,
        versao_modelo_producao=f"{nome_algoritmo_campeao}_Producao_v1.0.0",
        tempo_processamento_ms=round(latencia_ms, 3),
    )
    logging.info(
        "Teste unitário do modelo '%s' concluído em %.3f ms: %s (Prob: %.2f%%) -> Ação: %s",
        nome_algoritmo_campeao,
        resposta_api.tempo_processamento_ms,
        resposta_api.faixa_risco,
        resposta_api.probabilidade_risco * 100,
        resposta_api.acao_recomendada,
    )

    # ---------------------------------------------------------------------------------------------
    # PASSO 5: ESCORAGEM OPERACIONAL EM LOTE DA CARTEIRA E PERSISTÊNCIA PARA O METABASE[cite: 8, 15]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PASSO 5/5] ESCORAGEM EM LOTE DA CARTEIRA COMPLETA PARA O METABASE ---")
    df_clientes_carteira = pd.read_parquet(caminho_abt_bruta)
    logging.info("Processando lote de %d títulos cadastrados no ERP...", len(df_clientes_carteira))

    X_entrada_lote = df_clientes_carteira[nomes_features_entrada]

    # Execução vetorizada em lote pelo pipeline completo (sem nenhum aviso no log)[cite: 8, 9]:
    probabilidades_lote = pipeline_ativo_ram.predict_proba(X_entrada_lote)[:, 1]
    classes_lote = pipeline_ativo_ram.predict(X_entrada_lote)

    faixas_lote = []
    acoes_lote = []
    for p in probabilidades_lote:
        _, faixa_item, acao_item = MotorPredicaoVetorizado.prescrever_acao(float(p))
        faixas_lote.append(faixa_item)
        acoes_lote.append(acao_item)

    df_escoragem = pd.DataFrame({
        "codigo_cliente": df_clientes_carteira["codigo_cliente"],
        "razao_social_cliente": df_clientes_carteira["razao_social_cliente"],
        "cidade_cliente": df_clientes_carteira["cidade_cliente"],
        "uf_cliente": df_clientes_carteira["uf_cliente"],
        "volume_faturado_r$": df_clientes_carteira["volume_total_recebido"],
        "maximo_dias_atraso": df_clientes_carteira["maximo_dias_atraso_historico"],
        "probabilidade_inadimplencia": np.round(probabilidades_lote, 4),
        "classe_risco_predita": classes_lote,
        "faixa_risco": faixas_lote,
        "acao_recomendada_credito": acoes_lote,
    }).sort_values(by="probabilidade_inadimplencia", ascending=False).reset_index(drop=True)

    caminho_saida_parquet = pasta_saida_producao / "escoragem_risco_prescritiva.parquet"
    caminho_saida_csv = pasta_saida_producao / "escoragem_risco_prescritiva.csv"

    df_escoragem.to_parquet(caminho_saida_parquet, index=False)
    df_escoragem.to_csv(caminho_saida_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logging.info("Tabelas operacionais gravadas com sucesso em: %s", pasta_saida_producao.resolve())

    # ---------------------------------------------------------------------------------------------
    # EXIBIÇÃO DA TELEMETRIA DE PRODUÇÃO NO CONSOLE:
    # ---------------------------------------------------------------------------------------------
    print("\n" + "=" * 105)
    print(f"📊 AMOSTRA DA TABELA PRESCRITIVA GERADA PELO CAMPEÃO: '{nome_algoritmo_campeao.upper()}'")
    print("=" * 105)
    colunas_console = [
        "codigo_cliente",
        "razao_social_cliente",
        "probabilidade_inadimplencia",
        "faixa_risco",
        "acao_recomendada_credito",
    ]
    print(df_escoragem[colunas_console].head(10).to_string(index=False))

    print("\n" + "-" * 105)
    distribuicao = df_escoragem["faixa_risco"].value_counts()
    print("📈 DISTRIBUIÇÃO DA CARTEIRA POR FAIXAS DE RISCO:")
    for faixa_nome, qtd in distribuicao.items():
        percentual = (qtd / len(df_escoragem)) * 100.0
        print(f"   • {faixa_nome:<25} -> {qtd:>5} títulos ({percentual:>5.1f}%)")

    print("\n" + "=" * 105)
    print(f"✅ FASE 06 CONCLUÍDA! MODELO '{nome_algoritmo_campeao}' OPERACIONAL EM PRODUÇÃO")
    print(f"📁 Binário de Produção (SHA-256): {caminho_binario.resolve()}")
    print(f"📁 Manifesto de Governança: {caminho_manifesto.resolve()}")
    print(f"📁 Tabela Operacional CSV (Metabase): {caminho_saida_csv.resolve()}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()