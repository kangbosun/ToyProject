import numpy as np
from engine.transform import Transform, Vector3

class Camera:
    def __init__(self, position=(0, 0, 10), rotation=(0, 0, 0), zoom=1.0):
        self.transform = Transform(position, rotation)
        self.zoom = zoom
        self.ortho_size = 5.0 # Height of the view in world units

    def get_view_matrix(self):
        # View Matrix is Inverse of Camera Transform
        # For simplicity, let's just do translation and inverse Z translation
        
        # M_view = R_transpose * T_inverse
        
        # Invert Translation
        pos = self.transform.position.data
        t_inv = np.identity(4, dtype=np.float32)
        t_inv[3, :3] = -pos
        
        # Rotation (We will skip rotation for now or implement as inverse)
        # Assuming identity rotation for this 2D-style camera first
        
        return t_inv.transpose()

    def get_projection_matrix(self, width, height):
        aspect = width / height
        
        # Orthographic Projection
        # left, right, bottom, top, near, far
        height_half = self.ortho_size / 2.0 / self.zoom
        width_half = height_half * aspect
        
        left = -width_half
        right = width_half
        bottom = -height_half
        top = height_half
        near = 0.1
        far = 100.0
        
        p = np.identity(4, dtype=np.float32)
        p[0, 0] = 2.0 / (right - left)
        p[1, 1] = 2.0 / (top - bottom)
        p[2, 2] = -2.0 / (far - near)   
        p[3, 0] = -(right + left) / (right - left)
        p[3, 1] = -(top + bottom) / (top - bottom)
        p[3, 2] = -(far + near) / (far - near)
        
        return p.transpose()
