"""
Fish module for Ripple game.
Handles fish entities with swimming patterns and ripple reactions.
"""

import math
import random
import time
from game.physics import Vector2
from game.config import WATER_POOL_RECT


class Fish:
    """Fish entity with swimming behavior."""
    
    def __init__(self, position: Vector2, size: float = 15.0):
        """
        Initialize fish with position and swimming properties.
        
        Args:
            position: Initial position of the fish
            size: Size of the fish (length)
        """
        self.position = position.copy()
        self.size = size
        self.velocity = Vector2(0, 0)
        
        # Swimming pattern parameters
        self.base_speed = random.uniform(30, 60)  # pixels per second
        self.direction = random.uniform(0, 2 * math.pi)  # radians
        self.swim_time = 0.0  # Time counter for sine wave pattern
        self.sine_amplitude = random.uniform(10, 20)  # Amplitude of sine wave
        self.sine_frequency = random.uniform(1.5, 3.0)  # Frequency of sine wave
        
        # Direction change timing
        self.last_direction_change = time.time()
        self.direction_change_interval = random.uniform(3.0, 6.0)  # seconds
        
        # Flip state (for sprite rendering)
        self.facing_right = True
        
        # Reaction state
        self.is_reacting = False
        self.reaction_time = 0.0
        self.reaction_duration = 1.0  # seconds
    
    def update(self, dt: float):
        """
        Update fish position and behavior.
        
        Args:
            dt: Delta time in seconds
        """
        # Update swim time for sine wave pattern
        self.swim_time += dt
        
        # Check if it's time to change direction
        current_time = time.time()
        if current_time - self.last_direction_change > self.direction_change_interval:
            self._change_direction()
            self.last_direction_change = current_time
            self.direction_change_interval = random.uniform(3.0, 6.0)
        
        # Update reaction timer
        if self.is_reacting:
            self.reaction_time += dt
            if self.reaction_time >= self.reaction_duration:
                self.is_reacting = False
                self.reaction_time = 0.0
        
        # Calculate velocity using sine wave pattern for natural movement
        # Base direction vector
        base_direction = Vector2(math.cos(self.direction), math.sin(self.direction))
        
        # Perpendicular direction for sine wave
        perpendicular = Vector2(-math.sin(self.direction), math.cos(self.direction))
        
        # Sine wave offset
        sine_offset = math.sin(self.swim_time * self.sine_frequency) * self.sine_amplitude
        
        # Combine base movement with sine wave
        target_velocity = base_direction * self.base_speed + perpendicular * sine_offset
        
        # Smooth velocity transition (unless reacting to ripple)
        if not self.is_reacting:
            self.velocity = target_velocity
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Keep fish within pool boundaries
        self._keep_in_bounds()
        
        # Update facing direction based on velocity
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False
    
    def _change_direction(self):
        """Randomly change swimming direction."""
        # Change direction by a random angle
        angle_change = random.uniform(-math.pi / 2, math.pi / 2)
        self.direction += angle_change
        
        # Normalize direction to [0, 2π]
        self.direction = self.direction % (2 * math.pi)
    
    def _keep_in_bounds(self):
        """Keep fish within water pool boundaries."""
        x, y, width, height = WATER_POOL_RECT
        
        # Add padding to keep fish away from edges
        padding = self.size * 2
        
        # Check boundaries and bounce if needed
        if self.position.x < x + padding:
            self.position.x = x + padding
            self.direction = random.uniform(-math.pi / 4, math.pi / 4)  # Turn right
        elif self.position.x > x + width - padding:
            self.position.x = x + width - padding
            self.direction = random.uniform(math.pi * 3 / 4, math.pi * 5 / 4)  # Turn left
        
        if self.position.y < y + padding:
            self.position.y = y + padding
            self.direction = random.uniform(math.pi / 4, math.pi * 3 / 4)  # Turn down
        elif self.position.y > y + height - padding:
            self.position.y = y + height - padding
            self.direction = random.uniform(-math.pi * 3 / 4, -math.pi / 4)  # Turn up
    
    def react_to_ripple(self, ripple_position: Vector2, ripple_force: float):
        """
        React to nearby ripple by moving away.
        
        Args:
            ripple_position: Position of the ripple center
            ripple_force: Strength of the ripple (for scaling reaction)
        """
        # Calculate direction away from ripple
        away_direction = self.position - ripple_position
        distance = away_direction.magnitude()
        
        if distance < 0.1:
            # Too close, pick random direction
            away_direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        
        away_direction = away_direction.normalize()
        
        # Set velocity to move away (subtle movement)
        reaction_speed = self.base_speed * 2.0  # Move faster when reacting
        self.velocity = away_direction * reaction_speed
        
        # Update direction to match new velocity
        self.direction = math.atan2(away_direction.y, away_direction.x)
        
        # Mark as reacting
        self.is_reacting = True
        self.reaction_time = 0.0


def spawn_fish(count: int = 3) -> list:
    """
    Spawn multiple fish at random positions in the pool.
    
    Args:
        count: Number of fish to spawn (default 3, range 2-4)
    
    Returns:
        List of Fish objects
    """
    fish_list = []
    x, y, width, height = WATER_POOL_RECT
    
    # Ensure count is in valid range
    count = max(2, min(4, count))
    
    for _ in range(count):
        # Random position within pool (with padding)
        padding = 50
        pos_x = random.uniform(x + padding, x + width - padding)
        pos_y = random.uniform(y + padding, y + height - padding)
        
        # Random size variation
        size = random.uniform(12, 18)
        
        fish = Fish(Vector2(pos_x, pos_y), size)
        fish_list.append(fish)
    
    return fish_list
