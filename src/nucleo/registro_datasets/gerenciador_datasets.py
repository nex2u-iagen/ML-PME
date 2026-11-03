"""Módulo do Gerenciador de Registro de Datasets (Núcleo de Acesso a Dados).



Responsabilidade Única: Manter o cadastro persistente de cada base de dados

analisada pela plataforma, resolvendo de forma determinística *qual dataset* está

em operação. Substitui a seleção frágil ``subpastas[0]`` por uma resolução

explícita e auditável, habilitando múltiplas PMEs em coexistência.



O registro guarda também o Contrato de Problema associado, o estado de cada fase

CRISP-DM, o pódio de modelos e o campeão escolhido pelo humano.

"""



# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.

import logging



# 'from datetime' fornece o carimbo temporal ISO para rastreabilidade da persistência.

from datetime import datetime, timezone



# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.

from pathlib import Path



# 'from typing' oferece anotações de tipagem estática para coleções e dicionários.

from typing import Any, Dict, List, Optional



# 'from pydantic' traz o motor de validação de dados com tipagem forte e serialização JSON.

from pydantic import BaseModel, Field



# Importa o contrato de problema para persistência da pergunta de negócio associada.

from src.nucleo.contratos.contrato_problema import ContratoProblema



# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s — [%(levelname)s] — %(message)s",

)





