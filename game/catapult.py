"""
Catapult module for Ripple game.
Handles catapult aiming, trajectory calculation, and stone launching.
"""

import math
from typing import List, Optional, Tuple
from game.physics import Vector2
from game.config import (
    CATAPULT_MAX_POWER, CATAPULT_MAX_DISTANCE,
    SCREEN_WIDTH, SCREEN_HEIGHT, WATER_POOL_RECT, STONE_SIZE_RATIO, BALL_RADIUS,
    STONE_FLIGHT_TIME_MIN, STONE_FLIGHT_TIME_MAX
)


class Stone:
    """Stone projectile entity for top-down 2D view."""
    
    def __init__(self, position: Vector2, velocity: Vector2, flight_time: float):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.flight_time = flight_time  # How long stone flies before landing
        self.elapsed_time = 0.0
        self.in_flight = True
        self.sinking = False
        self.sink_timer = 0.0
        self.sink_duration = 0.5  # seconds
        self.radius = BALL_RADIUS * STONE_SIZE_RATIO
    
    def update(self, dt: float) -> bool:
        """
        Update stone physics for top-down view.
        Stone travels in straight line, then lands after flight_time.
        Returns True if stone is still active, False if it should be removed.
        """
        if self.sinking:
            # Update sinking animation
            self.sink_timer += dt
            if self.sink_timer >= self.sink_duration:
                return False  # Stone should be removed
            return True
        
        if self.in_flight:
            # Update elapsed time
            self.elapsed_time += dt
            
            # Move stone in straight line (no gravity in top-down view)
            self.position = self.position + self.velocity * dt
            
            # Check if flight time elapsed or stone is in water pool
            water_left = WATER_POOL_RECT[0]
            water_right = WATER_POOL_RECT[0] + WATER_POOL_RECT[2]
            water_top = WATER_POOL_RECT[1]
            water_bottom = WATER_POOL_RECT[1] + WATER_POOL_RECT[3]
            
            in_water_pool = (water_left <= self.position.x <= water_right and 
                           water_top <= self.position.y <= water_bottom)
            
            # Stone lands when flight time is up AND it's in the water pool
            if self.elapsed_time >= self.flight_time and in_water_pool:
                # Stone hit water
                self.in_flight = False
                self.sinking = True
                return True
            
            # Remove stone if it goes off screen
            if (self.position.x < 0 or self.position.x > SCREEN_WIDTH or
                self.position.y < 0 or self.position.y > SCREEN_HEIGHT):
                return False
        
        return True
    
    def get_impact_position(self) -> Optional[Vector2]:
        """Get the position where stone impacted water, or None if still in flight."""
        if self.sinking or not self.in_flight:
            return self.position.copy()
        return None
    
    def has_landed(self) -> bool:
        """Check if stone has landed in water (not in flight anymore)."""
        return not self.in_flight
    
    def get_alpha(self) -> float:
        """Get alpha transparency for rendering (1.0 = opaque, 0.0 = transparent)."""
        if self.sinking:
            # Fade out during sinking
            return 1.0 - (self.sink_timer / self.sink_duration)
        return 1.0
    
    def get_scale(self) -> float:
        """Get scale factor for rendering during sinking animation."""
        if self.sinking:
            # Scale down during sinking
            return 1.0 - (self.sink_timer / self.sink_duration) * 0.5
        return 1.0


