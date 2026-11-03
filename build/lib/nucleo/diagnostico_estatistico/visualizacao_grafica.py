"""Módulo de Renderização e Visualização Gráfica Padronizada.

Fornece métodos encapsulados para gerar gráficos analíticos
(distribuições, boxplots, correlações e dispersão) com configuração
estética uniforme, salvamento automático em disco e gestão de memória.
"""

# 'import' traz o módulo 'logging' da biblioteca padrão do Python.
# Ele serve para registrar mensagens de auditoria, avisos e confirmações no terminal com
# data e hora.
import logging

# 'from' navega até a biblioteca padrão 'pathlib' (responsável por caminhos de arquivos
# e pastas).
# 'import' traz a classe 'Path' para lidar com caminhos no Linux, Windows ou Mac como
# objetos.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python (usado para anotações
# de tipo estático).
# 'import' traz 'Optional', que documenta que um parâmetro pode receber um valor real ou
# 'None' (vazio).
# 'import' traz a biblioteca fundamental de gráficos do Python: 'matplotlib.pyplot'.
# 'as' cria o apelido reduzido 'plt', convenção universal usada por cientistas de dados
# no mundo todo.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca 'pandas', padrão da indústria para manipulação de tabelas
# bidimensionais.
# 'as' define o apelido clássico 'pd' para encurtar os comandos no código.
import pandas as pd

# 'import' traz a biblioteca estatística de visualização 'seaborn'.
# 'as' define o apelido oficial 'sns', amplamente adotado para construir gráficos
# estatísticos refinados.
import seaborn as sns

