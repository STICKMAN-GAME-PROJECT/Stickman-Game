import pygame
import Character as c
import math

Clock = pygame.time.Clock()

# Color constants
WHITE = (255, 255, 255)

class PyGame:
    def __init__(self):
        pygame.init()
        self.is_jump = False
        self.HEIGHT, self.WIDTH = 500, 800
        self.x, self.y = 20, 340
        self.speed = 10
        self.jump_right = 10
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        self.scroll = 0  
        self.camera_x = 0  

        self.value = 0
        self.combo_index = 0  # Separate index for combo animation
        self.combo_playing = False  # Track combo animation state

        # Load character animations
        self.character_idle = [pygame.image.load(f"Assets/fighter_idle/idle{i}.svg") for i in range(1, 9)]
        self.character_walk = [pygame.image.load(f"Assets/fighter_walk/walk{i}.svg") for i in range(1, 9)]
        self.character_run = [pygame.image.load(f"Assets/fighter_run/run{i}.svg") for i in range(1, 9)]
        self.combo = [pygame.image.load(f"Assets/fighter_combo/combo_{i}.svg") for i in range(1, 20)]

        # Load environment assets
        self.road = pygame.image.load("Assets/Terrain/road.png")
        self.wall = pygame.image.load("Assets/Terrain/wall.png")
        self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]

    def main(self):
        run = True
        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            # Movement logic
            if keys[pygame.K_LEFT]:
                if self.x > 20:
                    if keys[pygame.K_RSHIFT] and self.x >= 30:
                        self.x -= 40
                    else:
                        self.walk_left = True
                        self.camera_x -= self.speed
                        self.scroll += self.speed
                        self.x -= self.speed
                        self.walk_right = False

            if keys[pygame.K_RIGHT]:
                if self.x < 7700:
                    if keys[pygame.K_RSHIFT] and self.x < 740:
                        self.x += 40
                        self.camera_x += 40
                        self.scroll -= 10
                    else:
                        self.walk_right = True
                        self.x += self.speed
                        self.camera_x += self.speed
                        self.scroll -= self.speed
                    self.walk_left = False

            # Jump logic
            if not self.is_jump:
                if keys[pygame.K_UP]:
                    self.is_jump = True
            else:
                if self.jump_right >= -10:
                    neg = 1 if self.jump_right >= 0 else -1
                    self.y -= (self.jump_right**2) * 0.3 * neg
                    self.jump_right -= 1
                else:
                    self.is_jump = False
                    self.jump_right = 10

            win.fill(WHITE)

            # Load and scale animations
            char_idle = pygame.transform.scale(self.character_idle[self.value], (100, 140))
            char_walk = pygame.transform.scale(self.character_walk[self.value], (100, 140))
            char_run = pygame.transform.scale(self.character_run[self.value], (100, 140))
            char_combo = pygame.transform.scale(self.combo[self.combo_index], (100, 140))

            # Scrolling background
            building_width = self.buildings[0].get_width()
            tiles = math.ceil(self.WIDTH / building_width)

            for i in range(tiles):
                for b in self.buildings:
                    win.blit(b, (i * building_width + self.scroll - self.camera_x, 0))

            # Scrolling wall
            wall_width = self.wall.get_width()
            self.wall = pygame.transform.scale(self.wall, (2000, 200))
            for i in range(math.ceil(self.WIDTH / wall_width)):
                win.blit(self.wall, (i * wall_width + self.scroll - self.camera_x, 260))

            # Scrolling road
            road_width = self.road.get_width()
            self.road = pygame.transform.scale(self.road, (2000, 60))
            for i in range(math.ceil(self.WIDTH / road_width)):
                win.blit(self.road, (i * road_width + self.scroll - self.camera_x, 440))

            # Reset scroll overflow
            if abs(self.scroll) > road_width:
                self.scroll = 0

            # Player position relative to screen
            player_screen_x = 20

            # Handle combo animation
            if keys[pygame.K_KP_0]:  
                self.combo_playing = True  # Start playing combo

            if self.combo_playing:
                char_sprite = char_combo
                if self.combo_index < len(self.combo) - 1:
                    self.combo_index += 1  # Play next frame
                else:
                    self.combo_playing = False  # Stop when last frame reached
                    self.combo_index = 0  # Reset for next use
            else:
                # Regular animations when combo isn't playing
                if keys[pygame.K_RSHIFT]:  
                    char_sprite = char_run
                elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:  
                    char_sprite = char_walk
                else:  
                    char_sprite = char_idle


            if keys[pygame.K_LEFT]:
                char_sprite = pygame.transform.flip(char_sprite, True, False)

            # Draw character
            win.blit(char_sprite, (player_screen_x, self.y))


            if not self.combo_playing:
                self.value = (self.value + 1) % len(self.character_idle)

            pygame.display.update()
            Clock.tick(10)  # Adjust FPS
        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    pyg.main()