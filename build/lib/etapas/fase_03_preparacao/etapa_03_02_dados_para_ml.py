"""Módulo Orquestrador de Preparação de Dados para Machine Learning (Fase 3.2).

Responsabilidade Única: Servir de maestro enxuto da Fase 3.2, delegando a construção
da ABT, a partição tripla estratificada (70/15/15) e a montagem do ColumnTransformer
aos seus respectivos módulos especialistas, garantindo rastreabilidade e persistência.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional no console.
import logging

# 'from' acessa a biblioteca padrão 'pathlib'; 'import' traz 'Path' para manipulação orientada a objetos de pastas.
from pathlib import Path

# 'import' traz o módulo 'sys' nativo para manipulação e garantia do caminho de busca de módulos no interpretador.
import sys

# RESOLUÇÃO CANÔNICA DA RAIZ DO REPOSITÓRIO:
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent.parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# 'import' traz a biblioteca externa 'pandas' para formatação tabular final das partições de treino e teste.
import pandas as pd

# IMPORTAÇÃO DOS ESPECIALISTAS MODULARES DE ALTA COESÃO:
from src.etapas.fase_03_preparacao.engenharia_ml.construtor_abt import ConstrutorABTCliente
from src.etapas.fase_03_preparacao.engenharia_ml.divisor_amostras import DivisorAmostrasML
from src.etapas.fase_03_preparacao.engenharia_ml.pipeline_transformacao import ConstrutorPipelineTransformacao
from src.nucleo.aprendizado_maquina.persistencia_artefatos import GerenciadorPersistenciaModelos

# 'logging.basicConfig' parametriza a estética visual dos registros de auditoria no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o orquestrador enxuto com responsabilidade de coordenação pura.
class OrquestradorDadosML:
    """Maestro responsável por orquestrar a geração da ABT, partição tripla e pré-processamento de ML."""

    def __init__(
        self,
        pasta_bi: Path,
        pasta_saida_ml: Path,
        pasta_modelos: Path,
        semente_aleatoria: int = 42,
    ) -> None:
        """Inicializa o orquestrador configurando caminhos e instanciando o construtor da ABT."""
        self.pasta_bi = Path(pasta_bi)
        self.pasta_saida_ml = Path(pasta_saida_ml)
        self.pasta_modelos = Path(pasta_modelos)
        self.semente = semente_aleatoria

        # Garante a existência dos diretórios de saída no disco rígido.
        self.pasta_saida_ml.mkdir(parents=True, exist_ok=True)
        self.pasta_modelos.mkdir(parents=True, exist_ok=True)

        # Instancia o especialista responsável por cruzar as tabelas via DuckDB.
        self.construtor_abt = ConstrutorABTCliente(self.pasta_bi)

        logging.info("Orquestrador de ML ativo para o diretório: %s", self.pasta_saida_ml.name)

    def executar_preparacao_ml_completa(self, coluna_alvo: str = "alvo_inadimplente") -> dict[str, Path]:
        """Coordena o fluxo completo da Fase 3 delegando cada etapa aos especialistas desacoplados."""
        logging.info("=================================================================")
        logging.info("=== INICIANDO FASE 3.2: ENGENHARIA DE ABT E PREPARAÇÃO ML     ===")
        logging.info("=================================================================")

        # 1. DELEGAÇÃO: Constrói a ABT consolidada por cliente via DuckDB colunar.
        df_abt = self.construtor_abt.construir_abt()
        caminho_abt_bruta = self.pasta_saida_ml / "abt_cliente_bruta.parquet"
        df_abt.to_parquet(caminho_abt_bruta, index=False)
        logging.info("ABT Bruta persistida: %d clientes mapeados.", len(df_abt))

        # 2. ISOLA O ALVO (y) E AS VARIÁVEIS EXPLICATIVAS (X):
        y = df_abt[coluna_alvo]
        colunas_descarte = [coluna_alvo, "codigo_cliente", "razao_social_cliente"]
        X = df_abt.drop(columns=[col for col in colunas_descarte if col in df_abt.columns])

        # 3. DELEGAÇÃO: Particionamento triplo estratificado 70/15/15 via DivisorAmostrasML.
        x_treino, y_treino, x_val, y_val, x_teste, y_teste = DivisorAmostrasML.dividir_aleatorio_estratificado(
            x=X, y=y, proporcao_teste=0.15, proporcao_validacao=0.15, semente_aleatoria=self.semente
        )

        # 4. DELEGAÇÃO: Mapeia tipos e monta o ColumnTransformer via ConstrutorPipelineTransformacao.
        cols_num = list(x_treino.select_dtypes(include=["number"]).columns)
        cols_cat = list(x_treino.select_dtypes(include=["object", "category"]).columns)
        pipeline_preparacao = ConstrutorPipelineTransformacao.montar_pre_processador_completo(
            colunas_numericas=cols_num, colunas_categoricas=cols_cat, aplicar_corte_outliers=True
        )

        # 5. CALIBRAÇÃO PROTEGIDA CONTRA DATA LEAKAGE:
        logging.info("Calculando parâmetros estritamente sobre a partição de Treino (70%)...")
        matriz_treino = pipeline_preparacao.fit_transform(x_treino)

        logging.info("Aplicando a régua matemática estática sobre Validação e Teste Real...")
        matriz_val = pipeline_preparacao.transform(x_val)
        matriz_teste = pipeline_preparacao.transform(x_teste)

        # 6. PROPAGAÇÃO DE NOMES DE FEATURES (GRAÇAS AO NOVO get_feature_names_out):
        nomes_colunas = pipeline_preparacao.get_feature_names_out()

        # Remonta os DataFrames com as variáveis tratadas e o respectivo vetor-alvo.
        df_treino_proc = pd.DataFrame(matriz_treino, columns=nomes_colunas, index=x_treino.index)
        df_treino_proc[coluna_alvo] = y_treino.values

        df_val_proc = pd.DataFrame(matriz_val, columns=nomes_colunas, index=x_val.index)
        df_val_proc[coluna_alvo] = y_val.values

        df_teste_proc = pd.DataFrame(matriz_teste, columns=nomes_colunas, index=x_teste.index)
        df_teste_proc[coluna_alvo] = y_teste.values

        # 7. PERSISTÊNCIA DAS BASES HIGIENIZADAS EM PARQUET:
        caminho_treino = self.pasta_saida_ml / "treino_processado.parquet"
        caminho_val = self.pasta_saida_ml / "validacao_processada.parquet"
        caminho_teste = self.pasta_saida_ml / "teste_processado.parquet"

        df_treino_proc.to_parquet(caminho_treino, index=False)
        df_val_proc.to_parquet(caminho_val, index=False)
        df_teste_proc.to_parquet(caminho_teste, index=False)

        # 8. DELEGAÇÃO: Serializa o pipeline e registra os metadados de governança via GerenciadorPersistenciaModelos.
        caminho_pipeline_salvo = self.pasta_modelos / "pipeline_preparacao_ml.joblib"
        metadados = {
            "etapa": "Fase 3.2 - Preparação Matemática Rigorosa",
            "amostras_treino_linhas": int(len(df_treino_proc)),
            "amostras_validacao_linhas": int(len(df_val_proc)),
            "amostras_teste_linhas": int(len(df_teste_proc)),
            "total_atributos_finais": int(len(nomes_colunas)),
            "lista_variaveis": list(nomes_colunas),
        }
        GerenciadorPersistenciaModelos.salvar_modelo_com_metadados(
            objeto_modelo=pipeline_preparacao, caminho_artefato=caminho_pipeline_salvo, metadados_governanca=metadados
        )

        logging.info("=================================================================")
        logging.info("=== FASE 3 CONCLUÍDA: DADOS E PIPELINES DISPONÍVEIS PARA ML   ===")
        logging.info("=================================================================")

        return {
            "treino_parquet": caminho_treino,
            "validacao_parquet": caminho_val,
            "teste_parquet": caminho_teste,
            "pipeline_joblib": caminho_pipeline_salvo,
        }