"""
Tests for progressive difficulty scaling system.

Tests that difficulty increases every 6 waves and boss scaling works.
"""

import pygame
import pytest

from voidrunner.managers.spawn_manager import SpawnManager
from voidrunner.utils import config


class TestDifficultyScaling:
    """Test suite for difficulty scaling mechanics."""

    @pytest.fixture
    def mock_asset_manager(self):
        """Create mock asset manager."""
        class MockAssetManager:
            def get_sprite(self, name):
                pygame.init()
                return pygame.Surface((64, 64))
        
        return MockAssetManager()

    def test_difficulty_scales_every_6_waves(self, mock_asset_manager):
        """Test difficulty increases every DIFFICULTY_SCALE_INTERVAL waves."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Initial state
        assert spawn_manager.difficulty_tier == 0
        assert spawn_manager.bullet_speed_multiplier == 1.0
        assert spawn_manager.fire_rate_multiplier == 1.0
        
        # Advance to wave 6 (first scaling wave)
        for wave in range(1, 7):
            spawn_manager.advance_wave()
        
        # Difficulty should have scaled
        assert spawn_manager.difficulty_tier == 1
        assert spawn_manager.bullet_speed_multiplier > 1.0
        assert spawn_manager.fire_rate_multiplier < 1.0  # Lower = faster

    def test_difficulty_does_not_scale_on_boss_waves(self, mock_asset_manager):
        """Test difficulty doesn't scale on boss waves (5, 10, 15...)."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Advance to wave 5 (boss wave)
        for wave in range(1, 6):
            spawn_manager.advance_wave()
        
        # Should still be at initial difficulty
        assert spawn_manager.difficulty_tier == 0
        assert spawn_manager.bullet_speed_multiplier == 1.0

    def test_difficulty_scales_at_wave_6_12_18(self, mock_asset_manager):
        """Test difficulty scales at waves 6, 12, 18 (not 5, 10, 15)."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Wave 5 (boss) - no scaling
        for _ in range(5):
            spawn_manager.advance_wave()
        assert spawn_manager.difficulty_tier == 0
        
        # Wave 6 - should scale
        spawn_manager.advance_wave()
        assert spawn_manager.difficulty_tier == 1
        
        # Waves 7-11 - no additional scaling
        for _ in range(5):
            spawn_manager.advance_wave()
        assert spawn_manager.difficulty_tier == 1
        
        # Wave 12 - should scale again
        spawn_manager.advance_wave()
        assert spawn_manager.difficulty_tier == 2

    def test_bullet_speed_increases_correctly(self, mock_asset_manager):
        """Test bullet speed multiplier increases by correct amount."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Advance to wave 6
        for _ in range(6):
            spawn_manager.advance_wave()
        
        expected_multiplier = config.ENEMY_BULLET_SPEED_SCALE
        assert pytest.approx(spawn_manager.bullet_speed_multiplier, 0.01) == expected_multiplier

    def test_fire_rate_decreases_correctly(self, mock_asset_manager):
        """Test fire rate multiplier decreases (faster shooting)."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Advance to wave 6
        for _ in range(6):
            spawn_manager.advance_wave()
        
        expected_multiplier = config.ENEMY_FIRE_RATE_SCALE
        assert pytest.approx(spawn_manager.fire_rate_multiplier, 0.01) == expected_multiplier

    def test_multiple_difficulty_tiers(self, mock_asset_manager):
        """Test difficulty continues scaling across multiple intervals."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Advance to wave 18 (3 scaling events: waves 6, 12, 18)
        for _ in range(18):
            spawn_manager.advance_wave()
        
        assert spawn_manager.difficulty_tier == 3
        
        # Multipliers should compound
        expected_bullet_speed = config.ENEMY_BULLET_SPEED_SCALE ** 3
        expected_fire_rate = config.ENEMY_FIRE_RATE_SCALE ** 3
        
        assert pytest.approx(spawn_manager.bullet_speed_multiplier, 0.01) == expected_bullet_speed
        assert pytest.approx(spawn_manager.fire_rate_multiplier, 0.01) == expected_fire_rate

    def test_spawned_enemies_receive_multipliers(self, mock_asset_manager):
        """Test enemies spawned after scaling have increased difficulty."""
        spawn_manager = SpawnManager(mock_asset_manager)
        enemy_group = pygame.sprite.Group()
        
        # Scale difficulty
        for _ in range(6):
            spawn_manager.advance_wave()
        
        # Spawn an enemy
        spawn_manager._spawn_enemy(enemy_group)
        
        # Get the spawned enemy
        enemy = list(enemy_group)[0]
        
        # Enemy should have scaled multipliers
        assert enemy.bullet_speed_multiplier > 1.0
        assert enemy.fire_rate_multiplier < 1.0


class TestBossDifficultyScaling:
    """Test suite for boss-specific difficulty scaling."""

    @pytest.fixture
    def boss_sprite(self):
        """Create test sprite for boss."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_boss_health_scales_with_level(self, boss_sprite):
        """Test boss health increases each boss encounter."""
        from voidrunner.entities.enemies.boss_enemy import BossEnemy
        
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        boss3 = BossEnemy(400, 100, boss_sprite, boss_level=3)
        
        assert boss2.health > boss1.health
        assert boss3.health > boss2.health

    def test_boss_fire_rate_increases(self, boss_sprite):
        """Test boss shoots faster with each level."""
        from voidrunner.entities.enemies.boss_enemy import BossEnemy
        
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        
        # Lower fire_rate = shoots more frequently
        assert boss2.fire_rate < boss1.fire_rate

    def test_boss_bullet_speed_increases(self, boss_sprite):
        """Test boss bullets get faster with each level."""
        from voidrunner.entities.enemies.boss_enemy import BossEnemy
        
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        
        assert boss2.bullet_speed_multiplier > boss1.bullet_speed_multiplier

