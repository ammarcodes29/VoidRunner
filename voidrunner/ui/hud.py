"""
Heads-Up Display (HUD) for game information.

Displays score, health, wave number, and other player stats.
Reference: PRD Section 2.5 - Game States & UI
"""

import pygame

from ..utils import config


class HUD:
    """
    Heads-Up Display showing game stats during gameplay.

    Displays score, lives, shield, wave number, and active power-ups.
    """

    def __init__(self, font: pygame.font.Font) -> None:
        """
        Initialize the HUD.

        Args:
            font: Pygame font for rendering text
        """
        self.font = font

    def draw(
        self,
        screen: pygame.Surface,
        score: int,
        player,
        wave_number: int,
    ) -> None:
        """
        Draw all HUD elements.

        Args:
            screen: Pygame surface to draw on
            score: Current score
            player: Player object for health/shield info
            wave_number: Current wave number
        """
        self._draw_score(screen, score)
        self._draw_health(screen, player)
        self._draw_shield(screen, player)
        self._draw_wave(screen, wave_number)
        self._draw_kill_streak(screen, player)
        
        # Debug info
        if config.DEBUG_MODE:
            self._draw_debug_info(screen)

    def _draw_score(self, screen: pygame.Surface, score: int) -> None:
        """
        Draw the current score.

        Args:
            screen: Pygame surface to draw on
            score: Current score value
        """
        score_text = f"Score: {score}"
        text_surface = self.font.render(score_text, True, config.COLOR_WHITE)
        screen.blit(text_surface, (config.HUD_MARGIN, config.HUD_MARGIN))

    def _draw_health(self, screen: pygame.Surface, player) -> None:
        """
        Draw player health as hearts.

        Args:
            screen: Pygame surface to draw on
            player: Player object
        """
        health_text = f"Health: {player.health}/{player.max_health}"
        text_surface = self.font.render(health_text, True, config.COLOR_WHITE)
        screen.blit(
            text_surface,
            (config.HUD_MARGIN, config.HUD_MARGIN + 30),
        )

    def _draw_shield(self, screen: pygame.Surface, player) -> None:
        """
        Draw shield bar.

        Args:
            screen: Pygame surface to draw on
            player: Player object
        """
        # Shield bar background
        bar_x = config.HUD_MARGIN
        bar_y = config.HUD_MARGIN + 60
        bar_width = 200
        bar_height = 20
        
        # Background (empty)
        pygame.draw.rect(
            screen,
            config.COLOR_DARK_GRAY,
            (bar_x, bar_y, bar_width, bar_height),
        )
        
        # Foreground (filled based on shield)
        fill_width = int((player.shield / player.max_shield) * bar_width)
        pygame.draw.rect(
            screen,
            config.COLOR_BLUE,
            (bar_x, bar_y, fill_width, bar_height),
        )
        
        # Border
        pygame.draw.rect(
            screen,
            config.COLOR_WHITE,
            (bar_x, bar_y, bar_width, bar_height),
            2,
        )
        
        # Shield text
        shield_text = f"Shield: {int(player.shield)}"
        text_surface = self.font.render(shield_text, True, config.COLOR_WHITE)
        screen.blit(text_surface, (bar_x + bar_width + 10, bar_y - 2))

    def _draw_wave(self, screen: pygame.Surface, wave_number: int) -> None:
        """
        Draw current wave number.

        Args:
            screen: Pygame surface to draw on
            wave_number: Current wave number
        """
        wave_text = f"Wave: {wave_number}"
        text_surface = self.font.render(wave_text, True, config.COLOR_YELLOW)
        
        # Position in top-right corner
        text_rect = text_surface.get_rect()
        text_rect.topright = (
            config.SCREEN_WIDTH - config.HUD_MARGIN,
            config.HUD_MARGIN,
        )
        screen.blit(text_surface, text_rect)

    def _draw_kill_streak(self, screen: pygame.Surface, player) -> None:
        """
        Draw kill streak counter if active.

        Args:
            screen: Pygame surface to draw on
            player: Player object
        """
        if player.kill_streak >= config.STREAK_BONUS_THRESHOLD:
            streak_text = f"STREAK x{player.kill_streak}!"
            text_surface = self.font.render(streak_text, True, config.COLOR_GREEN)
            
            # Position in top-right corner below wave
            text_rect = text_surface.get_rect()
            text_rect.topright = (
                config.SCREEN_WIDTH - config.HUD_MARGIN,
                config.HUD_MARGIN + 30,
            )
            screen.blit(text_surface, text_rect)

    def _draw_debug_info(self, screen: pygame.Surface) -> None:
        """
        Draw debug information.

        Args:
            screen: Pygame surface to draw on
        """
        debug_font = pygame.font.Font(None, 18)
        
        # FPS (will be updated by game loop)
        if config.SHOW_FPS:
            fps_text = f"FPS: {pygame.time.Clock().get_fps():.1f}"
            text_surface = debug_font.render(fps_text, True, config.COLOR_GREEN)
            screen.blit(
                text_surface,
                (config.HUD_MARGIN, config.SCREEN_HEIGHT - 30),
            )

