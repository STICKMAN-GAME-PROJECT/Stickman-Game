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
        # Fix window size to 1200x720
        self.WIDTH, self.HEIGHT = 1200, 720
        self.x, self.y = 500, 380  # Base coordinates
        self.fixed_y = self.y
        self.height_rect, self.width_rect = 30, 30
        self.speed = 4
        self.health = 100  # Player health

        # Wave system
        self.current_wave = 0  # Start at wave 0 (will increment to 1 immediately)
        self.MAX_WAVES = 3  # Maximum number of waves
        self.wave_delay = 180  # 3 seconds at 60 FPS
        self.wave_timer = 0  # Timer for wave transition
        self.wave_in_progress = False  # Track if a wave is active
        self.font = pygame.font.Font(None, 36)  # Font for wave number display
        self.win_font = pygame.font.Font(None, 124)  # Larger font for win message
        self.enemies_to_spawn = []  # Queue for staggered spawning
        self.spawn_timer = 0  # Timer for staggering enemy spawns
        self.spawn_interval = 5  # Spawn one enemy every 5 frames

        # Jumping mechanics
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.85
        self.jump_strength = -16

        # Movement tracking
        self.walk_left = False
        self.walk_right = False
        self.facing_left = False  # Track last facing direction
        self.walk_count = 0

        # Animation handling
        self.value = 0
        self.animation_speed = {"idle": 0.25, "walk": 0.3, "run": 0.4, "combo": 0.3, "hit": 0.3, "death": 0.3}
        self.current_speed = self.animation_speed["idle"]
        
        # Character animations (pre-scaled to 400x400)
        self.sprite_size = (400, 400)
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
            self.footpath = pygame.Surface((100, 60))  # Fallback: gray rectangle
            self.footpath.fill((150, 150, 150))

        # Background dimensions
        self.building_width = self.buildings[0].get_width()
        self.footpath_width = self.footpath.get_width()
        self.road_width = self.road.get_width()
        self.wall_width = self.wall.get_width()
        
        # Calculate scaled footpath width
        original_height = self.footpath.get_height()
        self.scale_factor_adjusted = 60 / original_height
        self.footpath_scaled_width = int(self.footpath_width * self.scale_factor_adjusted)
        
        # Scroll positions
        self.building_scroll = 0
        self.footpath_scroll = 0
        self.road_scroll = 0
        self.wall_scroll = 0
        self.free_mode_offset = 0
        
        # Player's world position
        self.player_width = 400
        self.world_x = 500
        self.screen_x = self.WIDTH / 2 - self.player_width / 2

        # Fullscreen and enemy tracking (fullscreen disabled)
        self.enemy_exists = False
        self.last_tab_state = False

        # Combo state
        self.is_comboing = False
        self.combo_value = 0
        self.combo_frame_count = 19  # Total combo frames
        self.combo_damage = 20  # Damage per hit
        self.combo_range = 100  # Combo attack range

        # Enemies
        self.enemies = []

        # Scroll transition
        self.scroll_transition_frames = 10
        self.current_transition_frame = 0
        self.target_road_scroll = 0

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
            if not self.is_hit and not self.is_comboing and not self.is_dying:  # Don't interrupt other animations
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
        start_pos = 1000
        spacing = 1000
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

        self.world_x = max(0, min(self.world_x, 10000))

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
                b_scaled = pygame.transform.scale(b, (self.building_width, b.get_height()))
                win.blit(b_scaled, (pos_x, 60))

        # Wall (middle layer)
        wall_tiles = math.ceil(self.WIDTH / self.wall_width) + 2
        for i in range(-1, wall_tiles):
            scroll_amount = self.wall_scroll % self.wall_width
            pos_x = i * self.wall_width - scroll_amount
            if -self.wall_width <= pos_x <= self.WIDTH:
                wall = pygame.transform.scale(self.wall, (self.wall_width, 180))
                win.blit(wall, (pos_x, 380))

        # Footpath (second closest layer)
        footpath = pygame.transform.scale(self.footpath, (self.footpath_scaled_width, 60))
        footpath_tiles = math.ceil(self.WIDTH / self.footpath_scaled_width) + 2
        scroll_amount = self.footpath_scroll % self.footpath_scaled_width
        start_pos_x = -scroll_amount
        for i in range(footpath_tiles):
            pos_x = start_pos_x + i * self.footpath_scaled_width
            if pos_x > self.WIDTH or pos_x < -self.footpath_scaled_width:
                continue
            win.blit(footpath, (pos_x, 560))

        # Road (closest layer)
        road_tiles = math.ceil(self.WIDTH / self.road_width) + 2
        for i in range(-1, road_tiles):
            scroll_amount = self.road_scroll % self.road_width
            pos_x = i * self.road_width - scroll_amount
            if -self.road_width <= pos_x <= self.WIDTH:
                road = pygame.transform.scale(self.road, (self.road_width, 100))
                win.blit(road, (pos_x, 620))

    def draw_enemies(self, win):
        visible_enemies = 0
        scroll_offset = self.road_scroll
        for enemy in self.enemies[:]:
            previous_x = enemy.world_x
            enemy.update_movement(self.world_x, self)
            enemy.check_attack_hit(self.world_x, self)
            if enemy.world_x < 0:
                enemy.world_x += 10000
            elif enemy.world_x > 10000:
                enemy.world_x -= 10000
            enemy.update_animation()
            if enemy.ready_to_remove:
                self.enemies.remove(enemy)
                continue
            enemy.draw(win, scroll_offset)
            enemy_screen_x = enemy.world_x - scroll_offset
            if -enemy.width <= enemy_screen_x <= self.WIDTH:
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
                hitbox_center = self.world_x + self.player_width / 2 - 50
            else:
                hitbox_center = self.world_x + self.player_width / 2 + 50
            hitbox_left = hitbox_center - self.combo_range / 2
            hitbox_right = hitbox_center + self.combo_range / 2
            
            for enemy in self.enemies[:]:
                if enemy.death_animation_finished or enemy.health <= 0:
                    continue
                enemy_center = enemy.world_x + enemy.width / 2
                enemy_screen_center = enemy_center - self.road_scroll
                pygame.draw.circle(win, GREEN, (int(enemy_screen_center), self.y + 200), 5)
                
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
        win.blit(wave_text, (10, 10))
        if self.current_wave >= self.MAX_WAVES and not self.wave_in_progress and not self.enemies:
            win_text = self.win_font.render("You Win!", True, YELLOW)
            win.blit(win_text, (self.WIDTH // 2 - win_text.get_width() // 2, self.HEIGHT // 4))

    def main(self):
        run = True
        win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Fixed window size
        pygame.display.set_caption("Stickman")

        while run:
            dt = Clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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

            current_tab_state = keys[pygame.K_TAB]
            tab_just_pressed = current_tab_state and not self.last_tab_state
            self.last_tab_state = current_tab_state

            if tab_just_pressed:
                self.enemy_exists = not self.enemy_exists

            self.world_x += move_amount
            self.screen_x = self.WIDTH / 2 - self.player_width / 2
            self.road_scroll = self.world_x - (self.WIDTH / 2 - self.player_width / 2)
            self.building_scroll = self.road_scroll * 0.3
            self.wall_scroll = self.road_scroll * 0.65
            self.footpath_scroll = self.road_scroll * 0.75

            if keys[pygame.K_UP]:
                self.jump()

            self.update_wave()
            self.update_animations()
            self.update_enemies()

            # Clear the screen
            win.fill(BLACK)
            # Draw game content
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

            if keys[pygame.K_SPACE] and visible_enemies > 0 and not self.is_comboing and not self.is_hit and not self.is_dying:
                self.is_comboing = True
                self.current_speed = self.animation_speed["combo"]

            self.update(dt)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    pyg = PyGame()
    pyg.char_config()
    pyg.main()