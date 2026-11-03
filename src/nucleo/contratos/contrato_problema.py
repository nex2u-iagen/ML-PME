"""Módulo do Contrato de Problema de Negócio (Núcleo de Contratos).

Responsabilidade Única: Definir a estrutura declarativa e validada que descreve
*qual pergunta de negócio* a plataforma deve responder sobre *um dataset específico*.
O contrato é o único ponto de verdade que substitui o alvo hardcoded
``alvo_inadimplente`` e viabiliza a plataforma agnóstica a dataset e a problema.

O contrato é serializável em JSON, permitindo persistência ao lado dos artefatos
de modelagem e transporte entre o frontend, a API de orquestração e a esteira CRISP-DM.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional.
import logging

# 'from datetime' fornece o carimbo temporal ISO para rastreabilidade da persistência.
from datetime import datetime, timezone

# 'from pathlib' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'from enum' importa o construtor de enums certificados, base dos domínios fechados.
from enum import Enum

# 'from typing' oferece anotações de tipagem estática para coleções e uniões.
from typing import Any, Dict, List, Optional

# 'from pydantic' traz o motor de validação de dados com tipagem forte e serialização JSON.
from pydantic import BaseModel, Field, field_validator

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


class TipoTarefa(str, Enum):
    """Domínio fechado das tarefas de aprendizado de máquina suportadas pela plataforma."""

    CLASSIFICACAO = "classificacao"
    REGRESSAO = "regressao"
    AGRUPAMENTO = "agrupamento"
    DETECCAO_ANOMALIAS = "deteccao_anomalias"

    @property
    def supervisionado(self) -> bool:
        """Indica se a tarefa exige um vetor-alvo supervisionado para o treinamento."""
        return self in {TipoTarefa.CLASSIFICACAO, TipoTarefa.REGRESSAO}

    @property
    def metrica_padrao(self) -> str:
        """Retorna a métrica de otimização natural para o tipo de tarefa."""
        if self is TipoTarefa.CLASSIFICACAO:
            return "f1"
        if self is TipoTarefa.REGRESSAO:
            return "r2"
        if self is TipoTarefa.AGRUPAMENTO:
            return "silhueta"
        return "auc_anomalia"

    @property
    def rotulo_amostra(self) -> str:
        """Descreve em linguagem natural a unidade de análise da tarefa."""
        if self is TipoTarefa.AGRUPAMENTO:
            return "grupo"
        if self is TipoTarefa.DETECCAO_ANOMALIAS:
            return "observação"
        return "observação supervisionada"


class FuncaoAgregacao(str, Enum):
    """Funções de agregação SQL suportadas na construção da Tabela Analítica de Modelagem."""

    SUM = "SUM"
    AVG = "AVG"
    COUNT = "COUNT"
    COUNT_DISTINCT = "COUNT(DISTINCT {coluna})"
    MAX = "MAX"
    MIN = "MIN"
    MEDIAN = "MEDIAN"
    STDDEV = "STDDEV"


class AgregacaoABT(BaseModel):
    """Define uma única métrica agregada que compõe a Tabela Analítica de Modelagem."""

    nome: str = Field(..., description="Nome canônico da feature gerada na ABT.")
    funcao: FuncaoAgregacao = Field(..., description="Função de agregação aplicada.")
    coluna: Optional[str] = Field(
        default=None,
        description="Papel semântico da coluna base (ex.: 'valor'). Ignorado se expressao_sql existir.",
    )
    expressao_sql: Optional[str] = Field(
        default=None,
        description="Expressão SQL literal que substitui a resolução semântica da coluna.",
    )
    tipo_resultado: str = Field(
        default="DOUBLE",
        description="Tipo DuckDB do resultado ('DOUBLE', 'BIGINT', 'DATE'...).",
    )

    def montar_expressao_sql(self, coluna_resolvida: Optional[str]) -> str:
        """Compõe a expressão SQL final da agregação usando a coluna já resolvida.

        Args:
            coluna_resolvida (Optional[str]): Nome físico da coluna localizada no CSV.

        Returns:
            str: Fragmento SQL pronto para inserção na cláusula SELECT.
        """
        if self.expressao_sql:
            return f"TRY_CAST({self.expressao_sql} AS {self.tipo_resultado})"

        if self.funcao is FuncaoAgregacao.COUNT:
            if coluna_resolvida:
                return f"COUNT(\"{coluna_resolvida}\")"
            return "COUNT(*)"

        if self.funcao is FuncaoAgregacao.COUNT_DISTINCT:
            if coluna_resolvida:
                return f"COUNT(DISTINCT \"{coluna_resolvida}\")"
            return "COUNT(DISTINCT id_grupo)"

        if not coluna_resolvida:
            return f"CAST(NULL AS {self.tipo_resultado})"

        return f"TRY_CAST({self.funcao.value}(\"{coluna_resolvida}\") AS {self.tipo_resultado})"


class JuncaoReceita(BaseModel):
    """Descreve uma junção entre a tabela base e uma entidade canônica complementar.

    ERPs reais distribuem o grão de análise por múltiplas tabelas (cabeçalho de venda,
    destinatário, histórico de datas, itens). A junção declarativa permite que o
    contrato atravesse essas relações sem depender de codificação específica do ERP.
    """

    entidade: str = Field(
        ...,
        description="Papel semântico da tabela a ser unida (ex.: 'vendas_recebedor').",
    )
    chave_base: str = Field(
        ...,
        description="Papel semântico da chave na tabela base que participa da junção.",
    )
    chave_join: str = Field(
        ...,
        description="Papel semântico da chave na tabela unida que participa da junção.",
    )
    tipo: str = Field(default="left", description="Tipo de junção ('left' ou 'inner').")
    colunas: List[str] = Field(
        default_factory=list,
        description="Papéis semânticos trazidos da tabela unida para o CTE base.",
    )

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        """Garante que apenas os dois tipos de junção suportados sejam aceitos."""
        if valor not in {"left", "inner"}:
            raise ValueError("JuncaoReceita.tipo deve ser 'left' ou 'inner'.")
        return valor


class ReceitaABT(BaseModel):
    """Descreve como montar a Tabela Analítica de Modelagem a partir das tabelas do ERP."""

    entidade_base: str = Field(
        ...,
        description="Papel semântico da tabela base (ex.: 'contas_receber', 'vendas', 'estoque').",
    )
    chave_grupo: str = Field(
        ...,
        description="Papel semântico da chave que define o grão de análise (ex.: 'id_cliente').",
    )
    agregacoes: List[AgregacaoABT] = Field(
        default_factory=list,
        description="Métricas agregadas quesacam a feature na grão declarado.",
    )
    colunas_diretas: List[str] = Field(
        default_factory=list,
        description="Papéis semânticos copiados sem agregação (ex.: 'uf_cliente').",
    )
    juncoes: List[JuncaoReceita] = Field(
        default_factory=list,
        description="Junções declarativas que atravessam as tabelas do ERP.",
    )
    granularidade_temporal: Optional[str] = Field(
        default=None,
        description="Quando definido ('dia', 'semana', 'mes', 'ano'), o grão passa a ser o bucket temporal.",
    )
    coluna_data: str = Field(
        default="data_emissao",
        description="Papel semântico da data utilizada para montar o bucket temporal.",
    )
    dimensoes: List[str] = Field(
        default_factory=list,
        description=(
            "Papéis semânticos que compõem o grão junto com o bucket temporal "
            "(ex.: ['codigo_sku'] para uma série mensal por produto)."
        ),
    )
    deslocamento_alvo_periodos: int = Field(
        default=0,
        ge=0,
        description=(
            "Número de períodos à frente usado como vetor-alvo. Zero usa o mesmo período; "
            "1 (padrão das previsões) usa o período seguinte, evitando vazamento de informação."
        ),
    )
    filtro_sql: Optional[str] = Field(
        default=None,
        description="Cláusula WHERE adicional aplicada à tabela base.",
    )
    limite_linhas: Optional[int] = Field(
        default=None,
        description="Teto de linhas da tabela base para contenção de memória RAM.",
    )

    @field_validator("granularidade_temporal")
    @classmethod
    def validar_granularidade(cls, valor: Optional[str]) -> Optional[str]:
        """Garante que a granularidade temporal use apenas os buckets suportados."""
        if valor is not None and valor not in {"dia", "semana", "mes", "ano"}:
            raise ValueError(
                "ReceitaABT.granularidade_temporal deve ser 'dia', 'semana', 'mes' ou 'ano'."
            )
        return valor


class DefinicaoAlvo(BaseModel):
    """Especifica como o vetor-alvo supervisionado é derivado das tabelas do ERP."""

    tipo: str = Field(
        default="regra_sql",
        description="'regra_sql' (CASE WHEN sobre a tabela base) ou 'coluna' (coluna já existente).",
    )
    expressao_sql: Optional[str] = Field(
        default=None,
        description="Regra SQL que produz o alvo; referencie as expressões já resolvidas.",
    )
    coluna: Optional[str] = Field(
        default=None,
        description="Nome físico de uma coluna pré-existente que já é o alvo.",
    )
    tipo_dado: str = Field(default="BIGINT", description="Tipo do alvo ('BIGINT' ou 'DOUBLE').")

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        """Garante que apenas os dois mecanismos de definição suportados sejam aceitos."""
        if valor not in {"regra_sql", "coluna"}:
            raise ValueError("DefinicaoAlvo.tipo deve ser 'regra_sql' ou 'coluna'.")
        return valor


class CustosNegocio(BaseModel):
    """Representa o impacto financeiro dos erros para permitir a avaliação em moeda real."""

    falso_negativo: float = Field(default=12000.0, description="Custo de não detectar o evento adverso.")
    falso_positivo: float = Field(default=600.0, description="Custo de alarmar sobre um evento benigno.")
    verdadeiro_positivo: float = Field(default=4000.0, description="Ganho ao detectar corretamente.")

    def custo_total(self, falsos_negativos: float, falsos_positivos: float, verdadeiros_positivos: float) -> float:
        """Calcula o custo líquido em moeda real a partir da matriz de confusão."""
        perda = falsos_negativos * self.falso_negativo
        ruido = falsos_positivos * self.falso_positivo
        ganho = verdadeiros_positivos * self.verdadeiro_positivo
        return float(perda + ruido - ganho)


class ContratoProblema(BaseModel):
    """Contrato declarativo completo que descreve um problema de negócio sobre um dataset.

    Este é o único documento que a esteira CRISP-DM consome para decidir *o que construir*:
    ele substitui o alvo e a receita hardcoded por uma especificação validada e auditável.
    """

    id: str = Field(..., description="Identificador estável e único do problema.")
    nome: str = Field(..., description="Nome curto exibido ao humano no frontend.")
    pergunta_negocio: str = Field(
        ...,
        description="Pergunta em linguagem natural que o modelo deve responder.",
    )
    tipo_tarefa: TipoTarefa = Field(..., description="Família de aprendizado de máquina aplicável.")
    grao_analise: str = Field(
        default="cliente",
        description="Entidade que representa uma linha da ABT (cliente, produto, título, mês).",
    )
    metrica_otimizacao: Optional[str] = Field(
        default=None,
        description="Métrica que ordena o leaderboard; se omitida, usa a padrão do tipo de tarefa.",
    )
    receita: ReceitaABT = Field(..., description="Receita declarativa de construção da ABT.")
    alvo: Optional[DefinicaoAlvo] = Field(
        default=None,
        description="Definição do vetor-alvo; obrigatória apenas para tarefas supervisionadas.",
    )
    custos: Optional[CustosNegocio] = Field(
        default=None,
        description="Premissas financeiras para a avaliação de impacto em moeda real.",
    )
    parametros: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros livres de execução (semente, número de dobras, número de grupos...).",
    )
    criado_em: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
        description="Carimbo temporal ISO de criação do contrato.",
    )

    @field_validator("id")
    @classmethod
    def validar_id(cls, valor: str) -> str:
        """Normaliza o identificador para o padrão snake_case usado nos arquivos."""
        return valor.strip().lower().replace(" ", "_").replace("-", "_")

    @field_validator("alvo")
    @classmethod
    def validar_alvo(cls, valor: Optional[DefinicaoAlvo], info: Any) -> Optional[DefinicaoAlvo]:
        """Exige definição de alvo para tarefas supervisionadas e a proíbe para não supervisionadas."""
        tipo_tarefa: TipoTarefa = info.data.get("tipo_tarefa", TipoTarefa.CLASSIFICACAO)
        if tipo_tarefa.supervisionado and valor is None:
            raise ValueError(
                f"Tarefas supervisionadas ({tipo_tarefa.value}) exigem 'alvo' definido no contrato."
            )
        if not tipo_tarefa.supervisionado and valor is not None:
            raise ValueError(
                f"Tarefas não supervisionadas ({tipo_tarefa.value}) não devem declarar 'alvo'."
            )
        return valor

    @property
    def metrica_effective(self) -> str:
        """Retorna a métrica de otimização efetiva do contrato."""
        return self.metrica_otimizacao or self.tipo_tarefa.metrica_padrao

    @property
    def exige_alvo(self) -> bool:
        """Indica se o contrato demanda a produção de um vetor-alvo supervisionado."""
        return self.tipo_tarefa.supervisionado

    def obter_parametro(self, nome: str, padrao: Any = None) -> Any:
        """Acessa um parâmetro livre do contrato com valor padrão seguro.

        Args:
            nome (str): Chave do parâmetro sought.
            padrao (Any): Valor devolvido quando a chave não existe no contrato.

        Returns:
            Any: Valor do parâmetro ou o padrão fornecido.
        """
        return self.parametros.get(nome, padrao)

    def salvar_em_json(self, caminho_destino: Path) -> Path:
        """Persiste o contrato como JSON legível ao lado dos artefatos de modelagem.

        Args:
            caminho_destino (Path): Caminho absoluto do arquivo .json a ser gravado.

        Returns:
            Path: O mesmo caminho recebido, para encadeamento fluente.
        """
        caminho_destino = Path(caminho_destino)
        caminho_destino.parent.mkdir(parents=True, exist_ok=True)
        caminho_destino.write_text(
            self.model_dump_json(indent=2, exclude_none=False),
            encoding="utf-8",
        )
        logging.info("Contrato de problema '%s' persistido em: %s", self.id, caminho_destino)
        return caminho_destino

    @classmethod
    def carregar_de_json(cls, caminho_origem: Path) -> "ContratoProblema":
        """Reconstrói um contrato a partir do arquivo JSON previamente persistido.

        Args:
            caminho_origem (Path): Caminho absoluto do arquivo .json de origem.

        Returns:
            ContratoProblema: Instância validada do contrato.
        """
        dados = Path(caminho_origem).read_text(encoding="utf-8")
        return cls.model_validate_json(dados)

    def resumo_executivo(self) -> Dict[str, Any]:
        """Produz um dicionário compacto para exibição em relatórios e na API."""
        return {
            "id": self.id,
            "nome": self.nome,
            "pergunta_negocio": self.pergunta_negocio,
            "tipo_tarefa": self.tipo_tarefa.value,
            "grao_analise": self.grao_analise,
            "metrica_otimizacao": self.metrica_effective,
            "entidade_base": self.receita.entidade_base,
            "features": [agregacao.nome for agregacao in self.receita.agregacoes],
            "supervisionado": self.exige_alvo,
        }
