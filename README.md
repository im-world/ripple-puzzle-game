# Ripple

A zen-themed puzzle game where you guide a ball to its target by creating ripples in a tranquil water pool.

## Overview

Ripple is a meditative physics-based puzzle game that combines strategy with relaxation. Launch stones into a serene water pool to create realistic wave ripples that push a floating ball toward its destination. With calming pastel aesthetics, ambient sounds, and intuitive controls, Ripple offers a unique blend of challenge and tranquility.

## Game Objective

Your goal is simple: guide the ball from the red starting spot to the green target spot using ripples created by launching stones into the water. But there's a catch—you have a limited number of stones, so every throw counts!

## How Ripples Work

When a stone hits the water, it creates a circular ripple that propagates outward. These ripples aren't just visual—they generate real physical forces that push the ball:

- **Wave Propagation**: Ripples expand outward at a constant speed for 5 seconds
- **Amplitude Decay**: Wave strength decreases exponentially over time, simulating natural dissipation
- **Force Application**: Ripples push the ball radially away from their center with force proportional to their current amplitude
- **Wave Interference**: Multiple ripples combine their forces, creating complex interference patterns that can push the ball in unexpected directions
- **Physics Simulation**: The ball responds with realistic momentum, inertia, and water friction

Understanding wave interference is key to mastering Ripple. Strategic stone placement can create constructive interference (waves combining to push harder) or use multiple ripples to guide the ball along curved paths.

## Level Completion

To complete a level:
1. The ball must enter the green target spot
2. You must accomplish this before running out of stones

When you successfully complete a level:
- Any remaining stones carry over to the next level
- You'll see statistics showing how many stones you used
- The next level begins with your remaining stone inventory

## Stone Mechanics


**Stone Inventory**:
- You start with 10 stones at the beginning of the game
- Each stone launch decrements your counter by one
- Unused stones carry over between levels
- The stone counter is displayed at the top of the screen

**Resource Management**:
- Plan your shots carefully—once you're out of stones, it's game over
- Experiment with different stone placements to find efficient solutions
- Sometimes fewer, well-placed stones work better than many random throws

**Game Over Condition**:
- If your stone counter reaches zero and the ball hasn't reached the target, the level fails
- You can retry the level or return to the main menu

## Obstacles

As you progress through levels, you'll encounter new challenges:

**Anti-Ripple Zones** (Level 2+):
- Static rectangular barriers that block wave propagation
- Ripples cannot pass through these zones
- Forces the player to find creative stone placement strategies
- Adds strategic depth by limiting direct paths to the target

## Controls

**Mouse Controls**:
- **Click and Hold**: Aim the catapult
- **Mouse Movement**: Adjust angle and power while holding
- **Release**: Launch the stone

**Visual Feedback**:
- **Trajectory Preview**: Dotted line shows where your stone will land
- **Power Meter**: Indicates launch strength based on pull-back distance
- **Landing Marker**: Circle at the predicted impact point

## Installation

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: 512 MB minimum
- **Display**: 1024x768 resolution or higher
- **Audio**: Sound card for audio effects and music (optional)

### Installation Steps

1. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd ripple
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install Pygame, the only required dependency.

3. **Verify installation**:
   ```bash
   python --version
   ```
   Ensure Python 3.7+ is installed.

## How to Play

### Launch the Game

Run the following command from the project directory:

```bash
python main.py
```

The game window will open at 1024x768 resolution.

### Main Menu

- **Start Game**: Begin from level 1
- **Settings**: Adjust sound effects and music volume
- **Exit**: Close the game

### Gameplay

1. The ball starts at the red spot
2. Aim the catapult by clicking and dragging
3. Release to launch a stone
4. Watch the ripples push the ball
5. Guide the ball to the green target spot
6. Complete levels efficiently to conserve stones

### Tips

- Experiment with stone placement before committing
- Use the trajectory preview to aim accurately
- Multiple ripples can create powerful combined forces
- Sometimes indirect paths are more efficient than direct ones
- Watch how fish react to ripples—they show wave propagation in real-time

## Game Features

- **Realistic Wave Physics**: Authentic ripple propagation with interference patterns
- **Zen Aesthetic**: Calming pastel colors and smooth animations
- **Ambient Audio**: Gentle sound effects and looping background music
- **Progressive Difficulty**: Multiple levels with increasing complexity
- **Resource Management**: Strategic stone usage adds puzzle depth
- **Responsive Controls**: 60 FPS gameplay with sub-16ms input latency
- **Living Environment**: Fish swim and react to ripples naturally

## Project Structure

```
ripple/
├── main.py                 # Game entry point and main loop
├── requirements.txt        # Python dependencies
├── game/                   # Game modules
│   ├── audio.py           # Audio manager and sound effects
│   ├── catapult.py        # Catapult mechanics and trajectory
│   ├── config.py          # Configuration constants
│   ├── fish.py            # Fish entities and animations
│   ├── level.py           # Level management and progression
│   ├── particles.py       # Particle effects system
│   ├── physics.py         # Wave simulation and ball physics
│   ├── renderer.py        # Rendering system
│   └── transitions.py     # Screen transitions and effects
├── assets/                 # Audio files
│   ├── launch.wav
│   ├── splash.wav
│   ├── ripple.wav
│   ├── ball_move.wav
│   ├── level_complete.wav
│   ├── click.wav
│   └── background.ogg
└── levels/                 # Level data
    └── level_data.json    # Level definitions

```

## Troubleshooting

**Game won't start**:
- Verify Python 3.7+ is installed: `python --version`
- Ensure Pygame is installed: `pip install pygame`
- Check that you're in the correct directory

**No sound**:
- Check system volume settings
- Verify audio files exist in the `assets/` directory
- Adjust volume in the game's Settings menu

**Low frame rate**:
- Close other applications to free up resources
- The game automatically reduces quality if FPS drops below 50

**Ball gets stuck**:
- This is rare but can happen with certain ripple patterns
- If the ball doesn't move for several seconds, consider it a learning opportunity for better stone placement
- Restart the level if needed

## Credits

Ripple was created as a demonstration of physics-based puzzle game design with an emphasis on calming, meditative gameplay.

## License

This project is provided as-is for educational and entertainment purposes.

---

Enjoy the tranquility of Ripple! 🌊
