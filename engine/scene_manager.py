from engine.spatial_grid import SpatialGrid

class SceneManager:
    def __init__(self):
        self.objects = []
        self.grid = SpatialGrid(cell_size=0.2) 
        self.events = []
        self.logs = []
        self.is_paused = True # Default Paused
        self.aabb_checks = 0
        self.potential_checks = 0

    def add_object(self, obj):
        self.objects.append(obj)

    def tick(self, dt):
        if self.is_paused:
            return

        # Synchronous Tick
        for obj in self.objects:
            obj.tick(dt)
        
        # Collision Detection (Spatial Grid)
        self.check_collisions()
        
        # Process Events
        self.process_events()

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            
    def clear(self):
        self.objects.clear()
        self.events.clear()
        self.logs.clear()
        self.logs.append("World Reset")
        self.is_paused = True

    def check_collisions(self):
        # 1. Rebuild Grid
        self.grid.clear()
        for obj in self.objects:
            if obj.enable_collision_event:
               self.grid.insert(obj)
        
        # 2. Check Collisions
        checked_pairs = set()
        
        # Reset Stats
        self.aabb_checks = 0
        self.potential_checks = 0
        
        for obj_a in self.objects:
            if not obj_a.enable_collision_event:
                continue
            
            # Get nearby candidates
            candidates = self.grid.retrieve(obj_a)
            
            for obj_b in candidates:
                if obj_a == obj_b:
                    continue
                
                # Check duplicate pairs (a,b) vs (b,a)
                # Sort by id to ensure unique key
                if id(obj_a) < id(obj_b):
                    pair = (id(obj_a), id(obj_b))
                else:
                    pair = (id(obj_b), id(obj_a))
                
                if pair in checked_pairs:
                    continue
                
                checked_pairs.add(pair)
                
                if not obj_b.enable_collision_event:
                    continue
                
                self.potential_checks += 1
                
                # Check Sphere then AABB
                if self.check_aabb(obj_a, obj_b):
                    self.events.append({"type": "collision", "obj1": obj_a, "obj2": obj_b})

    def check_aabb(self, a, b):
        # Sphere Check Optimization
        dx = a.transform.position.X() - b.transform.position.X()
        dy = a.transform.position.Y() - b.transform.position.Y()
        dist_sq = dx*dx + dy*dy
        
        rad_sum = a.get_world_radius() + b.get_world_radius()
        if dist_sq > rad_sum * rad_sum:
            return False

        # Actual AABB Check start
        self.aabb_checks += 1

        # AABB Check
        min_a = a.get_world_bounds()[:2]
        max_a = a.get_world_bounds()[2:]

        if min_a[0] > max_a[0] or min_a[1] > max_a[1]:
            return False
        
        bounds_a = a.get_world_bounds()
        bounds_b = b.get_world_bounds()
        
        if (bounds_a[0] < bounds_b[2] and bounds_a[2] > bounds_b[0] and
            bounds_a[1] < bounds_b[3] and bounds_a[3] > bounds_b[1]):
            return True
        return False

    def process_events(self):
        # Synchronous event processing
        current_events = list(self.events)
        self.events.clear()
            
        for event in current_events:
            if event["type"] == "collision":
                obj1 = event["obj1"]
                obj2 = event["obj2"]
                
                # Delegate Collision Logic
                obj1.on_collision(obj2)
                obj2.on_collision(obj1)
                
                # Logging (Skip Hamster-Hamster)
                if "Hamster" in obj1.name and "Hamster" in obj2.name:
                    continue
                    
                # log_msg = f"Collision: {obj1.name} <-> {obj2.name}"
                # if len(self.logs) > 50:
                #    self.logs.pop(0)
                # self.logs.append(log_msg)

    def get_render_queue(self):
        queue = []
        for obj in self.objects:
            data = obj.get_render_data()
            if data:
                queue.append(data)
        return queue
