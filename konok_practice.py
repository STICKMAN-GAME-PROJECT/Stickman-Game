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
        self.x, self.y = 500, 420  # Start player in the middle of the screen
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
        self.animation_speed = {"idle": 0.15, "walk": 0.15, "run": 0.2}
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
        self.wall = pygame.image.load("Assets/Terrain/wall.png")
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
        self.screen_x = self.WIDTH // 2 - 50  # Center player horizontally
        
        # Fullscreen tracking
        self.fullscreen = False
    
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

    def char_config(self):
        for i in range(8):
            self.character_walk_left.append(pygame.transform.flip(self.character_walk_right[i], True, False))
            self.character_idle_left.append(pygame.transform.flip(self.character_idle_right[i], True, False))
            self.character_run_left.append(pygame.transform.flip(self.character_run_right[i], True, False))

    def draw_background(self, win):
    # Clear screen
        win.fill(WHITE)
        
        # PARALLAX SCROLLING PARAMETERS
        layer_properties = [
            {   # Distant buildings layer (slowest)
                "images": self.buildings,
                "scroll": self.building_scroll,
                "width": self.building_width,
                "speed": 0.3,  # 30% of player movement speed
                "y_pos": 0,
                "scale": 1.0
            },
            {   # Wall layer (medium speed)
                "images": [self.wall],
                "scroll": self.wall_scroll,
                "width": self.wall_width,
                "speed": 0.6,  # 60% of player movement speed
                "y_pos": 320,
                "scale": (self.wall_width, 180)  # Maintain your existing wall scale
            },
            {   # Road layer (fastest)
                "images": [self.road],
                "scroll": self.road_scroll,
                "width": self.road_width,
                "speed": 1.0,  # 100% of player movement speed
                "y_pos": 500,
                "scale": (self.road_width, 100)  # Maintain your existing road scale
            }
        ]

        # DRAW ALL LAYERS
        for layer in layer_properties:
            tiles = math.ceil(self.WIDTH / layer["width"]) + 2
            scroll_offset = layer["scroll"] % layer["width"]
            
            for i in range(-1, tiles):
                pos_x = i * layer["width"] - scroll_offset
                
                # Skip off-screen tiles
                if pos_x < -layer["width"] or pos_x > self.WIDTH:
                    continue
                    
                # Draw each image in the layer
                for img in layer["images"]:
                    # Apply scaling if needed
                    if layer["scale"] != 1.0:
                        if isinstance(layer["scale"], tuple):
                            scaled_img = pygame.transform.scale(img, layer["scale"])
                        else:
                            scaled_img = pygame.transform.scale(img, 
                                (int(img.get_width() * layer["scale"]), 
                                int(img.get_height() * layer["scale"])))
                    else:
                        scaled_img = img
                    
                    win.blit(scaled_img, (pos_x, layer["y_pos"]))
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
                self.building_scroll += int(self.speed * 0.3)
                self.wall_scroll += int(self.speed * 0.6)
                self.road_scroll -= int(self.speed * 0.2)
            elif keys[pygame.K_RIGHT]:
                move_amount = 10 if keys[pygame.K_RSHIFT] else self.speed
                self.walk_right = True
                self.walk_left = False
                self.building_scroll -= int(self.speed * 0.3)
                self.wall_scroll -= int(self.speed * 0.6)
                self.road_scroll += int(self.speed * 0.2)

            # Update world position and scroll values
            self.world_x += move_amount
            self.building_scroll += move_amount * 0.5  # 50% speed
            self.wall_scroll += move_amount * 0.8     # 80% speed
            self.road_scroll += move_amount           # 100% speed

            if keys[pygame.K_UP]:
                self.jump()

            # Drawing
            win.fill(WHITE)
            self.draw_background(win)

            # Animation
            if self.value >= 8:
                self.value = 0

            # Scale character sprites
            char_idle_right = pygame.transform.scale(self.character_idle_right[int(self.value)], (100, 140))
            char_idle_left = pygame.transform.scale(self.character_idle_left[int(self.value)], (100, 140))
            char_walk_right = pygame.transform.scale(self.character_walk_right[int(self.value)], (100, 140))
            char_walk_left = pygame.transform.scale(self.character_walk_left[int(self.value)], (100, 140))
            char_run_right = pygame.transform.scale(self.character_run_right[int(self.value)], (100, 140))
            char_run_left = pygame.transform.scale(self.character_run_left[int(self.value)], (100, 140))

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