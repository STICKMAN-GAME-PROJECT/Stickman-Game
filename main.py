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
        self.HEIGHT, self.WIDTH = 400, 800
        self.x, self.y = 20, 350
        self.height_rect, self.width_rect = 30, 30
        self.speed = 5
        self.jump_right = 10
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

    def main(self):

        run = True
        pygame.time.delay(1000)  # fps

        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                if self.x == 0:
                    pass

                else:
                    if keys[pygame.K_RSHIFT] and self.x >= 30:
                        self.x -= 10
                    else:
                        self.walk_left = True
                        self.x -= self.speed
                        self.walk_right = False
            if keys[pygame.K_RIGHT]:
                if self.x == 770:
                    pass
                else:
                    if keys[pygame.K_RSHIFT] and self.x < 740:
                        self.x += 10
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
            pygame.draw.rect(win, (0, 0, 25),
                             (self.x, self.y, self.width_rect, self.height_rect))
            # remove the previous rect if the character is set to the window
            pygame.display.update()
            Clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    pyg = PyGame()
    pyg.main()
