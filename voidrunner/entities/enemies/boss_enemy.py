"""
Boss Enemy implementation.

Large, powerful enemy that appears every 5 waves with special attack patterns.
"""

import math
import pygame

from ...utils import config
from ..enemy import Enemy


class BossEnemy(Enemy):
    """
    Boss enemy type with high health and penta-shot attack.

    Appears every 5 waves (5, 10, 15, 20...) with scaling difficulty.
    """

    def __init__(self, x: float, y: float, sprite: pygame.Surface, boss_level: int = 1) -> None:
        """
        Initialize a boss enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering (will be scaled)
            boss_level: Which boss this is (1 = first, 2 = second, etc.)
        """
        # Calculate boss stats based on level
        health = int(config.BOSS_BASE_HEALTH * (config.BOSS_HEALTH_MULTIPLIER ** (boss_level - 1)))
        score_value = config.BOSS_POINTS * boss_level
        
        # Scale sprite to be larger
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(sprite.get_width() * config.BOSS_SIZE_MULTIPLIER),
             int(sprite.get_height() * config.BOSS_SIZE_MULTIPLIER))
        )
        
        super().__init__(
            x=x,
            y=y,
            health=health,
            speed=config.BOSS_MOVEMENT_SPEED,
            score_value=score_value,
            sprite=scaled_sprite,
        )
        
        # Boss specific properties
        self.boss_level = boss_level
        self.can_shoot = True
        
        # Movement pattern (horizontal tracking with delay)
        self.base_x = x
        self.time_alive = 0.0
        self.target_x = x  # Target position to move towards (creates delay)
        self.movement_range = config.BOSS_MOVEMENT_RANGE
        
        # Boss shooting properties (scales with level)
        self.fire_rate = config.BOSS_BASE_FIRE_RATE * (config.BOSS_FIRE_RATE_DECREASE ** (boss_level - 1))
        self.bullet_speed_multiplier = config.BOSS_BULLET_SPEED_MULTIPLIER ** (boss_level - 1)
        self.shoot_timer = self.fire_rate  # Start ready to shoot

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update boss enemy behavior (stays at top, follows player with delay).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position
        """
        # Update time
        self.time_alive += dt
        
        # Update target position gradually towards player (creates delay effect)
        delay_factor = 2.5  # Lower = more delay, Higher = faster response
        self.target_x += (player_pos.x - self.target_x) * delay_factor * dt
        
        # Move towards the delayed target position with capped speed
        x_diff = self.target_x - self.position.x
        max_speed = 200.0  # Cap horizontal speed to prevent overflow
        
        # Calculate velocity and clamp it
        desired_velocity_x = x_diff * 3.0
        self.velocity.x = max(-max_speed, min(max_speed, desired_velocity_x))
        
        # STAY at top - no vertical movement once in position
        target_y = 100  # Fixed Y position at top
        
        # Only move down if above target, otherwise lock in place
        if self.position.y < target_y:
            self.velocity.y = 2.0  # Move down to position
        else:
            self.velocity.y = 0  # Lock at top, don't descend
            self.position.y = target_y  # Hard lock position

    def should_shoot(self) -> bool:
        """
        Boss shoots on a timer instead of randomly.

        Returns:
            True if boss should shoot
        """
        if self.shoot_timer <= 0:
            self.shoot_timer = self.fire_rate
            return True
        return False

    def create_penta_shot(self, bullet_sprite: pygame.Surface) -> list:
        """
        Create 5 bullets spread evenly in a fan pattern.

        Args:
            bullet_sprite: Pygame surface for bullet rendering

        Returns:
            List of 5 Bullet sprites in fan formation
        """
        from ..bullet import Bullet
        
        bullets = []
        base_speed = config.ENEMY_BULLET_SPEED * self.bullet_speed_multiplier
        
        # Create 5 bullets with different angles
        # Angles: -30°, -15°, 0°, 15°, 30° (in radians)
        angles = [-0.524, -0.262, 0, 0.262, 0.524]  # Radians
        
        for angle in angles:
            # Calculate velocity with angle
            velocity = pygame.Vector2(
                math.sin(angle) * base_speed,
                base_speed  # Downward component
            )
            
            bullet = Bullet(
                self.rect.centerx,
                self.rect.bottom,
                velocity,
                "enemy",
                bullet_sprite,
            )
            bullets.append(bullet)
        
        return bullets

    def create_bullet(self, bullet_sprite: pygame.Surface):
        """
        Override to return penta-shot instead of single bullet.

        Args:
            bullet_sprite: Pygame surface for bullet rendering

        Returns:
            List of bullets (penta-shot pattern)
        """
        return self.create_penta_shot(bullet_sprite)

