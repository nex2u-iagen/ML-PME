"""Visão agnóstica de Saúde 360° da Fase 02 (CRISP-DM).

Responsabilidade Única: transformar o ``prontuario_executivo.json`` do Raio-X
em uma PLACA ÚNICA de saúde da empresa — RADAR polar com os eixos de saúde
(margem, carga tributária, inadimplência, folha/receita, cobertura de estoque e
integridade estrutural), cartões de KPI executivos e semáforo de sinais.

Esta é a visão agnóstica (não departamental) do Raio-X: enxerga a companhia
como um todo, independentemente do setor analisado.

Uso por linha de comandos::

    python -m src.etapas.fase_02_exploracao.visao_360_saude --dataset mercadinho-v4
"""

# 'import json' lê o prontuário executivo persistido pela Fase 02.
import json

# 'import logging' registra mensagens de auditoria no console corporativo.
import logging

# 'from pathlib import Path' manipula caminhos de arquivo de forma orientada a objetos.
from pathlib import Path

# 'from typing import Any, Dict' importa tipagem estática para os laudos.
from typing import Any, Dict

# 'import matplotlib.pyplot' fornece o motor de renderização das placas gráficas.
import matplotlib.pyplot as plt

# 'from matplotlib.patches import FancyBboxPatch' desenha os cartões de KPI com cantos arredondados.
from matplotlib.patches import FancyBboxPatch

# 'import numpy' sustenta a malha do radar polar (ângulos e fechamento do polígono).
import numpy as np

# 'import pandas as pd' é usado para detecção resiliente de ausentes (pd.isna).
import pandas as pd

# Raiz do projeto (src/etapas/fase_02_exploracao/visao_360_saude.py → 3 níveis acima).
RAIZ_PROJETO = Path(__file__).resolve().parents[3]

# Paleta de semáforo corporativa.
VERDE = "#16a34a"
AMBAR = "#d97706"
VERMELHO = "#dc2626"
CINZA = "#64748b"
TEXTO = "#0f172a"
SECUNDARIO = "#475569"
BORDA = "#e2e8f0"
CARTAO = "#f8fafc"
RADAR = "#2563eb"


# 'def _brl(...)' formata um número como moeda brasileira (R$ 1.234,56).
def _brl(valor: float) -> str:
    """Formata um float em reais no padrão brasileiro.

    Args:
        valor (float): Montante em reais.

    Returns:
        str: Texto formatado (ex.: ``R$ 1.234,56``).
    """
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


# 'def _pct(...)' formata um número percentual no padrão brasileiro.
def _pct(valor: float, casas: int = 1) -> str:
    """Formata um float como percentual (ex.: ``12,3%``).

    Args:
        valor (float): Valor percentual.
        casas (int): Casas decimais.

    Returns:
        str: Texto formatado.
    """
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


# 'def _num(...)' formata um número inteiro com separador de milhar brasileiro.
def _num(valor: float) -> str:
    """Formata um número inteiro com ponto de milhar (ex.: ``1.234``).

    Args:
        valor (float): Valor numérico.

    Returns:
        str: Texto formatado.
    """
    return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


# 'def localizar_prontuario(...)' encontra o JSON do prontuário executivo.
def localizar_prontuario(dataset: str | None = None) -> Path | None:
    """Localiza o ``prontuario_executivo.json`` mais recente em ``relatorios/``.

    Args:
        dataset (str | None): Restringe a busca a um dataset específico.

    Returns:
        Path | None: Caminho encontrado ou ``None`` quando a Fase 02 nunca rodou.
    """
    raiz_relatorios = RAIZ_PROJETO / "relatorios"
    if not raiz_relatorios.is_dir():
        return None

    candidatos: list[Path] = []
    # Varre os dois formatos de saída: relatorios/<ds>/<ds>/fase_02 e relatorios/<ds>/fase_02.
    for caminho in raiz_relatorios.glob("*/**/fase_02/prontuario_executivo.json"):
        if dataset is None or dataset in caminho.parts:
            candidatos.append(caminho)

    if not candidatos:
        return None

    return max(candidatos, key=lambda caminho: caminho.stat().st_mtime)


