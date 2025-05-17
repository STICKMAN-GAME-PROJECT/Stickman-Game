import pygame
import Character as c

class Enemy:
    def __init__(self, world_x):
        self.initial_x = world_x  # Store initial position as patrol center
        self.world_x = world_x  # Enemy's current position in the world
        self.width = 400
        self.height = 400
        self.y = 250
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

        # Animation and movement state
        self.value = 0
        self.current_speed = 0.23  # Animation speed
        self.facing_right = True  # Direction flag (not sprite list)
        self.facing_left = False  # Direction flag
        self.moving = False  # Track if enemy is moving
        self.speed = 2  # Movement speed (units per frame)
        self.direction = 1  # 1 for right, -1 for left
        self.patrol_range = 100  # Half the patrol range

    def _scale_and_tint_sprites(self):
        # Scale all sprites to 400x400
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
        red_tint = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        red_tint.fill((255, 0, 0))  # Red with 50% opacity
        tinted_sprite = sprite.copy()
        tinted_sprite.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_sprite

    def update_animation(self):
        self.value += self.current_speed
        if self.value >= 8:
            self.value -= 8

    def update_movement(self):
        # Patrol within range (initial_x - patrol_range to initial_x + patrol_range)
        min_x = self.initial_x - self.patrol_range
        max_x = self.initial_x + self.patrol_range

        self.world_x += self.speed * self.direction
        if self.world_x <= min_x or self.world_x >= max_x:
            self.direction *= -1  # Reverse direction
            self.world_x = max(min_x, min(max_x, self.world_x))  # Clamp position

        # Update moving state and facing
        self.moving = abs(self.world_x - self.initial_x) > 1  # Consider moving if outside a small threshold
        if self.direction == 1:
            self.facing_right = True
            self.facing_left = False
        else:
            self.facing_left = True
            self.facing_right = False

    def draw(self, win, scroll_offset, player_walk_left, player_walk_right):
        # Calculate enemy's screen position
        enemy_screen_x = self.world_x - scroll_offset
        if -self.width <= enemy_screen_x <= win.get_width():
            # Set facing direction based on patrol direction only
            if self.direction == 1:
                self.facing_right = True
                self.facing_left = False
            else:
                self.facing_left = True
                self.facing_right = False

            # Select sprite based on movement state
            frame = int(self.value)
            if self.moving:
                self.current_sprite = self.walk_left[frame] if self.facing_left else self.walk_right[frame]
            else:
                self.current_sprite = self.idle_left[frame] if self.facing_left else self.idle_right[frame]
            win.blit(self.current_sprite, (enemy_screen_x, self.y))