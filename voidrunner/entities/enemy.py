"""
Enemy base class.

Abstract base for all enemy types with polymorphic behavior.
"""

from abc import ABC, abstractmethod

import pygame

from ..utils import config


class Enemy(pygame.sprite.Sprite, ABC):
    """
    Abstract base class for all enemy types.

    Subclasses implement specific movement behaviors and attack patterns.
    """

    def __init__(
        self,
        x: float,
        y: float,
        health: int,
        speed: float,
        score_value: int,
        sprite: pygame.Surface,
    ) -> None:
        """
        Initialize an enemy.

        Args:
            x: Starting x position
            y: Starting y position
            health: Enemy health points
            speed: Movement speed
            score_value: Points awarded for killing this enemy
            sprite: Pygame surface for rendering
        """
        super().__init__()
        
        self.original_image = sprite.copy()  # Store original for damage flash
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.health = health
        self.max_health = health
        self.speed = speed
        self.score_value = score_value
        
        # Shooting (some enemies shoot)
        self.can_shoot = False
        self.shoot_timer = 0.0
        
        # Damage flash effect
        self.damage_flash_timer = 0.0

    @abstractmethod
    def update_behavior(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update enemy-specific behavior.

        This method should be overridden by subclasses to implement
        unique movement patterns.

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position
        """
        pass

    def update(self, dt: float, player_pos: pygame.Vector2) -> None:
        """
        Update enemy state.

        Args:
            dt: Delta time in seconds
            player_pos: Player's current position
        """
        # Call subclass-specific behavior
        self.update_behavior(dt, player_pos)
        
        # Apply movement
        self.position += self.velocity * dt * 60  # Scale for 60 FPS reference
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Update shooting timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        # Update damage flash timer
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            if self.damage_flash_timer <= 0:
                # Restore original image
                self.image = self.original_image.copy()
        
        # Despawn if off-screen
        if self._is_off_screen():
            self.kill()

    def _is_off_screen(self) -> bool:
        """
        Check if enemy has left the screen boundaries.

        Returns:
            True if enemy is completely off-screen
        """
        return (
            self.rect.top > config.SCREEN_HEIGHT + 50  # Below screen
            or self.rect.bottom < -50  # Above screen
            or self.rect.right < -50  # Left of screen
            or self.rect.left > config.SCREEN_WIDTH + 50  # Right of screen
        )

    def take_damage(self, amount: int) -> bool:
        """
        Apply damage to enemy.

        Args:
            amount: Damage to apply

        Returns:
            True if enemy died, False otherwise
        """
        self.health -= amount
        
        # Trigger damage flash if still alive
        if self.health > 0:
            self.damage_flash_timer = config.DAMAGE_FLASH_DURATION
        
        return self.health <= 0

    def should_shoot(self) -> bool:
        """
        Determine if enemy should shoot this frame.

        Returns:
            True if enemy can and should shoot
        """
        if not self.can_shoot:
            return False
        
        if self.shoot_timer <= 0:
            # Random chance to shoot
            import random
            if random.random() < config.BASIC_ENEMY_SHOOT_CHANCE:
                self.shoot_timer = 2.0  # Cooldown between shots
                return True
        
        return False

    def create_bullet(self, bullet_sprite: pygame.Surface) -> "Bullet":
        """
        Create a bullet fired by this enemy.

        Args:
            bullet_sprite: Pygame surface for bullet rendering

        Returns:
            Bullet sprite moving downward
        """
        from .bullet import Bullet
        
        bullet_velocity = pygame.Vector2(0, config.ENEMY_BULLET_SPEED)
        bullet = Bullet(
            self.rect.centerx,
            self.rect.bottom,
            bullet_velocity,
            "enemy",
            bullet_sprite,
        )
        
        return bullet

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the enemy with damage flash effect.

        Args:
            screen: Pygame surface to draw on
        """
        # Flash red during damage
        if self.damage_flash_timer > 0:
            # Create red-tinted version
            red_surface = self.original_image.copy()
            red_overlay = pygame.Surface(red_surface.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 128))  # Red with 50% alpha
            red_surface.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = red_surface
        
        screen.blit(self.image, self.rect)
        
        # Debug: Draw collision box
        if config.DEBUG_MODE and config.SHOW_COLLISION_BOXES:
            pygame.draw.rect(screen, config.COLOR_RED, self.rect, 2)

