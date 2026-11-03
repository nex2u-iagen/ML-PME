"""Módulo do Gerenciador de Jobs Assíncronos (Núcleo de Orquestração).

Responsabilidade Única: Executar as fases CRISP-DM de forma **assíncrona e
persistente**, permitindo que o frontend (Streamlit) dispare uma etapa longa
sem bloquear e consulte o progresso, o log e o resultado posteriormente.

O gerente mantém um registro imutável por execução (persistido em JSON), com
quatro estados canônicos: ``pendente``, ``executando``, ``concluido`` e ``erro``.
Cada execução roda em uma *thread* dedicada, que tanto captura ``stdout``/``stderr``
do processo filho quanto registra o log incrementalmente, permitindo que o
frontend acompanhe a execução ao vivo.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.
import logging

# 'from concurrent.futures' executa as fases em threads sem bloquear o event loop.
from concurrent.futures import ThreadPoolExecutor

# 'from contextlib' redireciona os fluxos padrão durante a execução em thread.
from contextlib import redirect_stderr, redirect_stdout

# 'from datetime' fornece o carimbo temporal ISO para rastreabilidade da execução.
from datetime import datetime, timezone

# 'from enum' declara os estados canônicos do ciclo de vida de um job.
from enum import Enum

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'from typing' oferece anotações de tipagem estática para coleções.
from typing import Any, Callable, Dict, List, Optional

# 'from uuid' gera identificadores únicos e não reutilizáveis para cada job.
from uuid import uuid4

# 'from pydantic' traz o motor de validação de dados com tipagem forte.
from pydantic import BaseModel, Field


class StatusJob(str, Enum):
    """Estados canônicos do ciclo de vida de uma execução assíncrona."""

    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    CONCLUIDO = "concluido"
    ERRO = "erro"


class RegistroJob(BaseModel):
    """Estrutura persistente que descreve uma execução de fase do CRISP-DM."""

    id: str = Field(..., description="Identificador único e opaco do job.")
    dataset: str = Field(..., description="Nome do dataset (PME) alvo da execução.")
    fase: str = Field(..., description="Fase CRISP-DM executada ('01' a '06').")
    descricao: str = Field(default="", description="Descrição legível do job.")
    status: StatusJob = Field(
        default=StatusJob.PENDENTE,
        description="Estado atual da execução.",
    )
    comando: List[str] = Field(
        default_factory=list,
        description="Comando exato executado (vazio quando a execução é in-process).",
    )
    criado_em: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
        description="Carimbo temporal ISO de criação do job.",
    )
    iniciado_em: Optional[str] = Field(
        default=None,
        description="Carimbo temporal ISO de início da execução.",
    )
    finalizado_em: Optional[str] = Field(
        default=None,
        description="Carimbo temporal ISO de encerramento da execução.",
    )
    codigo_retorno: Optional[int] = Field(
        default=None,
        description="Código de saída do processo (0 = sucesso).",
    )
    mensagem: str = Field(
        default="",
        description="Resumo textual do resultado ou da falha.",
    )
    log: List[str] = Field(
        default_factory=list,
        description="Log incremental da execução (stdout + stderr combined).",
    )
    resultado: Dict[str, Any] = Field(
        default_factory=dict,
        description="Payload estruturado devolvido pela execução.",
    )

    def resumo_para_frontend(self) -> Dict[str, Any]:
        """Produz o dicionário compacto consumido pela API e pelo frontend Streamlit."""
        return {
            "id": self.id,
            "dataset": self.dataset,
            "fase": self.fase,
            "descricao": self.descricao,
            "status": self.status.value,
            "criado_em": self.criado_em,
            "iniciado_em": self.iniciado_em,
            "finalizado_em": self.finalizado_em,
            "codigo_retorno": self.codigo_retorno,
            "mensagem": self.mensagem,
            "ultimas_linhas_log": self.log[-40:],
            "total_linhas_log": len(self.log),
        }


class GerenciadorJobs:
    """Fachada responsável por submeter, acompanhar e persistir execuções de fases."""

    # 'MAXIMO_WORKERS' limita o paralelismo para não saturar a CPU da PME.
    MAXIMO_WORKERS = 2

    def __init__(self, diretorio_raiz: Path) -> None:
        """Inicializa o gerente ancorando a pasta oficial de registros de jobs.

        Args:
            diretorio_raiz (Path): Caminho absoluto da raiz do projeto.
        """
        self.diretorio_raiz = Path(diretorio_raiz)
        self.pasta_jobs = self.diretorio_raiz / "dados" / "registros" / "jobs"
        self.pasta_jobs.mkdir(parents=True, exist_ok=True)

        # 'ThreadPoolExecutor' executa os jobs em background sem bloquear a API.
        self.executor = ThreadPoolExecutor(
            max_workers=self.MAXIMO_WORKERS,
            thread_name_prefix="job-cr",
        )

        # Registro em memória, espelhado em disco para tolerância a reinícios.
        self.registros: Dict[str, RegistroJob] = {}
        self._carregar_registros_existentes()

    # ----------------------------------------------------------------------------------
    # PERSISTÊNCIA
    # ----------------------------------------------------------------------------------
    def _caminho_registro(self, id_job: str) -> Path:
        """Monta o caminho absoluto do JSON que persiste um job."""
        return self.pasta_jobs / f"{id_job}.json"

    def _carregar_registros_existentes(self) -> None:
        """Carrega da disco os jobs previamente persistidos, marcando-os como encerrados.

        Jobs que estavam ``executando`` quando o serviço caiu são marcados como
        ``erro``, evitando que o frontend fique eternamente aguardando um
        processo que não existe mais.
        """
        for arquivo in sorted(self.pasta_jobs.glob("*.json")):
            try:
                registro = RegistroJob.model_validate_json(arquivo.read_text(encoding="utf-8"))
                if registro.status in {StatusJob.PENDENTE, StatusJob.EXECUTANDO}:
                    registro.status = StatusJob.ERRO
                    registro.mensagem = "Execução interrompida pelo reinício do serviço."
                    registro.finalizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
                self.registros[registro.id] = registro
            except Exception as erro_leitura:
                logging.error("Registro de job inválido em '%s': %s", arquivo.name, erro_leitura)

    def _persistir(self, registro: RegistroJob) -> None:
        """Grava o estado corrente do job em disco de forma atômica."""
        caminho = self._caminho_registro(registro.id)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(registro.model_dump_json(indent=2), encoding="utf-8")
        temporario.replace(caminho)

    # ----------------------------------------------------------------------------------
    # SUBMISSÃO
    # ----------------------------------------------------------------------------------
    def submeter_comando(
        self,
        dataset: str,
        fase: str,
        comando: List[str],
        descricao: str = "",
        diretorio_trabalho: Optional[Path] = None,
    ) -> RegistroJob:
        """Submete a execução de um comando externo (CLI da fase) em background.

        Args:
            dataset (str): Nome do dataset alvo.
            fase (str): Identificador da fase CRISP-DM ('01' a '06').
            comando (List[str]): Comando completo a executar (sem ``shell=True``).
            descricao (str): Descrição legível exibida no frontend.
            diretorio_trabalho (Optional[Path]): Diretório de trabalho do processo.

        Returns:
            RegistroJob: Registro criado com estado ``pendente``.
        """
        registro = RegistroJob(
            id=f"job_{uuid4().hex[:12]}",
            dataset=dataset,
            fase=fase,
            descricao=descricao or f"Fase {fase} — {dataset}",
            comando=list(comando),
        )
        self.registros[registro.id] = registro
        self._persistir(registro)

        self.executor.submit(
            self._executar_comando,
            registro,
            list(comando),
            Path(diretorio_trabalho) if diretorio_trabalho else self.diretorio_raiz,
        )
        logging.info("Job '%s' submetido — fase %s do dataset '%s'.", registro.id, fase, dataset)
        return registro

    def submeter_funcao(
        self,
        dataset: str,
        fase: str,
        funcao: Callable[..., Any],
        *args: Any,
        descricao: str = "",
        **kwargs: Any,
    ) -> RegistroJob:
        """Submete a execução de uma função Python em background.

        Args:
            dataset (str): Nome do dataset alvo.
            fase (str): Identificador da fase CRISP-DM ('01' a '06').
            funcao (Callable[..., Any]): Função a executar.
            *args: Argumentos posicionais repassados à função.
            descricao (str): Descrição legível exibida no frontend.
            **kwargs: Argumentos nomeados repassados à função.

        Returns:
            RegistroJob: Registro criado com estado ``pendente``.
        """
        registro = RegistroJob(
            id=f"job_{uuid4().hex[:12]}",
            dataset=dataset,
            fase=fase,
            descricao=descricao or f"Fase {fase} — {dataset}",
        )
        self.registros[registro.id] = registro
        self._persistir(registro)

        self.executor.submit(
            self._executar_funcao,
            registro,
            funcao,
            args,
            kwargs,
        )
        logging.info("Job '%s' submetido — fase %s do dataset '%s'.", registro.id, fase, dataset)
        return registro

    # ----------------------------------------------------------------------------------
    # EXECUÇÃO
    # ----------------------------------------------------------------------------------
    def _caminho_log_completo(self, registro: RegistroJob) -> Path:
        """Monta o caminho do arquivo de log completo (tee) do job.

        Além de imprimir cada linha no stdout do processo que executa o job e de
        persisti-la no registro JSON, a mesma linha é gravada em
        ``logs/fases/<id_job>.log`` — permitindo acompanhar a execução ao vivo com
        ``tail -f`` de qualquer terminal, mesmo quando o job roda dentro do
        processo da API (cujo stdout pode estar redirecionado).

        Args:
            registro (RegistroJob): Job dono do arquivo de log.

        Returns:
            Path: Caminho absoluto do arquivo de log do job.
        """
        pasta_fases = self.diretorio_raiz / "logs" / "fases"
        pasta_fases.mkdir(parents=True, exist_ok=True)
        return pasta_fases / f"{registro.id}.log"

    @staticmethod
    def _gravar_em_log_completo(caminho_log: Path, conteudo: str) -> None:
        """Anexa texto ao arquivo de log completo do job (I/O defensivo).

        Args:
            caminho_log (Path): Arquivo de log do job.
            conteudo (str): Texto a anexar ao arquivo.
        """
        try:
            caminho_log.parent.mkdir(parents=True, exist_ok=True)
            with caminho_log.open("a", encoding="utf-8") as arquivo_log:
                arquivo_log.write(conteudo)
        except OSError as erro_arquivo:
            logging.warning("Não foi possível gravar o log completo em '%s': %s", caminho_log, erro_arquivo)

    def _registrar_linha(self, registro: RegistroJob, linha: str) -> None:
        """Acrescenta uma linha ao log incremental do job e persiste o estado."""
        registro.log.append(linha.rstrip())
        self._persistir(registro)

    def _executar_comando(
        self,
        registro: RegistroJob,
        comando: List[str],
        diretorio_trabalho: Path,
    ) -> None:
        """Executa o comando externo, capturando o log linha a linha.

        Args:
            registro (RegistroJob): Registro mutado ao longo da execução.
            comando (List[str]): Comando a executar.
            diretorio_trabalho (Path): Diretório de trabalho do processo.
        """
        import subprocess

        registro.status = StatusJob.EXECUTANDO
        registro.iniciado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._persistir(registro)

        # Tee de log: as mesmas linhas impressas no console também são gravadas em
        # 'logs/fases/<id_job>.log', permitindo 'tail -f' de qualquer terminal.
        caminho_log = self._caminho_log_completo(registro)
        logging.info(
            "Log completo do job '%s' gravado em: %s (acompanhe com 'tail -f').",
            registro.id,
            caminho_log,
        )

        try:
            processo = subprocess.Popen(
                comando,
                cwd=str(diretorio_trabalho),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={**dict(__import__("os").environ), "PYTHONPATH": str(self.diretorio_raiz)},
            )

            if processo.stdout is not None:
                with caminho_log.open("a", encoding="utf-8") as arquivo_log:
                    for linha in processo.stdout:
                        self._registrar_linha(registro, linha)
                        # Também exibir no terminal do processo pai para acompanhamento em tempo real
                        print(linha.rstrip(), flush=True)
                        # E gravar no arquivo de log completo do job (tee).
                        arquivo_log.write(linha if linha.endswith("\n") else f"{linha}\n")
                        arquivo_log.flush()

            codigo = processo.wait()

            registro.codigo_retorno = codigo
            registro.finalizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")

            if codigo == 0:
                registro.status = StatusJob.CONCLUIDO
                registro.mensagem = f"Fase {registro.fase} concluída com sucesso."
            else:
                registro.status = StatusJob.ERRO
                registro.mensagem = f"Fase {registro.fase} encerrou com código {codigo}."

        except Exception as erro_execucao:
            registro.status = StatusJob.ERRO
            registro.mensagem = f"Falha na execução: {erro_execucao}"
            registro.finalizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
            logging.exception("Falha ao executar o job '%s'.", registro.id)
            self._gravar_em_log_completo(caminho_log, f"[FALHA NA EXECUÇÃO] {erro_execucao}\n")

        self._persistir(registro)
        logging.info("Job '%s' finalizado com status '%s'.", registro.id, registro.status.value)

    def _executar_funcao(
        self,
        registro: RegistroJob,
        funcao: Callable[..., Any],
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Executa a função Python em background, capturando o console.

        Args:
            registro (RegistroJob): Registro mutado ao longo da execução.
            funcao (Callable[..., Any]): Função a executar.
            args (tuple): Argumentos posicionais da função.
            kwargs (dict): Argumentos nomeados da função.
        """
        import io

        registro.status = StatusJob.EXECUTANDO
        registro.iniciado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._persistir(registro)

        # Tee de log: o console capturado também é gravado em 'logs/fases/<id_job>.log'.
        caminho_log = self._caminho_log_completo(registro)
        logging.info(
            "Log completo do job '%s' gravado em: %s (acompanhe com 'tail -f').",
            registro.id,
            caminho_log,
        )

        buffer = io.StringIO()

        try:
            with redirect_stdout(buffer), redirect_stderr(buffer):
                resultado = funcao(*args, **kwargs)

            registro.status = StatusJob.CONCLUIDO
            registro.codigo_retorno = 0
            registro.mensagem = f"Fase {registro.fase} concluída com sucesso."
            if isinstance(resultado, dict):
                registro.resultado = resultado

        except Exception as erro_execucao:
            registro.status = StatusJob.ERRO
            registro.codigo_retorno = 1
            registro.mensagem = f"Falha na execução: {erro_execucao}"
            logging.exception("Falha ao executar o job '%s'.", registro.id)

        registro.finalizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")

        console_capturado = buffer.getvalue()
        for linha in console_capturado.splitlines():
            self._registrar_linha(registro, linha)

        # Tee de log: repete o console capturado no arquivo e no terminal do processo pai.
        if console_capturado:
            self._gravar_em_log_completo(caminho_log, console_capturado)
            if not console_capturado.endswith("\n"):
                self._gravar_em_log_completo(caminho_log, "\n")
        if registro.status is StatusJob.ERRO:
            self._gravar_em_log_completo(caminho_log, f"[{registro.mensagem}]\n")
            print(registro.mensagem, flush=True)

        self._persistir(registro)
        logging.info("Job '%s' finalizado com status '%s'.", registro.id, registro.status.value)

    # ----------------------------------------------------------------------------------
    # CONSULTA
    # ----------------------------------------------------------------------------------
    def obter(self, id_job: str) -> Optional[RegistroJob]:
        """Recupera um job pelo identificador.

        Args:
            id_job (str): Identificador do job.

        Returns:
            Optional[RegistroJob]: Registro do job ou ``None`` quando inexistente.
        """
        return self.registros.get(id_job)

    def listar(self, dataset: Optional[str] = None) -> List[RegistroJob]:
        """Lista os jobs conhecidos, opcionalmente filtrando por dataset.

        Args:
            dataset (Optional[str]): Nome do dataset a filtrar.

        Returns:
            List[RegistroJob]: Lista de registros (mais recentes primeiro).
        """
        registros = list(self.registros.values())
        if dataset:
            registros = [registro for registro in registros if registro.dataset == dataset]
        return sorted(registros, key=lambda registro: registro.criado_em, reverse=True)

    def aguardar_conclusao(self, id_job: str, timeout: float = 300.0) -> Optional[RegistroJob]:
        """Aguarda (de forma bloqueante e opcional) a conclusão de um job.

        Args:
            id_job (str): Identificador do job.
            timeout (float): Tempo máximo de espera em segundos.

        Returns:
            Optional[RegistroJob]: Registro final ou ``None`` se o job não existir.
        """
        import time

        registro = self.registros.get(id_job)
        if registro is None:
            return None

        limite = time.monotonic() + timeout
        while time.monotonic() < limite:
            if registro.status in {StatusJob.CONCLUIDO, StatusJob.ERRO}:
                return registro
            time.sleep(0.2)

        return registro
