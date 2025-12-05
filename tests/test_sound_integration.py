"""
Tests for sound integration (.ogg files).

Tests sound loading and playback for shooting and game over.
"""

import pytest

from voidrunner.managers.asset_manager import AssetManager


class TestSoundIntegration:
    """Test suite for sound system."""

    @pytest.fixture
    def asset_manager(self):
        """Create asset manager instance."""
        return AssetManager()

    def test_sound_files_loaded(self, asset_manager):
        """Test that .ogg sound files are loaded."""
        sounds = asset_manager.sounds
        
        # Check for key sound effects
        assert "player_shoot" in sounds or "shoot" in sounds
        assert "explosion" in sounds
        assert "player_hit" in sounds or "hit" in sounds

    def test_player_shoot_sound_exists(self, asset_manager):
        """Test player shooting sound is available."""
        # Try both possible names
        has_sound = (
            asset_manager.get_sound("player_shoot") is not None or
            asset_manager.get_sound("shoot") is not None
        )
        assert has_sound

    def test_explosion_sound_exists(self, asset_manager):
        """Test explosion sound is available."""
        sound = asset_manager.get_sound("explosion")
        assert sound is not None

    def test_hit_sound_exists(self, asset_manager):
        """Test hit/damage sound is available."""
        # Try both possible names
        has_sound = (
            asset_manager.get_sound("player_hit") is not None or
            asset_manager.get_sound("hit") is not None
        )
        assert has_sound

    def test_play_sound_does_not_crash(self, asset_manager):
        """Test playing sounds doesn't cause errors."""
        # Should not raise exceptions
        try:
            asset_manager.play_sound("explosion")
            asset_manager.play_sound("player_shoot")
        except Exception as e:
            pytest.fail(f"Playing sound raised exception: {e}")

    def test_play_missing_sound_handles_gracefully(self, asset_manager):
        """Test playing non-existent sound doesn't crash."""
        # Should handle gracefully, not crash
        try:
            asset_manager.play_sound("nonexistent_sound_file")
        except Exception as e:
            pytest.fail(f"Playing missing sound raised exception: {e}")

