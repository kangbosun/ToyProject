import imgui
from imgui.integrations.opengl import ProgrammablePipelineRenderer
from OpenGL.GLUT import *
import time

class ImGuiAdapter:
    def __init__(self, window_width, window_height):
        imgui.create_context()
        self.impl = ProgrammablePipelineRenderer()
        self.width = window_width
        self.height = window_height
        self.last_time = time.time()
        
        # Map GLUT keys if necessary (basic implementation)
        io = imgui.get_io()
        io.display_size = (window_width, window_height)

    def reshape(self, width, height):
        self.width = width
        self.height = height
        io = imgui.get_io()
        io.display_size = (width, height)
        self.impl.refresh_font_texture()

    def keyboard(self, key, x, y):
        io = imgui.get_io()
        # Simple ASCII mapping
        if hasattr(key, 'decode'):
            try:
                char = key.decode('utf-8')
                io.add_input_character(char)
            except:
                pass
        
    def mouse(self, button, state, x, y):
        io = imgui.get_io()
        if button == GLUT_LEFT_BUTTON:
            io.mouse_down[0] = (state == GLUT_DOWN)
        elif button == GLUT_RIGHT_BUTTON:
            io.mouse_down[1] = (state == GLUT_DOWN)
        elif button == GLUT_MIDDLE_BUTTON:
            io.mouse_down[2] = (state == GLUT_DOWN)

    def motion(self, x, y):
        io = imgui.get_io()
        io.mouse_pos = (x, y)

    def scroll(self, scroll):
        io = imgui.get_io()
        io.mouse_wheel = scroll

    def new_frame(self):
        io = imgui.get_io()
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        io.delta_time = delta if delta > 0 else 1.0/60.0
        
        imgui.new_frame()

    def render(self):
        imgui.render()
        self.impl.render(imgui.get_draw_data())
