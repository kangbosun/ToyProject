from engine.transform import Transform
from OpenGL.GL import *

class Object:
    def __init__(self, name="Object"):
        self.name = name
        self.is_selected = False
        self.enable_collision_event = True
        self.transform = Transform()
        self.mesh = None
        self.material = None
        self.material = None
        self.material = None
        self.uv_scale = (1.0, 1.0)
        self.components = []
        self.local_bounds = ((-0.5, -0.5, 0), (0.5, 0.5, 0)) # Default/Fallback

    def set_mesh(self, mesh):
        self.mesh = mesh
        if mesh:
            self.local_bounds = (mesh.min_point, mesh.max_point)

    def get_world_bounds(self):
        # Assumes scaling is uniform or handled simply for AABB
        # Center = Position
        pos = self.transform.position
        scale = self.transform.scale
        
        min_p = self.local_bounds[0]
        max_p = self.local_bounds[1]
        
        # Calculate Half Extents scaled
        half_w = (max_p[0] - min_p[0]) * scale.X() / 2.0
        half_h = (max_p[1] - min_p[1]) * scale.Y() / 2.0
        
        # Center is at Position (Assuming Pivot is Center)
        min_x = pos.X() - half_w
        max_x = pos.X() + half_w
        min_y = pos.Y() - half_h
        max_y = pos.Y() + half_h
        
        min_y = pos.Y() - half_h
        max_y = pos.Y() + half_h
        
        return (min_x, min_y, max_x, max_y)

    def get_world_radius(self):
        scale = self.transform.scale
        min_p = self.local_bounds[0]
        max_p = self.local_bounds[1]
        
        # Calculate Half Extents scaled
        half_w = (max_p[0] - min_p[0]) * scale.X() / 2.0
        half_h = (max_p[1] - min_p[1]) * scale.Y() / 2.0
        
        # Radius is distance from center to corner
        return (half_w**2 + half_h**2)**0.5

    def set_material(self, material):
        self.material = material

    def add_component(self, component):
        component.owner = self
        self.components.append(component)

    def get_component(self, component_type):
        for c in self.components:
            if isinstance(c, component_type):
                return c
        return None

    def tick(self, dt):
        for component in self.components:
            component.tick(dt)

    def get_render_data(self):
        if not self.mesh or not self.material:
            return None
            
        return {
            "mesh": self.mesh,
            "material": self.material,
            "matrix": self.transform.get_model_matrix(),
            "uv_scale": self.uv_scale
        }

    def on_collision(self, other):
        for component in self.components:
            if hasattr(component, "on_collision"):
                component.on_collision(other)
