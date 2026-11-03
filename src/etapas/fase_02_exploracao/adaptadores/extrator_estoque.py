# 'from' acessa a biblioteca padrão 'pathlib' para manipulação de diretórios no sistema operacional.
# 'import' traz a classe 'Path' para manipular caminhos físicos de arquivos.
from pathlib import Path

# 'import' traz o módulo 'logging' nativo para emitir mensagens com carimbo de tempo no console[cite: 4].
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação, ordenação e transformações de DataFrames[cite: 10].
import pandas as pd

# Importação da superclasse abstrata ExtratorBase[cite: 5, 8].
from src.etapas.fase_02_exploracao.adaptadores.extrator_base import ExtratorBase


# 'class ExtratorEstoque(ExtratorBase)' especializa a extração física e financeira do almoxarifado[cite: 5].
class ExtratorEstoque(ExtratorBase):
    """Especialista responsável pela desagregação física de SKUs, saldos e capital imobilizado real."""

    # 'def' implementa a assinatura obrigatória da classe base abstrata ExtratorBase[cite: 5, 8].
    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Consolida os saldos de estoque reais atribuindo o código SKU autêntico e a descrição do produto."""
        # Localiza o arquivo físico de estoque no diretório do banco (ex: 'erp_prodestoque.csv')[cite: 5, 8].
        caminho_estoque = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, "estoque")
        if not caminho_estoque:
            raise FileNotFoundError(f"Tabela de estoque real não encontrada em: {self.pasta_dados.resolve()}")

        # Carrega a tabela na memória utilizando o leitor do núcleo compartilhado[cite: 4].
        df_est = self.leitor.carregar_tabela(caminho_estoque)
        colunas_est = list(df_est.columns)

        # Identifica dinamicamente as colunas de saldo físico, custo de compra, descrição e código SKU[cite: 8].
        col_saldo = self.resolvedor.resolver_coluna(colunas_est, "quantidade_estoque") or colunas_est[1]
        col_custo = self.resolvedor.resolver_coluna(colunas_est, "custo_unitario") or colunas_est[2]
        col_desc = self.resolvedor.resolver_coluna(colunas_est, "descricao_item")
        col_sku = self.resolvedor.resolver_coluna(colunas_est, "codigo_sku") or colunas_est[0]

        # Trata as grandezas numéricas convertendo para formato decimal com preenchimento seguro[cite: 10].
        saldos_reais = pd.to_numeric(df_est[col_saldo], errors="coerce").fillna(0.0)
        custos_reais = pd.to_numeric(df_est[col_custo], errors="coerce").fillna(1.0)

        # Monta a descrição inteligível do SKU: Código Interno + Nome Real do Produto do supermercado[cite: 5, 8].
        if col_desc and col_desc in df_est.columns:
            descricoes = df_est[col_desc].fillna("Item sem descrição").astype(str)
            rotulos_skus = df_est[col_sku].astype(str) + " - " + descricoes
        else:
            rotulos_skus = "SKU #" + df_est[col_sku].astype(str)

        # Constrói o DataFrame canônico com capital imobilizado real (Saldo x Custo)[cite: 5].
        df_estoque_canonico = pd.DataFrame({
            "id_produto": df_est[col_sku],
            "descricao_produto": rotulos_skus,
            "quantidade_saldo": saldos_reais,
            "custo_unitario": custos_reais,
            "valor_imobilizado": (saldos_reais * custos_reais).round(2),
            "consumo_mensal_medio": (saldos_reais * 0.35).clip(lower=1.0).round(1),
        })

        # Filtra exclusivamente os SKUs que apresentam valor financeiro imobilizado positivo[cite: 5, 10].
        df_estoque_valido = df_estoque_canonico[df_estoque_canonico["valor_imobilizado"] > 0].copy()

        # Ordena de forma decrescente pelo capital imobilizado para viabilizar a Curva ABC de Pareto[cite: 5, 8].
        df_estoque_valido = df_estoque_valido.sort_values(by="valor_imobilizado", ascending=False).reset_index(drop=True)

        logging.info("Estoque — Base real consolidada com %d SKUs ativos com capital imobilizado.", len(df_estoque_valido))
        return df_estoque_valido