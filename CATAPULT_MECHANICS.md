# Catapult Mechanics Explanation - TOP-DOWN VIEW

## Game Perspective

This is a **top-down 2D game** - you're looking at the water surface from above (bird's eye view).

```
     ┌─────────────────────────────────┐
     │                                 │
     │         Water Surface           │
     │        (viewed from above)      │
     │                                 │
     │          [Catapult]             │
     │                                 │
     └─────────────────────────────────┘
```

## How the Slingshot Works

### Pull and Launch Directions

```
                    Launch Direction ↑
                                    |
                                    |
                    [Catapult] -----+
                                    |
                                    |
                    Pull Direction  ↓ (Mouse)
```

When you pull the catapult in one direction, the stone launches in the **opposite direction**.

### Coordinate System

Screen Coordinates (top-down view):
- X: 0 (left) → 1024 (right)
- Y: 0 (top) → 768 (bottom)

```
(0,0) ────────────────────────────→ X (1024)
  |
  |     ┌─────────────────────┐
  |     │                     │
  |     │    Water Pool       │
  |     │    (top-down)       │
  |     │                     │
  |     │   [Catapult]        │
  |     │                     │
  |     └─────────────────────┘
  |
  ↓
  Y (768)
```

## Physics Flow

### 1. User Input
- Mouse at position (mx, my)
- Catapult at position (cx, cy)

### 2. Pull Calculation
```python
pull_dx = mx - cx
pull_dy = my - cy
pull_angle = atan2(pull_dy, pull_dx)  # For visual feedback
```

### 3. Launch Calculation
```python
launch_dx = -pull_dx  # Opposite direction
launch_dy = -pull_dy
aim_angle = atan2(launch_dy, launch_dx)  # For physics
```

### 4. Initial Velocity
```python
speed = power * MAX_POWER
vx = speed * cos(aim_angle)
vy = speed * sin(aim_angle)
```

### 5. Flight Time
```python
flight_time = 0.3 + (power * 0.7)  # 0.3s to 1.0s
```
Higher power = longer flight time (simulates higher arc in 3D)

### 6. Stone Motion (Top-Down)
```python
Every frame (dt):
  position.x += vx * dt  # Move horizontally
  position.y += vy * dt  # Move vertically (on water surface)
  elapsed_time += dt
  
  if elapsed_time >= flight_time and in_water_pool:
    land()  # Create ripple
```

**Key Point:** No gravity! Stone travels in straight line across water surface.

### 7. Landing
- Stone lands when `elapsed_time >= flight_time`
- Must be within water pool boundaries
- Creates ripple at landing position

## Example Scenarios

### Scenario 1: Pull Down → Launch Up
```
Mouse: (512, 700)  [below catapult]
Catapult: (512, 618)
Pull: (0, 82) → straight down
Launch: (0, -82) → straight up
Result: Stone travels straight up across water surface
```

### Scenario 2: Pull Down-Left → Launch Up-Right
```
Mouse: (400, 700)
Catapult: (512, 618)
Pull: (-112, 82) → down and left
Launch: (112, -82) → up and right
Result: Stone travels diagonally up-right across water
```

### Scenario 3: Pull Down-Right → Launch Up-Left
```
Mouse: (624, 700)
Catapult: (512, 618)
Pull: (112, 82) → down and right
Launch: (-112, -82) → up and left
Result: Stone travels diagonally up-left across water
```

## Visual Feedback

### Trajectory Preview
- **Bright white line** with black outline (4px thick)
- **Yellow dots** every 2nd point along path
- Shows exact straight-line path stone will take

### Landing Marker
- **Pulsing yellow circle** at landing point
- Pulses to draw attention
- Shows exactly where ripple will be created

### Catapult Arm
- Points in **pull direction** (where you're dragging)
- Stretches based on power
- Visual feedback matches your input

## Key Improvements

1. **Top-Down Physics:** Stones travel across water surface, not through it
2. **Straight Line Motion:** No gravity, simple linear trajectory
3. **Flight Time System:** Simulates 3D arc height in 2D view
4. **Visible Trajectory:** Bright colors and thick lines for easy aiming
5. **Bounds Checking:** Stones only land if inside water pool
6. **Visual Feedback:** Catapult arm shows pull direction clearly
