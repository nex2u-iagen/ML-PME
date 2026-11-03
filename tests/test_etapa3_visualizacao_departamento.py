# -*- coding: utf-8 -*-
"""TDD — Etapa 3: Páginas de Visualização por Departamento.

Testes para visualizações por departamento com gráficos ano-a-ano (5 anos)
e mês-a-mês (12 meses), métricas de negócio e filtros.

Metodologia TDD:
1. Escrever teste (ver falhar - RED)
2. Implementar código mínimo (ver passar - GREEN)
3. Refatorar
4. Próximo teste
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    carregar_parametros_negocio,
    PARAMETROS_NEGOCIO_DEFAULT,
)

# Tentar importar a página de visualização (não existe ainda - fase RED)
try:
    from app_pages.pagina_visualizacao_departamento import (
        calcular_metricas_negocio,
        filtrar_por_periodo,
        filtrar_por_categoria,
        filtrar_por_valor,
        gerar_dados_anuais,
        gerar_dados_mensais,
        preparar_dados_visualizacao,
    )
except ImportError:
    calcular_metricas_negocio = None
    filtrar_por_periodo = None
    filtrar_por_categoria = None
    filtrar_por_valor = None
    gerar_dados_anuais = None
    gerar_dados_mensais = None
    preparar_dados_visualizacao = None


class TestGerarDadosAnuais(unittest.TestCase):
    """TDD: Geração de dados anuais (últimos 5 anos)."""

    def test_gerar_dados_anuais_5_anos(self):
        """Deve agregar dados por ano nos últimos 5 anos."""
        datas = pd.date_range("2021-01-01", "2026-06-30", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
        })

        resultado = gerar_dados_anuais(df, coluna_valor="valor_total", coluna_data="data_emissao")

        self.assertIsInstance(resultado, pd.DataFrame)
        self.assertIn("ano", resultado.columns)
        self.assertIn("valor_total", resultado.columns)
        # Deve ter 5 anos (2022-2026)
        anos = sorted(resultado["ano"].unique())
        self.assertEqual(len(anos), 5)
        self.assertEqual(anos[0], 2022)
        self.assertEqual(anos[-1], 2026)

    def test_dataframe_vazio(self):
        """Deve lidar com DataFrame vazio."""
        df = pd.DataFrame({"id_pedido": [], "data_emissao": [], "valor_total": []})
        resultado = gerar_dados_anuais(df, coluna_valor="valor_total", coluna_data="data_emissao")
        self.assertEqual(len(resultado), 0)


class TestGerarDadosMensais(unittest.TestCase):
    """TDD: Geração de dados mensais (últimos 12 meses)."""

    def test_gerar_dados_mensais_12_meses(self):
        """Deve agregar dados por mês nos últimos 12 meses."""
        datas = pd.date_range("2025-07-01", "2026-06-30", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
        })

        resultado = gerar_dados_mensais(df, coluna_valor="valor_total", coluna_data="data_emissao")

        self.assertIsInstance(resultado, pd.DataFrame)
        self.assertIn("ano_mes", resultado.columns)
        self.assertIn("valor_total", resultado.columns)
        # Deve ter 12 meses
        meses = sorted(resultado["ano_mes"].unique())
        self.assertEqual(len(meses), 12)


class TestCalcularMetricasNegocio(unittest.TestCase):
    """TDD: Cálculo de métricas de negócio com parâmetros configuráveis."""

    def test_calcular_cmv(self):
        """Deve calcular CMV baseado na taxa configurada."""
        df = pd.DataFrame({"valor_total": [1000.0, 2000.0, 3000.0]})
        parametros = {"cmv_taxa": 0.55}

        resultado = calcular_metricas_negocio(df, parametros)

        self.assertIn("cmv", resultado)
        self.assertAlmostEqual(resultado["cmv"], 3300.0)  # 6000 * 0.55

    def test_calcular_despesas_variaveis(self):
        """Deve calcular despesas variáveis baseado na taxa configurada."""
        df = pd.DataFrame({"valor_total": [1000.0, 2000.0]})
        parametros = {"despesas_variaveis_taxa": 0.12}

        resultado = calcular_metricas_negocio(df, parametros)

        self.assertIn("despesas_variaveis", resultado)
        self.assertAlmostEqual(resultado["despesas_variaveis"], 360.0)  # 3000 * 0.12

    def test_calcular_imc(self):
        """Deve calcular Índice de Margem de Contribuição."""
        df = pd.DataFrame({"valor_total": [10000.0]})
        parametros = {
            "cmv_taxa": 0.55,
            "despesas_variaveis_taxa": 0.12,
        }

        resultado = calcular_metricas_negocio(df, parametros)

        self.assertIn("imc", resultado)
        # IMC = (Receita - CMV - Despesas) / Receita
        # = (10000 - 5500 - 1200) / 10000 = 3300 / 10000 = 0.33
        self.assertAlmostEqual(resultado["imc"], 0.33, places=2)

    def test_calcular_break_even(self):
        """Deve calcular ponto de equilíbrio."""
        df = pd.DataFrame({"valor_total": [100000.0]})
        parametros = {
            "cmv_taxa": 0.55,
            "despesas_variaveis_taxa": 0.12,
            "custos_fixos_mensais": 25000.0,
        }

        resultado = calcular_metricas_negocio(df, parametros)

        self.assertIn("break_even", resultado)
        # Break-Even = custos fixos / margem fracionária
        # margem fracionária = 1 - 0.55 - 0.12 = 0.33
        # Break-Even = 25000 / 0.33 = 75757.58
        self.assertAlmostEqual(resultado["break_even"], 75757.58, places=2)

    def test_parametros_vazios_retorna_vazio(self):
        """Deve retornar dicionário vazio quando não há parâmetros."""
        df = pd.DataFrame({"valor_total": [100.0]})
        resultado = calcular_metricas_negocio(df, {})
        self.assertEqual(resultado, {})


class TestFiltrarPorPeriodo(unittest.TestCase):
    """TDD: Filtros por período."""

    def test_filtrar_por_ano(self):
        """Deve filtrar dados por ano específico."""
        datas = pd.date_range("2022-01-01", "2026-12-31", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
        })

        resultado = filtrar_por_periodo(df, coluna_data="data_emissao", ano=2024)
        self.assertEqual(len(resultado), 366)  # 2024 é bissexto
        self.assertTrue((resultado["data_emissao"].dt.year == 2024).all())

    def test_filtrar_por_mes(self):
        """Deve filtrar dados por mês específico."""
        datas = pd.date_range("2026-01-01", "2026-12-31", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
        })

        resultado = filtrar_por_periodo(df, coluna_data="data_emissao", mes=3)
        self.assertEqual(len(resultado), 31)  # Março tem 31 dias
        self.assertTrue((resultado["data_emissao"].dt.month == 3).all())

    def test_filtrar_por_ano_e_mes(self):
        """Deve filtrar por ano e mês simultaneamente."""
        datas = pd.date_range("2026-01-01", "2026-12-31", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
        })

        resultado = filtrar_por_periodo(df, coluna_data="data_emissao", ano=2026, mes=7)
        self.assertEqual(len(resultado), 31)  # Julho tem 31 dias


class TestFiltrarPorCategoria(unittest.TestCase):
    """TDD: Filtros por categoria."""

    def test_filtrar_por_categoria(self):
        """Deve filtrar dados por categoria específica."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3, 4, 5],
            "categoria": ["Mercearia", "Açougue", "Mercearia", "Padaria", "Mercearia"],
            "valor_total": [100, 200, 150, 300, 250],
        })

        resultado = filtrar_por_categoria(df, coluna_categoria="categoria", valor_categoria="Mercearia")
        self.assertEqual(len(resultado), 3)
        self.assertTrue((resultado["categoria"] == "Mercearia").all())