# 'def _status_semaforo(...)' classifica um indicador em verde, âmbar ou vermelho.
def _status_semaforo(
    valor: float | None,
    limite_verde: float,
    limite_ambar: float,
    invertido: bool = False,
) -> str:
    """Aplica a régua de semáforo a um indicador.

    Args:
        valor (float | None): Valor apurado (``None`` → neutro).
        limite_verde (float): Limite da zona verde.
        limite_ambar (float): Limite da zona de atenção.
        invertido (bool): ``True`` quando valores ALTOS são bons (ex.: margem).

    Returns:
        str: ``"verde"``, ``"ambar"``, ``"vermelho"`` ou ``"neutro"``.
    """
    if valor is None or pd.isna(valor):
        return "neutro"
    if invertido:
        if valor >= limite_verde:
            return "verde"
        return "ambar" if valor >= limite_ambar else "vermelho"
    if valor <= limite_verde:
        return "verde"
    return "ambar" if valor <= limite_ambar else "vermelho"


# 'def _extrair_kpis(...)' navega o prontuário e devolve os KPIs exibidos.
def _extrair_kpis(prontuario: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai os KPIs executivos de cada bloco do prontuário 360°.

    Args:
        prontuario (Dict[str, Any]): Conteúdo do ``prontuario_executivo.json``.

    Returns:
        Dict[str, Any]: KPIs prontos para plotagem (valores podem ser ``None``).
    """
    # Bloco contábil: receita, IMC e ponto de equilíbrio.
    contabil = prontuario.get("contabil") or {}
    margem = contabil.get("analise_margem_operacional") or {}
    equilibrio = contabil.get("analise_ponto_critico_equilibrio") or {}

    # Bloco fiscal: composição real dos tributos destacados.
    fiscal = prontuario.get("fiscal") or {}
    composicao = fiscal.get("composicao_tributaria_real") or {}

    # Bloco financeiro: inadimplência e carteiras do mês.
    financeiro = prontuario.get("financeiro") or {}
    inadimplencia = financeiro.get("analise_inadimplencia") or {}
    carteiras = financeiro.get("top_10_carteiras_mes") or {}

    # Bloco de RH: equipe ativa e folha projetada.
    rh = prontuario.get("recursos_humanos") or {}
    pessoal = rh.get("indicadores_pessoal") or {}
    folha = rh.get("folha_salarial_12_meses") or {}

    # Bloco de estoque: capital imobilizado e autonomia.
    estoque = prontuario.get("estoque") or {}

    # Bloco estrutural: auditoria de saúde das tabelas do ERP.
    estrutural = prontuario.get("saude_estrutural_dados") or {}
    tabelas = [t for t in estrutural.values() if isinstance(t, dict)]
    com_duplicatas = [t for t in tabelas if (t.get("linhas_duplicadas") or 0) > 0]
    pct_duplicadas = len(com_duplicatas) / len(tabelas) * 100 if tabelas else None

    return {
        "receita": margem.get("receita_bruta_reais"),
        "imc": margem.get("indice_margem_percentual"),
        "margem_seguranca": equilibrio.get("margem_seguranca_reais"),
        "carga_tributaria": composicao.get("carga_efetiva_declarada_percentual"),
        "inadimplencia": inadimplencia.get("taxa_inadimplencia_percentual"),
        "consumo_mes": carteiras.get("consumo_total_mes_reais"),
        "mes_carteiras": carteiras.get("mes_referencia"),
        "clientes_mes": carteiras.get("total_clientes_no_mes"),
        "folha_media": folha.get("folha_media_mensal_reais"),
        "folha_natureza": folha.get("natureza"),
        "equipe": pessoal.get("total_colaboradores_ativos"),
        "turnover": pessoal.get("taxa_turnover_percentual"),
        "folha_receita": pessoal.get("percentual_folha_sobre_receita"),
        "capital_estoque": estoque.get("capital_total_imobilizado_reais"),
        "cobertura_dias": estoque.get("media_dias_cobertura_geral"),
        "skus": estoque.get("total_skus_cadastrados"),
        "pct_tabelas_duplicadas": pct_duplicadas,
        "total_tabelas": len(tabelas),
    }


# 'def _pontuar_eixos(...)' converte os KPIs em notas 0–100 do radar.
def _pontuar_eixos(kpis: Dict[str, Any]) -> Dict[str, float]:
    """Calcula a nota de saúde (0–100, quanto MAIOR melhor) de cada eixo do radar.

    Réguas internas da plataforma:
      - Margem (IMC): 0% → 0 · ≥40% → 100;
      - Carga tributária: ≤15% → 100 · ≥40% → 0 (quanto menor, melhor);
      - Inadimplência: 0% → 100 · ≥10% → 0;
      - Folha/Receita: ≤10% → 100 · ≥30% → 0;
      - Cobertura de estoque: ≤45 dias → 100 · ≥120 dias → 0 (capital preso);
      - Integridade estrutural: 0% das tabelas com duplicatas → 100 · ≥50% → 0.

    Args:
        kpis (Dict[str, Any]): KPIs de ``_extrair_kpis``.

    Returns:
        Dict[str, float]: Nota por eixo (eixos sem dado são omitidos).
    """

    def escala(valor: float, pior: float, melhor: float) -> float:
        """Interpola linearmente uma nota 0–100 entre dois limites de régua."""
        if (pior - melhor) == 0:
            return 0.0
        nota = (valor - pior) / (melhor - pior) * 100
        return float(np.clip(nota, 0, 100))

    eixos: Dict[str, float] = {}

    if kpis["imc"] is not None:
        eixos["Margem (IMC)"] = escala(kpis["imc"], 0.0, 40.0)
    if kpis["carga_tributaria"] is not None:
        eixos["Carga tributária"] = escala(kpis["carga_tributaria"], 40.0, 15.0)
    if kpis["inadimplencia"] is not None:
        eixos["Inadimplência"] = escala(kpis["inadimplencia"], 10.0, 0.0)
    if kpis["folha_receita"] is not None:
        eixos["Folha/Receita"] = escala(kpis["folha_receita"], 30.0, 10.0)
    if kpis["cobertura_dias"] is not None:
        eixos["Cobertura de estoque"] = escala(kpis["cobertura_dias"], 120.0, 45.0)
    if kpis["pct_tabelas_duplicadas"] is not None:
        eixos["Integridade dos dados"] = escala(
            kpis["pct_tabelas_duplicadas"], 50.0, 0.0
        )

    return eixos


# 'def _desenhar_cartao(...)' renderiza um cartão de KPI na placa.
def _desenhar_cartao(
    eixo: Any,
    x: float,
    y: float,
    largura: float,
    altura: float,
    rotulo: str,
    valor: str,
    nota: str = "",
    cor: str = TEXTO,
) -> None:
    """Desenha um cartão de KPI (fundo, rótulo, valor e nota).

    Args:
        eixo: Eixo matplotlib já configurado em coordenadas de figura (0–16, 0–9).
        x (float): Canto inferior esquerdo X.
        y (float): Canto inferior esquerdo Y.
        largura (float): Largura do cartão.
        altura (float): Altura do cartão.
        rotulo (str): Rótulo superior do KPI.
        valor (str): Valor destacado.
        nota (str): Nota de rodapé opcional.
        cor (str): Cor do valor destacado.
    """
    # Fundo arredondado com borda discreta.
    eixo.add_patch(
        FancyBboxPatch(
            (x, y),
            largura,
            altura,
            boxstyle="round,pad=0,rounding_size=0.12",
            linewidth=1.0,
            edgecolor=BORDA,
            facecolor=CARTAO,
        )
    )
    # Rótulo do KPI.
    eixo.text(
        x + 0.22,
        y + altura - 0.34,
        rotulo,
        fontsize=10.5,
        color=SECUNDARIO,
        va="center",
    )
    # Valor destacado.
    eixo.text(
        x + 0.22,
        y + altura - 0.88,
        valor,
        fontsize=19,
        fontweight="bold",
        color=cor,
        va="center",
    )
    # Nota de rodapé (quando existir).
    if nota:
        eixo.text(
            x + 0.22,
            y + 0.24,
            nota,
            fontsize=9,
            color=CINZA,
            va="center",
        )


# 'def _desenhar_radar(...)' desenha o radar polar com os eixos de saúde.
def _desenhar_radar(figura: Any, eixos: Dict[str, float]) -> Any:
    """Renderiza o radar polar 0–100 com os eixos de saúde disponíveis.

    Args:
        figura: Figura matplotlib pai.
        eixos (Dict[str, float]): Nota por eixo (vazio → apenas aviso).

    Returns:
        Any: Eixo polar criado.
    """
    # Cria o eixo polar sobreposto na faixa inferior esquerda da placa.
    # Dimensões deixam folga para os rótulos de categoria (fora do círculo)
    # sem invadir o título acima nem o rodapé abaixo.
    eixo_radar = figura.add_axes([0.04, 0.105, 0.26, 0.30], projection="polar")

    # Sem eixos apurados: devolve vazio (o chamador exibe o aviso).
    if not eixos:
        eixo_radar.set_visible(False)
        return eixo_radar

    # Ângulos igualmente espaçados, fechando o polígono no ponto inicial.
    rotulos = list(eixos.keys())
    notas = [eixos[rotulo] for rotulo in rotulos]
    angulos = np.linspace(0, 2 * np.pi, len(rotulos), endpoint=False)
    angulos_fechados = np.concatenate([angulos, angulos[:1]])
    notas_fechadas = np.concatenate([notas, notas[:1]])

    # Malha do radar.
    eixo_radar.set_theta_offset(np.pi / 2)
    eixo_radar.set_theta_direction(-1)
    eixo_radar.set_ylim(0, 100)
    eixo_radar.set_yticks([25, 50, 75, 100])
    eixo_radar.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color=CINZA)
    eixo_radar.set_xticks(angulos)
    eixo_radar.set_xticklabels(rotulos, fontsize=9, color=TEXTO)
    eixo_radar.tick_params(axis="x", pad=9)
    eixo_radar.grid(color=BORDA, linewidth=0.8)
    eixo_radar.spines["polar"].set_color(BORDA)

    # Polígono preenchido da saúde da companhia.
    eixo_radar.plot(angulos_fechados, notas_fechadas, color=RADAR, linewidth=2)
    eixo_radar.fill(angulos_fechados, notas_fechadas, color=RADAR, alpha=0.22)
    eixo_radar.scatter(angulos, notas, color=RADAR, s=34, zorder=5)

    return eixo_radar


# 'def gerar_dashboard_saude(...)' monta e grava a placa única de saúde 360°.
def gerar_dashboard_saude(
    dataset: str | None = None,
    prontuario: Dict[str, Any] | None = None,
    pasta_saida: Path | None = None,
) -> Path:
    """Gera o PNG do Dashboard/Radar de Saúde 360° da Fase 02.

    Args:
        dataset (str | None): Dataset alvo (usa o mais recente quando ``None``).
        prontuario (Dict[str, Any] | None): Prontuário já em memória (o
            orquestrador passa o dicionário recém-construído); quando ausente,
            o JSON persistido em disco é lido.
        pasta_saida (Path | None): Pasta de gravação (padrão: pasta da Fase 02).

    Returns:
        Path: Caminho do PNG gerado.

    Raises:
        FileNotFoundError: Quando não existe prontuário nem JSON para ler.
    """
    # Caso 1: prontuário fornecido em memória pelo orquestrador da Fase 02.
    if prontuario is not None:
        if pasta_saida is None:
            caminho_json = localizar_prontuario(dataset)
            if caminho_json is None:
                raise FileNotFoundError(
                    "Sem pasta de saída: informe 'pasta_saida' ou rode a Fase 02 "
                    "para existir um prontuario_executivo.json."
                )
            pasta_saida = caminho_json.parent
    else:
        # Caso 2: lê o JSON persistido em disco.
        caminho_json = localizar_prontuario(dataset)
        if caminho_json is None:
            raise FileNotFoundError(
                "prontuario_executivo.json não encontrado — execute a Fase 02 "
                "(raio-x) antes de gerar o dashboard de saúde."
            )
        with caminho_json.open(encoding="utf-8") as arquivo:
            prontuario = json.load(arquivo)
        if pasta_saida is None:
            pasta_saida = caminho_json.parent

    nome_dataset = prontuario.get("cliente_ativo", dataset or "dataset")
    kpis = _extrair_kpis(prontuario)
    eixos_radar = _pontuar_eixos(kpis)

    # Pasta de saída padrão: a mesma pasta da Fase 02 do dataset.
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_png = pasta_saida / "dashboard_saude_360.png"

    # ------------------------------------------------------------------
    # MONTAGEM DA PLACA (figura única 16×9 em coordenadas de figura)
    # ------------------------------------------------------------------
    figura, eixo = plt.subplots(figsize=(16, 9))
    eixo.set_xlim(0, 16)
    eixo.set_ylim(0, 9)
    eixo.axis("off")
    figura.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # --- Cabeçalho ---
    eixo.text(
        0.4,
        8.72,
        "Dashboard de Saúde 360° — Raio-X Empresarial",
        fontsize=24,
        fontweight="bold",
        color=TEXTO,
        va="center",
    )
    eixo.text(
        0.4,
        8.36,
        f"Dataset {nome_dataset} · Fase 02 (CRISP-DM) · KPIs consolidados "
        "dos 10 departamentos",
        fontsize=12,
        color=SECUNDARIO,
        va="center",
    )
    # Selo do dataset no canto superior direito.
    eixo.text(
        15.6,
        8.72,
        str(nome_dataset),
        fontsize=13,
        fontweight="bold",
        color=SECUNDARIO,
        va="center",
        ha="right",
    )
    eixo.plot([0.4, 15.6], [8.15, 8.15], color=BORDA, linewidth=1.4)

    # --- Cartões de KPI (4 colunas × 2 linhas) ---
    largura_cartao = (15.2 - 3 * 0.3) / 4
    colunas_x = [0.4 + i * (largura_cartao + 0.3) for i in range(4)]

    nota_folha = (
        "projeção sobre equipe real" if kpis["folha_natureza"] else "sem série de folha"
    )
    nota_carteiras = ""
    if kpis["mes_carteiras"]:
        nota_carteiras = f"mês {kpis['mes_carteiras']}"
        if kpis["clientes_mes"]:
            nota_carteiras += f" · {int(kpis['clientes_mes'])} clientes"

    cartoes = [
        (
            "Receita documentada (janela analisada)",
            _brl(kpis["receita"]) if kpis["receita"] is not None else "—",
            "somatório da visão canônica de vendas",
            TEXTO,
        ),
        (
            "Índice de margem de contribuição",
            _pct(kpis["imc"]) if kpis["imc"] is not None else "—",
            "receita − CMV − despesas variáveis",
            VERDE if (kpis["imc"] or 0) >= 30 else AMBAR,
        ),
        (
            "Carga tributária efetiva",
            _pct(kpis["carga_tributaria"], 2)
            if kpis["carga_tributaria"] is not None
            else "—",
            "tributos declarados ÷ valor das NF-e",
            AMBAR if (kpis["carga_tributaria"] or 0) > 20 else VERDE,
        ),
        (
            "Inadimplência sobre títulos",
            _pct(kpis["inadimplencia"], 2)
            if kpis["inadimplencia"] is not None
            else "—",
            "títulos em risco ÷ carteira total",
            VERDE if (kpis["inadimplencia"] or 0) <= 2 else VERMELHO,
        ),
        (
            "Folha média mensal (projetada)",
            _brl(kpis["folha_media"]) if kpis["folha_media"] is not None else "—",
            nota_folha,
            TEXTO,
        ),
        (
            "Equipe ativa",
            f"{int(kpis['equipe'])} pessoas" if kpis["equipe"] is not None else "—",
            (
                "turnover " + _pct(kpis["turnover"])
                if kpis["turnover"] is not None
                else "vínculos reais do ERP"
            ),
            TEXTO,
        ),
        (
            "Capital imobilizado em estoque",
            _brl(kpis["capital_estoque"])
            if kpis["capital_estoque"] is not None
            else "—",
            (
                f"cobertura {kpis['cobertura_dias']:.0f} dias · "
                f"{_num(kpis['skus'])} SKUs"
                if kpis["cobertura_dias"] is not None
                else "saldo × custo"
            ),
            TEXTO,
        ),
        (
            "Consumo das carteiras no mês",
            _brl(kpis["consumo_mes"]) if kpis["consumo_mes"] is not None else "—",
            nota_carteiras or "top carteiras/cadernetas",
            TEXTO,
        ),
    ]

    for indice, (rotulo, valor, nota, cor) in enumerate(cartoes):
        linha = indice // 4
        coluna = indice % 4
        # Linha 0: 6.70..8.05  |  Linha 1: 5.05..6.40
        y_cartao = 6.70 if linha == 0 else 5.05
        _desenhar_cartao(
            eixo,
            colunas_x[coluna],
            y_cartao,
            largura_cartao,
            1.35,
            rotulo,
            valor,
            nota,
            cor,
        )

    # --- Radar de saúde (faixa inferior esquerda) ---
    indice_geral = (
        round(float(np.mean(list(eixos_radar.values())))) if eixos_radar else None
    )
    eixo.text(
        2.72,
        4.52,
        "Radar de Saúde 360°",
        fontsize=15,
        fontweight="bold",
        color=TEXTO,
        va="center",
        ha="center",
    )
    if indice_geral is not None:
        eixo.text(
            2.72,
            4.20,
            f"Índice geral: {indice_geral}/100",
            fontsize=11,
            fontweight="bold",
            color=RADAR,
            va="center",
            ha="center",
        )
    _desenhar_radar(figura, eixos_radar)

    # --- Semáforo de sinais (faixa inferior direita) ---
    eixo.text(
        5.9,
        4.52,
        "Semáforo de sinais de saúde",
        fontsize=15,
        fontweight="bold",
        color=TEXTO,
        va="center",
    )

    # Linha de cabeçalho da tabela.
    eixo.text(6.12, 4.12, "INDICADOR", fontsize=10, fontweight="bold", color=CINZA, va="center")
    eixo.text(10.9, 4.12, "VALOR APURADO", fontsize=10, fontweight="bold", color=CINZA, va="center")
    eixo.text(13.7, 4.12, "SINAL", fontsize=10, fontweight="bold", color=CINZA, va="center")
    eixo.plot([5.9, 15.6], [3.92, 3.92], color=BORDA, linewidth=1.0)

    # Linhas do semáforo: (indicador, valor textual, status).
    duplicadas = kpis["pct_tabelas_duplicadas"]
    linhas = [
        (
            "Integridade estrutural das tabelas do ERP",
            (
                # Texto curto: a coluna VALOR tem largura fixa antes do SINAL.
                f"{duplicadas:.0f}% de {kpis['total_tabelas']} tabelas"
                if duplicadas is not None
                else "—"
            ),
            _status_semaforo(duplicadas, 10, 30),
        ),
        (
            "Inadimplência da carteira a receber",
            _pct(kpis["inadimplencia"], 2)
            if kpis["inadimplencia"] is not None
            else "—",
            _status_semaforo(kpis["inadimplencia"], 2, 5),
        ),
        (
            "Margem de contribuição (IMC)",
            _pct(kpis["imc"]) if kpis["imc"] is not None else "—",
            _status_semaforo(kpis["imc"], 30, 15, invertido=True),
        ),
        (
            "Carga tributária efetiva sobre o faturamento",
            _pct(kpis["carga_tributaria"], 2)
            if kpis["carga_tributaria"] is not None
            else "—",
            _status_semaforo(kpis["carga_tributaria"], 20, 30),
        ),
        (
            "Folha sobre a receita",
            _pct(kpis["folha_receita"]) if kpis["folha_receita"] is not None else "—",
            _status_semaforo(kpis["folha_receita"], 15, 25),
        ),
        (
            "Autonomia de estoque (dias de cobertura)",
            (
                f"{kpis['cobertura_dias']:.0f} dias"
                if kpis["cobertura_dias"] is not None
                else "—"
            ),
            _status_semaforo(kpis["cobertura_dias"], 60, 90),
        ),
    ]

    # Cores e rótulos do semáforo.
    cores_status = {
        "verde": VERDE,
        "ambar": AMBAR,
        "vermelho": VERMELHO,
        "neutro": CINZA,
    }
    rotulos_status = {
        "verde": "SAUDÁVEL",
        "ambar": "ATENÇÃO",
        "vermelho": "CRÍTICO",
        "neutro": "SEM DADO",
    }

    # Desenha cada linha do semáforo.
    for indice, (indicador, valor_texto, status) in enumerate(linhas):
        y_linha = 3.55 - indice * 0.48
        cor = cores_status[status]
        # Ponto colorido do semáforo.
        eixo.plot(
            [6.12],
            [y_linha],
            marker="o",
            markersize=11,
            color=cor,
            markeredgecolor="#ffffff",
            markeredgewidth=1.4,
        )
        eixo.text(6.45, y_linha, indicador, fontsize=12, color=TEXTO, va="center")
        eixo.text(10.9, y_linha, valor_texto, fontsize=12, color=SECUNDARIO, va="center")
        eixo.text(
            13.7,
            y_linha,
            rotulos_status[status],
            fontsize=11.5,
            fontweight="bold",
            color=cor,
            va="center",
        )
        # Régua de linhas alternadas.
        if indice < len(linhas) - 1:
            eixo.plot(
                [5.9, 15.6],
                [y_linha - 0.24, y_linha - 0.24],
                color=BORDA,
                linewidth=0.6,
            )

    # --- Rodapé ---
    eixo.text(
        0.4,
        0.42,
        "Fonte: prontuario_executivo.json (Fase 02 — Raio-X Empresarial). "
        "Notas do radar e semáforo: régua interna da plataforma; sem dado → eixo omitido / SEM DADO.",
        fontsize=9.5,
        color=CINZA,
        va="center",
    )

    # Grava em alta resolução e libera o buffer.
    figura.savefig(caminho_png, dpi=200, facecolor="white")
    plt.close(figura)

    logging.info("Dashboard/Radar de Saúde 360° salvo em: %s", caminho_png)
    return caminho_png


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    # 'argparse' interpreta os parâmetros de linha de comandos do script.
    import argparse

    analisador_cli = argparse.ArgumentParser(
        description="Gera o Dashboard de Saúde 360° da Fase 02."
    )
    analisador_cli.add_argument(
        "--dataset",
        default=None,
        help="Nome do dataset (usa o prontuário mais recente quando omitido).",
    )
    argumentos = analisador_cli.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — [%(levelname)s] — %(message)s",
    )
    gerar_dashboard_saude(dataset=argumentos.dataset)
