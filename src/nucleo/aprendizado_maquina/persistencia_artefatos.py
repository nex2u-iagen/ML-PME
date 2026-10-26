"""Módulo de Persistência e Governança de Modelos e Pipelines.

Responsável por serializar artefatos matemáticos em formato binário (.joblib)
e registrar concomitantemente manifestos de metadados em formato legível (.json)
para rastreabilidade operacional, conformidade com a LGPD e governança de MLOps.
"""

# 'from' indica a biblioteca de origem; 'datetime' é a biblioteca nativa do Python para
# lidar com datas e horários.
# 'import' traz a classe 'datetime' (representa ano, mês, dia, hora, minuto e segundo)
# e 'timezone' (que permite fixar o fuso horário oficial, evitando ambiguidades de
# relógio entre servidores).
# 'import' traz o módulo 'json' da biblioteca padrão do Python.
# JSON (JavaScript Object Notation) é um padrão universal de texto estruturado para
# intercâmbio de dados na web.
import json

# 'import' traz o módulo 'logging' da biblioteca padrão do Python.
# Serve para imprimir mensagens com registro de nível (INFO, ERROR) e data/hora no
# console em vez de prints soltos.
import logging
from datetime import UTC, datetime

# 'from' acessa a biblioteca nativa 'pathlib'.
# 'import' traz 'Path', ferramenta moderna orientada a objetos para gerenciar endereços
# de pastas e arquivos no disco.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para documentar os
# tipos de dados esperados.
# 'Any' indica que a variável pode ser de qualquer tipo (número, texto, pipeline ou
# classe).
# 'Dict' documenta que a estrutura esperada é um dicionário contendo pares de chave e
# valor.
from typing import Any

# 'import' traz a biblioteca externa 'joblib', referência de alta performance para
# salvar estruturas de Machine Learning.
# Ela substitui o pickle comum por ser otimizada para salvar matrizes densas e pipelines
# inteiros no disco.
import joblib

