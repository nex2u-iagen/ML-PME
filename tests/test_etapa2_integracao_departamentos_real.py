# -*- coding: utf-8 -*-
"""Teste de integração para IntegradorDepartamentos com dados reais do mercadinho-t3.

Valida a integração de múltiplos departamentos por chaves comuns, incluindo:
- Descoberta automática de chaves comuns (idNFE)
- Join esquerdo mantendo registros do departamento principal
- Recortes temporais (5 anos + 12 meses) após integração
- Relatório de integridade
"""

import unittest
from pathlib import Path

import pandas as pd

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import ExtratorVendas
from src.etapas.fase_02_exploracao.adaptadores.integrador_departamentos import (
    IntegradorDepartamentos,
    descobrir_chaves_comuns,
    integrar_extratos_departamentos,
    gerar_relatorio_integridade,
)
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


class TestIntegradorDepartamentosIntegracao(unittest.TestCase):
    """Teste de integração com dados reais do mercadinho-t3."""

    @classmethod
    def setUpClass(cls):
        cls.resolvedor = ResolvedorSemantico()
        cls.leitor = LeitorArquivosTabulares()

        # Carregar extratos de vendas e contas a receber (ambas têm idNFE e datas)
        extrator_vendas = ExtratorVendas(
            pasta_dados="dados/brutos/csv/mercadinho-t3",
            nome_dataset="mercadinho-t3"
        )
        extrator_vendas.leitor = cls.leitor
        extrator_vendas.resolvedor = cls.resolvedor

        # Carregar vendas diretamente (não pelo extrator, pois ele filtra por 12 meses)
        cls.df_vendas = cls.leitor.carregar_tabela(
            Path("dados/brutos/csv/mercadinho-t3/erp_nfetotal.csv")
        )
        cls.df_nfecob = cls.leitor.carregar_tabela(
            Path("dados/brutos/csv/mercadinho-t3/erp_nfecob.csv")
        )

        # Selecionar colunas relevantes para simular extratos de departamento
        cls.extrato_vendas = cls.df_vendas[["idNFE", "vNF"]].copy()
        cls.extrato_vendas.columns = ["idNFE", "valor_venda"]

        cls.extrato_cobranca = cls.df_nfecob[["idNFE", "dVenc", "vDup"]].copy()
        cls.extrato_cobranca.columns = ["idNFE", "data_vencimento", "valor_cobranca"]

    def test_integrador_descobre_chave_comum_idNFE(self):
        """Deve descobrir idNFE como chave comum entre vendas e cobrança."""
        chaves = descobrir_chaves_comuns([self.extrato_vendas, self.extrato_cobranca])
        self.assertIn("idNFE", chaves)

    def test_integrador_integra_vendas_e_cobranca(self):
        """Deve integrar vendas e cobrança por idNFE."""
        resultado = integrar_extratos_departamentos(
            {"vendas": self.extrato_vendas, "cobranca": self.extrato_cobranca},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        self.assertGreater(len(resultado), 0)
        self.assertIn("vendas_valor_venda", resultado.columns)
        self.assertIn("cobranca_data_vencimento", resultado.columns)
        self.assertIn("cobranca_valor_cobranca", resultado.columns)
        self.assertIn("idNFE", resultado.columns)

    def test_integrador_aplica_recortes_temporais(self):
        """Deve aplicar recortes temporais quando coluna de dados está disponível."""
        # Usar subconjunto menor para teste de recorte temporal
        vendas_subset = self.extrato_vendas.head(500).copy()
        vendas_subset["data_emissao"] = pd.date_range(
            "2022-01-01", periods=len(vendas_subset), freq="D"
        )
        cobranca_subset = self.extrato_cobranca.head(500).copy()

        resultado = integrar_extratos_departamentos(
            {"vendas": vendas_subset, "cobranca": cobranca_subset},
            chave_comum="idNFE",
            departamento_principal="vendas",
            coluna_data="data_emissao",
            aplicar_recortes=True,
        )

        self.assertIn("ano", resultado.columns)
        self.assertIn("ano_mes", resultado.columns)
        recortes = resultado.attrs.get("recortes_temporais", {})
        self.assertIn("anos_disponiveis", recortes)
        self.assertIn("meses_disponiveis", recortes)
        self.assertGreaterEqual(len(recortes["anos_disponiveis"]), 1)
        self.assertGreaterEqual(len(recortes["meses_disponiveis"]), 1)

    def test_integrador_relatorio_integridade(self):
        """Deve gerar relatório de integridade com métricas corretas."""
        resultado = integrar_extratos_departamentos(
            {"vendas": self.extrato_vendas, "cobranca": self.extrato_cobranca},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        relatorio = gerar_relatorio_integridade(
            resultado,
            {"vendas": self.extrato_vendas, "cobranca": self.extrato_cobranca},
            "idNFE",
        )

        self.assertIn("registros_principal", relatorio)
        self.assertIn("registros_integrados", relatorio)
        self.assertIn("registros_perdidos", relatorio)
        self.assertIn("taxa_integracao", relatorio)
        self.assertEqual(relatorio["registros_principal"], len(self.extrato_vendas))

    def test_integrador_classe_metodo_instancia(self):
        """Deve integrar através do método da instância IntegradorDepartamentos."""
        integrador = IntegradorDepartamentos()
        resultado = integrador.integrar(
            {"vendas": self.extrato_vendas, "cobranca": self.extrato_cobranca},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        self.assertGreater(len(resultado), 0)
        self.assertIsNotNone(integrador.obter_relatorio_integridade())
        self.assertIsNotNone(integrador.obter_resultado())

    def test_integrador_departamento_principal_sem_chave(self):
        """Deve manter todos os registros do departamento principal mesmo sem chave em outros."""
        vendas_sem_correspondencia = pd.DataFrame({
            "idNFE": [9991, 9992, 9993],
            "valor": [100, 200, 300],
        })
        cobranca_poucas = pd.DataFrame({
            "idNFE": [1, 2],
            "valor_pago": [100, 200],
        })

        resultado = integrar_extratos_departamentos(
            {"vendas": vendas_sem_correspondencia, "cobranca": cobranca_poucas},
            chave_comum="idNFE",
            departamento_principal="vendas",
        )

        self.assertEqual(len(resultado), 3)
        # Nenhum deve ter correspondência em cobrança
        colunas_cobranca = [c for c in resultado.columns if c.startswith("cobranca_")]
        if colunas_cobranca:
            self.assertTrue(resultado[colunas_cobranca].isna().all().all())


if __name__ == "__main__":
    unittest.main()
