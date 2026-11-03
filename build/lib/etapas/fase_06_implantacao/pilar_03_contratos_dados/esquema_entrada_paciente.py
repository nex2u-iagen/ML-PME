"""Módulo de Contrato de Dados para Entrada de Inferência Clínica (Pilar 3 - Fase 6).

Responsabilidade Única: Definir formalmente os 10 atributos preditores (features)
exigidos pelo modelo homologado na Fase 5, com tipagem estrita, limites clínicos
realistas, descrições humanas e ordenação canónica de vetorização.
"""

# 'from' navega no pacote padrão de tipagem; 'import' carrega 'List' para anotação
# formal de vetores unidimensionais.

# 'from pydantic' carrega os componentes centrais de validação de esquemas da biblioteca
# Pydantic V2.
# - 'BaseModel': classe base que transforma classes Python em modelos de dados com
# validação em tempo de execução.
# - 'Field': função declarativa que permite anexar restrições numéricas, descrições e
# exemplos a cada atributo.
from pydantic import BaseModel, Field


# 'class EsquemaEntradaPaciente' herda de 'BaseModel' para atuar como o contrato oficial
# do corpo da requisição (Body).
class EsquemaEntradaPaciente(BaseModel):
    """Contrato formal das 10 variáveis clínicas necessárias para estimativa de risco
    cardiovascular.
    """

    # Feature 1: Idade cronológica do paciente em anos completos.
    # 'idade_paciente: int' estipula que a idade tem de ser obrigatoriamente um número
    # inteiro.
    # 'Field(...)': as reticências (...) definem que o campo é de preenchimento
    # obrigatório (sem valor por omissão).
    # 'ge=18' (Greater than or equal): impõe o limite inferior adulto de 18 anos.
    # 'le=110' (Less than or equal): impõe o teto biológico máximo aceitável de 110
    # anos.
    # 'description': texto informativo inserido automaticamente na documentação Swagger
    # da API.
    # 'examples': lista com valores clínicos realistas para testes interativos imediatos
    # no navegador.
    idade_paciente: int = Field(
        ...,
        ge=18,
        le=110,
        description="Idade cronológica do paciente em anos completos.",
        examples=[58],
    )

    # Feature 2: Pressão arterial sistólica aferida em repouso.
    # 'pressao_sistolica: float' aceita valores numéricos contínuos com casas decimais.
    # 'ge=60.0': limite inferior de sobrevivência hemodinâmica (abaixo disto há choque
    # circulatório grave).
    # 'le=260.0': limite superior de emergência hipertensiva extrema.
    pressao_sistolica: float = Field(
        ...,
        ge=60.0,
        le=260.0,
        description=(
            "Pressão arterial sistólica em repouso (milímetros de mercúrio — mmHg)."
        ),
        examples=[145.0],
    )

    # Feature 3: Concentração de colesterol total sérico.
    # 'colesterol_total: float' quantifica a massa de lípidos por decilitro de sangue.
    # 'ge=80.0': valor mínimo fisiológico do colesterol sérico total (mg/dL).
    # 'le=600.0': valor teto para hipercolesterolemia familiar severa.
    colesterol_total: float = Field(
        ...,
        ge=80.0,
        le=600.0,
        description="Concentração de colesterol sérico total em jejum (mg/dL).",
        examples=[235.0],
    )

    # Feature 4: Frequência cardíaca basal de repouso.
    # 'frequencia_cardiaca: float' afere a cadência do miocárdio em batimentos por
    # minuto (bpm).
    # 'ge=35.0': piso para bradicardia fisiológica extrema em repouso (atletas).
    # 'le=220.0': teto taquicárdico de esforço extremo.
    frequencia_cardiaca: float = Field(
        ...,
        ge=35.0,
        le=220.0,
        description=(
            "Frequência cardíaca aferida em repouso basal (batimentos por minuto —bpm)."
        ),
        examples=[78.0],
    )

    # Feature 5: Glicemia sérica quantificada após jejum.
    # 'glicemia_jejum: float' representa a taxa glicémica de repouso.
    # 'ge=40.0': piso crítico para hipoglicemia sintomática grave (mg/dL).
    # 'le=500.0': teto para cetoacidose diabética ou hiperglicemia severa.
    glicemia_jejum: float = Field(
        ...,
        ge=40.0,
        le=500.0,
        description=(
            "Glicemia sérica quantificada após jejum mínimo de 8 horas (mg/dL)."
        ),
        examples=[115.0],
    )

    # Feature 6: Índice de Massa Corporal (IMC = peso / altura^2).
    # 'indice_massa_corporal: float' avalia a composição ponderal do paciente.
    # 'ge=12.0': limite inferior de desnutrição severa (kg/m²).
    # 'le=65.0': limite superior para obesidade de classe III mórbida extrema.
    indice_massa_corporal: float = Field(
        ...,
        ge=12.0,
        le=65.0,
        description="Índice de Massa Corporal calculado (kg/m²).",
        examples=[29.4],
    )

    # Feature 7: Infradesnivelamento do segmento ST no eletrocardiograma induzido por
    # esforço.
    # 'infradesnivel_st: float' mede o desvio do traçado eletrocardiográfico durante
    # sobrecarga cardíaca.
    # 'ge=-5.0': admite pequenas elevações compensatórias ou depressões leves
    # (milímetros — mm).
    # 'le=10.0': depressão isquémica severa do segmento ST.
    infradesnivel_st: float = Field(
        ...,
        ge=-5.0,
        le=10.0,
        description=(
            "Infradesnivelamento do segmento ST no ECG induzido por esforço (mm)."
        ),
        examples=[1.8],
    )

    # Feature 8: Histórico familiar direto de eventos coronários precoces.
    # 'historico_familiar: int' variável binária nominal codificada numericamente (0 ou
    # 1).
    # 'ge=0' e 'le=1': força matematicamente a aceitação exclusiva dos números inteiros
    # zero e um.
    historico_familiar: int = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Indicador binário de cardiopatias em parentes de primeiro grau (0: Não, 1:"
            "Sim)."
        ),
        examples=[1],
    )

    # Feature 9: Escala clínica de sedentarismo e inatividade física.
    # 'nivel_sedentarismo: int' classificação ordinal em escala médica graduada.
    # 'ge=0': nível 0 corresponde a um atleta ativo com treino regular.
    # 'le=4': nível 4 corresponde a sedentarismo severo e continuado.
    nivel_sedentarismo: int = Field(
        ...,
        ge=0,
        le=4,
        description=(
            "Escala clínica de sedentarismo físico (0: Atleta regular, 4: Sedentário"
            "severo)."
        ),
        examples=[3],
    )

    # Feature 10: Tempo acumulado de hospitalizações prévias nos últimos 24 meses.
    # 'tempo_internacao_previo: float' histórico de internamentos clínicos em dias.
    # 'ge=0.0': paciente sem histórico prévio de internamento (zero dias).
    # 'le=365.0': teto máximo acumulado de hospitalização de um ano completo.
    tempo_internacao_previo: float = Field(
        ...,
        ge=0.0,
        le=365.0,
        description=(
            "Total acumulado de dias de internamento clínico nos últimos 24 meses."
        ),
        examples=[4.5],
    )

    # 'def exportar_vetor_ordenado(...)' é o método de conversão do Pydantic para o
    # formato matricial.
    # 'self': acede às 10 propriedades validadas presentes na instância do objeto.
    # '-> List[float]': garante formalmente a devolução de uma lista ordenada de números
    # flutuantes.
    def exportar_vetor_ordenado(self) -> list[float]:
        """Converte as 10 variáveis do contrato numa lista ordenada na sequência
        canónica do Scikit-Learn.

        Returns:
            List[float]: Vetor unidimensional com as 10 grandezas na ordem exata de
            treino do pipeline.
        """
        # Devolve a lista ordenada de acordo com a assinatura do StandardScaler e do SVM
        # da Fase 5.
        # Cada campo é explicitamente convertido para 'float' para garantir a
        # compatibilidade com a matriz NumPy.
        return [
            float(self.idade_paciente),
            float(self.pressao_sistolica),
            float(self.colesterol_total),
            float(self.frequencia_cardiaca),
            float(self.glicemia_jejum),
            float(self.indice_massa_corporal),
            float(self.infradesnivel_st),
            float(self.historico_familiar),
            float(self.nivel_sedentarismo),
            float(self.tempo_internacao_previo),
        ]
