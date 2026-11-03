"""Módulo de Simulação e Transição da Reforma Tributária Brasileira (EC 132/2023).

Responsável por calcular a tributação sob o modelo legado (ICMS, PIS, COFINS, ISS)
e simular dinamicamente o modelo de IVA Dual (CBS Federal + IBS Subnacional),
permitindo que os Data Marts de BI e modelos de ML avaliem cenários reais e futuros.
"""

# 'import' traz o módulo 'logging' nativo para registrar mensagens operacionais com data
# e hora.
import logging

# 'from' acessa o módulo 'typing' para anotações de tipagem estática (Type Hints).
# 'Dict' documenta dicionários de chave e valor; 'Tuple' documenta tuplas imutáveis de
# dados.
# 'import' traz a biblioteca externa 'pandas' para manipulação tabular de dados.
# 'as' define o apelido reduzido 'pd'.
import pandas as pd

# 'logging.basicConfig' configura a exibição de registros informativos no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o motor matemático tributário no padrão orientado a objetos.
class CalculadoraReformaTributaria:
    """Motor desacoplado de apuração e transição para o novo IVA Dual brasileiro."""

    # 'def' define o construtor da classe.
    # 'aliquota_cbs_padrao: float = 0.088' define a alíquota padrão estimada da CBS
    # federal (8.8%).
    # 'aliquota_ibs_padrao: float = 0.177' define a alíquota padrão estimada do IBS
    # estadual/municipal (17.7%).
    # 'soma_aliquota_iva_dual' representa a alíquota neutra estimada de consumo (em
    # torno de 26.5% a 27.5%).
    def __init__(
        self,
        aliquota_cbs_padrao: float = 0.088,
        aliquota_ibs_padrao: float = 0.177,
    ) -> None:
        """Inicializa a calculadora fiscal parametrizando as alíquotas do novo regime.

        Args:
            aliquota_cbs_padrao (float): Alíquota federal estimada da CBS (ex.: 0.088
            para 8.8%).
            aliquota_ibs_padrao (float): Alíquota subnacional estimada do IBS (ex.:
            0.177 para 17.7%).
        """
        # Armazena a alíquota da Contribuição sobre Bens e Serviços no objeto.
        self.aliquota_cbs = aliquota_cbs_padrao

        # Armazena a alíquota do Imposto sobre Bens e Serviços no objeto.
        self.aliquota_ibs = aliquota_ibs_padrao

        # Calcula a alíquota nominal total do IVA Dual somando as duas esferas.
        self.aliquota_iva_total = self.aliquota_cbs + self.aliquota_ibs

        # Emite log confirmando a prontidão do motor fiscal de transição.
        logging.info(
            "Calculadora da Reforma Tributária ativa. CBS: %.1f%% | IBS: %.1f%% | Total"
            "IVA: %.1f%%.",
            self.aliquota_cbs * 100,
            self.aliquota_ibs * 100,
            self.aliquota_iva_total * 100,
        )

    # 'def' define o método que calcula os tributos projetados no novo modelo IVA Dual.
    # 'valor_operacao: float' recebe o valor faturado da nota fiscal em reais.
    # '-> Dict[str, float]' documenta que o retorno será um dicionário contendo o
    # desdobramento da nova carga.
    def calcular_projecao_iva_dual(self, valor_operacao: float) -> dict[str, float]:
        """Calcula o montante monetário de CBS e IBS com base no novo modelo de
        tributação por fora.

        Args:
            valor_operacao (float): Valor bruto faturado da mercadoria ou serviço em
            reais.

        Returns:
            Dict[str, float]: Dicionário com CBS, IBS, total de IVA Dual e receita
            líquida projetada.
        """
        # Calcula o valor financeiro da CBS federal aplicando a alíquota sobre o valor
        # da operação.
        valor_cbs = round(valor_operacao * self.aliquota_cbs, 2)

        # Calcula o valor financeiro do IBS estadual/municipal aplicando a alíquota
        # correspondente.
        valor_ibs = round(valor_operacao * self.aliquota_ibs, 2)

        # Soma os dois novos tributos para apurar o montante total de IVA Dual
        # incidente.
        total_iva_dual = round(valor_cbs + valor_ibs, 2)

        # Calcula a receita líquida pré-tributária subtraindo o IVA projetado do total
        # faturado.
        receita_liquida_projetada = round(valor_operacao - total_iva_dual, 2)

        # 'return' devolve o laudo do novo modelo tributário estruturado.
        return {
            "valor_cbs_projetado_reais": valor_cbs,
            "valor_ibs_projetado_reais": valor_ibs,
            "total_iva_dual_projetado_reais": total_iva_dual,
            "receita_liquida_nova_regra_reais": receita_liquida_projetada,
            "aliquota_efetiva_iva_pct": round(self.aliquota_iva_total * 100, 2),
        }

    # 'def' define o método vetorizado para enriquecer DataFrames inteiros com a visão
    # de transição.
    # 'df: pd.DataFrame' recebe a tabela de notas fiscais do ERP.
    # 'coluna_valor: str' indica o nome da coluna que armazena a receita faturada da
    # transação.
    def enriquecer_tabela_com_cenario_transicao(
        self, df: pd.DataFrame, coluna_valor: str = "valor_bruto_faturado_reais"
    ) -> pd.DataFrame:
        """Enriquece a tabela fiscal adicionando colunas de simulação do IVA Dual lado a
        lado com os impostos legados.

        Args:
            df (pd.DataFrame): Tabela de notas fiscais contendo tributos legados.
            coluna_valor (str): Nome da coluna com o valor da operação comercial.

        Returns:
            pd.DataFrame: Tabela expandida com colunas comparativas do Regime Legado vs.
            Novo IVA Dual.
        """
        # '.copy()' cria uma cópia independente para manipulação segura em memória RAM.
        df_enriquecido = df.copy()

        # Calcula de forma vetorizada a CBS projetada para todas as linhas da tabela.
        df_enriquecido["cbs_projetada_reais"] = (
            df_enriquecido[coluna_valor] * self.aliquota_cbs
        ).round(2)

        # Calcula de forma vetorizada o IBS projetado para todas as notas.
        df_enriquecido["ibs_projetado_reais"] = (
            df_enriquecido[coluna_valor] * self.aliquota_ibs
        ).round(2)

        # Soma a CBS e o IBS projetados gerando a carga tributária total sob a Reforma
        # Tributária.
        df_enriquecido["total_iva_dual_reais"] = (
            df_enriquecido["cbs_projetada_reais"]
            + df_enriquecido["ibs_projetado_reais"]
        ).round(2)

        # 'return' entrega o DataFrame pronto para alimentar dashboards de impacto
        # tributário.
        return df_enriquecido
