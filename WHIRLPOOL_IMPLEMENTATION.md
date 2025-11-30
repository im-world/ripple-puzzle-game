# Whirlpool Obstacle Implementation

## Overview
Whirlpools are circular obstacles that pull the ball toward their center with increasing force. If the ball gets too close to the center, it becomes stuck and the player loses.

## Features Implemented

### 1. Whirlpool Class (`game/level.py`)
- **Circular shape** with configurable center point and radius
- **Pull strength** parameter controls force magnitude
- **Center threshold** (15% of radius) defines the "stuck" zone

### 2. Physics Integration (`game/physics.py`)

#### Radial Force Toward Center
- Force increases quadratically as ball approaches center
- Formula: `force = pull_strength * (1 - distance/radius)²`
- At edge: force = 0
- At center: force = maximum
- Direction always points toward whirlpool center

#### Ball Escape Mechanics
- Ball can escape if ripple forces overcome whirlpool pull
- Net force = whirlpool pull + ripple forces
- If net force points away from center, ball escapes
- Creates strategic gameplay: timing stone throws to create escape ripples

### 3. Lose Condition
- Ball is "stuck" when it enters the center threshold (15% of radius)
- Triggers game over state
- Visual warning: red pulsing danger zone in center

### 4. Ripple Trajectory Curving
- Ripples curve toward whirlpool center as they propagate
- Curve strength increases closer to center
- Maximum 50% influence on ripple direction
- Creates realistic water physics effect

### 5. Visual Rendering (`game/renderer.py`)

#### Swirling Water Animation
- Rotating spiral patterns (6 spirals)
- Gradient from light at edge to dark at center
- Animated particles rotating around edge
- Smooth rotation at 2 radians/second

#### Danger Zone Visualization
- Red pulsing center area
- Indicates the "stuck" threshold
- Warns players of danger

#### Color Scheme
- Dark blue gradient (darker toward center)
- White/blue spiral lines
- Red danger zone in center
- Rotating white particles at edge

### 6. Level JSON Format
```json
{
  "whirlpools": [
    {
      "position": [400, 300],
      "radius": 100,
      "pull_strength": 200
    }
  ]
}
```

## Physics Parameters

### Recommended Values
- **Radius**: 60-120 pixels (depending on level difficulty)
- **Pull Strength**: 100-300 (higher = harder to escape)
- **Center Threshold**: Automatically calculated as 15% of radius

### Force Calculation
```python
distance_ratio = 1.0 - (distance / radius)  # 0 at edge, 1 at center
force_magnitude = pull_strength * (distance_ratio ** 2)  # Quadratic increase
```

## Gameplay Strategy

### For Players
1. **Avoid the center**: Stay away from the red danger zone
2. **Use ripples to escape**: Create strong ripples on the far side to push ball away
3. **Timing is key**: Launch stones when ball is being pulled in
4. **Multiple ripples**: Combine forces from multiple ripples for stronger escape

### For Level Designers
1. **Placement**: Position whirlpools to create challenging paths
2. **Strength tuning**: Lower strength = easier to escape, higher = more dangerous
3. **Radius sizing**: Larger radius = wider danger area
4. **Combinations**: Combine with walls and current zones for complex puzzles

## Testing
All whirlpool features have been tested:
- ✓ Whirlpool creation and configuration
- ✓ Force calculation (quadratic increase toward center)
- ✓ Stuck condition (lose condition)
- ✓ Ball escape with ripple forces
- ✓ Ripple trajectory curving
- ✓ JSON serialization/deserialization
- ✓ Integration with LevelData

Run tests: `python test_whirlpool.py`

## Integration Points

### Main Game Loop (`main.py`)
- Whirlpools loaded from level JSON
- Set on wave simulator and ball physics
- Checked for stuck condition each frame
- Rendered before ripples (layer order)

### Wave Simulator (`game/physics.py`)
- Stores whirlpool list
- Applies whirlpool forces to ball
- Curves ripple trajectories (future enhancement)

### Ball Physics (`game/physics.py`)
- Receives whirlpool forces
- Combines with ripple and current zone forces
- Updates ball velocity and position

### Renderer (`game/renderer.py`)
- Renders swirling animation
- Shows danger zone
- Animates rotation and particles

## Example Level
Level 2 now includes a whirlpool at position (300, 500) with radius 80 and pull strength 150. Players must navigate around it while dealing with walls and current zones.

## Future Enhancements (Optional)
- Multiple whirlpools with overlapping effects
- Whirlpool strength that varies over time (pulsing)
- Visual ripple distortion when passing through whirlpool
- Sound effects for whirlpool pull and stuck condition
