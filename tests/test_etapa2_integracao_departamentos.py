# -*- coding: utf-8 -*-
"""TDD — Etapa 2: Camada de Integração para Visão 360.

Testes para a classe IntegradorDepartamentos que une extratos de múltiplos
departamentos por chaves comuns descobertas dinamicamente.

Metodologia TDD:
1. Escrever teste (ver falhar - RED)
2. Implementar código mínimo (ver passar - GREEN)
3. Refatorar
4. Próximo teste
"""

import json
import os
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
)

# Importar a classe que vamos criar (não existe ainda - será o GREEN)
try:
    from src.etapas.fase_02_exploracao.adaptadores.integrador_departamentos import (
        IntegradorDepartamentos,
        descobrir_chaves_comuns,
        integrar_extratos_departamentos,
        gerar_relatorio_integridade,
    )
except ImportError:
    # Classes ainda não existem - esperado na fase RED
    IntegradorDepartamentos = None
    descobrir_chaves_comuns = None
    integrar_extratos_departamentos = None
    gerar_relatorio_integridade = None


class TestDescobrirChavesComuns(unittest.TestCase):
    """TDD: Descoberta automática de chaves comuns entre departamentos."""

    def test_descobrir_chave_idNFE_comum(self):
        """Deve descobrir idNFE como chave comum entre vendas e cobrança."""
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2, 3, 4, 5],
            "vNF": [100, 200, 300, 400, 500],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2, 3, 6, 7],
            "valor_pago": [100, 200, 300, 600, 700],
        })

        chaves = descobrir_chaves_comuns([df_vendas, df_cobranca])
        self.assertIn("idNFE", chaves)

    def test_descobrir_multiplas_chaves(self):
        """Deve descobrir múltiplas chaves comuns quando existirem."""
        df1 = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "idCliente": [10, 20, 30],
            "valor": [100, 200, 300],
        })
        df2 = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "idCliente": [10, 20, 30],
            "pago": [100, 200, 300],
        })

        chaves = descobrir_chaves_comuns([df1, df2])
        self.assertIn("idNFE", chaves)
        self.assertIn("idCliente", chaves)

    def test_nao_encontra_chave_comum(self):
        """Deve retornar lista vazia quando não há chaves comuns."""
        df1 = pd.DataFrame({
            "idVenda": [1, 2, 3],
            "valor": [100, 200, 300],
        })
        df2 = pd.DataFrame({
            "idProduto": [10, 20, 30],
            "estoque": [5, 10, 15],
        })

        chaves = descobrir_chaves_comuns([df1, df2])
        self.assertEqual(len(chaves), 0)

    def test_dataframe_vazio(self):
        """Deve lidar com DataFrame vazio sem erro."""
        df1 = pd.DataFrame({"idNFE": [], "valor": []})
        df2 = pd.DataFrame({"idNFE": [], "pago": []})

        chaves = descobrir_chaves_comuns([df1, df2])
        self.assertEqual(len(chaves), 0)


