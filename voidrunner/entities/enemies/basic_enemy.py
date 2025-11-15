"""
Basic Enemy implementation.

Moves straight down and shoots occasionally.
Reference: PRD Section 2.2 - Enemy System
"""

import pygame

from ...utils import config
from ..enemy import Enemy


class BasicEnemy(Enemy):
    """
    Basic enemy type that moves straight down.

    This is the simplest enemy type, moving vertically downward
    and occasionally shooting at the player.
    """

    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        """
        Initialize a basic enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
        """
        speed = config.ENEMY_BASE_SPEED * config.BASIC_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.BASIC_ENEMY_HEALTH,
            speed=speed,
            score_value=config.BASIC_ENEMY_POINTS,
            sprite=sprite,
        )
        
        # Basic enemies can shoot
        self.can_shoot = True
        
        # Set initial velocity (moving down)
        self.velocity = pygame.Vector2(0, self.speed)

    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update basic enemy behavior (moves straight down).

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position (unused for basic enemy)
        """
        # Basic enemy just continues moving down
        # Velocity is already set in __init__
        pass

