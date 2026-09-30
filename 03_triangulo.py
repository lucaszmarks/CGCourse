"""
Primeiro triangulo: VBO, VAO e o par de shaders.
Único programa do curso com o GLSL embutido em string.
A partir do 03, os shaders passam a ser gravados em arquivos próprios.

MCCC007-23 - Computação Gráfica - UFABC
Prof. João Paulo Gois

Executar: python 02_triangulo.py      Sair: ESC ou fechar a janela
"""
import sys
from pathlib import Path
import glfw
import moderngl
import numpy as np

SHADERS = Path ( __file__ ) . parent / "shaders"

def erro_glfw(codigo, descricao):
    """Substitui o aviso padrão do pyGLFW: imprime código 
    e descrição de qualquer erro do GLFW em stderr"""
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)

glfw.set_error_callback(erro_glfw)

if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)


janela = glfw.create_window(800, 600, "Olá triângulo", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: não foi possível criar a janela")

glfw.make_context_current(janela)
ctx = moderngl.create_context()

# -------------- lado da GPU

prog = ctx.program(vertex_shader=( SHADERS / "basico.vert").read_text(
    encoding ="utf -8") ,fragment_shader =( SHADERS / "basico.frag").read_text(
    encoding ="utf -8"),)


# ------------------- lado da CPU
posicoes = np.array ([
    0.0 , 0.5 , 0.0 , 1.0 ,    # v0 topo
    -0.5 , -0.5 , 0.0 , 1.0 , # v1 esquerda
    0.5 , -0.5 , 0.0 , 1.0 , # v2 direita
] , dtype ='f4')


cores = np.array ([
    1.0 , 0.0 , 0.0 , 1.0 , # v0 vermelho
    0.0 , 1.0 , 0.0 , 1.0 , # v1 verde
    0.0 , 0.0 , 1.0 , 1.0 , # v2 azul
] , dtype ='f4')    
# Dados intercalados: posição (x,y,z,w) e cor (r,g,b,a) de cada vértice,
# vizinhos na memória. 'f4' é float de 32 bits. 

# O VBO é memória bruta na VRAM. 
# VAO diz como lê-la. '4f 4f' significa quatro floats
# para vPosition e quatro para vColors, nessa ordem.
vbo_pos = ctx . buffer ( posicoes . tobytes () )
vbo_cor = ctx . buffer ( cores . tobytes () )
vao = ctx . vertex_array ( prog , [
    ( vbo_pos , '4f', 'vPosition') ,
     ( vbo_cor , '4f', 'vColors') ,
])


while not glfw.window_should_close(janela):
    if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(janela, True)

    ctx.clear(1.0, 1.0, 1.0, 1.0)
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(janela)
    glfw.poll_events()

vao.release()
vbo_pos.release()
vbo_cor.release()
prog.release()
glfw.terminate()
print("Execucao finalizada.")
