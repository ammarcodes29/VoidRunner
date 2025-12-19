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
        
        # Sprite is already scaled by BOSS_SIZE_MULTIPLIER in AssetManager
        # No additional scaling needed here
        
        super().__init__(
            x=x,
            y=y,
            health=health,
            speed=config.BOSS_MOVEMENT_SPEED,
            score_value=score_value,
            sprite=sprite,
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
        # Use smooth interpolation instead of velocity-based movement to prevent oscillation
        delay_factor = 2.0  # How quickly boss tracks player (lower = more delay)
        self.target_x += (player_pos.x - self.target_x) * delay_factor * dt
        
        # Smoothly interpolate position towards target (prevents oscillation)
        # Use direct position lerp instead of velocity to ensure stability
        lerp_speed = 3.0  # How quickly boss moves to target position
        lerp_factor = min(1.0, lerp_speed * dt)  # Clamp to prevent overshoot
        
        # Directly interpolate position (stable, no oscillation)
        self.position.x += (self.target_x - self.position.x) * lerp_factor
        
        # Set velocity to 0 since we're moving position directly
        # (velocity is still used by base class but we override the movement)
        self.velocity.x = 0
        
        # STAY at top - no vertical movement once in position
        target_y = 120  # Fixed Y position at top with breathing room
        
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

