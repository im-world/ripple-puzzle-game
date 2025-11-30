"""
Physics module for Ripple game.
Contains vector math utilities and physics data structures.
"""

import math
import time
from typing import List, Tuple
from game.config import (
    BALL_MASS, BALL_RADIUS, BALL_FRICTION, BALL_MAX_SPEED,
    RIPPLE_LIFETIME, RIPPLE_PROPAGATION_SPEED, RIPPLE_MAX_AMPLITUDE, RIPPLE_DECAY_RATE,
    WATER_POOL_RECT
)


class Vector2:
    """2D vector class with basic operations."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2':
        """Multiply vector by scalar."""
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vector2':
        """Multiply vector by scalar (reverse)."""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2':
        """Divide vector by scalar."""
        if scalar == 0:
            return Vector2(0, 0)
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self) -> 'Vector2':
        """Return a normalized (unit length) version of the vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)
    
    def copy(self) -> 'Vector2':
        """Return a copy of the vector."""
        return Vector2(self.x, self.y)
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple for Pygame compatibility."""
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


class Ball:
    """Ball entity with physics properties."""
    
    def __init__(self, position: Vector2, mass: float = BALL_MASS, radius: float = BALL_RADIUS):
        self.position = position.copy()
        self.velocity = Vector2(0, 0)
        self.mass = mass
        self.radius = radius
        self.friction = BALL_FRICTION
    
    def apply_force(self, force: Vector2, dt: float):
        """Apply force to the ball and update velocity."""
        # F = ma, so a = F/m
        acceleration = force / self.mass
        self.velocity = self.velocity + acceleration * dt
    
    def update_position(self, dt: float):
        """Update ball position based on velocity."""
        self.position = self.position + self.velocity * dt
    
    def apply_friction(self):
        """Apply friction to slow down the ball."""
        self.velocity = self.velocity * self.friction
    
    def clamp_velocity(self, max_speed: float = BALL_MAX_SPEED):
        """Clamp velocity to maximum speed."""
        speed = self.velocity.magnitude()
        if speed > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
    
    def keep_in_bounds(self, bounds: Tuple[float, float, float, float]):
        """Keep ball within specified boundaries (x, y, width, height)."""
        x, y, width, height = bounds
        
        # Check left boundary
        if self.position.x - self.radius < x:
            self.position.x = x + self.radius
            self.velocity.x = abs(self.velocity.x) * 0.5  # Bounce with damping
        
        # Check right boundary
        if self.position.x + self.radius > x + width:
            self.position.x = x + width - self.radius
            self.velocity.x = -abs(self.velocity.x) * 0.5  # Bounce with damping
        
        # Check top boundary
        if self.position.y - self.radius < y:
            self.position.y = y + self.radius
            self.velocity.y = abs(self.velocity.y) * 0.5  # Bounce with damping
        
        # Check bottom boundary
        if self.position.y + self.radius > y + height:
            self.position.y = y + height - self.radius
            self.velocity.y = -abs(self.velocity.y) * 0.5  # Bounce with damping


class Ripple:
    """Ripple wave entity."""
    
    def __init__(self, position: Vector2, amplitude: float = RIPPLE_MAX_AMPLITUDE,
                 propagation_speed: float = RIPPLE_PROPAGATION_SPEED,
                 lifetime: float = RIPPLE_LIFETIME):
        self.position = position.copy()
        self.creation_time = time.time()
        self.max_amplitude = amplitude
        self.propagation_speed = propagation_speed
        self.lifetime = lifetime
    
    def get_age(self) -> float:
        """Get the age of the ripple in seconds."""
        return time.time() - self.creation_time
    
    def is_expired(self) -> bool:
        """Check if the ripple has exceeded its lifetime."""
        return self.get_age() > self.lifetime
    
    def get_current_amplitude(self) -> float:
        """Calculate current amplitude with exponential decay: A(t) = A₀ × e^(-λt)."""
        age = self.get_age()
        return self.max_amplitude * math.exp(-RIPPLE_DECAY_RATE * age)
    
    def get_current_radius(self) -> float:
        """Calculate current radius based on propagation."""
        age = self.get_age()
        return self.propagation_speed * age
    
    def calculate_force_at(self, position: Vector2) -> Vector2:
        """
        Calculate the force exerted by this ripple at a given position.
        Force is radial (outward from ripple center) with distance-based falloff.
        """
        # Vector from ripple center to position
        direction = position - self.position
        distance = direction.magnitude()
        
        # Avoid division by zero at center
        if distance < 0.1:
            return Vector2(0, 0)
        
        # Normalize direction
        direction_normalized = direction.normalize()
        
        # Calculate force magnitude with distance falloff: 1 / (1 + distance²)
        amplitude = self.get_current_amplitude()
        distance_factor = 1.0 / (1.0 + distance * distance * 0.001)  # Scale factor for reasonable forces
        force_magnitude = amplitude * distance_factor
        
        # Return force vector
        return direction_normalized * force_magnitude


class WaveSimulator:
    """Manages wave simulation with multiple ripples."""
    
    def __init__(self):
        self.active_ripples: List[Ripple] = []
        self.obstacles = []  # List of obstacles that block wave propagation
        self.walls = []  # List of walls that reflect ripples
        self.current_zones = []  # List of current zones that affect ripple propagation
    
    def create_ripple(self, position: Vector2, amplitude: float = RIPPLE_MAX_AMPLITUDE):
        """Create a new ripple at the specified position."""
        ripple = Ripple(position, amplitude)
        self.active_ripples.append(ripple)
    
    def update(self, dt: float = 0.0):
        """Update wave simulation, removing expired ripples."""
        # Remove expired ripples
        self.active_ripples = [r for r in self.active_ripples if not r.is_expired()]
    
    def calculate_force_at(self, position: Vector2) -> Vector2:
        """Calculate combined force from all active ripples at a given position."""
        total_force = Vector2(0, 0)
        
        for ripple in self.active_ripples:
            # Check if ripple is blocked by any obstacle
            is_blocked = False
            for obstacle in self.obstacles:
                # Import here to avoid circular dependency
                from game.level import CollisionDetector
                if CollisionDetector.is_ripple_blocked_by_obstacle(ripple.position, position, obstacle):
                    is_blocked = True
                    break
            
            if not is_blocked:
                force = ripple.calculate_force_at(position)
                total_force = total_force + force
        
        return total_force
    
    def get_ripple_count(self) -> int:
        """Get the number of active ripples."""
        return len(self.active_ripples)
    
    def set_obstacles(self, obstacles):
        """Set obstacles that block wave propagation."""
        self.obstacles = obstacles
    
    def set_walls(self, walls):
        """Set walls that reflect ripples."""
        self.walls = walls
    
    def set_current_zones(self, current_zones):
        """Set current zones that affect ball and ripple propagation."""
        self.current_zones = current_zones
    
    def set_whirlpools(self, whirlpools):
        """Set whirlpools that affect ball physics."""
        # Whirlpools don't affect wave propagation, only ball physics
        # This method exists for API consistency
        pass
    
    def create_reflected_ripple(self, original_ripple: Ripple, wall):
        """
        Create a reflected ripple when a ripple hits a wall.
        The reflected ripple maintains amplitude and reflects at angle of incidence.
        
        Args:
            original_ripple: The ripple that hit the wall
            wall: The wall that caused the reflection
        """
        # Get closest point on wall (reflection point)
        reflection_point = wall.get_closest_point_on_wall(original_ripple.position)
        
        # Calculate incident direction (from ripple center to reflection point)
        to_wall = reflection_point - original_ripple.position
        distance = to_wall.magnitude()
        
        if distance < 0.1:
            return  # Too close to calculate direction
        
        incident = to_wall.normalize()
        
        # Get reflected direction using wall normal
        reflected_direction = wall.get_reflection_vector(incident)
        
        # Create new ripple on the reflected side
        # Position it at the reflection point, slightly offset in reflected direction
        reflected_position = reflection_point + reflected_direction * 15
        
        # Maintain amplitude through reflection (with slight loss for realism)
        current_amplitude = original_ripple.get_current_amplitude() * 0.9
        
        # Create reflected ripple with maintained amplitude
        reflected_ripple = Ripple(reflected_position, current_amplitude)
        # Adjust creation time to match original ripple's age (so it continues propagating)
        reflected_ripple.creation_time = original_ripple.creation_time
        
        self.active_ripples.append(reflected_ripple)


class BallPhysics:
    """Handles ball physics updates."""
    
    def __init__(self, ball: Ball, wave_simulator: WaveSimulator):
        self.ball = ball
        self.wave_simulator = wave_simulator
        self.walls = []  # List of walls for collision detection
        self.current_zones = []  # List of current zones for force application
        self.whirlpools = []  # List of whirlpools for force application
    
    def set_walls(self, walls):
        """Set walls for collision detection."""
        self.walls = walls
    
    def set_current_zones(self, current_zones):
        """Set current zones for force application."""
        self.current_zones = current_zones
    
    def set_whirlpools(self, whirlpools):
        """Set whirlpools for force application."""
        self.whirlpools = whirlpools if whirlpools else []
    
    def update(self, dt: float):
        """
        Update ball physics for one frame.
        Steps: calculate forces -> apply forces -> apply friction -> update position -> clamp velocity -> boundary collision -> wall collision
        """
        # Calculate net force from all active ripples
        net_force = self.wave_simulator.calculate_force_at(self.ball.position)
        
        # Add forces from current zones (if ball is inside any)
        for current_zone in self.current_zones:
            zone_force = current_zone.get_force_at(self.ball.position)
            net_force = net_force + zone_force
        
        # Apply force to update velocity
        self.ball.apply_force(net_force, dt)
        
        # Apply friction
        self.ball.apply_friction()
        
        # Update position
        self.ball.update_position(dt)
        
        # Clamp velocity to maximum speed
        self.ball.clamp_velocity()
        
        # Keep ball within pool boundaries
        self.ball.keep_in_bounds(WATER_POOL_RECT)
        
        # Check wall collisions and bounce
        from game.level import CollisionDetector
        for wall in self.walls:
            if CollisionDetector.check_ball_wall_collision(self.ball.position, self.ball.radius, wall):
                CollisionDetector.handle_ball_wall_bounce(self.ball, wall)
