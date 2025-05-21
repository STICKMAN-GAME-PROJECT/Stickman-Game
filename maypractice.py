import pygame
import Character as c
import math
from enemy import Enemy

# Initialize Pygame clock to control the frame rate
Clock = pygame.time.Clock()

# Define colors
WHITE = (220, 221, 220)
RED = (255, 0, 0)  # For hitbox
GREEN = (0, 255, 0)  # For enemy center

class PyGame:
    def __init__(self):
        pygame.init()
        self.HEIGHT, self.WIDTH = 600, 1000
        self.x, self.y = 500, 250
        self.fixed_y = self.y
        self.height_rect, self.width_rect = 30, 30
        self.speed = 4
        self.health = 100  # Player health

        # Jumping mechanics
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -12

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.facing_left = False  # Track last facing direction
        self.walk_count = 0

        # Animation handling
        self.value = 0
        self.animation_speed = {"idle": 0.25, "walk": 0.3, "run": 0.4, "combo": 0.3, "hit": 0.15}
        self.current_speed = self.animation_speed["idle"]
        
        # Character animations (pre-scaled to 400x400 for performance)
        self.sprite_size = (400, 400)
        self.character_idle_right = [pygame.transform.scale(pygame.image.load(c.stand_Right[i]), self.sprite_size) for i in range(8)]
        self.character_walk_right = [pygame.transform.scale(pygame.image.load(c.walk[i]), self.sprite_size) for i in range(8)]
        self.character_run_right = [pygame.transform.scale(pygame.image.load(c.run[i]), self.sprite_size) for i in range(8)]
        self.character_combo_right = [pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size) for i in range(19)]
        self.character_hit_right = [pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size) for i in range(4)]  # Load hit animation
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []
        self.character_combo_left = []
        self.character_hit_left = []

        # Hit animation state
        self.is_hit = False
        self.hit_value = 0
        self.hit_frame_count = 4  # Total hit animation frames (matches enemy)

        # Environment assets
        self.road = pygame.image.load("Assets/Terrain/road.png")
        self.wall = pygame.image.load("Assets/Terrain/wallr.png")
        self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]

        # Background dimensions
        self.building_width = self.buildings[0].get_width()
        self.road_width = self.road.get_width()
        self.wall_width = self.wall.get_width()
        
        # Scroll positions
        self.building_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0
        self.free_mode_offset = 0
        
        # Player's world position
        self.player_width = 400
        self.world_x = 500
        self.screen_x = self.WIDTH / 2 - self.player_width / 2  # 300

        # Fullscreen and enemy tracking
        self.fullscreen = False
        self.enemy_exists = False
        self.last_tab_state = False

        # Combo state
        self.is_comboing = False
        self.combo_value = 0
        self.combo_frame_count = 19  # Total combo frames
        self.combo_damage = 2  # Damage per hit
        self.combo_range = 100  # Combo attack range

        # Enemies
        self.enemies = [Enemy(world_x, self.world_x, self.character_idle_right, self.character_walk_right, self.character_run_right) for world_x in range(1000, 10000, 1000)]

        # Scroll transition for smooth toggling
        self.scroll_transition_frames = 10
        self.current_transition_frame = 0
        self.target_road_scroll = 0

    def take_damage(self, damage):
        if self.health > 0:  # Only take damage if alive
            self.health -= damage
            print(f"Player takes {damage} damage! Health: {self.health}")
            # Trigger hit animation if not already playing
            if not self.is_hit and not self.is_comboing:  # Don't interrupt combo
                self.is_hit = True
                self.hit_value = 0
            if self.health <= 0:
                print("Player defeated!")
                pygame.quit()
                exit()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.WIDTH, self.WIDTH))

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def update(self, dt):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y

        if self.y >= self.fixed_y:
            self.y = self.fixed_y
            self.velocity_y = 0
            self.is_jumping = False

        # Clamp positions
        if self.enemy_exists:
            self.screen_x = max(0, min(self.screen_x, self.WIDTH - self.player_width))
        else:
            self.world_x = max(0, min(self.world_x, 10000))

    def char_config(self):
        for i in range(8):
            self.character_walk_left.append(pygame.transform.flip(self.character_walk_right[i], True, False))
            self.character_idle_left.append(pygame.transform.flip(self.character_idle_right[i], True, False))
            self.character_run_left.append(pygame.transform.flip(self.character_run_right[i], True, False))
        for i in range(19):
            self.character_combo_left.append(pygame.transform.flip(self.character_combo_right[i], True, False))
        for i in range(4):
            self.character_hit_left.append(pygame.transform.flip(self.character_hit_right[i], True, False))

    def draw_background(self, win):
        # Buildings (farthest layer)
        building_tiles = math.ceil(self.WIDTH / self.building_width) + 3
        for i in range(-1, building_tiles):
            scroll_amount = self.building_scroll % self.building_width
            pos_x = i * self.building_width - scroll_amount
            if pos_x < -self.building_width:
                continue
            if pos_x > self.WIDTH:
                continue
            for b in self.buildings:
                win.blit(b, (pos_x, 0))

        # Wall (middle layer)
        wall_tiles = math.ceil(self.WIDTH / self.wall_width) + 2
        for i in range(-1, wall_tiles):
            scroll_amount = self.wall_scroll % self.wall_width
            pos_x = i * self.wall_width - scroll_amount
            if -self.wall_width <= pos_x <= self.WIDTH:
                wall = pygame.transform.scale(self.wall, (self.wall_width, 180))
                win.blit(wall, (pos_x, 320))

        # Road (closest layer)
        road_tiles = math.ceil(self.WIDTH / self.road_width) + 2
        for i in range(-1, road_tiles):
            scroll_amount = self.road_scroll % self.road_width
            pos_x = i * self.road_width - scroll_amount
            if -self.road_width <= pos_x <= self.WIDTH:
                road = pygame.transform.scale(self.road, (self.road_width, 100))
                win.blit(road, (pos_x, 500))

    def draw_enemies(self, win):
        visible_enemies = 0
        scroll_offset = self.free_mode_offset if self.enemy_exists else self.road_scroll
        for enemy in self.enemies:
            previous_x = enemy.world_x
            enemy.update_movement(self.world_x, self)  # Pass self as the player
            enemy.check_attack_hit(self.world_x, self)  # Check for hits on player
            if enemy.world_x < 0:
                enemy.world_x += 10000
                print(f"Enemy wrapped around from left: {previous_x} to {enemy.world_x}")
            elif enemy.world_x > 10000:
                enemy.world_x -= 10000
                print(f"Enemy wrapped around from right: {previous_x} to {enemy.world_x}")
            enemy.update_animation()
            enemy.draw(win, scroll_offset)
            enemy_screen_x = enemy.world_x - scroll_offset
            if -enemy.width <= enemy_screen_x <= win.get_width():
                visible_enemies += 1
        return visible_enemies

    def update_animations(self):
        # Update player animation
        if self.is_hit:
            self.hit_value += self.animation_speed["hit"]
            if self.hit_value >= self.hit_frame_count:
                self.hit_value = 0
                self.is_hit = False
                self.current_speed = self.animation_speed["idle"]
        elif self.is_comboing:
            self.combo_value += self.animation_speed["combo"]
            if self.combo_value >= self.combo_frame_count:
                self.combo_value = 0
                self.is_comboing = False
                self.current_speed = self.animation_speed["idle"]
        else:
            self.value += self.current_speed
            if self.value >= 8:
                self.value -= 8

    def update_enemies(self):
        # Update enemy movements (handled in draw_enemies now)
        pass

    def check_combo_hits(self, win):
        # Check for combo hits on frames 1, 6, and 16
        if self.is_comboing:
            # Adjust hitbox center based on facing direction
            if self.facing_left:
                hitbox_center = self.world_x + self.player_width / 2 - 50  # Shift left
            else:
                hitbox_center = self.world_x + self.player_width / 2 + 50  # Shift right
            hitbox_left = hitbox_center - self.combo_range / 2
            hitbox_right = hitbox_center + self.combo_range / 2
            
            # Check collisions with enemies (no red hitbox drawn)
            for enemy in self.enemies[:]:  # Copy list to allow removal
                enemy_center = enemy.world_x + enemy.width / 2
                enemy_screen_center = enemy_center - (self.free_mode_offset if self.enemy_exists else self.road_scroll)
                # Draw enemy center (green dot) for debugging
                pygame.draw.circle(win, GREEN, (int(enemy_screen_center), self.y + 200), 5)
                
                # Apply damage on frames 1, 6, 16
                if int(self.combo_value) in [1, 6, 16]:
                    distance = abs(enemy_center - hitbox_center)
                    if hitbox_left <= enemy_center <= hitbox_right:
                        enemy.take_damage(self.combo_damage)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)

    def main(self):
        run = True
        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Stickman")

        while run:
            dt = Clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.draw_enemies(win) > 0 and not self.is_comboing and not self.is_hit:
                    self.is_comboing = True
                    self.current_speed = self.animation_speed["combo"]

            keys = pygame.key.get_pressed()

            # Animation speed
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.current_speed = self.animation_speed["walk"]
                if keys[pygame.K_RSHIFT]:
                    self.current_speed = self.animation_speed["run"]
            else:
                self.current_speed = self.animation_speed["idle"]

            # Movement logic
            move_amount = 0
            if keys[pygame.K_LEFT]:
                move_amount = -(10 if keys[pygame.K_RSHIFT] else self.speed)
                self.walk_left = True
                self.walk_right = False
                self.facing_left = True
            elif keys[pygame.K_RIGHT]:
                move_amount = 10 if keys[pygame.K_RSHIFT] else self.speed
                self.walk_right = True
                self.walk_left = False
                self.facing_left = False
            else:
                self.walk_left = False
                self.walk_right = False

            # Handle TAB toggle
            current_tab_state = keys[pygame.K_TAB]
            tab_just_pressed = current_tab_state and not self.last_tab_state
            self.last_tab_state = current_tab_state

            if tab_just_pressed:
                self.enemy_exists = not self.enemy_exists
                if self.enemy_exists:
                    self.screen_x = self.WIDTH / 2 - self.player_width / 2
                    self.free_mode_offset = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
                    self.road_scroll = self.free_mode_offset
                    self.building_scroll = self.free_mode_offset * 0.3
                    self.wall_scroll = self.free_mode_offset * 0.65
                else:
                    self.screen_x = self.WIDTH / 2 - self.player_width / 2
                    self.target_road_scroll = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
                    self.current_transition_frame = 0
                    self.road_scroll = self.free_mode_offset
                    self.building_scroll = self.road_scroll * 0.3
                    self.wall_scroll = self.road_scroll * 0.65
                    self.free_mode_offset = 0

            # Update positions based on mode
            if self.enemy_exists:
                self.screen_x += move_amount
                self.world_x = self.screen_x + self.free_mode_offset
                self.road_scroll = self.free_mode_offset
                self.building_scroll = self.free_mode_offset * 0.3
                self.wall_scroll = self.free_mode_offset * 0.65
            else:
                self.world_x += move_amount
                self.screen_x = self.WIDTH / 2 - self.player_width / 2
                if self.current_transition_frame < self.scroll_transition_frames:
                    t = self.current_transition_frame / self.scroll_transition_frames
                    self.road_scroll = self.road_scroll * (1 - t) + self.target_road_scroll * t
                    self.current_transition_frame += 1
                else:
                    self.road_scroll = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
                self.building_scroll = self.road_scroll * 0.3
                self.wall_scroll = self.road_scroll * 0.65

            if keys[pygame.K_UP]:
                self.jump()

            # Update animations and check for hits
            self.update_animations()
            self.update_enemies()  # Update movement before checking hits (now a no-op)

            # Drawing
            win.fill(WHITE)
            self.draw_background(win)
            visible_enemies = self.draw_enemies(win)
            self.check_combo_hits(win)  # Pass win to check hits

            # Use pre-scaled sprites
            char_idle_right = self.character_idle_right[int(self.value)]
            char_idle_left = self.character_idle_left[int(self.value)]
            char_walk_right = self.character_walk_right[int(self.value)]
            char_walk_left = self.character_walk_left[int(self.value)]
            char_run_right = self.character_run_right[int(self.value)]
            char_run_left = self.character_run_left[int(self.value)]
            char_combo_right = self.character_combo_right[int(self.combo_value)] if self.is_comboing else None
            char_combo_left = self.character_combo_left[int(self.combo_value)] if self.is_comboing else None
            char_hit_right = self.character_hit_right[int(self.hit_value)] if self.is_hit else None
            char_hit_left = self.character_hit_left[int(self.hit_value)] if self.is_hit else None

            # Display animation
            if self.is_hit:
                win.blit(char_hit_left if self.facing_left else char_hit_right, (self.screen_x, self.y))
            elif self.is_comboing:
                win.blit(char_combo_left if self.facing_left else char_combo_right, (self.screen_x, self.y))
            elif not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                win.blit(char_idle_left if self.facing_left else char_idle_right, (self.screen_x, self.y))
            elif keys[pygame.K_RSHIFT]:
                win.blit(char_run_right if self.walk_right else char_run_left, (self.screen_x, self.y))
            else:
                win.blit(char_walk_left if self.walk_left else char_walk_right, (self.screen_x, self.y))

            self.update(dt)
            if self.enemies:
                pass
            else:
                pass

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    pyg.char_config()
    pyg.main()