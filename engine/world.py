from engine.scene_manager import SceneManager
from engine.world_setting import WorldSetting
from engine.camera import Camera
from engine.mesh import Mesh
from engine.material import Material
from game_objects.object import Object
from game_objects.components.ai_component import HamsterAIComponent, CatAIComponent

import random
from OpenGL.GL import *
from OpenGL.GLU import gluUnProject
import numpy as np
import math

class World:
    def __init__(self, screen_width, screen_height):
        self.setting = WorldSetting(10, 10)
        self.scene_manager = SceneManager()
        self.camera = Camera(position=(0, 0, 10))
        
        # Game State
        self.selected_object = None
        
        # Resources
        self.quad_mesh = None
        self.materials = {}
        
    def load_assets(self):
        self.quad_mesh = Mesh.create_quad()
        self.materials["mouse"] = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/mouse.png")
        self.materials["wood"] = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/woodtile.png")
        self.materials["cat"] = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/cat.png")

    def reset(self):
        self.scene_manager.clear()
        self.selected_object = None
        
        width, height = self.setting.field_size
        
        # Floor
        tile = Object(name="Floor")
        tile.set_mesh(self.quad_mesh)
        tile.set_material(self.materials["wood"])
        tile.enable_collision_event = False
        tile.transform.scale.SetX(width)
        tile.transform.scale.SetY(height)
        tile.transform.position.SetZ(-0.1)
        tile.uv_scale = (width, height)
        self.scene_manager.add_object(tile)
        
        # Hamsters
    def spawn_hamster(self, x, y, is_baby=False):
        # Unique Name
        idx = len([o for o in self.scene_manager.objects if "Hamster" in o.name])
        name_prefix = "Baby Hamster" if is_baby else "Hamster"
        hamster = Object(name=f"{name_prefix} {idx}")
        hamster.set_mesh(self.quad_mesh)
        hamster.set_material(self.materials["mouse"])
        
        hamster.transform.position.SetX(x)
        hamster.transform.position.SetY(y)
        
        scale = 0.25
        if is_baby:
             scale /= 3.0
             
        hamster.transform.scale.Set(scale) 
        
        ai = HamsterAIComponent(self) # Pass World instance
        if is_baby:
            ai.is_adult = False
            ai.scale_ref = 0.25 # Full size
        
        hamster.add_component(ai)
        self.scene_manager.add_object(hamster)

    def reset(self):
        self.scene_manager.clear()
        self.selected_object = None
        
        width, height = self.setting.field_size
        
        # Floor
        tile = Object(name="Floor")
        tile.set_mesh(self.quad_mesh)
        tile.set_material(self.materials["wood"])
        tile.enable_collision_event = False
        tile.transform.scale.SetX(width)
        tile.transform.scale.SetY(height)
        tile.transform.position.SetZ(-0.1)
        tile.uv_scale = (width, height)
        self.scene_manager.add_object(tile)
        
        # Hamsters
        for i in range(self.setting.hamster_count):
            half_w = width / 2.0
            half_h = height / 2.0
            rx = random.uniform(-half_w + 1, half_w - 1)
            ry = random.uniform(-half_h + 1, half_h - 1)
            self.spawn_hamster(rx, ry)
            
        # Cat
        cat = Object(name="Cat")
        cat.set_mesh(self.quad_mesh)
        cat.set_material(self.materials["cat"])
        cat.transform.position.SetY(2.0)
        cat.transform.scale.Set(0.5)
        cat.add_component(CatAIComponent(self))
        self.scene_manager.add_object(cat)
        
    def tick(self, dt):
        self.scene_manager.tick(dt)

    def select_object(self, x, y, view_matrix, proj_matrix, viewport):
        if view_matrix is None or proj_matrix is None:
            return

        winX = float(x)
        winY = float(viewport[3] - y)
        
        try:
            # Transpose matrices for gluUnProject (which expects Column-Major memory layout)
            # The matrices from Camera are designed for Row-Major (GL_TRUE transpose) upload,
            # so they have translation in the 'wrong' place for raw Column-Major reading.
            view_d = np.ascontiguousarray(view_matrix.transpose(), dtype=np.float64)
            proj_d = np.ascontiguousarray(proj_matrix.transpose(), dtype=np.float64)
            
            # Unproject to Z=0 plane
            world_x_near, world_y_near, world_z_near = gluUnProject(winX, winY, 0.0, view_d, proj_d, viewport)
            world_x_far, world_y_far, world_z_far = gluUnProject(winX, winY, 1.0, view_d, proj_d, viewport)
            
            if (world_z_far - world_z_near) != 0:
                t = -world_z_near / (world_z_far - world_z_near)
                wx = world_x_near + t * (world_x_far - world_x_near)
                wy = world_y_near + t * (world_y_far - world_y_near)
            else:
                 wx, wy = world_x_near, world_y_near
                 
            min_dist = 999.0
            clicked_obj = None
            
            for obj in self.scene_manager.objects:
                ox = obj.transform.position.X()
                oy = obj.transform.position.Y()
                dist = math.sqrt((ox - wx)**2 + (oy - wy)**2)
                radius = max(obj.transform.scale.X(), obj.transform.scale.Y()) / 2.0
                
                if dist < radius:
                    if dist < min_dist:
                        min_dist = dist
                        clicked_obj = obj
            
            # Deselect previous
            if self.selected_object:
                self.selected_object.is_selected = False

            self.selected_object = clicked_obj
            
            # Select new
            if self.selected_object:
                self.selected_object.is_selected = True
                
            # print(f"Selected: {self.selected_object.name if self.selected_object else 'None'}")
            
        except Exception as e:
            print(f"Selection Error: {e}")
