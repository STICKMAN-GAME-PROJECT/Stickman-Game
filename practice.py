import pygame
import Character as c
import math
from enemy import Enemy

# Initialize Pygame clock to control the frame rate
Clock = pygame.time.Clock()

# Define colors
YELLOW = (225, 225, 0)
RED = (255, 0, 0)  # For hitbox
GREEN = (0, 255, 0)  # For enemy center
BLACK = (0, 0, 0)  # For text
WHITE = (220, 221, 220)

class PyGame:
    def __init__(self):
        pygame.init()
        # Get display info to adapt to screen resolution
        display_info = pygame.display.Info()
        self.base_width, self.base_height = 1200, 720  # Default resolution
        # Calculate initial scale factor based on display width
        self.scale_factor = max(1, display_info.current_w / self.base_width)
        self.WIDTH = int(self.base_width * self.scale_factor)
        self.HEIGHT = int(self.base_height * self.scale_factor)
        self.x, self.y = int(500 * self.scale_factor), int(380 * self.scale_factor)
        self.fixed_y = self.y
        self.height_rect, self.width_rect = int(30 * self.scale_factor), int(30 * self.scale_factor)
        self.speed = 4 * self.scale_factor
        self.health = 100  # Player health

        # Wave system
        self.current_wave = 0  # Start at wave 0 (will increment to 1 immediately)
        self.MAX_WAVES = 3  # Maximum number of waves
        self.wave_delay = 180  # 3 seconds at 60 FPS
        self.wave_timer = 0  # Timer for wave transition
        self.wave_in_progress = False  # Track if a wave is active
        self.font = pygame.font.Font(None, int(36 * self.scale_factor))  # Font for wave number display
        self.win_font = pygame.font.Font(None, int(124 * self.scale_factor))  # Larger font for win message
        self.enemies_to_spawn = []  # Queue for staggered spawning
        self.spawn_timer = 0  # Timer for staggering enemy spawns
        self.spawn_interval = 5  # Spawn one enemy every 5 frames (about 0.083 seconds at 60 FPS)

        # Jumping mechanics
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.85 * self.scale_factor
        self.jump_strength = -16 * self.scale_factor

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.facing_left = False  # Track last facing direction
        self.walk_count = 0

        # Animation handling
        self.value = 0
        self.animation_speed = {"idle": 0.25, "walk": 0.3, "run": 0.4, "combo": 0.3, "hit": 0.3, "death": 0.3}
        self.current_speed = self.animation_speed["idle"]
        
        # Character animations (pre-scaled to 400x400 for performance)
        self.sprite_size = (int(400 * self.scale_factor), int(400 * self.scale_factor))
        self.character_idle_right = [pygame.transform.scale(pygame.image.load(c.stand_Right[i]), self.sprite_size) for i in range(8)]
        self.character_walk_right = [pygame.transform.scale(pygame.image.load(c.walk[i]), self.sprite_size) for i in range(8)]
        self.character_run_right = [pygame.transform.scale(pygame.image.load(c.run[i]), self.sprite_size) for i in range(8)]
        self.character_combo_right = [pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size) for i in range(19)]
        self.character_hit_right = [pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size) for i in range(4)]
        self.character_death_right = [pygame.transform.scale(pygame.image.load(c.death[i]), self.sprite_size) for i in range(10)]
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []
        self.character_combo_left = []
        self.character_hit_left = []
        self.character_death_left = []

        # Preload enemy sprites with tint
        tint_color = (255, 0, 0)  # Red tint for enemies
        self.enemy_fight_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size), tint_color) for i in range(19)]
        self.enemy_fight_left = [pygame.transform.flip(self.enemy_fight_right[i], True, False) for i in range(19)]
        self.enemy_hit_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size), tint_color) for i in range(4)]
        self.enemy_hit_left = [pygame.transform.flip(self.enemy_hit_right[i], True, False) for i in range(4)]
        self.enemy_death_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.death[i]), self.sprite_size), tint_color) for i in range(10)]
        self.enemy_death_left = [pygame.transform.flip(self.enemy_death_right[i], True, False) for i in range(10)]
        self.enemy_idle_right = [self.tint_surface(sprite.copy(), tint_color) for sprite in self.character_idle_right]
        self.enemy_walk_right = [self.tint_surface(sprite.copy(), tint_color) for sprite in self.character_walk_right]

        # Animation states
        self.is_hit = False
        self.hit_value = 0
        self.hit_frame_count = 4  # Total hit animation frames
        self.is_dying = False  # Death animation state
        self.death_value = 0
        self.death_frame_count = 10  # Total death animation frames

        # Environment assets
        try:
            self.road = pygame.image.load("Assets/Terrain/ohk_road_asset.png")
            self.footpath = pygame.image.load("Assets/Terrain/footpath_asset.png")
            self.wall = pygame.image.load("Assets/Terrain/ohk_wall_asset.png")
            self.buildings = [pygame.image.load(f"Assets/buildings/{i}.png") for i in range(1, 6)]
        except pygame.error as e:
            self.footpath = pygame.Surface((int(100 * self.scale_factor), int(60 * self.scale_factor)))  # Fallback: gray rectangle
            self.footpath.fill((150, 150, 150))

        # Background dimensions
        self.building_width = int(self.buildings[0].get_width() * self.scale_factor)
        self.footpath_width = int(self.footpath.get_width() * self.scale_factor)
        self.road_width = int(self.road.get_width() * self.scale_factor)
        self.wall_width = int(self.wall.get_width() * self.scale_factor)
        
        # Calculate scaled footpath width
        original_height = self.footpath.get_height() / self.scale_factor
        self.scale_factor_adjusted = 60 / original_height
        self.footpath_scaled_width = int(self.footpath_width * self.scale_factor_adjusted)
        
        # Scroll positions
        self.building_scroll = 0
        self.footpath_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0
        self.free_mode_offset = 0
        
        # Player's world position
        self.player_width = int(400 * self.scale_factor)
        self.world_x = int(500 * self.scale_factor)
        self.screen_x = self.WIDTH / 2 - self.player_width / 2

        # Fullscreen and enemy tracking
        self.fullscreen = False
        self.enemy_exists = False
        self.last_tab_state = False

        # Combo state
        self.is_comboing = False
        self.combo_value = 0
        self.combo_frame_count = 19  # Total combo frames
        self.combo_damage = 20  # Damage per hit
        self.combo_range = int(100 * self.scale_factor)  # Combo attack range

        # Enemies (start empty, will spawn with waves)
        self.enemies = []

        # Scroll transition for smooth toggling
        self.scroll_transition_frames = 10
        self.current_transition_frame = 0
        self.target_road_scroll = 0

        # Fullscreen scale factor
        self.fullscreen_scale_factor = 1.0
        # Initialize effective scale (used throughout the game)
        self.effective_scale = self.scale_factor * self.fullscreen_scale_factor

    def tint_surface(self, surface, color):
        """Apply a raw tint to the surface using color modulation."""
        tinted = surface.copy()
        array = pygame.surfarray.pixels3d(tinted)
        array[...] = (array * color) // 255  # Element-wise multiplication and normalization
        del array  # Clean up the array to avoid memory issues
        return tinted

    def take_damage(self, damage):
        if self.health > 0:  # Only take damage if alive
            self.health -= damage
            # Trigger hit animation if not already playing
            if not self.is_hit and not self.is_comboing and not self.is_dying:  # Don't interrupt other animations
                self.is_hit = True
                self.hit_value = 0
            if self.health <= 0 and not self.is_dying:
                self.is_dying = True
                self.death_value = 0
                self.current_speed = self.animation_speed["death"]

    def toggle_fullscreen(self):
        display_info = pygame.display.Info()
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Get the native resolution in fullscreen
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            fullscreen_width = display_info.current_w
            fullscreen_height = display_info.current_h
            # Calculate new scale factor to match fullscreen height while preserving aspect ratio
            self.fullscreen_scale_factor = fullscreen_height / self.base_height
            self.WIDTH = int(self.base_width * self.fullscreen_scale_factor)
            self.HEIGHT = int(self.base_height * self.fullscreen_scale_factor)
        else:
            # Revert to windowed mode with original scaling
            self.fullscreen_scale_factor = 1.0
            self.scale_factor = max(1, display_info.current_w / self.base_width)
            self.WIDTH = int(self.base_width * self.scale_factor)
            self.HEIGHT = int(self.base_height * self.scale_factor)
            pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        # Update effective scale
        self.effective_scale = self.scale_factor * self.fullscreen_scale_factor

        # Update scaled values for fullscreen or windowed mode
        self.x, self.y = int(500 * self.effective_scale), int(380 * self.effective_scale)
        self.fixed_y = self.y
        self.height_rect, self.width_rect = int(30 * self.effective_scale), int(30 * self.effective_scale)
        self.speed = 4 * self.effective_scale
        self.gravity = 0.85 * self.effective_scale
        self.jump_strength = -16 * self.effective_scale
        self.font = pygame.font.Font(None, int(36 * self.effective_scale))
        self.win_font = pygame.font.Font(None, int(124 * self.effective_scale))
        self.sprite_size = (int(400 * self.effective_scale), int(400 * self.effective_scale))
        self.character_idle_right = [pygame.transform.scale(pygame.image.load(c.stand_Right[i]), self.sprite_size) for i in range(8)]
        self.character_walk_right = [pygame.transform.scale(pygame.image.load(c.walk[i]), self.sprite_size) for i in range(8)]
        self.character_run_right = [pygame.transform.scale(pygame.image.load(c.run[i]), self.sprite_size) for i in range(8)]
        self.character_combo_right = [pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size) for i in range(19)]
        self.character_hit_right = [pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size) for i in range(4)]
        self.character_death_right = [pygame.transform.scale(pygame.image.load(c.death[i]), self.sprite_size) for i in range(10)]
        self.char_config()  # Update flipped sprites
        tint_color = (255, 0, 0)
        self.enemy_fight_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size), tint_color) for i in range(19)]
        self.enemy_fight_left = [pygame.transform.flip(self.enemy_fight_right[i], True, False) for i in range(19)]
        self.enemy_hit_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size), tint_color) for i in range(4)]
        self.enemy_hit_left = [pygame.transform.flip(self.enemy_hit_right[i], True, False) for i in range(4)]
        self.enemy_death_right = [self.tint_surface(pygame.transform.scale(pygame.image.load(c.death[i]), self.sprite_size), tint_color) for i in range(10)]
        self.enemy_death_left = [pygame.transform.flip(self.enemy_death_right[i], True, False) for i in range(10)]
        self.enemy_idle_right = [self.tint_surface(sprite.copy(), tint_color) for sprite in self.character_idle_right]
        self.enemy_walk_right = [self.tint_surface(sprite.copy(), tint_color) for sprite in self.character_walk_right]
        self.building_width = int(self.buildings[0].get_width() * self.effective_scale)
        self.footpath_width = int(self.footpath.get_width() * self.effective_scale)
        self.road_width = int(self.road.get_width() * self.effective_scale)
        self.wall_width = int(self.wall.get_width() * self.effective_scale)
        original_height = self.footpath.get_height() / self.effective_scale
        self.scale_factor_adjusted = 60 / original_height
        self.footpath_scaled_width = int(self.footpath_width * self.scale_factor_adjusted)
        self.player_width = int(400 * self.effective_scale)
        self.world_x = int(500 * self.effective_scale)
        self.screen_x = self.WIDTH / 2 - self.player_width / 2
        self.combo_range = int(100 * self.effective_scale)

    def jump(self):
        if not self.is_jumping and not self.is_dying:
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def spawn_wave(self):
        self.current_wave += 1
        self.wave_in_progress = True
        num_enemies = 2 + (self.current_wave - 1)
        start_pos = int(1000 * self.effective_scale)
        spacing = int(1000 * self.effective_scale)
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
                    wave_number=self.current_wave
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

        if self.enemy_exists and not self.is_dying:
            self.screen_x = max(0, min(self.screen_x, self.WIDTH - self.player_width))
        else:
            self.world_x = max(0, min(self.world_x, int(10000 * self.effective_scale)))

    def char_config(self):
        self.character_walk_left = []
        self.character_run_left = []
        self.character_idle_left = []
        self.character_combo_left = []
        self.character_hit_left = []
        self.character_death_left = []
        for i in range(8):
            self.character_walk_left.append(pygame.transform.flip(self.character_walk_right[i], True, False))
            self.character_idle_left.append(pygame.transform.flip(self.character_idle_right[i], True, False))
            self.character_run_left.append(pygame.transform.flip(self.character_run_right[i], True, False))
        for i in range(19):
            self.character_combo_left.append(pygame.transform.flip(self.character_combo_right[i], True, False))
        for i in range(4):
            self.character_hit_left.append(pygame.transform.flip(self.character_hit_right[i], True, False))
        for i in range(10):
            self.character_death_left.append(pygame.transform.flip(self.character_death_right[i], True, False))

    def draw_background(self, win):
        # Buildings (farthest layer)
        building_tiles = math.ceil(self.WIDTH / self.building_width) + 3
        for i in range(-1, building_tiles):
            scroll_amount = self.building_scroll % self.building_width
            pos_x = i * self.building_width - scroll_amount
            if pos_x < -self.building_width or pos_x > self.WIDTH:
                continue
            for b in self.buildings:
                b_scaled = pygame.transform.scale(b, (self.building_width, int(b.get_height() * self.effective_scale)))
                win.blit(b_scaled, (pos_x, int(60 * self.effective_scale)))

        # Wall (middle layer)
        wall_tiles = math.ceil(self.WIDTH / self.wall_width) + 2
        for i in range(-1, wall_tiles):
            scroll_amount = self.wall_scroll % self.wall_width
            pos_x = i * self.wall_width - scroll_amount
            if -self.wall_width <= pos_x <= self.WIDTH:
                wall = pygame.transform.scale(self.wall, (self.wall_width, int(180 * self.effective_scale)))
                win.blit(wall, (pos_x, int(380 * self.effective_scale)))

        # Footpath (second closest layer)
        footpath = pygame.transform.scale(self.footpath, (self.footpath_scaled_width, int(60 * self.effective_scale)))
        footpath_tiles = math.ceil(self.WIDTH / self.footpath_scaled_width) + 2
        scroll_amount = self.footpath_scroll % self.footpath_scaled_width
        start_pos_x = -scroll_amount
        for i in range(footpath_tiles):
            pos_x = start_pos_x + i * self.footpath_scaled_width
            if pos_x > self.WIDTH or pos_x < -self.footpath_scaled_width:
                continue
            win.blit(footpath, (pos_x, int(560 * self.effective_scale)))

        # Road (closest layer)
        road_tiles = math.ceil(self.WIDTH / self.road_width) + 2
        for i in range(-1, road_tiles):
            scroll_amount = self.road_scroll % self.road_width
            pos_x = i * self.road_width - scroll_amount
            if -self.road_width <= pos_x <= self.WIDTH:
                road = pygame.transform.scale(self.road, (self.road_width, int(100 * self.effective_scale)))
                win.blit(road, (pos_x, int(620 * self.effective_scale)))

    def draw_enemies(self, win):
        visible_enemies = 0
        scroll_offset = self.free_mode_offset if self.enemy_exists else self.road_scroll
        for enemy in self.enemies[:]:
            previous_x = enemy.world_x
            enemy.update_movement(self.world_x, self)
            enemy.check_attack_hit(self.world_x, self)
            if enemy.world_x < 0:
                enemy.world_x += int(10000 * self.effective_scale)
            elif enemy.world_x > int(10000 * self.effective_scale):
                enemy.world_x -= int(10000 * self.effective_scale)
            enemy.update_animation()
            if enemy.ready_to_remove:
                self.enemies.remove(enemy)
                continue
            enemy.draw(win, scroll_offset)
            enemy_screen_x = enemy.world_x - scroll_offset
            if -enemy.width <= enemy_screen_x <= win.get_width():
                visible_enemies += 1
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

    def update_enemies(self):
        pass

    def check_combo_hits(self, win):
        if self.is_comboing:
            if self.facing_left:
                hitbox_center = self.world_x + self.player_width / 2 - int(50 * self.effective_scale)
            else:
                hitbox_center = self.world_x + self.player_width / 2 + int(50 * self.effective_scale)
            hitbox_left = hitbox_center - self.combo_range / 2
            hitbox_right = hitbox_center + self.combo_range / 2
            
            for enemy in self.enemies[:]:
                if enemy.death_animation_finished or enemy.health <= 0:
                    continue
                enemy_center = enemy.world_x + enemy.width / 2
                enemy_screen_center = enemy_center - (self.free_mode_offset if self.enemy_exists else self.road_scroll)
                pygame.draw.circle(win, GREEN, (int(enemy_screen_center), self.y + int(200 * self.effective_scale)), int(5 * self.effective_scale))
                
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

    def draw_wave_info(self, win):
        wave_text = self.font.render(f"Wave: {self.current_wave}", True, BLACK)
        win.blit(wave_text, (int(10 * self.effective_scale), int(10 * self.effective_scale)))
        if self.current_wave >= self.MAX_WAVES and not self.wave_in_progress and not self.enemies:
            win_text = self.win_font.render("You Win!", True, YELLOW)
            win.blit(win_text, (self.WIDTH // 2 - win_text.get_width() // 2, int(self.HEIGHT // 4)))

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
                    win = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN if self.fullscreen else 0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.draw_enemies(win) > 0 and not self.is_comboing and not self.is_hit and not self.is_dying:
                    self.is_comboing = True
                    self.current_speed = self.animation_speed["combo"]

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.current_speed = self.animation_speed["walk"]
                if keys[pygame.K_RSHIFT]:
                    self.current_speed = self.animation_speed["run"]
            else:
                self.current_speed = self.animation_speed["idle"]

            move_amount = 0
            if keys[pygame.K_LEFT]:
                move_amount = -(int(10 * self.effective_scale) if keys[pygame.K_RSHIFT] else int(self.speed))
                self.walk_left = True
                self.walk_right = False
                self.facing_left = True
            elif keys[pygame.K_RIGHT]:
                move_amount = int(10 * self.effective_scale) if keys[pygame.K_RSHIFT] else int(self.speed)
                self.walk_right = True
                self.walk_left = False
                self.facing_left = False
            else:
                self.walk_left = False
                self.walk_right = False

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
                    self.footpath_scroll = self.free_mode_offset * 0.75
                else:
                    self.screen_x = self.WIDTH / 2 - self.player_width / 2
                    self.target_road_scroll = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
                    self.current_transition_frame = 0
                    self.road_scroll = self.free_mode_offset
                    self.building_scroll = self.road_scroll * 0.3
                    self.wall_scroll = self.road_scroll * 0.65
                    self.footpath_scroll = self.road_scroll * 0.75
                    self.free_mode_offset = 0

            if self.enemy_exists and not self.is_dying:
                self.screen_x += move_amount
                self.world_x = self.screen_x + self.free_mode_offset
                self.road_scroll = self.free_mode_offset
                self.building_scroll = self.free_mode_offset * 0.3
                self.wall_scroll = self.free_mode_offset * 0.65
                self.footpath_scroll = self.free_mode_offset * 0.75
            else:
                self.world_x += move_amount
                self.screen_x = self.WIDTH / 2 - self.player_width / 2
                if self.current_transition_frame < self.scroll_transition_frames:
                    t = self.current_transition_frame / self.scroll_transition_frames
                    self.road_scroll = self.road_scroll * (1 - t) + self.target_road_scroll * t
                    self.building_scroll = self.road_scroll * 0.3
                    self.wall_scroll = self.road_scroll * 0.65
                    self.footpath_scroll = self.road_scroll * 0.75
                    self.current_transition_frame += 1
                else:
                    self.road_scroll = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
                    self.building_scroll = self.road_scroll * 0.3
                    self.wall_scroll = self.road_scroll * 0.65
                    self.footpath_scroll = self.road_scroll * 0.75

            if keys[pygame.K_UP]:
                self.jump()

            self.update_wave()
            self.update_animations()
            self.update_enemies()

            win.fill(WHITE)
            self.draw_background(win)
            visible_enemies = self.draw_enemies(win)
            self.check_combo_hits(win)
            self.draw_wave_info(win)

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
            char_death_right = self.character_death_right[int(self.death_value)] if self.is_dying else None
            char_death_left = self.character_death_left[int(self.death_value)] if self.is_dying else None

            if self.is_dying:
                win.blit(char_death_left if self.facing_left else char_death_right, (self.screen_x, self.y))
            elif self.is_hit:
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