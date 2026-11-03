"""Módulo de Persistência e Governança de Artefactos de Machine Learning (Núcleo Compartilhado).

Responsabilidade Única: Serializar e desserializar pipelines e estimadores treinados
utilizando Joblib, gravando simultaneamente manifestos JSON com metadados de rastreabilidade.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registo estruturado de auditoria.
import logging

# 'import' traz o módulo 'json' da biblioteca padrão para manipulação e persistência de manifestos de governança.
import json

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para gestão de ficheiros no disco.
from pathlib import Path

# 'from' acessa o módulo 'typing' para anotações de tipagem estática rigorosas.
from typing import Any, Dict, Tuple

# 'import' traz a biblioteca externa 'joblib', padrão de alta eficiência para serialização de matrizes e modelos de ML.
import joblib

# 'logging.basicConfig' parametriza a formatação dos avisos técnicos no terminal corporativo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o molde especialista em gestão de ciclo de vida e gravação de modelos.
class GerenciadorPersistenciaModelos:
    """Classe responsável pelo salvamento e carregamento auditável de modelos e pipelines de IA."""

    # 'def' define a função estática encarregada de gravar o modelo e o respetivo manifesto de metadados em disco.
    @staticmethod
    def salvar_modelo_com_metadados(
        objeto_modelo: Any,
        caminho_artefato: Path,
        metadados_governanca: Dict[str, Any],
    ) -> Tuple[Path, Path]:
        """Serializa o modelo em formato .joblib e grava um manifesto .json com os metadados de auditoria.

        Args:
            objeto_modelo (Any): Objeto treinado do Scikit-Learn (Pipeline, ColumnTransformer ou Estimador).
            caminho_artefato (Path): Rota física de destino do modelo serializado (ex.: 'modelos/pipeline.joblib').
            metadados_governanca (Dict[str, Any]): Dicionário com informações de versão, métricas e variáveis.

        Returns:
            Tuple[Path, Path]: Tupla contendo o caminho do ficheiro .joblib e o caminho do ficheiro .json gerados.
        """
        # Garante a criação de pastas intermediárias caso ainda não existam no sistema de ficheiros.
        caminho_artefato.parent.mkdir(parents=True, exist_ok=True)

        # 'joblib.dump()' executa a serialização em binário comprimido de alta velocidade.
        joblib.dump(objeto_modelo, caminho_artefato)

        # Constrói o caminho homólogo para o manifesto de governança alterando a extensão para .json.
        caminho_manifesto = caminho_artefato.with_suffix(".json")

        # Abre o ficheiro de manifesto em modo de escrita com codificação neutra UTF-8.
        with open(caminho_manifesto, mode="w", encoding="utf-8") as ficheiro_json:
            # 'json.dump()' grava o dicionário estruturado com indentação de 4 espaços para alta legibilidade humana.
            json.dump(metadados_governanca, ficheiro_json, indent=4, ensure_ascii=False)

        # 'logging.info' documenta o sucesso da persistência com rastreabilidade nos logs do terminal.
        logging.info(
            "Governança ML: Artefacto binário gravado em '%s' e manifesto em '%s'.",
            caminho_artefato.name,
            caminho_manifesto.name,
        )

        # Retorna a tupla formal com as duas rotas físicas perenes.
        return caminho_artefato, caminho_manifesto

    # 'def' define o método encarregado de restaurar o modelo e os respetivos metadados para inferência.
    @staticmethod
    def carregar_modelo_com_metadados(caminho_artefato: Path) -> Tuple[Any, Dict[str, Any]]:
        """Desserializa o objeto matemático do disco e carrega o respetivo manifesto de governança.

        Args:
            caminho_artefato (Path): Rota do ficheiro .joblib previamente gravado no sistema.

        Returns:
            Tuple[Any, Dict[str, Any]]: Tupla contendo o objeto do modelo carregado em memória e o dicionário de metadados.

        Raises:
            FileNotFoundError: Se o ficheiro binário .joblib não for localizado no endereço fornecido.
        """
        # Checagem defensiva de existência física do ficheiro antes de carregar na memória RAM.
        if not caminho_artefato.is_file():
            logging.error("Persistência ML: Ficheiro de artefacto não encontrado em: %s", caminho_artefato)
            raise FileNotFoundError(f"Modelo não localizado no caminho: {caminho_artefato.resolve()}")

        # 'joblib.load()' desserializa o grafo de computação do Scikit-Learn de volta para a memória RAM.
        objeto_modelo = joblib.load(caminho_artefato)

        # Localiza o caminho correspondente do ficheiro JSON de metadados.
        caminho_manifesto = caminho_artefato.with_suffix(".json")
        metadados: Dict[str, Any] = {}

        # Se o manifesto existir fisicamente, efetua a leitura da documentação de governança.
        if caminho_manifesto.is_file():
            with open(caminho_manifesto, mode="r", encoding="utf-8") as ficheiro_json:
                metadados = json.load(ficheiro_json)

        # Regista no console a restauração bem-sucedida do estimador em memória operacional.
        logging.info("Governança ML: Modelo '%s' restaurado com sucesso em memória.", caminho_artefato.name)

        # Retorna o modelo e os respetivos metadados para produção ou avaliação.
        return objeto_modelo, metadados