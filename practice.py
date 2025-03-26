import Character as c
import os
import pygame
pygame.init()


Clock = pygame.time.Clock()


HEIGHT, WIDTH = 400, 800

x, y = 20, 350
speed = 5
is_jump = False  # is the character is jumping
jump_right = 10
walk_left = False
walk_right = False
walk_count = 0
value = 0

# character_walk = pygame.image.load(os.path.join("Assets", "fighter_walk", "walk1.svg"))

character_walk = [pygame.image.load(f"Assets/fighter_walk/walk{i}.svg") for i in range(1, 9)]

# character_walk_right = pygame.transform.scale(character_walk, (512, 512))
# character_walk_left = pygame.transform.flip(character_walk_right, True,  False)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman")

run = True


def draw_BG_gameWindow():
    # win.blit(background_image, (0, 0))
    pass


def Character_walk():
    pass


# char_walk = pygame.rect((70, 300), 70, 100)


def Character_stand():
    pass


while (run):
    pygame.time.delay(60)  # fps

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if value >= len(character_walk):
        value = 0

    keys = pygame.key.get_pressed()
    # if keys[pygame.K_d]:
    #     if x == 770:
    #         pass
    #     else:
    #         x += 10
    if keys[pygame.K_LEFT]:
        if x == 0:
            pass
        # elif (pygame.KMOD_RSHIFT):
        #     x += 10
        else:
            if keys[pygame.K_RSHIFT] and x >= 30:
                x -= 20
            else:
                walk_left = True
                x -= speed
                walk_right = False
    if keys[pygame.K_RIGHT]:
        if x == 770:
            pass
        else:
            if keys[pygame.K_RSHIFT] and x < 740:
                x += 20
            else:
                walk_right = True
                x += speed
            walk_left = False
    if is_jump == False:
        if keys[pygame.K_UP]:
            is_jump = True
    else:
        if jump_right >= -10:
            neg = 1
            if jump_right < 0:
                neg = -1
            y -= (jump_right**2)*.5 * neg
            jump_right -= 1
        else:
            is_jump = False
            jump_right = 10

    win.fill((150, 10, 0))  # remove this after applying the bg
    # pygame.draw.rect(win, (255, 255, 255), (x, y, width_rect, height_rect))
    # remove the previous rect if the character is set to the window

    ch_walk = character_walk[value]
    ch_walk = pygame.transform.scale(ch_walk, (512, 512))  
    win.blit(ch_walk, (0, 0))

    pygame.display.update()
    Clock.tick(60)

    value+=1

draw_BG_gameWindow()
Character_walk()

pygame.quit()
