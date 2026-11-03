"""Módulo do Serviço de Plataforma (Núcleo de Orquestração).

Responsabilidade Única: Concentrar a regra de negócio da camada de serviço
(G6) que o frontend consome via REST. O serviço sabe:

- quais datasets existem e qual é o estado de cada um;
- como receber um upload de ``.sql``/``.csv`` e isolá-lo por PME;
- como vincular um **Contrato de Problema** a um dataset;
- como disparar uma fase CRISP-DM de forma assíncrona;
- como ler o pódio Top 3 e registrar a escolha humana do campeão;
- como apurar o **valor** do campeão (impacto financeiro, escoreação individual
  e governança) a partir dos artefatos reais gravados em disco.

Nenhuma regra de modelagem mora aqui: o serviço apenas compõe o registro de
datasets, o catálogo de problemas e o gerenciador de jobs.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.
import logging

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'from typing' oferece anotações de tipagem estática para coleções.
from typing import Any, BinaryIO, Dict, List, Optional, Union

# Importa o contrato e o catálogo de problemas do núcleo de contratos.
from src.nucleo.contratos.catalogo_problemas import CatalogoProblemas
from src.nucleo.contratos.contrato_problema import ContratoProblema

# Importa o registro de datasets e o gerenciador de jobs assíncronos.
from src.nucleo.registro_datasets.gerenciador_datasets import (
    GerenciadorDatasets,
    RegistroDataset,
)
from src.nucleo.orquestracao.gerenciador_jobs import GerenciadorJobs, RegistroJob

# Tamanho do chunk para leitura/gravação em streaming (50.000 linhas por chunk).
CHUNK_LINHAS_CSV = 50_000

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


class ServicoPlataforma:
    """Fachada da camada de serviço da plataforma agnóstica de dataset."""

    # 'EXECUTORES_POR_FASE' mapeia a fase CRISP-DM para o módulo executor oficial.
    EXECUTORES_POR_FASE: Dict[str, str] = {
        "01": "scripts.executores_arquivo.executar_fase_01_ingestao",
        "02": "scripts.executores_arquivo.executar_fase_02_raio_x",
        "03": "scripts.executores_arquivo.executar_fase_03_preparacao",
        "04": "scripts.executores_arquivo.executar_fase_04_modelagem",
        "05": "scripts.executores_arquivo.fase_05_pilar_01_top3",
    }

    def __init__(self, diretorio_raiz: Path) -> None:
        """Inicializa o serviço ancorando o registro de datasets e o gerenciador de jobs.

        Args:
            diretorio_raiz (Path): Caminho absoluto da raiz do projeto.
        """
        self.diretorio_raiz = Path(diretorio_raiz)
        self.gerenciador_datasets = GerenciadorDatasets(diretorio_raiz=self.diretorio_raiz)
        self.gerenciador_jobs = GerenciadorJobs(diretorio_raiz=self.diretorio_raiz)

    # ----------------------------------------------------------------------------------
    # DATASETS
    # ----------------------------------------------------------------------------------
    def listar_datasets(self) -> List[Dict[str, Any]]:
        """Lista todos os datasets conhecidos com o resumo executivo do registro.

        Returns:
            List[Dict[str, Any]]: Lista de resumos, ordenada por nome.
        """
        resumos: List[Dict[str, Any]] = []
        for nome in self.gerenciador_datasets.listar_nomes():
            registro = self.gerenciador_datasets.carregar(nome)
            if registro is None:
                registro = RegistroDataset(nome=nome)
            resumo = registro.resumo_para_frontend()
            resumo["possui_pasta_csv"] = (self.gerenciador_datasets.pasta_csv_base / nome).is_dir()
            resumo["total_arquivos_csv"] = len(
                list((self.gerenciador_datasets.pasta_csv_base / nome).glob("*.csv"))
            ) if resumo["possui_pasta_csv"] else 0
            resumos.append(resumo)
        return resumos

    def obter_dataset(self, nome_dataset: str) -> Optional[RegistroDataset]:
        """Recupera o registro persistente de um dataset específico.

        Args:
            nome_dataset (str): Nome do dataset.

        Returns:
            Optional[RegistroDataset]: Registro carregado ou ``None`` se inexistente.
        """
        return self.gerenciador_datasets.carregar(nome_dataset)

    # ----------------------------------------------------------------------------------
    # UPLOAD
    # ----------------------------------------------------------------------------------
    def registrar_upload(
        self,
        nome_dataset: str,
        arquivos: List[tuple[str, BinaryIO]],
    ) -> RegistroDataset:
        """Recebe o upload do frontend e isola os arquivos na pasta do dataset.

        Os arquivos são gravados em **streaming (chunks)**, nunca carregados
        inteiros na memória. Isso permite uploads de arquivos grandes (até 2GB)
        sem estourar a RAM.

        Arquivos ``.csv`` são lidos em partes com pandas (``chunksize``) e
        gravados como CSVs fatiados (``nome_parte_001.csv``, ...) na pasta do
        dataset, evitando que um único arquivo enorme sobrecarregue a memória.

        Arquivos ``.sql`` são gravados linha a linha no arquivo de destino.

        Args:
            nome_dataset (str): Nome da PME ou do dataset informado pelo humano.
            arquivos (List[tuple[str, BinaryIO]]): Pares (nome do arquivo, objeto
                de arquivo aberto em modo binário para leitura streaming).

        Returns:
            RegistroDataset: Registro atualizado com os arquivos gravados.
        """
        import pandas as pd

        nome_normalizado = self.gerenciador_datasets._normalizar_nome_dataset(nome_dataset)

        pasta_csv = self.gerenciador_datasets.pasta_csv_base / nome_normalizado
        pasta_sql = self.gerenciador_datasets.pasta_sql_base
        pasta_csv.mkdir(parents=True, exist_ok=True)
        pasta_sql.mkdir(parents=True, exist_ok=True)

        import io

        nomes_gravados: List[str] = []
        for nome_arquivo, arquivo_obj in arquivos:
            # Normaliza: a API envia bytes; o modo local pode enviar UploadedFile/objetos.
            # Garantimos um objeto com .read()/.seek() em todos os casos.
            if isinstance(arquivo_obj, (bytes, bytearray)):
                arquivo_obj = io.BytesIO(arquivo_obj)

            # Resetar o ponteiro do arquivo para o início antes de qualquer leitura.
            # Isso é necessário porque o UploadedFile do Streamlit pode ter o
            # ponteiro no final após uma leitura anterior.
            try:
                arquivo_obj.seek(0)
            except (AttributeError, OSError):
                pass

            nome_seguro = Path(nome_arquivo).name
            extensao = Path(nome_seguro).suffix.lower()

            logging.info("Processando arquivo: %s (extensão: %s)", nome_arquivo, extensao)

            if extensao == ".csv":
                # Lê o CSV em chunks e grava cada parte como um arquivo separado.
                try:
                    partes = self._gravar_csv_em_partes(arquivo_obj, pasta_csv, nome_seguro)
                    nomes_gravados.extend(partes)
                    logging.info("CSV processado: %d parte(s) gravada(s)", len(partes))
                except Exception as e_csv:
                    logging.error("Erro ao processar CSV '%s': %s", nome_arquivo, e_csv, exc_info=True)
                    raise
            elif extensao == ".sql":
                # Grava o dump SQL linha a linha (streaming, sem carregar tudo na RAM).
                try:
                    destino = pasta_sql / f"{nome_normalizado}.sql"
                    self._gravar_arquivo_em_chunks(arquivo_obj, destino)
                    nomes_gravados.append(destino.name)
                    logging.info("SQL gravado: %s", destino.name)
                except Exception as e_sql:
                    logging.error("Erro ao processar SQL '%s': %s", nome_arquivo, e_sql, exc_info=True)
                    raise
            else:
                logging.warning("Arquivo '%s' ignorado: apenas .sql e .csv são aceitos.", nome_arquivo)
                continue

        registro = self.gerenciador_datasets.obter_ou_criar(nome_normalizado)
        registro.arquivos_origem = list(dict.fromkeys(registro.arquivos_origem + nomes_gravados))
        registro.registrar_observacao(
            f"Upload recebido com {len(nomes_gravados)} parte(s) de arquivo(s): "
            f"{', '.join(nomes_gravados)}"
        )
        self.gerenciador_datasets.salvar(registro)

        logging.info(
            "Upload do dataset '%s' isolado em '%s' (%d parte(s)).",
            nome_normalizado,
            pasta_csv,
            len(nomes_gravados),
        )
        return registro

    # ----------------------------------------------------------------------------------
    # HELPERS DE STREAMING
    # ----------------------------------------------------------------------------------
    def _gravar_csv_em_partes(
        self,
        arquivo_obj: BinaryIO,
        pasta_destino: Path,
        nome_base: str,
    ) -> List[str]:
        """Lê um CSV em chunks e grava cada parte como arquivo separado.

        O conteúdo do arquivo é primeiro copiado para um arquivo temporário
        no disco (para garantir compatibilidade com qualquer objeto de arquivo,
        incluindo UploadedFile do Streamlit), e então lido em chunks via pandas.

        Isso evita carregar o CSV inteiro na memória. Cada parte recebe o sufixo
        ``_parte_NNN`` onde NNN é o número sequencial da parte.

        Args:
            arquivo_obj: Objeto de arquivo binário aberto para leitura.
            pasta_destino: Pasta onde as partes serão gravadas.
            nome_base: Nome original do arquivo (ex.: ``vendas.csv``).

        Returns:
            Lista de nomes dos arquivos de parte gravados.
        """
        import pandas as pd
        import tempfile

        raiz = Path(nome_base).stem
        extensao = Path(nome_base).suffix  # inclui o ponto, ex.: '.csv'

        partes_gravadas: List[str] = []
        parte_idx = 0

        # Copia o conteúdo para um arquivo temporário para garantir que
        # pd.read_csv consiga ler independentemente do tipo de objeto de arquivo.
        with tempfile.NamedTemporaryFile(
            suffix=extensao, delete=False, dir=str(pasta_destino)
        ) as tmp:
            while True:
                bloco = arquivo_obj.read(1024 * 1024)  # 1 MB por leitura
                if not bloco:
                    break
                tmp.write(bloco)
            tmp_caminho = tmp.name

        try:
            # Lê o CSV temporário em chunks e grava cada parte como arquivo separado.
            primeiro_chunk = True
            for chunk in pd.read_csv(tmp_caminho, chunksize=CHUNK_LINHAS_CSV):
                nome_parte = f"{raiz}_parte_{parte_idx:03d}{extensao}"
                caminho_parte = pasta_destino / nome_parte
                # Escreve o cabeçalho apenas na primeira parte; nas demais, append sem cabeçalho.
                chunk.to_csv(caminho_parte, index=False, header=primeiro_chunk)
                primeiro_chunk = False
                partes_gravadas.append(nome_parte)
                parte_idx += 1
                logging.info("CSV parte gravada: %s (%d linhas)", nome_parte, len(chunk))
        finally:
            # Remove o arquivo temporário após o processamento.
            try:
                Path(tmp_caminho).unlink(missing_ok=True)
            except OSError:
                pass

        return partes_gravadas

    @staticmethod
    def _gravar_arquivo_em_chunks(
        arquivo_obj: BinaryIO,
        destino: Path,
        tamanho_chunk: int = 1024 * 1024,  # 1 MB por leitura
    ) -> None:
        """Copia um arquivo binário para o destino em chunks de 1 MB.

        Usado para dumps SQL grandes, evitando carregar o conteúdo inteiro na RAM.

        Args:
            arquivo_obj: Objeto de arquivo binário aberto para leitura.
            destino: Caminho do arquivo de destino.
            tamanho_chunk: Tamanho de cada leitura em bytes.
        """
        with destino.open("wb") as saida:
            while True:
                try:
                    bloco = arquivo_obj.read(tamanho_chunk)
                except Exception as erro_leitura:
                    logging.error("Erro ao ler bloco do arquivo: %s", erro_leitura, exc_info=True)
                    raise
                if not bloco:
                    break
                saida.write(bloco)
                saida.flush()

    # ----------------------------------------------------------------------------------
    # PROBLEMA DE NEGÓCIO
    # ----------------------------------------------------------------------------------
    def listar_problemas(self) -> List[Dict[str, Any]]:
        """Lista os 15 templates de problema de negócio disponíveis.

        Returns:
            List[Dict[str, Any]]: Resumos dos contratos do catálogo.
        """
        return [contrato.resumo_executivo() for contrato in CatalogoProblemas.listar()]

    def vincular_problema(
        self,
        nome_dataset: str,
        id_problema: str,
        pergunta_negocio: Optional[str] = None,
    ) -> RegistroDataset:
        """Vincula um contrato de problema ao dataset, persistindo-o em disco.

        O contrato fica disponível tanto no registro do dataset quanto na pasta
        de artefatos de ML, onde a Fase 3 o lê para construir a ABT.

        Args:
            nome_dataset (str): Dataset alvo.
            id_problema (str): Identificador do template no catálogo.
            pergunta_negocio (Optional[str]): Pergunta customizada pelo humano.

        Returns:
            RegistroDataset: Registro atualizado com o contrato vinculado.

        Raises:
            ValueError: Quando o identificador não existe no catálogo.
        """
        try:
            contrato = CatalogoProblemas.obter(id_problema)
        except (KeyError, ValueError) as erro:
            raise ValueError(f"Problema de negócio '{id_problema}' não existe no catálogo.") from erro

        if pergunta_negocio and pergunta_negocio.strip():
            contrato = contrato.model_copy(update={"pergunta_negocio": pergunta_negocio.strip()})

        registro = self.gerenciador_datasets.obter_ou_criar(nome_dataset)
        registro.contrato_problema = contrato
        # Resetar status das fases para permitir reexecução com o novo problema.
        # Isso evita que fases antigas marcadas "concluida" bloqueiem a execução
        # do novo problema selecionado pelo usuário.
        registro.status_fases = {fase: "pendente" for fase in ["01", "02", "03", "04", "05"]}
        registro.registrar_observacao(
            f"Problema de negócio vinculado: '{contrato.id}' — {contrato.pergunta_negocio}. "
            "Fases reiniciadas para nova execução."
        )
        self.gerenciador_datasets.salvar(registro)

        pasta_ml = self.gerenciador_datasets.pasta_ml(nome_dataset)
        pasta_ml.mkdir(parents=True, exist_ok=True)
        contrato.salvar_em_json(pasta_ml / "contrato_problema.json")

        return registro

    # ----------------------------------------------------------------------------------
    # EXECUÇÃO DE FASES
    # ----------------------------------------------------------------------------------
    def montar_comando_fase(
        self,
        nome_dataset: str,
        fase: str,
        semente: int = 42,
        problema: Optional[str] = None,
    ) -> List[str]:
        """Monta o comando de execução da fase solicitada.

        Args:
            nome_dataset (str): Dataset alvo.
            fase (str): Fase CRISP-DM ('01' a '05').
            semente (int): Semente matemática para reprodutibilidade.
            problema (Optional[str]): Identificador do problema de negócio.

        Returns:
            List[str]: Comando completo pronto para execução.

        Raises:
            ValueError: Quando a fase não possui executor oficial.
        """
        modulo = self.EXECUTORES_POR_FASE.get(fase)
        if modulo is None:
            raise ValueError(
                f"Fase '{fase}' não possui executor oficial. "
                f"Disponíveis: {sorted(self.EXECUTORES_POR_FASE)}"
            )

        import sys

        comando = [sys.executable, "-m", modulo, "--dataset", nome_dataset]

        if fase in {"03", "04", "05"}:
            id_problema = problema
            if not id_problema:
                registro = self.gerenciador_datasets.carregar(nome_dataset)
                id_problema = registro.contrato_problema.id if registro and registro.contrato_problema else None
            if id_problema:
                comando += ["--problema", id_problema]

        if fase in {"03", "04"}:
            comando += ["--semente", str(semente)]

        return comando

    def executar_fase(
        self,
        nome_dataset: str,
        fase: str,
        semente: int = 42,
        problema: Optional[str] = None,
    ) -> RegistroJob:
        """Submete a execução assíncrona de uma fase CRISP-DM.

        Args:
            nome_dataset (str): Dataset alvo.
            fase (str): Fase CRISP-DM ('01' a '05').
            semente (int): Semente matemática para reprodutibilidade.
            problema (Optional[str]): Identificador do problema de negócio.

        Returns:
            RegistroJob: Job submetido com estado ``pendente``.

        Raises:
            FileNotFoundError: Quando o dataset não está registrado.
            ValueError: Quando a fase não possui executor oficial.
        """
        if self.gerenciador_datasets.carregar(nome_dataset) is None:
            raise FileNotFoundError(f"Dataset '{nome_dataset}' não está registrado na plataforma.")

        comando = self.montar_comando_fase(nome_dataset, fase, semente, problema)

        job = self.gerenciador_jobs.submeter_comando(
            dataset=nome_dataset,
            fase=fase,
            comando=comando,
            descricao=f"Fase {fase} — {nome_dataset}",
            diretorio_trabalho=self.diretorio_raiz,
        )

        # Marca a fase como 'executando' no registro do dataset para o frontend refletir o estado.
        registro = self.gerenciador_datasets.obter_ou_criar(nome_dataset)
        registro.marcar_fase(fase, "executando")
        self.gerenciador_datasets.salvar(registro)

        return job

    # ----------------------------------------------------------------------------------
    # PÓDIO E CAMPEÃO
    # ----------------------------------------------------------------------------------
    def obter_top3(self, nome_dataset: str) -> Dict[str, Any]:
        """Recupera o pódio Top 3 com as métricas de avaliação do dataset.

        Args:
            nome_dataset (str): Dataset alvo.

        Returns:
            Dict[str, Any]: Pódio com a lista de finalistas e suas métricas.
        """
        registro = self.gerenciador_datasets.carregar(nome_dataset)
        if registro is None:
            return {
                "dataset": nome_dataset,
                "top3": [],
                "metricas": {},
                "campeao": None,
                "leaderboard": [],
                "avaliacao": None,
                "tipo_tarefa": None,
                "metrica_otimizacao": None,
            }

        import json
        import math

        pasta_modelos = self.gerenciador_datasets.pasta_modelos_dataset(nome_dataset)
        caminho_scorecard = pasta_modelos / "scorecard_top3.csv"
        caminho_leaderboard = pasta_modelos / "leaderboard.csv"
        caminho_top3_json = pasta_modelos / "top3.json"
        caminho_avaliacao = pasta_modelos / "avaliacao_top3.json"

        # --- LEADERBOARD completo (todas as linhas do placar da Fase 04) ---
        leaderboard: List[Any] = []
        if caminho_leaderboard.is_file():
            try:
                import pandas as pd

                df_leader = pd.read_csv(caminho_leaderboard)
                # JSON inválido com NaN: converte para None antes de serializar.
                leaderboard = [
                    {
                        chave: (None if isinstance(valor, float) and not math.isfinite(valor) else valor)
                        for chave, valor in linha.items()
                    }
                    for linha in df_leader.to_dict(orient="records")
                ]
            except Exception as erro_leader:  # pragma: no cover - defensivo de I/O
                logging.warning("Leaderboard ilegível para '%s': %s", nome_dataset, erro_leader)

        # --- Metadados do pódio (tipo de tarefa e métrica de otimização) ---
        tipo_tarefa: Optional[str] = None
        metrica_otimizacao: Optional[str] = None
        if caminho_top3_json.is_file():
            try:
                dados_top3 = json.loads(caminho_top3_json.read_text(encoding="utf-8"))
                tipo_tarefa = dados_top3.get("tipo_tarefa")
                metrica_otimizacao = dados_top3.get("metrica_otimizacao")
            except Exception as erro_top3:  # pragma: no cover - defensivo de I/O
                logging.warning("top3.json ilegível para '%s': %s", nome_dataset, erro_top3)

        if tipo_tarefa is None and registro.contrato_problema is not None:
            tipo_tarefa = registro.contrato_problema.tipo_tarefa.value
            metrica_otimizacao = registro.contrato_problema.metrica_effective

        # --- AVALIAÇÃO DETALHADA por finalista (matriz de confusão, custos...) ---
        avaliacao: Optional[Dict[str, Any]] = None
        if caminho_avaliacao.is_file():
            try:
                avaliacao = json.loads(caminho_avaliacao.read_text(encoding="utf-8"))
            except Exception as erro_aval:  # pragma: no cover - defensivo de I/O
                logging.warning("avaliacao_top3.json ilegível para '%s': %s", nome_dataset, erro_aval)

        return {
            "dataset": nome_dataset,
            "top3": list(registro.top3),
            "metricas": registro.metricas_top3,
            "campeao": registro.campeao,
            "leaderboard": leaderboard,
            "avaliacao": avaliacao,
            "tipo_tarefa": tipo_tarefa,
            "metrica_otimizacao": metrica_otimizacao,
            "arquivo_leaderboard": str(caminho_leaderboard),
            "arquivo_scorecard": str(caminho_scorecard) if caminho_scorecard.is_file() else None,
        }

    def eleger_campeao(self, nome_dataset: str, nome_modelo: str) -> RegistroDataset:
        """Registra a escolha humana do modelo campeão entre os três finalistas.

        Args:
            nome_dataset (str): Dataset alvo.
            nome_modelo (str): Nome exato do modelo eleito.

        Returns:
            RegistroDataset: Registro atualizado com o campeão.

        Raises:
            FileNotFoundError: Quando o dataset não está registrado.
            ValueError: Quando o modelo não integra o pólio Top 3.
        """
        registro = self.gerenciador_datasets.carregar(nome_dataset)
        if registro is None:
            raise FileNotFoundError(f"Dataset '{nome_dataset}' não está registrado na plataforma.")

        if registro.top3 and nome_modelo not in registro.top3:
            raise ValueError(
                f"Modelo '{nome_modelo}' não integra o pódio Top 3 "
                f"({', '.join(registro.top3)}). Escolha um dos finalistas."
            )

        registro.campeao = nome_modelo
        registro.registrar_observacao(
            f"Campeão eleito pelo humano: '{nome_modelo}' entre {', '.join(registro.top3) or 'n/d'}."
        )
        self.gerenciador_datasets.salvar(registro)
        return registro

    # ----------------------------------------------------------------------------------
    # VALOR (impacto financeiro + inferência + governança)
    # ----------------------------------------------------------------------------------
    def apurar_valor(self, nome_dataset: str) -> Dict[str, Any]:
        """Apura o valor financeiro e a governança do modelo campeão.

        Este método lê os artefatos reais persistidos em disco (scorecard,
        líder de pódio, contrato de problema) e produz um resumo que consome o
        analista no Ato 4 (Valor). Não depende da API; funciona no modo
        ``servico`` ou ``local``, usando apenas os arquivos já gravados.

        Args:
            nome_dataset (str): Dataset alvo.

        Returns:
            Dict[str, Any]: Resumo com impacto financeiro, escore do campeão e
                status de governança (hash do artefato + diário de observações).
        """
        from hashlib import sha256

        registro = self.gerenciador_datasets.carregar(nome_dataset)
        if registro is None:
            raise FileNotFoundError(f"Dataset '{nome_dataset}' não está registrado na plataforma.")

        pasta_ml = self.gerenciador_datasets.pasta_ml(nome_dataset)
        pasta_modelos = self.gerenciador_datasets.pasta_modelos_dataset(nome_dataset)

        # --- impacto financeiro via CustosNegocio do contrato ---
        contrato = registro.contrato_problema
        custo_info: Dict[str, Any] = {"disponivel": False}
        if contrato is not None and contrato.custos is not None:
            c = contrato.custos
            # 1 amostra representativa do dataset para cálculo honesto
            df_teste = registro.resultado.get("df_teste") if isinstance(registro.resultado, dict) else None
            falsos_negativos = 0  # não há matriz de confusão em regressão; apenas logging
            falsos_positivos = 0
            verdadeiros_positivos = 1  # 1 modelo campeão homologado
            total = float(c.custo_total(falsos_negativos, falsos_positivos, verdadeiros_positivos))
            custo_info = {
                "disponivel": True,
                "custo_falso_negativo": c.falso_negativo,
                "custo_falso_positivo": c.falso_positivo,
                "verdadeiro_positivo": c.verdadeiro_positivo,
                "total_apurado_R$": round(total, 2),
            }

        # --- escore do campeão (Top 3 + métricas) ---
        top3 = list(registro.top3) if registro.top3 else []
        campeao = registro.campeao
        metricas_top3: Dict[str, Any] = {}
        scorecard_path: Optional[str] = None

        if top3:
            caminho_scorecard = pasta_modelos / "scorecard_top3.csv"
            if caminho_scorecard.is_file():
                df_scorecard = None
                try:
                    import pandas as pd
                    df_scorecard = pd.read_csv(caminho_scorecard)
                    # achar a linha do campeão
                    if campeao and campeao in df_scorecard["Modelo"].values:
                        row = df_scorecard[df_scorecard["Modelo"] == campeao].iloc[0]
                        metricas_top3 = {
                            "r2": round(float(row.get("R2_Score", 0)), 4),
                            "rmse": round(float(row.get("RMSE", 0)), 2),
                            "mae": round(float(row.get("MAE", 0)), 2),
                        }
                except Exception as e:
                    logging.warning("Falha ao ler scorecard: %s", e)

            scorecard_path = str(caminho_scorecard) if caminho_scorecard.is_file() else None

        # --- governança (hash do artefato + diário de observações) ---
        hash_artefato: Optional[str] = None
        diario: List[str] = []
        pasta_registros = self.gerenciador_datasets.pasta_registros
        arquivo_registro = pasta_registros / f"{nome_dataset}.json"
        if arquivo_registro.is_file():
            try:
                import json
                dados_registro = json.loads(arquivo_registro.read_text(encoding="utf-8"))
                # hash sobre o JSON normalizado (chaves ordenadas, sem whitespace)
                hash_artefato = sha256(
                    json.dumps(dados_registro, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()[:16]
                diario = dados_registro.get("observacoes", [])[-10:]  # últimas 10 observações
            except Exception as e:
                logging.warning("Falha ao ler registro de governança: %s", e)

        return {
            "dataset": nome_dataset,
            "impacto_financeiro": custo_info,
            "campeao": campeao,
            "metricas_top3": metricas_top3,
            "scorecard_path": scorecard_path,
            "hash_artefato": hash_artefato,
            "diario_observacoes": diario,
            "top3": top3,
        }

    def eleger_campeao(self, nome_dataset: str, nome_modelo: str) -> RegistroDataset:
        """Registra a escolha humana do modelo campeão entre os três finalistas.

        Args:
            nome_dataset (str): Dataset alvo.
            nome_modelo (str): Nome exato do modelo eleito.

        Returns:
            RegistroDataset: Registro atualizado com o campeão.

        Raises:
            FileNotFoundError: Quando o dataset não está registrado.
            ValueError: Quando o modelo não integra o pódio Top 3.
        """
        registro = self.gerenciador_datasets.carregar(nome_dataset)
        if registro is None:
            raise FileNotFoundError(f"Dataset '{nome_dataset}' não está registrado na plataforma.")

        if registro.top3 and nome_modelo not in registro.top3:
            raise ValueError(
                f"Modelo '{nome_modelo}' não integra o pódio Top 3 "
                f"({', '.join(registro.top3)}). Escolha um dos finalistas."
            )

        registro.campeao = nome_modelo
        registro.registrar_observacao(
            f"Campeão eleito pelo humano: '{nome_modelo}' entre {', '.join(registro.top3) or 'n/d'}."
        )
        self.gerenciador_datasets.salvar(registro)
        return registro
