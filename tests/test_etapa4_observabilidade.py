# -*- coding: utf-8 -*-
"""TDD — Etapa 4: Observabilidade e Qualidade de Dados.

Testes para o módulo de observabilidade que calcula métricas de qualidade,
alertas e logs estruturados para extração e integração de dados.

Metodologia TDD:
1. Escrever teste (ver falhar - RED)
2. Implementar código mínimo (ver passar - GREEN)
3. Refatorar
4. Próximo teste
"""

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Tentar importar o módulo de observabilidade (não existe ainda - fase RED)
try:
    from src.etapas.fase_02_exploracao.adaptadores.observabilidade import (
        Observabilidade,
        calcular_taxa_sucesso_data,
        calcular_taxa_integracao,
        gerar_alerta_qualidade,
        logger_estruturado,
    )
except ImportError:
    Observabilidade = None
    calcular_taxa_sucesso_data = None
    calcular_taxa_integracao = None
    gerar_alerta_qualidade = None
    logger_estruturado = None


class TestCalcularTaxaSucessoData(unittest.TestCase):
    """TDD: Cálculo de taxa de sucesso de extração de data."""

    def test_taxa_sucesso_100(self):
        """Deve retornar 100% quando todas as datas são válidas."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3],
            "data_emissao": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        })
        resultado = calcular_taxa_sucesso_data(df, coluna_data="data_emissao")
        self.assertAlmostEqual(resultado, 100.0)

    def test_taxa_sucesso_50(self):
        """Deve retornar 50% quando metade das datas são válidas."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3, 4],
            "data_emissao": pd.to_datetime(["2026-01-01", None, "2026-01-03", None]),
        })
        resultado = calcular_taxa_sucesso_data(df, coluna_data="data_emissao")
        self.assertAlmostEqual(resultado, 50.0)

    def test_taxa_sucesso_0(self):
        """Deve retornar 0% quando não há datas válidas."""
        df = pd.DataFrame({
            "id_pedido": [1, 2, 3],
            "data_emissao": [None, None, None],
        })
        resultado = calcular_taxa_sucesso_data(df, coluna_data="data_emissao")
        self.assertAlmostEqual(resultado, 0.0)

    def test_dataframe_vazio(self):
        """Deve retornar 0.0 para DataFrame vazio."""
        df = pd.DataFrame({"id_pedido": [], "data_emissao": []})
        resultado = calcular_taxa_sucesso_data(df, coluna_data="data_emissao")
        self.assertAlmostEqual(resultado, 0.0)

    def test_coluna_inexistente(self):
        """Deve retornar 0.0 quando a coluna de data não existe."""
        df = pd.DataFrame({"id_pedido": [1, 2, 3], "valor": [100, 200, 300]})
        resultado = calcular_taxa_sucesso_data(df, coluna_data="data_inexistente")
        self.assertAlmostEqual(resultado, 0.0)


class TestCalcularTaxaIntegracao(unittest.TestCase):
    """TDD: Cálculo de taxa de integração entre departamentos."""

    def test_taxa_integracao_100(self):
        """Deve retornar 100% quando todos os registros têm correspondência."""
        df_integrado = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vendas_vNF": [100, 200, 300],
            "cobranca_valor_pago": [100, 200, 300],
        })
        extratos = {
            "vendas": pd.DataFrame({"idNFE": [1, 2, 3], "vNF": [100, 200, 300]}),
            "cobranca": pd.DataFrame({"idNFE": [1, 2, 3], "valor_pago": [100, 200, 300]}),
        }
        resultado = calcular_taxa_integracao(
            df_integrado, extratos, chave_comum="idNFE", departamento_principal="vendas"
        )
        self.assertAlmostEqual(resultado, 100.0)

    def test_taxa_integracao_66_67(self):
        """Deve retornar ~66.67% quando 2 de 3 registros têm correspondência."""
        df_integrado = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vendas_vNF": [100, 200, 300],
            "cobranca_valor_pago": [100, 200, None],
        })
        extratos = {
            "vendas": pd.DataFrame({"idNFE": [1, 2, 3], "vNF": [100, 200, 300]}),
            "cobranca": pd.DataFrame({"idNFE": [1, 2, 3], "valor_pago": [100, 200, 300]}),
        }
        resultado = calcular_taxa_integracao(
            df_integrado, extratos, chave_comum="idNFE", departamento_principal="vendas"
        )
        self.assertAlmostEqual(resultado, 66.67, places=2)

    def test_taxa_integracao_0(self):
        """Deve retornar 0% quando nenhum registro tem correspondência."""
        df_integrado = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vendas_vNF": [100, 200, 300],
            "cobranca_valor_pago": [None, None, None],
        })
        extratos = {
            "vendas": pd.DataFrame({"idNFE": [1, 2, 3], "vNF": [100, 200, 300]}),
            "cobranca": pd.DataFrame({"idNFE": [1, 2, 3], "valor_pago": [100, 200, 300]}),
        }
        resultado = calcular_taxa_integracao(
            df_integrado, extratos, chave_comum="idNFE", departamento_principal="vendas"
        )
        self.assertAlmostEqual(resultado, 0.0)


