"""
Basic Enemy implementation.

Moves straight down and shoots occasionally.
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

    def __init__(
        self,
        x: float,
        y: float,
        sprite: pygame.Surface,
        bullet_speed_multiplier: float = 1.0,
        fire_rate_multiplier: float = 1.0,
    ) -> None:
        """
        Initialize a basic enemy.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for rendering
            bullet_speed_multiplier: Difficulty scaling for bullet speed
            fire_rate_multiplier: Difficulty scaling for fire rate
        """
        speed = config.ENEMY_BASE_SPEED * config.BASIC_ENEMY_SPEED_MULT
        super().__init__(
            x=x,
            y=y,
            health=config.BASIC_ENEMY_HEALTH,
            speed=speed,
            score_value=config.BASIC_ENEMY_POINTS,
            sprite=sprite,
            bullet_speed_multiplier=bullet_speed_multiplier,
            fire_rate_multiplier=fire_rate_multiplier,
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