class TestIntegrarExtratos(unittest.TestCase):
    """TDD: Integração de extratos de departamentos."""

    def test_integrar_dois_departamentos(self):
        """Deve integrar dois departamentos pela chave comum idNFE."""
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vNF": [100, 200, 300],
            "data": ["2026-01-01", "2026-01-02", "2026-01-03"],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "valor_pago": [100, 200, 300],
            "status": ["pago", "pago", "pendente"],
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": df_vendas, "cobranca": df_cobranca},
            chave_comum="idNFE",
        )

        self.assertIsInstance(resultado, pd.DataFrame)
        self.assertEqual(len(resultado), 3)
        self.assertIn("vendas_vNF", resultado.columns)
        self.assertIn("cobranca_valor_pago", resultado.columns)
        self.assertIn("cobranca_status", resultado.columns)

    def test_integrar_tres_departamentos(self):
        """Deve integrar três departamentos pela chave comum."""
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2],
            "vNF": [100, 200],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2],
            "valor_pago": [100, 200],
        })
        df_estoque = pd.DataFrame({
            "idNFE": [1, 2],
            "estoque": [5, 10],
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": df_vendas, "cobranca": df_cobranca, "estoque": df_estoque},
            chave_comum="idNFE",
        )

        self.assertEqual(len(resultado), 2)
        self.assertIn("vendas_vNF", resultado.columns)
        self.assertIn("cobranca_valor_pago", resultado.columns)
        self.assertIn("estoque_estoque", resultado.columns)

    def test_join_esquerdo_mantem_registros_sem_chave(self):
        """Deve manter registros do departamento principal mesmo sem chave em outros."""
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vNF": [100, 200, 300],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2],
            "valor_pago": [100, 200],
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": df_vendas, "cobranca": df_cobranca},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        self.assertEqual(len(resultado), 3)
        # idNFE=3 deve estar presente com valor_pago NaN
        linha_3 = resultado[resultado["idNFE"] == 3]
        self.assertEqual(len(linha_3), 1)
        self.assertTrue(pd.isna(linha_3["cobranca_valor_pago"].iloc[0]))

    def test_aplica_recortes_temporais_apos_integracao(self):
        """Deve aplicar recortes temporais (5 anos + 12 meses) após integração."""
        datas = pd.date_range("2021-01-01", "2026-06-30", freq="D")
        df_vendas = pd.DataFrame({
            "idNFE": range(len(datas)),
            "vNF": [100.0] * len(datas),
            "data_emissao": datas,
        })
        df_cobranca = pd.DataFrame({
            "idNFE": range(len(datas)),
            "valor_pago": [100.0] * len(datas),
            "data_emissao": datas,
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": df_vendas, "cobranca": df_cobranca},
            chave_comum="idNFE",
            coluna_data="data_emissao",
            aplicar_recortes=True,
        )

        self.assertIn("ano", resultado.columns)
        self.assertIn("ano_mes", resultado.columns)
        self.assertIn("recortes_temporais", resultado.attrs)


class TestGerarRelatorioIntegridade(unittest.TestCase):
    """TDD: Relatório de integridade da integração."""

    def test_relatorio_integridade(self):
        """Deve gerar relatório com contagem de registros integrados e perdidos."""
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2, 3, 4, 5],
            "vNF": [100, 200, 300, 400, 500],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "valor_pago": [100, 200, 300],
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": df_vendas, "cobranca": df_cobranca},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        relatorio = gerar_relatorio_integridade(
            resultado, {"vendas": df_vendas, "cobranca": df_cobranca}, "idNFE"
        )

        self.assertIn("registros_principal", relatorio)
        self.assertIn("registros_integrados", relatorio)
        self.assertIn("registros_perdidos", relatorio)
        self.assertIn("taxa_integracao", relatorio)
        self.assertEqual(relatorio["registros_principal"], 5)
        self.assertEqual(relatorio["registros_integrados"], 3)


class TestIntegradorDepartamentosClasse(unittest.TestCase):
    """TDD: Classe IntegradorDepartamentos."""

    def test_instanciar_classe(self):
        """Deve instanciar IntegradorDepartamentos com parâmetros opcionais."""
        if IntegradorDepartamentos is None:
            self.skipTest("Classe IntegradorDepartamentos não implementada ainda")

        integrador = IntegradorDepartamentos()
        self.assertIsNotNone(integrador)

    def test_integrar_metodo_instancia(self):
        """Deve integrar extratos através do método da instância."""
        if IntegradorDepartamentos is None:
            self.skipTest("Classe IntegradorDepartamentos não implementada ainda")

        integrador = IntegradorDepartamentos()
        df_vendas = pd.DataFrame({
            "idNFE": [1, 2],
            "vNF": [100, 200],
        })
        df_cobranca = pd.DataFrame({
            "idNFE": [1, 2],
            "valor_pago": [100, 200],
        })

        resultado = integrador.integrar(
            {"vendas": df_vendas, "cobranca": df_cobranca},
            chave_comum="idNFE",
        )
        self.assertEqual(len(resultado), 2)


if __name__ == "__main__":
    unittest.main()
