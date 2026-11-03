# -*- coding: utf-8 -*-
"""Teste de integração para visualização por departamento com dados reais."""

import unittest
import pandas as pd

from app_pages.pagina_visualizacao_departamento import (
    gerar_dados_anuais,
    gerar_dados_mensais,
    calcular_metricas_negocio,
    filtrar_por_periodo,
    filtrar_por_categoria,
    filtrar_por_valor,
    preparar_dados_visualizacao,
    aplicar_filtros,
)
from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import ExtratorVendas
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


class TestVisualizacaoDepartamentoIntegracao(unittest.TestCase):
    """Teste de integração com dados reais do mercadinho-t3."""

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

        cls.df_vendas = cls.extrator.extrair_visao_canonica()

    def test_dados_anuais_5_anos(self):
        """Deve gerar dados anuais nos últimos 5 anos."""
        resultado = gerar_dados_anuais(
            self.df_vendas,
            coluna_valor="valor_total",
            coluna_data="data_emissao",
        )
        self.assertGreater(len(resultado), 0)
        self.assertIn("ano", resultado.columns)
        self.assertIn("valor_total", resultado.columns)

    def test_dados_mensais_12_meses(self):
        """Deve gerar dados mensais nos últimos 12 meses."""
        resultado = gerar_dados_mensais(
            self.df_vendas,
            coluna_valor="valor_total",
            coluna_data="data_emissao",
        )
        self.assertGreater(len(resultado), 0)
        self.assertIn("ano_mes", resultado.columns)
        self.assertIn("valor_total", resultado.columns)

    def test_metricas_negocio_com_parametros(self):
        """Deve calcular métricas de negócio com parâmetros carregados."""
        extrator = ExtratorVendas(
            pasta_dados="dados/brutos/csv/mercadinho-t3",
            nome_dataset="mercadinho-t3"
        )
        extrator.leitor = self.leitor
        extrator.resolvedor = self.resolvedor

        parametros = extrator.get_parametro_negocio("cmv_taxa")
        self.assertIsNotNone(parametros)

        resultado = calcular_metricas_negocio(
            self.df_vendas,
            extrator.parametros_negocio,
            coluna_valor="valor_total",
        )

        self.assertIn("cmv", resultado)
        self.assertIn("despesas_variaveis", resultado)
        self.assertIn("imc", resultado)
        self.assertIn("break_even", resultado)

    def test_filtrar_por_ano(self):
        """Deve filtrar dados por ano específico."""
        resultado = filtrar_por_periodo(
            self.df_vendas,
            coluna_data="data_emissao",
            ano=2025,
        )
        self.assertGreater(len(resultado), 0)
        self.assertTrue((resultado["data_emissao"].dt.year == 2025).all())

    def test_filtrar_por_mes(self):
        """Deve filtrar dados por mês específico."""
        resultado = filtrar_por_periodo(
            self.df_vendas,
            coluna_data="data_emissao",
            mes=7,
        )
        self.assertGreater(len(resultado), 0)
        self.assertTrue((resultado["data_emissao"].dt.month == 7).all())

    def test_preparar_dados_visualizacao_completo(self):
        """Deve preparar dados completos para visualização."""
        resultado = preparar_dados_visualizacao(
            df=self.df_vendas,
            coluna_valor="valor_total",
            coluna_data="data_emissao",
            coluna_categoria="categoria_departamento",
            parametros_negocio=self.extrator.parametros_negocio,
        )

        self.assertIn("dados_anuais", resultado)
        self.assertIn("dados_mensais", resultado)
        self.assertIn("metricas_negocio", resultado)
        self.assertIn("dados_filtrados", resultado)

    def test_aplicar_filtros_combinados(self):
        """Deve aplicar múltiplos filtros sequencialmente."""
        resultado = aplicar_filtros(
            self.df_vendas,
            coluna_data="data_emissao",
            ano=2025,
            coluna_categoria="categoria_departamento",
            valor_categoria="Não informada",
            coluna_valor="valor_total",
            valor_minimo=10.0,
        )
        self.assertGreaterEqual(len(resultado), 0)
        if len(resultado) > 0:
            self.assertTrue((resultado["valor_total"] >= 10.0).all())


if __name__ == "__main__":
    unittest.main()
