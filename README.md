# VoidRunner 🚀

**A 2D Space Survival Shooter built with Python and Pygame**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📖 Overview

VoidRunner is an arcade-style space shooter where you survive increasingly difficult waves of enemies while collecting power-ups and achieving high scores. This project demonstrates:

- ✅ Clean OOP architecture with inheritance and composition
- ✅ Efficient collision detection using sprite groups
- ✅ State management pattern for game flow
- ✅ Comprehensive unit testing (90%+ coverage goal)
- ✅ Frame-independent movement with delta time
- ✅ Asset management and caching

---

## 🎮 Features

### Core Gameplay (MVP)
- **Player Controls**: Smooth WASD/Arrow key movement and spacebar shooting
- **Enemy Types**: Basic enemies that move and shoot (more types coming soon!)
- **Wave System**: Increasing difficulty with each wave
- **Combat**: Satisfying bullet collision with explosion effects
- **HUD**: Real-time score, health bar, lives counter, and wave display
- **Health System**: 3 lives with 100 health per life

### Coming Soon
- 🔄 Power-ups (Rapid Fire, Shield Boost, Magnet)
- 🎯 Additional enemy types (Chaser, Zigzag)
- 💾 High score persistence
- 🎵 Sound effects and music
- 🏆 Full menu system (Main Menu, Pause, Game Over)

---

## 🛠️ Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/ammar/VoidRunner.git
cd VoidRunner
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Game

### Start the game:
```bash
python main.py
```

### Enable debug mode:
```bash
python main.py --debug
```

Debug mode shows:
- FPS counter
- Collision boxes
- Entity count

---

## 🎯 Controls

| Action | Keys |
|--------|------|
| **Move Up** | W or ↑ |
| **Move Down** | S or ↓ |
| **Move Left** | A or ← |
| **Move Right** | D or → |
| **Shoot** | Spacebar |
| **Pause** | ESC (coming soon) |
| **Restart** | R (when game over) |
| **Toggle Debug** | F3 |
| **Quit** | ESC (at game over) |

---

## 🧪 Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage report:
```bash
pytest --cov=voidrunner --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_player.py -v
```

### Run with verbose output:
```bash
pytest -v
```

---

## 📁 Project Structure

```
VoidRunner/
├── main.py                 # Entry point
├── voidrunner/
│   ├── __init__.py
│   ├── game.py             # Main game loop
│   ├── states/             # Game state classes
│   │   ├── base_state.py
│   │   └── playing_state.py
│   ├── entities/           # Game entities
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── bullet.py
│   │   └── enemies/
│   │       └── basic_enemy.py
│   ├── managers/           # System managers
│   │   ├── asset_manager.py
│   │   ├── spawn_manager.py
│   │   └── collision_manager.py
│   ├── ui/                 # UI components
│   │   └── hud.py
│   └── utils/              # Utilities
│       ├── config.py
│       └── helpers.py
├── assets/                 # Game assets
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
├── tests/                  # Unit tests
│   ├── conftest.py
│   ├── test_player.py
│   ├── test_enemy.py
│   └── test_collision_manager.py
├── requirements.txt
├── prd.md                  # Product requirements
└── README.md
```

---

## 🎨 Asset Credits

Currently using placeholder sprites (colored rectangles). Final game will use:

- **Kenney Space Shooter Redux** (CC0 License)
  - https://kenney.nl/assets/space-shooter-redux
  - Free pixel art assets for space games

---

## 🧩 Architecture Highlights

### OOP Principles
- **Inheritance**: `Enemy` base class with specialized subclasses
- **Composition**: Player uses bullet components, not inheritance
- **Encapsulation**: Private attributes with property accessors
- **Polymorphism**: Different enemy behaviors via `update_behavior()`

### Design Patterns
- **State Pattern**: Game states (Menu, Playing, Paused, GameOver)
- **Manager Pattern**: Asset, Spawn, and Collision managers
- **Sprite Groups**: Batch collision detection for performance

### Performance
- Target: 60 FPS with 20+ entities
- Delta time for frame-independent movement
- Object pooling for bullets (coming soon)
- Asset caching in AssetManager

---

## 🐛 Development

### Code Style
- PEP 8 compliant
- Black formatter (88 char line length)
- Type hints for all function signatures
- Comprehensive docstrings

### Format code:
```bash
black voidrunner/
```

### Lint code:
```bash
pylint voidrunner/
```

---

## 📊 Testing Coverage

Goal: 90%+ test coverage

Current test suites:
- ✅ `test_player.py` - Player movement, shooting, damage (20+ tests)
- ✅ `test_enemy.py` - Enemy behavior, spawning, damage (10+ tests)
- ✅ `test_collision_manager.py` - Collision detection (10+ tests)

---

## 🗓️ Development Roadmap

### Phase 1: Core Foundation ✅
- [x] Project structure
- [x] Basic game loop
- [x] Player movement and shooting
- [x] Enemy spawning (1 type)
- [x] Collision detection
- [x] Simple HUD
- [x] Unit tests

### Phase 2: Feature Completion
- [ ] All 3 enemy types
- [ ] Power-up system
- [ ] Wave progression
- [ ] Complete UI states
- [ ] High score persistence
- [ ] Sound effects

### Phase 3: Polish & Testing
- [ ] Final assets
- [ ] Background music
- [ ] Particle effects
- [ ] Playtesting and balancing
- [ ] Full test coverage
- [ ] Performance optimization

### Phase 4: Final Release
- [ ] Demo video
- [ ] Documentation
- [ ] Executable build

---

## 📝 License

This project is available under the MIT License.

---

## 🙏 Acknowledgments

- Pygame community for excellent documentation
- Kenney.nl for free game assets
- Open source community for inspiration

---

