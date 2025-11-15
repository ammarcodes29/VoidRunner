"""
Heads-Up Display (HUD) for game information.

Displays score, health, wave number, and other player stats.
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
            player: Player object for health/lives info
            wave_number: Current wave number
        """
        self._draw_score(screen, score)
        self._draw_lives(screen, player)
        self._draw_health(screen, player)
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

    def _draw_lives(self, screen: pygame.Surface, player) -> None:
        """
        Draw player lives count.

        Args:
            screen: Pygame surface to draw on
            player: Player object
        """
        lives_text = f"Lives: {player.lives}/{player.max_lives}"
        text_surface = self.font.render(lives_text, True, config.COLOR_WHITE)
        screen.blit(
            text_surface,
            (config.HUD_MARGIN, config.HUD_MARGIN + 30),
        )

    def _draw_health(self, screen: pygame.Surface, player) -> None:
        """
        Draw health bar.

        Args:
            screen: Pygame surface to draw on
            player: Player object
        """
        # Health bar background
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
        
        # Foreground (filled based on health)
        health_percent = max(0, player.health / player.max_health)
        fill_width = int(health_percent * bar_width)
        
        # Color based on health level
        if health_percent > 0.6:
            bar_color = config.COLOR_GREEN
        elif health_percent > 0.3:
            bar_color = config.COLOR_YELLOW
        else:
            bar_color = config.COLOR_RED
        
        pygame.draw.rect(
            screen,
            bar_color,
            (bar_x, bar_y, fill_width, bar_height),
        )
        
        # Border
        pygame.draw.rect(
            screen,
            config.COLOR_WHITE,
            (bar_x, bar_y, bar_width, bar_height),
            2,
        )
        
        # Health text
        health_text = f"Health: {int(player.health)}/{int(player.max_health)}"
        text_surface = self.font.render(health_text, True, config.COLOR_WHITE)
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
        Draw debug information (entity count, etc).
        
        Note: FPS is drawn separately by Game class for better accuracy.

        Args:
            screen: Pygame surface to draw on
        """
        # FPS is handled by game.py _draw_fps() method
        # Could add entity count or other debug info here in the future
        pass

