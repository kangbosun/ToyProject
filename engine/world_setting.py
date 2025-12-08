class UnitSetting:
    def __init__(self, speed=2.0):
        self.move_speed = speed
        self.move_duration = 2.0
        self.rest_duration = 2.0
        self.hunger_rate = 5.0
        self.detection_radius = 1.5
        self.mating_search_range = 3.0

class WorldSetting:
    def __init__(self, width=5, height=5):
        self.field_size = (width, height)
        self.cat_setting = UnitSetting(speed=2.5)
        self.cat_setting.move_duration = 3.0
        self.hamster_setting = UnitSetting(speed=2.0)
        self.hamster_count = 15
        self.cat_count = 1
