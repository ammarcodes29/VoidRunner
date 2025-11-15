"""
Pytest configuration and fixtures.

Common test fixtures for VoidRunner test suite.
"""

import pytest
import pygame


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for testing
    yield
    pygame.quit()


@pytest.fixture
def mock_sprite():
    """Create a mock sprite surface for testing."""
    surface = pygame.Surface((64, 64))
    surface.fill((255, 0, 0))
    return surface


@pytest.fixture
def mock_bullet_sprite():
    """Create a mock bullet sprite surface for testing."""
    surface = pygame.Surface((32, 32))
    surface.fill((0, 255, 0))
    return surface


@pytest.fixture
def player_instance(mock_sprite, mock_bullet_sprite):
    """Create a Player instance for testing."""
    from voidrunner.entities.player import Player
    return Player(400, 300, mock_sprite, mock_bullet_sprite)


@pytest.fixture
def basic_enemy_instance(mock_sprite):
    """Create a BasicEnemy instance for testing."""
    from voidrunner.entities.enemies.basic_enemy import BasicEnemy
    return BasicEnemy(400, 100, mock_sprite)


@pytest.fixture
def bullet_instance(mock_bullet_sprite):
    """Create a Bullet instance for testing."""
    from voidrunner.entities.bullet import Bullet
    velocity = pygame.Vector2(0, -8)
    return Bullet(400, 300, velocity, "player", mock_bullet_sprite)

