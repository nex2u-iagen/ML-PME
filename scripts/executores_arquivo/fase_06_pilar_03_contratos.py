"""Script Executável de Homologação e Teste do Pilar 3 da Fase 6 (Contratos de Dados).

Responsabilidade Única: Submeter os esquemas Pydantic V2 a uma bateria de validação
técnica:
1. Validação de dados clínicos perfeitos e exportação ordenada do vetor para o
Scikit-Learn.
2. Teste de rejeição imediata de limites biológicos violados (ex: idade = 150 anos).
3. Teste de rejeição por omissão de campos obrigatórios (ausência de atributo preditor).
4. Teste de conformidade do esquema de saída e serialização em formato JSON.
"""

# 'import logging' gere os registos estruturados de auditoria no terminal.
import logging

# 'from pydantic import ValidationError' permite capturar formalmente violações de
# contrato do Pydantic.
from pydantic import ValidationError

from scripts.bootstrap import configurar_ambiente

# Importa o contrato das 10 variáveis preditoras do paciente construído no Pilar 3.
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_paciente import (  # noqa: E501
    EsquemaEntradaPaciente,
)

# Importa o contrato da resposta oficial de inferência construído no Pilar 3.
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_resposta_predicao import (  # noqa: E501
    EsquemaRespostaPredicao,
)

# Configura o layout das mensagens de log no console com indicação de tempo e
# severidade.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info(
        "=== INICIANDO HOMOLOGAÇÃO DO PILAR 3: CONTRATOS DE DADOS PYDANTIC V2 (FASE 6)"
        "===\n"
    )

    # ----------------------------------------------------------------------------------
    # TESTE 1: ENTRADA CLÍNICA VÁLIDA E VETORIZAÇÃO ORDENADA PARA O SCIKIT-LEARN
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 1: Instanciação de paciente conforme e exportação de vetor..."
    )

    # Criação de um payload em conformidade com as restrições biológicas.
    dados_paciente_legitimo = {
        "idade_paciente": 62,
        "pressao_sistolica": 160.0,
        "colesterol_total": 240.0,
        "frequencia_cardiaca": 82.0,
        "glicemia_jejum": 130.0,
        "indice_massa_corporal": 31.5,
        "infradesnivel_st": 2.1,
        "historico_familiar": 1,
        "nivel_sedentarismo": 3,
        "tempo_internacao_previo": 5.0,
    }

    # Validação via construtor do modelo Pydantic.
    paciente_validado = EsquemaEntradaPaciente(**dados_paciente_legitimo)

    # Extrai o vetor numérico contínuo para aferição da ordem canónica.
    vetor_ordenado = paciente_validado.exportar_vetor_ordenado()

    # Confere se o vetor exportou exatamente 10 atributos de ponto flutuante.
    assert len(vetor_ordenado) == 10, (
        "Falha Crítica: O vetor gerado não contém exatamente 10 atributos!"
    )
    assert vetor_ordenado[0] == 62.0, (
        "Falha de Posição: A primeira feature deve ser 'Idade_Paciente'!"
    )
    assert vetor_ordenado[7] == 1.0, (
        "Falha de Posição: A oitava feature deve ser 'Historico_Familiar'!"
    )

    logging.info(
        "Teste 1 Aprovado: Contrato validado e vetor de 10 atributos exportado com"
        "sucesso."
    )

    # ----------------------------------------------------------------------------------
    # TESTE 2: REJEIÇÃO DEFENSIVA DE LIMITES BIOLÓGICOS (IDADE = 150 ANOS)
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 2: Auditoria de limites biológicos com idade impossível (150"
        "anos)..."
    )

    dados_paciente_invalido = dados_paciente_legitimo.copy()
    dados_paciente_invalido["idade_paciente"] = 150  # Violação da regra 'le=110'

    try:
        EsquemaEntradaPaciente(**dados_paciente_invalido)
        assert False, (
            "Falha de Segurança: O Pydantic permitiu uma idade superior ao teto de 110"
            "anos!"
        )
    except ValidationError as erro_validacao:
        logging.info(
            "Teste 2 Aprovado: Violação intercetada com sucesso. Erro formal: %s",
            erro_validacao.errors()[0]["msg"],
        )

    # ----------------------------------------------------------------------------------
    # TESTE 3: REJEIÇÃO POR OMISSÃO DE CAMPO OBRIGATÓRIO (FALTA DE COLESTEROL)
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 3: Auditoria contra omissão de exames clínicos no payload..."
    )

    dados_paciente_incompleto = dados_paciente_legitimo.copy()
    del dados_paciente_incompleto["colesterol_total"]  # Remove um atributo obrigatório

    try:
        EsquemaEntradaPaciente(**dados_paciente_incompleto)
        assert False, (
            "Falha de Segurança: O Pydantic aceitou um payload com atributo ausente!"
        )
    except ValidationError as erro_omissao:
        logging.info(
            "Teste 3 Aprovado: Omissão intercetada. Campo ausente exigido: '%s'",
            erro_omissao.errors()[0]["loc"][0],
        )

    # ----------------------------------------------------------------------------------
    # TESTE 4: CONFORMIDADE E SERIALIZAÇÃO DO ESQUEMA DE RESPOSTA
    # ----------------------------------------------------------------------------------
    logging.info(
        "Executando Teste 4: Emissão e validação do esquema de resposta preditiva..."
    )

    resposta_producao = EsquemaRespostaPredicao(
        classe_predita=1,
        diagnostico_rotulo="ALTO_RISCO_CARDIOVASCULAR",
        probabilidade_risco=0.8845,
        limiar_decisao_aplicado=0.50,
        grau_severidade="CRÍTICO",
        versao_modelo_producao="SVM_Calibrado_Producao_v1.0.0",
        tempo_processamento_ms=1.235,
    )

    # Valida se o modelo serializa o dicionário JSON perfeitamente sem falhas de tipo.
    dicionario_json = resposta_producao.model_dump()
    assert dicionario_json["classe_predita"] == 1
    assert dicionario_json["grau_severidade"] == "CRÍTICO"
    assert dicionario_json["tempo_processamento_ms"] == 1.235

    logging.info(
        "Teste 4 Aprovado: Resposta preditiva estruturada e conforme o contrato de"
        "saída."
    )

    # ----------------------------------------------------------------------------------
    # EXIBIÇÃO FORMATADA DO RESULTADO DA HOMOLOGAÇÃO
    # ----------------------------------------------------------------------------------
    print("\n" + "=" * 105)
    print("📋 CERTIFICADO DE HOMOLOGAÇÃO DOS CONTRATOS DE DADOS (PILAR 3 - FASE 6)")
    print("=" * 105)
    print("🩺 Atributos Validados: 10 Variáveis Clínicas com Restrições Biológicas")
    print("🛡️ Motor de Validação: Pydantic V2 (Verificação Estrita de Tipos e Limites)")
    print(
        "📊 Formato de Resposta: Decisão Binária, Escore Probabilístico, Severidade e"
        "Latência (ms)[cite: 18]"
    )
    print(f"📄 Exemplo do Vetor de Entrada Extraído (10 Features): {vetor_ordenado}")
    print("=" * 105 + "\n")

    logging.info(
        "=== PILAR 3 DA FASE 6 CONCLUÍDO COM SUCESSO! CONTRATOS 100% HOMOLOGADOS ==="
    )
