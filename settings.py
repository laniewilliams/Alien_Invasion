class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's settings."""
        #Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230,230,230)

        # Ship settings 
        self.ship_limit = 3  # setting it to 2 allows there to be 3 chances for the game since the checking if ships left is > 0 happens after it's been hit by an alien

        # Bullet settings
        self.bullet_width = 3.0
        self.bullet_height = 15
        self.bullet_color = (255,0,0)
        self.bullets_allowed = 3

        # Alien settings
        self.fleet_drop_speed = 7

        #How quickly the game speeds up
        self.speedup_scale = 1.1

        # How quickly the alien point value increases when a new level is reached
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        #Initialize settings that change throughout the game
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0 #how quickly the alien moves right and left

        #fleet direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

        #Scoring
        self.alien_points = 50

    def increase_speed(self):
        #Increase speed settings and alien point values
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale) 
        