class TestGerarAlertaQualidade(unittest.TestCase):
    """TDD: Geração de alertas de qualidade de dados."""

    def test_alerta_quando_taxa_abaixo_limiar(self):
        """Deve gerar alerta quando taxa está abaixo do limiar."""
        resultado = gerar_alerta_qualidade(
            taxa_sucesso_data=45.0,
            limiar=50.0,
            nome_dataset="mercadinho-t3",
        )
        self.assertTrue(resultado["alerta_ativo"])
        self.assertEqual(resultado["nivel"], "alto")
        self.assertIn("mercadinho-t3", resultado["mensagem"])

    def test_sem_alerta_quando_taxa_acima_limiar(self):
        """Deve não gerar alerta quando taxa está acima do limiar."""
        resultado = gerar_alerta_qualidade(
            taxa_sucesso_data=80.0,
            limiar=50.0,
            nome_dataset="mercadinho-t3",
        )
        self.assertFalse(resultado["alerta_ativo"])
        self.assertEqual(resultado["nivel"], "baixo")

    def test_alerta_nivel_medio(self):
        """Deve gerar alerta nível médio quando taxa está entre 50% e 70%."""
        resultado = gerar_alerta_qualidade(
            taxa_sucesso_data=65.0,
            limiar=50.0,
            nome_dataset="teste",
        )
        self.assertTrue(resultado["alerta_ativo"])
        self.assertEqual(resultado["nivel"], "medio")

    def test_limiar_configuravel(self):
        """Deve usar limiar personalizado quando fornecido."""
        # Taxa bem acima do limiar + 20 → sem alerta
        resultado = gerar_alerta_qualidade(
            taxa_sucesso_data=60.0,
            limiar=30.0,
            nome_dataset="teste",
        )
        self.assertFalse(resultado["alerta_ativo"])
        self.assertEqual(resultado["nivel"], "baixo")
        self.assertEqual(resultado["limiar"], 30.0)


class TestLoggerEstruturado(unittest.TestCase):
    """TDD: Logs estruturados para auditoria."""

    def test_log_estruturado_contem_campos_obrigatorios(self):
        """Deve gerar log com timestamp, nível, mensagem e dados."""
        resultado = logger_estruturado(
            nivel="INFO",
            mensagem="Extração concluída",
            dados={"dataset": "mercadinho-t3", "registros": 1000},
        )
        self.assertIn("timestamp", resultado)
        self.assertIn("nivel", resultado)
        self.assertIn("mensagem", resultado)
        self.assertIn("dados", resultado)
        self.assertEqual(resultado["nivel"], "INFO")
        self.assertEqual(resultado["mensagem"], "Extração concluída")
        self.assertEqual(resultado["dados"]["dataset"], "mercadinho-t3")

    def test_log_estruturado_eh_json_valido(self):
        """Deve gerar log que pode ser serializado para JSON."""
        resultado = logger_estruturado(
            nivel="WARNING",
            mensagem="Taxa de sucesso baixa",
            dados={"taxa": 45.0, "limiar": 50.0},
        )
        json_str = json.dumps(resultado, default=str)
        self.assertIsInstance(json_str, str)
        # Deve ser possível deserializar
        json.loads(json_str)


class TestClasseObservabilidade(unittest.TestCase):
    """TDD: Classe Observabilidade."""

    def test_instanciar_classe(self):
        """Deve instanciar Observabilidade com parâmetros opcionais."""
        if Observabilidade is None:
            self.skipTest("Classe Observabilidade não implementada ainda")

        obs = Observabilidade()
        self.assertIsNotNone(obs)

    def test_calcular_metricas_completas(self):
        """Deve calcular todas as métricas de qualidade."""
        if Observabilidade is None:
            self.skipTest("Classe Observabilidade não implementada ainda")

        obs = Observabilidade()

        df_integrado = pd.DataFrame({
            "idNFE": [1, 2, 3],
            "vendas_vNF": [100, 200, 300],
            "cobranca_valor_pago": [100, 200, None],
        })
        extratos = {
            "vendas": pd.DataFrame({"idNFE": [1, 2, 3], "vNF": [100, 200, 300]}),
            "cobranca": pd.DataFrame({"idNFE": [1, 2, 3], "valor_pago": [100, 200, 300]}),
        }

        metricas = obs.calcular_metricas(
            df_integrado=df_integrado,
            extratos=extratos,
            chave_comum="idNFE",
            departamento_principal="vendas",
            coluna_data="vendas_data_emissao",
        )

        self.assertIn("taxa_sucesso_data", metricas)
        self.assertIn("taxa_integracao", metricas)
        self.assertIn("alerta", metricas)
        self.assertIn("timestamp", metricas)


if __name__ == "__main__":
    unittest.main()
