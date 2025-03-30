import pygame
import Character as c


Clock = pygame.time.Clock()


''''character init section'''

''''--------------------------------'''

'''color section'''
WHITE = (220, 221, 220)
'''---------------------------'''


class PyGame:
    def __init__(self):
        pygame.init()
        self.HEIGHT, self.WIDTH = 500, 800
        self.x, self.y = 20, 320
        self.fixed_y = self.y   # Save base position in different variable. will be used for jumping
        self.height_rect, self.width_rect = 30, 30
        self.speed = 10

        # Things needed for jumping
        self.is_jumping = False  # Set initial jump status to false.
        self.velocity_y = 0      # initial vertical velocity.
        self.gravity = 16        # gravity value (setting high for faster animation).
        self.jump_strength = -80 # how high and strong the jump should be. (affects animation)

        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        self.value = 0
        # it was missing a frame because i ranged it (0, 7), but it had to be (0, 8)/(8)
        self.character_idle_right = [pygame.image.load(
            c.stand_Right[i]) for i in range(8)]
        self.character_walk_right = [pygame.image.load(
            c.walk[i]) for i in range(8)]
        self.character_run_right = [pygame.image.load(
            c.run[i]) for i in range(8)]
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []

    # Initialize and check condition for jumping.
    def jump(self):
        # Check if character is jumping.
        if not self.is_jumping:
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    # Update character position.
    def update(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Check if character is hitting the base position
        if self.y >= self.fixed_y:
            self.y = self.fixed_y
            self.velocity_y = 0
            self.is_jumping = False

    def char_config(self):
        # it was missing a frame because i ranged it (7), but it had to be (8)
        for i in range(8):
            a = pygame.transform.flip(
                self.character_walk_right[i], True, False)
            self.character_walk_left.append(a)
        for i in range(8):
            a = pygame.transform.flip(
                self.character_idle_right[i], True, False)
            self.character_idle_left.append(a)
        for i in range(8):
            a = pygame.transform.flip(self.character_run_right[i], True, False)
            self.character_run_left.append(a)

    def main(self):

        run = True

        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            if self.value >= self.character_idle_right.__len__():
                self.value = 0
            if self.value >= self.character_idle_left.__len__():
                self.value = 0
            if self.value >= self.character_walk_right.__len__():
                self.value = 0
            if self.value >= self.character_walk_left.__len__():
                self.value = 0
            if self.value >= self.character_run_right.__len__():
                self.value = 0
            if self.value >= self.character_run_left.__len__():
                self.value = 0

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:

                if self.x == 0:
                    pass

                else:
                    if keys[pygame.K_RSHIFT] and self.x >= 30:
                        self.x -= 30
                    else:
                        self.walk_left = True
                        self.x -= self.speed
                        self.walk_right = False

            if keys[pygame.K_RIGHT]:
                if self.x == 700:
                    pass
                else:
                    if keys[pygame.K_RSHIFT] and self.x < 690:
                        if self.x == 700:
                            pass
                        else:
                            self.x += 30
                    else:
                        self.walk_right = True
                        self.x += self.speed
                    self.walk_left = False

            # Check for up arrow key.
            if keys[pygame.K_UP]:
                # initiate jumping
                self.jump()


            win.fill(WHITE)
            # pygame.draw.rect(win, (0, 0, 25),
            #                  (self.x, self.y, self.width_rect, self.height_rect))
            # remove the previous rect if the character is set to the window
            char_idle_right = self.character_idle_right[self.value]
            char_idle_right = pygame.transform.scale(
                char_idle_right, (100, 140))

            char_idle_left = self.character_idle_left[self.value]
            char_idle_left = pygame.transform.scale(
                char_idle_left, (100, 140))

            char_walk_right = self.character_walk_right[self.value]
            char_walk_right = pygame.transform.scale(
                char_walk_right, (100, 140))

            char_walk_left = self.character_walk_left[self.value]
            char_walk_left = pygame.transform.scale(char_walk_left, (100, 140))

            char_run_right = self.character_run_right[self.value]
            char_run_right = pygame.transform.scale(char_run_right, (100, 140))

            char_run_left = self.character_run_left[self.value]
            char_run_left = pygame.transform.scale(char_run_left, (100, 140))

            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                win.blit(char_idle_left, (self.x, self.y)) if keys[pygame.K_LEFT] else win.blit(
                    char_idle_right, (self.x, self.y))

            elif keys[pygame.K_RSHIFT] == True:
                win.blit(char_run_right, (self.x, self.y)) if keys[pygame.K_RIGHT] else win.blit(
                    char_run_left, (self.x, self.y))

            else:
                win.blit(char_walk_left, (self.x, self.y)) if keys[pygame.K_LEFT] else win.blit(
                    char_walk_right, (self.x, self.y))

            self.value += 1

            # Update position
            self.update()
            pygame.display.update()
            Clock.tick(14) # 14 fps
        pygame.quit()


if __name__ == "__main__":
    pyg = PyGame()
    pyg.char_config()
    pyg.main()
