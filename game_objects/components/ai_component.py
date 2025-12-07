from engine.component import Component
import random
import math

class BaseAIComponent(Component):
    def __init__(self, world_setting, scene_manager=None):
        super().__init__()
        self.world_setting = world_setting
        self.scene_manager = scene_manager
        self.state_timer = 0.0
        self.is_moving = False
        self.direction = (0, 0)
        # Defaults
        self.is_moving = True
        self.state_timer = self.get_move_duration()
        self.randomize_direction()

    def get_setting(self):
        return None 

    def get_speed(self):
        s = self.get_setting()
        return s.move_speed if s else 1.0

    def get_move_duration(self):
        s = self.get_setting()
        return s.move_duration if s else 2.0

    def get_rest_duration(self):
        s = self.get_setting()
        return s.rest_duration if s else 2.0

    def randomize_direction(self):
        angle = random.uniform(0, 6.28318)
        self.direction = (math.cos(angle), math.sin(angle))

    def tick(self, dt):
        if not self.owner:
            return
            
        self.state_timer -= dt
        
        # State Transition
        if self.state_timer <= 0:
            self.is_moving = not self.is_moving
            if self.is_moving:
                self.state_timer = self.get_move_duration()
                self.randomize_direction()
            else:
                self.state_timer = self.get_rest_duration()
        
        # Move Logic
        if self.is_moving:
            self.move(dt)

    def move(self, dt):
        dx, dy = self.direction
        current_x = self.owner.transform.position.X()
        current_y = self.owner.transform.position.Y()
        speed = self.get_speed()
        
        step_x = dx * speed * dt
        step_y = dy * speed * dt
        
        # Apply Move
        self.owner.transform.position.SetX(current_x + step_x)
        self.owner.transform.position.SetY(current_y + step_y)
        
        # Boundary Check
        self.check_boundary(current_x, current_y, dx, dy, speed, dt)

    def check_boundary(self, old_x, old_y, dx, dy, speed, dt):
        min_x, min_y, max_x, max_y = self.owner.get_world_bounds()
        field_w, field_h = self.world_setting.field_size
        half_w = field_w / 2.0
        half_h = field_h / 2.0
        
        collision = False
        if min_x < -half_w or max_x > half_w:
            self.direction = (-dx, dy)
            collision = True
        if min_y < -half_h or max_y > half_h:
            # Re-fetch in case X flip changed it
            cdx, cdy = self.direction
            self.direction = (cdx, -dy)
            collision = True
            
        if collision:
            self.owner.transform.position.SetX(old_x)
            self.owner.transform.position.SetY(old_y)
            # Step with new direction
            ndx, ndy = self.direction
            self.owner.transform.position.SetX(old_x + ndx * speed * dt)
            self.owner.transform.position.SetY(old_y + ndy * speed * dt)

class CatAIComponent(BaseAIComponent):
    def __init__(self, world_setting, scene_manager=None):
        super().__init__(world_setting, scene_manager)
        self.satiety = 50.0

    def get_setting(self):
        return self.world_setting.cat_setting

    def feed(self, amount):
        self.satiety += amount
        if self.satiety > 100.0:
            self.satiety = 100.0

    def on_collision(self, other):
        if "Hamster" in other.name:
            if self.satiety < 90.0:
                self.feed(25.0)
                self.scene_manager.logs.append(f"{self.owner.name} ate {other.name}!")
                self.scene_manager.remove_object(other)
            #else:
                #self.scene_manager.logs.append(f"{self.owner.name} is full (Satiety: {self.satiety:.1f}) and ignored {other.name}")
        
    def tick(self, dt):
        # Hunger Logic
        rate = self.get_setting().hunger_rate
        self.satiety -= rate * dt
        if self.satiety < 0: 
            self.satiety = 0
            # Starvation Death
            self.scene_manager.logs.append(f"{self.owner.name} starved to death!")
            self.scene_manager.remove_object(self.owner)
            return
        
        # Behavior Check
        if self.satiety >= 60.0:
            # Satiated - Stop hunting/moving
            self.is_moving = False
            # self.state_timer is for switching logic, we can leave it or pause it.
            # To ensure it resumes, we can just return early or force is_moving=False
            return
            
        super().tick(dt)
        
    def move(self, dt):
        # Chase Logic override
        # Find nearest Hamster
        if self.scene_manager:
            target = None
            min_dist = 9999.0
            
            my_pos = (self.owner.transform.position.X(), self.owner.transform.position.Y())
            
            for obj in self.scene_manager.objects:
                if "Hamster" in obj.name:
                    ox = obj.transform.position.X()
                    oy = obj.transform.position.Y()
                    dist = math.sqrt((ox - my_pos[0])**2 + (oy - my_pos[1])**2)
                    if dist < min_dist:
                        min_dist = dist
                        target = obj
            
            if target:
                # Update direction towards target
                tx = target.transform.position.X()
                ty = target.transform.position.Y()
                
                dir_x = tx - my_pos[0]
                dir_y = ty - my_pos[1]
                length = math.sqrt(dir_x**2 + dir_y**2)
                
                if length > 0:
                    self.direction = (dir_x/length, dir_y/length)
        
        # Call base move (which handles actual position update and bounds)
        # But base move uses self.direction which we just updated
        super().move(dt)

class HamsterAIComponent(BaseAIComponent):
    def get_setting(self):
        return self.world_setting.hamster_setting

    def tick(self, dt):
        # Flee Logic
        if self.scene_manager:
            my_pos = (self.owner.transform.position.X(), self.owner.transform.position.Y())
            detection_range = self.get_setting().detection_radius
            
            # Find nearest Cat
            nearest_cat = None
            min_dist = 9999.0
            
            # Optimization: Use Grid if possible, but Cat might be anywhere. 
            # Given low count of Cats (usually 1), iteration is fine.
            # But we can query grid for nearby objects if we tagged them.
            # For now, simple iteration over objects to find "Cat" is reasonably fast for 100 objs.
            # (Or iterate ALL objects is O(N), but we scan for specific name)
            
            # Better: SceneManager could cache 'cats' list. 
            # But let's stick to iteration for simplicity or Grid retrieval.
            
            # Let's use Grid properly: Retrieve neighbors. 
            # If Cat is not in neighbor cells, it's far enough (assuming cell size ~ detection range).
            # Grid cell size is 0.2, detection 1.5 -> ~7 cells away. Grid retrieval only gets immediate neighbors.
            # So Grid retrieve is NOT sufficient for 1.5 range with 0.2 cells.
            # Fallback to global list for Cats (since there are few).
            
            cats = [o for o in self.scene_manager.objects if "Cat" in o.name]
            
            for cat in cats:
                cx = cat.transform.position.X()
                cy = cat.transform.position.Y()
                dist_sq = (cx - my_pos[0])**2 + (cy - my_pos[1])**2
                
                if dist_sq < detection_range * detection_range:
                    if dist_sq < min_dist:
                        min_dist = dist_sq
                        nearest_cat = cat

            if nearest_cat:
                # RUN AWAY!
                cx = nearest_cat.transform.position.X()
                cy = nearest_cat.transform.position.Y()
                
                dx = my_pos[0] - cx
                dy = my_pos[1] - cy
                
                # Normalize
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0.001:
                     self.direction = (dx/length, dy/length)
                     self.is_moving = True
                     # Reset state timer to keep running for a bit? 
                     # Or just frame-by-frame override? Frame-by-frame is more responsive.
                     
        super().tick(dt)
