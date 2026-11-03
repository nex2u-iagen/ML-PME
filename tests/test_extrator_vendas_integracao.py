# -*- coding: utf-8 -*-
"""Teste de integração para o ExtratorVendas com dados reais do mercadinho-t3.

Valida o extrator genérico end-to-end com dados reais do ERP, incluindo:
- Detecção automática de tabela de vendas
- Detecção automática de colunas ID e valor
- Estratégia resiliente de data (join com erp_nfecob)
- Separação temporal: 5 anos + 12 meses
- Carregamento de parâmetros de negócio
"""

import unittest
import pandas as pd

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import ExtratorVendas
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


class TestExtratorVendasIntegracao(unittest.TestCase):
    """Teste de integração com dados reais."""

    @classmethod
    def setUpClass(cls):
        cls.resolvedor = ResolvedorSemantico()
        cls.leitor = LeitorArquivosTabulares()
        cls.extrator = ExtratorVendas(
            pasta_dados="dados/brutos/csv/mercadinho-t3",
            nome_dataset="mercadinho-t3"
        )
        cls.extrator.leitor = cls.leitor
        cls.extrator.resolvedor = cls.resolvedor

    def test_extrator_detecta_tabela_vendas(self):
        """Deve detectar automaticamente erp_nfetotal.csv como tabela de vendas."""
        caminho = self.extrator.localizar_arquivo_tabela()
        self.assertIsNotNone(caminho)
        self.assertIn("nfetotal", caminho.name.lower())

    def test_extrator_extrai_dados_com_datas(self):
        """Deve extrair dados com datas válidas via join resiliente."""
        resultado = self.extrator.extrair_visao_canonica()
        self.assertGreater(len(resultado), 0)
        self.assertIn("id_pedido", resultado.columns)
        self.assertIn("data_emissao", resultado.columns)
        self.assertIn("valor_total", resultado.columns)
        self.assertIn("ano", resultado.columns)
        self.assertIn("ano_mes", resultado.columns)

    def test_extrator_datas_nao_sao_todas_nat(self):
        """Pelo menos algumas datas devem ser válidas (não todas NaT)."""
        resultado = self.extrator.extrair_visao_canonica()
        datas_validas = resultado["data_emissao"].notna().sum()
        self.assertGreater(datas_validas, 0)
        self.assertEqual(datas_validas, len(resultado))

    def test_extrator_tem_recortes_temporais(self):
        """Deve ter recortes de 5 anos e 12 meses anexados."""
        resultado = self.extrator.extrair_visao_canonica()
        recortes = self.extrator.obter_recortes_temporais()
        self.assertIsNotNone(recortes)
        self.assertIn("anos_disponiveis", recortes)
        self.assertIn("meses_disponiveis", recortes)
        self.assertGreaterEqual(len(recortes["anos_disponiveis"]), 1)
        self.assertGreaterEqual(len(recortes["meses_disponiveis"]), 1)

    def test_extrator_parametros_negocio_carregados(self):
        """Deve carregar parâmetros de negócio com defaults."""
        self.assertIn("cmv_taxa", self.extrator.parametros_negocio)
        self.assertIn("icms_aliquota", self.extrator.parametros_negocio)
        self.assertEqual(self.extrator.parametros_negocio["cmv_taxa"], 0.55)

    def test_extrator_ano_mes_para_agregacao_mensal(self):
        """Deve gerar ano_mes para agregação mensal."""
        resultado = self.extrator.extrair_visao_canonica()
        meses_unicos = resultado["ano_mes"].unique()
        self.assertGreaterEqual(len(meses_unicos), 1)
        # Verificar formato YYYY-MM
        for mes in meses_unicos[:3]:
            self.assertRegex(mes, r"^\d{4}-\d{2}$")

    def test_extrator_anos_para_agregacao_anual(self):
        """Deve gerar coluna ano para agregação anual."""
        resultado = self.extrator.extrair_visao_canonica()
        anos_unicos = resultado["ano"].unique()
        self.assertGreaterEqual(len(anos_unicos), 1)
        # Deve incluir anos recentes (2022-2026)
        anos_int = [int(a) for a in anos_unicos]
        self.assertTrue(any(a >= 2022 for a in anos_int))


if __name__ == "__main__":
    unittest.main()
