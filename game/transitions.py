"""
Transitions and screen effects module.
Handles fade in/out transitions and camera shake effects.
"""

import pygame
import math
import random
from typing import Optional


class FadeTransition:
    """Handles fade in/out transitions between game states."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fade_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        self.is_active = False
        self.fade_type = "in"  # "in" or "out"
        self.duration = 0.5  # seconds
        self.elapsed = 0.0
        self.callback = None
    
    def start_fade_out(self, duration: float = 0.5, callback=None):
        """
        Start a fade out transition (screen goes to black).
        
        Args:
            duration: Duration of fade in seconds
            callback: Optional callback to execute when fade completes
        """
        self.is_active = True
        self.fade_type = "out"
        self.duration = duration
        self.elapsed = 0.0
        self.callback = callback
    
    def start_fade_in(self, duration: float = 0.5, callback=None):
        """
        Start a fade in transition (screen comes from black).
        
        Args:
            duration: Duration of fade in seconds
            callback: Optional callback to execute when fade completes
        """
        self.is_active = True
        self.fade_type = "in"
        self.duration = duration
        self.elapsed = 0.0
        self.callback = callback
    
    def update(self, dt: float):
        """Update transition state."""
        if not self.is_active:
            return
        
        self.elapsed += dt
        
        # Check if transition is complete
        if self.elapsed >= self.duration:
            self.is_active = False
            if self.callback:
                self.callback()
    
    def render(self, screen: pygame.Surface):
        """Render fade overlay."""
        if not self.is_active:
            return
        
        # Calculate alpha based on progress
        progress = min(1.0, self.elapsed / self.duration)
        
        if self.fade_type == "out":
            # Fade to black
            alpha = int(255 * progress)
        else:
            # Fade from black
            alpha = int(255 * (1.0 - progress))
        
        # Clear and fill fade surface
        self.fade_surface.fill((0, 0, 0, alpha))
        
        # Blit to screen
        screen.blit(self.fade_surface, (0, 0))
    
    def is_fading(self) -> bool:
        """Check if a fade transition is currently active."""
        return self.is_active
    
    def get_progress(self) -> float:
        """Get current progress of transition (0.0 to 1.0)."""
        if not self.is_active:
            return 1.0
        return min(1.0, self.elapsed / self.duration)


class CameraShake:
    """Handles camera shake effect for impacts."""
    
    def __init__(self):
        self.is_active = False
        self.intensity = 0.0
        self.duration = 0.0
        self.elapsed = 0.0
        self.offset_x = 0
        self.offset_y = 0
    
    def start_shake(self, intensity: float = 10.0, duration: float = 0.3):
        """
        Start camera shake effect.
        
        Args:
            intensity: Maximum shake offset in pixels
            duration: Duration of shake in seconds
        """
        self.is_active = True
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0.0
    
    def update(self, dt: float):
        """Update shake effect."""
        if not self.is_active:
            self.offset_x = 0
            self.offset_y = 0
            return
        
        self.elapsed += dt
        
        # Check if shake is complete
        if self.elapsed >= self.duration:
            self.is_active = False
            self.offset_x = 0
            self.offset_y = 0
            return
        
        # Calculate shake intensity with decay
        progress = self.elapsed / self.duration
        current_intensity = self.intensity * (1.0 - progress)
        
        # Generate random offset
        self.offset_x = random.uniform(-current_intensity, current_intensity)
        self.offset_y = random.uniform(-current_intensity, current_intensity)
    
    def get_offset(self) -> tuple:
        """Get current camera offset as (x, y) tuple."""
        return (int(self.offset_x), int(self.offset_y))
    
    def is_shaking(self) -> bool:
        """Check if shake is currently active."""
        return self.is_active
    
    def apply_to_surface(self, screen: pygame.Surface, content_surface: pygame.Surface):
        """
        Apply shake offset by blitting content with offset.
        
        Args:
            screen: Target screen surface
            content_surface: Surface to blit with shake offset
        """
        offset = self.get_offset()
        screen.blit(content_surface, offset)


class LevelCompleteAnimation:
    """Handles level completion animation sequence."""
    
    def __init__(self):
        self.is_active = False
        self.duration = 2.0  # Total animation duration
        self.elapsed = 0.0
        self.phase = 0  # Animation phase
    
    def start(self):
        """Start level complete animation."""
        self.is_active = True
        self.elapsed = 0.0
        self.phase = 0
    
    def update(self, dt: float):
        """Update animation state."""
        if not self.is_active:
            return
        
        self.elapsed += dt
        
        # Update phase based on elapsed time
        if self.elapsed < 0.5:
            self.phase = 0  # Initial pause
        elif self.elapsed < 1.0:
            self.phase = 1  # Zoom/scale effect
        elif self.elapsed < 1.5:
            self.phase = 2  # Sparkle burst
        else:
            self.phase = 3  # Fade to completion screen
        
        # Check if animation is complete
        if self.elapsed >= self.duration:
            self.is_active = False
    
    def get_scale_factor(self) -> float:
        """Get current scale factor for zoom effect."""
        if self.phase == 1:
            # Zoom in slightly
            phase_progress = (self.elapsed - 0.5) / 0.5
            return 1.0 + math.sin(phase_progress * math.pi) * 0.1
        return 1.0
    
    def should_show_sparkles(self) -> bool:
        """Check if sparkles should be shown."""
        return self.phase >= 2
    
    def is_animating(self) -> bool:
        """Check if animation is active."""
        return self.is_active


class GameOverAnimation:
    """Handles game over animation sequence."""
    
    def __init__(self):
        self.is_active = False
        self.duration = 1.5
        self.elapsed = 0.0
    
    def start(self):
        """Start game over animation."""
        self.is_active = True
        self.elapsed = 0.0
    
    def update(self, dt: float):
        """Update animation state."""
        if not self.is_active:
            return
        
        self.elapsed += dt
        
        # Check if animation is complete
        if self.elapsed >= self.duration:
            self.is_active = False
    
    def get_alpha(self) -> int:
        """Get current alpha for fade effect."""
        if not self.is_active:
            return 255
        
        progress = min(1.0, self.elapsed / self.duration)
        return int(255 * progress)
    
    def is_animating(self) -> bool:
        """Check if animation is active."""
        return self.is_active
