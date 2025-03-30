import pygame
import Character as c
import math

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
        self.x, self.y = 20, 340
        self.speed = 10
        self.jump_right = 10
        self.walk_left = False
        self.walk_right = False
        self.walk_count = 0

        self.scroll = 0  # Added scroll as an instance variable
        self.camera_x = 0  # Camera position

        self.value = 0
        self.character_idle = [pygame.image.load(f"Assets/fighter_idle/idle{i}.svg") for i in range(1, 9)]
        self.character_walk = [pygame.image.load(f"Assets/fighter_walk/walk{i}.svg") for i in range(1, 9)]
        self.character_run = [pygame.image.load(f"Assets/fighter_run/run{i}.svg") for i in range(1, 9)]

        #load roads & backgrounds
        self.road = pygame.image.load("Assets/roads/road.png")
        self.wall = pygame.image.load("Assets/roads/wall.png")
        self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]
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

                if self.x == 20:
                    pass

                else:
                    if keys[pygame.K_RSHIFT] and self.x >= 30:
                        self.x -= 40
                    else:
                        self.walk_left = True
                        self.camera_x -= self.speed  # Move camera left
                        self.scroll += self.speed  # Move road right
                        self.x -= self.speed
                        self.walk_right = False

            if keys[pygame.K_RIGHT]:
                if self.x == 7700:
                    pass
                else:
                    if keys[pygame.K_RSHIFT] and self.x < 740:
                        self.x += 40
                        self.camera_x += 40  # Move camera right
                        self.scroll -= 10  # Move road left
                    else:
                        self.walk_right = True
                        self.x += self.speed
                        self.camera_x += self.speed  # Move camera right
                        self.scroll -= self.speed  # Move road left
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


            # Scrolling buildings
            building_width = self.buildings[0].get_width()
            tiles = math.ceil(self.WIDTH / building_width)

            for i in range(tiles):
                win.blit(self.buildings[0], (i * building_width + self.scroll - self.camera_x, 0))
                win.blit(self.buildings[1], (i * building_width + self.scroll - self.camera_x, 0))
                win.blit(self.buildings[2], (i * building_width + self.scroll - self.camera_x, 0))
                win.blit(self.buildings[3], (i * building_width + self.scroll - self.camera_x, 0))
                win.blit(self.buildings[4], (i * building_width + self.scroll - self.camera_x, 0))


            # Scrolling wall
            wall_width = self.wall.get_width()
            tiles = math.ceil(self.WIDTH / wall_width)

            self.wall = pygame.transform.scale(self.wall, (2000, 200))

            for i in range(tiles):
                win.blit(self.wall, (i * wall_width + self.scroll - self.camera_x, 260))

            # Scrolling road
            road_width = self.road.get_width()
            tiles = math.ceil(self.WIDTH / road_width)

            self.road = pygame.transform.scale(self.road, (2000, 60))

            for i in range(tiles):
                win.blit(self.road, (i * road_width + self.scroll - self.camera_x, 440))


            # Reset scroll to prevent overflow
            if self.scroll > road_width:
                self.scroll = 0
            elif self.scroll < -road_width:
                self.scroll = 0


            # Adjust player position relative to camera
            player_screen_x = 20 


            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                if self.walk_left == True:
                    char_idle = pygame.transform.flip(char_idle, True, False)
                win.blit(char_idle, (player_screen_x, self.y))

            elif keys[pygame.K_RSHIFT]==True:
                if keys[pygame.K_LEFT]==True:
                    char_run = pygame.transform.flip(char_run, True, False)
                    win.blit(char_run, (player_screen_x, self.y))
                else:
                    win.blit(char_run, (player_screen_x, self.y))

            else:
                if keys[pygame.K_LEFT]==True:
                    char_walk = pygame.transform.flip(char_walk, True, False)
                    win.blit(char_walk, (player_screen_x, self.y))
                else:
                    win.blit(char_walk, (player_screen_x, self.y))
            

            self.value += 1
            pygame.display.update()
            Clock.tick(10)
        pygame.quit()


if __name__ == "__main__":
    pyg = PyGame()
    pyg.main()
