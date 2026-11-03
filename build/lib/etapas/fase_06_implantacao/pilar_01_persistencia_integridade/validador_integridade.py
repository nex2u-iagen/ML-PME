"""Módulo Especialista em Verificação Criptográfica de Integridade (Pilar 1 - Fase 6).

Responsabilidade Única: Calcular a assinatura digital SHA-256 de artefatos
no disco e confrontá-la com manifestos de governança para prevenir adulterações,
injeção de código malicioso ou corrupção de arquivos antes da carga na memória RAM[cite:
17].
"""

# 'import' traz o módulo 'hashlib' da biblioteca padrão para cálculo de funções de
# resumo criptográfico[cite: 17].
import hashlib

# 'import' carrega o módulo 'json' para permitir a leitura e decodificação do manifesto
# gravado no disco[cite: 18].
import json

# 'import' traz o módulo 'logging' para emissão de mensagens rastreáveis de segurança no
# console[cite: 18].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de arquivos
# e diretórios[cite: 18].
from pathlib import Path


# 'class' define a classe responsável pelas rotinas de auditoria e validação matemática
# de integridade física[cite: 17].
class ValidadorIntegridadeArtefato:
    """Motor de cálculo e conferência de hashes criptográficos SHA-256 para modelos
    de IA[cite: 17].
    """

    # 'def' define o método especialista de leitura em baixo nível e extração do hash de
    # segurança[cite: 17].
    def calcular_hash_arquivo(self, caminho_arquivo: Path) -> str:
        """Gera o hash SHA-256 de um arquivo processando o fluxo de dados em blocos
        contidos de memória[cite: 17].

        Args:
            caminho_arquivo (Path): Endereço físico do arquivo binário a ser examinado
            no disco[cite: 18].

        Returns:
            str: Assinatura hexadecimal única e imutável de 64 caracteres representativa
            do arquivo[cite: 17].
        """
        # 'hashlib.sha256()' inicializa uma nova instância do algoritmo Secure Hash
        # Algorithm 2 com saída de 256 bits[cite: 17].
        gerador_hash = hashlib.sha256()

        # 'with open(...)' gerencia a abertura segura do arquivo binário garantindo seu
        # fechamento ao término[cite: 24].
        # 'caminho_arquivo': a localização exata do arquivo binário no sistema de
        # arquivos[cite: 18].
        # '"rb"' (Read Binary): modo de leitura binária pura essencial para não
        # interpretar bytes como texto ASCII/UTF-8[cite: 24].
        # 'as arquivo': armazena o descritor de arquivo aberto na variável local
        # 'arquivo'[cite: 24].
        with open(caminho_arquivo, "rb") as arquivo:
            # 'for bloco in iter(...)': padrão otimizado do Python para leitura
            # iterativa de fluxos sem esgotar a memória RAM[cite: 18, 24].
            # 'lambda: arquivo.read(65536)': função anônima que lê exatamente 64
            # Kilobytes (65.536 bytes) por ciclo[cite: 24].
            # 'b""' (Byte Vazio): condição de parada do iterador quando o ponteiro
            # atinge o final do arquivo (EOF)[cite: 24].
            for bloco in iter(lambda: arquivo.read(65536), b""):
                # 'gerador_hash.update(bloco)' alimenta o motor criptográfico com os 64
                # KB lidos, acumulando o cálculo[cite: 17].
                gerador_hash.update(bloco)

        # 'gerador_hash.hexdigest()' finaliza o processamento e devolve o hash como uma
        # cadeia textual hexadecimal de 64 caracteres[cite: 17].
        return gerador_hash.hexdigest()

    # 'def' define o método que confronta a assinatura calculada com o valor registrado
    # no manifesto JSON[cite: 17].
    def validar_artefato_contra_manifesto(
        self, caminho_artefato: Path, caminho_manifesto: Path
    ) -> bool:
        """Confronta a assinatura digital calculada do artefato com o valor certificado
        no manifesto[cite: 17].

        Args:
            caminho_artefato (Path): Rota física do arquivo binário (.joblib) a ser
            conferido[cite: 17, 18].
            caminho_manifesto (Path): Rota física do arquivo de metadados (.json) de
            referência[cite: 17, 18].

        Returns:
            bool: True se a assinatura for perfeitamente autêntica; interrompe com erro
            caso contrário[cite: 17].

        Raises:
            ValueError: Se os arquivos físicos não existirem ou se houver discrepância
            de integridade (adulteração)[cite: 24].
        """
        # '.is_file()' verifica fisicamente no sistema de arquivos se o binário e o
        # manifesto existem no disco[cite: 18].
        # 'if not' atua defensivamente caso algum dos dois caminhos seja inválido ou o
        # arquivo tenha sido deletado[cite: 18, 24].
        if not caminho_artefato.is_file() or not caminho_manifesto.is_file():
            # 'logging.error' registra no terminal a ausência dos arquivos necessários
            # para a validação[cite: 18].
            logging.error(
                "Validação de Segurança — Arquivos de produção não encontrados nodisco!"
            )
            # 'raise ValueError' aborta o processo levantando erro formal de valor
            # ausente[cite: 24].
            raise ValueError(
                f"Arquivos ausentes no disco: {caminho_artefato} ou {caminho_manifesto}"
            )

        # 'with open(...)' abre o manifesto JSON em modo de leitura de texto com
        # codificação UTF-8 padronizada[cite: 24].
        with open(caminho_manifesto, encoding="utf-8") as arquivo:
            # 'json.load(arquivo)' faz o parse do texto JSON convertendo-o de volta em
            # um dicionário Python na memória[cite: 18].
            dados_manifesto = json.load(arquivo)

        # '.get("hash_sha256", "")' extrai a assinatura que foi homologada na Fase 5 sem
        # levantar erro se a chave faltar[cite: 17, 18].
        hash_esperado = str(dados_manifesto.get("hash_sha256", ""))

        # Dispara o método especialista anterior para recalcular a impressão digital
        # real do binário que reside no disco[cite: 17].
        hash_calculado = self.calcular_hash_arquivo(caminho_artefato)

        # 'if' compara as duas assinaturas; se 1 único bit for diferente, a igualdade
        # falha[cite: 17].
        if hash_calculado != hash_esperado:
            # 'logging.critical' emite alerta de nível máximo informando que o arquivo
            # foi modificado por terceiros ou corrompido[cite: 17, 18].
            logging.critical(
                "ALERTA CRÍTICO DE SEGURANÇA: Assinatura SHA-256 do arquivo diverge do"
                "manifesto!"
            )
            logging.critical("Hash Esperado pelo Certificado: %s", hash_esperado)
            logging.critical("Hash Calculado do Arquivo Real: %s", hash_calculado)
            # 'raise ValueError' bloqueia a execução da aplicação para evitar a carga de
            # binários adulterados na memória RAM[cite: 17, 24].
            raise ValueError(
                "Falha de Integridade: O modelo serializado foi corrompido ou"
                "adulterado no disco!"
            )

        # 'logging.info' confirma no terminal que o arquivo binário passou no teste
        # rigoroso de segurança criptográfica[cite: 17, 18].
        logging.info(
            "Integridade criptográfica SHA-256 confirmada: o modelo em disco é"
            "autêntico e homologado."
        )

        # 'return True' atesta formalmente a conformidade para os módulos que gerenciam
        # a carga na memória RAM[cite: 17].
        return True
