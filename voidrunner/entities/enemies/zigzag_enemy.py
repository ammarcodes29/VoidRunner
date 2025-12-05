"""
Zigzag Enemy implementation.

Moves straight downward while oscillating horizontally (pure zigzag, no player tracking).
"""

import math
import pygame

from ...utils import config
from ..enemy import Enemy


class ZigzagEnemy(Enemy):
    """
    Zigzag enemy type that oscillates horizontally while descending.

    This enemy moves in a predictable zigzag pattern without tracking
    the player, making it easier to predict but harder to aim at.
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
        Initialize a zigzag enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
            bullet_speed_multiplier: Difficulty scaling for bullet speed
            fire_rate_multiplier: Difficulty scaling for fire rate
        """
        speed = config.ENEMY_BASE_SPEED * config.ZIGZAG_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.ZIGZAG_ENEMY_HEALTH,
            speed=speed,
            score_value=config.ZIGZAG_ENEMY_POINTS,
            sprite=sprite,
            bullet_speed_multiplier=bullet_speed_multiplier,
            fire_rate_multiplier=fire_rate_multiplier,
        )
        
        # Zigzag enemies can shoot
        self.can_shoot = True
        
        # Zigzag specific properties
        self.base_x = x  # Original x position (center of oscillation)
        self.time_alive = 0.0  # Track time for sine wave
        self.amplitude = 120.0  # How far left/right to oscillate
        self.frequency = 2.5  # Speed of oscillation

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update zigzag enemy behavior (pure zigzag motion, ignores player).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position (intentionally unused)
        """
        # Update time
        self.time_alive += dt
        
        # Pure zigzag: constant downward movement + sine wave horizontal
        self.velocity.y = self.speed
        
        # X velocity based on derivative of sine wave for smooth motion
        # dx/dt = amplitude * frequency * cos(frequency * time)
        self.velocity.x = (self.amplitude * self.frequency * 
                          math.cos(self.time_alive * self.frequency))

