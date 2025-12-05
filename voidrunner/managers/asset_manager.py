"""
Asset loading and caching manager.

Loads all sprites, sounds, and fonts once at startup for reuse.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import pygame

from ..utils import config


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetManager:
    """
    Manages loading and caching of game assets.

    All assets are loaded once at initialization and cached for performance.
    Supports placeholder generation if asset files are missing.
    """

    def __init__(self) -> None:
        """Initialize the asset manager and load all assets."""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}

        # Initialize pygame modules
        pygame.mixer.init()
        pygame.font.init()

        self._load_all_assets()

    def _load_all_assets(self) -> None:
        """Load all game assets (sprites, sounds, fonts)."""
        logger.info("Loading game assets...")
        self._load_sprites()
        self._load_sounds()
        self._load_fonts()
        logger.info("Asset loading complete!")

    def _load_sprites(self) -> None:
        """
        Load sprite images from assets/sprites directory.

        If files are missing, generate colored placeholder rectangles.
        """
        sprite_definitions = {
            # Player sprites
            "player": (config.PLAYER_SPRITE_WIDTH, config.PLAYER_SPRITE_HEIGHT, config.COLOR_BLUE),
            "player_bullet": (config.BULLET_SPRITE_WIDTH, config.BULLET_SPRITE_HEIGHT, config.COLOR_GREEN),
            "player_bullet_hit": (config.BULLET_SPRITE_WIDTH, config.BULLET_SPRITE_HEIGHT, config.COLOR_YELLOW),
            
            # Enemy sprites
            "basic_enemy": (config.ENEMY_SPRITE_WIDTH, config.ENEMY_SPRITE_HEIGHT, config.COLOR_RED),
            "chaser_enemy": (config.ENEMY_SPRITE_WIDTH, config.ENEMY_SPRITE_HEIGHT, (255, 128, 0)),  # Orange
            "zigzag_enemy": (config.ENEMY_SPRITE_WIDTH, config.ENEMY_SPRITE_HEIGHT, (255, 0, 255)),  # Magenta
            "boss_enemy": (config.ENEMY_SPRITE_WIDTH * 2, config.ENEMY_SPRITE_HEIGHT * 2, (128, 0, 0)),  # Dark Red
            "enemy_bullet": (config.BULLET_SPRITE_WIDTH, config.BULLET_SPRITE_HEIGHT, config.COLOR_RED),
            "enemy_bullet_hit": (config.BULLET_SPRITE_WIDTH, config.BULLET_SPRITE_HEIGHT, (255, 128, 0)),  # Orange
            
            # Power-up sprites
            "powerup_rapid_fire": (config.POWERUP_SPRITE_WIDTH, config.POWERUP_SPRITE_HEIGHT, config.COLOR_YELLOW),
            "powerup_shield": (config.POWERUP_SPRITE_WIDTH, config.POWERUP_SPRITE_HEIGHT, config.COLOR_BLUE),
            "powerup_magnet": (config.POWERUP_SPRITE_WIDTH, config.POWERUP_SPRITE_HEIGHT, (128, 0, 128)),  # Purple
            
            # Background
            "background": (config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.COLOR_BLACK),
        }

        for sprite_name, (width, height, color) in sprite_definitions.items():
            sprite_path = config.SPRITES_DIR / f"{sprite_name}.png"
            
            if sprite_path.exists():
                try:
                    surface = pygame.image.load(str(sprite_path)).convert_alpha()
                    surface = pygame.transform.scale(surface, (width, height))
                    self.sprites[sprite_name] = surface
                    logger.debug(f"Loaded sprite: {sprite_name}")
                except pygame.error as e:
                    logger.warning(f"Failed to load {sprite_name}: {e}. Using placeholder.")
                    self.sprites[sprite_name] = self._create_placeholder(width, height, color)
            else:
                # Create placeholder
                self.sprites[sprite_name] = self._create_placeholder(width, height, color)
                logger.debug(f"Created placeholder sprite: {sprite_name}")

    def _create_placeholder(
        self, width: int, height: int, color: tuple[int, int, int]
    ) -> pygame.Surface:
        """
        Create a placeholder sprite (colored rectangle).

        Args:
            width: Sprite width in pixels
            height: Sprite height in pixels
            color: RGB color tuple

        Returns:
            Pygame surface with the placeholder sprite
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, width, height))
        # Add border for visibility
        pygame.draw.rect(surface, config.COLOR_WHITE, (0, 0, width, height), 2)
        return surface

    def _load_sounds(self) -> None:
        """
        Load sound effects from assets/sounds directory.

        If files are missing, use silent placeholders.
        """
        sound_definitions = [
            "player_shoot",
            "enemy_shoot",
            "explosion",
            "powerup_collect",
            "player_hit",
        ]

        for sound_name in sound_definitions:
            # Try both .ogg and .wav formats
            loaded = False
            for ext in ['.ogg', '.wav']:
                sound_path = config.SOUNDS_DIR / f"{sound_name}{ext}"
                
                if sound_path.exists():
                    try:
                        sound = pygame.mixer.Sound(str(sound_path))
                        sound.set_volume(config.SFX_VOLUME)
                        self.sounds[sound_name] = sound
                        logger.debug(f"Loaded sound: {sound_name}{ext}")
                        loaded = True
                        break
                    except pygame.error as e:
                        logger.warning(f"Failed to load {sound_name}{ext}: {e}")
            
            if not loaded:
                # Create silent placeholder
                self.sounds[sound_name] = self._create_silent_sound()
                logger.debug(f"Created placeholder sound: {sound_name}")

    def _create_silent_sound(self) -> pygame.mixer.Sound:
        """
        Create a silent sound placeholder.

        Returns:
            Silent pygame Sound object
        """
        # Create a minimal silent sound (1 sample at 22050 Hz)
        import numpy as np
        silent_array = np.zeros((1, 2), dtype=np.int16)
        return pygame.mixer.Sound(buffer=silent_array)

    def _load_fonts(self) -> None:
        """Load fonts for UI rendering."""
        try:
            # Try to load custom fonts if they exist
            hud_font_path = config.FONTS_DIR / "hud_font.ttf"
            menu_font_path = config.FONTS_DIR / "menu_font.ttf"
            
            # Store the custom font path for dynamic loading
            self.custom_font_path = None
            if hud_font_path.exists():
                self.custom_font_path = str(hud_font_path)
                self.fonts["hud"] = pygame.font.Font(str(hud_font_path), config.HUD_FONT_SIZE)
            else:
                self.fonts["hud"] = pygame.font.Font(None, config.HUD_FONT_SIZE)
            
            if menu_font_path.exists():
                self.fonts["menu"] = pygame.font.Font(str(menu_font_path), config.MENU_FONT_SIZE)
            else:
                self.fonts["menu"] = pygame.font.Font(None, config.MENU_FONT_SIZE)
            
            # Small font for debug info
            self.fonts["debug"] = pygame.font.Font(None, 18)
            
            logger.debug("Fonts loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load fonts: {e}")
            # Fallback to default fonts
            self.custom_font_path = None
            self.fonts["hud"] = pygame.font.Font(None, config.HUD_FONT_SIZE)
            self.fonts["menu"] = pygame.font.Font(None, config.MENU_FONT_SIZE)
            self.fonts["debug"] = pygame.font.Font(None, 18)

    def load_font(self, size: int) -> pygame.font.Font:
        """
        Load custom font at specified size.
        
        Args:
            size: Font size in points
            
        Returns:
            Pygame Font object
        """
        if self.custom_font_path:
            try:
                return pygame.font.Font(self.custom_font_path, size)
            except Exception as e:
                logger.warning(f"Failed to load custom font at size {size}: {e}")
                return pygame.font.Font(None, size)
        else:
            return pygame.font.Font(None, size)

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """
        Get a sprite by name.

        Args:
            name: Sprite identifier

        Returns:
            Pygame surface or None if not found
        """
        sprite = self.sprites.get(name)
        if sprite is None:
            logger.warning(f"Sprite '{name}' not found")
        return sprite

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """
        Get a sound by name.

        Args:
            name: Sound identifier

        Returns:
            Pygame Sound object or None if not found
        """
        sound = self.sounds.get(name)
        if sound is None:
            logger.warning(f"Sound '{name}' not found")
        return sound

    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """
        Get a font by name.

        Args:
            name: Font identifier ('hud', 'menu', or 'debug')

        Returns:
            Pygame Font object or None if not found
        """
        font = self.fonts.get(name)
        if font is None:
            logger.warning(f"Font '{name}' not found")
        return font

    def play_sound(self, name: str) -> None:
        """
        Play a sound effect.

        Args:
            name: Sound identifier
        """
        sound = self.get_sound(name)
        if sound:
            sound.play()

