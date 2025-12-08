import threading
from OpenGL.GL import *
import math

class Renderer:
    def __init__(self):
        self.queues = []
        self.lock = threading.Lock()
        
        # Debug Flags
        self.show_aabb = False
        self.show_sphere = False

    def submit_queue(self, queue):
        with self.lock:
            if len(self.queues) >= 3:
                # Replace the last one
                self.queues[-1] = queue
            else:
                self.queues.append(queue)

    def render(self, view_matrix, proj_matrix):
        """
        Consumes the oldest queue and renders it.
        """
        queue = None
        with self.lock:
            if self.queues:
                queue = self.queues.pop(0)
        
        if not queue:
            return

        for item in queue:
            mesh = item["mesh"]
            material = item["material"]
            model_matrix = item["matrix"]
            uv_scale = item["uv_scale"]
            
            if not mesh or not material:
                continue

            material.use()
            
            # Set Model Matrix
            model_loc = glGetUniformLocation(material.program_id, "model")
            glUniformMatrix4fv(model_loc, 1, GL_TRUE, model_matrix)
            
            # Set View Matrix
            view_loc = glGetUniformLocation(material.program_id, "view")
            glUniformMatrix4fv(view_loc, 1, GL_TRUE, view_matrix)

            # Set Projection Matrix
            proj_loc = glGetUniformLocation(material.program_id, "projection")
            glUniformMatrix4fv(proj_loc, 1, GL_TRUE, proj_matrix)
            
            # Set UV Scale
            uv_scale_loc = glGetUniformLocation(material.program_id, "uvScale")
            if uv_scale_loc != -1:
                glUniform2f(uv_scale_loc, uv_scale[0], uv_scale[1])
            
            mesh.draw()
            
    def render_debug(self, scene_manager, view_matrix, proj_matrix):
        # Always run debug pass for selection highlight
        # if not self.show_aabb and not self.show_sphere:
        #    return
            
        glUseProgram(0) # Fixed function pipeline
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST) # See through objects
        
        # Apply Camera Matrices to Fixed Function Pipeline
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(proj_matrix.transpose())
        
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(view_matrix.transpose())
        
        for obj in scene_manager.objects:
            pos = obj.transform.position
            
            # Draw Sphere (Green)
            if self.show_sphere:
                radius = obj.get_world_radius()
                glColor3f(0.0, 1.0, 0.0)
                glBegin(GL_LINE_LOOP)
                for i in range(16):
                    theta = 2.0 * 3.1415926 * float(i) / 16.0
                    dx = radius * math.cos(theta)
                    dy = radius * math.sin(theta)
                    glVertex3f(pos.X() + dx, pos.Y() + dy, 0.0)
                glEnd()
                
            # Draw AABB (Red)
            if self.show_aabb:
                bounds = obj.get_world_bounds() # min_x, min_y, max_x, max_y
                glColor3f(1.0, 0.0, 0.0)
                glBegin(GL_LINE_LOOP)
                glVertex3f(bounds[0], bounds[1], 0.0)
                glVertex3f(bounds[2], bounds[1], 0.0)
                glVertex3f(bounds[2], bounds[3], 0.0)
                glVertex3f(bounds[0], bounds[3], 0.0)
                glEnd()

            # Draw Selection (Yellow)
            if hasattr(obj, 'is_selected') and obj.is_selected:
                bounds = obj.get_world_bounds()
                glColor3f(1.0, 1.0, 0.0) # Yellow
                glLineWidth(2.0)
                glBegin(GL_LINE_LOOP)
                glVertex3f(bounds[0], bounds[1], 0.0)
                glVertex3f(bounds[2], bounds[1], 0.0)
                glVertex3f(bounds[2], bounds[3], 0.0)
                glVertex3f(bounds[0], bounds[3], 0.0)
                glEnd()
                glLineWidth(1.0)
                
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
