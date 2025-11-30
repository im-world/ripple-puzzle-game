"""
Environment system for Ripple game.
Handles randomization of background themes, weather effects, and time of day.
"""

import random
import pygame
import math
from typing import List, Tuple
from game.config import ENVIRONMENT_THEMES, WEATHER_EFFECTS, TIME_OF_DAY, SCREEN_WIDTH, SCREEN_HEIGHT


class WeatherParticle:
    """Particle for weather effects."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, particle_type: str):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.particle_type = particle_type
        self.lifetime = 0.0
        self.max_lifetime = random.uniform(3.0, 6.0)
        
        # Type-specific properties
        if particle_type == 'leaves':
            self.size = random.randint(3, 6)
            self.color = random.choice([
                (139, 69, 19),   # Brown
                (205, 133, 63),  # Peru
                (255, 140, 0),   # Dark orange
                (218, 165, 32)   # Goldenrod
            ])
            self.rotation = random.uniform(0, 2 * math.pi)
            self.rotation_speed = random.uniform(-2, 2)
        elif particle_type == 'snow':
            self.size = random.randint(2, 5)
            self.color = (255, 255, 255)
            self.drift = random.uniform(-0.5, 0.5)
        elif particle_type == 'rain':
            self.size = random.randint(8, 15)
            self.color = (150, 180, 220)
            self.width = 1
        elif particle_type == 'fireflies':
            self.size = random.randint(2, 4)
            self.color = (255, 255, 150)
            self.glow_phase = random.uniform(0, 2 * math.pi)
            self.glow_speed = random.uniform(2, 4)
    
    def update(self, dt: float):
        """Update particle position and lifetime."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime += dt
        
        # Type-specific updates
        if self.particle_type == 'leaves':
            self.rotation += self.rotation_speed * dt
            # Leaves drift side to side
            self.x += math.sin(self.lifetime * 2) * 10 * dt
        elif self.particle_type == 'snow':
            # Snow drifts gently
            self.x += self.drift * dt * 20
        elif self.particle_type == 'fireflies':
            # Fireflies move in wavy patterns
            self.x += math.sin(self.lifetime * 3) * 15 * dt
            self.y += math.cos(self.lifetime * 2) * 10 * dt
            self.glow_phase += self.glow_speed * dt
        
        # Check if particle is out of bounds or expired
        return (0 <= self.x <= SCREEN_WIDTH and 
                -50 <= self.y <= SCREEN_HEIGHT + 50 and 
                self.lifetime < self.max_lifetime)
    
    def render(self, screen: pygame.Surface):
        """Render the particle."""
        if self.particle_type == 'leaves':
            # Draw leaf as small rotated rectangle
            points = [
                (self.x + self.size * math.cos(self.rotation), 
                 self.y + self.size * math.sin(self.rotation)),
                (self.x + self.size * math.cos(self.rotation + 2.5), 
                 self.y + self.size * math.sin(self.rotation + 2.5)),
                (self.x + self.size * math.cos(self.rotation + math.pi), 
                 self.y + self.size * math.sin(self.rotation + math.pi)),
                (self.x + self.size * math.cos(self.rotation - 2.5), 
                 self.y + self.size * math.sin(self.rotation - 2.5))
            ]
            pygame.draw.polygon(screen, self.color, points)
        elif self.particle_type == 'snow':
            # Draw snowflake as circle
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        elif self.particle_type == 'rain':
            # Draw rain as line
            pygame.draw.line(screen, self.color, 
                           (int(self.x), int(self.y)), 
                           (int(self.x), int(self.y + self.size)), 
                           self.width)
        elif self.particle_type == 'fireflies':
            # Draw firefly with glow effect
            glow_intensity = abs(math.sin(self.glow_phase))
            alpha = int(150 + 105 * glow_intensity)
            
            # Create glow surface
            glow_size = self.size * 4
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Draw glow layers
            for i in range(3, 0, -1):
                glow_alpha = int(alpha * (i / 3) * 0.5)
                pygame.draw.circle(glow_surface, (*self.color, glow_alpha), 
                                 (glow_size, glow_size), i * self.size)
            
            screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))
            
            # Draw core
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class EnvironmentSystem:
    """Manages environment visuals including themes, weather, and time of day."""
    
    def __init__(self):
        """Initialize environment system with default settings."""
        self.current_theme = 'forest_green'
        self.current_weather = 'none'
        self.current_time = 'day'
        
        self.weather_particles: List[WeatherParticle] = []
        self.particle_spawn_timer = 0.0
        self.particle_spawn_rate = 0.1  # Spawn every 0.1 seconds
        
        # Transition system for smooth color fading
        self.transition_active = False
        self.transition_timer = 0.0
        self.transition_duration = 0.3  # 0.3 seconds fade
        self.old_water_light = None
        self.old_water_dark = None
        self.old_background_color = None
        self.target_water_light = None
        self.target_water_dark = None
        self.target_background_color = None
        
        # Get initial theme colors
        self._update_theme_colors()
    
    def _update_theme_colors(self):
        """Update current theme colors."""
        theme = ENVIRONMENT_THEMES[self.current_theme]
        self.water_light = theme['water_light']
        self.water_dark = theme['water_dark']
        self.background_color = theme['background']
    
    def randomize(self, use_fade: bool = False):
        """
        Randomize all environment components.
        
        Args:
            use_fade: If True, use 0.3s fade transition. If False, instant change.
        """
        # Store old colors for transition
        if use_fade:
            self.old_water_light = self.water_light
            self.old_water_dark = self.water_dark
            self.old_background_color = self.background_color
        
        # Randomize theme
        self.current_theme = random.choice(list(ENVIRONMENT_THEMES.keys()))
        
        # Randomize weather
        self.current_weather = random.choice(WEATHER_EFFECTS)
        
        # Randomize time of day
        self.current_time = random.choice(TIME_OF_DAY)
        
        # Update colors
        self._update_theme_colors()
        
        # Apply time of day tint
        self._apply_time_tint()
        
        # Set up transition if fade is enabled
        if use_fade:
            self.target_water_light = self.water_light
            self.target_water_dark = self.water_dark
            self.target_background_color = self.background_color
            self.water_light = self.old_water_light
            self.water_dark = self.old_water_dark
            self.background_color = self.old_background_color
            self.transition_active = True
            self.transition_timer = 0.0
        
        # Clear existing weather particles
        self.weather_particles.clear()
    
    def _apply_time_tint(self):
        """Apply color tint based on time of day."""
        if self.current_time == 'dusk':
            # Orange/purple tint for dusk
            self.water_light = tuple(min(255, int(c * 1.1 + 30)) if i == 0 else int(c * 0.9) 
                                    for i, c in enumerate(self.water_light))
            self.water_dark = tuple(min(255, int(c * 1.1 + 20)) if i == 0 else int(c * 0.85) 
                                   for i, c in enumerate(self.water_dark))
            self.background_color = tuple(min(255, int(c * 1.05 + 20)) if i == 0 else int(c * 0.9) 
                                         for i, c in enumerate(self.background_color))
        elif self.current_time == 'night':
            # Dark blue tint for night
            self.water_light = tuple(int(c * 0.5) for c in self.water_light)
            self.water_dark = tuple(int(c * 0.4) for c in self.water_dark)
            self.background_color = tuple(int(c * 0.4) for c in self.background_color)
    
    def update(self, dt: float):
        """Update weather particles and color transitions."""
        # Update color transition
        if self.transition_active:
            self.transition_timer += dt
            progress = min(1.0, self.transition_timer / self.transition_duration)
            
            # Smooth interpolation (ease-in-out)
            smooth_progress = progress * progress * (3 - 2 * progress)
            
            # Interpolate colors
            self.water_light = self._lerp_color(self.old_water_light, self.target_water_light, smooth_progress)
            self.water_dark = self._lerp_color(self.old_water_dark, self.target_water_dark, smooth_progress)
            self.background_color = self._lerp_color(self.old_background_color, self.target_background_color, smooth_progress)
            
            # End transition when complete
            if progress >= 1.0:
                self.transition_active = False
        
        # Update weather particles
        if self.current_weather == 'none':
            return
        
        # Update existing particles
        self.weather_particles = [p for p in self.weather_particles if p.update(dt)]
        
        # Spawn new particles
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= self.particle_spawn_rate:
            self.particle_spawn_timer = 0.0
            self._spawn_weather_particle()
    
    def _spawn_weather_particle(self):
        """Spawn a new weather particle."""
        if self.current_weather == 'none':
            return
        
        # Spawn position (top of screen, random x)
        x = random.uniform(0, SCREEN_WIDTH)
        y = -20
        
        # Velocity based on weather type
        if self.current_weather == 'leaves':
            vx = random.uniform(-10, 10)
            vy = random.uniform(30, 60)
        elif self.current_weather == 'snow':
            vx = random.uniform(-5, 5)
            vy = random.uniform(20, 40)
        elif self.current_weather == 'rain':
            vx = random.uniform(-5, 5)
            vy = random.uniform(300, 500)
        elif self.current_weather == 'fireflies':
            # Fireflies spawn anywhere and move slowly
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            vx = random.uniform(-20, 20)
            vy = random.uniform(-20, 20)
        else:
            return
        
        particle = WeatherParticle(x, y, vx, vy, self.current_weather)
        self.weather_particles.append(particle)
    
    def render_weather(self, screen: pygame.Surface):
        """Render weather particles."""
        for particle in self.weather_particles:
            particle.render(screen)
    
    def get_background_color(self) -> Tuple[int, int, int]:
        """Get current background color."""
        return self.background_color
    
    def get_water_colors(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Get current water colors (light, dark)."""
        return self.water_light, self.water_dark
    
    def _lerp_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """
        Linear interpolation between two colors.
        
        Args:
            color1: Starting color (r, g, b)
            color2: Ending color (r, g, b)
            t: Interpolation factor (0.0 to 1.0)
        
        Returns:
            Interpolated color (r, g, b)
        """
        return (
            int(color1[0] * (1 - t) + color2[0] * t),
            int(color1[1] * (1 - t) + color2[1] * t),
            int(color1[2] * (1 - t) + color2[2] * t)
        )
