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
        
        io = imgui.get_io()
        io.display_size = (window_width, window_height)
        
        # Setup Key Map
        self._setup_key_map(io)

    def _setup_key_map(self, io):
        # We will use ASCII codes for keys_down for simple keys
        # And map special keys to higher indices
        io.key_map[imgui.KEY_TAB] = 9
        io.key_map[imgui.KEY_LEFT_ARROW] = GLUT_KEY_LEFT
        io.key_map[imgui.KEY_RIGHT_ARROW] = GLUT_KEY_RIGHT
        io.key_map[imgui.KEY_UP_ARROW] = GLUT_KEY_UP
        io.key_map[imgui.KEY_DOWN_ARROW] = GLUT_KEY_DOWN
        io.key_map[imgui.KEY_PAGE_UP] = GLUT_KEY_PAGE_UP
        io.key_map[imgui.KEY_PAGE_DOWN] = GLUT_KEY_PAGE_DOWN
        io.key_map[imgui.KEY_HOME] = GLUT_KEY_HOME
        io.key_map[imgui.KEY_END] = GLUT_KEY_END
        io.key_map[imgui.KEY_INSERT] = GLUT_KEY_INSERT
        io.key_map[imgui.KEY_DELETE] = 127
        io.key_map[imgui.KEY_BACKSPACE] = 8
        io.key_map[imgui.KEY_SPACE] = 32
        io.key_map[imgui.KEY_ENTER] = 13
        io.key_map[imgui.KEY_ESCAPE] = 27
        io.key_map[imgui.KEY_A] = 65
        io.key_map[imgui.KEY_C] = 67
        io.key_map[imgui.KEY_V] = 86
        io.key_map[imgui.KEY_X] = 88
        io.key_map[imgui.KEY_Y] = 89
        io.key_map[imgui.KEY_Z] = 90

    def reshape(self, width, height):
        self.width = width
        self.height = height
        io = imgui.get_io()
        io.display_size = (width, height)
        # Check if refresh_font_texture exists in this version of header?
        # self.impl.refresh_font_texture()

    def _update_modifiers(self):
        io = imgui.get_io()
        mods = glutGetModifiers()
        io.key_ctrl = bool(mods & GLUT_ACTIVE_CTRL)
        io.key_shift = bool(mods & GLUT_ACTIVE_SHIFT)
        io.key_alt = bool(mods & GLUT_ACTIVE_ALT)

    def keyboard(self, key, x, y):
        self._update_modifiers()
        io = imgui.get_io()
        if hasattr(key, 'decode'):
            try:
                char = key.decode('utf-8')
                code = ord(char)
                
                # Update Key State
                if code < 512:
                    io.keys_down[code] = True
                
                # Add Input Character (Printable only)
                # Filter out control codes like Backspace (8), Enter (13), Esc (27)
                # because they are keys_down events, not text input.
                if code >= 32: 
                    io.add_input_character(char)
                    # print(f"Input Char Added: {char} (Code: {code})")
            except:
                pass
                
    def keyboard_up(self, key, x, y):
        self._update_modifiers()
        io = imgui.get_io()
        if hasattr(key, 'decode'):
            try:
                char = key.decode('utf-8')
                code = ord(char)
                if code < 512:
                    io.keys_down[code] = False
            except:
                pass
    
    def special(self, key, x, y):
        self._update_modifiers()
        io = imgui.get_io()
        if key < 512:
            io.keys_down[key] = True

    def special_up(self, key, x, y):
        self._update_modifiers()
        io = imgui.get_io()
        if key < 512:
            io.keys_down[key] = False

    def mouse(self, button, state, x, y):
        self._update_modifiers()
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