class RegistroDataset(BaseModel):

    """Estrutura persistente que descreve completamente um dataset em análise."""



    nome: str = Field(..., description="Identificador do dataset, geralmente o nome da PME.")

    criado_em: str = Field(

        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),

        description="Carimbo temporal ISO de criação do registro.",

    )

    atualizado_em: str = Field(

        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),

        description="Carimbo temporal ISO da última mutação do registro.",

    )

    arquivos_origem: List[str] = Field(

        default_factory=list,

        description="Nomes dos arquivos .sql/.csv que originaram o dataset.",

    )

    tabelas: List[str] = Field(

        default_factory=list,

        description="Entidades tabulares descobertas na extração.",

    )

    matching_semantico: Dict[str, Optional[str]] = Field(

        default_factory=dict,

        description="Mapa papel semântico -> tabela física efetivamente localizada.",

    )

    colunas_semanticas: Dict[str, Dict[str, Optional[str]]] = Field(

        default_factory=dict,

        description="Mapa tabela -> papel semântico -> coluna física localizada.",

    )

    contrato_problema: Optional[ContratoProblema] = Field(

        default=None,

        description="Contrato de problema de negócio declarado para este dataset.",

    )

    status_fases: Dict[str, str] = Field(

        default_factory=dict,

        description="Estado de cada fase CRISP-DM ('pendente', 'executando', 'concluida', 'erro').",

    )

    top3: List[str] = Field(

        default_factory=list,

        description="Nomes dos três modelos finalistas do torneio da Fase 4.",

    )

    metricas_top3: Dict[str, Dict[str, float]] = Field(

        default_factory=dict,

        description="Métricas de avaliação por finalist, usadas na tela de decisão humana.",

    )

    campeao: Optional[str] = Field(

        default=None,

        description="Modelo eleito pelo humano entre os três finalistas.",

    )

    observacoes: List[str] = Field(

        default_factory=list,

        description="Diário de auditoria com as decisões humanas registradas.",

    )



    @property

    def caminho_csv(self) -> str:

        """Retorna o nome da subpasta de CSV onde os arquivos brutos residem."""

        return self.nome



    def marcar_fase(self, numero_fase: str, estado: str) -> None:

        """Registra o estado de uma fase e atualiza o carimbo temporal de auditoria.



        Args:

            numero_fase (str): Identificador da fase ('01' a '06').

            estado (str): Novo estado ('pendente', 'executando', 'concluida', 'erro').

        """

        self.status_fases[numero_fase] = estado

        self.atualizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")



    def registrar_observacao(self, mensagem: str) -> None:

        """Acrescenta uma entrada datada ao diário de auditoria do dataset."""

        carimbo = datetime.now(timezone.utc).isoformat(timespec="seconds")

        self.observacoes.append(f"[{carimbo}] {mensagem}")

        self.atualizado_em = carimbo



    def resumo_para_frontend(self) -> Dict[str, Any]:

        """Produz o dicionário compacto consumido pela API e pelo frontend Streamlit."""

        return {

            "nome": self.nome,

            "criado_em": self.criado_em,

            "arquivos_origem": self.arquivos_origem,

            "total_tabelas": len(self.tabelas),

            "matching_semantico": self.matching_semantico,

            "contrato": (

                self.contrato_problema.resumo_executivo() if self.contrato_problema else None

            ),

            "status_fases": self.status_fases,

            "top3": self.top3,

            "campeao": self.campeao,

        }

    def gerar_relatorio_governanca(self) -> Path:
        """Gera um relatório de governança executiva para o dataset.

        Este método consolida todas as informações de governança relevantes
        sobre o dataset em um documento Markdown, incluindo:
        - Metadados do dataset (nome, fonte, matching semântico)
        - Contrato de problema vinculado
        - Status de todas as fases CRISP-DM
        - Pódio Top 3 com métricas resumo
        - Impacto financeiro estimado (baseado no contrato de custos)
        - Observações e rastreabilidade

        O relatório é gravado em relatorios/<nome_dataset>/governanca/governanca_dataset.md.

        Returns:
            Path: Caminho absolute do relatório gravado.
        """
        import datetime

        from src.nucleo.contratos.catalogo_problemas import CatalogoProblemas

        pasta_relatorios = self.pasta_relatorios / "governanca"
        pasta_relatorios.mkdir(parents=True, exist_ok=True)

        # --- Metadados do dataset ---
        metadado_nome = self.nome
        criado_em = (
            self.criado_em
            if self.criado_em
            else datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        arquivos_origem = self.arquivos_origem or []
        matching_semantico = self.matching_semantico or {}
        total_arquivos_csv = len(
            list((Path(self.diretorio_raiz) / "dados" / "brutos" / "csv" / metadado_nome).glob("*.csv"))
        ) if metadado_nome else 0

        # --- Contrato de problema ---
        contrato_info = self.contrato_problema
        if contrato_info:
            contrato = contrato_info
            contrato_dict = {
                "id": contrato.id,
                "nome": contrato.nome,
                "pergunta_negocio": contrato.pergunta_negocio,
                "tipo_tarefa": contrato.tipo_tarefa.value,
                "grao_analise": contrato.grao_analise,
                "metrica_otimizacao": contrato.metrica_effective,
                "entidade_base": contrato.receita.entidade_base if contrato.receita else None,
                "custos": {
                    "falso_negativo": contrato.custos.falso_negativo if contrato.custos else None,
                    "falso_positivo": contrato.custos.falso_positivo if contrato.custos else None,
                    "verdadeiro_positivo": contrato.custos.verdadeiro_positivo if contrato.custos else None,
                }
                if contrato.custos
                else None,
            }
        else:
            contrato_dict = None

        # --- Status das fases ---
        status_fases = self.status_fases or {}

        # --- Pódio Top 3 ---
        top3 = self.top3 or []
        metricas_top3 = {}
        if hasattr(self, "metricas_top3") and self.metricas_top3:
            metricas_top3 = self.metricas_top3

        campeao = self.campeao or None

        # --- Cálculo de impacto financeiro estimado ---
        impacto_financeiro = {}
        if contrato_info and contrato_info.custos:
            # Estimativa baseada nos custos do contrato e nas métricas do top3
            # VP * ganho_VP + FP * custo_FP + FN * custo_FN
            # Simplificação: usar as métricas do campeão se disponível
            if metricas_top3 and campeao and campeao in metricas_top3:
                mc = metricas_top3[campeao]
                # Taxas estimadas a partir do F1 e do recall/precisão
                # Esta é uma estimativa simplificada para o relatório
                impacto_financeiro = {
                    "custo_por_falso_negativo_estimado": (
                        None
                        if mc.get("recall") is None
                        else round(8000 * mc.get("recall", 0), 2)
                    ),
                    "custo_por_falso_positivo_estimado": (
                        None
                        if mc.get("precision") is None
                        else round(500 * mc.get("precision", 0), 2)
                    ),
                    "ganho_por_verdadeiro_positivo_estimado": (
                        None
                        if mc.get("recall") is None
                        else round(3500 * mc.get("recall", 0), 2)
                    ),
                }

        # --- Montagem do relatório em Markdown ---
        linhas = [
            "#  Relatório de Governança Executiva - Dataset",
            "",
            f"**Dataset:** ",
            f"**Data de Criação:** {criado_em[:10] if criado_em else 'N/A'}",
            "",
            "---",
            "",
            "## 1. Metadados Técnicos",
            "",
            "| Item | Valor |",
            "|---|---|",
            f"- **Nome do Dataset** | ",
            f"- **Data de Criação** | {criado_em[:10] if criado_em else 'N/A'}",
            f"- **Arquivos de Origem** | {', '.join(arquivos_origem) if arquivos_origem else 'N/A'}",
            f"- **Total de Tabelas Mapeadas** | {total_arquivos_csv}",
            f"- **Matching Semântico** | {len(matching_semantico)} entidades mapeadas",
            "",
            "",
            "## 2. Contrato de Problema Vinculado",
            "",
            "| Item | Valor |",
            "|---|---|",
        ]

        if contrato_dict:
            linhas += [
                f"- **ID do Contrato** | ",
                f"- **Nome do Contrato** | {contrato_dict['nome']}",
                f"- **Pergunta de Negócio** | {contrato_dict['pergunta_negocio']}",
                f"- **Tipo de Tarefa** | {contrato_dict['tipo_tarefa']}",
                f"- **Grão de Análise** | {contrato_dict['grao_analise']}",
                f"- **Métrica de Otimização** | {contrato_dict['metrica_otimizacao']}",
                f"- **Entidade Base** | {contrato_dict['entidade_base']}",
                "",
                "### Custos de Negócio (por erro)",
                f"- **Custo FN (Não detectar evento)** | R$ {contrato_dict['custos']['falso_negativo']:,.2f}",
                f"- **Custo FP (Alarmar benigno)** | R$ {contrato_dict['custos']['falso_positivo']:,.2f}",
                f"- **Ganho VP (Detetar corretamente)** | R$ {contrato_dict['custos']['verdadeiro_positivo']:,.2f}",
            ]
        else:
            linhas += ["Nenhum contrato de problema vinculado.", ""]

        linhas += [
            "",
            "---",
            "",
            "## 3. Status das Fases CRISP-DM",
            "",
            "| Fase | Status |",
            "|---|---|",
        ]

        fase_labels = {
            "01": "Ingestão",
            "02": "Raio-X / Exploração",
            "03": "Preparação / ABT",
            "04": "Modelagem / Torneio",
            "05": "Avaliação / Governança",
        }

        for fase in ["01", "02", "03", "04", "05"]:
            status = status_fases.get(fase, "pendente")
            label = fase_labels.get(fase, fase)
            linhas += [f"- **{label}** | "]

        linhas += [
            "",
            "---",
            "",
            "## 4. Pódio Top 3 - Modelos Finalistas",
            "",
            "| Modelo | Acurácia | F1-Score | ROC-AUC |",
            "|---|---|---|---|",
        ]

        # Ordenar top3 pelas métricas (usando F1 como referência quando disponível)
        top3_ordenado = list(top3)
        if metricas_top3:
            # Tentar ordenar pelo F1 do modelo na validação
            def get_f1(modelo_nome):
                if modelo_nome in metricas_top3 and "f1_score" in metricas_top3[modelo_nome]:
                    return metricas_top3[modelo_nome]["f1_score"]
                return 0

            top3_ordenado.sort(key=get_f1, reverse=True)

        for modelo in top3_ordenado:
            f1 = ""
            if metricas_top3 and modelo in metricas_top3 and "f1_score" in metricas_top3[modelo]:
                f1 = f"{metricas_top3[modelo]['f1_score']:.4f}"
            acc = ""
            if metricas_top3 and modelo in metricas_top3 and "acuracia" in metricas_top3[modelo]:
                acc = f"{metricas_top3[modelo]['acuracia']:.4f}"
            roc = ""
            if metricas_top3 and modelo in metricas_top3 and "roc_auc" in metricas_top3[modelo]:
                roc = f"{metricas_top3[modelo]['roc_auc']:.4f}"
            linhas += [f"| {modelo} | {acc} | {f1} | {roc} |"]

        linhas += [
            "",
            "",
            "---",
            "",
            "## 5. Campeão Atual",
            "",
        ]

        if campeao:
            linhas += [
                f"- **Modelo Campeão:** ",
                "",
                "### Impacto Financeiro Estimado",
            ]
            if impacto_financeiro:
                for k, v in impacto_financeiro.items():
                    label = k.replace("custo_por_falso_", "FN ").replace("custo_por_falso_positivo_", "FP ").replace("ganho_por_verdadeiro_positivo_", "VP ")
                    linhas += [f"- **{label}** | R$ {v:,.2f}" if v is not None else f"- **{label}** | --"]
            else:
                linhas += ["- Dados insuficientes para estimativa financeira."]
        else:
            linhas += ["- Nenhum modelo campeão eleito ainda."]

        linhas += [
            "",
            "---",
            "",
            "## 6. Rastreabilidade e Observações",
            "",
            "*Relatório gerado automaticamente pelo sistema de governança da plataforma ML.*",
            "",
        ]

        # Gravando o relatório
        caminho_dossie = pasta_relatorios / "governanca_dataset.md"
        with open(caminho_dossie, "w", encoding="utf-8") as arquivo:
            arquivo.write("".join(linhas))

        logging.info("Relatório de governança executiva gravado em: %s", caminho_dossie)
        return caminho_dossie





    



        # --- Montagem do relatório em Markdown ---

        linhas = [

            "# 📋 Relatório de Governança Executiva - Dataset",

            "",

            f"**Dataset:** `{metadado_nome}`",

            f"**Data de Criação:** {criado_em[:10] if criado_em else 'N/A'}",

            "",

            "---",

            "",

            "## 1. Metadados Técnicos",

            "",

            "| Item | Valor |",

            "|---|---|",

            f"- **Nome do Dataset** | `{metadado_nome}`",

            f"- **Data de Criação** | {criado_em[:10] if criado_em else 'N/A'}",

            f"- **Arquivos de Origem** | {', '.join(arquivos_origem) if arquivos_origem else 'N/A'}",

            f"- **Total de Tabelas Mapeadas** | {total_arquivos_csv}",

            f"- **Matching Semântico** | {len(matching_semantico)} entidades mapeadas",

            "",

            "",

            "## 2. Contrato de Problema Vinculado",

            "",

            "| Item | Valor |",

            "|---|---|",

        ]



        if contrato_dict:

            linhas += [

                f"- **ID do Contrato** | `{contrato_dict['id']}`",

                f"- **Nome do Contrato** | {contrato_dict['nome']}",

                f"- **Pergunta de Negócio** | {contrato_dict['pergunta_negocio']}",

                f"- **Tipo de Tarefa** | {contrato_dict['tipo_tarefa']}",

                f"- **Grão de Análise** | {contrato_dict['grao_analise']}",

                f"- **Métrica de Otimização** | {contrato_dict['metrica_otimizacao']}",

                f"- **Entidade Base** | {contrato_dict['entidade_base']}",

                "",

                "### Custos de Negócio (por erro)",

                f"- **Custo FN (Não detectar evento)** | R$ {contrato_dict['custos']['falso_negativo']:,.2f}",

                f"- **Custo FP (Alarmar benigno)** | R$ {contrato_dict['custos']['falso_positivo']:,.2f}",

                f"- **Ganho VP (Detetar corretamente)** | R$ {contrato_dict['custos']['verdadeiro_positivo']:,.2f}",

            ]

        else:

            linhas += ["Nenhum contrato de problema vinculado.", ""]



        linhas += [

            "",

            "---",

            "",

            "## 3. Status das Fases CRISP-DM",

            "",

            "| Fase | Status |",

            "|---|---|",

        ]



        fase_labels = {

            "01": "Ingestão",

            "02": "Raio-X / Exploração",

            "03": "Preparação / ABT",

            "04": "Modelagem / Torneio",

            "05": "Avaliação / Governança",

        }



        for fase in ["01", "02", "03", "04", "05"]:

            status = status_fases.get(fase, "pendente")

            label = fase_labels.get(fase, fase)

            linhas += [f"- **{label}** | `{status}`"]



        linhas += [

            "",

            "---",

            "",

            "## 4. Pódio Top 3 - Modelos Finalistas",

            "",

            "| Modelo | Acurácia | F1-Score | ROC-AUC |",

            "|---|---|---|---|",

        ]



        # Ordenar top3 pelas métricas (usando F1 como referência quando disponível)

        top3_ordenado = list(top3)

        if metricas_top3:

            # Tentar ordenar pelo F1 do modelo na validação

            def get_f1(modelo_nome):

                if modelo_nome in metricas_top3 and "f1_score" in metricas_top3[modelo_nome]:

                    return metricas_top3[modelo_nome]["f1_score"]

                return 0



            top3_ordenado.sort(key=get_f1, reverse=True)



        for modelo in top3_ordenado:

            f1 = ""

            if metricas_top3 and modelo in metricas_top3 and "f1_score" in metricas_top3[modelo]:

                f1 = f"{metricas_top3[modelo]['f1_score']:.4f}"

            acc = ""

            if metricas_top3 and modelo in metricas_top3 and "acuracia" in metricas_top3[modelo]:

                acc = f"{metricas_top3[modelo]['acuracia']:.4f}"

            roc = ""

            if metricas_top3 and modelo in metricas_top3 and "roc_auc" in metricas_top3[modelo]:

                roc = f"{metricas_top3[modelo]['roc_auc']:.4f}"

            linhas += [f"| {modelo} | {acc} | {f1} | {roc} |"]



        linhas += [

            "",

            "",

            "---",

            "",

            "## 5. Campeão Atual",

            "",

        ]



        if campeao:

            linhas += [

                f"- **Modelo Campeão:** `{campeao}`",

                "",

                "### Impacto Financeiro Estimado",

            ]

            if impacto_financeiro:

                for k, v in impacto_financeiro.items():

                    label = k.replace("custo_por_falso_", "FN ").replace("custo_por_falso_positivo_", "FP ").replace("ganho_por_verdadeiro_positivo_", "VP ")

                    linhas += [f"- **{label}** | R$ {v:,.2f}" if v is not None else f"- **{label}** | --"]

            else:

                linhas += ["- Dados insuficientes para estimativa financeira."]

        else:

            linhas += ["- Nenhum modelo campeão eleito ainda."]



        linhas += [

            "",

            "---",

            "",

            "## 6. Rastreabilidade e Observações",

            "",

            "*Relatório gerado automaticamente pelo sistema de governança da plataforma ML.*",

            "",

        ]



        # Gravando o relatório

        caminho_dossie = pasta_relatorios / "governanca_dataset.md"

        with open(caminho_dossie, "w", encoding="utf-8") as arquivo:

            arquivo.write("\n".join(linhas))



        logging.info("Relatório de governança executiva gravado em: %s", caminho_dossie)

        return caminho_dossie





class GerenciadorDatasets:

    """Fachada responsável por descobrir, carregar, salvar e resolver datasets."""



    def __init__(self, diretorio_raiz: Path) -> None:

        """Inicializa o gerenciador ancorando as pastas oficiais de dados e registros.



        Args:

            diretorio_raiz (Path): Caminho absoluto da raiz do projeto.

        """

        self.diretorio_raiz = Path(diretorio_raiz)

        self.pasta_csv_base = self.diretorio_raiz / "dados" / "brutos" / "csv"

        self.pasta_sql_base = self.diretorio_raiz / "dados" / "brutos" / "sql"

        self.pasta_registros = self.diretorio_raiz / "dados" / "registros"

        self.pasta_registros.mkdir(parents=True, exist_ok=True)



    # ----------------------------------------------------------------------------------

    # DESCOBERTA E RESOLUÇÃO

    # ----------------------------------------------------------------------------------

    def descobrir_datasets(self) -> List[str]:

        """Lista os nomes de todos os datasets presentes na árvore de dados brutos.



        Returns:

            List[str]: Nomes normalizados (minúsculos, sem prefixo 'erp_') das subpastas.

        """

        if not self.pasta_csv_base.is_dir():

            return []



        nomes: List[str] = []

        for pasta in sorted(self.pasta_csv_base.iterdir()):

            if pasta.is_dir() and not pasta.name.startswith(".") and pasta.name != "mocks":

                nomes.append(pasta.name)



        # Datasets ainda não extraídos (apenas o dump SQL presente) também entram no catálogo.

        if self.pasta_sql_base.is_dir():

            for arquivo in sorted(self.pasta_sql_base.glob("*.sql")):

                nome_candidato = self._normalizar_nome_dataset(arquivo.stem)

                if nome_candidato and nome_candidato not in nomes:

                    nomes.append(nome_candidato)



        return nomes



    def _normalizar_nome_dataset(self, nome_bruto: str) -> str:

        """Normaliza o nome de um dump SQL removendo carimbos de data e sufixos técnicos."""

        import re



        nome_base = nome_bruto.strip().lower()

        nome_limpo = re.sub(r"_\d{8}(?:_\d+)?$", "", nome_base)

        return nome_limpo if nome_limpo else nome_base



    def resolver_pasta_csv(self, nome_dataset: Optional[str] = None) -> Path:

        """Resolve de forma determinística a pasta de CSV do dataset solicitado.



        Este método substitui a seleção frágil ``subpastas[0]`` presente no código original.



        Args:

            nome_dataset (Optional[str]): Nome do dataset desejado. Se ``None``, usa o

                dataset mais recente modificado ou, em último caso, o único disponível.



        Returns:

            Path: Caminho absoluto da pasta de CSV do dataset.



        Raises:

            FileNotFoundError: Quando o dataset solicitado não existe ou nenhum está disponível.

        """

        if nome_dataset:

            pasta = self.pasta_csv_base / nome_dataset

            if pasta.is_dir():

                return pasta

            raise FileNotFoundError(

                f"Dataset '{nome_dataset}' não encontrado em {self.pasta_csv_base}. "

                f"Disponíveis: {self.descobrir_datasets()}"

            )



        candidatos = [

            pasta

            for pasta in self.pasta_csv_base.iterdir()

            if pasta.is_dir() and not pasta.name.startswith(".") and pasta.name != "mocks"

        ] if self.pasta_csv_base.is_dir() else []



        if not candidatos:

            raise FileNotFoundError(

                f"Nenhum dataset disponível em {self.pasta_csv_base}. Faça o upload pela interface."

            )



        if len(candidatos) == 1:

            return candidatos[0]



        # Com múltiplos datasets, assume o mais recentemente modificado como padrão.

        candidatos.sort(key=lambda pasta: pasta.stat().st_mtime, reverse=True)

        logging.warning(

            "Múltiplos datasets detectados (%s). Selecionado '%s' por recência. "

            "Informe o nome explicitamente para eliminar a ambiguidade.",

            [pasta.name for pasta in candidatos],

            candidatos[0].name,

        )

        return candidatos[0]



    # ----------------------------------------------------------------------------------

    # PERSISTÊNCIA

    # ----------------------------------------------------------------------------------

    def _caminho_registro(self, nome_dataset: str) -> Path:

        """Monta o caminho absoluto do arquivo JSON que guarda o registro do dataset."""

        return self.pasta_registros / f"{nome_dataset}.json"



    def salvar(self, registro: RegistroDataset) -> Path:

        """Persiste o registro do dataset em disco, sobrepondo a versão anterior.



        Args:

            registro (RegistroDataset): Estrutura a ser gravada.



        Returns:

            Path: Caminho absoluto do arquivo JSON gravado.

        """

        registro.atualizado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")

        caminho = self._caminho_registro(registro.nome)

        caminho.parent.mkdir(parents=True, exist_ok=True)

        caminho.write_text(registro.model_dump_json(indent=2), encoding="utf-8")

        logging.info("Registro do dataset '%s' persistido em: %s", registro.nome, caminho)

        return caminho



    def carregar(self, nome_dataset: str) -> Optional[RegistroDataset]:

        """Carrega o registro persistido de um dataset específico.



        Args:

            nome_dataset (str): Nome do dataset a carregar.



        Returns:

            Optional[RegistroDataset]: O registro carregado ou ``None`` se ainda não existir.

        """

        caminho = self._caminho_registro(nome_dataset)

        if not caminho.is_file():

            return None

        return RegistroDataset.model_validate_json(caminho.read_text(encoding="utf-8"))



    def obter_ou_criar(self, nome_dataset: str) -> RegistroDataset:

        """Carrega o registro existente ou inicializa um novo para o dataset informado.



        Args:

            nome_dataset (str): Nome do dataset.



        Returns:

            RegistroDataset: Registro carregado ou recém-criado.

        """

        existente = self.carregar(nome_dataset)

        if existente is not None:

            return existente

        return RegistroDataset(nome=nome_dataset)



    def listar_registros(self) -> List[RegistroDataset]:

        """Carrega todos os registros persistidos no diretório de registros.



        Returns:

            List[RegistroDataset]: Lista de registros ordenados por nome.

        """

        registros: List[RegistroDataset] = []

        for arquivo in sorted(self.pasta_registros.glob("*.json")):

            try:

                registros.append(

                    RegistroDataset.model_validate_json(arquivo.read_text(encoding="utf-8"))

                )

            except Exception as erro_leitura:

                logging.error("Registro inválido em '%s': %s", arquivo.name, erro_leitura)

        return registros



    def listar_nomes(self) -> List[str]:

        """Lista os nomes dos datasets registrados, incluindo os ainda não extraídos."""

        nomes_registrados = {registro.nome for registro in self.listar_registros()}

        nomes_descobertos = set(self.descobrir_datasets())

        return sorted(nomes_registrados | nomes_descobertos)



    # ----------------------------------------------------------------------------------

    # INGESTÃO DE ARQUIVOS ENVIADOS PELO FRONTEND

    # ----------------------------------------------------------------------------------

    def registrar_upload(

        self,

        nome_dataset: str,

        arquivos: List[tuple[str, bytes]],

    ) -> RegistroDataset:

        """Recebe arquivos enviados pelo frontend e os deposita na árvore de dados brutos.



        Args:

            nome_dataset (str): Nome da PME ou do dataset informado pelo humano.

            arquivos (List[tuple[str, bytes]]): Pares (nome do arquivo, conteúdo binário).



        Returns:

            RegistroDataset: Registro atualizado com os arquivos recebidos.

        """

        nome_normalizado = self._normalizar_nome_dataset(nome_dataset)

        pasta_destino = self.pasta_sql_base

        pasta_destino.mkdir(parents=True, exist_ok=True)



        nomes_gravados: List[str] = []

        for nome_arquivo, conteudo in arquivos:

            nome_seguro = Path(nome_arquivo).name

            caminho = pasta_destino / nome_seguro

            caminho.write_bytes(conteudo)

            nomes_gravados.append(nome_seguro)



        registro = self.obter_ou_criar(nome_normalizado)

        registro.arquivos_origem = list(dict.fromkeys(registro.arquivos_origem + nomes_gravados))

        registro.registrar_observacao(

            f"Upload recebido com {len(nomes_gravados)} arquivo(s): {', '.join(nomes_gravados)}"

        )

        self.salvar(registro)

        logging.info("Upload do dataset '%s' depositado em: %s", nome_normalizado, pasta_destino)

        return registro



    # ----------------------------------------------------------------------------------

    # PROPRIEDADES DERIVADAS

    # ----------------------------------------------------------------------------------

    @property

    def pasta_dados_processados(self) -> Path:

        """Retorna a pasta raiz onde os artefatos processados de cada dataset são gravados."""

        return self.diretorio_raiz / "dados" / "processados"



    @property

    def pasta_modelos(self) -> Path:

        """Retorna a pasta raiz onde os modelos serializados de cada dataset são gravados."""

        return self.diretorio_raiz / "modelos"



    def pasta_ml(self, nome_dataset: str) -> Path:

        """Retorna a pasta de artefatos de ML (Parquet) de um dataset específico."""

        return self.pasta_dados_processados / nome_dataset / "ml"



    def pasta_modelos_dataset(self, nome_dataset: str) -> Path:

        """Retorna a pasta de modelos serializados de um dataset específico."""

        return self.pasta_modelos / nome_dataset



    def pasta_relatorios(self, nome_dataset: str) -> Path:

        """Retorna a pasta de relatórios e figuras de um dataset específico."""

        return self.diretorio_raiz / "relatorios" / nome_dataset
