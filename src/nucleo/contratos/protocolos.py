"""Módulo de Contratos e Protocolos Estruturais do Sistema.

Este arquivo funciona como o manual de regras e contratos do nosso projeto.
Ele não executa ações pesadas no computador, mas dita a forma exata
como os outros arquivos devem ser escritos.
"""

# 'from' indica a biblioteca de origem; 'collections.abc' é uma gaveta
# padrão do Python com coleções abstratas.
# 'import' traz para o nosso arquivo apenas a ferramenta solicitada.
# 'Generator' (Gerador) é um tipo especial de função
# que entrega dados aos poucos (fatiados), economizando memória RAM.
from collections.abc import Generator

# 'pathlib' é a biblioteca oficial e moderna do Python
# para lidar com pastas e arquivos do computador.
# 'Path' (Caminho) é uma classe que representa
# o endereço físico de um arquivo no Windows, Linux ou Mac.
from pathlib import Path

# 'typing' é a biblioteca de 'tipagem estática' do Python,
# usada para documentar o tipo de dado de cada variável.
# 'Any' (Qualquer) indica que a função pode receber qualquer
# tipo de dado (texto, número, dicionário, etc.).
# 'Protocol' (Protocolo) é o molde que define as regras e nomes
# de métodos que outras classes devem ter.
# 'runtime_checkable' é um recurso que permite ao Python
# checar em tempo de execução se uma classe obedece ao protocolo.
from typing import Any, Protocol, runtime_checkable

# 'import' traz a biblioteca inteira 'pandas'
# (ferramenta padrão para criar e tratar tabelas de dados).
# 'as' cria um apelido (alias) reduzido; no mercado mundial,
# convencionou-se chamar 'pandas' de 'pd' para digitar menos.
import pandas as pd


# O caractere '@' representa um 'decorador' (decorator):
# uma etiqueta especial que adiciona superpoderes à classe abaixo.
# Aqui, ativamos a checagem dinâmica em tempo de execução para o contrato.
@runtime_checkable
# 'class' é a palavra-chave que declara uma nova classe
# (um molde ou fábrica de objetos).
# 'ProtocoloLeitorArquivos' é o nome da nossa classe em Português do Brasil,
# usando o padrão PascalCase (iniciais maiúsculas).
# '(Protocol)' entre parênteses indica herança:
# nossa classe herda todos os poderes estruturais da classe Protocol.
class ProtocoloLeitorArquivos(Protocol):
    """Contrato formal para qualquer leitor de arquivos tabulares do projeto."""

    # 'def' é a palavra-chave que define uma nova função ou método dentro da classe.
    # 'carregar_tabela' é o nome da ação que o leitor deve ser capaz de executar.
    # 'self' representa a própria instância da classe acessando seus métodos internos.
    # 'caminho_arquivo: Path' é um parâmetro obrigatório que exige receber um objeto do
    # tipo Path (o endereço do arquivo).
    # '**kwargs: Any' captura múltiplos argumentos extras no formato chave=valor
    # (keyword arguments), aceitando qualquer valor.
    # '-> pd.DataFrame' é uma anotação de retorno: avisa formalmente que este método
    # DEVE devolver uma tabela do pandas.
    # O caractere ':' (dois pontos) finaliza a assinatura e abre o bloco de código
    # interno.
    def carregar_tabela(self, caminho_arquivo: Path, **kwargs: Any) -> pd.DataFrame:
        """Assinatura obrigatória para leitura integral de uma tabela na memória."""
        # O símbolo '...' (três pontos consecutivos, chamado de Ellipsis) avisa ao
        # Python:
        # 'Não execute nada aqui agora; este método é apenas um molde, o código real
        # será escrito na classe concreta'.
        ...

    # 'def' inicia a declaração do segundo método obrigatório do nosso leitor.
    # 'carregar_em_lotes' é o método focado em processar arquivos gigantescos sem travar
    # o computador.
    # 'tamanho_lote: int' é um parâmetro que exige um número inteiro (int), indicando
    # quantas linhas ler por vez.
    # '-> Generator[pd.DataFrame, None, None]' declara que o retorno é um gerador que
    # entrega DataFrames fatiados.
    def carregar_em_lotes(
        self,
        caminho_arquivo: Path,
        tamanho_lote: int,
        **kwargs: Any,
    ) -> Generator[pd.DataFrame, None, None]:
        """Assinatura obrigatória para leitura de arquivos massivos em blocos
        iterativos.
        """
        # Novamente as reticências indicando que se trata de uma casca abstrata de
        # contrato.
        ...


# Aplicamos o mesmo decorador para que o visualizador também possa ser inspecionado
# durante o programa.
@runtime_checkable
# Criamos a classe de contrato para qualquer motor que desenhe ou exporte gráficos.
class ProtocoloVisualizador(Protocol):
    """Contrato formal para motores de renderização visual e persistência de imagens."""

    # 'figura: Any' aceita o objeto gráfico criado (seja do matplotlib, seaborn ou
    # plotly).
    # 'caminho_saida: Path' exige o caminho onde a imagem será salva no computador (ex:
    # pasta relatorios).
    # '-> Path' avisa que o método deve devolver o próprio caminho confirmado de onde a
    # imagem foi gravada.
    def salvar_figura(self, figura: Any, caminho_saida: Path) -> Path:
        """Assinatura obrigatória para gravação padronizada de gráficos analíticos em
        disco.
        """
        # Reticências reservando o espaço da implementação concreta.
        ...
