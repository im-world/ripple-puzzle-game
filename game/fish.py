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
    
    def __init__(self, position: Vector2, size: float = 15.0, speed: float = 50.0, 
                 behavior_pattern: str = "Random", reaction_intensity: float = 1.0):
        """
        Initialize fish with position and swimming properties.
        
        Args:
            position: Initial position of the fish
            size: Size of the fish (length)
            speed: Base swimming speed in pixels per second
            behavior_pattern: Swimming behavior ("Schooling", "Solo", "Circular Patrol", "Random")
            reaction_intensity: Multiplier for ripple reactions
        """
        self.position = position.copy()
        self.size = size
        self.velocity = Vector2(0, 0)
        self.behavior_pattern = behavior_pattern
        self.reaction_intensity = reaction_intensity
        
        # Swimming pattern parameters
        self.base_speed = speed
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
        
        # Behavior-specific parameters
        if behavior_pattern == "Circular Patrol":
            # Set up circular patrol
            x, y, width, height = WATER_POOL_RECT
            self.patrol_center = Vector2(x + width / 2, y + height / 2)
            self.patrol_radius = min(width, height) / 3
            self.patrol_angle = random.uniform(0, 2 * math.pi)
            self.patrol_speed = speed / self.patrol_radius  # Angular speed
        elif behavior_pattern == "Schooling":
            # Schooling fish will follow nearby fish (simplified)
            self.school_radius = 100  # Distance to consider other fish
        elif behavior_pattern == "Solo":
            # Solo fish move more deliberately, less random
            self.direction_change_interval = random.uniform(5.0, 10.0)
    
    def update(self, dt: float, other_fish: list = None):
        """
        Update fish position and behavior.
        
        Args:
            dt: Delta time in seconds
            other_fish: List of other fish (for schooling behavior)
        """
        # Update swim time for sine wave pattern
        self.swim_time += dt
        
        # Update reaction timer
        if self.is_reacting:
            self.reaction_time += dt
            if self.reaction_time >= self.reaction_duration:
                self.is_reacting = False
                self.reaction_time = 0.0
        
        # Behavior-specific movement
        if self.behavior_pattern == "Circular Patrol":
            self._update_circular_patrol(dt)
        elif self.behavior_pattern == "Schooling" and other_fish:
            self._update_schooling(dt, other_fish)
        elif self.behavior_pattern == "Solo":
            self._update_solo(dt)
        else:  # Random
            self._update_random(dt)
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Keep fish within pool boundaries
        self._keep_in_bounds()
        
        # Update facing direction based on velocity
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False
    
    def _update_circular_patrol(self, dt: float):
        """Update circular patrol behavior."""
        if not self.is_reacting:
            # Move in a circle around patrol center
            self.patrol_angle += self.patrol_speed * dt
            
            # Calculate position on circle
            target_x = self.patrol_center.x + self.patrol_radius * math.cos(self.patrol_angle)
            target_y = self.patrol_center.y + self.patrol_radius * math.sin(self.patrol_angle)
            
            # Calculate velocity to move along circle
            tangent_direction = Vector2(-math.sin(self.patrol_angle), math.cos(self.patrol_angle))
            self.velocity = tangent_direction * self.base_speed
    
    def _update_schooling(self, dt: float, other_fish: list):
        """Update schooling behavior - follow nearby fish."""
        if not self.is_reacting:
            # Find nearby fish
            nearby_fish = []
            for fish in other_fish:
                if fish != self:
                    distance = (fish.position - self.position).magnitude()
                    if distance < self.school_radius:
                        nearby_fish.append(fish)
            
            if nearby_fish:
                # Calculate average direction of nearby fish
                avg_direction = Vector2(0, 0)
                for fish in nearby_fish:
                    avg_direction = avg_direction + Vector2(math.cos(fish.direction), math.sin(fish.direction))
                
                avg_direction = avg_direction.normalize()
                
                # Blend with current direction
                current_dir = Vector2(math.cos(self.direction), math.sin(self.direction))
                blended = (current_dir * 0.7 + avg_direction * 0.3).normalize()
                self.direction = math.atan2(blended.y, blended.x)
            
            # Move in current direction with sine wave
            base_direction = Vector2(math.cos(self.direction), math.sin(self.direction))
            perpendicular = Vector2(-math.sin(self.direction), math.cos(self.direction))
            sine_offset = math.sin(self.swim_time * self.sine_frequency) * self.sine_amplitude
            self.velocity = base_direction * self.base_speed + perpendicular * sine_offset
    
    def _update_solo(self, dt: float):
        """Update solo behavior - deliberate, less random movement."""
        if not self.is_reacting:
            # Check if it's time to change direction (less frequent)
            current_time = time.time()
            if current_time - self.last_direction_change > self.direction_change_interval:
                self._change_direction()
                self.last_direction_change = current_time
                self.direction_change_interval = random.uniform(5.0, 10.0)
            
            # Move in straight line mostly (less sine wave)
            base_direction = Vector2(math.cos(self.direction), math.sin(self.direction))
            perpendicular = Vector2(-math.sin(self.direction), math.cos(self.direction))
            sine_offset = math.sin(self.swim_time * self.sine_frequency) * (self.sine_amplitude * 0.3)
            self.velocity = base_direction * self.base_speed + perpendicular * sine_offset
    
    def _update_random(self, dt: float):
        """Update random behavior - original behavior."""
        if not self.is_reacting:
            # Check if it's time to change direction
            current_time = time.time()
            if current_time - self.last_direction_change > self.direction_change_interval:
                self._change_direction()
                self.last_direction_change = current_time
                self.direction_change_interval = random.uniform(3.0, 6.0)
            
            # Calculate velocity using sine wave pattern for natural movement
            base_direction = Vector2(math.cos(self.direction), math.sin(self.direction))
            perpendicular = Vector2(-math.sin(self.direction), math.cos(self.direction))
            sine_offset = math.sin(self.swim_time * self.sine_frequency) * self.sine_amplitude
            self.velocity = base_direction * self.base_speed + perpendicular * sine_offset
    
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
        
        # Set velocity to move away (scaled by reaction intensity)
        reaction_speed = self.base_speed * 2.0 * self.reaction_intensity
        self.velocity = away_direction * reaction_speed
        
        # Update direction to match new velocity
        self.direction = math.atan2(away_direction.y, away_direction.x)
        
        # Mark as reacting
        self.is_reacting = True
        self.reaction_time = 0.0


def spawn_fish(count: int = 3, fish_templates: list = None) -> list:
    """
    Spawn multiple fish at random positions in the pool.
    Uses global fish configuration if available.
    
    Args:
        count: Number of fish to spawn (default 3, range 2-4) - used if no templates provided
        fish_templates: List of FishTemplate objects from fish builder
    
    Returns:
        List of Fish objects
    """
    fish_list = []
    x, y, width, height = WATER_POOL_RECT
    
    if fish_templates:
        # Use configured templates
        for template in fish_templates:
            if not template.enabled:
                continue
            
            # Spawn random number of fish based on min/max count
            spawn_count = random.randint(template.min_count, template.max_count)
            
            for _ in range(spawn_count):
                # Random position within pool (with padding)
                padding = 50
                pos_x = random.uniform(x + padding, x + width - padding)
                pos_y = random.uniform(y + padding, y + height - padding)
                
                fish = Fish(
                    Vector2(pos_x, pos_y),
                    size=template.size,
                    speed=template.speed,
                    behavior_pattern=template.behavior_pattern,
                    reaction_intensity=template.reaction_intensity
                )
                fish_list.append(fish)
    else:
        # Fallback to default behavior
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
