"""
Bullet entity class.

Represents projectiles fired by player or enemies.
"""

from typing import Literal

import pygame

from ..utils import config


class Bullet(pygame.sprite.Sprite):
    """
    Bullet sprite for player and enemy projectiles.

    Uses the owner property to distinguish between player and enemy bullets
    for collision detection purposes.
    """

    def __init__(
        self,
        x: float,
        y: float,
        velocity: pygame.Vector2,
        owner: Literal["player", "enemy"],
        sprite: pygame.Surface,
    ) -> None:
        """
        Initialize a bullet.

        Args:
            x: Starting x position
            y: Starting y position
            velocity: Velocity vector (direction and speed)
            owner: Who fired this bullet ('player' or 'enemy')
            sprite: Pygame surface for rendering
        """
        super().__init__()
        
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.owner = owner
        self.damage = config.BULLET_DAMAGE

    def update(self, dt: float) -> None:
        """
        Update bullet position.

        Args:
            dt: Delta time in seconds
        """
        # Move based on velocity and delta time
        self.position += self.velocity * dt * 60  # Scale for 60 FPS reference
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Despawn if off-screen
        if self._is_off_screen():
            self.kill()

    def _is_off_screen(self) -> bool:
        """
        Check if bullet has left the screen boundaries.

        Returns:
            True if bullet is off-screen
        """
        return (
            self.rect.right < 0
            or self.rect.left > config.SCREEN_WIDTH
            or self.rect.bottom < 0
            or self.rect.top > config.SCREEN_HEIGHT
        )

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the bullet.

        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.image, self.rect)

