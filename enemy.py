import pygame
import Character as c

class Enemy:
    def __init__(self, world_x, player_world_x=500, idle_right=None, walk_right=None, run_right=None):
        self.world_x = world_x
        self.width = 400
        self.height = 400
        self.health = 50
        self.stunned = False
        self.stun_duration = 300  # 5 seconds at 60 FPS
        self.stun_timer = 0
        self.speed = 2
        self.facing_left = world_x > player_world_x  # Face player initially
        self.value = 0  # For idle/walk animation
        self.current_speed = 0.23  # Default to walk speed
        self.animation_speed = {"idle": 0.23, "walk": 0.23, "fight": 0.15, "hit": 0.15}
        self.initial_x = world_x  # Store initial position for patrol
        self.patrol_range = 100  # Half of 1000-unit patrol range
        self.direction = 1 if not self.facing_left else -1  # Start moving toward initial direction
        self.minimum_distance = 100  # Stop 50 units away from player
        self.patrol_at_distance_range = 25  # Patrol ±25 units when at minimum distance
        self.at_minimum_distance = False  # Track if enemy is at minimum distance
        self.patrol_center = None  # Center point for patrolling when at minimum distance
        self.is_fighting = False  # For combo attack animation
        self.fight_value = 0
        self.fight_duration = 19  # Match 19-frame combo animation
        self.is_hit = False  # For hit animation when taking damage
        self.hit_value = 0
        self.hit_duration = 4  # Match 4-frame hit animation
        self.attack_cooldown = 60  # 1 second at 60 FPS
        self.attack_timer = 0  # Timer to manage attack frequency
        self.attack_damage = 2  # Match player's combo damage
        self.attack_range = 100  # Match player's combo range

        # Load and scale player's fight combo animation
        self.sprite_size = (400, 400)
        self.fight_right = [pygame.transform.scale(pygame.image.load(c.combo[i]), self.sprite_size) for i in range(19)]
        self.fight_left = [pygame.transform.flip(self.fight_right[i], True, False) for i in range(19)]
        # Load and scale hit animation for taking damage
        self.hit_right = [pygame.transform.scale(pygame.image.load(c.hit[i]), self.sprite_size) for i in range(4)]
        self.hit_left = [pygame.transform.flip(self.hit_right[i], True, False) for i in range(4)]

        # Use passed player animations directly (no tinting)
        self.idle_right = idle_right or []
        self.walk_right = walk_right or []
        self.idle_left = [pygame.transform.flip(self.idle_right[i], True, False) for i in range(8)]
        self.walk_left = [pygame.transform.flip(self.walk_right[i], True, False) for i in range(8)]

    def take_damage(self, damage):
        if self.health > 0:  # Only trigger hit animation if alive
            self.health -= damage
            if self.is_fighting:
                self.is_fighting = False  # Stop combo animation if active
            if not self.is_hit:  # Start hit animation only if not already playing
                self.is_hit = True
                self.hit_value = 0
            if self.health <= 0:
                self.health = 0
                self.stunned = False  # No stun after death
            else:
                self.stunned = True  # Stun on hit if still alive
                self.stun_timer = self.stun_duration

    def check_attack_hit(self, player_world_x, player):
        if self.is_fighting:
            # Adjust hitbox center based on facing direction
            if self.facing_left:
                hitbox_center = self.world_x + self.width / 2 - 200  # Shift left
            else:
                hitbox_center = self.world_x + self.width / 2 + 200  # Shift right
            hitbox_left = hitbox_center - self.attack_range / 2
            hitbox_right = hitbox_center + self.attack_range / 2

            # Apply damage on frames 1, 6, 16
            player_center = player_world_x + self.width / 2  # Assuming player width is same as enemy
            if int(self.fight_value) in [1, 6, 16]:
                if hitbox_left <= player_center <= hitbox_right:
                    print(f"Enemy attacks player for {self.attack_damage} damage on frame {int(self.fight_value)}!")
                    # Assuming player has a take_damage method
                    if player:
                        player.take_damage(self.attack_damage)

    def update_animation(self):
        if self.is_hit:
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
        else:
            self.value += self.current_speed
            if self.value >= 8:  # Loop idle/walk animation
                self.value -= 8

    def update_movement(self, player_world_x, player=None):
        if not self.stunned and self.health > 0:
            # Calculate distance to player
            distance_to_player = abs(player_world_x - self.world_x)
            print(f"Enemy at world_x: {self.world_x}, Direction: {self.direction}, Distance to player: {distance_to_player}, Animation speed: {self.current_speed}")

            # Manage attack cooldown
            if self.attack_timer > 0:
                self.attack_timer -= 1

            if distance_to_player > 500:  # Patrol if player is far
                print(f"Patrolling: Initial x: {self.initial_x}, Patrol range: {self.initial_x - self.patrol_range} to {self.initial_x + self.patrol_range}")
                self.at_minimum_distance = False  # Reset when far from player
                self.patrol_center = None
                # Update position
                self.world_x += self.speed * self.direction
                # Immediately enforce patrol boundaries
                if self.world_x >= self.initial_x + self.patrol_range:
                    print(f"Hit max range at world_x: {self.world_x}, clamping to {self.initial_x + self.patrol_range}")
                    self.world_x = self.initial_x + self.patrol_range  # Clamp at max
                    self.direction = -1  # Turn left
                    self.facing_left = True
                    print("Turning left at max range")
                elif self.world_x <= self.initial_x - self.patrol_range:
                    print(f"Hit min range at world_x: {self.world_x}, clamping to {self.initial_x - self.patrol_range}")
                    self.world_x = self.initial_x - self.patrol_range  # Clamp at min
                    self.direction = 1  # Turn right
                    self.facing_left = False
                    print("Turning right at min range")
                self.current_speed = self.animation_speed["walk"]  # Walk during patrol
            else:  # Engage player if within 500 units
                print("Engaging player")
                # Determine target position to stop at minimum distance
                if player_world_x < self.world_x:
                    target_x = player_world_x + self.minimum_distance  # Stop to the right of player
                    self.facing_left = True
                else:
                    target_x = player_world_x - self.minimum_distance  # Stop to the left of player
                    self.facing_left = False

                # Check if enemy is within minimum distance
                if abs(self.world_x - player_world_x) <= self.minimum_distance:
                    self.at_minimum_distance = True
                    self.patrol_center = target_x  # Set patrol center at the stopping point
                else:
                    self.at_minimum_distance = False

                if not self.at_minimum_distance:
                    # Move toward the target position
                    if self.world_x > target_x:
                        self.world_x -= self.speed  # Move left toward target
                        self.direction = -1
                        print("Moving left toward player")
                    else:
                        self.world_x += self.speed  # Move right toward target
                        self.direction = 1
                        print("Moving right toward player")
                    self.current_speed = self.animation_speed["walk"]
                else:
                    # Attack the player instead of patrolling
                    if not self.is_fighting and self.attack_timer == 0:
                        self.is_fighting = True
                        self.fight_value = 0
                        self.attack_timer = self.attack_cooldown
                    self.current_speed = self.animation_speed["idle"]  # Idle while attacking

        if self.stunned and self.health > 0:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False

    def draw(self, win, scroll_offset):
        enemy_screen_x = self.world_x - scroll_offset
        if -self.width <= enemy_screen_x <= win.get_width():  # Only draw if visible
            if self.is_hit:
                hit_sprite = self.hit_left[int(self.hit_value)] if self.facing_left else self.hit_right[int(self.hit_value)]
                win.blit(hit_sprite, (enemy_screen_x, 250))  # Adjust y-position as needed
            elif self.is_fighting:
                fight_sprite = self.fight_left[int(self.fight_value)] if self.facing_left else self.fight_right[int(self.fight_value)]
                win.blit(fight_sprite, (enemy_screen_x, 250))  # Adjust y-position as needed
            else:
                if self.current_speed == self.animation_speed["walk"]:
                    sprite = self.walk_left[int(self.value)] if self.facing_left else self.walk_right[int(self.value)]
                else:  # idle
                    sprite = self.idle_left[int(self.value)] if self.facing_left else self.idle_right[int(self.value)]
                if sprite:  # Ensure sprite exists before blitting
                    win.blit(sprite, (enemy_screen_x, 250))  # Adjust y-position as needed