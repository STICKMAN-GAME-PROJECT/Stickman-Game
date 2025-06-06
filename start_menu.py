import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (170, 170, 170)
BLACK = (0, 0, 0)
BUTTON_COLOR = (252, 152, 3)
HOVER_BUTTON_COLOR = (5, 5, 5)
BG = pygame.image.load("Assets/start_screen/start_screen.png")
RUN = True

# Fonts
title_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 60)

# Button class


class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

    def update(self, mouse_pos):
        self.color = BUTTON_COLOR if self.rect.collidepoint(
            mouse_pos) else HOVER_BUTTON_COLOR

# Button callbacks


def nothing():
    print("Nothing")


def audio():
    print("audio")


def controls():
    con_run = True
    width_sc_half = (WIDTH//2)
    center_sc = width_sc_half - (width_sc_half//2)

    while con_run:
        pygame.display.set_caption("Controls Screen")
        bg = pygame.transform.scale(BG, (1000, 600))
        screen.blit(bg, (0, 0))

        title_text = title_font.render(
            "Controls Screen", True, (232, 213, 39))
        screen.blit(title_text, (230, 10))

        image = pygame.transform.scale(pygame.image.load(
            "Assets/Controls_image/controls.png"), (600, 400))
        screen.blit(image, (200, 100))

        buttons = [
            Button("Back", 466 - 100, 510, 200, 60, nothing)
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button == buttons[0]:
                        con_run = False

        for button in buttons:
            button.update(pygame.mouse.get_pos())
            button.draw(screen)

        pygame.display.flip()


def start_game():
    pygame.quit()
    print("Game started!")  # Replace with game loop call
    os.system("python konok_practice.py")
    sys.exit()


def open_options():
    opt_run = True
    width_sc_half = (WIDTH//2)
    center_sc = width_sc_half - (width_sc_half//2)

    while opt_run:
        pygame.display.set_caption("Option Screen")
        bg = pygame.transform.scale(BG, (1000, 600))
        screen.blit(bg, (0, 0))

        title_text = title_font.render(
            "Options Menu", True, (232, 213, 39))
        screen.blit(title_text, (center_sc, 50))

        buttons = [
            Button("Audio", 466 - 100, 330, 200, 60, audio),
            Button("Controls", 466 - 100, 400, 200, 60, controls),
            Button("Back", 466 - 100, 470, 200, 60, nothing),
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button == buttons[2]:
                        opt_run = False
                    else:
                        button.check_click(pygame.mouse.get_pos())

        for button in buttons:
            button.update(pygame.mouse.get_pos())
            button.draw(screen)

        pygame.display.flip()


def quit_game():
    pygame.quit()
    sys.exit()


# Create buttons
buttons = [
    Button("Play", 466 - 100, 330, 200, 60, start_game),
    Button("Options", 466 - 100, 400, 200, 60, open_options),
    Button("Quit", 466 - 100, 470, 200, 60, quit_game)
]


def show_start_screen():

    while RUN:
        bg = pygame.transform.scale(BG, (1000, 600))
        screen.blit(bg, (0, 0))

        # Draw title
        title_text = title_font.render(
            "Stickman Fight 1", True, (232, 213, 39))
        # title_rect = title_text.get_rect(center=(WIDTH//2, 150))
        # screen.blit(title_text, title_rect)
        screen.blit(title_text, (200, 50))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.check_click(mouse_pos)

        for button in buttons:
            button.update(mouse_pos)
            button.draw(screen)

        pygame.display.set_caption("Game Start Screen")
        pygame.display.flip()


# Show the start screen
show_start_screen()
