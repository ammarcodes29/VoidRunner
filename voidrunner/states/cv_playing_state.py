"""
CV Playing state - hand tracking controlled gameplay.

Uses MediaPipe hand tracking for player movement and shooting.
"""

import logging

import pygame

from ..input.hand_tracker import HandTracker
from ..utils import config
from .playing_state import PlayingState

logger = logging.getLogger(__name__)


class CVPlayingState(PlayingState):
    """
    Hand-tracking controlled gameplay state.
    
    Movement: Left hand position (virtual joystick)
    Shooting: Right hand fist gesture
    Only ESC (pause) works from keyboard.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initialize the CV playing state.

        Args:
            game: Reference to the main Game object
        """
        super().__init__(game)
        
        # Hand tracking
        self.hand_tracker: HandTracker | None = None
        self.hand_tracking_active = False
        self.cv_error_message = ""
        
        # Webcam preview (mini view in corner)
        self.show_webcam_preview = True
        self.preview_size = (160, 120)  # Small preview
        self.preview_pos = (config.SCREEN_WIDTH - 170, config.SCREEN_HEIGHT - 130)
        
        # Auto-fire state (to prevent shooting every frame)
        self.was_shooting = False
        self.shoot_held_time = 0.0
        self.auto_fire_delay = 0.15  # Seconds between auto-fire shots
        
        # Try to start hand tracking
        self._init_hand_tracking()

    def _init_hand_tracking(self) -> None:
        """Initialize the hand tracker."""
        try:
            self.hand_tracker = HandTracker()
            if self.hand_tracker.start():
                self.hand_tracking_active = True
                logger.info("CV mode: Hand tracking initialized successfully")
            else:
                self.cv_error_message = "Failed to open webcam"
                logger.error("CV mode: Failed to start hand tracker")
        except FileNotFoundError as e:
            self.cv_error_message = "Model file not found. Check assets/models/"
            logger.error(f"CV mode: {e}")
        except ImportError as e:
            self.cv_error_message = "Install: pip install mediapipe opencv-python"
            logger.error(f"CV mode: {e}")
        except Exception as e:
            self.cv_error_message = f"Error: {str(e)[:50]}"
            logger.error(f"CV mode: Unexpected error - {e}")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle input events (only ESC for pause in CV mode).

        Args:
            events: List of pygame events from this frame
        """
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.paused:
                    # Handle pause menu button clicks
                    if self.resume_button_rect.collidepoint(event.pos):
                        self.paused = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    elif self.quit_button_rect.collidepoint(event.pos):
                        self._return_to_menu()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    # Handle game over input
                    if event.key == pygame.K_r:
                        self._restart_game()
                    elif event.key == pygame.K_m:
                        self._return_to_menu()
                    elif event.key == pygame.K_ESCAPE:
                        self.game.running = False
                elif self.paused:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                else:
                    # Only ESC works in CV mode (no WASD, no Space)
                    if event.key == pygame.K_ESCAPE:
                        self.paused = True
                    # Toggle webcam preview with P
                    elif event.key == pygame.K_p:
                        self.show_webcam_preview = not self.show_webcam_preview

    def update(self, dt: float) -> None:
        """
        Update gameplay logic using hand tracking input.

        Args:
            dt: Delta time in seconds since last frame
        """
        if self.game_over:
            return
        
        if self.paused:
            # Update cursor for pause menu buttons
            if (self.resume_button_rect.collidepoint(self.mouse_pos) or
                self.quit_button_rect.collidepoint(self.mouse_pos)):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return
        
        # Handle wave transitions
        if self.in_wave_transition:
            self._update_wave_transition(dt)
            return
        
        # Get hand tracking input
        if self.hand_tracking_active and self.hand_tracker:
            control_state = self.hand_tracker.update()
            dx, dy = control_state['movement']
            shooting = control_state['shooting']
        else:
            dx, dy = 0.0, 0.0
            shooting = False
        
        # Update player movement using hand tracking
        self._update_player_cv(dt, dx, dy)
        
        # Handle shooting from hand gesture
        self._handle_cv_shooting(dt, shooting)
        
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

        self.spawn_manager.enemies_killed_this_wave += kills
        self.score += points_earned
        
        if player_died:
            self.game_over = True
            self.game.asset_manager.play_sound("player_hit")
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

    def _update_player_cv(self, dt: float, dx: float, dy: float) -> None:
        """
        Update player position based on hand tracking movement.

        Args:
            dt: Delta time in seconds
            dx: Horizontal movement (-1 to 1)
            dy: Vertical movement (-1 to 1)
        """
        # Apply movement based on hand position
        self.player.velocity.x = dx * config.PLAYER_SPEED
        self.player.velocity.y = dy * config.PLAYER_SPEED
        
        # Normalize diagonal movement
        if self.player.velocity.length() > 0:
            # Only normalize if magnitude > 1 (diagonal exceeds speed)
            if self.player.velocity.length() > config.PLAYER_SPEED:
                self.player.velocity = self.player.velocity.normalize() * config.PLAYER_SPEED
        
        # Apply movement
        self.player.position += self.player.velocity * dt * 60
        
        # Update other player systems
        self.player._update_shooting_cooldown(dt)
        self.player._update_invincibility(dt)
        self.player._update_health_regen(dt)
        self.player._constrain_to_screen()
        self.player.rect.center = (int(self.player.position.x), int(self.player.position.y))

    def _handle_cv_shooting(self, dt: float, shooting: bool) -> None:
        """
        Handle shooting based on hand gesture.

        Args:
            dt: Delta time in seconds
            shooting: Whether shooting gesture is detected
        """
        if shooting:
            self.shoot_held_time += dt
            
            # Shoot on first fist detection or after auto-fire delay
            if not self.was_shooting or self.shoot_held_time >= self.auto_fire_delay:
                if self.player.can_shoot():
                    bullet = self.player.shoot()
                    self.player_bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    self.game.asset_manager.play_sound("player_shoot")
                    self.shoot_held_time = 0.0
            
            self.was_shooting = True
        else:
            self.was_shooting = False
            self.shoot_held_time = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the gameplay with webcam preview.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw base gameplay
        super().draw(screen)
        
        # Draw webcam preview if enabled and not paused/game over
        if (self.show_webcam_preview and 
            self.hand_tracking_active and 
            self.hand_tracker and 
            not self.paused and 
            not self.game_over):
            self._draw_webcam_preview(screen)
        
        # Draw CV mode indicator
        if not self.paused and not self.game_over:
            self._draw_cv_status(screen)
        
        # Draw error message if hand tracking failed
        if self.cv_error_message and not self.hand_tracking_active:
            self._draw_cv_error(screen)

    def _draw_webcam_preview(self, screen: pygame.Surface) -> None:
        """Draw small webcam preview in corner."""
        if self.hand_tracker is None:
            return
            
        debug_frame = self.hand_tracker.get_debug_frame()
        if debug_frame is None:
            return
        
        import cv2
        
        # Resize for preview
        preview = cv2.resize(debug_frame, self.preview_size)
        
        # Convert BGR to RGB for pygame
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        
        # Convert to pygame surface
        preview_surface = pygame.surfarray.make_surface(preview.swapaxes(0, 1))
        
        # Draw border
        border_rect = pygame.Rect(
            self.preview_pos[0] - 2, 
            self.preview_pos[1] - 2,
            self.preview_size[0] + 4,
            self.preview_size[1] + 4
        )
        pygame.draw.rect(screen, config.COLOR_WHITE, border_rect, 2)
        
        # Draw preview
        screen.blit(preview_surface, self.preview_pos)

    def _draw_cv_status(self, screen: pygame.Surface) -> None:
        """Draw CV mode status indicator."""
        font = self.game.asset_manager.get_font("hud")
        
        # Status text
        if self.hand_tracking_active and self.hand_tracker:
            hands = self.hand_tracker.hands_detected
            if hands == 2:
                text = "CV MODE: 2 HANDS"
                color = config.COLOR_GREEN
            elif hands == 1:
                text = "CV MODE: 1 HAND"
                color = config.COLOR_YELLOW
            else:
                text = "CV MODE: NO HANDS"
                color = config.COLOR_RED
        else:
            text = "CV MODE: INACTIVE"
            color = config.COLOR_RED
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (10, config.SCREEN_HEIGHT - 30))
        
        # Toggle hint
        if self.show_webcam_preview:
            hint = "[P] Hide preview"
        else:
            hint = "[P] Show preview"
        hint_surface = font.render(hint, True, config.COLOR_GRAY)
        screen.blit(hint_surface, (10, config.SCREEN_HEIGHT - 50))

    def _draw_cv_error(self, screen: pygame.Surface) -> None:
        """Draw CV error message."""
        font = self.game.asset_manager.get_font("hud")
        
        # Error background
        error_rect = pygame.Rect(50, config.SCREEN_HEIGHT // 2 - 40, 
                                 config.SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(screen, (80, 0, 0), error_rect)
        pygame.draw.rect(screen, config.COLOR_RED, error_rect, 2)
        
        # Error text
        title = "HAND TRACKING UNAVAILABLE"
        title_surface = font.render(title, True, config.COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                     config.SCREEN_HEIGHT // 2 - 20))
        screen.blit(title_surface, title_rect)
        
        # Error detail
        detail_surface = font.render(self.cv_error_message, True, config.COLOR_GRAY)
        detail_rect = detail_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                       config.SCREEN_HEIGHT // 2 + 10))
        screen.blit(detail_surface, detail_rect)

    def _restart_game(self) -> None:
        """Restart the game in CV mode."""
        self.exit()
        self.game.current_state = CVPlayingState(self.game)
        self.game.current_state.enter()

    def exit(self) -> None:
        """Clean up when leaving state."""
        super().exit()
        if self.hand_tracker:
            self.hand_tracker.release()
            self.hand_tracker = None
            self.hand_tracking_active = False

