# 'from' acessa a biblioteca padrão 'pathlib' para manipulação orientada a objetos de caminhos no disco.
# 'import' traz a classe 'Path' para representar diretórios.
from pathlib import Path

# 'import' traz o módulo 'logging' nativo para emitir mensagens com carimbo de tempo no console[cite: 4].
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação matemática de matrizes e datas[cite: 10].
import pandas as pd

# Importação da superclasse abstrata ExtratorBase[cite: 5, 8].
from src.etapas.fase_02_exploracao.adaptadores.extrator_base import ExtratorBase


# 'class ExtratorFinanceiro(ExtratorBase)' especializa a análise de liquidez e envelhecimento de títulos[cite: 5, 7].
class ExtratorFinanceiro(ExtratorBase):
    """Especialista responsável pelo cálculo do Aging real e apuração de risco em contas a receber."""

    # 'def' implementa a assinatura obrigatória da classe base abstrata ExtratorBase[cite: 5, 8].
    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Consolida os títulos reais de contas a receber e distribui os saldos por faixas reais de vencimento."""
        # Localiza o arquivo físico de contas a receber no diretório do banco[cite: 5].
        caminho_cr = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, "contas_receber")
        if not caminho_cr:
            raise FileNotFoundError(f"Tabela de contas a receber não encontrada em: {self.pasta_dados.resolve()}")

        # Carrega a tabela na memória RAM com o leitor defensivo do núcleo[cite: 4].
        df_cr = self.leitor.carregar_tabela(caminho_cr)
        colunas_cr = list(df_cr.columns)

        # Identifica dinamicamente as colunas de valor, data de vencimento e liquidação[cite: 8].
        col_valor = self.resolvedor.resolver_coluna(colunas_cr, "valor") or colunas_cr[1]
        col_venc = self.resolvedor.resolver_coluna(colunas_cr, "data_vencimento")
        col_pagto = self.resolvedor.resolver_coluna(colunas_cr, "data_pagamento")
        col_status = self.resolvedor.resolver_coluna(colunas_cr, "status_cobranca") or colunas_cr[-1]

        # Trata os valores monetários convertendo para formato decimal numérico[cite: 10].
        valores_monetarios = pd.to_numeric(df_cr[col_valor], errors="coerce").fillna(0.0)

        # CÁLCULO DE AGING REAL: Se a tabela possuir coluna de vencimento, computa as faixas matemáticas de atraso[cite: 5, 9].
        if col_venc and col_venc in df_cr.columns:
            datas_venc = pd.to_datetime(df_cr[col_venc], errors="coerce")
            datas_pagto = pd.to_datetime(df_cr[col_pagto], errors="coerce") if col_pagto else pd.Series(pd.NaT, index=df_cr.index)
            data_referencia = datas_venc.max() if not datas_venc.dropna().empty else pd.Timestamp("2026-10-01")

            def classificar_faixa(linha: pd.Series) -> str:
                # Se o título apresentar data de liquidação preenchida, é classificado como recebido.
                if pd.notna(linha["pagto"]):
                    return "Liquidado"
                venc = linha["venc"]
                if pd.isna(venc):
                    return "Liquidado"
                # Calcula a diferença em dias entre a data de corte e o vencimento do título.
                dias = (data_referencia - venc).days
                if dias <= 0:
                    return "A Vencer (No Prazo)"
                elif dias <= 30:
                    return "Atraso 1 a 30 dias"
                elif dias <= 60:
                    return "Atraso 31 a 60 dias"
                elif dias <= 90:
                    return "Atraso 61 a 90 dias"
                else:
                    return "Atraso > 90 dias (Crítico)"

            df_temp = pd.DataFrame({"venc": datas_venc, "pagto": datas_pagto})
            status_calculado = df_temp.apply(classificar_faixa, axis=1)
        else:
            # Fallback semântico caso não haja coluna temporal de vencimento no banco[cite: 8].
            status_calculado = df_cr[col_status].astype(str)

        # Monta a tabela canônica com valor financeiro e a classificação do título[cite: 5].
        df_financeiro = pd.DataFrame({
            "valor_total": valores_monetarios,
            "status_pagamento": status_calculado,
        })

        # Filtra exclusivamente os títulos com saldo financeiro ativo e positivo[cite: 5, 10].
        df_financeiro = df_financeiro[df_financeiro["valor_total"] > 0].copy()
        logging.info("Financeiro — Aging Real consolidado sobre %d títulos auditados.", len(df_financeiro))
        return df_financeiro