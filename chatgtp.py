import pygame
import Character as c

# Initialize Pygame clock to control the frame rate
Clock = pygame.time.Clock()

# Define colors
WHITE = (220, 221, 220)

class PyGame:
    def __init__(self):
        pygame.init()
        self.HEIGHT, self.WIDTH = 500, 1200
        self.x, self.y = 20, 320  # Character's initial position
        self.fixed_y = self.y  # Base position, used for jumping mechanics
        self.height_rect, self.width_rect = 30, 30
        self.speed = 10  # Character's walking speed

        # Variables for jumping mechanics
        self.is_jumping = False  # Keeps track of whether the character is in the air
        self.velocity_y = 0  # Vertical speed
        self.gravity = 16  # Gravity value (higher for faster falling)
        self.jump_strength = -80  # Determines how high the character jumps

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        # Animation handling
        self.value = 0  # Current animation frame
        self.animation_speed = {"idle": 0.8, "walk": 0.86, "run": 0.92}  # Different speeds for animations
        self.current_speed = self.animation_speed["idle"]  # Default animation speed
        
        # Load character sprite animations
        self.character_idle_right = [pygame.image.load(c.stand_Right[i]) for i in range(8)]
        self.character_walk_right = [pygame.image.load(c.walk[i]) for i in range(8)]
        self.character_run_right = [pygame.image.load(c.run[i]) for i in range(8)]
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []

    def jump(self):
        """Handles the jumping mechanics."""
        if not self.is_jumping:  # Only jump if the character is on the ground
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def update(self):
        """Updates the character's vertical position based on gravity."""
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Prevent falling below ground level
        if self.y >= self.fixed_y:
            self.y = self.fixed_y
            self.velocity_y = 0
            self.is_jumping = False

    def char_config(self):
        """Creates left-facing versions of character animations by flipping right-facing images."""
        for i in range(8):
            self.character_walk_left.append(pygame.transform.flip(self.character_walk_right[i], True, False))
            self.character_idle_left.append(pygame.transform.flip(self.character_idle_right[i], True, False))
            self.character_run_left.append(pygame.transform.flip(self.character_run_right[i], True, False))

    def main(self):
        """Main game loop."""
        run = True
        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Create game window
        pygame.display.set_caption("Stickman")


        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Allow quitting the game
                    run = False

             # Toggle fullscreen mode when F11 is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

            keys = pygame.key.get_pressed()

            # Adjust animation speed based on movement
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.current_speed = self.animation_speed["walk"]
                if keys[pygame.K_RSHIFT]:  # Running animation speed
                    self.current_speed = self.animation_speed["run"]
            else:
                self.current_speed = self.animation_speed["idle"]

            # Character movement logic
            if keys[pygame.K_LEFT] and self.x > 0:
                self.x -= 26 if keys[pygame.K_RSHIFT] else self.speed
                self.walk_left = True
                self.walk_right = False

            if keys[pygame.K_RIGHT] and self.x < 700:
                self.x += 26 if keys[pygame.K_RSHIFT] else self.speed
                self.walk_right = True
                self.walk_left = False

            if keys[pygame.K_UP]:
                self.jump()

            # Drawing background
            win.fill(WHITE)

            # Reset animation frame if it exceeds limit
            if self.value >= 8:
                self.value = 0

            # Scale character sprites before displaying
            char_idle_right = pygame.transform.scale(self.character_idle_right[int(self.value)], (100, 140))
            char_idle_left = pygame.transform.scale(self.character_idle_left[int(self.value)], (100, 140))
            char_walk_right = pygame.transform.scale(self.character_walk_right[int(self.value)], (100, 140))
            char_walk_left = pygame.transform.scale(self.character_walk_left[int(self.value)], (100, 140))
            char_run_right = pygame.transform.scale(self.character_run_right[int(self.value)], (100, 140))
            char_run_left = pygame.transform.scale(self.character_run_left[int(self.value)], (100, 140))

            # Display the correct animation based on movement
            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                win.blit(char_idle_left if self.walk_left else char_idle_right, (self.x, self.y))
            elif keys[pygame.K_RSHIFT]:
                win.blit(char_run_right if self.walk_right else char_run_left, (self.x, self.y))
            else:
                win.blit(char_walk_left if self.walk_left else char_walk_right, (self.x, self.y))

            # Increment animation frame based on speed
            self.value += self.current_speed
            if self.value >= 8:
                self.value = 0

            self.update()  # Update character's position
            pygame.display.update()  # Refresh display
            Clock.tick(14)  # Control frame rate

        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    pyg.char_config()
    pyg.main()