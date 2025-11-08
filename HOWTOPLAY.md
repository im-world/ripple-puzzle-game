# How to Play Ripple

A comprehensive guide to mastering the art of ripple-based puzzle solving.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Control Scheme](#control-scheme)
3. [Catapult Mechanics](#catapult-mechanics)
4. [Understanding Wave Physics](#understanding-wave-physics)
5. [Strategy Guide](#strategy-guide)
6. [Advanced Techniques](#advanced-techniques)
7. [Level-Specific Tips](#level-specific-tips)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Launch

1. Run `python main.py` from the project directory
2. Click **Start Game** from the main menu
3. You'll begin at Level 1 with 10 stones

### Game Screen Layout

```
┌─────────────────────────────────────────┐
│         Stones: 10          [Top]       │
├─────────────────────────────────────────┤
│                                         │
│    🔴 (Red Starting Spot)               │
│                                         │
│         Water Pool                      │
│         (Pastel Blue)                   │
│                                         │
│                  🟢 (Green Target)      │
│                                         │
├─────────────────────────────────────────┤
│         🏹 Catapult        [Bottom]     │
└─────────────────────────────────────────┘
```

### Objective

Guide the ball from the red starting spot to the green target spot using ripples created by launching stones into the water.

---

## Control Scheme

### Mouse Controls

**Aiming**:
- **Click and Hold** on the catapult area (bottom of screen)
- The catapult arm will pull back and aim toward your cursor

**Adjusting Your Shot**:
- **Move Mouse** while holding the button
- The trajectory preview line updates in real-time
- The power meter shows launch strength

**Launching**:
- **Release Mouse Button** to launch the stone
- The stone follows a parabolic arc to the predicted landing point

### Visual Indicators

While aiming, you'll see:
- **Dotted Trajectory Line**: Shows the stone's flight path
- **Landing Marker**: Circle indicating where the stone will hit the water
- **Power Meter**: Vertical bar near the catapult showing launch strength
  - Green = Low power
  - Yellow = Medium power
  - Red = High power
- **Catapult Arm**: Rotates and pulls back based on your aim

---

## Catapult Mechanics

### Aiming System

**Angle Control**:
- The catapult aims toward your mouse cursor
- Pull back farther from the catapult for more power
- Pull at different angles to change the landing position

**Power Calculation**:
- Power is based on the distance between your cursor and the catapult
- Maximum power is reached at approximately 200 pixels from the catapult
- The power meter provides visual feedback

**Trajectory Preview**:
- The dotted line shows the exact path your stone will take
- The landing marker circle shows the impact point
- Both X (horizontal) and Y (vertical) positions are accurately predicted
- Use this to plan your ripple placement precisely

### Launch Physics

**Projectile Motion**:
- Stones follow realistic parabolic arcs
- Gravity pulls the stone down as it flies
- Initial velocity is determined by your aim angle and power

**Impact**:
- When the stone hits the water, it creates a splash effect
- A ripple immediately begins propagating from the impact point
- The stone sinks and disappears after impact

### Tips for Accurate Aiming

1. **Take Your Time**: There's no time limit—aim carefully
2. **Use the Preview**: The trajectory line is accurate—trust it
3. **Experiment**: Try different angles and powers to see their effects
4. **Plan Ahead**: Think about where you want the ripple, not just where the stone lands

---

## Understanding Wave Physics

### Ripple Behavior

**Creation**:
- Each stone impact creates one ripple at the landing point
- Ripples begin with maximum amplitude (strength)

**Propagation**:
- Ripples expand outward in perfect circles
- Propagation speed: 200 pixels per second
- Lifetime: 5 seconds before disappearing

**Amplitude Decay**:
- Ripple strength decreases exponentially over time
- Formula: A(t) = A₀ × e^(-0.3t)
- Older ripples have less pushing force than fresh ones

**Visual Representation**:
- Ripples appear as expanding circular waves on the water
- Transparency indicates current strength (more transparent = weaker)
- Watch the fish—they react to nearby ripples, showing wave presence

### Force Application

**How Ripples Push the Ball**:
- Ripples exert radial force (pushing outward from the center)
- Force strength depends on:
  - Current amplitude (decreases over time)
  - Distance from ripple center (closer = stronger)
- The ball accelerates in the direction of the net force

**Distance Falloff**:
- Force decreases with distance from the ripple center
- Formula: force_factor = 1 / (1 + distance²)
- Ripples are most effective when close to the ball

### Wave Interference

**Multiple Ripples**:
- When multiple ripples overlap, their forces combine
- This is vector addition—forces add in both X and Y directions

**Constructive Interference**:
- Ripples pushing in the same direction create stronger combined force
- Example: Two ripples on opposite sides of the ball push it in one direction

**Complex Patterns**:
- Three or more ripples can create curved paths
- Strategic placement allows you to "steer" the ball around obstacles
- Timing matters—launch stones in sequence for continuous force

---

## Strategy Guide

### Basic Strategies

**1. Direct Push**:
- Place a ripple directly behind the ball (opposite the target)
- Simple and effective for short distances
- Uses 1-2 stones

**2. Sequential Ripples**:
- Launch multiple stones in a line behind the ball
- Each new ripple continues pushing as the previous one fades
- Good for long distances
- Uses 3-4 stones

**3. Angled Approach**:
- Place ripples at angles to guide the ball around obstacles
- Requires understanding of force vectors
- More stone-efficient for complex paths

**4. Interference Steering**:
- Use multiple simultaneous ripples to create curved paths
- Place stones on both sides of the desired path
- Advanced technique but very powerful

### Stone Placement Tips

**Optimal Distance**:
- Place ripples 50-150 pixels from the ball for best effect
- Too close: Ball moves too fast and overshoots
- Too far: Weak force, ball barely moves

**Timing**:
- Wait for previous ripples to fade before launching new ones (for control)
- OR launch quickly for maximum combined force (for power)
- Watch the ripple transparency to judge remaining strength

**Prediction**:
- Anticipate where the ball will be, not just where it is now
- Lead your shots if the ball is already moving
- Account for momentum and friction

### Resource Management

**Stone Conservation**:
- Level 1: Try to complete with 6-7 stones (save 3-4 for Level 2)
- Level 2: Use remaining stones wisely around obstacles
- Experiment in early attempts, then execute efficiently

**When to Reset**:
- If you've used 8+ stones and the ball is barely closer to the target
- If the ball is moving away from the target with no stones left
- If you want to try a different strategy

---

## Advanced Techniques

### The Slingshot

Create a "pocket" of ripples around the ball:
1. Place 3 stones in a triangle around the ball
2. The ball will be pushed toward the center, then accelerate outward
3. Time the fourth stone to catch the ball and direct it toward the target

### The Corridor

Guide the ball through a narrow path:
1. Place ripples alternating on left and right sides
2. Each ripple nudges the ball back toward the center line
3. Effective for navigating between obstacles

### The Brake

Stop a fast-moving ball:
1. Place a ripple directly in front of the ball's path
2. The opposing force will slow or stop the ball
3. Useful if the ball is heading the wrong direction

### Wave Timing

Maximize force by synchronizing ripples:
1. Launch stones in quick succession (0.5-1 second apart)
2. Ripples will overlap at the ball's position
3. Combined amplitude creates powerful push
4. Risk: Less control, potential overshoot

---

## Level-Specific Tips

### Level 1: Open Water

**Layout**:
- Ball starts on the left
- Target on the right
- No obstacles

**Strategy**:
- Direct approach works well
- Use 2-3 ripples in a line behind the ball
- Aim slightly above or below the direct line to account for drift

**Par**: 6-7 stones

**Common Mistakes**:
- Using too much power (ball overshoots)
- Not accounting for momentum (ball keeps moving after ripples fade)
- Placing ripples too far from the ball

### Level 2: Anti-Ripple Zone

**Layout**:
- Ball starts on the left
- Target on the right
- Rectangular anti-ripple zone in the middle

**Challenge**:
- Ripples cannot pass through the obstacle
- Must find a path around it

**Strategy**:
- **Option A**: Go over the top
  - Place ripples below the ball to push it upward
  - Once above the obstacle, push right toward the target
  
- **Option B**: Go under the bottom
  - Place ripples above the ball to push it downward
  - Once below the obstacle, push right toward the target

- **Option C**: Curved path
  - Use angled ripples to create an arc around the obstacle
  - More stone-efficient but requires precision

**Par**: 4-6 stones (with carryover from Level 1)

**Common Mistakes**:
- Trying to push straight through the obstacle
- Not accounting for the ball's momentum carrying it into the obstacle
- Using too many stones on the first approach

---

## Troubleshooting

### Common Issues

**"The ball isn't moving"**
- **Cause**: Ripples are too far away or have faded
- **Solution**: Place stones closer to the ball (50-100 pixels)
- **Check**: Are there any active ripples? Look for expanding circles

**"The ball moved the wrong direction"**
- **Cause**: Ripple placement or wave interference
- **Solution**: Remember ripples push AWAY from their center
- **Tip**: Place ripples on the opposite side of where you want the ball to go

**"The trajectory preview doesn't match where the stone lands"**
- **Cause**: This shouldn't happen—the preview is accurate
- **Check**: Make sure you're not moving the mouse between aiming and releasing
- **Note**: If this persists, it may be a bug—please report it

**"I can't aim the catapult"**
- **Cause**: Clicking outside the catapult area
- **Solution**: Click and hold near the bottom center of the screen
- **Visual**: The catapult arm should appear and pull back

**"The ball is stuck and won't move"**
- **Cause**: Ball velocity near zero with no active ripples
- **Solution**: Launch more stones to create new ripples
- **Prevention**: Keep ripples active until the ball reaches the target

**"I ran out of stones"**
- **Cause**: Inefficient stone placement or strategy
- **Solution**: Click "Retry Level" to try again with 10 stones
- **Learning**: Analyze what went wrong and try a different approach

**"The game is laggy"**
- **Cause**: Too many active ripples or system resources
- **Solution**: The game automatically reduces quality if FPS drops
- **Help**: Close other applications to free up resources

**"No sound effects"**
- **Cause**: Audio files missing or system volume muted
- **Solution**: 
  - Check system volume settings
  - Verify files exist in `assets/` directory
  - Adjust volume in Settings menu

### Performance Tips

- The game targets 60 FPS
- If performance drops, the game will automatically:
  - Reduce ripple visual quality
  - Limit active ripples
  - Disable fish animations
- Close background applications for best performance

---

## Practice Exercises

### Exercise 1: Precision Aiming
- Complete Level 1 using only 3 stones
- Focus on accurate trajectory prediction

### Exercise 2: Wave Interference
- Create a ripple on each side of the ball simultaneously
- Observe how the forces combine

### Exercise 3: Momentum Management
- Get the ball moving, then stop it before it reaches the target
- Practice using opposing ripples as brakes

### Exercise 4: Curved Path
- Guide the ball in a circular path back to the starting spot
- Master angled ripple placement

---

## Keyboard Shortcuts

- **ESC**: Pause game / Return to menu
- **Mouse Click**: All interactions

---

## Final Tips

1. **Patience is key**: Take time to aim carefully
2. **Observe the physics**: Watch how ripples affect the ball
3. **Learn from mistakes**: Each attempt teaches you something
4. **Experiment freely**: There's no penalty for trying different approaches
5. **Enjoy the zen**: The game is designed to be calming—don't stress about perfection

Remember: The journey is as important as the destination. Enjoy the ripples! 🌊

---

**Need more help?** Check the README.md for installation and technical information.
