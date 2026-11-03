"""Módulo de Metadados e Manifesto de Governança do Modelo (Pilar 1 - Fase 6).

Responsabilidade Única: Encapsular os parâmetros fundamentais de certificação
operacional (nome do algoritmo, versão semântica, autor da homologação, limiar
de corte ótimo e lista ordenada de atributos preditores) e persistir a ficha
técnica em formato JSON no disco com integridade física e rastreabilidade[cite: 17, 21].
"""

# 'from' navega no pacote padrão de tipagem; 'import' carrega 'Any', 'Dict' e 'List'
# para anotações estáticas de tipos.
# 'import' carrega o módulo 'json' da biblioteca padrão do Python para conversão de
# dicionários em texto estruturado[cite: 18].
import json

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz a classe 'Path' para
# manipulação orientada a objetos de arquivos[cite: 18].
from pathlib import Path
from typing import Any


# 'class' define o molde orientado a objetos; 'MetadadosModeloProducao' é o objeto de
# domínio do manifesto técnico.
class MetadadosModeloProducao:
    """Classe responsável por gerenciar e registrar o certificado de governança de
    modelos homologados[cite: 17, 20].
    """

    # 'def' define um método; '__init__' é o método construtor invocado no instante em
    # que o objeto nasce na memória RAM[cite: 18].
    # 'self' referencia a própria instância alocada; parâmetros anotados com tipagem
    # estrita para validação de contrato[cite: 18, 24].
    def __init__(
        self,
        nome_modelo: str,
        versao: str,
        nomes_atributos: list[str],
        limiar_decisao_homologado: float = 0.50,
        responsavel_tecnico: str = "Dr. Arthur - Staff Data Scientist",
    ) -> None:
        """Inicializa os metadados de certificação operacional do modelo preditivo[cite:
        17, 21].

        Args:
            nome_modelo (str): Identificador textual do algoritmo aprovado (ex.:
            'SVM_Calibrado_Producao')[cite: 22].
            versao (str): Versão semântica oficial da entrega para controle de releases
            (ex.: 'v1.0.0')[cite: 21].
            nomes_atributos (List[str]): Lista na ordem canônica estrita das colunas
            exigidas pelo modelo.
            limiar_decisao_homologado (float): Ponto de corte ótimo definido na
            avaliação para mitigar negligência[cite: 18, 21].
            responsavel_tecnico (str): Assinatura nominal da autoridade técnica que
            homologou a solução[cite: 21].
        """
        # 'if not' faz a validação defensiva verificando se a lista de variáveis
        # preditoras está nula ou vazia[cite: 18].
        if not nomes_atributos or len(nomes_atributos) == 0:
            # 'raise' interrompe o fluxo de execução levantando uma exceção de valor
            # inválido no sistema.
            raise ValueError(
                "Erro de Integridade: A lista de atributos do modelo não pode servazia."
            )

        # 'if not' assegura que a probabilidade de corte do limiar permaneça
        # estritamente no intervalo biológico e matemático válido[cite: 18].
        if not (0.0 < limiar_decisao_homologado < 1.0):
            # 'raise' barra a criação de instâncias com limiares matematicamente
            # impossíveis no mundo real[cite: 24].
            raise ValueError(
                "Erro de Conformidade: O limiar de decisão deve estar estritamente"
                "entre 0.0 e 1.0."
            )

        # 'self.nome_modelo' cria e vincula o atributo de instância que guarda o nome do
        # modelo na memória do objeto[cite: 18].
        self.nome_modelo = nome_modelo

        # 'self.versao' armazena a versão semântica de entrega para governança e
        # controle de versão de software[cite: 21].
        self.versao = versao

        # 'self.nomes_atributos' guarda a sequência exata de variáveis que alimentam as
        # matrizes matemáticas do pipeline[cite: 18, 21].
        self.nomes_atributos = nomes_atributos

        # 'float(...)' converte o valor explicitamente para número de ponto flutuante
        # com precisão decimal[cite: 18, 24].
        self.limiar_decisao = float(limiar_decisao_homologado)

        # 'self.responsavel' grava a identificação do cientista de dados ou engenheiro
        # responsável pela homologação[cite: 21].
        self.responsavel = responsavel_tecnico

    # 'def' define o método especialista encarregado de montar o dicionário estruturado
    # e persistir o arquivo JSON no disco.
    def salvar_manifesto(
        self, hash_sha256: str, arquivo_artefato: str, caminho_destino_json: Path
    ) -> Path:
        """Monta a estrutura de governança do modelo e grava o arquivo de manifesto JSON
        no disco[cite: 17, 21].

        Args:
            hash_sha256 (str): Impressão digital criptográfica de 64 caracteres do
            arquivo binário joblib[cite: 17].
            arquivo_artefato (str): Nome do arquivo físico comprimido correspondente
            (ex: 'pipeline_svm.joblib')[cite: 17].
            caminho_destino_json (Path): Endereço físico completo onde o arquivo JSON
            deve ser criado no disco[cite: 18].

        Returns:
            Path: Objeto Path com a rota física confirmada do arquivo de manifesto JSON
            persistido[cite: 18].
        """
        # 'manifesto: Dict[str, Any]' declara a variável com anotação estática de
        # dicionário com chaves em texto e valores heterogêneos[cite: 18].
        # Cria a estrutura de dados chave-valor para empacotamento das propriedades do
        # certificado[cite: 18].
        manifesto: dict[str, Any] = {
            # 'modelo': armazena o identificador canônico do algoritmo aprovado no pódio
            # da Fase 5[cite: 21].
            "modelo": self.nome_modelo,
            # 'versao': registra o identificador de release para prevenir regressão de
            # modelos em produção[cite: 21].
            "versao": self.versao,
            # 'autor_homologacao': grava formalmente o responsável técnico para
            # rastreabilidade de conformidade[cite: 21].
            "autor_homologacao": self.responsavel,
            # 'arquivo_artefato': guarda o nome exato do arquivo binário que contém os
            # pesos e escaladores treinados[cite: 17].
            "arquivo_artefato": arquivo_artefato,
            # 'hash_sha256': armazena a impressão digital calculada para impedir a carga
            # de arquivos adulterados[cite: 17].
            "hash_sha256": hash_sha256,
            # 'limiar_decisao_homologado': registra o ponto de corte ótimo de
            # probabilidade validado no teste de holdout[cite: 18].
            "limiar_decisao_homologado": self.limiar_decisao,
            # 'total_atributos_esperados': contagem inteira de variáveis necessárias
            # para a predição[cite: 21, 22].
            "total_atributos_esperados": len(self.nomes_atributos),
            # 'ordem_atributos': vetor ordenado com os nomes de cada coluna exigida pelo
            # estimador[cite: 21, 22].
            "ordem_atributos": self.nomes_atributos,
        }

        # 'with' abre o gerenciador de contexto do Python garantindo o fechamento
        # automático do arquivo mesmo sob erros[cite: 24].
        # 'open(...)' requisita ao sistema operacional a abertura do fluxo de
        # comunicação com o arquivo no disco[cite: 24].
        # 'caminho_destino_json': o caminho físico onde o arquivo de texto será
        # gravado[cite: 18].
        # '"w"' (Write Mode): modo de escrita destrutiva, criando o arquivo se não
        # existir ou limpando-o se já existir[cite: 24].
        # 'encoding="utf-8"': define a tabela de caracteres Unicode de 8 bits para
        # suportar acentos sem corrupção no Linux/Windows[cite: 24, 25].
        # 'as arquivo': vincula o fluxo de I/O aberto à variável de escopo local
        # 'arquivo'[cite: 24].
        with open(caminho_destino_json, "w", encoding="utf-8") as arquivo:
            # 'json.dump(...)' executa a serialização convertendo o dicionário Python
            # diretamente no fluxo aberto de arquivo[cite: 18].
            # 'manifesto': a fonte de dados na memória RAM a ser traduzida em texto
            # JSON[cite: 18].
            # 'arquivo': o descritor de arquivo aberto que recebe o fluxo de bytes
            # gravados no disco[cite: 24].
            # 'indent=4': aplica 4 espaços de tabulação em cada nível do JSON para
            # facilitar a inspeção humana[cite: 24].
            # 'ensure_ascii=False': impede a conversão de acentos em sequências de
            # escape unicode como \u00e1[cite: 24].
            json.dump(manifesto, arquivo, indent=4, ensure_ascii=False)

        # 'return' devolve o caminho do arquivo gravado para que os orquestradores
        # registrem logs de auditoria[cite: 18].
        return caminho_destino_json
