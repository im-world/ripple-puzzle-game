"""
Particle system for visual effects.
Handles splash particles and sparkle effects.
"""

import pygame
import math
import random
from typing import List
from game.physics import Vector2


class Particle:
    """Base particle class with lifetime and physics."""
    
    def __init__(self, position: Vector2, velocity: Vector2, lifetime: float, 
                 color: tuple, size: float):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.initial_size = size
        self.size = size
        self.alpha = 1.0
        self.gravity = Vector2(0, 300)  # Downward gravity for splash particles
    
    def update(self, dt: float) -> bool:
        """
        Update particle physics and lifetime.
        Returns True if particle is still alive, False if expired.
        """
        self.age += dt
        
        # Check if expired
        if self.age >= self.lifetime:
            return False
        
        # Update velocity with gravity
        self.velocity = self.velocity + self.gravity * dt
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Update alpha (fade out over lifetime)
        life_ratio = self.age / self.lifetime
        self.alpha = 1.0 - life_ratio
        
        # Update size (shrink over lifetime)
        self.size = self.initial_size * (1.0 - life_ratio * 0.5)
        
        return True
    
    def render(self, screen: pygame.Surface):
        """Render particle on screen."""
        if self.size < 1:
            return
        
        # Create surface with alpha
        size_int = int(self.size * 2 + 2)
        temp_surface = pygame.Surface((size_int, size_int), pygame.SRCALPHA)
        
        # Draw particle with alpha
        color_with_alpha = (*self.color[:3], int(255 * self.alpha))
        center = (size_int // 2, size_int // 2)
        pygame.draw.circle(temp_surface, color_with_alpha, center, int(self.size))
        
        # Blit to screen
        screen.blit(temp_surface, (int(self.position.x - size_int // 2), 
                                   int(self.position.y - size_int // 2)))


class SparkleParticle(Particle):
    """Sparkle particle for level completion effect."""
    
    def __init__(self, position: Vector2, velocity: Vector2, lifetime: float, 
                 color: tuple, size: float):
        super().__init__(position, velocity, lifetime, color, size)
        self.gravity = Vector2(0, -50)  # Slight upward drift
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)
    
    def update(self, dt: float) -> bool:
        """Update sparkle particle with rotation."""
        result = super().update(dt)
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Pulsing effect
        life_ratio = self.age / self.lifetime
        pulse = math.sin(life_ratio * math.pi * 4) * 0.3 + 0.7
        self.size = self.initial_size * pulse * (1.0 - life_ratio * 0.3)
        
        return result
    
    def render(self, screen: pygame.Surface):
        """Render sparkle as a star shape."""
        if self.size < 1:
            return
        
        # Create surface with alpha
        size_int = int(self.size * 3 + 2)
        temp_surface = pygame.Surface((size_int, size_int), pygame.SRCALPHA)
        
        # Draw star shape
        color_with_alpha = (*self.color[:3], int(255 * self.alpha))
        center = (size_int // 2, size_int // 2)
        
        # Draw cross pattern for sparkle
        arm_length = int(self.size)
        pygame.draw.line(temp_surface, color_with_alpha, 
                        (center[0] - arm_length, center[1]), 
                        (center[0] + arm_length, center[1]), 2)
        pygame.draw.line(temp_surface, color_with_alpha, 
                        (center[0], center[1] - arm_length), 
                        (center[0], center[1] + arm_length), 2)
        
        # Draw diagonal lines
        diag_offset = int(arm_length * 0.7)
        pygame.draw.line(temp_surface, color_with_alpha, 
                        (center[0] - diag_offset, center[1] - diag_offset), 
                        (center[0] + diag_offset, center[1] + diag_offset), 2)
        pygame.draw.line(temp_surface, color_with_alpha, 
                        (center[0] - diag_offset, center[1] + diag_offset), 
                        (center[0] + diag_offset, center[1] - diag_offset), 2)
        
        # Blit to screen
        screen.blit(temp_surface, (int(self.position.x - size_int // 2), 
                                   int(self.position.y - size_int // 2)))


class ParticleSystem:
    """Manages particle effects."""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def create_splash_effect(self, position: Vector2):
        """
        Create splash particle effect for stone water impact.
        Spawns multiple particles in a circular pattern.
        """
        num_particles = random.randint(15, 25)
        
        for i in range(num_particles):
            # Random angle for circular spread
            angle = random.uniform(0, 2 * math.pi)
            
            # Random speed
            speed = random.uniform(50, 150)
            
            # Calculate velocity
            velocity = Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed - random.uniform(50, 150)  # Upward bias
            )
            
            # Random lifetime
            lifetime = random.uniform(0.5, 1.2)
            
            # Water droplet colors (light blue shades)
            colors = [
                (173, 216, 230),  # Light blue
                (135, 206, 235),  # Sky blue
                (176, 224, 230),  # Powder blue
                (200, 230, 255)   # Very light blue
            ]
            color = random.choice(colors)
            
            # Random size
            size = random.uniform(2, 5)
            
            # Create particle
            particle = Particle(position, velocity, lifetime, color, size)
            self.particles.append(particle)
    
    def create_sparkle_effect(self, position: Vector2):
        """
        Create sparkle effect for level completion.
        Spawns sparkle particles around the target.
        """
        num_particles = random.randint(20, 30)
        
        for i in range(num_particles):
            # Random offset from center
            offset_x = random.uniform(-40, 40)
            offset_y = random.uniform(-40, 40)
            particle_pos = Vector2(position.x + offset_x, position.y + offset_y)
            
            # Random velocity (gentle drift)
            velocity = Vector2(
                random.uniform(-30, 30),
                random.uniform(-50, -20)  # Upward drift
            )
            
            # Random lifetime
            lifetime = random.uniform(1.0, 2.0)
            
            # Sparkle colors (gold, yellow, white)
            colors = [
                (255, 215, 0),    # Gold
                (255, 255, 100),  # Yellow
                (255, 255, 255),  # White
                (255, 240, 150)   # Light gold
            ]
            color = random.choice(colors)
            
            # Random size
            size = random.uniform(3, 7)
            
            # Create sparkle particle
            particle = SparkleParticle(particle_pos, velocity, lifetime, color, size)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles and remove expired ones."""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self, screen: pygame.Surface):
        """Render all active particles."""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """Get the number of active particles."""
        return len(self.particles)
