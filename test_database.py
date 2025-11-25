"""
Test script for database operations.

Run this to verify SQLite authentication and score storage works correctly.
"""

from voidrunner.managers.data_manager import DataManager


def test_database():
    """Test database functionality."""
    print("=" * 50)
    print("VoidRunner Database Test")
    print("=" * 50)
    
    dm = DataManager()
    print("\n✓ Database initialized")
    
    # Test signup
    print("\n--- Testing Signup ---")
    success, msg = dm.signup("testuser", "password123")
    print(f"Signup attempt: {msg}")
    
    # Try duplicate username
    success, msg = dm.signup("testuser", "different")
    print(f"Duplicate signup: {msg}")
    
    # Test login
    print("\n--- Testing Login ---")
    success, msg = dm.login("testuser", "wrongpassword")
    print(f"Wrong password: {msg}")
    
    success, msg = dm.login("testuser", "password123")
    print(f"Correct login: {msg}")
    
    if success:
        print(f"Current user: {dm.get_current_username()}")
        print(f"Is logged in: {dm.is_logged_in()}")
    
    # Test score saving
    print("\n--- Testing Score Storage ---")
    print("Saving scores: 1500, 2200, 1800...")
    dm.save_score(1500)
    dm.save_score(2200)
    dm.save_score(1800)
    
    high_score = dm.get_high_score()
    print(f"High score: {high_score}")
    
    # Test getting user scores
    print("\n--- User's Top Scores ---")
    scores = dm.get_user_scores(limit=5)
    for i, score_data in enumerate(scores, 1):
        print(f"{i}. Score: {score_data['score']} - {score_data['achieved_at']}")
    
    # Create another user
    print("\n--- Testing Multiple Users ---")
    dm.logout()
    success, msg = dm.signup("player2", "test123")
    print(f"Second user signup: {msg}")
    
    if success:
        dm.login("player2", "test123")
        dm.save_score(2500)
        dm.save_score(3000)
        print(f"Player2 high score: {dm.get_high_score()}")
    
    # Test global leaderboard
    print("\n--- Global Leaderboard ---")
    leaderboard = dm.get_global_leaderboard(limit=10)
    for i, entry in enumerate(leaderboard, 1):
        print(f"{i}. {entry['username']}: {entry['score']} - {entry['achieved_at']}")
    
    print("\n" + "=" * 50)
    print("✓ All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_database()

