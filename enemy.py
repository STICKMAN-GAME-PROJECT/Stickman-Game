import pygame
import Character as c

class Enemy:
    def __init__(self, world_x):
        self.world_x = world_x  # Enemy's position in the world
        self.width = 400
        self.height = 400
        self.y = 250  # Place enemies on the ground
        self.sprite_size = (self.width, self.height)

        # Load enemy sprites (same as player)
        self.idle_right = [pygame.image.load(c.stand_Right[i]) for i in range(8)]
        self.walk_right = [pygame.image.load(c.walk[i]) for i in range(8)]
        self.run_right = [pygame.image.load(c.run[i]) for i in range(8)]
        self.idle_left = []
        self.walk_left = []
        self.run_left = []

        # Scale and tint sprites
        self._scale_and_tint_sprites()

        # Animation state (for future use)
        self.current_sprite = self.idle_right[0]  # Start with idle right, frame 0

    def _scale_and_tint_sprites(self):
        # Scale all sprites to 50x50
        self.idle_right = [pygame.transform.scale(sprite, self.sprite_size) for sprite in self.idle_right]
        self.walk_right = [pygame.transform.scale(sprite, self.sprite_size) for sprite in self.walk_right]
        self.run_right = [pygame.transform.scale(sprite, self.sprite_size) for sprite in self.run_right]

        # Create left-facing sprites
        for i in range(8):
            self.idle_left.append(pygame.transform.flip(self.idle_right[i], True, False))
            self.walk_left.append(pygame.transform.flip(self.walk_right[i], True, False))
            self.run_left.append(pygame.transform.flip(self.run_right[i], True, False))

        # Apply red tint to all sprites
        self.idle_right = [self._apply_red_tint(sprite) for sprite in self.idle_right]
        self.idle_left = [self._apply_red_tint(sprite) for sprite in self.idle_left]
        self.walk_right = [self._apply_red_tint(sprite) for sprite in self.walk_right]
        self.walk_left = [self._apply_red_tint(sprite) for sprite in self.walk_left]
        self.run_right = [self._apply_red_tint(sprite) for sprite in self.run_right]
        self.run_left = [self._apply_red_tint(sprite) for sprite in self.run_left]

    def _apply_red_tint(self, sprite):
        # Create a red surface with alpha to control tint intensity
        red_tint = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        red_tint.fill((255, 0, 0))  # Red with 50% opacity for blending

        # Copy the original sprite
        tinted_sprite = sprite.copy()
        # Blend the red tint onto the sprite
        tinted_sprite.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_sprite

    def draw(self, win, scroll_offset):
        # Calculate enemy's screen position
        enemy_screen_x = self.world_x - scroll_offset
        # Draw only if enemy is on screen
        if -self.width <= enemy_screen_x <= win.get_width():
            win.blit(self.current_sprite, (enemy_screen_x, self.y))