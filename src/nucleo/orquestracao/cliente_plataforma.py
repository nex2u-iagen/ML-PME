"""Módulo do Cliente da Plataforma (Núcleo de Orquestração).

Responsabilidade Única: Falar com a camada de serviço da plataforma por dois
canais intercambiáveis, sem que o frontend precise saber qual está no ar:

1. **Serviço** — HTTP contra a API FastAPI (``http://localhost:8000``). É o modo
   preferido: os jobs ficam persistidos num processo servidor que sobrevive ao
   recarregamento da página do Streamlit.
2. **Local** — chamada direta ao :class:`ServicoPlataforma` no mesmo processo do
   Streamlit. É o modo de contingência: o console continua operando quando a API
   não está de pé, executando as fases em *threads* dentro do próprio app.

O frontend apenas chama os métodos declarados aqui; a troca de canal é invisível.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.
import logging

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'from typing' oferece anotações de tipagem estática para coleções.
from typing import Any, Dict, List, Optional, Tuple

# Importa o serviço local (mesmo processo) usado como modo de contingência.
from src.nucleo.orquestracao.servico_plataforma import ServicoPlataforma

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


class ClientePlataforma:
    """Fachada de comunicação com a plataforma, comutando entre API e execução local."""

    # 'MODO_SERVICO' e 'MODO_LOCAL' nomeiam os dois canais disponíveis.
    MODO_SERVICO = "servico"
    MODO_LOCAL = "local"

    # 'MARCADOR_FIM_ARQUIVO' delimita o corpo binário em requisições multipart.
    MARCADOR_FIM_ARQUIVO = "----CRISP-DMOperacional"

    def __init__(
        self,
        diretorio_raiz: Path,
        url_base: str = "http://localhost:8000",
        timeout: float = 30.0,
    ) -> None:
        """Inicializa o cliente com a raiz do projeto e o endereço da API.

        Args:
            diretorio_raiz (Path): Caminho absoluto da raiz do projeto.
            url_base (str): Endereço base da API FastAPI.
            timeout (float): Tempo máximo de espera por resposta, em segundos.
        """
        self.diretorio_raiz = Path(diretorio_raiz)
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout

        # Serviço local, instanciado sob demanda apenas quando o modo local é usado.
        self._servico_local: Optional[ServicoPlataforma] = None

        # Modo vigente: detectado automaticamente na primeira consulta.
        self.modo: str = self.MODO_SERVICO
        self.api_disponivel: bool = False

    # ----------------------------------------------------------------------------------
    # CANAIS
    # ----------------------------------------------------------------------------------
    @property
    def servico_local(self) -> ServicoPlataforma:
        """Retorna (criando se necessário) o serviço rodando no mesmo processo."""
        if self._servico_local is None:
            self._servico_local = ServicoPlataforma(diretorio_raiz=self.diretorio_raiz)
        return self._servico_local

    def definir_modo(self, modo: str) -> None:
        """Fixa manualmente o canal de comunicação usado pelas próximas chamadas.

        Args:
            modo (str): ``'servico'`` ou ``'local'``.
        """
        if modo == self.MODO_LOCAL:
            self.modo = self.MODO_LOCAL
            self.api_disponivel = False
        else:
            self.modo = self.MODO_SERVICO
            self.api_disponivel = self._detectar_api()

    def detectar_modo(self) -> str:
        """Sonda a API e escolhe o canal mais conveniente para a sessão.

        Returns:
            str: ``'servico'`` quando a API responde, ``'local'`` caso contrário.
        """
        if self._detectar_api():
            self.modo = self.MODO_SERVICO
            self.api_disponivel = True
        else:
            self.modo = self.MODO_LOCAL
            self.api_disponivel = False
        return self.modo

    def _detectar_api(self) -> bool:
        """Verifica se a API responde com os endpoints da plataforma (G6).

        Verifica não apenas a sonda de prontidão, mas também se o endpoint
        ``/datasets`` está disponível, garantindo que a API em execução tenha
        a camada de serviço agnóstica carregada.

        Returns:
            bool: ``True`` quando a API está operacional com os endpoints G6.
        """
        try:
            status, _ = self._http("GET", "/datasets", timeout=3.0)
            return status == 200
        except Exception:
            return False

    def _http(
        self,
        metodo: str,
        caminho: str,
        corpo_json: Optional[Dict[str, Any]] = None,
        arquivos: Optional[List[Tuple[str, Any]]] = None,
        timeout: Optional[float] = None,
    ) -> Tuple[int, str]:
        """Executa uma requisição HTTP contra a API usando apenas a biblioteca padrão.

        Args:
            metodo (str): Verbo HTTP ('GET', 'POST', 'PUT').
            caminho (str): Caminho do endpoint (sem o endereço base).
            corpo_json (Optional[Dict[str, Any]]): Corpo JSON da requisição.
            arquivos (Optional[List[Tuple[str, Any]]]): Arquivos para envio multipart.
                Cada item é (nome, conteúdo_em_bytes OU objeto_binário_para_leitura).
            timeout (Optional[float]): Tempo máximo de espera específico.

        Returns:
            Tuple[int, str]: Par (código HTTP, corpo textual).
        """
        import json
        import urllib.error
        import urllib.request

        cabecalhos: Dict[str, str] = {}
        dados: Optional[bytes] = None

        if arquivos is not None:
            partes: List[bytes] = []
            for nome, conteudo in arquivos:
                # Se for um objeto binário (não bytes), lê o conteúdo para o multipart.
                # No modo serviço, o limite de 2GB está configurado no config.toml.
                if isinstance(conteudo, (bytes, bytearray)):
                    conteudo_bytes = conteudo
                else:
                    # Resetar ponteiro para garantir leitura completa do arquivo.
                    try:
                        conteudo.seek(0)
                    except (AttributeError, OSError):
                        pass
                    conteudo_bytes = conteudo.read()
                partes.append(
                    f"--{self.MARCADOR_FIM_ARQUIVO}\r\n".encode()
                    + f'Content-Disposition: form-data; name="arquivos"; filename="{nome}"\r\n'.encode()
                    + b"Content-Type: application/octet-stream\r\n\r\n"
                    + conteudo_bytes
                    + b"\r\n"
                )
            partes.append(f"--{self.MARCADOR_FIM_ARQUIVO}--\r\n".encode())
            dados = b"".join(partes)
            cabecalhos["Content-Type"] = (
                f"multipart/form-data; boundary={self.MARCADOR_FIM_ARQUIVO}"
            )
        elif corpo_json is not None:
            dados = json.dumps(corpo_json).encode("utf-8")
            cabecalhos["Content-Type"] = "application/json"

        requisicao = urllib.request.Request(
            f"{self.url_base}{caminho}",
            data=dados,
            headers=cabecalhos,
            method=metodo,
        )

        try:
            with urllib.request.urlopen(
                requisicao, timeout=timeout or self.timeout
            ) as resposta:
                return resposta.status, resposta.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as erro:
            return erro.code, erro.read().decode("utf-8", errors="replace")

    # ----------------------------------------------------------------------------------
    # OPERACOES DE PLATAFORMA
    # ----------------------------------------------------------------------------------
    def listar_datasets(self) -> List[Dict[str, Any]]:
        """Lista os datasets registrados na plataforma.

        Returns:
            List[Dict[str, Any]]: Resumos dos datasets.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http("GET", "/datasets")
            if status == 200:
                import json

                return json.loads(corpo).get("datasets", [])
            logging.warning("API respondeu %s ao listar datasets; usando canal local.", status)

        return self.servico_local.listar_datasets()

    def obter_dataset(self, nome_dataset: str) -> Optional[Dict[str, Any]]:
        """Recupera o resumo de um dataset específico.

        Args:
            nome_dataset (str): Nome do dataset.

        Returns:
            Optional[Dict[str, Any]]: Resumo do dataset ou ``None`` se inexistente.
        """
        for resumo in self.listar_datasets():
            if resumo.get("nome") == nome_dataset:
                return resumo
        return None

    def listar_problemas(self) -> List[Dict[str, Any]]:
        """Lista os 15 templates de problema de negócio.

        Returns:
            List[Dict[str, Any]]: Resumos dos contratos do catálogo.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http("GET", "/problemas")
            if status == 200:
                import json

                return json.loads(corpo).get("problemas", [])

        return self.servico_local.listar_problemas()

    def registrar_upload(self, nome_dataset: str, arquivos: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """Envia os arquivos do dataset para a pasta isolada da PME.

        Tenta primeiro via API (modo serviço). Se a API não estiver disponível
        ou rejeitar a requisição, faz fallback automático para execução local
        (in-process), garantindo que o upload funcione mesmo sem o servidor
        FastAPI em execução.

        Args:
            nome_dataset (str): Nome do dataset (PME).
            arquivos (List[Tuple[str, Any]]): Pares (nome do arquivo, conteúdo em
                bytes ou objeto binário para leitura streaming).

        Returns:
            Dict[str, Any]: Confirmação do upload com o registro atualizado.
        """
        # Tenta via API primeiro (modo serviço).
        if self.modo == self.MODO_SERVICO:
            try:
                status, corpo = self._http(
                    "POST", f"/datasets/{nome_dataset}/upload", arquivos=arquivos
                )
                if status == 200:
                    import json

                    return json.loads(corpo)
                # Se a API rejeitar (404, 400, 500...), faz fallback para local.
                logging.warning(
                    "Upload via API falhou (HTTP %s); fazendo fallback para modo local.",
                    status,
                )
            except Exception as erro_api:
                logging.warning(
                    "Upload via API indisponível (%s); fazendo fallback para modo local.",
                    erro_api,
                )

        # Fallback: execução local (in-process).
        registro = self.servico_local.registrar_upload(nome_dataset, arquivos)
        return registro.resumo_para_frontend()

    def vincular_problema(
        self,
        nome_dataset: str,
        problema: str,
        pergunta_negocio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Vincula um contrato de problema ao dataset.

        Args:
            nome_dataset (str): Dataset alvo.
            problema (str): Identificador do template no catálogo.
            pergunta_negocio (Optional[str]): Pergunta customizada pelo humano.

        Returns:
            Dict[str, Any]: Confirmação com o resumo do contrato vinculado.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http(
                "POST",
                f"/datasets/{nome_dataset}/problema",
                corpo_json={"problema": problema, "pergunta_negocio": pergunta_negocio},
            )
            if status == 200:
                import json

                return json.loads(corpo)
            raise RuntimeError(f"Não foi possível vincular o problema (HTTP {status}): {corpo}")

        registro = self.servico_local.vincular_problema(nome_dataset, problema, pergunta_negocio)
        return {
            "dataset": registro.nome,
            "contrato": registro.contrato_problema.resumo_executivo()
            if registro.contrato_problema
            else None,
        }

    def executar_fase(
        self,
        nome_dataset: str,
        fase: str,
        semente: int = 42,
        problema: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispara a execução assíncrona de uma fase CRISP-DM.

        Args:
            nome_dataset (str): Dataset alvo.
            fase (str): Fase CRISP-DM ('01' a '05').
            semente (int): Semente matemática para reprodutibilidade.
            problema (Optional[str]): Problema de negócio a aplicar.

        Returns:
            Dict[str, Any]: Resumo do job submetido.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http(
                "POST",
                f"/datasets/{nome_dataset}/fases/{fase}/executar",
                corpo_json={"semente": semente, "problema": problema},
            )
            if status == 200:
                import json

                return json.loads(corpo)["job"]
            raise RuntimeError(f"A fase {fase} não foi submetida (HTTP {status}): {corpo}")

        job = self.servico_local.executar_fase(nome_dataset, fase, semente, problema)
        return job.resumo_para_frontend()

    def consultar_job(self, id_job: str) -> Optional[Dict[str, Any]]:
        """Consulta o estado de um job em execução.

        Args:
            id_job (str): Identificador do job.

        Returns:
            Optional[Dict[str, Any]]: Resumo do job ou ``None`` se inexistente.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http("GET", f"/jobs/{id_job}")
            if status == 200:
                import json

                return json.loads(corpo)["job"]
            return None

        job = self.servico_local.gerenciador_jobs.obter(id_job)
        return job.resumo_para_frontend() if job else None

    def obter_top3(self, nome_dataset: str) -> Dict[str, Any]:
        """Recupera o pódio Top 3 do dataset.

        Args:
            nome_dataset (str): Dataset alvo.

        Returns:
            Dict[str, Any]: Pódio com finalistas, métricas e campeão.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http("GET", f"/datasets/{nome_dataset}/top3")
            if status == 200:
                import json

                return json.loads(corpo)

        return self.servico_local.obter_top3(nome_dataset)

    def eleger_campeao(self, nome_dataset: str, nome_modelo: str) -> Dict[str, Any]:
        """Registra a escolha humana do modelo campeão.

        Args:
            nome_dataset (str): Dataset alvo.
            nome_modelo (str): Nome do finalist eleito.

        Returns:
            Dict[str, Any]: Confirmação com o campeão registrado.
        """
        if self.modo == self.MODO_SERVICO:
            status, corpo = self._http(
                "POST", f"/datasets/{nome_dataset}/campeao", corpo_json={"modelo": nome_modelo}
            )
            if status == 200:
                import json

                return json.loads(corpo)
            raise RuntimeError(f"A eleição falhou (HTTP {status}): {corpo}")

        registro = self.servico_local.eleger_campeao(nome_dataset, nome_modelo)
        return {"dataset": registro.nome, "campeao": registro.campeao, "top3": registro.top3}

    def apurar_valor(self, nome_dataset: str) -> Dict[str, Any]:
        """Apura o valor financeiro e a governança do modelo campeão.

        Operação baseada em artefatos em disco, executada sempre no serviço
        local (não depende da API).
        """
        return self.servico_local.apurar_valor(nome_dataset)

    def saude_api(self) -> Optional[Dict[str, Any]]:
        """Consulta a sonda de prontidão da API.

        Returns:
            Optional[Dict[str, Any]]: Estado da API ou ``None`` quando inacessível.
        """
        try:
            status, corpo = self._http("GET", "/saude/prontidao", timeout=3.0)
            if status == 200:
                import json

                return json.loads(corpo)
        except Exception:
            return None
        return None
