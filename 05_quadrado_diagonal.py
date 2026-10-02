"""
Quadrado com EBO: quatro vertices, dois triangulos, seis indices.
MCCC007-23 - Computacao Grafica - UFABC

Executar: python 04_quadrado.py      Sair: ESC ou fechar a janela
"""
import sys
from pathlib import Path

import glfw
import moderngl
import numpy as np

SHADERS = Path(__file__).parent / "shaders"

vertices = np.array([
    -0.5, -0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,
    0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,
    0.5, 0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0,
    -0.5, 0.5, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0,
],dtype='f4')

diagonal_02 = np.array([0, 1, 2, 2, 3, 0],dtype='u4')
diagonal_13 = np.array([0, 1, 3, 1, 2, 3],dtype='u4')

branco = (1.0, 1.0, 1.0, 1.0)
preto = (0.0, 0.0, 0.0, 0.0)


def erro_glfw(codigo, descricao):
    """Substitui o aviso padrão do pyGLFW: imprime código 
    e descrição de qualquer erro do GLFW em stderr"""
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


glfw.set_error_callback(erro_glfw)   # antes de glfw.init(), de proposito

if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)


janela = glfw.create_window(600, 600, "Troca de diagonal", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: nao foi possivel criar a janela")

glfw.make_context_current(janela)
glfw.swap_interval(1)
ctx = moderngl.create_context()

prog = ctx.program(
    vertex_shader=(SHADERS / "basico.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
)



vbo = ctx.buffer(vertices.tobytes())
ebo = ctx.buffer(diagonal_02.tobytes())

vao = ctx.vertex_array(
    prog, [(vbo, '4f 4f', 'vPosition', 'vColors')], index_buffer=ebo
)

diagonal_alternativa = False
modo_noite = False
def tecla(window, key, scancode, action, mods):
    global diagonal_alternativa, modo_noite
    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_D:
        modo_noite = not modo_noite
    elif key == glfw.KEY_SPACE:
        diagonal_alternativa = not diagonal_alternativa
        novos = diagonal_13 if diagonal_alternativa else diagonal_02
        ebo.write(novos.tobytes())    
glfw.set_key_callback(janela, tecla)


while not glfw.window_should_close(janela):
    ctx.clear(*(preto if modo_noite else branco))
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(janela)
    glfw.poll_events()


for recurso in (vao, ebo, vbo, prog):
    recurso.release
glfw.terminate()
print("Execucao finalizada.")
