<div align="center">
  <h1>Ripple</h1>
  <p><b>A Zen-Themed Physics Puzzle Game</b></p>
</div>

**Ripple** is a meditative physics-based puzzle game that combines strategy with relaxation. Launch stones into a serene water pool to create realistic wave ripples that push a floating ball toward its destination. With calming pastel aesthetics, ambient sounds, and intuitive controls. You can also seamlessly play your favorite song in the background while enjoying this game to complete the zen experience!

<video src="game_demo.mp4" width="100%" controls autoplay loop></video>

---

## 🚀 Installation & Launch

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: 512 MB minimum
- **Display**: 1024x768 resolution or higher
- **Audio**: Sound card for audio effects and music (optional)

### Setup Steps
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ripple
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch the game**:
   ```bash
   python main.py
   ```

---

## 📖 How to Play

### Objective
Your goal is simple: guide the ball from the red starting spot to the green target spot using ripples created by launching stones into the water. But there's a catch—you have a limited number of stones, so every throw counts!

### Controls & Mechanics
1. **Aim:** Click and hold the mouse backward to aim your catapult. A dotted trajectory preview shows where your stone will land based on pull-back distance.
2. **Launch:** Release the mouse button to launch the stone. Once it hits the water, a ripple will expand outward.
3. **Push the Ball:** Ripples apply a radial pushing force against the ball. Experiment with different placements to take advantage of wave interference.
4. **Manage Resources:** Your remaining stones carry over when you beat a level. Running out of stones before the ball reaches the target results in game over!

---

## 🌟 Upcoming Features

- **Level Builder:** Design, customize, and share your own serene puzzle setups.
- **Fish Creator:** Customize and populate the aquatic life in your digital water pool.

---

## 🤝 Support the Developer

**Ripple** is completely free, open-source, and has no hidden fees. If this game gave you a moment of relaxation or helped you chill, please consider supporting its ongoing development!

---

## 🛠️ Contributing

Contributions to Ripple are welcome. Please ensure that any proposed changes adhere to the project's meditative atmosphere and our objective of maintaining an optimized, physics-based environment.

### 1. Local Development Setup
To build and run the game from source:
```bash
# Clone the repository
git clone https://github.com/yourusername/ripple.git
cd ripple

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the game locally
python main.py
```

### 2. Building the Executable
We can use PyInstaller to package the game. Once you have made your changes:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "levels;levels" main.py
```
*(Note: Ensure that assets and level data files are properly linked!)*

### 3. Guidelines
- **Code Style:** Follow PEP-8 standards. Keep core systems like `physics.py` and `renderer.py` clean, modular, and performant.
- **Game Aesthetics:** We prioritize a minimalistic, relaxing experience. Do not add stressful visual noise or discordant sounds.
- **Pull Requests:** Open an issue first to discuss major architectural changes, bug fixes, or entirely new levels before submitting a PR.