# 'logging.basicConfig' parametriza a exibição dos registros de execução no console do
# computador.
# 'level=logging.INFO' garante que mensagens operacionais importantes e de sucesso sejam
# mostradas.
# 'format' define o molde visual da mensagem: ano-mês-dia hora:minuto:segundo — [NÍVEL]
# — texto do aviso.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave que cria um molde estruturado de Orientação a Objetos.
# 'GeradorVisualizacaoGrafica' é o nome da nossa classe, batizada em Português do Brasil
# com iniciais maiúsculas.
class GeradorVisualizacaoGrafica:
    """Classe responsável pela criação, estilização e salvamento de artefatos
    visuais.
    """

    # 'def' define o método especial construtor '__init__', chamado no momento em que a
    # classe é instanciada.
    # 'self' referencia a própria instância da classe para guardar parâmetros dentro do
    # objeto criado.
    # 'estilo_visual: str = "whitegrid"' define o tema padrão do seaborn com fundo
    # branco e linhas de grade.
    # 'resolucao_dpi: int = 300' configura a densidade de pontos por polegada (DPI) em
    # 300 (padrão para impressão).
    # '-> None' indica formalmente que o construtor apenas inicializa o objeto e não
    # devolve nada.
    def __init__(
        self, estilo_visual: str = "whitegrid", resolucao_dpi: int = 300
    ) -> None:
        """Inicializa o gerador gráfico configurando o padrão estético corporativo.

        Args:
            estilo_visual (str, opcional): Tema base do seaborn. Padrão: 'whitegrid'.
            resolucao_dpi (int, opcional): Resolução da imagem exportada. Padrão: 300
            DPI.
        """
        # 'self.resolucao_dpi' armazena o valor inteiro 300 na memória do próprio
        # objeto.
        self.resolucao_dpi = resolucao_dpi

        # 'sns.set_theme' aplica o tema visual escolhido globalmente para todos os
        # gráficos gerados.
        # 'palette="deep"' define uma paleta de cores balanceada, suave e agradável ao
        # olho humano.
        sns.set_theme(style=estilo_visual, palette="deep")

        # 'plt.rcParams' é um dicionário interno do matplotlib que guarda as
        # configurações universais da sessão.
        # Aqui, fixamos a fonte padrão do sistema como 'sans-serif' para garantir
        # legibilidade corporativa.
        plt.rcParams["font.sans-serif"] = "DejaVu Sans"

        # Define a cor das bordas dos eixos do gráfico com um cinza claro suave
        # (#cccccc) para evitar poluição.
        plt.rcParams["axes.edgecolor"] = "#cccccc"

        # Define a espessura da linha da borda em 0.8 pontos, mantendo o gráfico
        # elegante e leve.
        plt.rcParams["axes.linewidth"] = 0.8

        # Registra no log que o motor visual foi calibrado com a resolução escolhida.
        logging.info(
            "Motor visual calibrado para exportação com: %d DPI.", self.resolucao_dpi
        )

    # 'def' inicia a declaração do método focado em desenhar distribuições univariadas.
    # 'dados: pd.DataFrame' exige a tabela completa com as colunas do ERP.
    # 'coluna: str' é o nome da variável contínua a ser mapeada (ex.: 'valor_venda').
    # 'caminho_saida: Path' exige o caminho do arquivo de imagem onde o gráfico será
    # gravado (.png).
    # 'titulo: Optional[str] = None' aceita um texto personalizado para o título ou None
    # para usar o padrão.
    # '-> Path' avisa que o método devolve o próprio endereço do arquivo salvo para fins
    # de rastreabilidade.
    def plotar_distribuicao(
        self,
        dados: pd.DataFrame,
        coluna: str,
        caminho_saida: Path,
        titulo: str | None = None,
    ) -> Path:
        """Renderiza um histograma combinado com curva de densidade contínua (KDE).

        Args:
            dados (pd.DataFrame): Tabela de dados contendo a amostra analisada.
            coluna (str): Nome da coluna numérica contínua a ser inspecionada.
            caminho_saida (Path): Caminho físico no disco para salvar a imagem (.png).
            titulo (Optional[str], opcional): Título personalizado para o topo da
            figura.

        Returns:
            Path: Endereço físico da imagem consolidada e salva no disco.
        """
        # 'plt.subplots()' cria dois objetos em uma tupla: a tela em branco ('figura') e
        # a área de desenho ('eixo').
        # 'figsize=(8, 5)' define a largura em 8 polegadas e a altura em 5 polegadas
        # (proporção áurea retangular).
        figura, eixo = plt.subplots(figsize=(8, 5))

        # 'sns.histplot' plota o histograma com barras verticais medindo a frequência
        # dos dados.
        # 'dados[coluna]' extrai a série de dados selecionada.
        # 'kde=True' calcula e sobrepõe a linha suave de Estimativa de Densidade de
        # Kernel.
        # 'ax=eixo' manda o seaborn desenhar exatamente dentro da moldura que
        # preparamos.
        # 'color="#1f77b4"' aplica a tonalidade azul clássica industrial de alta
        # visibilidade.
        sns.histplot(dados[coluna], kde=True, ax=eixo, color="#1f77b4", edgecolor=None)

        # 'eixo.set_title' define o texto no topo do gráfico; usa o título do usuário ou
        # um padrão automático.
        # 'fontsize=12' ajusta o tamanho da fonte e 'pad=10' afasta o título das barras
        # para não colar.
        eixo.set_title(
            titulo or f"Distribuição da Variável: {coluna}", fontsize=12, pad=10
        )

        # 'eixo.set_xlabel' escreve o nome da variável no eixo horizontal X com fonte
        # tamanho 10.
        eixo.set_xlabel(coluna, fontsize=10)

        # 'eixo.set_ylabel' nomeia o eixo vertical Y como contagem absoluta de
        # ocorrências.
        eixo.set_ylabel("Frequência Absoluta", fontsize=10)

        # 'plt.tight_layout()' ajusta automaticamente os espaçamentos das margens para
        # não cortar textos.
        plt.tight_layout()

        # 'caminho_saida.parent' extrai a pasta onde o arquivo vai morar (ex.:
        # 'relatorios/figuras/').
        # 'mkdir(parents=True, exist_ok=True)' cria a pasta no computador caso ela ainda
        # não exista no disco.
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        # 'figura.savefig' grava a imagem no disco no formato especificado na extensão
        # (.png) em alta resolução.
        figura.savefig(caminho_saida, dpi=self.resolucao_dpi)

        # 'plt.close(figura)' limpa e destrói o objeto gráfico da memória RAM,
        # prevenindo travamento do sistema.
        plt.close(figura)

        # Registra no terminal a gravação bem-sucedida do gráfico de distribuição.
        logging.info("Gráfico de distribuição salvo em: %s", caminho_saida.name)

        # 'return' devolve o caminho do arquivo criado.
        return caminho_saida

    # Método focado em diagnosticar valores extremos e dispersão entre quartis.
    def plotar_diagrama_caixa(
        self,
        dados: pd.DataFrame,
        coluna: str,
        caminho_saida: Path,
        titulo: str | None = None,
    ) -> Path:
        """Renderiza um Boxplot para inspeção visual de anomalias (outliers) e quartis.

        Args:
            dados (pd.DataFrame): Tabela de dados contendo a amostra analisada.
            coluna (str): Nome da coluna numérica a ser mapeada.
            caminho_saida (Path): Caminho para salvar a figura.
            titulo (Optional[str], opcional): Título da figura.

        Returns:
            Path: Endereço do arquivo de imagem salvo.
        """
        # Cria a moldura com proporção horizontal de 8 por 4 polegadas.
        figura, eixo = plt.subplots(figsize=(8, 4))

        # 'sns.boxplot' desenha a caixa de Tukey delimitada pelo 1º quartil (Q1) e 3º
        # quartil (Q3).
        # A linha central dentro da caixa representa a Mediana dos dados.
        # Os pontos desenhados fora das linhas laterais (whiskers) são anomalias
        # estatísticas severas.
        # 'x=dados[coluna]' orienta o boxplot na horizontal para facilitar a leitura dos
        # eixos numéricos.
        # 'color="#2ca02c"' aplica uma tonalidade verde suave.
        sns.boxplot(x=dados[coluna], ax=eixo, color="#2ca02c")

        # Configura o título do topo com fallback para o nome da coluna.
        eixo.set_title(
            titulo or f"Diagrama de Caixa (Outliers): {coluna}", fontsize=12, pad=10
        )

        # Identifica a variável no eixo horizontal.
        eixo.set_xlabel(coluna, fontsize=10)

        # Otimiza margens internas da imagem.
        plt.tight_layout()

        # Assegura a criação das pastas de destino no disco.
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        # Salva o arquivo em disco com 300 DPI de resolução.
        figura.savefig(caminho_saida, dpi=self.resolucao_dpi)

        # Fecha a figura para liberar a memória imediatamente.
        plt.close(figura)

        # Log de confirmação.
        logging.info("Diagrama de caixa salvo em: %s", caminho_saida.name)

        # Retorna o endereço físico da figura gerada.
        return caminho_saida

    # Método dedicado à renderização da matriz de correlações lineares.
    def plotar_matriz_correlacao(
        self,
        matriz_correlacao: pd.DataFrame,
        caminho_saida: Path,
        titulo: str = "Matriz de Correlação Linear",
    ) -> Path:
        """Gera um mapa de calor (Heatmap) com anotações numéricas dos coeficientes.

        Args:
            matriz_correlacao (pd.DataFrame): Tabela quadrada de coeficientes entre -1 e
            +1.
            caminho_saida (Path): Caminho físico para salvamento da imagem (.png).
            titulo (str, opcional): Título da figura. Padrão: 'Matriz de Correlação
            Linear'.

        Returns:
            Path: Endereço do mapa de calor gerado e salvo.
        """
        # Cria uma moldura quadrada ampla de 10 por 8 polegadas para acomodar as células
        # da matriz.
        figura, eixo = plt.subplots(figsize=(10, 8))

        # 'sns.heatmap' renderiza a matriz bidimensional em cores.
        # 'annot=True' escreve os números dos coeficientes dentro de cada quadradinho da
        # matriz.
        # 'fmt=".2f"' formata os números para duas casas decimais (ex.: 0.85 ou -0.42).
        # 'cmap="vlag"' utiliza uma escala divergente (azul para valores negativos e
        # vermelho para positivos).
        # 'center=0.0' fixa o ponto neutro de cor em zero (ausência de correlação).
        # 'square=True' força cada célula a ter formato perfeitamente quadrado.
        # 'linewidths=0.5' cria um vão branco fino e sutil entre as células para
        # separação visual.
        # 'cbar_kws={"shrink": 0.8}' redimensiona a barra de escala de cor lateral para
        # 80% do tamanho.
        sns.heatmap(
            matriz_correlacao,
            annot=True,
            fmt=".2f",
            cmap="vlag",
            center=0.0,
            square=True,
            linewidths=0.5,
            ax=eixo,
            cbar_kws={"shrink": 0.8},
        )

        # Define o título principal do mapa de calor.
        eixo.set_title(titulo, fontsize=13, pad=12)

        # Ajusta as margens para não cortar os nomes das colunas e linhas.
        plt.tight_layout()

        # Garante a existência do diretório pai.
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        # Salva o arquivo com qualidade de publicação científica.
        figura.savefig(caminho_saida, dpi=self.resolucao_dpi)

        # Libera o buffer gráfico da memória RAM.
        plt.close(figura)

        # Emite log de confirmação.
        logging.info("Mapa de correlação salvo com sucesso em: %s", caminho_saida.name)

        # Retorna o caminho do arquivo gerado.
        return caminho_saida

    # Método focado no relacionamento visual bivariado entre duas variáveis contínuas.
    def plotar_dispersao(
        self,
        dados: pd.DataFrame,
        coluna_x: str,
        coluna_y: str,
        caminho_saida: Path,
        adicionar_tendencia: bool = True,
        titulo: str | None = None,
    ) -> Path:
        """Renderiza um gráfico de dispersão com reta de regressão linear opcional.

        Args:
            dados (pd.DataFrame): Tabela contendo as variáveis a serem comparadas.
            coluna_x (str): Nome da variável atribuída ao eixo horizontal X.
            coluna_y (str): Nome da variável atribuída ao eixo vertical Y.
            caminho_saida (Path): Destino do arquivo de imagem no disco.
            adicionar_tendencia (bool, opcional): Se True, plota a reta de regressão
            OLS. Padrão: True.
            titulo (Optional[str], opcional): Título customizado do gráfico.

        Returns:
            Path: Endereço físico da figura salva.
        """
        # Cria a moldura de 8 por 6 polegadas.
        figura, eixo = plt.subplots(figsize=(8, 6))

        # 'if adicionar_tendencia:' decide se desenha a reta de tendência linear ou
        # apenas os pontos soltos.
        if adicionar_tendencia:
            # 'sns.regplot' calcula internamente os Mínimos Quadrados Ordinários (OLS) e
            # traça a reta linear.
            # 'scatter_kws={"alpha": 0.5}' torna os pontos semi-transparentes para
            # mostrar densidade de sobreposição.
            # 'line_kws={"color": "red", "linewidth": 1.5}' desenha a linha de tendência
            # em vermelho destacado.
            sns.regplot(
                data=dados,
                x=coluna_x,
                y=coluna_y,
                ax=eixo,
                scatter_kws={"alpha": 0.5, "color": "#1f77b4"},
                line_kws={"color": "#d62728", "linewidth": 1.5},
            )
        else:
            # 'sns.scatterplot' desenha apenas os pontos da nuvem sem ajustar reta
            # linear.
            sns.scatterplot(
                data=dados,
                x=coluna_x,
                y=coluna_y,
                ax=eixo,
                alpha=0.6,
                color="#1f77b4",
            )

        # Aplica o título no gráfico.
        eixo.set_title(
            titulo or f"Relação entre {coluna_x} e {coluna_y}", fontsize=12, pad=10
        )

        # Rótulos descritivos para ambos os eixos.
        eixo.set_xlabel(coluna_x, fontsize=10)
        eixo.set_ylabel(coluna_y, fontsize=10)

        # Organiza o espaçamento das margens.
        plt.tight_layout()

        # Cria os diretórios necessários.
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        # Grava o arquivo de imagem no disco.
        figura.savefig(caminho_saida, dpi=self.resolucao_dpi)

        # Limpa os artefatos da memória RAM.
        plt.close(figura)

        # Registra a persistência no log.
        logging.info("Gráfico de dispersão salvo em: %s", caminho_saida.name)

        # Retorna o endereço da imagem criada.
        return caminho_saida
