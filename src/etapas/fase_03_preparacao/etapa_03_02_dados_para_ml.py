"""Módulo Orquestrador de Preparação de Dados para Machine Learning (Fase 3.2).

Responsável por orquestrar a construção da ABT, aplicar a partição tripla
estratificada (70% Treino / 15% Validação / 15% Teste Real), encadear o
ColumnTransformer do Scikit-Learn sem Data Leakage e serializar os artefatos.
"""

# 'import' traz o módulo 'logging' da biblioteca padrão para registros profissionais de
# auditoria no terminal.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipular
# pastas de modo orientado a objetos.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotação de tipos de dados
# de retorno.
# 'import' traz a biblioteca externa 'pandas' para manipulação tabular e conversão em
# arquivos Parquet.
# 'as' define o apelido oficial 'pd' para facilitar as chamadas de funções.
import pandas as pd

# 'from' acessa os estimadores compostos do Scikit-Learn para transformação de
# colunas[cite: 2].
# 'ColumnTransformer' aplica transformações diferentes (numéricas vs texto) em colunas
# específicas[cite: 2].
from sklearn.compose import ColumnTransformer

# 'from' importa os imputadores matemáticos para preenchimento de valores nulos
# (NaN)[cite: 2].
from sklearn.impute import SimpleImputer

# 'from' acessa as ferramentas de seleção e divisão de dados do Scikit-Learn[cite: 2].
# 'train_test_split' divide matrizes em partições aleatórias ou estratificadas de forma
# segura[cite: 2].
from sklearn.model_selection import train_test_split

# 'from' importa a classe 'Pipeline' para encadear etapas matemáticas sequenciais
# (imputar -> escalar)[cite: 2].
from sklearn.pipeline import Pipeline

# 'from' importa os pré-processadores estatísticos para padronização e codificação[cite:
# 2].
# 'StandardScaler' padroniza números contínuos para média zero e variância unitária
# (z-score)[cite: 2].
# 'OneHotEncoder' converte variáveis nominais de texto em matrizes binárias
# interpretáveis por algoritmos[cite: 2].
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 'from' importa a classe que constrói a Tabela Analítica de Modelagem (ABT)
# consolidando o grão do cliente.
from src.etapas.fase_03_preparacao.engenharia_ml.construtor_abt import (
    ConstrutorABTCliente,
)

# 'from' importa o gerenciador de persistência do núcleo para serializar e salvar os
# arquivos .joblib e .json.
from src.nucleo.aprendizado_maquina.persistencia_artefatos import (
    GerenciadorPersistenciaModelos,
)

# 'from' importa o nosso transformador customizado de corte de anomalias (IQR) criado no
# núcleo compartilhado.
from src.nucleo.aprendizado_maquina.transformadores_dados import (
    TruncadorDeValoresExtremos,
)