# 'logging.basicConfig' configura a aparência dos registros no console.
# 'level=logging.INFO' define que mensagens informativas, avisos e falhas serão exibidos
# no terminal.
# 'format' dita o molde visual: carimbo de data/hora — [gravidade da mensagem] —
# conteúdo do evento.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra reservada para criar uma classe de objetos.
# 'GerenciadorPersistenciaModelos' é o nome da classe em Português do Brasil com
# iniciais maiúsculas (PascalCase).
class GerenciadorPersistenciaModelos:
    """Classe responsável por salvar, carregar e auditar artefatos de Machine
    Learning.
    """

    # O caractere '@' marca um decorador em Python; 'staticmethod' declara que o método
    # é estático.
    # Métodos estáticos realizam tarefas puras sem precisar do parâmetro 'self' ou de
    # instanciar a classe.
    @staticmethod
    # 'def' define a função 'salvar_modelo_com_metadados'.
    # 'objeto_modelo: Any' recebe o pipeline ajustado do Scikit-Learn ou o estimador
    # matemático a ser gravado.
    # 'caminho_artefato: Path' é o caminho físico no disco onde o arquivo .joblib será
    # salvo.
    # 'metadados_governanca: Dict[str, Any]' recebe um dicionário com métricas, nomes de
    # features e sementes.
    # '-> Path' documenta formalmente que a função devolverá o próprio caminho do
    # arquivo gravado no disco.
    def salvar_modelo_com_metadados(
        objeto_modelo: Any,
        caminho_artefato: Path,
        metadados_governanca: dict[str, Any],
    ) -> Path:
        """Serializa o modelo em joblib e gera o arquivo JSON de governança
        correspondente.

        Args:
            objeto_modelo (Any): Objeto do pipeline treinado ou estimador preditivo.
            caminho_artefato (Path): Endereço onde o arquivo binário .joblib será
            persistido.
            metadados_governanca (Dict[str, Any]): Dicionário com informações técnicas
            do modelo.

        Returns:
            Path: Endereço físico do artefato binário gerado e protegido no disco.
        """
        # 'caminho_artefato.parent' extrai o diretório pai onde o arquivo ficará
        # guardado (ex.: 'modelos/').
        # 'mkdir(parents=True, exist_ok=True)' cria a pasta no sistema operacional caso
        # ela ainda não exista.
        caminho_artefato.parent.mkdir(parents=True, exist_ok=True)

        # 'joblib.dump' converte o objeto de aprendizado de máquina em uma cadeia de
        # bytes e salva no disco.
        # Ele compacta a inteligência do modelo, permitindo que seja transportado para
        # servidores ou nuvem.
        joblib.dump(objeto_modelo, caminho_artefato)

        # Emite um log informativo no console confirmando o salvamento bem-sucedido do
        # binário.
        # 'caminho_artefato.name' extrai apenas o nome final do arquivo (ex.:
        # 'pipeline_credito_v1.joblib').
        logging.info(
            "Artefato de ML serializado com sucesso em: %s", caminho_artefato.name
        )

        # 'caminho_artefato.with_suffix(".json")' troca a extensão '.joblib' para
        # '.json' mantendo o mesmo nome base.
        # Isso garante que o manifesto de texto estruturado acompanhe o arquivo binário
        # lado a lado na pasta.
        caminho_manifesto = caminho_artefato.with_suffix(".json")

        # 'manifesto_completo' é uma variável do tipo dicionário construída para reunir
        # os dados de auditoria.
        # 'datetime.now(timezone.utc).isoformat()' gera a data e hora oficial global
        # (UTC) no padrão ISO 8601.
        # '**metadados_governanca' utiliza o operador de desempacotamento de dicionário
        # (duplo asterisco):
        # ele extrai todas as chaves e valores enviados pelo usuário (métricas, colunas)
        # e une no mesmo dicionário.
        manifesto_completo = {
            "data_geracao_utc": datetime.now(UTC).isoformat(),
            "nome_arquivo_modelo": caminho_artefato.name,
            **metadados_governanca,
        }

        # 'with open' abre o arquivo de texto em modo de escrita ('w' = write) com
        # codificação padrão universal UTF-8.
        # Ao término da indentação, o Python fecha o arquivo no sistema operacional
        # automaticamente.
        with open(caminho_manifesto, "w", encoding="utf-8") as ponteiro_arquivo:
            # 'json.dump' converte o dicionário Python em texto formatado dentro do
            # arquivo físico.
            # 'indent=4' organiza o arquivo com indentação de 4 espaços, tornando-o
            # perfeitamente legível para humanos.
            # 'ensure_ascii=False' garante que caracteres com acentos do português (como
            # 'Média') sejam preservados.
            json.dump(
                manifesto_completo, ponteiro_arquivo, indent=4, ensure_ascii=False
            )

        # Registra no log que a etiqueta de auditoria em JSON foi persistida com
        # sucesso.
        logging.info("Manifesto de auditoria registrado em: %s", caminho_manifesto.name)

        # 'return' devolve o caminho do arquivo de modelo para o pipeline de
        # orquestração.
        return caminho_artefato

    # Segundo método estático da classe, focado em recuperar o modelo do disco para uso
    # operacional.
    @staticmethod
    # 'caminho_artefato: Path' exige o caminho do arquivo binário .joblib existente no
    # computador.
    # '-> Any' indica que a função devolverá o objeto de Machine Learning reconstruído e
    # pronto para prever.
    def carregar_modelo(caminho_artefato: Path) -> Any:
        """Carrega o artefato de modelo a partir do disco com checagem defensiva de
        existência.

        Args:
            caminho_artefato (Path): Caminho do arquivo .joblib a ser carregado.

        Returns:
            Any: Objeto do estimador ou pipeline reconstruído e pronto para inferência.

        Raises:
            FileNotFoundError: Se o arquivo especificado não existir fisicamente no
            disco.
        """
        # 'if not' faz a validação defensiva: confere se o arquivo .joblib realmente
        # existe antes de tentar lê-lo.
        if not caminho_artefato.is_file():
            # Emite log no nível de erro alertando sobre a ausência do arquivo.
            logging.error(
                "Arquivo binário de modelo não localizado: %s", caminho_artefato
            )
            # 'raise' interrompe o programa levantando a exceção formal
            # FileNotFoundError com o caminho absoluto.
            raise FileNotFoundError(f"Artefato ausente: {caminho_artefato.resolve()}")

        # Emite log avisando que o carregamento do pipeline começou.
        logging.info("Carregando pipeline de ML a partir de: %s", caminho_artefato.name)

        # 'joblib.load' lê a cadeia de bytes do disco e reconstrói o objeto Python
        # exatamente como ele foi treinado.
        # 'return' devolve o objeto pronto para que você possa chamar métodos como
        # '.predict()' ou '.transform()'.
        return joblib.load(caminho_artefato)

    # Terceiro método estático da classe, dedicado a ler e consultar o manifesto de
    # governança.
    @staticmethod
    # 'caminho_manifesto: Path' exige o caminho do arquivo .json correspondente ao
    # modelo.
    # '-> Dict[str, Any]' avisa formalmente que o método devolverá um dicionário com os
    # metadados.
    def carregar_manifesto(caminho_manifesto: Path) -> dict[str, Any]:
        """Lê o arquivo de manifesto JSON e retorna os metadados do modelo como um
        dicionário.

        Args:
            caminho_manifesto (Path): Endereço físico do arquivo .json de auditoria.

        Returns:
            Dict[str, Any]: Dicionário contendo os parâmetros de governança gravados.

        Raises:
            FileNotFoundError: Caso o arquivo JSON não seja localizado no caminho
            especificado.
        """
        # Checagem defensiva de existência do arquivo de manifesto.
        if not caminho_manifesto.is_file():
            logging.error(
                "Manifesto de auditoria não encontrado: %s", caminho_manifesto
            )
            raise FileNotFoundError(
                f"Manifesto inexistente: {caminho_manifesto.resolve()}"
            )

        # Abre o arquivo JSON em modo de leitura ('r' = read) com suporte a caracteres
        # acentuados.
        with open(caminho_manifesto, encoding="utf-8") as ponteiro_arquivo:
            # 'json.load' lê o texto e o converte de volta em uma estrutura de
            # dicionário Python.
            dados_manifesto: dict[str, Any] = json.load(ponteiro_arquivo)

        # Devolve os dados lidos para inspeção da equipe ou validação de regras de
        # produção.
        return dados_manifesto