class TestFiltrarPorValor(unittest.TestCase):
    """TDD: Filtros por valor."""

    def test_filtrar_por_valor_minimo(self):
        """Deve filtrar dados por valor mínimo."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3, 4, 5],
            "valor_total": [50.0, 150.0, 300.0, 500.0, 1000.0],
        })

        resultado = filtrar_por_valor(df, coluna_valor="valor_total", valor_minimo=200.0)
        self.assertEqual(len(resultado), 3)
        self.assertTrue((resultado["valor_total"] >= 200.0).all())

    def test_filtrar_por_valor_maximo(self):
        """Deve filtrar dados por valor máximo."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3, 4, 5],
            "valor_total": [50.0, 150.0, 300.0, 500.0, 1000.0],
        })

        resultado = filtrar_por_valor(df, coluna_valor="valor_total", valor_maximo=300.0)
        self.assertEqual(len(resultado), 3)
        self.assertTrue((resultado["valor_total"] <= 300.0).all())


class TestPrepararDadosVisualizacao(unittest.TestCase):
    """TDD: Preparação completa de dados para visualização."""

    def test_preparar_dados_completos(self):
        """Deve preparar dados com todas as informações necessárias."""
        datas = pd.date_range("2025-07-01", "2026-06-30", freq="D")
        df = pd.DataFrame({
            "id_pedido": range(len(datas)),
            "data_emissao": datas,
            "valor_total": [100.0] * len(datas),
            "categoria": ["Mercearia"] * len(datas),
        })
        parametros = {"cmv_taxa": 0.55, "despesas_variaveis_taxa": 0.12}

        resultado = preparar_dados_visualizacao(
            df=df,
            coluna_valor="valor_total",
            coluna_data="data_emissao",
            coluna_categoria="categoria",
            parametros_negocio=parametros,
        )

        self.assertIn("dados_anuais", resultado)
        self.assertIn("dados_mensais", resultado)
        self.assertIn("metricas_negocio", resultado)
        self.assertIn("dados_filtrados", resultado)


if __name__ == "__main__":
    unittest.main()
