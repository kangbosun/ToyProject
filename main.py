from OpenGL.GL import *
from OpenGL.GLUT import *
import sys
import math
import numpy as np
import imgui
from engine.renderer import Renderer
from engine.world import World
from utils.imgui_adapter import ImGuiAdapter
import time

# Global variables
world = None
renderer = None
gui_adapter = None

# Metrics
last_time = 0
last_calc_time = 0
current_sps = 0

# Input State
mouse_down = False
last_mouse_pos = (0, 0)
current_view_matrix = None
current_proj_matrix = None

def init():
    global world, renderer, gui_adapter, last_time, last_calc_time, current_sps
    
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)

    # Initialize ImGui
    gui_adapter = ImGuiAdapter(1280, 720)
    
    # Initialize World
    world = World(1280, 720)
    world.load_assets()
    world.reset()
    
    renderer = Renderer()

    last_time = time.time()
    last_calc_time = time.time()

def reshape(w, h):
    glViewport(0, 0, w, h)
    if gui_adapter:
        gui_adapter.reshape(w, h)

def keyboard(key, x, y):
    if gui_adapter:
        gui_adapter.keyboard(key, x, y)

def keyboard_up(key, x, y):
    if gui_adapter:
        gui_adapter.keyboard_up(key, x, y)

def special(key, x, y):
    if gui_adapter:
        gui_adapter.special(key, x, y)

def special_up(key, x, y):
    if gui_adapter:
        gui_adapter.special_up(key, x, y)

def mouse(button, state, x, y):
    global last_mouse_pos, mouse_down
    
    if imgui.get_io().want_capture_mouse:
        if gui_adapter:
            gui_adapter.mouse(button, state, x, y)
        return

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            last_mouse_pos = (x, y)
        elif state == GLUT_UP:
            mouse_down = False
            
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
         # Raycast Selection delegate to World
         viewport = glGetIntegerv(GL_VIEWPORT)
         if world:
             world.select_object(x, y, current_view_matrix, current_proj_matrix, viewport)

    if gui_adapter:
        gui_adapter.mouse(button, state, x, y)

def motion(x, y):
    global mouse_down, last_mouse_pos
    
    if gui_adapter:
        gui_adapter.motion(x, y)
    
    if mouse_down and world and world.camera:
        dx = x - last_mouse_pos[0]
        dy = y - last_mouse_pos[1]
        
        viewport = glGetIntegerv(GL_VIEWPORT)
        screen_h = viewport[3] if viewport[3] > 0 else 720
        
        cam = world.camera
        world_scale = cam.ortho_size / screen_h
        
        world_dx = dx * world_scale / cam.zoom
        world_dy = dy * world_scale / cam.zoom
        
        # Move camera OPPOSITE to drag
        new_x = cam.transform.position.X() - world_dx
        new_y = cam.transform.position.Y() + world_dy 
        
        cam.transform.position.SetX(new_x)
        cam.transform.position.SetY(new_y)
        
        last_mouse_pos = (x, y)

def mouse_wheel(wheel, direction, x, y):
    if gui_adapter:
        gui_adapter.scroll(direction)
        if imgui.get_io().want_capture_mouse:
            return

    if world and world.camera:
        cam = world.camera
        zoom_speed = 0.5
        new_size = cam.ortho_size - (direction * zoom_speed)
        if new_size < 0.1: new_size = 0.1
        if new_size > 50.0: new_size = 50.0
        
        cam.ortho_size = new_size

def display():
    global last_time, current_view_matrix, current_proj_matrix
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Calculate Delta Time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Sync Game Logic
    if world:
        world.tick(dt)
        queue = world.scene_manager.get_render_queue()
        if renderer:
            renderer.submit_queue(queue)
    
    # Get Camera Matrices from World
    view = np.identity(4)
    projection = np.identity(4)
    
    if world and world.camera:
        view = world.camera.get_view_matrix()
        if gui_adapter:
             projection = world.camera.get_projection_matrix(gui_adapter.width, gui_adapter.height)
        else:
             projection = world.camera.get_projection_matrix(1280, 720)

    # Store for Selection
    current_view_matrix = view
    current_proj_matrix = projection
    
    # Render Scene
    if renderer:
        renderer.render(view, projection)
    
    # Render UI
    if gui_adapter:
        gui_adapter.new_frame()
        
        from ui.game_ui import render_ui, render_status_bars
        # Pass world components to UI
        reset_req = render_ui(gui_adapter.width, gui_adapter.height, 
                              world.scene_manager if world else None, 
                              world.setting if world else None, 
                              renderer, 
                              world.selected_object if world else None)
        
        # Render Overlays (HP Bars)
        if world:
             viewport = glGetIntegerv(GL_VIEWPORT)
             render_status_bars(world.scene_manager, current_view_matrix, current_proj_matrix, viewport)

        if reset_req and world:
            world.reset()
        
        gui_adapter.render()
        
    # Debug Render
    if renderer and world:
        renderer.render_debug(world.scene_manager, view, projection)
    
    glutSwapBuffers()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitContextVersion(3, 3)
    glutInitContextProfile(GLUT_COMPATIBILITY_PROFILE)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    
    glutInitWindowSize(1280, 720)
    glutCreateWindow(b"ImGui + OpenGL")
    
    init()
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse)
    glutMouseWheelFunc(mouse_wheel)
    glutMotionFunc(motion)
    glutPassiveMotionFunc(motion)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
