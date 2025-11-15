"""
Data persistence manager.

Handles loading and saving high scores and settings to JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from ..utils import config

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages game data persistence (high scores, settings).

    All data is stored in JSON format for easy reading and modification.
    """

    def __init__(self) -> None:
        """Initialize the data manager and ensure data directory exists."""
        # Ensure data directory exists
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize high score
        self._high_score = self.load_high_score()

    def load_high_score(self) -> int:
        """
        Load the high score from file.

        Returns:
            High score value, or 0 if file doesn't exist
        """
        try:
            if config.HIGH_SCORES_FILE.exists():
                with open(config.HIGH_SCORES_FILE, 'r') as f:
                    data = json.load(f)
                    high_score = data.get('high_score', 0)
                    logger.info(f"Loaded high score: {high_score}")
                    return high_score
            else:
                logger.info("No high score file found, starting with 0")
                return 0
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading high score: {e}")
            return 0

    def save_high_score(self, score: int) -> bool:
        """
        Save a new high score to file.

        Args:
            score: Score to save

        Returns:
            True if save was successful
        """
        try:
            data = {
                'high_score': score,
                'last_updated': self._get_timestamp()
            }
            
            with open(config.HIGH_SCORES_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            self._high_score = score
            logger.info(f"Saved new high score: {score}")
            return True
            
        except IOError as e:
            logger.error(f"Error saving high score: {e}")
            return False

    def get_high_score(self) -> int:
        """
        Get the current high score.

        Returns:
            Current high score
        """
        return self._high_score

    def check_and_update_high_score(self, current_score: int) -> bool:
        """
        Check if current score is a new high score and update if so.

        Args:
            current_score: Current game score

        Returns:
            True if this is a new high score
        """
        if current_score > self._high_score:
            self.save_high_score(current_score)
            return True
        return False

    def _get_timestamp(self) -> str:
        """
        Get current timestamp as string.

        Returns:
            ISO format timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def load_settings(self) -> dict:
        """
        Load game settings from file.

        Returns:
            Dictionary of settings, or defaults if file doesn't exist
        """
        try:
            if config.SETTINGS_FILE.exists():
                with open(config.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    logger.info("Loaded settings")
                    return settings
            else:
                return self._get_default_settings()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading settings: {e}")
            return self._get_default_settings()

    def save_settings(self, settings: dict) -> bool:
        """
        Save game settings to file.

        Args:
            settings: Dictionary of settings to save

        Returns:
            True if save was successful
        """
        try:
            with open(config.SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Saved settings")
            return True
        except IOError as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def _get_default_settings(self) -> dict:
        """
        Get default game settings.

        Returns:
            Dictionary of default settings
        """
        return {
            'music_volume': config.MUSIC_VOLUME,
            'sfx_volume': config.SFX_VOLUME,
            'debug_mode': config.DEBUG_MODE
        }

