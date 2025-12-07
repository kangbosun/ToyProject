from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

def load_shader_source(path):
    with open(path, 'r') as f:
        return f.read()

def load_shader(vertex_src, fragment_src):
    """
    Compiles and links a vertex and fragment shader into a program.
    """
    vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    
    return compileProgram(vertex_shader, fragment_shader)

def load_shader_from_file(vertex_path, fragment_path):
    vertex_src = load_shader_source(vertex_path)
    fragment_src = load_shader_source(fragment_path)
    return load_shader(vertex_src, fragment_src)
