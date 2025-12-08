from engine.component import Component
import random
import math

class BaseAIComponent(Component):
    def __init__(self, world):
        super().__init__()
        self.world = world
        self.world_setting = world.setting
        self.scene_manager = world.scene_manager
        
        # Copy stats from setting (Decoupling)
        setting = self.get_initial_setting()
        self.move_speed = setting.move_speed if setting else 1.0
        self.move_duration = setting.move_duration if setting else 2.0
        self.rest_duration = setting.rest_duration if setting else 2.0
        
        self.state_timer = 0.0
        self.is_moving = False
        self.direction = (0, 0)
        # Defaults
        self.is_moving = True
        self.state_timer = self.move_duration
        self.randomize_direction()

    def get_initial_setting(self):
        return None 

    # Removed get_speed, get_move_duration etc to use instance vars directly
    
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
                self.state_timer = self.move_duration
                self.randomize_direction()
            else:
                self.state_timer = self.rest_duration
        
        # Move Logic
        if self.is_moving:
            self.move(dt)

    def move(self, dt):
        dx, dy = self.direction
        current_x = self.owner.transform.position.X()
        current_y = self.owner.transform.position.Y()
        speed = self.move_speed
        
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
    def get_initial_setting(self):
        return self.world_setting.cat_setting

    def __init__(self, world):
        super().__init__(world)
        self.satiety = 50.0
        # Cat specific stats
        self.hunger_rate = self.get_initial_setting().hunger_rate if self.get_initial_setting() else 5.0

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
        rate = self.hunger_rate
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
from engine.component import Component
import random
import math

class BaseAIComponent(Component):
    def __init__(self, world):
        super().__init__()
        self.world = world
        self.world_setting = world.setting
        self.scene_manager = world.scene_manager
        
        # Copy stats from setting (Decoupling)
        setting = self.get_initial_setting()
        self.move_speed = setting.move_speed if setting else 1.0
        self.move_duration = setting.move_duration if setting else 2.0
        self.rest_duration = setting.rest_duration if setting else 2.0
        
        self.state_timer = 0.0
        self.is_moving = False
        self.direction = (0, 0)
        # Defaults
        self.is_moving = True
        self.state_timer = self.move_duration
        self.randomize_direction()

    def get_initial_setting(self):
        return None 

    # Removed get_speed, get_move_duration etc to use instance vars directly
    
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
                self.state_timer = self.move_duration
                self.randomize_direction()
            else:
                self.state_timer = self.rest_duration
        
        # Move Logic
        if self.is_moving:
            self.move(dt)

    def move(self, dt):
        dx, dy = self.direction
        current_x = self.owner.transform.position.X()
        current_y = self.owner.transform.position.Y()
        speed = self.move_speed
        
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
    def get_initial_setting(self):
        return self.world_setting.cat_setting

    def __init__(self, world):
        super().__init__(world)
        self.satiety = 50.0
        # Cat specific stats
        self.hunger_rate = self.get_initial_setting().hunger_rate if self.get_initial_setting() else 5.0

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
        rate = self.hunger_rate
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
    def get_initial_setting(self):
        return self.world_setting.hamster_setting
    
    def __init__(self, world):
        super().__init__(world)
        self.detection_radius = self.get_initial_setting().detection_radius if self.get_initial_setting() else 1.5
        
        # Reproduction Stats
        self.gender = random.randint(0, 1) # 0: Male, 1: Female
        self.is_adult = True
        self.growth_timer = 0.0
        self.repro_timer = 0.0
        self.repro_range = self.get_initial_setting().mating_search_range if self.get_initial_setting() else 3.0
        self.scale_ref = 0.25 # Full size scale

    def tick(self, dt):
        # 1. Growth Logic
        if not self.is_adult:
            self.growth_timer += dt
            if self.growth_timer >= 10.0:
                self.is_adult = True
                self.owner.transform.scale.Set(self.scale_ref)
                self.scene_manager.logs.append(f"{self.owner.name} grew up!")
        
        # 2. Cooldown Logic
        if self.repro_timer > 0:
            self.repro_timer -= dt

        # 3. Flee Logic (Highest Priority)
        detecting_cat = False
        if self.scene_manager:
            my_pos = (self.owner.transform.position.X(), self.owner.transform.position.Y())
            detection_range = self.detection_radius
            
            cats = [o for o in self.scene_manager.objects if "Cat" in o.name]
            nearest_cat = None
            min_dist = 9999.0
            
            for cat in cats:
                cx = cat.transform.position.X()
                cy = cat.transform.position.Y()
                dist_sq = (cx - my_pos[0])**2 + (cy - my_pos[1])**2
                
                if dist_sq < detection_range * detection_range:
                    if dist_sq < min_dist:
                        min_dist = dist_sq
                        nearest_cat = cat
                        
            if nearest_cat:
                detecting_cat = True
                cx = nearest_cat.transform.position.X()
                cy = nearest_cat.transform.position.Y()
                dx = my_pos[0] - cx
                dy = my_pos[1] - cy
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0.001:
                     self.direction = (dx/length, dy/length)
                     self.is_moving = True
                     # Reset state timer to keep running for a bit? 
                     # Or just frame-by-frame override? Frame-by-frame is more responsive.
                     
        # 4. Mating Logic (If not fleeing and is adult)
        if not detecting_cat and self.is_adult and self.repro_timer <= 0:
            if self.gender == 0: # Male
                # Search for Waiting Female
                target_female = None
                closest_f_dist = self.repro_range
                
                # Check neighbors or all? All hamsters.
                # Since we accept world, we can filter or use scene_manager
                for obj in self.scene_manager.objects:
                    if "Hamster" in obj.name and obj != self.owner:
                        comp = obj.get_component(HamsterAIComponent)
                        if comp and comp.gender == 1 and comp.is_adult and comp.repro_timer <= 0:
                             # Found ready female
                             fx = obj.transform.position.X()
                             fy = obj.transform.position.Y()
                             dist = math.sqrt((fx - my_pos[0])**2 + (fy - my_pos[1])**2)
                             if dist < closest_f_dist:
                                 closest_f_dist = dist
                                 target_female = obj
                
                if target_female:
                    # Move towards her
                    tx = target_female.transform.position.X()
                    ty = target_female.transform.position.Y()
                    dx = tx - my_pos[0]
                    dy = ty - my_pos[1]
                    l = math.sqrt(dx*dx + dy*dy)
                    if l > 0.001:
                        self.direction = (dx/l, dy/l)
                        self.is_moving = True
            
            else: # Female
                 # Stop and Wait
                 self.is_moving = False
        
        super().tick(dt)

    def on_collision(self, other):
        # Mating Contact
        if self.gender == 0 and "Hamster" in other.name: # Male logic driver
            comp = other.get_component(HamsterAIComponent)
            if comp and comp.gender == 1: # Female
                # Check availability
                if self.is_adult and self.repro_timer <= 0 and comp.is_adult and comp.repro_timer <= 0:
                    # Reproduce
                    self.repro_timer = 10.0
                    comp.repro_timer = 10.0
                    
                    # Spawn Baby at Female's location
                    sx = other.transform.position.X()
                    sy = other.transform.position.Y()
                    self.world.spawn_hamster(sx, sy, is_baby=True)
                    self.scene_manager.logs.append("New baby born!")
