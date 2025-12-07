from OpenGL.GL import *
import numpy as np

class Mesh:
    def __init__(self, vertices, indices, min_point=None, max_point=None):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        self.indices_count = len(indices)
        
        # Bounding Box
        self.min_point = min_point if min_point else (-0.5, -0.5, 0)
        self.max_point = max_point if max_point else (0.5, 0.5, 0)

        glBindVertexArray(self.vao)

        # VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Position Attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Texture Coord Attribute
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0) 
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.indices_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    @staticmethod
    def create_quad():
        # Vertices: Pos(x,y,z), Tex(u,v)
        vertices = np.array([
             0.5,  0.5, 0.0,  1.0, 1.0, # Top Right
             0.5, -0.5, 0.0,  1.0, 0.0, # Bottom Right
            -0.5, -0.5, 0.0,  0.0, 0.0, # Bottom Left
            -0.5,  0.5, 0.0,  0.0, 1.0  # Top Left
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 3,
            1, 2, 3
        ], dtype=np.uint32)
        
        return Mesh(vertices, indices, (-0.5, -0.5, 0), (0.5, 0.5, 0))
