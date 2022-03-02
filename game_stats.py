class GameStats:
    # Track statistics for Alien invasion

    def __init__(self, ai_game):
        #Initialize the statistics
        self.settings = ai_game.settings
        self.reset_stats()

        # Start Alien Invasion in an inactive state so you have to press PLAY to begin
        self.game_active = False

        #high score should never be reset so it's not in the reset_stats
        self.high_score = 0

    
    def reset_stats(self):
        #Initialize statistics that can change during the game
        # When this is called, these attributes revert to these values
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1