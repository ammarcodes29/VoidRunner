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
        self.hit_effects = pygame.sprite.Group()
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
        self.is_new_high_score = False
        
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
                if self.game_over:
                    # Handle game over input
                    if event.key == pygame.K_r:
                        # Restart game
                        self._restart_game()
                    elif event.key == pygame.K_m:
                        # Return to menu
                        self._return_to_menu()
                    elif event.key == pygame.K_ESCAPE:
                        # Quit game
                        self.game.running = False
                else:
                    # Normal gameplay input
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
        
        # Update hit effects
        self.hit_effects.update(dt)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.position)
            
            # Check if enemy should shoot
            if enemy.should_shoot():
                bullet_sprite = self.game.asset_manager.get_sprite("enemy_bullet")
                bullets = enemy.create_bullet(bullet_sprite)
                
                # Boss returns list of bullets (penta-shot), regular enemies return single bullet
                if isinstance(bullets, list):
                    for bullet in bullets:
                        self.enemy_bullets.add(bullet)
                        self.all_sprites.add(bullet)
                else:
                    self.enemy_bullets.add(bullets)
                    self.all_sprites.add(bullets)
                
                self.game.asset_manager.play_sound("enemy_shoot")
        
        # Check collisions
        points_earned, player_died, kills = self.collision_manager.check_all_collisions(
            self.player,
            self.player_bullets,
            self.enemies,
            self.enemy_bullets,
            self.hit_effects,
            self.spawn_manager,
        )

        # Counts enemies killed current wave
        self.spawn_manager.enemies_killed_this_wave += kills
        
        self.score += points_earned
        
        if player_died:
            self.game_over = True
            # Play game over sound
            self.game.asset_manager.play_sound("player_hit")
            # Save score to database and check if it's a new high score
            previous_high_score = self.game.data_manager.get_high_score()
            self.game.data_manager.save_score(self.score)
            if self.score > previous_high_score:
                self.is_new_high_score = True
        
        # Check for wave completion
        if self.spawn_manager.is_wave_complete(self.enemies):
            self.player.hp = min(self.player.max_health, self.player.health + 50)
            for bullet in self.player_bullets:
                bullet.kill()
            for bullet in self.enemy_bullets:
                bullet.kill()
            for enemy in self.enemies:
                enemy.kill()
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

    def _restart_game(self) -> None:
        """Restart the game."""
        from .playing_state import PlayingState
        self.exit()
        self.game.current_state = PlayingState(self.game)
        self.game.current_state.enter()

    def _return_to_menu(self) -> None:
        """Return to main menu."""
        from .menu_state import MenuState
        self.exit()
        self.game.current_state = MenuState(self.game)
        self.game.current_state.enter()

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
        
        # Draw hit effects
        for effect in self.hit_effects:
            effect.draw(screen)
        
        # Draw HUD
        self.hud.draw(
            screen,
            self.score,
            self.player,
            self.spawn_manager.get_wave_number(),
            self.game.data_manager.get_high_score(),
            spawn_manager=self.spawn_manager,
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
        text_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 80)
        
        # Final score
        score_font = self.game.asset_manager.get_font("hud")
        score_text = f"Final Score: {self.score}"
        score_surface = score_font.render(score_text, True, config.COLOR_WHITE)
        score_rect = score_surface.get_rect()
        score_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 10)
        
        # New high score message
        y_offset = 30
        if self.is_new_high_score:
            new_high_text = "NEW HIGH SCORE!"
            new_high_surface = font.render(new_high_text, True, config.COLOR_YELLOW)
            new_high_rect = new_high_surface.get_rect()
            new_high_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + y_offset)
            y_offset += 60
        
        # Instructions
        restart_text = "R: Restart  |  M: Menu  |  ESC: Quit"
        restart_surface = score_font.render(restart_text, True, config.COLOR_GRAY)
        restart_rect = restart_surface.get_rect()
        restart_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + y_offset)
        
        # Semi-transparent background
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(config.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        screen.blit(text_surface, text_rect)
        screen.blit(score_surface, score_rect)
        if self.is_new_high_score:
            screen.blit(new_high_surface, new_high_rect)
        screen.blit(restart_surface, restart_rect)

