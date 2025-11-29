"""
Chaser Enemy implementation.

Tracks and moves toward the player's position with zigzag pattern.
"""

import math
import pygame

from ...utils import config
from ..enemy import Enemy


class ChaserEnemy(Enemy):
    """
    Chaser enemy type that follows the player while oscillating.

    This enemy actively tracks the player's position and adjusts
    its movement to chase them, but adds a zigzag oscillation pattern
    to make it more challenging and visually interesting.
    """

    def __init__(
        self,
        x: float,
        y: float,
        sprite: pygame.Surface,
        bullet_speed_multiplier: float = 1.0,
        fire_rate_multiplier: float = 1.0,
    ) -> None:
        """
        Initialize a chaser enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
            bullet_speed_multiplier: Difficulty scaling for bullet speed
            fire_rate_multiplier: Difficulty scaling for fire rate
        """
        speed = config.ENEMY_BASE_SPEED * config.CHASER_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.CHASER_ENEMY_HEALTH,
            speed=speed,
            score_value=config.CHASER_ENEMY_POINTS,
            sprite=sprite,
            bullet_speed_multiplier=bullet_speed_multiplier,
            fire_rate_multiplier=fire_rate_multiplier,
        )
        
        # Chaser enemies can shoot
        self.can_shoot = True
        
        # Oscillation properties for zigzag effect while chasing
        self.time_alive = 0.0
        self.oscillation_amplitude = 30.0  # Smaller than pure zigzag
        self.oscillation_frequency = 4.0   # Faster oscillation

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update chaser enemy behavior (chases player with zigzag pattern).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position
        """
        # Update time for oscillation
        self.time_alive += dt
        
        # Calculate base direction to player
        direction = player_pos - self.position
        
        # Normalize and scale to speed
        if direction.length() > 0:
            direction = direction.normalize()
            base_velocity = direction * self.speed
            
            # Add oscillation perpendicular to direction
            perpendicular = pygame.Vector2(-direction.y, direction.x)
            oscillation = perpendicular * self.oscillation_amplitude * math.sin(
                self.time_alive * self.oscillation_frequency
            ) / 10.0  # Divide to make subtle
            
            self.velocity = base_velocity + oscillation
        else:
            # If at exact player position, just move down
            self.velocity = pygame.Vector2(0, self.speed)