# 'logging.basicConfig' parametriza a formatação visual e a criticidade dos logs
# exibidos no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o molde estrutural do orquestrador de Machine Learning.
class OrquestradorDadosML:
    """Classe responsável pelo particionamento seguro e pré-processamento matemático
    para ML.
    """

    # 'def' define o método construtor '__init__', acionado ao instanciar o objeto na
    # memória RAM.
    # 'self' referencia a própria instância para acessar seus parâmetros internos.
    # 'pasta_bi: Path' recebe o diretório onde as matrizes departamentais de BI estão
    # arquivadas.
    # 'pasta_saida_ml: Path' recebe a pasta onde os arquivos Parquet de treino e teste
    # serão salvos.
    # 'pasta_modelos: Path' recebe o endereço de destino para o Pipeline matemático
    # (.joblib).
    # 'semente_aleatoria: int' fixa a aleatoriedade estatística para garantir
    # reprodutibilidade nos testes.
    def __init__(
        self,
        pasta_bi: Path,
        pasta_saida_ml: Path,
        pasta_modelos: Path,
        semente_aleatoria: int = 42,
    ) -> None:
        """Inicializa o orquestrador de ML configurando diretórios operacionais e
        construtores.

        Args:
            pasta_bi (Path): Diretório contendo os Data Marts de BI consolidados e
            limpos.
            pasta_saida_ml (Path): Diretório onde os arquivos Parquet de treino e teste
            ficarão armazenados.
            pasta_modelos (Path): Diretório onde o pipeline .joblib de pré-processamento
            será gravado.
            semente_aleatoria (int): Semente (seed) para o gerador de números
            pseudoaleatórios.
        """
        # Armazena os caminhos recebidos como atributos definitivos do objeto
        # orquestrador.
        self.pasta_bi = pasta_bi
        self.pasta_saida_ml = pasta_saida_ml
        self.pasta_modelos = pasta_modelos
        self.semente = semente_aleatoria

        # '.mkdir()' garante que as pastas de destino existam no sistema, criando-as se
        # necessário.
        self.pasta_saida_ml.mkdir(parents=True, exist_ok=True)
        self.pasta_modelos.mkdir(parents=True, exist_ok=True)

        # Instancia o construtor transversal responsável por cruzar as tabelas de BI em
        # formato ABT.
        self.construtor_abt = ConstrutorABTCliente(self.pasta_bi)

        # Emite uma mensagem afirmativa no console registrando a ativação do módulo.
        logging.info(
            "Orquestrador de ML ativo. Destino ML: %s | Semente: %d",
            self.pasta_saida_ml.name,
            self.semente,
        )

    # 'def' define a função responsável por fatiar a base completa em conjuntos
    # independentes.
    # 'df: pd.DataFrame' recebe a tabela analítica completa (ABT) bruta.
    # '-> Tuple' atesta que o método devolverá uma coleção múltipla contendo as matrizes
    # X e os alvos y.
    def dividir_treino_validacao_teste(
        self, df: pd.DataFrame, coluna_alvo: str = "alvo_inadimplente"
    ) -> tuple[
        pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series
    ]:
        """Realiza a divisão tripla (70% Treino / 15% Validação / 15% Teste) com
        contingência para bases pequenas.

        Args:
            df (pd.DataFrame): Tabela analítica (ABT) consolidada por cliente.
            coluna_alvo (str): O nome da variável binária que o modelo deve prever.

        Returns:
            Tuple: Seis objetos na ordem (X_treino, y_treino, X_val, y_val, x_teste,
            y_teste).
        """
        # Extrai a coluna-alvo (target/y) da tabela principal, isolando a resposta que
        # queremos prever.
        y = df[coluna_alvo]

        # Lista as colunas textuais identificadoras que não podem entrar no treinamento
        # matemático.
        colunas_descarte = [coluna_alvo, "codigo_cliente", "razao_social_cliente"]

        # '.drop()' remove as colunas de descarte, deixando apenas as variáveis
        # explicativas estatísticas na matriz X.
        x = df.drop(columns=[col for col in colunas_descarte if col in df.columns])

        # CONTAGEM DEFENSIVA: Verifica quantos clientes inadimplentes existem na base
        # sintética atual.
        # '.value_counts().min()' identifica o tamanho da menor classe (neste caso,
        # y=1).
        tamanho_classe_minoria = y.value_counts().min()

        # Avalia se a classe minoritária tem tamanho suficiente para suportar a
        # matemática da estratificação.
        if tamanho_classe_minoria < 2:
            # Se a base for muito pequena (ex: 8 linhas geradas na contingência),
            # desativamos a estratificação (None).
            estratificador_1 = None
            logging.warning(
                "Divisão Fase 1: Base minúscula detectada (%d registros minoritários)."
                "Estratificação desativada.",
                tamanho_classe_minoria,
            )
        else:
            # Caso a base seja volumosa e real, aplicamos a proteção estratificada
            # rigorosa pelo alvo y.
            estratificador_1 = y

        # PRIMEIRA DIVISÃO: Separa 70% da base para Treino e guarda 30% no conjunto
        # Holdout (Restante).
        x_treino, x_restante, y_treino, y_restante = train_test_split(
            x, y, test_size=0.30, random_state=self.semente, stratify=estratificador_1
        )

        # RE-AVALIAÇÃO DEFENSIVA PARA A SEGUNDA DIVISÃO (Validação vs Teste).
        tamanho_minoria_restante = y_restante.value_counts().min()

        # Confirma novamente se o corte de 30% reteve exemplares suficientes para
        # estratificar.
        if estratificador_1 is None or tamanho_minoria_restante < 2:
            estratificador_2 = None
            logging.warning(
                "Divisão Fase 2: Amostras insuficientes no holdout. Estratificação de"
                "Teste desativada."
            )
        else:
            estratificador_2 = y_restante

        # SEGUNDA DIVISÃO: Fica com os 30% do Holdout e corta exatamente no meio
        # ('test_size=0.50'), gerando 15% / 15%.
        x_val, x_teste, y_val, y_teste = train_test_split(
            x_restante,
            y_restante,
            test_size=0.50,
            random_state=self.semente,
            stratify=estratificador_2,
        )

        # Emite log detalhando o volume exato de linhas separadas para cada finalidade
        # de aprendizado.
        logging.info(
            "Triagem pronta: Treino (70%%)=%d | Validação (15%%)=%d | Teste Real"
            "(15%%)=%d",
            len(x_treino),
            len(x_val),
            len(x_teste),
        )

        # Retorna as seis partições perfeitamente isoladas.
        return x_treino, y_treino, x_val, y_val, x_teste, y_teste

    # 'def' define o método responsável por encadear as lógicas de tratamento de valores
    # nulos e escalas.
    # '-> ColumnTransformer' documenta que a função entrega o objeto composto final do
    # Scikit-Learn.
    def montar_pipeline_preparacao(
        self, x_referencia: pd.DataFrame
    ) -> ColumnTransformer:
        """Configura a esteira do Scikit-Learn para aplicar regras matemáticas estritas
        às features numéricas e de texto.

        Args:
            x_referencia (pd.DataFrame): Amostra de Treinamento usada apenas para
            descobrir os nomes das colunas.

        Returns:
            ColumnTransformer: Ferramenta configurada para aplicar as transformações
            paralelamente.
        """
        # '.select_dtypes()' varre o DataFrame e captura os nomes de todas as colunas
        # numéricas (int, float).
        colunas_numericas = list(x_referencia.select_dtypes(include=["number"]).columns)

        # '.select_dtypes()' varre o DataFrame e captura as colunas baseadas em texto ou
        # categorias nominais.
        colunas_categoricas = list(
            x_referencia.select_dtypes(include=["object", "category"]).columns
        )

        # Registra a volumetria de colunas separadas para o devido tratamento
        # estatístico.
        logging.info(
            "Features mapeadas: %d numéricas contínuas | %d textuais categóricas.",
            len(colunas_numericas),
            len(colunas_categoricas),
        )

        # 1. ESTEIRA DE VARIÁVEIS NUMÉRICAS
        # 'SimpleImputer' cobre eventuais buracos de dados preenchendo-os com a mediana
        # geral da coluna[cite: 2].
        # 'TruncadorDeValoresExtremos' impede que limites de crédito muito altos
        # distorçam a média geral.
        # 'StandardScaler' puxa os dados para o centro e estabiliza a variância para
        # algoritmos lineares funcionarem[cite: 2].
        pipeline_numerico = Pipeline(
            steps=[
                ("imputador", SimpleImputer(strategy="median")),
                ("truncador_iqr", TruncadorDeValoresExtremos(multiplicador_iqr=1.5)),
                ("escalonador", StandardScaler()),
            ]
        )

        # 2. ESTEIRA DE VARIÁVEIS CATEGÓRICAS (TEXTOS)
        # 'SimpleImputer' substitui eventuais textos vazios pelo termo que mais aparece
        # na tabela (moda)[cite: 2].
        # 'OneHotEncoder' converte palavras (ex: 'Sudeste') em colunas de Zero e Um
        # compreensíveis pelo PC[cite: 2].
        pipeline_categorico = Pipeline(
            steps=[
                ("imputador", SimpleImputer(strategy="most_frequent")),
                (
                    "one_hot",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
            ]
        )

        # 'ColumnTransformer' junta a esteira numérica e a categórica em uma única
        # máquina paralela[cite: 2].
        pre_processador = ColumnTransformer(
            transformers=[
                ("num", pipeline_numerico, colunas_numericas),
                ("cat", pipeline_categorico, colunas_categoricas),
            ]
        )

        # Devolve a máquina de pré-processamento pronta para ser treinada.
        return pre_processador

    # 'def' define a função orquestradora geral, que unifica a Fase 3.2 de ponta a
    # ponta.
    def executar_preparacao_ml_completa(self) -> dict[str, Path]:
        """Comanda a geração da ABT, o corte 70/15/15, a calibração antí-vazamento e a
        serialização final.

        Returns:
            Dict[str, Path]: Lista com os endereços de destino dos arquivos Parquet e
            Joblib gravados.
        """
        # Emite no terminal o aviso de início da fase de engenharia de ML.
        logging.info(
            "================================================================="
        )
        logging.info(
            "=== INICIANDO FASE 3.2: ENGENHARIA DE ABT E PREPARAÇÃO ML     ==="
        )
        logging.info(
            "================================================================="
        )

        # 1. Dispara o agrupamento dos 10 Data Marts em uma tabela flat (1 linha por
        # cliente).
        df_abt = self.construtor_abt.construir_abt()

        # Constrói o endereço de salvamento e exporta a ABT em modo original Parquet.
        caminho_abt_bruta = self.pasta_saida_ml / "abt_cliente_bruta.parquet"
        df_abt.to_parquet(caminho_abt_bruta, index=False)
        logging.info(
            "ABT Bruta formatada e salva: %d clientes consolidados.", len(df_abt)
        )

        # 2. Particiona a base bruta em blocos independentes (70% Treino / 15% Val / 15%
        # Teste).
        x_treino, y_treino, x_val, y_val, x_teste, y_teste = (
            self.dividir_treino_validacao_teste(df_abt)
        )

        # 3. Exige a montagem das catracas de limpeza e padronização matemática.
        pipeline_preparacao = self.montar_pipeline_preparacao(x_treino)

        # 4. CALIBRAÇÃO PROTEGIDA CONTRA VAZAMENTO DE DADOS (DATA LEAKAGE).
        # '.fit_transform()' força as fórmulas estatísticas a estudarem APENAS os dados
        # dos 70% de Treino[cite: 2].
        logging.info(
            "Calculando médias e desvios-padrões estritamente sobre a partição de"
            "Treino (70%)..."
        )
        matriz_treino_transformada = pipeline_preparacao.fit_transform(x_treino)

        # '.transform()' aplica a régua viciada do Treino sobre o Teste, sem aprender os
        # dados novos (Simula Produção)[cite: 2].
        logging.info(
            "Aplicando a régua matemática isolada sobre Validação e Teste Real..."
        )
        matriz_val_transformada = pipeline_preparacao.transform(x_val)
        matriz_teste_transformada = pipeline_preparacao.transform(x_teste)

        # 5. Captura os novos nomes de colunas expandidas (geradas pelo codificador
        # OneHotEncoder).
        nomes_colunas_processadas = pipeline_preparacao.get_feature_names_out()

        # Remonta as matrizes numéricas geradas pelo Scikit-Learn de volta para
        # DataFrames amigáveis do pandas.
        df_treino_proc = pd.DataFrame(
            matriz_treino_transformada,
            columns=nomes_colunas_processadas,
            index=x_treino.index,
        )
        # Re-acopla a coluna dependente 'alvo_inadimplente' ao final da tabela tratada.
        df_treino_proc["alvo_inadimplente"] = y_treino.values

        df_val_proc = pd.DataFrame(
            matriz_val_transformada,
            columns=nomes_colunas_processadas,
            index=x_val.index,
        )
        df_val_proc["alvo_inadimplente"] = y_val.values

        df_teste_proc = pd.DataFrame(
            matriz_teste_transformada,
            columns=nomes_colunas_processadas,
            index=x_teste.index,
        )
        df_teste_proc["alvo_inadimplente"] = y_teste.values

        # 6. Estabelece os nomes físicos dos três arquivos limpos em disco.
        caminho_treino = self.pasta_saida_ml / "treino_processado.parquet"
        caminho_val = self.pasta_saida_ml / "validacao_processada.parquet"
        caminho_teste = self.pasta_saida_ml / "teste_processado.parquet"

        # Executa a persistência de alta performance salvando cada base finalizada na
        # extensão Parquet.
        df_treino_proc.to_parquet(caminho_treino, index=False)
        df_val_proc.to_parquet(caminho_val, index=False)
        df_teste_proc.to_parquet(caminho_teste, index=False)

        # 7. Dispara a rotina de Governança arquivando o modelo e emitindo o laudo de
        # rastreabilidade (JSON).
        caminho_pipeline_salvo = self.pasta_modelos / "pipeline_preparacao_ml.joblib"

        # Dicionário de auditoria descrevendo os metadados e contagens da transformação
        # atual.
        metadados_governanca = {
            "etapa": "Fase 3.2 - Preparação Matemática Rigorosa",
            "particionamento": "Triplo (70/15/15) via Scikit-Learn",
            "amostras_treino_linhas": int(len(df_treino_proc)),
            "amostras_validacao_linhas": int(len(df_val_proc)),
            "amostras_teste_linhas": int(len(df_teste_proc)),
            "total_atributos_apos_expansao": int(len(nomes_colunas_processadas)),
            "lista_variaveis_oficiais": list(nomes_colunas_processadas),
        }

        # Acessa o núcleo para gravar fisicamente o cérebro matemático de
        # pré-processamento.
        GerenciadorPersistenciaModelos.salvar_modelo_com_metadados(
            objeto_modelo=pipeline_preparacao,
            caminho_artefato=caminho_pipeline_salvo,
            metadados_governanca=metadados_governanca,
        )

        # Emite no terminal a conclusão absoluta da fase preparatória de dados.
        logging.info(
            "================================================================="
        )
        logging.info(
            "=== FASE 3 CONCLUÍDA: DADOS E PIPELINES DISPONÍVEIS PARA ML   ==="
        )
        logging.info(
            "================================================================="
        )

        # Retorna o mapa de onde todos os materiais entregues foram alocados.
        return {
            "treino_parquet": caminho_treino,
            "validacao_parquet": caminho_val,
            "teste_parquet": caminho_teste,
            "pipeline_joblib": caminho_pipeline_salvo,
        }


# Bloco condicional para execução em terminal como script independente.
if __name__ == "__main__":
    # Localiza o ponto de raiz estrutural do repositório subindo diretórios.
    raiz_do_projeto = Path(__file__).resolve().parent.parent.parent.parent

    # Encontra a pasta 'bi/' de onde os Data Marts brutos serão puxados.
    caminho_dados_bi = raiz_do_projeto / "dados" / "processados" / "bi"

    # Encontra a pasta 'ml/' onde os Parquets segmentados serão despejados.
    caminho_destino_ml = raiz_do_projeto / "dados" / "processados" / "ml"

    # Encontra a pasta de gestão de modelos onde o pipeline joblib ficará salvo.
    caminho_modelos = raiz_do_projeto / "modelos"

    # Declara a classe em memória configurando seus ponteiros básicos.
    orquestrador_ml = OrquestradorDadosML(
        pasta_bi=caminho_dados_bi,
        pasta_saida_ml=caminho_destino_ml,
        pasta_modelos=caminho_modelos,
    )

    # Roda a inteligência orquestradora ponta a ponta.
    artefatos_ml_gerados = orquestrador_ml.executar_preparacao_ml_completa()
