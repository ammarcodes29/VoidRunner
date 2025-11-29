"""
Hit Effect sprite for collision visual feedback.

Displays briefly at collision points before disappearing.
"""

import pygame


class HitEffect(pygame.sprite.Sprite):
    """
    Visual effect displayed at bullet collision points.
    
    Automatically despawns after a short duration.
    """

    def __init__(self, x: float, y: float, sprite: pygame.Surface, lifetime: float = 0.15) -> None:
        """
        Initialize a hit effect.

        Args:
            x: X position
            y: Y position
            sprite: Pygame surface for rendering
            lifetime: How long the effect lasts in seconds
        """
        super().__init__()
        
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.lifetime = lifetime
        self.time_alive = 0.0

    def update(self, dt: float) -> None:
        """
        Update the effect lifetime.

        Args:
            dt: Delta time in seconds
        """
        self.time_alive += dt
        
        # Remove effect when lifetime expires
        if self.time_alive >= self.lifetime:
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the hit effect.

        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.image, self.rect)

