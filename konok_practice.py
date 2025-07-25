import pygame
import Character as c
import math
import random
import gc  # For manual garbage collection
from fake_enemy import Enemy
import cProfile

# Initialize Pygame clock to control the frame rate
Clock = pygame.time.Clock()

# Define colors
YELLOW = (225, 225, 0)
RED = (255, 0, 0)  # For hitbox
GREEN = (0, 255, 0)  # For enemy center
BLACK = (0, 0, 0)  # For text and black bars
WHITE = (220, 221, 220)

class PyGame:
    def __init__(self):
        pygame.init()
        # Base resolution and aspect ratio
        self.BASE_WIDTH, self.BASE_HEIGHT = 1200, 720
        self.ASPECT_RATIO = self.BASE_WIDTH / self.BASE_HEIGHT  # 5:3 = 1.6667

        # Get monitor resolution
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h

        # Calculate scaled resolution to maintain aspect ratio
        screen_ratio = self.screen_width / self.screen_height
        if screen_ratio > self.ASPECT_RATIO:
            # Screen is wider than game aspect ratio, fit to height
            self.game_height = self.screen_height
            self.game_width = int(self.game_height * self.ASPECT_RATIO)
        else:
            # Screen is taller than game aspect ratio, fit to width
            self.game_width = self.screen_width
            self.game_height = int(self.game_width / self.ASPECT_RATIO)

        # Calculate scaling factor and offsets for centering
        self.scale_factor = self.game_width / self.BASE_WIDTH
        self.offset_x = (self.screen_width - self.game_width) // 2
        self.offset_y = (self.screen_height - self.game_height) // 2

        # Sprite size for dynamic scaling
        self.sprite_size = (int(400 * self.scale_factor), int(400 * self.scale_factor))

        # Base coordinates (unscaled)
        self.x, self.y = 500, 380
        self.fixed_y = self.y
        self.height_rect, self.width_rect = 30, 30
        self.speed = 4
        self.health = 100  # Player health

        # Wave system
        self.current_wave = 0
        self.MAX_WAVES = 3
        self.wave_delay = 180
        self.wave_timer = 0
        self.wave_in_progress = False
        self.font = pygame.font.Font(None, int(36 * self.scale_factor))  # Scale font
        self.win_font = pygame.font.Font(None, int(124 * self.scale_factor))
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_interval = 5

        # Jumping mechanics
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.85
        self.jump_strength = -16

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.facing_left = False
        self.walk_count = 0

        # Animation handling
        self.value = 0
        self.animation_speed = {"idle": 0.25, "walk": 0.3, "run": 0.4, "combo": 0.3, "hit": 0.3, "death": 0.3}
        self.current_speed = self.animation_speed["idle"]

        # Load base sprites without scaling
        tint_color = (255, 0, 0)
        self.character_idle_right = [pygame.image.load(c.stand_Right[i]) for i in range(8)]
        self.character_walk_right = [pygame.image.load(c.walk[i]) for i in range(8)]
        self.character_run_right = [pygame.image.load(c.run[i]) for i in range(8)]
        self.character_combo_right = [pygame.image.load(c.combo[i]) for i in range(19)]
        self.character_hit_right = [pygame.image.load(c.hit[i]) for i in range(4)]
        self.character_death_right = [pygame.image.load(c.death[i]) for i in range(10)]

        self.enemy_fight_right = [self.tint_surface(pygame.image.load(c.combo[i]), tint_color) for i in range(19)]
        self.enemy_hit_right = [self.tint_surface(pygame.image.load(c.hit[i]), tint_color) for i in range(4)]
        self.enemy_death_right = [self.tint_surface(pygame.image.load(c.death[i]), tint_color) for i in range(10)]
        self.enemy_idle_right = [self.tint_surface(pygame.image.load(c.stand_Right[i]), tint_color) for i in range(8)]
        self.enemy_walk_right = [self.tint_surface(pygame.image.load(c.walk[i]), tint_color) for i in range(8)]

        # Pre-generate left-facing sprites (base size)
        self.character_walk_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_walk_right]
        self.character_run_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_run_right]
        self.character_idle_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_idle_right]
        self.character_combo_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_combo_right]
        self.character_hit_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_hit_right]
        self.character_death_left = [pygame.transform.flip(sprite, True, False) for sprite in self.character_death_right]
        self.enemy_fight_left = [pygame.transform.flip(sprite, True, False) for sprite in self.enemy_fight_right]
        self.enemy_hit_left = [pygame.transform.flip(sprite, True, False) for sprite in self.enemy_hit_right]
        self.enemy_death_left = [pygame.transform.flip(sprite, True, False) for sprite in self.enemy_death_right]

        # Animation states
        self.is_hit = False
        self.hit_value = 0
        self.hit_frame_count = 4
        self.is_dying = False
        self.death_value = 0
        self.death_frame_count = 10

        # Load and scale background assets
        try:
            self.road = pygame.image.load("Assets/Terrain/compress3/ohk_road_asset.png")
            self.footpath = pygame.image.load("Assets/Terrain/compress3/footpath_asset.png")
            self.wall = pygame.image.load("Assets/Terrain/compress3/ohk_wall_asset.png")
            # self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]
            self.buildings = pygame.image.load(f"Assets/buildings/bg_buildings-compressed.png")

            #gate - wall --
            self.gate_wall = pygame.image.load("Assets/Terrain/bpi_gate_temp/gate_wall -1-min2.png")
        
        except pygame.error as e:
            print(f"Error loading background assets: {e}")
            self.road = pygame.Surface((1200, 100))
            self.road.fill((100, 100, 100))
            self.footpath = pygame.Surface((1200, 60))
            self.footpath.fill((150, 150, 150))
            self.wall = pygame.Surface((1200, 180))
            self.wall.fill((50, 50, 50))
            self.buildings = [pygame.Surface((1200, 200)) for _ in range(5)]
            for b in self.buildings:
                b.fill((200, 200, 200))

        # Background dimensions (base resolution)
        # self.building_width = self.buildings[0].get_width()
        self.building_width = self.buildings.get_width()
        self.footpath_width = self.footpath.get_width()
        self.road_width = self.road.get_width()
        self.wall_width = self.wall.get_width()
        self.gate_wall_width = self.gate_wall.get_width()

        # Calculate scaled footpath width (base resolution)
        original_height = self.footpath.get_height()
        self.scale_factor_adjusted = 60 / original_height
        self.footpath_scaled_width = int(self.footpath_width * self.scale_factor_adjusted)

        # Pre-scale background assets for the scaled resolution
        self.road_scaled = pygame.transform.scale(self.road, (int(self.road_width * self.scale_factor), int(100 * self.scale_factor)))
        self.footpath_scaled = pygame.transform.scale(self.footpath, (int(self.footpath_scaled_width * self.scale_factor), int(60 * self.scale_factor)))
        self.wall_scaled = pygame.transform.scale(self.wall, (int(self.wall_width * self.scale_factor), int(180 * self.scale_factor)))
        self.buildings_scaled = pygame.transform.scale(self.buildings, (int(self.building_width * self.scale_factor), int(self.buildings.get_height() * self.scale_factor)))

        self.gate_wall_scaled = pygame.transform.scale(self.gate_wall, (int(self.gate_wall_width * self.scale_factor), int(self.gate_wall.get_height() * self.scale_factor)))
        # Update scaled dimensions
        self.building_width = self.buildings_scaled.get_width()
        self.footpath_scaled_width = self.footpath_scaled.get_width()
        self.road_width = self.road_scaled.get_width()
        self.wall_width = self.wall_scaled.get_width()

        self.gate_wall_width = self.gate_wall_scaled.get_width()

        # Background scroll positions (scaled resolution)
        self.building_scroll = 0
        self.footpath_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0

        # Scroll positions
        self.building_scroll = 0
        self.footpath_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0

        # Player's world position
        self.player_width = int(400 * self.scale_factor)
        self.world_x = 500
        self.screen_x = (self.BASE_WIDTH / 2 - 400 / 2)  # Base coordinates

        # Combo state
        self.is_comboing = False
        self.combo_value = 0
        self.combo_frame_count = 19
        self.combo_damage = 20
        self.combo_range = int(100 * self.scale_factor)

        # Enemies
        self.enemies = []

        # Garbage collection counter
        self.gc_counter = 0

    def tint_surface(self, surface, color):
        tinted = surface.copy()
        array = pygame.surfarray.pixels3d(tinted)
        array[...] = (array * color) // 255
        del array
        return tinted

    def take_damage(self, damage):
        if self.health > 0:
            self.health -= damage
            if not self.is_hit and not self.is_comboing and not self.is_dying:
                self.is_hit = True
                self.hit_value = 0
            if self.health <= 0 and not self.is_dying:
                self.is_dying = True
                self.death_value = 0
                self.current_speed = self.animation_speed["death"]

    def jump(self):
        if not self.is_jumping and not self.is_dying:
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def spawn_wave(self):
        self.current_wave += 1
        self.wave_in_progress = True
        num_enemies = 2 + (self.current_wave - 1)
        start_pos = random.randint(1000, 3000)
        spacing = random.randint(100, 500)
        self.enemies_to_spawn = [(start_pos + i * spacing) for i in range(num_enemies)]
        self.spawn_timer = 0

    def update_spawning(self):
        if self.enemies_to_spawn:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                world_x = self.enemies_to_spawn.pop(0)
                enemy = Enemy(
                    world_x=world_x,
                    player_world_x=self.world_x,
                    idle_right=self.enemy_idle_right,
                    walk_right=self.enemy_walk_right,
                    run_right=self.character_run_right,
                    fight_right=self.enemy_fight_right,
                    fight_left=self.enemy_fight_left,
                    hit_right=self.enemy_hit_right,
                    hit_left=self.enemy_hit_left,
                    death_right=self.enemy_death_right,
                    death_left=self.enemy_death_left,
                    wave_number=self.current_wave,
                    scale_factor=self.scale_factor
                )
                self.enemies.append(enemy)
                self.spawn_timer = self.spawn_interval

    def update(self, dt):
        if self.is_jumping and not self.is_dying:
            self.velocity_y += self.gravity
            self.y += self.velocity_y

        if self.y >= self.fixed_y and not self.is_dying:
            self.y = self.fixed_y
            self.velocity_y = 0
            self.is_jumping = False

        self.world_x = max(0, min(self.world_x, 5000))

    def draw_background(self, surface):
        # Buildings (farthest layer)
        building_tiles = math.ceil(self.BASE_WIDTH / (self.building_width / self.scale_factor)) + 2
        for i in range(-1, building_tiles):
            scroll_amount = (self.building_scroll * self.scale_factor) % self.building_width
            pos_x = i * self.building_width - scroll_amount
            if pos_x < -self.building_width or pos_x > self.game_width:
                continue
            else:
                surface.blit(self.buildings_scaled, (pos_x, 60 * self.scale_factor))

        # Wall (middle layer)

        # Set the gate's world position (fixed, not tied to tile index)
        gate_world_x = self.wall_width * 0  # e.g., one tile-width from the start
        gate_y = 112 * self.scale_factor

        # Calculate screen position of gate relative to scroll
        scroll_amount = self.wall_scroll * self.scale_factor
        gate_screen_x = gate_world_x - scroll_amount

        # Only draw if gate is on screen
        if -self.wall_width <= gate_screen_x <= self.game_width:
            surface.blit(self.gate_wall_scaled, (gate_screen_x, gate_y))

        # Now draw the regular wall tiles, skip the tile that overlaps gate
        wall_tiles = math.ceil(self.BASE_WIDTH / (self.wall_width / self.scale_factor)) + 3
        for i in range(-1, wall_tiles):
            pos_x = i * self.wall_width - scroll_amount
            if -self.wall_width <= pos_x <= self.game_width:
                # Skip wall tile that would overlap the gate
                if abs((i * self.wall_width) - gate_world_x) < self.wall_width:
                    continue
                surface.blit(self.wall_scaled, (pos_x, 380 * self.scale_factor))


        # Footpath (second closest layer)
        footpath_tiles = math.ceil(self.BASE_WIDTH / (self.footpath_scaled_width / self.scale_factor)) + 2
        scroll_amount = (self.footpath_scroll * self.scale_factor) % self.footpath_scaled_width
        start_pos_x = -scroll_amount
        for i in range(footpath_tiles):
            pos_x = start_pos_x + i * self.footpath_scaled_width
            if pos_x > self.game_width or pos_x < -self.footpath_scaled_width:
                continue
            surface.blit(self.footpath_scaled, (pos_x, 560 * self.scale_factor))

        # Road (closest layer)
        road_tiles = math.ceil(self.BASE_WIDTH / (self.road_width / self.scale_factor)) + 2
        for i in range(-1, road_tiles):
            scroll_amount = (self.road_scroll * self.scale_factor) % self.road_width
            pos_x = i * self.road_width - scroll_amount
            if -self.road_width <= pos_x <= self.game_width:
                surface.blit(self.road_scaled, (pos_x, 620 * self.scale_factor))

    def draw_enemies(self, surface):
        visible_enemies = 0
        scroll_offset = self.road_scroll
        if len(self.enemies) > 20:  # Reduced from 50 to 20
            self.enemies = self.enemies[-20:]
        remaining_enemies = []
        for enemy in self.enemies:
            previous_x = enemy.world_x
            enemy_screen_x = (enemy.world_x - scroll_offset) * self.scale_factor
            # Only update enemies that are on-screen
            if -enemy.width <= enemy_screen_x <= self.game_width:
                enemy.update_movement(self.world_x, self)
                enemy.check_attack_hit(self.world_x, self)
                enemy.update_animation()
            if enemy.world_x < 0:
                enemy.world_x += 10000
            elif enemy.world_x > 10000:
                enemy.world_x -= 10000
            if not enemy.ready_to_remove:
                enemy.draw(surface, scroll_offset * self.scale_factor, 0)
                if -enemy.width <= enemy_screen_x <= self.game_width:
                    visible_enemies += 1
                remaining_enemies.append(enemy)
        self.enemies = remaining_enemies
        return visible_enemies

    def update_animations(self):
        if self.is_dying:
            self.death_value += self.animation_speed["death"]
            if self.death_value >= self.death_frame_count:
                pygame.quit()
                exit()
        elif self.is_hit:
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

    def check_combo_hits(self, surface):
        if self.is_comboing:
            if self.facing_left:
                hitbox_center = self.world_x + (400 * self.scale_factor) / 2 - 50 * self.scale_factor
            else:
                hitbox_center = self.world_x + (400 * self.scale_factor) / 2 + 50 * self.scale_factor
            hitbox_left = hitbox_center - (100 * self.scale_factor) / 2
            hitbox_right = hitbox_center + (100 * self.scale_factor) / 2

            for enemy in self.enemies[:]:
                if enemy.death_animation_finished or enemy.health <= 0:
                    continue
                enemy_center = enemy.world_x + enemy.width / (2 * self.scale_factor)
                enemy_screen_center = (enemy_center - self.road_scroll) * self.scale_factor
                pygame.draw.circle(surface, GREEN, (int(enemy_screen_center), int((self.y + 200) * self.scale_factor)), int(5 * self.scale_factor))

                if int(self.combo_value) in [1, 6, 16]:
                    distance = abs(enemy_center - hitbox_center)
                    if hitbox_left <= enemy_center <= hitbox_right:
                        enemy.take_damage(self.combo_damage)

    def update_wave(self):
        if self.current_wave == 0:
            self.spawn_wave()
            return

        if self.wave_in_progress and not self.enemies and not self.enemies_to_spawn:
            self.wave_in_progress = False
            if self.current_wave < self.MAX_WAVES:
                self.wave_timer = self.wave_delay
            else:
                self.wave_timer = -1

        if not self.wave_in_progress and self.wave_timer > 0:
            self.wave_timer -= 1
            if self.wave_timer <= 0:
                self.spawn_wave()
        elif self.wave_timer == -1:
            self.wave_in_progress = False
            self.wave_timer = 0

        self.update_spawning()

    def draw_wave_info(self, surface):
        wave_text = self.font.render(f"Wave: {self.current_wave}", True, YELLOW)
        surface.blit(wave_text, (10 * self.scale_factor, 10 * self.scale_factor))
        if self.current_wave >= self.MAX_WAVES and not self.wave_in_progress and not self.enemies:
            win_text = self.win_font.render("You Win!", True, YELLOW)
            surface.blit(win_text, (self.game_width // 2 - win_text.get_width() // 2, self.game_height // 4))

        # Draw remaining enemies number
        remaining_enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, YELLOW)
        surface.blit(remaining_enemies_text, (self.game_width - remaining_enemies_text.get_width() - 10 * self.scale_factor, 10 * self.scale_factor))

        # Draw player health number in top middle
        health_text = self.font.render(f"Player Health: {self.health}", True, YELLOW)
        surface.blit(health_text, (self.game_width // 2 - health_text.get_width() // 2, 10 * self.scale_factor))



    def main(self):
        run = True
        # Set fullscreen mode
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Stickman")

        # Create a surface for the game content (scaled resolution)
        game_surface = pygame.Surface((self.game_width, self.game_height))

        while run:
            dt = Clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.current_speed = self.animation_speed["walk"]
                if keys[pygame.K_RSHIFT]:
                    self.current_speed = self.animation_speed["run"]
            else:
                self.current_speed = self.animation_speed["idle"]

            move_amount = 0
            if keys[pygame.K_LEFT]:
                move_amount = -10 if keys[pygame.K_RSHIFT] else -self.speed
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

            self.world_x += move_amount
            self.screen_x = self.BASE_WIDTH / 2 - 400 / 2  # Base coordinates
            self.road_scroll = self.world_x - (self.BASE_WIDTH / 2 - 400 / 2)
            self.building_scroll = self.road_scroll * 0.3
            self.wall_scroll = self.road_scroll * 0.65
            self.footpath_scroll = self.road_scroll * 0.75

            if keys[pygame.K_UP]:
                self.jump()

            self.update_wave()
            self.update_animations()

            # Clear the game surface
            game_surface.fill(BLACK)

            # Draw game content on the game surface
            self.draw_background(game_surface)
            visible_enemies = self.draw_enemies(game_surface)
            self.check_combo_hits(game_surface)
            self.draw_wave_info(game_surface)

            # Dynamically scale sprites
            char_idle_right = pygame.transform.scale(self.character_idle_right[int(self.value)], self.sprite_size)
            char_idle_left = pygame.transform.scale(self.character_idle_left[int(self.value)], self.sprite_size)
            char_walk_right = pygame.transform.scale(self.character_walk_right[int(self.value)], self.sprite_size)
            char_walk_left = pygame.transform.scale(self.character_walk_left[int(self.value)], self.sprite_size)
            char_run_right = pygame.transform.scale(self.character_run_right[int(self.value)], self.sprite_size)
            char_run_left = pygame.transform.scale(self.character_run_left[int(self.value)], self.sprite_size)
            char_combo_right = pygame.transform.scale(self.character_combo_right[int(self.combo_value)], self.sprite_size) if self.is_comboing else None
            char_combo_left = pygame.transform.scale(self.character_combo_left[int(self.combo_value)], self.sprite_size) if self.is_comboing else None
            char_hit_right = pygame.transform.scale(self.character_hit_right[int(self.hit_value)], self.sprite_size) if self.is_hit else None
            char_hit_left = pygame.transform.scale(self.character_hit_left[int(self.hit_value)], self.sprite_size) if self.is_hit else None
            char_death_right = pygame.transform.scale(self.character_death_right[int(self.death_value)], self.sprite_size) if self.is_dying else None
            char_death_left = pygame.transform.scale(self.character_death_left[int(self.death_value)], self.sprite_size) if self.is_dying else None

            if self.is_dying:
                game_surface.blit(char_death_left if self.facing_left else char_death_right, (self.screen_x * self.scale_factor, self.y * self.scale_factor))
            elif self.is_hit:
                game_surface.blit(char_hit_left if self.facing_left else char_hit_right, (self.screen_x * self.scale_factor, self.y * self.scale_factor))
            elif self.is_comboing:
                game_surface.blit(char_combo_left if self.facing_left else char_combo_right, (self.screen_x * self.scale_factor, self.y * self.scale_factor))
            elif not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                game_surface.blit(char_idle_left if self.facing_left else char_idle_right, (self.screen_x * self.scale_factor, self.y * self.scale_factor))
            elif keys[pygame.K_RSHIFT]:
                game_surface.blit(char_run_right if self.walk_right else char_run_left, (self.screen_x * self.scale_factor, self.y * self.scale_factor))
            else:
                game_surface.blit(char_walk_left if self.walk_left else char_walk_right, (self.screen_x * self.scale_factor, self.y * self.scale_factor))

            if keys[pygame.K_SPACE] and visible_enemies > 0 and not self.is_comboing and not self.is_hit and not self.is_dying:
                self.is_comboing = True
                self.current_speed = self.animation_speed["combo"]

            self.update(dt)

            # Clear the screen with black (for black bars)
            screen.fill(BLACK)

            # Blit the game surface onto the screen, centered
            screen.blit(game_surface, (self.offset_x, self.offset_y))

            # Garbage collection every 60 frames
            self.gc_counter += 1
            if self.gc_counter >= 60:
                gc.collect()
                self.gc_counter = 0

            pygame.display.flip()
            print(Clock.get_fps())

        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    cProfile.run('pyg.main()')
    