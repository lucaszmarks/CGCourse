"""
Acerte o alvo : um quadrado , quatro papeis .

Reune o que veio antes -- VBO , EBO , VAO , uniformes -- e
    acrescenta a peca que
faltava : um laco em que o movimento depende do TEMPO
    DECORRIDO , e nao do numero
de quadros desenhados .
O mesmo quadrado de quatro vertices e o jogador , o alvo , o
tiro e cada marca do
    placar . Nenhum byte da VRAM e reescrito durante a partida .
MCCC007 -23 - Computacao Grafica - UFABC
Executar : python 08 _acerte_o_alvo .py
Teclas: CIMA e BAIXO movem o jogador | ESPACO atira | ESC sai
"""

import sys
from pathlib import Path

import glfw
import moderngl
import numpy as np

SHADERS = Path ( __file__ ) . parent / " shaders "

LADO = 800 # janela quadrada : ver a nota sobre proporcao

JOGADOR_X , ESCALA_JOGADOR = -0.80 , 0.20
ALVO_X , ESCALA_ALVO = 0.80 , 0.26
ESCALA_TIRO = 0.06

# Unidades de NDC por SEGUNDO -- nao por quadro . Essa e a diferenca do capitulo .
VEL_JOGADOR , VEL_ALVO , VEL_TIRO = 1.5 , 1.2 , 2.5
LIMITE_Y = 0.78 # ate onde jogador e alvo sobem
DT_MAXIMO = 0.05 # trava de seguranca : ver a nota sobre o passo grande

# Placar : uma marca por acerto , desenhada com o MESMO quadrado .
PLACAR_CANTO = ( -0.90 , 0.90)
PLACAR_PASSO , ESCALA_MARCA = 0.058 , 0.042
PLACAR_MAXIMO = 12 # depois disso a fileira sairiada tela

FUNDO = (0.04 , 0.05 , 0.09 , 1.0)

# Inicializacao -------------------

def erro_glfw ( codigo , descricao ) :
""" Sem este callback , a razao real de uma falha do GLFW
    e descartada e
    so resta a mensagem generica do sys . exit .
"""
print ( f" GLFW [{ codigo }]: { descricao }", file = sys . stderr )


glfw . set_error_callback ( erro_glfw ) # antes de glfw . init () , de proposito

if not glfw . init () :
    sys . exit (" FALHA : glfw nao inicializou ")

glfw . window_hint ( glfw . CONTEXT_VERSION_MAJOR , 4)
glfw . window_hint ( glfw . CONTEXT_VERSION_MINOR , 0)
glfw . window_hint ( glfw . OPENGL_PROFILE , glfw .
    OPENGL_CORE_PROFILE )
glfw . window_hint ( glfw . OPENGL_FORWARD_COMPAT , glfw . TRUE )
# Sem a dica acima , o macOS recusa qualquer contexto 3.2+ e
61 # create_window devolve None . E inofensiva no Windows e no Linux .
glfw . window_hint ( glfw . SAMPLES , 4)
# Sem esta linha , redimensionar a janela deforma a cena : o viewport continua
# com o tamanho antigo , e o NDC deixa de ser quadrado na tela .
glfw . window_hint ( glfw . RESIZABLE , False )

janela = glfw . create_window ( LADO , LADO , " Acerte o alvo ",
None , None )
if not janela :
    glfw . terminate ()
    sys . exit (" FALHA : nao foi possivel criar a janela ")

glfw . make_context_current ( janela )
glfw . swap_interval (1) # espera o retraco vertical : ver a nota sobre vsync
ctx = moderngl . create_context ()

prog = ctx . program (
vertex_shader =( SHADERS / " acerte_o_alvo . vert ") . read_text
( encoding ="utf -8") ,
fragment_shader =( SHADERS / " basico . frag "). read_text (
encoding ="utf -8") ,
)

#GEOMETRIA ------------------------------------------


CANTOS = (( -0.5 , -0.5) , (0.5 , -0.5) , (0.5 , 0.5) , ( -0.5 , 0.5)
)
CORES = ((1.0 , 0.2 , 0.2) , (0.2 , 1.0 , 0.2) , (0.2 , 0.4 , 1.0) ,
(1.0 , 0.9 , 0.2) )

QUADRADO = np . array ([
    v for (x , y ) , cor in zip ( CANTOS , CORES )
    for v in (x , y , 0.0 , 1.0) + cor + (1.0 ,)
] , dtype ='f4' )

# Os MESMOS quatro vertices , lidos de duas maneiras . Como no exemplo da

# diagonal : muda so a ordem de leitura , o VBO nao e tocado .
TRIANGULOS = np . array ([0 , 1 , 2 , 2 , 3 , 0] , dtype ='u4') # dois triangulos
CONTORNO = np . array ([0 , 1 , 2 , 3] , dtype ='u4' ) # o ciclo dos cantos

vbo = ctx . buffer ( QUADRADO . tobytes () )
ebo_cheio = ctx . buffer ( TRIANGULOS . tobytes () )
ebo_borda = ctx . buffer ( CONTORNO . tobytes () )

# Um VAO por EBO : o buffer de indices faz parte do estado do VAO .
vao_cheio = ctx . vertex_array (
prog , [( vbo , '4f 4f', 'vPosition', 'vColors ')] ,
    index_buffer = ebo_cheio )
vao_borda = ctx . vertex_array (
    prog, [(vbo, '4f,4f', 'vPosition', 'vColors')],
    index_buffer=ebo_borda)


# ESTADO E CONTROLES ----------------------------------

jogador_y , alvo_y = 0.0 , 0.0
sentido_alvo = 1.0
atirando , tiro = False , [0.0 , 0.0]
acertos = 0


def tecla ( window , key , scancode , action , mods ) :
    global atirando
    if key == glfw . KEY_ESCAPE and action == glfw . PRESS :
        glfw . set_window_should_close ( window , True )
    # Movimento continuo precisa do inicio E do fim do toque, por isso o
    # callback trata PRESS e RELEASE em vez de so PRESS .
    elif key == glfw . KEY_SPACE and action == glfw . PRESS and not atirando :
        atirando = True
        tiro [0] , tiro [1] = JOGADOR_X , jogador_y


glfw . set_key_callback ( janela , tecla )


def desenhar ( vao , escala , deslocamento , modo = moderngl .TRIANGLES ) :
    prog ['u_escala']. value = escala
    prog ['u_deslocamento']. value = deslocamento
    vao . render ( modo )

def colidiu () :
    """ Sobreposicao de dois retangulos alinhados aos eixos :
os centros distam
137 menos que a soma das meias - larguras , nos dois eixos ao
mesmo tempo ."""
    meio_alvo , meio_tiro = ESCALA_ALVO / 2 , ESCALA_TIRO / 2
    return ( abs ( tiro [0] - ALVO_X ) < meio_alvo + meio_tiro
    and abs ( tiro [1] - alvo_y ) < meio_alvo +
    meio_tiro )

# LAÇO PRINCIPAL ------------------------------------------------
    
instante_anterior = glfw . get_time ()
quadros , marco = 0 , instante_anterior

while not glfw . window_should_close ( janela ) :
    agora = glfw . get_time ()
    # Se a janela for arrastada ou o sistema engasgar , dt vira um numero enorme
    # e o tiro atravessa o alvo sem tocar nele . A trava evita isso .
    dt = min ( agora - instante_anterior , DT_MAXIMO )
    instante_anterior = agora

    # --- atualizacao : tudo multiplicado por dt , nada por quadro ---
    # Movimento continuo : consulta direta do estado das teclas .




