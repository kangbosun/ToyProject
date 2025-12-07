from OpenGL.GL import *
from OpenGL.GLUT import *
import sys
import imgui
from engine.mesh import Mesh
from engine.material import Material
from game_objects.object import Object
from utils.imgui_adapter import ImGuiAdapter

from engine.camera import Camera
from engine.world_setting import WorldSetting
from engine.scene_manager import SceneManager
from engine.renderer import Renderer
from game_objects.components.ai_component import CatAIComponent, HamsterAIComponent
import time

# Global variables
scene_manager = None
renderer = None
gui_adapter = None
camera = None
world_setting = None
last_time = 0

# Metrics
last_calc_time = 0
current_sps = 0

def init():
    global scene_manager, renderer, gui_adapter, camera, world_setting, last_time, \
           quad_mesh, wood_material, mouse_material, cat_material, \
           last_calc_time, current_sps
    
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST) # Enable Depth Test for Z-ordering

    # Initialize ImGui
    gui_adapter = ImGuiAdapter(1280, 720)
    
    # Initialize Camera
    camera = Camera(position=(0, 0, 10))
    
    # Initialize World Settings
    world_setting = WorldSetting(5, 5)
    
    # Initialize Scene Manager
    scene_manager = SceneManager()
    renderer = Renderer()


    # Initialize Resources (Shared)
    quad_mesh = Mesh.create_quad()
    mouse_material = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/mouse.png")
    wood_material = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/woodtile.png")
    cat_material = Material("assets/shaders/default.vert", "assets/shaders/default.frag", "assets/textures/cat.png")

    init_world()
    
    last_time = time.time()
    last_calc_time = time.time()

def init_world():
    global scene_manager, world_setting, quad_mesh, wood_material, mouse_material, cat_material
    
    scene_manager.clear()
    
    # Generate Field Tiles
    width, height = world_setting.field_size
    
    tile = Object(name="Floor")
    tile.set_mesh(quad_mesh)
    tile.set_material(wood_material)
    tile.enable_collision_event = False

    tile.transform.scale.SetX(width)
    tile.transform.scale.SetY(height)
    tile.transform.position.SetZ(-0.1)
    tile.uv_scale = (width, height)
    scene_manager.add_object(tile)

    import random
    
    for i in range(world_setting.hamster_count):
        hamster = Object(name=f"Hamster {i}")
        hamster.set_mesh(quad_mesh)
        hamster.set_material(mouse_material)
        
        # Random Position within field bounds
        # Field is centered at 0,0 with size (width, height)
        # Random Range: [-width/2, width/2]
        half_w = width / 2.0
        half_h = height / 2.0
        
        rx = random.uniform(-half_w + 1, half_w - 1)
        ry = random.uniform(-half_h + 1, half_h - 1)
        
        hamster.transform.position.SetX(rx)
        hamster.transform.position.SetY(ry)
        hamster.transform.scale.Set(0.25) 
        hamster.add_component(HamsterAIComponent(world_setting, scene_manager))
        scene_manager.add_object(hamster)
    
    # Cat Object
    cat = Object(name="Cat")
    cat.set_mesh(quad_mesh)
    cat.set_material(cat_material)
    cat.transform.position.SetY(2.0) 
    cat.transform.scale.Set(0.5)
    cat.add_component(CatAIComponent(world_setting, scene_manager))
    scene_manager.add_object(cat)

def reshape(w, h):
    glViewport(0, 0, w, h)
    if gui_adapter:
        gui_adapter.reshape(w, h)

def keyboard(key, x, y):
    if gui_adapter:
        gui_adapter.keyboard(key, x, y)

# Input State
is_dragging = False
last_mouse_pos = (0, 0)

def mouse(button, state, x, y):
    global is_dragging, last_mouse_pos
    
    if gui_adapter:
        gui_adapter.mouse(button, state, x, y)
        if imgui.get_io().want_capture_mouse:
            is_dragging = False
            return

    # Use Right Mouse Button for Panning
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            is_dragging = True
            last_mouse_pos = (x, y)
        elif state == GLUT_UP:
            is_dragging = False

def motion(x, y):
    global is_dragging, last_mouse_pos
    
    if gui_adapter:
        gui_adapter.motion(x, y)
    
    if is_dragging and camera:
        dx = x - last_mouse_pos[0]
        dy = y - last_mouse_pos[1]
        
        viewport = glGetIntegerv(GL_VIEWPORT)
        screen_h = viewport[3] if viewport[3] > 0 else 720
        
        world_scale = camera.ortho_size / screen_h
        
        world_dx = dx * world_scale / camera.zoom
        world_dy = dy * world_scale / camera.zoom
        
        # Move camera OPPOSITE to drag
        new_x = camera.transform.position.X() - world_dx
        new_y = camera.transform.position.Y() + world_dy 
        
        camera.transform.position.SetX(new_x)
        camera.transform.position.SetY(new_y)
        
        last_mouse_pos = (x, y)

def mouse_wheel(wheel, direction, x, y):
    if gui_adapter:
        gui_adapter.scroll(direction)
        if imgui.get_io().want_capture_mouse:
            return

    if camera:
        zoom_speed = 0.5
        new_size = camera.ortho_size - (direction * zoom_speed)
        if new_size < 0.1: new_size = 0.1
        if new_size > 50.0: new_size = 50.0
        
        camera.ortho_size = new_size



def display():
    global last_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Calculate Delta Time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Sync Game Logic (Main Thread)
    if scene_manager:
        scene_manager.tick(dt)
        queue = scene_manager.get_render_queue()
        if renderer:
            renderer.submit_queue(queue)
    
    # Get Camera Matrices
    view = camera.get_view_matrix()
    if gui_adapter:
        projection = camera.get_projection_matrix(gui_adapter.width, gui_adapter.height)
    else:
        projection = camera.get_projection_matrix(1280, 720) # Fallback

    # Render Scene (Main Thread)
    if renderer:
        renderer.render(view, projection)
    
    # Render UI
    if gui_adapter:
        gui_adapter.new_frame()
        
        # Use separated UI module
        from ui.game_ui import render_ui
        reset_req = render_ui(gui_adapter.width, gui_adapter.height, scene_manager, world_setting, renderer)
        
        if reset_req:
            init_world()
        
        gui_adapter.render()
        
    # Debug Render
    if renderer:
        # Re-get matrices if needed, or reuse from above (vars 'view' and 'projection' are available)
        renderer.render_debug(scene_manager, view, projection)
    
    glutSwapBuffers()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitContextVersion(3, 3)
    glutInitContextProfile(GLUT_COMPATIBILITY_PROFILE)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    
    # Updated resolution
    glutInitWindowSize(1280, 720)
    glutCreateWindow(b"ImGui + OpenGL")
    
    init()
    
    # Callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMouseWheelFunc(mouse_wheel)
    glutMotionFunc(motion)
    glutPassiveMotionFunc(motion)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
