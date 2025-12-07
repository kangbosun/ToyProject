import numpy as np
from OpenGL.GL import *

# Vector3 based on array
class Vector3:
    def __init__(self, x, y, z):
        self.data = np.array([x, y, z], dtype=np.float32)

    def X(self):
        return self.data[0]
    def Y(self):
        return self.data[1]
    def Z(self):
        return self.data[2]

    def SetX(self, x):
        self.data[0] = x
    def SetY(self, y):
        self.data[1] = y
    def SetZ(self, z):
        self.data[2] = z

    def Set(self, x, y, z):
        self.data[0] = x
        self.data[1] = y
        self.data[2] = z

    def Set(self, f):
        self.data[0] = f
        self.data[1] = f
        self.data[2] = f



class Transform:
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        self.position = Vector3(position[0], position[1], position[2])
        self.rotation = Vector3(rotation[0], rotation[1], rotation[2]) # Euler angles in degrees
        self.scale = Vector3(scale[0], scale[1], scale[2])

    def get_rotation_matrix(self):
        cx, cy, cz = np.cos([self.rotation.X(), self.rotation.Y(), self.rotation.Z()])
        sx, sy, sz = np.sin([self.rotation.X(), self.rotation.Y(), self.rotation.Z()])
        
        R = np.array([
            [cz*cy,  cz*sy*sx - sz*cx,  cz*sy*cx + sz*sx,  0],
            [sz*cy,  sz*sy*sx + cz*cx,  sz*sy*cx - cz*sx,  0],
            [-sy,    cy*sx,             cy*cx,             0],
            [0,      0,                 0,                 1]
        ])
        return R

    def get_scale_matrix(self):
        scale_matrix = np.array([
            [self.scale.X(), 0, 0, 0],
            [0, self.scale.Y(), 0, 0],
            [0, 0, self.scale.Z(), 0],
            [0, 0, 0, 1]
        ])
        return scale_matrix

    def get_model_matrix(self):
        model = np.identity(4, dtype=np.float32)

        rot_matrix = self.get_rotation_matrix()
        scale_matrix = self.get_scale_matrix()

        model = scale_matrix @ rot_matrix
        model[3, :3] = self.position.data
        return model.transpose()
       
