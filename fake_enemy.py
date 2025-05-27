import pygame
import Character as c

class Enemy:
    def __init__(self, world_x, player_world_x=500, idle_right=None, walk_right=None, run_right=None, fight_right=None, fight_left=None, hit_right=None, hit_left=None, death_right=None, death_left=None, wave_number=1, scale_factor=1.0):
        self.world_x = world_x
        self.scale_factor = scale_factor
        # Scale width and height based on scale_factor
        self.width = int(400 * self.scale_factor)
        self.height = int(400 * self.scale_factor)
        # Base health is 50, increases by 10 per wave (e.g., Wave 2: 60, Wave 3: 70)
        self.health = 50 + (wave_number - 1) * 10
        self.stunned = False
        self.stun_duration = 300  # 5 seconds at 60 FPS
        self.stun_timer = 0
        # Base speed is 2, increases slightly per wave
        self.speed = 2 + (wave_number - 1) * 0.2
        self.facing_left = world_x > player_world_x  # Face player initially
        self.value = 0  # For idle/walk animation
        self.current_speed = 0.23  # Default to walk speed
        self.animation_speed = {"idle": 0.25, "walk": 0.23, "fight": 0.15, "hit": 0.3, "death": 0.3}
        self.initial_x = world_x  # Store initial position for patrol
        self.patrol_range = 100  # Half of 200-unit patrol range (±100 units)
        self.direction = 1 if not self.facing_left else -1  # Start moving toward initial direction
        self.minimum_distance = 100  # Stop 100 units away from player
        self.patrol_at_distance_range = 25  # Patrol ±25 units when at minimum distance
        self.at_minimum_distance = False  # Track if enemy is at minimum distance
        self.patrol_center = None  # Center point for patrolling when at minimum distance
        self.is_fighting = False  # For combo attack animation
        self.fight_value = 0
        self.fight_duration = 19  # Match 19-frame combo animation
        self.is_hit = False  # For hit animation when taking damage
        self.hit_value = 0
        self.hit_duration = 4  # Match 4-frame hit animation
        self.is_dying = False  # Death animation state
        self.death_value = 0
        self.death_duration = 10  # Match 10-frame death animation
        self.death_animation_finished = False  # Flag to indicate death animation completion
        self.ready_to_remove = False  # Signal for immediate removal
        self.attack_cooldown = 60  # 1 second at 60 FPS
        self.attack_timer = 0  # Timer to manage attack frequency
        self.attack_damage = 2  # Match player's combo damage
        self.attack_range = int(100 * self.scale_factor)  # Scale attack range
        self.combo_delay = 60  # 1 second delay before starting combo (at 60 FPS)
        self.combo_delay_timer = 0  # Timer for delay

        # Use preloaded sprites (assuming they are pre-scaled by the caller)
        self.fight_right = fight_right
        self.fight_left = fight_left
        self.hit_right = hit_right
        self.hit_left = hit_left
        self.death_right = death_right
        self.death_left = death_left
        self.idle_right = idle_right
        self.walk_right = walk_right
        self.idle_left = [pygame.transform.flip(self.idle_right[i], True, False) for i in range(8)]
        self.walk_left = [pygame.transform.flip(self.walk_right[i], True, False) for i in range(8)]

    def take_damage(self, damage):
        if self.death_animation_finished:  # Ignore damage if already dead
            print(f"Enemy at {self.world_x} is already dead, ignoring damage")
            return
        self.health -= damage
        print(f"Enemy at {self.world_x} taking {damage} damage, health: {self.health}")
        if self.health > 0:  # Only trigger hit animation if alive
            if self.is_fighting:
                self.is_fighting = False  # Stop combo animation if active
            if not self.is_hit and not self.is_dying:  # Start hit animation only if not already playing or dying
                self.is_hit = True
                self.hit_value = 0
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.death_value = 0
            self.current_speed = self.animation_speed["death"]
            print(f"Enemy at {self.world_x} taking fatal damage, starting death animation")

    def check_attack_hit(self, player_world_x, player):
        if self.is_fighting and not self.is_dying:
            # Adjust hitbox center based on facing direction
            if self.facing_left:
                hitbox_center = self.world_x + self.width / 2 - 50 * self.scale_factor  # Shift left
            else:
                hitbox_center = self.world_x + self.width / 2 + 50 * self.scale_factor  # Shift right
            hitbox_left = hitbox_center - self.attack_range / 2
            hitbox_right = hitbox_center + self.attack_range / 2

            # Apply damage on frames 1, 6, 16
            player_center = player_world_x + self.width / (2 * self.scale_factor)  # Convert to base coordinates
            if int(self.fight_value) in [1, 6, 16]:
                if hitbox_left <= player_center <= hitbox_right:
                    if player:
                        player.take_damage(self.attack_damage)

    def update_animation(self):
        if self.is_dying and not self.death_animation_finished:
            self.death_value += self.animation_speed["death"]
            print(f"Enemy at {self.world_x} death animation frame: {self.death_value}")
            if self.death_value >= self.death_duration:
                self.death_value = self.death_duration - 1  # Cap at last frame (9)
                self.is_dying = False
                self.death_animation_finished = True  # Mark animation as finished
                self.ready_to_remove = True  # Signal for immediate removal
                self.current_speed = 0  # Stop all animations
                print(f"Enemy at {self.world_x} death animation locked at frame {self.death_value}, finished: {self.death_animation_finished}")
        elif self.is_hit:
            self.hit_value += self.animation_speed["hit"]
            if self.hit_value >= self.hit_duration:
                self.hit_value = 0
                self.is_hit = False
                self.stunned = False  # End stun when hit animation finishes
        elif self.is_fighting:
            self.fight_value += self.animation_speed["fight"]
            if self.fight_value >= self.fight_duration:
                self.fight_value = 0
                self.is_fighting = False
        elif not self.death_animation_finished:  # Only update idle/walk if not dead
            self.value += self.current_speed
            if self.value >= 8:  # Loop idle/walk animation
                self.value -= 8

    def update_movement(self, player_world_x, player=None):
        if not self.stunned and self.health > 0 and not self.is_dying:
            # Calculate distance to player
            distance_to_player = abs(player_world_x - self.world_x)

            # Manage attack cooldown and delay
            if self.attack_timer > 0:
                self.attack_timer -= 1
            if self.combo_delay_timer > 0:
                self.combo_delay_timer -= 1

            if distance_to_player > 200:  # Patrol if player is farther than 200 units
                self.at_minimum_distance = False  # Reset when far from player
                self.patrol_center = None
                self.combo_delay_timer = 0  # Reset delay when moving away
                # Update position
                self.world_x += self.speed * self.direction
                # Immediately enforce patrol boundaries
                if self.world_x >= self.initial_x + self.patrol_range:
                    self.world_x = self.initial_x + self.patrol_range  # Clamp at max
                    self.direction = -1  # Turn left
                    self.facing_left = True
                elif self.world_x <= self.initial_x - self.patrol_range:
                    self.world_x = self.initial_x - self.patrol_range  # Clamp at min
                    self.direction = 1  # Turn right
                    self.facing_left = False
                self.current_speed = self.animation_speed["walk"]  # Walk during patrol
            else:  # Follow player if within 200 units
                # Determine target position to stop at minimum distance
                if player_world_x < self.world_x:
                    target_x = player_world_x + self.minimum_distance  # Stop to the right of player
                    self.facing_left = True
                else:
                    target_x = player_world_x - self.minimum_distance  # Stop to the left of player
                    self.facing_left = False

                # Check if enemy is within minimum distance
                if abs(self.world_x - player_world_x) <= self.minimum_distance:
                    if not self.at_minimum_distance:  # Only set to True if it wasn't already True
                        self.at_minimum_distance = True
                        self.patrol_center = target_x  # Set patrol center at the stopping point
                        self.combo_delay_timer = self.combo_delay  # Start delay only when first entering range
                else:
                    self.at_minimum_distance = False
                    self.combo_delay_timer = 0  # Reset delay if moving out of range

                if not self.at_minimum_distance:
                    # Move toward the target position
                    if self.world_x > target_x:
                        self.world_x -= self.speed  # Move left toward target
                        self.direction = -1
                    else:
                        self.world_x += self.speed  # Move right toward target
                        self.direction = 1
                    self.current_speed = self.animation_speed["walk"]
                else:
                    # Attack the player after delay
                    if not self.is_fighting and self.attack_timer == 0 and self.combo_delay_timer == 0:
                        self.is_fighting = True
                        self.fight_value = 0
                        self.attack_timer = self.attack_cooldown
                    self.current_speed = self.animation_speed["idle"]  # Idle while waiting or attacking

        if self.stunned and self.health > 0 and not self.is_dying:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False

    def draw(self, win, scroll_offset, offset_y=0):
        enemy_screen_x = self.world_x * self.scale_factor - scroll_offset
        # Adjust y-position with offset_y for letterboxing and scale it
        base_y = (380 + offset_y) * self.scale_factor
        if -self.width <= enemy_screen_x <= win.get_width():  # Only draw if visible
            if self.is_dying:
                death_sprite = self.death_left[int(self.death_value)] if self.facing_left else self.death_right[int(self.death_value)]
                print(f"Enemy at {self.world_x} drawing death frame: {int(self.death_value)}")
                win.blit(death_sprite, (enemy_screen_x, base_y))
            elif self.is_hit:
                hit_sprite = self.hit_left[int(self.hit_value)] if self.facing_left else self.hit_right[int(self.hit_value)]
                print(f"Enemy at {self.world_x} drawing hit frame: {int(self.hit_value)}")
                win.blit(hit_sprite, (enemy_screen_x, base_y))
            elif self.is_fighting:
                fight_sprite = self.fight_left[int(self.fight_value)] if self.facing_left else self.fight_right[int(self.fight_value)]
                print(f"Enemy at {self.world_x} drawing fight frame: {int(self.fight_value)}")
                win.blit(fight_sprite, (enemy_screen_x, base_y))
            elif not self.death_animation_finished:  # Only draw idle/walk if not dead
                if self.current_speed == self.animation_speed["walk"]:
                    sprite = self.walk_left[int(self.value)] if self.facing_left else self.walk_right[int(self.value)]
                else:  # idle
                    sprite = self.idle_left[int(self.value)] if self.facing_left else self.idle_right[int(self.value)]
                if sprite:  # Ensure sprite exists before blitting
                    print(f"Enemy at {self.world_x} drawing idle/walk frame: {int(self.value)}")
                    win.blit(sprite, (enemy_screen_x, base_y))
            else:
                print(f"Enemy at {self.world_x} is dead, not drawing (finished: {self.death_animation_finished})")