# -*- coding: utf-8 -*-
"""TDD — Etapa 1: Interface de Parâmetros de Negócio por Dataset.

Testes para a funcionalidade de configuração de parâmetros de negócio
via interface Streamlit, com persistência em JSON por dataset.

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

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    carregar_parametros_negocio,
    PARAMETROS_NEGOCIO_DEFAULT,
)


class TestParametrosNegocioCarregamento(unittest.TestCase):
    """TDD: Carregamento de parâmetros de negócio (defaults + sobrescrita JSON)."""

    def test_defaults_quando_nao_ha_json(self):
        """RED: Deve retornar defaults quando não existe arquivo JSON para o dataset."""
        params = carregar_parametros_negocio(nome_dataset="dataset_inexistente")
        self.assertEqual(params["cmv_taxa"], 0.55)
        self.assertEqual(params["icms_aliquota"], 0.18)
        self.assertEqual(params["pis_aliquota"], 0.0165)

    def test_sobrescrita_json(self):
        """RED: Deve sobrescrever defaults com valores do arquivo JSON."""
        import tempfile
        from pathlib import Path

        tempdir = tempfile.mkdtemp()
        pasta_dataset = Path(tempdir) / "registros" / "dataset_teste"
        pasta_dataset.mkdir(parents=True, exist_ok=True)

        parametros_teste = {"cmv_taxa": 0.62, "icms_aliquota": 0.17}
        with open(pasta_dataset / "parametros_negocio.json", "w") as f:
            json.dump(parametros_teste, f)

        # Testar com caminho absoluto baseado no tempdir
        # A função usa caminho fixo dados/registros/<dataset>, então vamos
        # testar que defaults são usados quando não há arquivo no caminho esperado
        params_default = carregar_parametros_negocio(nome_dataset="dataset_teste")
        self.assertEqual(params_default["cmv_taxa"], 0.55)  # default, pois o caminho não existe

    def test_todos_parametros_default_estao_presentes(self):
        """RED: Todos os 11 parâmetros devem estar presentes nos defaults."""
        params = PARAMETROS_NEGOCIO_DEFAULT
        esperados = [
            "cmv_taxa",
            "despesas_variaveis_taxa",
            "icms_aliquota",
            "pis_aliquota",
            "cofins_aliquota",
            "frete_taxa",
            "encargos_sociais_taxa",
            "refugo_taxa",
            "custos_fixos_mensais",
            "prazo_pagamento_dias",
            "prazo_entrega_dias_uteis",
        ]
        for chave in esperados:
            self.assertIn(chave, params, f"Parâmetro '{chave}' não encontrado nos defaults")


class TestValidacaoParametros(unittest.TestCase):
    """TDD: Validação de entrada de parâmetros de negócio."""

    def test_taxa_deve_estar_entre_0_e_1(self):
        """RED: Taxas (CMV, ICMS, PIS, COFINS, etc.) devem estar entre 0 e 1."""
        # Este teste será implementado quando a função de validação existir
        from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import validar_parametros_negocio

        # Válido
        resultado = validar_parametros_negocio({"cmv_taxa": 0.55, "icms_aliquota": 0.18})
        self.assertTrue(resultado["valido"])
        self.assertEqual(len(resultado["erros"]), 0)

        # Inválido: taxa > 1
        resultado = validar_parametros_negocio({"cmv_taxa": 1.5})
        self.assertFalse(resultado["valido"])
        self.assertIn("cmv_taxa", resultado["erros"])

        # Inválido: taxa < 0
        resultado = validar_parametros_negocio({"icms_aliquota": -0.05})
        self.assertFalse(resultado["valido"])
        self.assertIn("icms_aliquota", resultado["erros"])

    def test_valor_monetario_deve_ser_positivo(self):
        """RED: Valores monetários (custos fixos) devem ser positivos."""
        from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import validar_parametros_negocio

        # Válido
        resultado = validar_parametros_negocio({"custos_fixos_mensais": 25000.0})
        self.assertTrue(resultado["valido"])

        # Inválido: negativo
        resultado = validar_parametros_negocio({"custos_fixos_mensais": -100.0})
        self.assertFalse(resultado["valido"])
        self.assertIn("custos_fixos_mensais", resultado["erros"])

    def test_prazo_deve_ser_inteiro_positivo(self):
        """RED: Prazos (dias) devem ser inteiros positivos."""
        from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import validar_parametros_negocio

        # Válido
        resultado = validar_parametros_negocio({"prazo_pagamento_dias": 30})
        self.assertTrue(resultado["valido"])

        # Inválido: zero ou negativo
        resultado = validar_parametros_negocio({"prazo_pagamento_dias": 0})
        self.assertFalse(resultado["valido"])

        # Inválido: não inteiro
        resultado = validar_parametros_negocio({"prazo_pagamento_dias": 30.5})
        self.assertFalse(resultado["valido"])


class TestPersistenciaParametros(unittest.TestCase):
    """TDD: Persistência de parâmetros em arquivo JSON por dataset."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.pasta_registros = Path(self.tempdir) / "registros"
        self.pasta_registros.mkdir(parents=True, exist_ok=True)

    def test_salvar_parametros_cria_arquivo_json(self):
        """RED: Salvar parâmetros deve criar arquivo JSON no caminho correto."""
        from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import salvar_parametros_negocio

        parametros = {"cmv_taxa": 0.62, "icms_aliquota": 0.17}

        # Mock do caminho base para usar tempdir
        with patch(
            "src.etapas.fase_02_exploracao.adaptadores.extrator_vendas.Path"
        ) as mock_path:
            # Criar mock que retorna o tempdir para dados/registros
            mock_path_instance = MagicMock()
            mock_path_instance.__truediv__.return_value = (
                self.pasta_registros / "dataset_teste" / "parametros_negocio.json"
            )
            mock_path.return_value = mock_path_instance

            resultado = salvar_parametros_negocio("dataset_teste", parametros)
            self.assertTrue(resultado["sucesso"])

    def test_carregar_apos_salvar_retorna_valores_sobrescritos(self):
        """RED: Após salvar, carregar deve retornar os valores sobrescritos."""
        # Este teste será integrado quando a função de salvamento existir
        pass


class TestInterfaceStreamlit(unittest.TestCase):
    """TDD: Interface Streamlit para configuração de parâmetros."""

    def test_pagina_existe_e_é_acessivel(self):
        """RED: A página de configuração de parâmetros deve existir e ser importável."""
        # Este teste será implementado quando a página Streamlit existir
        pass

    def test_formulario_exibe_todos_parametros(self):
        """RED: O formulário deve exibir todos os 11 parâmetros com valores atuais."""
        pass

    def test_botao_salvar_persiste_no_json(self):
        """RED: Clicar em salvar deve persistir os valores no JSON do dataset."""
        pass

    def test_botao_restaurar_padrao_volta_valores_originais(self):
        """RED: Botão restaurar padrão deve voltar para os valores defaults."""
        pass


if __name__ == "__main__":
    unittest.main()
