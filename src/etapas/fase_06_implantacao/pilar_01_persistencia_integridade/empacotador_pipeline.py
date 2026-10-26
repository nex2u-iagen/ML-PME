"""Módulo Especialista em Empacotamento e Congelamento de Pipelines (Pilar 1 - Fase 6).

Responsabilidade Única: Persistir o Pipeline do Scikit-Learn completo (pré-processador
e estimador final calibrado) com compressão otimizada via joblib e coordenar
a emissão do manifesto com assinatura criptográfica SHA-256 no disco[cite: 17].
"""

# 'from typing import ...' importa anotações de dicionário e múltiplos tipos aceitos
# para tipagem estática[cite: 18].
# 'import logging' importa o sistema de mensagens de auditoria técnica no console[cite:
# 18].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de pastas
# no sistema de arquivos[cite: 18].
from pathlib import Path
from typing import Any

# 'import joblib' carrega a biblioteca padrão oficial do Scikit-Learn para serialização
# de modelos e arrays NumPy[cite: 17, 18].
import joblib

# 'from ...' importa a classe de metadados de domínio do próprio pilar de
# persistência[cite: 17].
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.metadados_modelo import (  # noqa: E501
    MetadadosModeloProducao,
)

# 'from ...' importa o validador de assinatura digital para cálculo automático do hash
# de segurança[cite: 17].
from src.etapas.fase_06_implantacao.pilar_01_persistencia_integridade.validador_integridade import (  # noqa: E501
    ValidadorIntegridadeArtefato,
)


# 'class' define a classe especialista no empacotamento e compressão física dos modelos
# de Machine Learning[cite: 17].
class EmpacotadorPipelineProducao:
    """Especialista responsável pela compressão física e governança de artefatos de
    IA[cite: 17].
    """

    # 'def __init__(...)' instancia o empacotador configurando o diretório de destino no
    # disco[cite: 18].
    def __init__(self, pasta_destino_modelos: Path) -> None:
        """Inicializa o empacotador com a pasta de persistência dos binários
        homologados[cite: 17, 21].

        Args:
            pasta_destino_modelos (Path): Diretório onde os artefatos de produção serão
            armazenados no disco[cite: 18].
        """
        # 'self.pasta_destino' armazena o caminho do diretório dentro do estado do
        # objeto empacotador[cite: 18].
        self.pasta_destino = pasta_destino_modelos

        # '.mkdir(parents=True, exist_ok=True)' garante a criação recursiva das pastas
        # caso ainda não existam no sistema[cite: 18].
        self.pasta_destino.mkdir(parents=True, exist_ok=True)

        # 'self.validador' instancia o perito criptográfico por Composição Orientada a
        # Objetos para cálculo do hash[cite: 17, 18].
        self.validador = ValidadorIntegridadeArtefato()

    # 'def salvar_pipeline_com_manifesto(...)' coordena o salvamento binário e a emissão
    # do certificado JSON[cite: 17].
    def salvar_pipeline_com_manifesto(
        self,
        pipeline_campeao: Any,
        metadados: MetadadosModeloProducao,
        nome_arquivo_base: str = "pipeline_campeao_producao",
    ) -> dict[str, Path]:
        """Serializa o pipeline com compressão gzip e emite o manifesto criptográfico
        correspondente[cite: 17].

        Args:
            pipeline_campeao (Any): Pipeline ajustado contendo o pré-processador e o
            modelo calibrado na Fase 5[cite: 17, 21].
            metadados (MetadadosModeloProducao): Objeto com as propriedades de
            governança e limiar do modelo[cite: 17, 20].
            nome_arquivo_base (str): Nome base dos arquivos gerados sem a extensão
            física[cite: 18].

        Returns:
            Dict[str, Path]: Dicionário com os caminhos físicos confirmados do arquivo
            .joblib e do manifesto .json[cite: 17, 18].
        """
        # O operador '/' do Pathlib concatena de forma nativa e portável o caminho da
        # pasta com o nome do arquivo binário[cite: 18].
        caminho_artefato = self.pasta_destino / f"{nome_arquivo_base}.joblib"

        # Constrói o caminho completo para o arquivo de manifesto JSON
        # correspondente[cite: 18].
        caminho_manifesto = self.pasta_destino / f"{nome_arquivo_base}_manifesto.json"

        # 'logging.info' emite mensagem informando o início da gravação do binário
        # compactado[cite: 18].
        logging.info(
            "Serializando Pipeline campeão com compressão no disco: %s...",
            caminho_artefato.name,
        )

        # 'joblib.dump(...)' executa a serialização em baixo nível do grafo de objetos e
        # tensores em memória[cite: 17].
        # 'pipeline_campeao': o objeto na memória RAM contendo escaladores e pesos
        # aprendidos[cite: 17].
        # 'caminho_artefato': a rota física de gravação do arquivo binário[cite: 18].
        # 'compress=3': aplica algoritmo de compressão gzip de nível 3, reduzindo o
        # tamanho em disco sem penalizar a velocidade de carga[cite: 17].
        joblib.dump(pipeline_campeao, caminho_artefato, compress=3)

        # 'logging.info' informa o início do cálculo de integridade criptográfica[cite:
        # 18].
        logging.info(
            "Calculando assinatura digital SHA-256 e gravando manifesto degovernança..."
        )

        # Dispara o método do validador para extrair a impressão digital real do arquivo
        # recém-gerado no disco[cite: 17].
        hash_sha256 = self.validador.calcular_hash_arquivo(caminho_artefato)

        # Aciona o método do objeto de metadados para embutir o hash e persistir o
        # arquivo JSON de governança[cite: 17].
        metadados.salvar_manifesto(
            hash_sha256=hash_sha256,
            arquivo_artefato=caminho_artefato.name,
            caminho_destino_json=caminho_manifesto,
        )

        # 'logging.info' confirma que a dupla de artefatos de produção foi gerada com
        # sucesso[cite: 17, 18].
        logging.info(
            "Pipeline comprimido e manifesto de governança persistidos com sucesso."
        )

        # 'return' devolve o dicionário estruturado com as duas rotas físicas para uso
        # do orquestrador geral[cite: 17, 18].
        return {
            "caminho_artefato_joblib": caminho_artefato,
            "caminho_manifesto_json": caminho_manifesto,
        }
