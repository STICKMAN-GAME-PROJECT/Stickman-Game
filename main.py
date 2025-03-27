import pygame
import Character as c


Clock = pygame.time.Clock()


''''character init section'''

''''--------------------------------'''

'''color section'''
WHITE = (255, 255, 255)
'''---------------------------'''


class PyGame:
    def __init__(self):
        pygame.init()
        self.is_jump = False
        self.HEIGHT, self.WIDTH = 500, 800
        self.x, self.y = 20, 320
        self.height_rect, self.width_rect = 30, 30
        self.speed = 10
        self.jump_right = 10
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        self.value = 0
        self.character_idle = [pygame.image.load(f"Assets/fighter_idle/idle{i}.svg") for i in range(1, 9)]
        self.character_walk = [pygame.image.load(f"Assets/fighter_walk/walk{i}.svg") for i in range(1, 9)]
        self.character_run = [pygame.image.load(f"Assets/fighter_run/run{i}.svg") for i in range(1, 9)]
    def main(self):

        run = True
        pygame.time.delay(100)  # fps

        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            if self.value >= self.character_idle.__len__():
                self.value = 0

            if self.value >= self.character_walk.__len__():
                self.value = 0

            if self.value >= self.character_run.__len__():
                self.value = 0

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:

                if self.x == 0:
                    pass

                else:
                    if keys[pygame.K_RSHIFT] and self.x >= 30:
                        self.x -= 40
                    else:
                        self.walk_left = True
                        self.x -= self.speed
                        self.walk_right = False

            if keys[pygame.K_RIGHT]:
                if self.x == 770:
                    pass
                else:
                    if keys[pygame.K_RSHIFT] and self.x < 740:
                        self.x += 40
                    else:
                        self.walk_right = True
                        self.x += self.speed
                    self.walk_left = False

            if self.is_jump != True:
                if keys[pygame.K_UP]:
                    self.is_jump = True
            else:
                if self.jump_right >= -10:
                    neg = 1
                    if self.jump_right < 0:
                        neg = -1
                    self.y -= (self.jump_right**2)*.3 * neg
                    self.jump_right -= 1
                else:
                    self.is_jump = False
                    self.jump_right = 10

            win.fill(WHITE)


            char_idle = self.character_idle[self.value]
            char_idle = pygame.transform.scale(char_idle, (100, 140))

            char_walk = self.character_walk[self.value]
            char_walk = pygame.transform.scale(char_walk, (100, 140))

            char_run = self.character_run[self.value]
            char_run = pygame.transform.scale(char_run, (100, 140))

            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                if self.walk_left == True:
                    char_idle = pygame.transform.flip(char_idle, True, False)
                win.blit(char_idle, (self.x, self.y))

            elif keys[pygame.K_RSHIFT]==True:
                if keys[pygame.K_LEFT]==True:
                    char_run = pygame.transform.flip(char_run, True, False)
                    win.blit(char_run, (self.x, self.y))
                else:
                    win.blit(char_run, (self.x, self.y))

            else:
                if keys[pygame.K_LEFT]==True:
                    char_walk = pygame.transform.flip(char_walk, True, False)
                    win.blit(char_walk, (self.x, self.y))
                else:
                    win.blit(char_walk, (self.x, self.y))
            

            self.value += 1
            pygame.display.update()
            Clock.tick(10)
        pygame.quit()


if __name__ == "__main__":
    pyg = PyGame()
    pyg.main()
