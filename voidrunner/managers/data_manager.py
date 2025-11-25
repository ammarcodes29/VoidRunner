"""
Data persistence manager with SQLite database.

Handles user authentication and high scores.
"""

import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..utils import config

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages game data persistence using SQLite.
    
    Handles user authentication and high scores.
    """

    def __init__(self) -> None:
        """Initialize the data manager and database."""
        # Ensure data directory exists
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        self.db_path = config.DATABASE_FILE
        self.current_user_id: Optional[int] = None
        self.current_username: Optional[str] = None
        
        # Initialize database
        self._init_database()
        
        logger.info("DataManager initialized with SQLite backend")

    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # High scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_high_scores_user_id 
                ON high_scores(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_high_scores_score 
                ON high_scores(score DESC)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, username: str, password: str) -> tuple[bool, str]:
        """
        Create a new user account.
        
        Args:
            username: Desired username
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validation
        if len(username) < config.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {config.MIN_USERNAME_LENGTH} characters"
        if len(username) > config.MAX_USERNAME_LENGTH:
            return False, f"Username must be at most {config.MAX_USERNAME_LENGTH} characters"
        if len(password) < config.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters"
        if not username.replace("_", "").isalnum():
            return False, "Username must be alphanumeric (underscores allowed)"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists"
            
            # Create user
            password_hash = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"New user created: {username}")
            return True, "Account created successfully!"
            
        except sqlite3.Error as e:
            logger.error(f"Signup error: {e}")
            return False, "Database error occurred"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                "SELECT user_id, username FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            result = cursor.fetchone()
            
            if result:
                self.current_user_id, self.current_username = result
                
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(), self.current_user_id)
                )
                conn.commit()
                conn.close()
                
                logger.info(f"User logged in: {username}")
                return True, f"Welcome back, {username}!"
            else:
                conn.close()
                return False, "Invalid username or password"
                
        except sqlite3.Error as e:
            logger.error(f"Login error: {e}")
            return False, "Database error occurred"

    def logout(self) -> None:
        """Log out the current user."""
        logger.info(f"User logged out: {self.current_username}")
        self.current_user_id = None
        self.current_username = None

    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user_id is not None

    def get_current_username(self) -> Optional[str]:
        """Get the current logged-in username."""
        return self.current_username

    def save_score(self, score: int) -> bool:
        """
        Save a game score for the current user.
        
        Args:
            score: Final score
            
        Returns:
            True if save was successful
        """
        if not self.is_logged_in():
            logger.warning("Cannot save score: no user logged in")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO high_scores (user_id, score) VALUES (?, ?)",
                (self.current_user_id, score)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Score saved: {score} for user {self.current_username}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving score: {e}")
            return False

    def get_high_score(self) -> int:
        """
        Get the current user's highest score.
        
        Returns:
            Highest score, or 0 if none
        """
        if not self.is_logged_in():
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT MAX(score) FROM high_scores WHERE user_id = ?",
                (self.current_user_id,)
            )
            
            result = cursor.fetchone()[0]
            conn.close()
            
            return result if result else 0
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching high score: {e}")
            return 0

    def get_user_scores(self, limit: int = 10) -> list[dict]:
        """
        Get the current user's top scores.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of score dictionaries
        """
        if not self.is_logged_in():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT score, achieved_at
                   FROM high_scores 
                   WHERE user_id = ?
                   ORDER BY score DESC
                   LIMIT ?""",
                (self.current_user_id, limit)
            )
            
            scores = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return scores
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching user scores: {e}")
            return []

    def get_global_leaderboard(self, limit: int = 10) -> list[dict]:
        """
        Get global top scores across all users (one high score per user).
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of score dictionaries with usernames
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT u.username, MAX(h.score) as score, 
                          MAX(h.achieved_at) as achieved_at
                   FROM high_scores h
                   JOIN users u ON h.user_id = u.user_id
                   GROUP BY u.user_id, u.username
                   ORDER BY score DESC
                   LIMIT ?""",
                (limit,)
            )
            
            scores = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return scores
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching leaderboard: {e}")
            return []
