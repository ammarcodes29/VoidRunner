"""
Game configuration constants.

All magic numbers and tunable parameters are defined here.
"""

from pathlib import Path

# ============================================================================
# SCREEN SETTINGS
# ============================================================================
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60
WINDOW_TITLE: str = "VoidRunner - Space Survival Shooter"

# ============================================================================
# PLAYER SETTINGS
# ============================================================================
PLAYER_SPEED: float = 5.0
PLAYER_SHOOT_COOLDOWN: float = 0.25  # seconds
PLAYER_MAX_HEALTH: int = 3
PLAYER_MAX_SHIELD: float = 100.0
PLAYER_SHIELD_REGEN_RATE: float = 5.0  # per second
PLAYER_INVINCIBILITY_DURATION: float = 1.5  # seconds after taking damage
PLAYER_SPRITE_WIDTH: int = 64
PLAYER_SPRITE_HEIGHT: int = 64

# ============================================================================
# BULLET SETTINGS
# ============================================================================
BULLET_SPEED: float = 8.0
BULLET_DAMAGE: int = 1
BULLET_SPRITE_WIDTH: int = 32
BULLET_SPRITE_HEIGHT: int = 32

# ============================================================================
# ENEMY SETTINGS
# ============================================================================
ENEMY_BASE_SPEED: float = 2.0
ENEMY_SPAWN_RATE_BASE: float = 2.0  # seconds between spawns
WAVE_DIFFICULTY_MULTIPLIER: float = 1.15  # spawn rate increase per wave
ENEMY_SPRITE_WIDTH: int = 64
ENEMY_SPRITE_HEIGHT: int = 64

# Enemy-specific speeds (multipliers of base speed)
BASIC_ENEMY_SPEED_MULT: float = 1.0
CHASER_ENEMY_SPEED_MULT: float = 0.7
ZIGZAG_ENEMY_SPEED_MULT: float = 1.2

# Enemy health
BASIC_ENEMY_HEALTH: int = 1
CHASER_ENEMY_HEALTH: int = 2
ZIGZAG_ENEMY_HEALTH: int = 1

# Enemy shooting
BASIC_ENEMY_SHOOT_CHANCE: float = 0.02  # per frame chance
ENEMY_BULLET_SPEED: float = 4.0

# ============================================================================
# POWER-UP SETTINGS
# ============================================================================
POWERUP_DROP_CHANCE: float = 0.15  # chance on enemy kill
POWERUP_SPRITE_WIDTH: int = 48
POWERUP_SPRITE_HEIGHT: int = 48
POWERUP_FALL_SPEED: float = 2.0

# Power-up durations (seconds)
RAPID_FIRE_DURATION: float = 10.0
SHIELD_BOOST_DURATION: float = 15.0
MAGNET_DURATION: float = 12.0

# Power-up effects
RAPID_FIRE_MULTIPLIER: float = 0.5  # 50% faster shooting
SHIELD_BOOST_AMOUNT: float = 50.0
MAGNET_RADIUS: float = 150.0  # pixel radius for attraction

# ============================================================================
# SCORING SETTINGS
# ============================================================================
BASIC_ENEMY_POINTS: int = 10
CHASER_ENEMY_POINTS: int = 25
ZIGZAG_ENEMY_POINTS: int = 20
STREAK_BONUS_THRESHOLD: int = 5  # kills without taking damage
STREAK_BONUS_MULTIPLIER: float = 1.5

# ============================================================================
# WAVE SYSTEM
# ============================================================================
WAVE_CLEAR_DELAY: float = 3.0  # seconds before next wave starts
ENEMIES_PER_WAVE_BASE: int = 5
ENEMIES_PER_WAVE_INCREMENT: int = 2  # additional enemies per wave

# ============================================================================
# VISUAL EFFECTS
# ============================================================================
SCREEN_SHAKE_DURATION: float = 0.2  # seconds
SCREEN_SHAKE_INTENSITY: int = 5  # pixels
DAMAGE_FLASH_DURATION: float = 0.15  # seconds
PARTICLE_LIFETIME: float = 1.0  # seconds
EXPLOSION_PARTICLE_COUNT: int = 15

# ============================================================================
# UI SETTINGS
# ============================================================================
HUD_MARGIN: int = 10
HUD_FONT_SIZE: int = 24
HUD_FONT_NAME: str = "Arial"
MENU_FONT_SIZE: int = 48
MENU_FONT_NAME: str = "Arial"

# Colors (RGB tuples)
COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK: tuple[int, int, int] = (0, 0, 0)
COLOR_RED: tuple[int, int, int] = (255, 0, 0)
COLOR_GREEN: tuple[int, int, int] = (0, 255, 0)
COLOR_BLUE: tuple[int, int, int] = (0, 100, 255)
COLOR_YELLOW: tuple[int, int, int] = (255, 255, 0)
COLOR_GRAY: tuple[int, int, int] = (128, 128, 128)
COLOR_DARK_GRAY: tuple[int, int, int] = (64, 64, 64)

# ============================================================================
# FILE PATHS
# ============================================================================
# Get project root directory
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
DATA_DIR: Path = PROJECT_ROOT / "voidrunner" / "data"
ASSETS_DIR: Path = PROJECT_ROOT / "voidrunner" / "assets"

# Data files
HIGH_SCORES_FILE: Path = DATA_DIR / "high_scores.json"
SETTINGS_FILE: Path = DATA_DIR / "settings.json"

# Asset directories
SPRITES_DIR: Path = ASSETS_DIR / "sprites"
SOUNDS_DIR: Path = ASSETS_DIR / "sounds"
FONTS_DIR: Path = ASSETS_DIR / "fonts"

# ============================================================================
# AUDIO SETTINGS
# ============================================================================
MUSIC_VOLUME: float = 0.5  # 0.0 to 1.0
SFX_VOLUME: float = 0.7  # 0.0 to 1.0

# ============================================================================
# DEBUG SETTINGS
# ============================================================================
DEBUG_MODE: bool = False  # Toggle with F3
SHOW_FPS: bool = True
SHOW_COLLISION_BOXES: bool = False
SHOW_ENTITY_COUNT: bool = True

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
MAX_ENTITIES_ON_SCREEN: int = 50  # Despawn oldest if exceeded
OBJECT_POOL_SIZE: int = 100  # Pre-allocated bullets/particles

