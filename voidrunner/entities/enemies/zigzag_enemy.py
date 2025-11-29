"""
Zigzag Enemy implementation.

Moves downward while oscillating horizontally in a sine wave pattern.
"""

import math
import pygame

from ...utils import config
from ..enemy import Enemy


class ZigzagEnemy(Enemy):
    """
    Zigzag enemy type that oscillates horizontally while descending.

    This enemy moves in a zigzag pattern, making it harder to predict
    and requiring more precise aim to hit.
    """

    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        """
        Initialize a zigzag enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
        """
        speed = config.ENEMY_BASE_SPEED * config.ZIGZAG_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.ZIGZAG_ENEMY_HEALTH,
            speed=speed,
            score_value=config.ZIGZAG_ENEMY_POINTS,
            sprite=sprite,
        )
        
        # Zigzag enemies can shoot
        self.can_shoot = True
        
        # Zigzag specific properties
        self.base_x = x  # Original x position (center of oscillation)
        self.time_alive = 0.0  # Track time for sine wave
        self.amplitude = 100.0  # How far left/right to oscillate
        self.frequency = 2.0  # Speed of oscillation

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update zigzag enemy behavior (oscillates horizontally while moving down).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position (unused for zigzag enemy)
        """
        # Update time
        self.time_alive += dt
        
        # Calculate zigzag motion using sine wave
        # X position oscillates around base_x
        target_x = self.base_x + self.amplitude * math.sin(self.time_alive * self.frequency)
        
        # Set velocity: move down and adjust x to reach target
        self.velocity.y = self.speed
        
        # Smooth x movement toward target position
        x_diff = target_x - self.position.x
        self.velocity.x = x_diff * 3.0  # Adjust multiplier for smoothness

