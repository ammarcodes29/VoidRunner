"""
Chaser Enemy implementation.

Tracks and moves toward the player's position.
"""

import pygame

from ...utils import config
from ..enemy import Enemy


class ChaserEnemy(Enemy):
    """
    Chaser enemy type that follows the player.

    This enemy actively tracks the player's position and adjusts
    its movement to chase them, making it more challenging to avoid.
    """

    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        """
        Initialize a chaser enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
        """
        speed = config.ENEMY_BASE_SPEED * config.CHASER_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.CHASER_ENEMY_HEALTH,
            speed=speed,
            score_value=config.CHASER_ENEMY_POINTS,
            sprite=sprite,
        )
        
        # Chaser enemies can shoot
        self.can_shoot = True

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update chaser enemy behavior (moves toward player).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position
        """
        # Calculate direction to player
        direction = player_pos - self.position
        
        # Normalize and scale to speed (only if not zero vector)
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * self.speed
        else:
            # If somehow at exact player position, just move down
            self.velocity = pygame.Vector2(0, self.speed)

