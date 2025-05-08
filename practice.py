import pygame
import Character as c
import math


# Initialize Pygame clock to control the frame rate
Clock = pygame.time.Clock()

# Define colors
WHITE = (220, 221, 220)

class PyGame:
    def __init__(self):
        pygame.init()
        self.HEIGHT, self.WIDTH = 600, 1000
        self.x, self.y = 500, 180  # Start player in the middle of the screen
        self.fixed_y = self.y
        self.height_rect, self.width_rect = 30, 30
        self.speed = 4

        # Jumping mechanics
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -12

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        # Animation handling
        self.value = 0
        self.animation_speed = {"idle": 0.23, "walk": 0.23, "run": 0.4}
        self.current_speed = self.animation_speed["idle"]
        
        # Character animations
        self.character_idle_right = [pygame.image.load(c.stand_Right[i]) for i in range(8)]
        self.character_walk_right = [pygame.image.load(c.walk[i]) for i in range(8)]
        self.character_run_right = [pygame.image.load(c.run[i]) for i in range(8)]
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []
        
        # Environment assets
        self.road = pygame.image.load("Assets/Terrain/road.png")
        self.wall = pygame.image.load("Assets/Terrain/wallr.png")
        self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]

        # Background dimensions
        self.building_width = self.buildings[0].get_width()
        self.road_width = self.road.get_width()
        self.wall_width = self.wall.get_width()
        
        # Scroll positions
        self.building_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0
        
        # Player's world position
        self.world_x = self.x
        self.screen_x = self.WIDTH // 2  # Center player horizontally
        self.player_width = 500  # Store player width for boundary checks
        
        # Fullscreen tracking
        self.fullscreen = False
        self.enemy_exists = False
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def update(self, dt):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y

        if self.y >= self.fixed_y:
            self.y = self.fixed_y
            self.velocity_y = 0
            self.is_jumping = False

        if self.enemy_exists:
            # Clamp player position to keep entire sprite on screen
            self.world_x = max(0, min(self.world_x, self.WIDTH - self.player_width))

    def char_config(self):
        for i in range(8):
            self.character_walk_left.append(pygame.transform.flip(self.character_walk_right[i], True, False))
            self.character_idle_left.append(pygame.transform.flip(self.character_idle_right[i], True, False))
            self.character_run_left.append(pygame.transform.flip(self.character_run_right[i], True, False))

    def draw_background(self, win):
        # Buildings (farthest layer)
        building_tiles = math.ceil(self.WIDTH / self.building_width) + 3  # +2 for safety
        for i in range(-1, building_tiles):
            scroll_amount = self.building_scroll % self.building_width
            pos_x = i * self.building_width - scroll_amount
            if pos_x < -self.building_width:  # Skip tiles that are completely off-screen left
                continue
            if pos_x > self.WIDTH:  # Skip tiles that are completely off-screen right
                continue
            for b in self.buildings:
                win.blit(b, (pos_x, 0))

        # Wall (middle layer)
        wall_tiles = math.ceil(self.WIDTH / self.wall_width) + 2
        for i in range(-1, wall_tiles):
            scroll_amount = self.wall_scroll % self.wall_width
            pos_x = i * self.wall_width - scroll_amount
            if -self.wall_width <= pos_x <= self.WIDTH:
                wall = pygame.transform.scale(self.wall, (self.wall_width, 180))
                win.blit(wall, (pos_x, 320))

        # Road (closest layer)
        road_tiles = math.ceil(self.WIDTH / self.road_width) + 2
        for i in range(-1, road_tiles):
            scroll_amount = self.road_scroll % self.road_width
            pos_x = i * self.road_width - scroll_amount
            if -self.road_width <= pos_x <= self.WIDTH:
                road = pygame.transform.scale(self.road, (self.road_width, 100))
                win.blit(road, (pos_x, 500))

    def main(self):
        run = True
        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            dt = Clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()

            keys = pygame.key.get_pressed()

            # Animation speed
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.current_speed = self.animation_speed["walk"]
                if keys[pygame.K_RSHIFT]:
                    self.current_speed = self.animation_speed["run"]
            else:
                self.current_speed = self.animation_speed["idle"]

            # Movement logic
            move_amount = 0
            if keys[pygame.K_LEFT]:
                move_amount = -(10 if keys[pygame.K_RSHIFT] else self.speed)
                self.walk_left = True
                self.walk_right = False
            elif keys[pygame.K_RIGHT]:
                move_amount = 10 if keys[pygame.K_RSHIFT] else self.speed
                self.walk_right = True
                self.walk_left = False

            # Update world position and scroll values
            self.world_x += move_amount

            # Check if an enemy exists
            if self.enemy_exists:
                # Update screen_x to match world_x (player moves on screen)
                self.screen_x = self.world_x  
            else:
                # Normal scrolling behavior (player stays centered)
                self.screen_x = self.WIDTH // 2 - self.player_width // 2  # True center  
                self.building_scroll += move_amount * 0.3  
                self.wall_scroll += move_amount * 0.65  
                self.road_scroll += move_amount  

            #enemy tigger toggle
            if keys[pygame.K_TAB]:
                self.enemy_exists = not self.enemy_exists
                if self.enemy_exists:
                    self.world_x = self.screen_x


            if keys[pygame.K_UP]:
                self.jump()

            # Drawing
            win.fill(WHITE)
            self.draw_background(win)

            # Animation
            if self.value >= 8:
                self.value = 0

            # Scale character sprites
            char_idle_right = pygame.transform.scale(self.character_idle_right[int(self.value)], (500, 500))
            char_idle_left = pygame.transform.scale(self.character_idle_left[int(self.value)], (500, 500))
            char_walk_right = pygame.transform.scale(self.character_walk_right[int(self.value)], (500, 500))
            char_walk_left = pygame.transform.scale(self.character_walk_left[int(self.value)], (500, 500))
            char_run_right = pygame.transform.scale(self.character_run_right[int(self.value)], (500, 500))
            char_run_left = pygame.transform.scale(self.character_run_left[int(self.value)], (500, 500))

            # Display animation
            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                win.blit(char_idle_left if self.walk_left else char_idle_right, (self.screen_x, self.y))
            elif keys[pygame.K_RSHIFT]:
                win.blit(char_run_right if self.walk_right else char_run_left, (self.screen_x, self.y))
            else:
                win.blit(char_walk_left if self.walk_left else char_walk_right, (self.screen_x, self.y))

            self.value += self.current_speed
            self.update(dt)
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    pyg.char_config()
    pyg.main()