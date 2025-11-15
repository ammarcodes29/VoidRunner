"""
Playing state - main gameplay.

Handles active gameplay with player control, enemies, and combat.
"""

import pygame

from ..entities.player import Player
from ..managers.collision_manager import CollisionManager
from ..managers.spawn_manager import SpawnManager
from ..ui.hud import HUD
from ..utils import config
from .base_state import BaseState


class PlayingState(BaseState):
    """
    Active gameplay state.

    Manages player, enemies, bullets, collisions, and wave progression.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initialize the playing state.

        Args:
            game: Reference to the main Game object
        """
        super().__init__(game)
        
        # Managers
        self.spawn_manager = SpawnManager(game.asset_manager)
        self.collision_manager = CollisionManager(game.asset_manager)
        
        # Sprite groups
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        # Player
        player_sprite = game.asset_manager.get_sprite("player")
        bullet_sprite = game.asset_manager.get_sprite("player_bullet")
        self.player = Player(
            config.SCREEN_WIDTH // 2,
            config.SCREEN_HEIGHT - 100,
            player_sprite,
            bullet_sprite,
        )
        self.all_sprites.add(self.player)
        
        # UI
        hud_font = game.asset_manager.get_font("hud")
        self.hud = HUD(hud_font)
        
        # Game state
        self.score = 0
        self.game_over = False
        self.wave_transition_timer = 0.0
        self.in_wave_transition = False
        
        # Background
        self.background = game.asset_manager.get_sprite("background")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle input events.

        Args:
            events: List of pygame events from this frame
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # TODO: Transition to pause state
                    pass
                elif event.key == pygame.K_SPACE:
                    # Shoot
                    if self.player.can_shoot():
                        bullet = self.player.shoot()
                        self.player_bullets.add(bullet)
                        self.all_sprites.add(bullet)
                        self.game.asset_manager.play_sound("player_shoot")

    def update(self, dt: float) -> None:
        """
        Update gameplay logic.

        Args:
            dt: Delta time in seconds since last frame
        """
        if self.game_over:
            # TODO: Transition to game over state
            return
        
        # Handle wave transitions
        if self.in_wave_transition:
            self._update_wave_transition(dt)
            return
        
        # Get key state for continuous movement
        keys = pygame.key.get_pressed()
        
        # Update player
        self.player.update(dt, keys)
        
        # Handle continuous shooting (hold spacebar)
        if keys[pygame.K_SPACE] and self.player.can_shoot():
            bullet = self.player.shoot()
            self.player_bullets.add(bullet)
            self.all_sprites.add(bullet)
            self.game.asset_manager.play_sound("player_shoot")
        
        # Update spawn manager
        self.spawn_manager.update(dt, self.enemies)
        
        # Update bullets
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.position)
            
            # Check if enemy should shoot
            if enemy.should_shoot():
                bullet_sprite = self.game.asset_manager.get_sprite("enemy_bullet")
                bullet = enemy.create_bullet(bullet_sprite)
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.game.asset_manager.play_sound("enemy_shoot")
        
        # Check collisions
        points_earned, player_died = self.collision_manager.check_all_collisions(
            self.player,
            self.player_bullets,
            self.enemies,
            self.enemy_bullets,
        )
        
        self.score += points_earned
        
        if player_died:
            self.game_over = True
        
        # Check for wave completion
        if self.spawn_manager.is_wave_complete(self.enemies):
            self._start_wave_transition()

    def _update_wave_transition(self, dt: float) -> None:
        """
        Handle wave transition delay.

        Args:
            dt: Delta time in seconds
        """
        self.wave_transition_timer += dt
        
        if self.wave_transition_timer >= config.WAVE_CLEAR_DELAY:
            self.spawn_manager.advance_wave()
            self.in_wave_transition = False
            self.wave_transition_timer = 0.0

    def _start_wave_transition(self) -> None:
        """Start the wave transition delay."""
        self.in_wave_transition = True
        self.wave_transition_timer = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the gameplay.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw all sprites
        self.player.draw(screen)
        
        for bullet in self.player_bullets:
            bullet.draw(screen)
        
        for bullet in self.enemy_bullets:
            bullet.draw(screen)
        
        for enemy in self.enemies:
            enemy.draw(screen)
        
        # Draw HUD
        self.hud.draw(
            screen,
            self.score,
            self.player,
            self.spawn_manager.get_wave_number(),
        )
        
        # Draw wave transition message
        if self.in_wave_transition:
            self._draw_wave_transition_message(screen)
        
        # Draw game over message
        if self.game_over:
            self._draw_game_over_message(screen)

    def _draw_wave_transition_message(self, screen: pygame.Surface) -> None:
        """
        Draw wave complete message.

        Args:
            screen: Pygame surface to draw on
        """
        font = self.game.asset_manager.get_font("menu")
        
        wave_text = f"Wave {self.spawn_manager.get_wave_number()} Complete!"
        text_surface = font.render(wave_text, True, config.COLOR_YELLOW)
        
        text_rect = text_surface.get_rect()
        text_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        
        # Semi-transparent background
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(config.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        screen.blit(text_surface, text_rect)

    def _draw_game_over_message(self, screen: pygame.Surface) -> None:
        """
        Draw game over message.

        Args:
            screen: Pygame surface to draw on
        """
        font = self.game.asset_manager.get_font("menu")
        
        # Game Over text
        game_over_text = "GAME OVER"
        text_surface = font.render(game_over_text, True, config.COLOR_RED)
        text_rect = text_surface.get_rect()
        text_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 50)
        
        # Final score
        score_font = self.game.asset_manager.get_font("hud")
        score_text = f"Final Score: {self.score}"
        score_surface = score_font.render(score_text, True, config.COLOR_WHITE)
        score_rect = score_surface.get_rect()
        score_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 20)
        
        # Instructions
        restart_text = "Press R to Restart or ESC to Quit"
        restart_surface = score_font.render(restart_text, True, config.COLOR_GRAY)
        restart_rect = restart_surface.get_rect()
        restart_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 60)
        
        # Semi-transparent background
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(config.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        screen.blit(text_surface, text_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(restart_surface, restart_rect)

