"""
Player entity class.

Represents the player's spaceship with movement, shooting, and damage.
"""

import pygame

from ..utils import config


class Player(pygame.sprite.Sprite):
    """
    Player spaceship sprite.

    Handles movement, shooting, health/shield management, and power-ups.
    """

    def __init__(
        self, x: float, y: float, sprite: pygame.Surface, bullet_sprite: pygame.Surface
    ) -> None:
        """
        Initialize the player.

        Args:
            x: Starting x position
            y: Starting y position
            sprite: Pygame surface for player rendering
            bullet_sprite: Pygame surface for player bullets
        """
        super().__init__()
        
        self.original_image = sprite.copy()  # Store original for damage flash
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        # Stats (renamed: shield->health, health->lives)
        self.lives = config.PLAYER_MAX_LIVES
        self.health = config.PLAYER_MAX_HEALTH
        self.max_lives = config.PLAYER_MAX_LIVES
        self.max_health = config.PLAYER_MAX_HEALTH
        
        # Shooting
        self.shoot_cooldown = 0.0
        self.base_shoot_cooldown = config.PLAYER_SHOOT_COOLDOWN
        self.current_shoot_cooldown = self.base_shoot_cooldown
        self.bullet_sprite = bullet_sprite
        
        # Damage state
        self.invincible = False
        self.invincibility_timer = 0.0
        self.damage_flash_timer = 0.0
        self.time_since_damage = 0.0  # For health regen delay
        
        # Power-ups (will be managed by PowerUp classes)
        self.active_powerups: list = []
        
        # Stats tracking
        self.kill_streak = 0

    def update(self, dt: float, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """
        Update player state.

        Args:
            dt: Delta time in seconds
            keys_pressed: Pygame key state
        """
        self._handle_movement(dt, keys_pressed)
        self._update_shooting_cooldown(dt)
        self._update_invincibility(dt)
        self._update_health_regen(dt)
        self._constrain_to_screen()
        
        # Update rect position
        self.rect.center = (int(self.position.x), int(self.position.y))

    def _handle_movement(
        self, dt: float, keys_pressed: pygame.key.ScancodeWrapper
    ) -> None:
        """
        Handle player movement based on input.

        Args:
            dt: Delta time in seconds
            keys_pressed: Pygame key state
        """
        # Reset velocity
        self.velocity.x = 0
        self.velocity.y = 0
        
        # WASD or Arrow keys
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            self.velocity.y = -config.PLAYER_SPEED
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.velocity.y = config.PLAYER_SPEED
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            self.velocity.x = -config.PLAYER_SPEED
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            self.velocity.x = config.PLAYER_SPEED
        
        # Normalize diagonal movement
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * config.PLAYER_SPEED
        
        # Apply movement
        self.position += self.velocity * dt * 60  # Scale for 60 FPS reference

    def _update_shooting_cooldown(self, dt: float) -> None:
        """
        Update shooting cooldown timer.

        Args:
            dt: Delta time in seconds
        """
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def _update_invincibility(self, dt: float) -> None:
        """
        Update invincibility frames after taking damage.

        Args:
            dt: Delta time in seconds
        """
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
        
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            if self.damage_flash_timer <= 0:
                # Restore original image
                self.image = self.original_image.copy()

    def _update_health_regen(self, dt: float) -> None:
        """
        Regenerate health over time (only after delay since last damage).

        Args:
            dt: Delta time in seconds
        """
        # Increment time since last damage
        self.time_since_damage += dt
        
        # Only regenerate if enough time has passed and health is not full
        if (self.time_since_damage >= config.PLAYER_HEALTH_REGEN_DELAY and 
            self.health < self.max_health and
            config.PLAYER_HEALTH_REGEN_RATE > 0):
            self.health += config.PLAYER_HEALTH_REGEN_RATE * dt
            self.health = min(self.health, self.max_health)

    def _constrain_to_screen(self) -> None:
        """Keep player within screen boundaries."""
        half_width = self.rect.width // 2
        half_height = self.rect.height // 2
        
        self.position.x = max(half_width, min(self.position.x, config.SCREEN_WIDTH - half_width))
        self.position.y = max(half_height, min(self.position.y, config.SCREEN_HEIGHT - half_height))

    def can_shoot(self) -> bool:
        """
        Check if player can shoot (cooldown elapsed).

        Returns:
            True if shooting is allowed
        """
        return self.shoot_cooldown <= 0

    def shoot(self) -> "Bullet":
        """
        Create a bullet from the player's position.

        Returns:
            Bullet sprite moving upward
        """
        from .bullet import Bullet
        
        # Reset cooldown
        self.shoot_cooldown = self.current_shoot_cooldown
        
        # Create bullet moving upward
        bullet_velocity = pygame.Vector2(0, -config.BULLET_SPEED)
        bullet = Bullet(
            self.rect.centerx,
            self.rect.top,
            bullet_velocity,
            "player",
            self.bullet_sprite,
        )
        
        return bullet

    def take_damage(self, amount: float) -> bool:
        """
        Apply damage to player (health first, then lose a life).

        Args:
            amount: Damage to apply

        Returns:
            True if player died (all lives lost), False otherwise
        """
        if self.invincible:
            return False
        
        # Reset time since damage for regen
        self.time_since_damage = 0.0
        
        # Apply damage to health
        self.health -= amount
        
        # If health depleted, lose a life and reset health
        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                # Still have lives left, reset health
                self.health = self.max_health
            else:
                # Out of lives
                self.health = 0
                return True
        
        # Reset kill streak
        self.kill_streak = 0
        
        # Trigger invincibility
        self.invincible = True
        self.invincibility_timer = config.PLAYER_INVINCIBILITY_DURATION
        self.damage_flash_timer = config.DAMAGE_FLASH_DURATION
        
        return False

    def add_kill_to_streak(self) -> None:
        """Increment kill streak counter."""
        self.kill_streak += 1

    def is_alive(self) -> bool:
        """
        Check if player is still alive.

        Returns:
            True if lives > 0
        """
        return self.lives > 0

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the player with damage flash effect.

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
            pygame.draw.rect(screen, config.COLOR_GREEN, self.rect, 2)

