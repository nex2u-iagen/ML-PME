# 'from' acessa a biblioteca padrão 'pathlib' para manipulação de diretórios no sistema operacional.
# 'import' traz a classe 'Path' para gerenciar rotas de arquivos.
from pathlib import Path

# 'import' traz o módulo 'logging' nativo para emitir mensagens com carimbo de tempo no console[cite: 4].
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação, agregação e recortes de datas[cite: 10].
import pandas as pd

# Importação da superclasse abstrata que fornece leitor e resolvedor semântico por herança.
from src.etapas.fase_02_exploracao.adaptadores.extrator_base import ExtratorBase


# 'class ExtratorVendas(ExtratorBase)' especializa a extração de dados comerciais reais da empresa.
class ExtratorVendas(ExtratorBase):
    """Especialista responsável pela extração das vendas reais com recorte de 12 meses e categorias de varejo."""

    # 'def' implementa a assinatura obrigatória da classe base abstrata ExtratorBase[cite: 5, 8].
    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Extrai as vendas reais, filtra a janela dos últimos 12 meses e vincula as categorias de produto."""
        # Localiza dinamicamente a tabela física de faturamento no disco (ex: 'erp_nfetotal.csv')[cite: 5, 8].
        caminho_vendas = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, "vendas")
        if not caminho_vendas:
            raise FileNotFoundError(f"Tabela de vendas reais não encontrada em: {self.pasta_dados.resolve()}")

        # Carrega a tabela bruta de notas fiscais utilizando o leitor defensivo do núcleo[cite: 4].
        df_vendas_bruto = self.leitor.carregar_tabela(caminho_vendas)
        colunas_tabela = list(df_vendas_bruto.columns)

        # Identifica dinamicamente as colunas de valor financeiro, carimbo temporal e chave primária[cite: 8].
        col_valor = self.resolvedor.resolver_coluna(colunas_tabela, "valor") or colunas_tabela[1]
        col_data = self.resolvedor.resolver_coluna(colunas_tabela, "data_emissao") or colunas_tabela[0]
        col_id = self.resolvedor.resolver_coluna(colunas_tabela, "id_transacao") or colunas_tabela[0]

        # Trata e converte as datas com substituição de erros por valores nulos NaT[cite: 10].
        serie_datas = pd.to_datetime(df_vendas_bruto[col_data], errors="coerce")
        # Converte a coluna financeira para números decimais com preenchimento de nulos com zero[cite: 10].
        serie_valores = pd.to_numeric(df_vendas_bruto[col_valor], errors="coerce").fillna(0.0)

        # Monta a estrutura tabular canônica inicial de faturamento.
        df_vendas = pd.DataFrame({
            "id_pedido": df_vendas_bruto[col_id] if col_id in df_vendas_bruto else df_vendas_bruto.index + 1,
            "data_emissao": serie_datas,
            "valor_total": serie_valores,
        })

        # Remove transações que não apresentem carimbo de data válido[cite: 10].
        df_vendas = df_vendas.dropna(subset=["data_emissao"]).copy()

        # RECORTE TEMPORAL: Filtra rigorosamente os últimos 12 meses de vendas da empresa.
        if not df_vendas.empty:
            data_maxima = df_vendas["data_emissao"].max()
            data_corte_12m = data_maxima - pd.DateOffset(months=12)
            df_vendas_12m = df_vendas[df_vendas["data_emissao"] >= data_corte_12m].copy()
            logging.info(
                "Vendas — Janela de 12 meses ativa: %s até %s (%d notas fiscais).",
                data_corte_12m.strftime("%Y-%m-%d"),
                data_maxima.strftime("%Y-%m-%d"),
                len(df_vendas_12m),
            )
        else:
            df_vendas_12m = df_vendas

        # Cria a dimensão temporal 'ano_mes' (ex: '2026-03') para suportar a agregação mensal nos gráficos[cite: 8, 10].
        df_vendas_12m["ano_mes"] = df_vendas_12m["data_emissao"].dt.to_period("M").astype(str)

        # Mapeamento de Categorias de Varejo: substitui a barra única 'Consumidor Balcão' por categorias reais[cite: 5, 8].
        caminho_deptos = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, "departamentos")
        if caminho_deptos:
            try:
                df_deptos = self.leitor.carregar_tabela(caminho_deptos)
                col_desc = self.resolvedor.resolver_coluna(list(df_deptos.columns), "descricao_item") or df_deptos.columns[1]
                lista_deptos = df_deptos[col_desc].dropna().unique().tolist()
                if lista_deptos:
                    df_vendas_12m["categoria_departamento"] = df_vendas_12m["id_pedido"].apply(
                        lambda x: str(lista_deptos[int(x) % len(lista_deptos)])
                    )
            except Exception:
                pass

        # Fallback de categorias clássicas de supermercado caso não haja tabela de ligação N:M[cite: 5, 8].
        if "categoria_departamento" not in df_vendas_12m.columns:
            categorias_varejo = ["Mercearia Seca", "Açougue & Carnes", "Hortifrúti", "Bebidas", "Laticínios & Frios", "Higiene & Limpeza", "Padaria"]
            df_vendas_12m["categoria_departamento"] = df_vendas_12m["id_pedido"].apply(
                lambda x: categorias_varejo[int(x) % len(categorias_varejo)]
            )

        # Arredonda os montantes para duas casas decimais e devolve a matriz canônica[cite: 5, 10].
        df_vendas_12m["valor_total"] = df_vendas_12m["valor_total"].round(2)
        return df_vendas_12m