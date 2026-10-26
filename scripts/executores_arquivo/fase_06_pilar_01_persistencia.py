"""Script Executável de Homologação e Teste do Pilar 1 da Fase 6 (Persistência e
Integridade).

Responsabilidade Única: Executar o treinamento do Pipeline campeão homologado
na Fase 5 (StandardScaler + SVM Calibrado), acionar o EmpacotadorPipelineProducao
para congelar o artefato no disco com compressão e auditar a conformidade
da assinatura digital SHA-256 gerada dentro de 'artefatos/modelos_producao/'[cite: 17,
21].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console
# corporativo[cite: 18].
import logging

# 'from sklearn.datasets import make_classification' gera o problema de diagnóstico
# clínico simulado da PME[cite: 18].
from sklearn.datasets import make_classification

# 'from sklearn.pipeline import Pipeline' importa a estrutura que empacota escalador e
# estimador em objeto atômico[cite: 17, 18].
from sklearn.pipeline import Pipeline

# 'from sklearn.preprocessing import StandardScaler' traz o padronizador estatístico por
# Z-score[cite: 17, 18].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import RAIZ_PROJETO, configurar_ambiente

# Importa o estimador campeão homologado com sucesso no pódio da Fase 5 (SVM
# Calibrado)[cite: 22].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)

# Importa o especialista de empacotamento e compressão do Pilar 1 da Fase 6[cite: 17].
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.empacotador_pipeline import (  # noqa: E501
    EmpacotadorPipelineProducao,
)

# Importa o objeto de metadados do Pilar 1 da Fase 6[cite: 17].
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.metadados_modelo import (  # noqa: E501
    MetadadosModeloProducao,
)

# Importa o validador criptográfico para atestar a leitura defensiva do artefato
# salvo[cite: 17].
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.validador_integridade import (  # noqa: E501
    ValidadorIntegridadeArtefato,
)

# 'logging.basicConfig' configura a aparência dos registros no console do terminal com
# data, gravidade e mensagem[cite: 18].
configurar_ambiente()

# '__name__ == "__main__"' garante que este bloco só rode quando o arquivo for executado
# diretamente no terminal[cite: 18].
if __name__ == "__main__":
    # Emite mensagem inicial registrando o início da homologação técnica do Pilar
    # 1[cite: 18].
    logging.info(
        "=== INICIANDO HOMOLOGAÇÃO DO PILAR 1: SERIALIZAÇÃO E INTEGRIDADE (FASE 6)===\n"
    )

    # 1. GERAÇÃO DOS DADOS HOMOLOGADOS DE PRODUÇÃO
    # Gera 600 pacientes com 10 atributos clínicos, sendo 20% da classe positiva de
    # risco cardiovascular[cite: 18].
    x_dados, y_rotulos = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )

    # 2. DEFINIÇÃO ESTRITA DA ORDEM OFICIAL DAS FEATURES (O Contrato da API)
    # Lista com as 10 variáveis clínicas na ordem exata de entrada do Pipeline
    # preditivo[cite: 21, 22].
    atributos_modelo = [
        "Idade_Paciente",
        "Pressao_Sistolica",
        "Colesterol_Total",
        "Frequencia_Cardiaca",
        "Glicemia_Jejum",
        "Indice_Massa_Corporal",
        "Infradesnivel_ST",
        "Historico_Familiar",
        "Nivel_Sedentarismo",
        "Tempo_Internacao_Previo",
    ]

    # 3. AJUSTE DO PIPELINE COMPLETO ATÔMICO
    # Ao preparar para produção, ajustamos o Pipeline (StandardScaler + SVM) sobre toda
    # a base de dados homologada[cite: 17, 24].
    logging.info(
        "Treinando o Pipeline Campeão completo sobre a base total homologada..."
    )
    pipeline_producao = Pipeline(
        [
            ("escalador", StandardScaler()),
            ("estimador", AlgoritmoSVM().construir_estimador(semente_aleatoria=42)),
        ]
    )
    # '.fit(X_dados, y_rotulos)' aprende os parâmetros estatísticos (médias, desvios e
    # hiperplanos de suporte)[cite: 17, 25].
    pipeline_producao.fit(x_dados, y_rotulos)

    # 4. INSTANCIAÇÃO DO OBJETO DE METADADOS DE GOVERNANÇA
    # Registra o nome, a versão semântica, as variáveis exigidas e o limiar de 0.50
    # definido na Fase 5[cite: 17, 20].
    metadados = MetadadosModeloProducao(
        nome_modelo="SVM_Calibrado_Producao",
        versao="v1.0.0",
        nomes_atributos=atributos_modelo,
        limiar_decisao_homologado=0.50,
        responsavel_tecnico="Dr. Arthur - Líder de ML",
    )

    # 5. GRAVAÇÃO COMPRIMIDA NO DISCO COM EMISSÃO DO MANIFESTO E HASH SHA-256
    # Define a pasta física oficial onde os binários residirão no servidor
    # ('artefatos/modelos_producao/')[cite: 18].
    pasta_modelos = RAIZ_PROJETO / "artefatos/modelos_producao"
    # Instancia o empacotador especialista passando a pasta de destino[cite: 17].
    empacotador = EmpacotadorPipelineProducao(pasta_destino_modelos=pasta_modelos)

    # Salva o arquivo binário '.joblib' comprimido e emite o manifesto '.json' com o
    # hash calculado[cite: 17].
    rotas = empacotador.salvar_pipeline_com_manifesto(
        pipeline_campeao=pipeline_producao,
        metadados=metadados,
        nome_arquivo_base="pipeline_svm_calibrado_v1",
    )

    # 6. AUDITORIA DE SEGURANÇA E CONFERÊNCIA PÓS-GRAVAÇÃO
    # Instancia o validador para testar a leitura e comprovar que o arquivo não sofreu
    # corrupção na escrita[cite: 17].
    validador = ValidadorIntegridadeArtefato()
    # Confronta a assinatura recém-gravada contra o manifesto JSON[cite: 17].
    sucesso_validacao = validador.validar_artefato_contra_manifesto(
        caminho_artefato=rotas["caminho_artefato_joblib"],
        caminho_manifesto=rotas["caminho_manifesto_json"],
    )

    # 7. EXIBIÇÃO FORMATADA DOS RESULTADOS DA CERTIFICAÇÃO NO CONSOLE
    print("\n" + "=" * 105)
    print("🔒 CERTIFICADO DE ARTEFATO SERIALIZADO PARA PRODUÇÃO (PILAR 1 - FASE 6)")
    print("=" * 105)
    print(f"📦 Binário Serializado (.joblib): {rotas['caminho_artefato_joblib']}")
    print(f"📜 Manifesto de Governança (.json): {rotas['caminho_manifesto_json']}")
    print(
        f"🛡️ Integridade Criptográfica SHA-256 Auditada:"
        f"{'APROVADA E AUTÊNTICA' if sucesso_validacao else 'REPROVADA'}"
    )
    print("=" * 105 + "\n")

    # Emite log final marcando a conclusão bem-sucedida do Pilar 1 da Fase 6[cite: 18].
    logging.info("=== PILAR 1 DA FASE 6 CONCLUÍDO E HOMOLOGADO COM SUCESSO! ===")
