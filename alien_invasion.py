import sys
from time import sleep #allows us to access methods that pause the game when we lose

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()

        self.settings = Settings() #creating an instance of settings

        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN) #sets the game to fullscreen
        self.settings.screen_width = self.screen.get_rect().width 
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion") #Titles the game Alien Invasion

        #Create an instance to store game statistics
        #    and create a scoreboard
        self.stats = GameStats(self) 
        self.sb = Scoreboard(self)

        self.ship = Ship(self) #Create an instance to build the ships
        self.bullets = pygame.sprite.Group() #group the bullets
        self.aliens = pygame.sprite.Group() #group the aliens

        self._create_fleet() #calls the create fleet method to build the fleet of aliens

        #Make the Play button
        self.play_button = Button(self, "Play") #calls the play_button method to show up when the game starts and restarts
        

    def run_game(self): #THIS IS WHAT RUNS THE GAME
        """Start the main loop for the game."""
        while True:
            #Watch for keyboard and mouse events.
            self._check_events()  #this can't be in the if statement because we have to check when the player hits the play button

            if self.stats.game_active: #Meaning if the play button has been selected
                #Updates the positions of the ship, bullets, and aliens
                self.ship.update() #this is what moves the ships when checkevents registers a keydown/keyup events
                self._update_bullets() #UPDATED EVERYTHING ABOUT BULLETS
                self._update_aliens()    #UPDATES EVERYTHING ABOUT ALIENS       
            
            # Redraw the screen during each pass through the loop.
            self._update_screen()

            
            
    def _check_events(self):
        #Respond to keypresses and mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event) #in a separate method
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event) #in a separate method
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos() #makes sure that the click is actually on the play button
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        #Start a new game when the player clicks Play
        button_clicked = self.play_button.rect.collidepoint(mouse_pos) #setting the collide point to be where the play button is and the mouse click
        if button_clicked and not self.stats.game_active: #this runs only if the play button is clicked and the game is inactive
            #Reset the game settings
            self.settings.initialize_dynamic_settings() #Resets the settings that change

            #Reset the game statistics
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score() #resets the score to 0 after the game stats have been reset
            self.sb.prep_level() #resets the level reached
            self.sb.prep_ships() #resets the ships

            #Get rid of remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship() #centers the ship in the middle bottom of the screen

            #Hide the mouse cursor
            pygame.mouse.set_visible(False) 

    
    def _check_keydown_events(self, event):
        # Respond to keypresses
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        # Respond to key releases to stop motion when the key isn't pressed
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        # Create a new bullet and add it to the bullets group
        if len(self.bullets) < self.settings.bullets_allowed: #only allow 3 bullets on the screen at one time
            new_bullet = Bullet(self) #create a new instance of the bullet
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        # Update position of bullets and get rid of old bullets
        #update bullet positions
        self.bullets.update()


        # Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        # Check for any bullets that have hit aliens
        # if so, get rid of the bullet and the alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True) #The first TRUE can be changed to FALSE if you want to keep the bullet active after collision

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points *len(aliens) #assigns points based on alien hit
            self.sb.prep_score() #makes the score change on the screen
            self.sb.check_high_score() #checks if it's a high score and displays the high score

        if not self.aliens: #this checks to see if you've hit all the aliend
            # Destory existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed() #increases the the x and y speed of the aliens, the ship's speed, and the bullet's speed

            #Increase the level
            self.stats.level += 1 #increase the level before drawing it to the screen
            self.sb.prep_level() #makes the level appear on the screen

    def _create_fleet(self):
        # Create the fleet of aliens
        # Create an alien and find the number of aliens in a row
        # Spacing between each alien is equal to one alien width
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size #size is a tuple of width and height
        available_space_x = self.settings.screen_width - (2 * alien_width) #spaces the aliens one alien apart
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2*alien_height)
        
        # Create the full fleet of aliens
        for row_number in range(number_rows): #starts with the first row and moves down
            for alien_number in range(number_aliens_x): #in a specific row creates the aliens across
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number,row_number):
        # Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2*alien_width*alien_number
        alien.rect.x = alien.x #sets the x position of the alien
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number #sets the y position of the alien
        self.aliens.add(alien) #adds the alien to the group

    def _check_fleet_edges(self):
        #Respond appropriately if any aliens have reached an edge
        for alien in self.aliens.sprites():
            if alien.check_edges(): #this function returns true if an alien is at an edge
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        #Drop the entire fleet and change the fleet's direction
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed #want to drop each alien by the drop speed
        self.settings.fleet_direction *= -1 #change the direction just once for every alien
        #because the update method is called, the direction updates when the value is changed to -1

    def _ship_hit(self):
        # Respond to the ship being hit by an alien
        if self.stats.ships_left > 0:
            #Decrement ships_left, and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens or bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)
        
        else: #stops the game and the play button appears because the game is inactive
            self.stats.game_active = False
            pygame.mouse.set_visible(True)


    def _check_aliens_bottom(self):
        # Check if any aliens have reached the bottom of the screen
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Treat this the same as if a ship got hit
                self._ship_hit()
                break
    
    def _update_aliens(self): #THIS UPDATES EVERYTHING ABOUT ALIENS
            #check if the fleet is at an edge.
        #then update the positions of all aliens in the fleet
        self._check_fleet_edges()

        # Update the positions of all the aliens in the fleet
        self.aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()


    def _update_screen(self):
        #Update images on the screen, and flip to the new screen
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme() #draws the ship
        for bullet in self.bullets.sprites():
            bullet.draw_bullet() #settings to draw the bullet
        self.aliens.draw(self.screen) #because this is an image it calls the draw method

        #Draw the score information
        self.sb.show_score()

        #Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible. THIS HAS TO COME LAST
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion() #makes an instance of the game
    ai.run_game() #runs the game