class Catapult:
    """Catapult controller for aiming and launching stones."""
    
    def __init__(self, position: Vector2):
        self.position = position.copy()
        self.is_aiming = False
        self.aim_angle = 0.0  # radians - launch direction in screen coordinates
        self.pull_angle = 0.0  # radians - visual pull direction for rendering
        self.aim_power = 0.0  # normalized [0, 1]
        self.trajectory_points: List[Vector2] = []
        self.landing_position: Optional[Vector2] = None
    
    def start_aiming(self, mouse_pos: Tuple[int, int]):
        """Start aiming mode when mouse is pressed."""
        self.is_aiming = True
        self.pull_angle = 0.0  # Initialize pull angle
        self.update_aim(mouse_pos)
    
    def update_aim(self, mouse_pos: Tuple[int, int]):
        """
        Update aim angle and power based on mouse position.
        Catapult works like a slingshot: pull BACK to launch FORWARD.
        The launch direction is OPPOSITE to the pull direction.
        """
        if not self.is_aiming:
            return
        
        mouse_x, mouse_y = mouse_pos
        
        # Calculate pull direction (from catapult to mouse)
        pull_dx = mouse_x - self.position.x
        pull_dy = mouse_y - self.position.y
        
        # Launch direction is OPPOSITE to pull direction
        launch_dx = -pull_dx
        launch_dy = -pull_dy
        
        # Calculate angle for launch physics (in screen coordinates)
        # Screen Y increases downward, so positive dy means downward
        self.aim_angle = math.atan2(launch_dy, launch_dx)
        
        # Store pull angle separately for rendering (visual feedback)
        self.pull_angle = math.atan2(pull_dy, pull_dx)
        
        # Calculate power based on pull distance
        pull_distance = math.sqrt(pull_dx * pull_dx + pull_dy * pull_dy)
        self.aim_power = min(pull_distance / CATAPULT_MAX_DISTANCE, 1.0)
        
        # Update trajectory preview
        self._calculate_trajectory()
    
    def stop_aiming(self) -> Optional[Stone]:
        """
        Stop aiming and launch stone.
        Returns Stone object if launched, None if aiming was cancelled.
        """
        if not self.is_aiming:
            return None
        
        self.is_aiming = False
        
        # Create stone with initial velocity
        stone = self._create_stone()
        
        # Clear trajectory preview
        self.trajectory_points = []
        self.landing_position = None
        
        return stone
    
    def cancel_aiming(self):
        """Cancel aiming without launching."""
        self.is_aiming = False
        self.trajectory_points = []
        self.landing_position = None
    
    def _create_stone(self) -> Stone:
        """Create a stone with initial velocity based on current aim."""
        # Calculate initial velocity from power and angle
        initial_speed = self.aim_power * CATAPULT_MAX_POWER
        vx = initial_speed * math.cos(self.aim_angle)
        vy = initial_speed * math.sin(self.aim_angle)
        
        velocity = Vector2(vx, vy)
        
        # Calculate flight time based on power (higher power = longer flight)
        # This simulates the arc height in 3D projected to 2D top-down view
        flight_time = STONE_FLIGHT_TIME_MIN + (self.aim_power * (STONE_FLIGHT_TIME_MAX - STONE_FLIGHT_TIME_MIN))
        
        # Stone starts at catapult position
        return Stone(self.position, velocity, flight_time)
    
    def _calculate_trajectory(self):
        """
        Calculate trajectory preview for top-down view.
        Stone travels in straight line for a fixed flight time.
        """
        self.trajectory_points = []
        self.landing_position = None
        
        # Need minimum power to show trajectory
        if self.aim_power < 0.05:
            return
        
        # Initial conditions
        x0 = self.position.x
        y0 = self.position.y
        initial_speed = self.aim_power * CATAPULT_MAX_POWER
        
        # Calculate velocity components
        vx = initial_speed * math.cos(self.aim_angle)
        vy = initial_speed * math.sin(self.aim_angle)
        
        # Calculate flight time (same as in _create_stone)
        flight_time = STONE_FLIGHT_TIME_MIN + (self.aim_power * (STONE_FLIGHT_TIME_MAX - STONE_FLIGHT_TIME_MIN))
        
        # Calculate landing position (straight line motion)
        x_landing = x0 + vx * flight_time
        y_landing = y0 + vy * flight_time
        
        self.landing_position = Vector2(x_landing, y_landing)
        
        # Generate trajectory preview points (straight line)
        num_points = 15
        for i in range(num_points + 1):
            t = (i / num_points) * flight_time
            x = x0 + vx * t
            y = y0 + vy * t
            self.trajectory_points.append(Vector2(x, y))
    
    def get_trajectory_points(self) -> List[Vector2]:
        """Get trajectory preview points for rendering."""
        return self.trajectory_points
    
    def get_landing_position(self) -> Optional[Vector2]:
        """Get predicted landing position for rendering."""
        return self.landing_position

