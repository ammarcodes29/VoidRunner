"""
Spawn manager for enemy wave generation.

Handles wave-based enemy spawning with difficulty scaling.
"""

import random

import pygame

from ..entities.enemies.basic_enemy import BasicEnemy
from ..entities.enemies.boss_enemy import BossEnemy
from ..entities.enemies.chaser_enemy import ChaserEnemy
from ..entities.enemies.zigzag_enemy import ZigzagEnemy
from ..utils import config, helpers


class SpawnManager:
    """
    Manages enemy spawning based on wave progression.

    Increases spawn rate and enemy count as waves progress.
    """

    def __init__(self, asset_manager) -> None:
        """
        Initialize the spawn manager.

        Args:
            asset_manager: Reference to AssetManager for loading sprites
        """
        self.asset_manager = asset_manager
        
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0
        self.max_kills_this_wave = config.ENEMIES_PER_WAVE_BASE
        self.enemies_killed_this_wave = 0
        
        self.spawn_timer = 0.0
        self.spawn_interval = config.ENEMY_SPAWN_RATE_BASE
        
        self.max_alive = config.ENEMIES_ON_SCREEN_MAX
        
        # Boss wave tracking
        self.boss_spawned = False
        self.boss_killed = False
        self.boss_level = 0
        
        # Difficulty scaling (progressive difficulty every 6 waves)
        self.difficulty_tier = 0  # Increases every DIFFICULTY_SCALE_INTERVAL waves
        self.bullet_speed_multiplier = 1.0  # Multiplier for enemy bullet speed
        self.fire_rate_multiplier = 1.0  # Multiplier for enemy fire rate

    def update(self, dt: float, enemy_group: pygame.sprite.Group) -> None:
        """
        Update spawn timer and create enemies.

        Args:
            dt: Delta time in seconds
            enemy_group: Sprite group to add new enemies to
        """
        # Spawn boss at start of boss wave (check if boss actually exists in group)
        if self.is_boss_wave() and not self.boss_spawned:
            # Double check no boss already exists
            from ..entities.enemies.boss_enemy import BossEnemy
            existing_boss = any(isinstance(enemy, BossEnemy) for enemy in enemy_group)
            
            if not existing_boss:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Spawning boss for wave {self.current_wave}!")
                self._spawn_boss(enemy_group)
            
            self.boss_spawned = True
        
        if self.enemies_killed_this_wave >= self.max_kills_this_wave:
            return
        
        # Update spawn timer
        self.spawn_timer += dt

        alive_enemies = len(enemy_group)
        
        can_spawn = (alive_enemies < self.max_alive and self.enemies_killed_this_wave < self.max_kills_this_wave)
        # Check if it's time to spawn
        if not can_spawn:
            return

        if (self.spawn_timer >= self.spawn_interval):
            self.spawn_timer = 0.0
            self._spawn_enemy(enemy_group)
            self.enemies_spawned_this_wave += 1

        # if self.spawn_timer >= self.spawn_interval:
        #     self.spawn_timer = 0.0
            
        #     # Spawn enemy if we haven't reached the wave limit
        #     if self.enemies_spawned_this_wave < self.max_kills_this_wave:
        #         self._spawn_enemy(enemy_group)
        #         self.enemies_spawned_this_wave += 1


        #     # Check if wave is complete
        #     if self.enemies_spawned_this_wave >= self.max_kills_this_wave:
        #         self.wave_complete = True

    def _spawn_enemy(self, enemy_group: pygame.sprite.Group) -> None:
        """
        Spawn a single enemy at the top of the screen.

        Args:
            enemy_group: Sprite group to add the enemy to
        """
        # Random position at top of screen
        x = random.uniform(50, config.SCREEN_WIDTH - 50)
        y = -50
        
        # Randomly choose enemy type
        enemy_type = random.choices(
            ["basic", "zigzag", "chaser"],
            weights=[50, 30, 20],  # 50% basic, 30% zigzag, 20% chaser
            k=1
        )[0]
        
        # Apply difficulty scaling multipliers to spawned enemies
        if enemy_type == "basic":
            sprite = self.asset_manager.get_sprite("basic_enemy")
            enemy = BasicEnemy(
                x, y, sprite,
                bullet_speed_multiplier=self.bullet_speed_multiplier,
                fire_rate_multiplier=self.fire_rate_multiplier
            )
        elif enemy_type == "chaser":
            sprite = self.asset_manager.get_sprite("chaser_enemy")
            enemy = ChaserEnemy(
                x, y, sprite,
                bullet_speed_multiplier=self.bullet_speed_multiplier,
                fire_rate_multiplier=self.fire_rate_multiplier
            )
        else:  # zigzag
            sprite = self.asset_manager.get_sprite("zigzag_enemy")
            enemy = ZigzagEnemy(
                x, y, sprite,
                bullet_speed_multiplier=self.bullet_speed_multiplier,
                fire_rate_multiplier=self.fire_rate_multiplier
            )
        
        enemy_group.add(enemy)

    def _spawn_boss(self, enemy_group: pygame.sprite.Group) -> None:
        """
        Spawn the boss enemy at the top of screen.

        Args:
            enemy_group: Sprite group to add the boss to
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Boss spawns at center top (visible from start)
        x = config.SCREEN_WIDTH // 2
        y = 100  # Start visible at top, will lock in place
        
        self.boss_level += 1
        sprite = self.asset_manager.get_sprite("boss_enemy")
        boss = BossEnemy(x, y, sprite, self.boss_level)
        
        logger.info(f"Boss created - Level: {self.boss_level}, Health: {boss.health}, Position: ({x}, {y})")
        enemy_group.add(boss)

    def advance_wave(self) -> None:
        """
        Progress to the next wave with increased difficulty.
        Applies progressive difficulty scaling every 6 waves (not on boss waves).
        """
        self.current_wave += 1
        self.enemies_killed_this_wave = 0
        
        # Reset boss tracking
        self.boss_spawned = False
        self.boss_killed = False
        
        # Increase enemies per wave
        self.max_kills_this_wave = (
            config.ENEMIES_PER_WAVE_BASE
            + (self.current_wave - 1) * config.ENEMIES_PER_WAVE_INCREMENT
        )
        
        # Apply progressive difficulty scaling every DIFFICULTY_SCALE_INTERVAL waves
        # BUT NOT on boss waves (5, 10, 15, 20...) - only on 6, 12, 18, 24...
        if (self.current_wave % config.DIFFICULTY_SCALE_INTERVAL == 0 and 
            not self.is_boss_wave()):
            self.difficulty_tier += 1
            
            # Increase bullet speed and fire rate for regular enemies
            self.bullet_speed_multiplier *= config.ENEMY_BULLET_SPEED_SCALE
            self.fire_rate_multiplier *= config.ENEMY_FIRE_RATE_SCALE
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"Wave {self.current_wave}: Difficulty scaled! "
                f"Bullet speed: {self.bullet_speed_multiplier:.2f}x, "
                f"Fire rate: {self.fire_rate_multiplier:.2f}x"
            )
        
        # Decrease spawn interval (faster spawning)
        self.spawn_interval = config.ENEMY_SPAWN_RATE_BASE / (
            config.WAVE_DIFFICULTY_MULTIPLIER ** (self.current_wave - 1)
        )
        
        # Ensure minimum spawn rate
        self.spawn_interval = max(0.5, self.spawn_interval)
        
        # Reset wave state
        self.enemies_spawned_this_wave = 0
        self.spawn_timer = 0.0

    def is_wave_complete(self, enemy_group: pygame.sprite.Group) -> bool:
        """
        Check if the current wave is complete.

        A wave is complete when all enemies have been killed.
        For boss waves, boss must also be killed.

        Args:
            enemy_group: Sprite group containing active enemies

        Returns:
            True if wave is complete
        """
        regular_enemies_done = self.enemies_killed_this_wave >= self.max_kills_this_wave
        
        if self.is_boss_wave():
            # Boss wave requires boss to be killed too
            return regular_enemies_done and self.boss_killed
        else:
            return regular_enemies_done
    
    def is_boss_wave(self) -> bool:
        """
        Check if current wave is a boss wave.

        Returns:
            True if this is a boss wave (every 5th wave)
        """
        return self.current_wave % config.BOSS_WAVE_INTERVAL == 0
    
    def register_boss_killed(self) -> None:
        """Mark that the boss has been killed."""
        self.boss_killed = True 

    def get_wave_number(self) -> int:
        """
        Get the current wave number.

        Returns:
            Current wave number
        """
        return self.current_wave

    def register_enemy_killed(self):
        self.enemies_killed_this_wave += 1