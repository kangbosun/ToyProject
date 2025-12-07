from collections import defaultdict

class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = defaultdict(list)

    def clear(self):
        self.cells.clear()

    def insert(self, obj):
        # Determine cell range using AABB
        bounds = obj.get_world_bounds() # min_x, min_y, max_x, max_y
        
        start_x = int(bounds[0] / self.cell_size)
        start_y = int(bounds[1] / self.cell_size)
        end_x = int(bounds[2] / self.cell_size)
        end_y = int(bounds[3] / self.cell_size)
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                self.cells[(x, y)].append(obj)

    def retrieve(self, obj):
        # Return unique objects in all occupied cells
        found_objects = set()
        
        bounds = obj.get_world_bounds()
        
        start_x = int(bounds[0] / self.cell_size)
        start_y = int(bounds[1] / self.cell_size)
        end_x = int(bounds[2] / self.cell_size)
        end_y = int(bounds[3] / self.cell_size)
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                cell = (x, y)
                if cell in self.cells:
                    found_objects.update(self.cells[cell])
        
        return list(found_objects)
