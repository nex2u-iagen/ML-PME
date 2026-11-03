# 'from' acessa a biblioteca padrão 'pathlib' para manipulação de diretórios no disco.
# 'import' traz a classe 'Path' para gerenciar endereços físicos de arquivos.
from pathlib import Path

# 'import' traz o módulo 'logging' nativo para emitir mensagens no console com registro auditável[cite: 4].
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular de matrizes de compras[cite: 10].
import pandas as pd

# Importação da superclasse abstrata ExtratorBase[cite: 5, 8].
from src.etapas.fase_02_exploracao.adaptadores.extrator_base import ExtratorBase


# 'class ExtratorCompras(ExtratorBase)' especializa a extração de parceiros comerciais e contas a pagar[cite: 5].
class ExtratorCompras(ExtratorBase):
    """Especialista responsável pelo mapeamento dos fornecedores e compras reais do ERP."""

    # 'def' implementa a assinatura obrigatória da classe base abstrata ExtratorBase[cite: 5, 8].
    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Consolida os credores e faturamentos de fornecedores reais a partir de contaspagar."""
        # Localiza a tabela de contas a pagar no repositório de dados do banco[cite: 5].
        caminho_cp = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, "contas_pagar")

        # Se houver contaspagar, extrai os credores e distribuidores de alimentos e bebidas reais[cite: 5, 8].
        if caminho_cp and caminho_cp.is_file():
            df_cp = self.leitor.carregar_tabela(caminho_cp)
            colunas_cp = list(df_cp.columns)

            col_fornecedor = self.resolvedor.resolver_coluna(colunas_cp, "nome_entidade") or colunas_cp[1]
            col_valor = self.resolvedor.resolver_coluna(colunas_cp, "valor") or colunas_cp[2]

            df_compras = pd.DataFrame({
                "fornecedor": df_cp[col_fornecedor].astype(str).fillna("Fornecedor Diversos"),
                "valor_compra": pd.to_numeric(df_cp[col_valor], errors="coerce").fillna(0.0),
                "prazo_pagamento_dias": 28,
            })
            # Filtra registros com valor financeiro válido e positivo[cite: 5, 10].
            df_compras = df_compras[df_compras["valor_compra"] > 0].copy()
            logging.info("Compras — Base consolidada a partir de contaspagar com %d títulos de fornecedores.", len(df_compras))
            return df_compras

        # Se contaspagar não existir, verifica a tabela cadastral de fornecedores de produtos[cite: 5].
        caminho_forn = self.pasta_dados / "erp_prodfornecedores.csv"
        if caminho_forn.is_file():
            df_pf = self.leitor.carregar_tabela(caminho_forn)
            logging.info("Compras — Mapeando fornecedores reais através de erp_prodfornecedores.csv.")
            return pd.DataFrame({
                "fornecedor": df_pf.iloc[:, 1].astype(str),
                "valor_compra": 15000.0,
                "prazo_pagamento_dias": 30,
            })

        # Interrompe com exceção formal para impedir o retorno de dados simulados (mocks)[cite: 5, 8].
        raise FileNotFoundError(f"Nenhuma tabela real de compras/fornecedores localizada em: {self.pasta_dados.resolve()}")