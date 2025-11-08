# Physics and Catapult Animation Fixes

## Issues Fixed

### 1. Stone Landing Physics Issue - TOP-DOWN VIEW
**Problem:** Stones were falling off screen instead of landing inside the pond.

**Root Cause:**
The game uses a **top-down 2D perspective** (bird's eye view of the water surface), but the physics was implemented as a side-view projectile with gravity pulling stones downward off the screen. In a top-down view, there is no vertical gravity - stones travel across the water surface plane.

**Fixes Applied:**

1. **Removed Gravity-Based Physics** (`game/catapult.py`):
   - Removed all gravity calculations (GRAVITY constant no longer used)
   - Stones now travel in straight lines across the 2D water surface
   - Flight time determines when stone lands (simulates arc height in 3D)
   - Formula: `position += velocity * dt` (simple linear motion)

2. **Flight Time System** (`game/catapult.py` and `game/config.py`):
   - Added `flight_time` parameter to Stone class
   - Flight time ranges from 0.3s (low power) to 1.0s (high power)
   - Stone lands when `elapsed_time >= flight_time` AND inside water pool
   - This simulates the stone's arc in 3D projected to 2D top-down view

3. **Improved Landing Detection** (`game/catapult.py`):
   - Stone lands only when inside water pool boundaries
   - Checks both horizontal (X) and vertical (Y) bounds
   - Stones that miss the pool or go off-screen are removed
   - Landing creates ripple at exact impact position

### 2. Trajectory Visibility Issue
**Problem:** The trajectory line was not visible, making it difficult to aim.

**Fixes Applied** (`game/renderer.py`):
1. Increased line thickness from 3px to 4px with 6px black outline
2. Changed dots from every 3rd point to every 2nd point
3. Made dots bright yellow (255, 255, 0) with white centers
4. Enhanced landing marker with pulsing animation
5. Added semi-transparent yellow fill to landing marker
6. Increased landing marker size and pulse amplitude

### 3. Catapult Animation Direction Issue
**Problem:** The catapult arm animation was horizontally inverted - when pulling left, the arm pointed right, and vice versa.

**Root Cause:** The catapult rendering was using `aim_angle` (the launch direction) instead of the pull direction for visual feedback. Since launch direction is opposite to pull direction, the visual was backwards.

**Fix Applied** (`game/catapult.py` and `game/renderer.py`):
1. Added `pull_angle` attribute to Catapult class to store the visual pull direction separately from launch physics
2. Updated `update_aim()` to calculate both:
   - `aim_angle` for physics (launch direction)
   - `pull_angle` for rendering (pull direction)
3. Modified `render_catapult()` to use `pull_angle` for arm position visualization
4. Now the arm visually follows the mouse pull direction while physics use the correct launch direction

## Files Modified

1. `game/catapult.py`:
   - Completely rewrote `Stone` class for top-down physics
   - Removed gravity-based projectile motion
   - Added `flight_time` parameter to Stone constructor
   - Implemented straight-line motion with timed landing
   - Added `pull_angle` attribute for visual feedback
   - Simplified `_calculate_trajectory()` for straight-line paths
   - Updated landing detection to check water pool bounds

2. `game/config.py`:
   - Removed `GRAVITY` constant (not needed for top-down view)
   - Added `STONE_FLIGHT_TIME_MIN = 0.3` seconds
   - Added `STONE_FLIGHT_TIME_MAX = 1.0` seconds

3. `game/renderer.py`:
   - Updated `render_catapult()` to use `pull_angle` instead of `aim_angle`
   - Enhanced trajectory line visibility (thicker, outlined, brighter)
   - Improved landing marker with pulsing animation and transparency
   - Changed trajectory dots to bright yellow with white centers

## Testing

The fixes ensure:
- ✅ Stones travel in straight lines across the water surface (top-down view)
- ✅ Stones land inside the water pool at the correct XY position
- ✅ Flight time determines landing (simulates 3D arc in 2D)
- ✅ Trajectory preview is highly visible with bright colors
- ✅ Landing marker pulses to show exact impact point
- ✅ Catapult arm animation matches the pull direction
- ✅ Launch direction is correctly opposite to pull direction
- ✅ Stones create ripples at their landing position within the pool
