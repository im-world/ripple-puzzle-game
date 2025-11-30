#!/usr/bin/env python3
"""
Ripple - A zen-themed wave physics puzzle game
Main entry point
"""

import sys
import math
import random
from enum import Enum
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, WATER_POOL_RECT, INITIAL_STONES
from game.renderer import Renderer
from game.physics import Vector2, Ball, WaveSimulator, BallPhysics
from game.catapult import Catapult
from game.level import LevelManager, load_levels_with_fallback
from game.audio import AudioManager
from game.fish import spawn_fish
from game.fish_builder import load_global_fish_config
from game.particles import ParticleSystem
from game.transitions import FadeTransition, CameraShake, LevelCompleteAnimation, GameOverAnimation
from game.tutorial import TutorialManager
from game.level_builder import LevelBuilder
from game.fish_builder import FishBuilder


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    LEVEL_SELECT = "level_select"
    LEVEL_BUILDER = "level_builder"
    FISH_BUILDER = "fish_builder"
    SETTINGS = "settings"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"


class Button:
    """Simple button class for menu interactions."""
    
    def __init__(self, x, y, width, height, text, color=(100, 150, 200), hover_color=(120, 170, 220)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def update(self, mouse_pos):
        """Update button hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen, font):
        """Draw button on screen."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (70, 70, 70), self.rect, 2, border_radius=10)
        
        # Render text
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)


class EnvironmentRandomizerButton:
    """Environment randomizer button with hover pulse and click spin animation."""
    
    def __init__(self, x, y, size):
        """
        Initialize environment randomizer button.
        
        Args:
            x, y: Position (top-left corner)
            size: Size of the button
        """
        self.x = x
        self.y = y
        self.size = size
        self.is_hovered = False
        self.is_spinning = False
        self.spin_angle = 0.0
        self.spin_duration = 0.5  # 0.5 seconds for full spin
        self.spin_progress = 0.0
        
        # Create clickable rect
        self.rect = pygame.Rect(x, y, size, size)
    
    def update(self, mouse_pos, dt):
        """Update button hover state and animations."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update spin animation
        if self.is_spinning:
            self.spin_progress += dt / self.spin_duration
            if self.spin_progress >= 1.0:
                self.is_spinning = False
                self.spin_progress = 0.0
                self.spin_angle = 0.0
            else:
                # Smooth spin with easing
                eased_progress = self.spin_progress * self.spin_progress * (3 - 2 * self.spin_progress)
                self.spin_angle = eased_progress * 2 * math.pi
    
    def draw(self, screen, font):
        """Draw button with hover pulse and spin animation."""
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Hover pulse effect
        pulse_scale = 1.0
        if self.is_hovered and not self.is_spinning:
            import time
            pulse = abs(math.sin(time.time() * 4)) * 0.1
            pulse_scale = 1.0 + pulse
        
        # Calculate button radius with pulse
        button_radius = int((self.size // 2) * pulse_scale)
        
        # Draw button background with glow
        if self.is_hovered or self.is_spinning:
            # Draw glow effect
            glow_surface = pygame.Surface((self.size + 40, self.size + 40), pygame.SRCALPHA)
            glow_center = (self.size // 2 + 20, self.size // 2 + 20)
            
            for i in range(5, 0, -1):
                alpha = int(30 * (i / 5))
                glow_radius = button_radius + i * 4
                pygame.draw.circle(glow_surface, (100, 180, 220, alpha), glow_center, glow_radius)
            
            screen.blit(glow_surface, (self.x - 20, self.y - 20))
        
        # Draw button circle
        bg_color = (120, 170, 220) if self.is_hovered else (100, 150, 200)
        pygame.draw.circle(screen, bg_color, (center_x, center_y), button_radius)
        pygame.draw.circle(screen, (70, 120, 170), (center_x, center_y), button_radius, 2)
        
        # Draw dice/shuffle icon with rotation
        icon_size = self.size // 3
        
        # Create rotated surface for icon
        icon_surface = pygame.Surface((icon_size * 3, icon_size * 3), pygame.SRCALPHA)
        icon_center = (icon_size * 3 // 2, icon_size * 3 // 2)
        
        # Draw dice dots pattern (simplified)
        dot_radius = max(2, icon_size // 6)
        dot_color = (255, 255, 255)
        
        # Center dot
        pygame.draw.circle(icon_surface, dot_color, icon_center, dot_radius)
        
        # Corner dots (4 corners)
        offset = icon_size // 2
        for dx, dy in [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)]:
            pygame.draw.circle(icon_surface, dot_color, 
                             (icon_center[0] + dx, icon_center[1] + dy), dot_radius)
        
        # Rotate icon if spinning
        if self.is_spinning:
            icon_surface = pygame.transform.rotate(icon_surface, -math.degrees(self.spin_angle))
        
        # Blit icon to screen
        icon_rect = icon_surface.get_rect(center=(center_x, center_y))
        screen.blit(icon_surface, icon_rect.topleft)
    
    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)
    
    def start_spin(self):
        """Start spin animation."""
        self.is_spinning = True
        self.spin_progress = 0.0
        self.spin_angle = 0.0


class Checkbox:
    """Minimalist checkbox for HUD with soft glow when enabled."""
    
    def __init__(self, x, y, size, label, checked=False):
        """
        Initialize checkbox.
        
        Args:
            x, y: Position (top-left corner)
            size: Size of the checkbox square
            label: Text label to display next to checkbox
            checked: Initial checked state
        """
        self.x = x
        self.y = y
        self.size = size
        self.label = label
        self.checked = checked
        self.is_hovered = False
        
        # Create rect for the checkbox square
        self.checkbox_rect = pygame.Rect(x, y, size, size)
        
        # Calculate full clickable area (checkbox + label)
        font = pygame.font.SysFont('Arial', 18)
        label_surface = font.render(label, True, (70, 70, 70))
        label_width = label_surface.get_width()
        self.clickable_rect = pygame.Rect(x, y, size + 10 + label_width, size)
    
    def update(self, mouse_pos):
        """Update checkbox hover state."""
        self.is_hovered = self.clickable_rect.collidepoint(mouse_pos)
    
    def draw(self, screen, font):
        """Draw checkbox with minimalist style and soft glow when enabled."""
        # Draw checkbox background
        bg_color = (240, 245, 250) if not self.checked else (220, 240, 255)
        pygame.draw.rect(screen, bg_color, self.checkbox_rect, border_radius=4)
        
        # Draw soft glow when enabled
        if self.checked:
            glow_surface = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
            glow_center = (self.size // 2 + 10, self.size // 2 + 10)
            
            # Multiple layers for soft glow effect
            for i in range(5, 0, -1):
                alpha = int(20 * (i / 5))
                glow_radius = self.size // 2 + i * 3
                pygame.draw.circle(glow_surface, (100, 180, 220, alpha), glow_center, glow_radius)
            
            screen.blit(glow_surface, (self.x - 10, self.y - 10))
        
        # Draw checkbox border
        border_color = (100, 150, 200) if self.is_hovered else (150, 170, 190)
        if self.checked:
            border_color = (70, 140, 200)
        pygame.draw.rect(screen, border_color, self.checkbox_rect, 2, border_radius=4)
        
        # Draw checkmark if checked
        if self.checked:
            # Draw checkmark symbol
            check_color = (70, 140, 200)
            check_points = [
                (self.x + self.size * 0.2, self.y + self.size * 0.5),
                (self.x + self.size * 0.4, self.y + self.size * 0.7),
                (self.x + self.size * 0.8, self.y + self.size * 0.3)
            ]
            pygame.draw.lines(screen, check_color, False, check_points, 3)
        
        # Draw label
        label_color = (70, 70, 70)
        label_surface = font.render(self.label, True, label_color)
        label_x = self.x + self.size + 10
        label_y = self.y + (self.size - label_surface.get_height()) // 2
        screen.blit(label_surface, (label_x, label_y))
    
    def is_clicked(self, mouse_pos):
        """Check if checkbox is clicked."""
        return self.clickable_rect.collidepoint(mouse_pos)
    
    def toggle(self):
        """Toggle checkbox state."""
        self.checked = not self.checked
    
    def set_checked(self, checked):
        """Set checkbox state."""
        self.checked = checked
    
    def is_checked(self):
        """Get checkbox state."""
        return self.checked


class LevelCard:
    """Level card for level selection screen."""
    
    def __init__(self, x, y, width, height, level_number, is_tutorial=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.level_number = level_number
        self.is_tutorial = is_tutorial
        self.is_hovered = False
        self.is_selected = False
    
    def update(self, mouse_pos):
        """Update card hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen, font_large, font_small):
        """Draw level card on screen."""
        # Determine card color based on state
        if self.is_selected:
            bg_color = (120, 170, 220)
            border_color = (70, 120, 170)
        elif self.is_hovered:
            bg_color = (140, 190, 240)
            border_color = (90, 140, 190)
        else:
            bg_color = (160, 200, 240)
            border_color = (110, 150, 190)
        
        # Draw card background
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=8)
        
        # Draw level number
        level_text = f"{self.level_number}"
        level_surface = font_large.render(level_text, True, (255, 255, 255))
        level_rect = level_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
        screen.blit(level_surface, level_rect)
        
        # Draw tutorial badge if applicable
        if self.is_tutorial:
            badge_font = font_small
            badge_text = "Tutorial"
            badge_surface = badge_font.render(badge_text, True, (255, 215, 0))
            badge_rect = badge_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))
            
            # Draw badge background
            badge_bg = badge_rect.inflate(8, 4)
            pygame.draw.rect(screen, (70, 70, 70, 180), badge_bg, border_radius=3)
            
            screen.blit(badge_surface, badge_rect)
    
    def is_clicked(self, mouse_pos):
        """Check if card is clicked."""
        return self.rect.collidepoint(mouse_pos)


class Slider:
    """Slider control for volume adjustment."""
    
    def __init__(self, x, y, width, height, min_val=0.0, max_val=1.0, initial_val=0.5, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        
        # Slider components
        self.track_rect = pygame.Rect(x, y + height // 2 - 2, width, 4)
        self.handle_radius = 10
        self.handle_x = self._value_to_x(initial_val)
    
    def _value_to_x(self, value):
        """Convert value to x position."""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.x + int(ratio * self.width)
    
    def _x_to_value(self, x):
        """Convert x position to value."""
        ratio = (x - self.x) / self.width
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events for slider."""
        handle_rect = pygame.Rect(
            self.handle_x - self.handle_radius,
            self.y + self.height // 2 - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(mouse_pos) or self.track_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.handle_x = max(self.x, min(self.x + self.width, mouse_pos[0]))
                self.value = self._x_to_value(self.handle_x)
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_x = max(self.x, min(self.x + self.width, mouse_pos[0]))
                self.value = self._x_to_value(self.handle_x)
                return True
        
        return False
    
    def draw(self, screen, font):
        """Draw slider on screen."""
        # Draw label
        if self.label:
            label_surface = font.render(self.label, True, (70, 70, 70))
            screen.blit(label_surface, (self.x, self.y - 25))
        
        # Draw track
        pygame.draw.rect(screen, (150, 150, 150), self.track_rect, border_radius=2)
        
        # Draw filled portion
        filled_rect = pygame.Rect(self.x, self.y + self.height // 2 - 2, 
                                   self.handle_x - self.x, 4)
        pygame.draw.rect(screen, (100, 150, 200), filled_rect, border_radius=2)
        
        # Draw handle
        handle_color = (120, 170, 220) if self.dragging else (100, 150, 200)
        pygame.draw.circle(screen, handle_color, 
                          (self.handle_x, self.y + self.height // 2), 
                          self.handle_radius)
        pygame.draw.circle(screen, (70, 70, 70), 
                          (self.handle_x, self.y + self.height // 2), 
                          self.handle_radius, 2)
        
        # Draw value
        value_text = f"{int(self.value * 100)}%"
        value_surface = font.render(value_text, True, (70, 70, 70))
        screen.blit(value_surface, (self.x + self.width + 15, self.y + self.height // 2 - 10))
    
    def get_value(self):
        """Get current slider value."""
        return self.value
    
    def set_value(self, value):
        """Set slider value."""
        self.value = max(self.min_val, min(self.max_val, value))
        self.handle_x = self._value_to_x(self.value)


class Game:
    """Main game class with state machine."""
    
    def __init__(self):
        """Initialize game systems."""
        # Initialize Pygame
        pygame.init()
        
        # Create game window (1024x768)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ripple")
        
        # Create clock for frame rate control
        self.clock = pygame.time.Clock()
        
        # Initialize renderer
        self.renderer = Renderer(self.screen)
        
        # Initialize environment system
        from game.environment import EnvironmentSystem
        self.environment = EnvironmentSystem()
        self.renderer.environment = self.environment
        
        # Initialize audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.load_sound_effects("assets")
        self.audio_manager.load_music("assets/background.ogg")
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        
        # Game entities (initialized when starting game)
        self.ball = None
        self.wave_simulator = None
        self.ball_physics = None
        self.catapult = None
        self.level_manager = None
        
        # Stones in flight
        self.stones_in_flight = []
        
        # Fish entities
        self.fish_list = []
        
        # Particle system
        self.particle_system = ParticleSystem()
        
        # Transitions and effects
        self.fade_transition = FadeTransition(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_shake = CameraShake()
        self.level_complete_animation = LevelCompleteAnimation()
        self.game_over_animation = GameOverAnimation()
        
        # Tutorial system
        self.tutorial_manager = TutorialManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Star rating animation
        self.star_animation_progress = 0.0
        self.star_animation_duration = 1.5  # 1.5 seconds for stars to fill
        self.current_star_rating = 0
        self.zen_mode = False  # Zen mode flag
        self.hide_trajectory = False  # Hide trajectory flag
        
        # Zen Mode checkbox (positioned in top-right corner)
        checkbox_size = 20
        checkbox_x = SCREEN_WIDTH - 180
        checkbox_y = 20
        self.zen_mode_checkbox = Checkbox(checkbox_x, checkbox_y, checkbox_size, "Zen Mode", checked=False)
        
        # Hide Trajectory checkbox (positioned below Zen Mode checkbox)
        hide_trajectory_y = checkbox_y + 35  # 35px below Zen Mode checkbox
        self.hide_trajectory_checkbox = Checkbox(checkbox_x, hide_trajectory_y, checkbox_size, "Hide Trajectory", checked=False)
        
        # Environment Randomizer button (positioned in top-left corner)
        env_button_size = 50
        env_button_x = 20
        env_button_y = 20
        self.env_randomizer_button = EnvironmentRandomizerButton(env_button_x, env_button_y, env_button_size)
        
        # Menu buttons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 120
        
        self.menu_buttons = {
            'start': Button(button_x, start_y+120, button_width, button_height, "Start Game"),
            'level_select': Button(button_x, start_y + 180, button_width, button_height, "Level Select"),
            # 'level_builder': Button(button_x, start_y + 120, button_width, button_height, "Level Builder"),
            # 'fish_builder': Button(button_x, start_y + 180, button_width, button_height, "Fish Builder"),
            # 'settings': Button(button_x, start_y + 240, button_width, button_height, "Settings"),
            'exit': Button(button_x, start_y + 240, button_width, button_height, "Exit")
        }
        
        # # Level builder
        # self.level_builder = LevelBuilder(self.screen)
        
        # # Level builder back button
        # self.level_builder_back_button = Button(
        #     SCREEN_WIDTH // 2 - 100,
        #     SCREEN_HEIGHT - 60,
        #     200,
        #     50,
        #     "Back to Menu"
        # )
        
        # # Fish builder
        # self.fish_builder = FishBuilder(self.screen)
        # self.fish_builder.load_fish_config()  # Load saved configuration
        
        # # Fish builder back button
        # self.fish_builder_back_button = Button(
        #     SCREEN_WIDTH // 2 - 100,
        #     SCREEN_HEIGHT - 60,
        #     200,
        #     50,
        #     "Back to Menu"
        # )
        
        # Level selection UI
        self.level_cards = []
        self.selected_level_index = 0  # For keyboard navigation
        self._create_level_cards()
        
        # Level selection back button
        self.level_select_back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 80, 
            200, 
            50, 
            "Back to Menu"
        )
        
        # Level complete buttons
        self.level_complete_buttons = {
            'continue': Button(button_x, SCREEN_HEIGHT // 2 + 50, button_width, button_height, "Continue")
        }
        
        # Game over buttons
        self.game_over_buttons = {
            'retry': Button(button_x, SCREEN_HEIGHT // 2 + 30, button_width, button_height, "Retry Level"),
            'menu': Button(button_x, SCREEN_HEIGHT // 2 + 100, button_width, button_height, "Return to Menu")
        }
        
        # # Settings UI elements
        # slider_width = 300
        # slider_x = SCREEN_WIDTH // 2 - slider_width // 2
        
        # self.sound_volume_slider = Slider(slider_x, 200, slider_width, 40, 0.0, 1.0, 0.7, "Sound Effects Volume")
        # self.music_volume_slider = Slider(slider_x, 280, slider_width, 40, 0.0, 1.0, 0.25, "Music Volume")
        
        # # High-contrast mode checkbox
        # checkbox_size = 20
        # checkbox_x = SCREEN_WIDTH // 2 - 100
        # checkbox_y = 360
        # self.high_contrast_checkbox = Checkbox(checkbox_x, checkbox_y, checkbox_size, "High-Contrast Mode", checked=False)
        
        # # Mute toggle buttons
        # toggle_button_width = 150
        # toggle_button_x = SCREEN_WIDTH // 2 - toggle_button_width // 2
        
        # self.settings_buttons = {
        #     'sound_mute': Button(toggle_button_x, 420, toggle_button_width, 40, "Mute Sounds", (150, 100, 100), (170, 120, 120)),
        #     'music_mute': Button(toggle_button_x, 470, toggle_button_width, 40, "Mute Music", (150, 100, 100), (170, 120, 120)),
        #     'back': Button(button_x, SCREEN_HEIGHT - 120, button_width, button_height, "Back to Menu")
        # }
    
    def _create_level_cards(self):
        """Create level cards for level selection screen."""
        # Grid layout: 5 columns x 4 rows = 20 levels
        cols = 5
        rows = 4
        card_width = 140
        card_height = 100
        spacing_x = 20
        spacing_y = 20
        
        # Calculate starting position to center the grid
        total_width = cols * card_width + (cols - 1) * spacing_x
        total_height = rows * card_height + (rows - 1) * spacing_y
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 120  # Below title
        
        # Load levels to check tutorial status
        levels = load_levels_with_fallback("levels/level_data.json")
        
        # Create cards
        for i in range(20):
            row = i // cols
            col = i % cols
            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)
            
            # Check if this level is a tutorial level
            is_tutorial = i < len(levels) and levels[i].tutorial
            
            card = LevelCard(x, y, card_width, card_height, i + 1, is_tutorial)
            self.level_cards.append(card)
    
    def start_game(self, level_index=0):
        """Initialize game entities and start playing from specified level."""
        # Load levels
        levels = load_levels_with_fallback("levels/level_data.json")
        
        # Create game entities
        self.wave_simulator = WaveSimulator()
        # Position catapult at bottom of water pool
        # Players pull down/back to launch stones up/forward into the water
        water_bottom_y = WATER_POOL_RECT[1] + WATER_POOL_RECT[3] - 50  # 50px from bottom
        self.catapult = Catapult(Vector2(SCREEN_WIDTH // 2, water_bottom_y))
        self.level_manager = LevelManager(levels)
        
        # Initialize specified level (default to first level)
        # If starting from level select, treat as random level (give 10 stones)
        is_random_level = level_index > 0
        self.level_manager.initialize_level(Ball, level_index, is_random_level)
        self.ball = self.level_manager.ball
        self.ball_physics = BallPhysics(self.ball, self.wave_simulator)
        
        # Get level data
        level_data = self.level_manager.get_current_level()
        
        # Set obstacles for wave simulator
        self.wave_simulator.set_obstacles(level_data.obstacles)
        
        # Set walls for wave simulator and ball physics
        self.wave_simulator.set_walls(level_data.walls)
        self.ball_physics.set_walls(level_data.walls)
        
        # Set current zones for wave simulator and ball physics
        self.wave_simulator.set_current_zones(level_data.current_zones)
        self.ball_physics.set_current_zones(level_data.current_zones)
        
        # Set whirlpools for wave simulator and ball physics
        self.wave_simulator.set_whirlpools(level_data.whirlpools)
        self.ball_physics.set_whirlpools(level_data.whirlpools)
        
        # Reset stone counter if starting from level 1, otherwise keep current stones
        if level_index == 0:
            self.level_manager.reset_stones_for_new_game()
        self.stones_in_flight = []
        
        # Clear particle system
        self.particle_system.clear()
        
        # Spawn fish using global configuration
        fish_templates = load_global_fish_config()
        self.fish_list = spawn_fish(fish_templates=fish_templates)
        
        # Start background music when game starts
        self.audio_manager.play_music(loops=-1)
        
        # Start tutorial if this is a tutorial level (1-4)
        current_level_number = self.level_manager.get_current_level_number()
        if current_level_number >= 1 and current_level_number <= 4:
            self.tutorial_manager.start_tutorial(current_level_number, level_data)
        
        # Transition to playing state
        self.state = GameState.PLAYING
        
        # Start fade in transition (from black to clear)
        self.fade_transition.start_fade_in(0.5)
    
    def handle_input_menu(self, event):
        """Handle input for menu state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check Start Game button
            if self.menu_buttons['start'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                # Start fade out transition before starting game
                self.fade_transition.start_fade_out(0.3, self.start_game)
            
            # Check Level Select button
            elif self.menu_buttons['level_select'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.LEVEL_SELECT
                self.selected_level_index = 0  # Reset selection
            
            # Check Level Builder button
            elif self.menu_buttons['level_builder'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.LEVEL_BUILDER
            
            # Check Fish Builder button
            elif self.menu_buttons['fish_builder'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.FISH_BUILDER
            
            # Check Settings button
            elif self.menu_buttons['settings'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.SETTINGS
            
            # Check Exit button
            elif self.menu_buttons['exit'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.running = False
    
    def handle_input_level_select(self, event):
        """Handle input for level selection state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if back button clicked
            if self.level_select_back_button.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.MENU
                return
            
            # Check if any level card clicked
            for i, card in enumerate(self.level_cards):
                if card.is_clicked(mouse_pos):
                    self.audio_manager.play_sound('click')
                    # Start game from selected level
                    level_index = i
                    self.fade_transition.start_fade_out(0.3, lambda: self.start_game(level_index))
                    return
        
        elif event.type == pygame.KEYDOWN:
            # Keyboard navigation
            cols = 5
            rows = 4
            current_row = self.selected_level_index // cols
            current_col = self.selected_level_index % cols
            
            if event.key == pygame.K_LEFT:
                if current_col > 0:
                    self.selected_level_index -= 1
                    self.audio_manager.play_sound('click')
            elif event.key == pygame.K_RIGHT:
                if current_col < cols - 1 and self.selected_level_index < 19:
                    self.selected_level_index += 1
                    self.audio_manager.play_sound('click')
            elif event.key == pygame.K_UP:
                if current_row > 0:
                    self.selected_level_index -= cols
                    self.audio_manager.play_sound('click')
            elif event.key == pygame.K_DOWN:
                if current_row < rows - 1 and self.selected_level_index + cols < 20:
                    self.selected_level_index += cols
                    self.audio_manager.play_sound('click')
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Start selected level
                self.audio_manager.play_sound('click')
                level_index = self.selected_level_index
                self.fade_transition.start_fade_out(0.3, lambda: self.start_game(level_index))
    
    def handle_input_playing(self, event):
        """Handle input for playing state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if Environment Randomizer button was clicked
            if self.env_randomizer_button.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.environment.randomize()
                self.env_randomizer_button.start_spin()
                return
            
            # Check if Zen Mode checkbox was clicked
            if self.zen_mode_checkbox.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.zen_mode_checkbox.toggle()
                self.zen_mode = self.zen_mode_checkbox.is_checked()
                return
            
            # Check if Hide Trajectory checkbox was clicked
            if self.hide_trajectory_checkbox.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.hide_trajectory_checkbox.toggle()
                self.hide_trajectory = self.hide_trajectory_checkbox.is_checked()
                return
            
            # Check if tutorial UI handled the click
            if self.tutorial_manager.handle_click(mouse_pos):
                self.audio_manager.play_sound('click')
                return
            
            # Normal gameplay input
            self.catapult.start_aiming(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            stone = self.catapult.stop_aiming()
            if stone:
                # In Zen mode, don't check or deduct stones
                if self.zen_mode or self.level_manager.has_stones():
                    # Play launch sound when stone is launched
                    self.audio_manager.play_sound('launch')
                    self.stones_in_flight.append(stone)
                    # Only deduct stone if NOT in Zen mode
                    if not self.zen_mode:
                        self.level_manager.use_stone()
        elif event.type == pygame.MOUSEMOTION:
            if self.catapult.is_aiming:
                self.catapult.update_aim(pygame.mouse.get_pos())
    
    def handle_input_level_complete(self, event):
        """Handle input for level complete state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check Continue button
            if self.level_complete_buttons['continue'].is_clicked(mouse_pos):
                # Play click sound for UI interaction
                self.audio_manager.play_sound('click')
                
                # Try to transition to next level
                if self.level_manager.has_next_level():
                    # Define transition callback
                    def transition_to_next_level():
                        # Transition to next level (adds 10 stones automatically)
                        self.level_manager.transition_to_next_level(Ball)
                        self.ball = self.level_manager.ball
                        self.ball_physics = BallPhysics(self.ball, self.wave_simulator)
                        
                        # Update obstacles and walls for wave simulator
                        level_data = self.level_manager.get_current_level()
                        self.wave_simulator.set_obstacles(level_data.obstacles)
                        self.wave_simulator.set_walls(level_data.walls)
                        self.ball_physics.set_walls(level_data.walls)
                        self.wave_simulator.set_current_zones(level_data.current_zones)
                        self.ball_physics.set_current_zones(level_data.current_zones)
                        self.wave_simulator.set_whirlpools(level_data.whirlpools)
                        self.ball_physics.set_whirlpools(level_data.whirlpools)
                        
                        # Clear stones in flight
                        self.stones_in_flight = []
                        
                        # Return to playing state
                        self.state = GameState.PLAYING
                        
                        # Fade in
                        self.fade_transition.start_fade_in(0.3)
                    
                    # Fade out before transition
                    self.fade_transition.start_fade_out(0.3, transition_to_next_level)
                else:
                    # No more levels, return to menu with fade
                    def return_to_menu():
                        self.state = GameState.MENU
                        self.fade_transition.start_fade_in(0.3)
                    
                    self.fade_transition.start_fade_out(0.3, return_to_menu)
    
    def handle_input_settings(self, event):
        """Handle input for settings state."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle slider events
        if self.sound_volume_slider.handle_event(event, mouse_pos):
            # Update audio manager volume
            self.audio_manager.set_sound_volume(self.sound_volume_slider.get_value())
        
        if self.music_volume_slider.handle_event(event, mouse_pos):
            # Update audio manager volume
            self.audio_manager.set_music_volume(self.music_volume_slider.get_value())
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check high-contrast mode checkbox
            if self.high_contrast_checkbox.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.high_contrast_checkbox.toggle()
                # Update renderer high-contrast mode
                self.renderer.set_high_contrast_mode(self.high_contrast_checkbox.is_checked())
            
            # Check mute buttons
            elif self.settings_buttons['sound_mute'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.audio_manager.toggle_sound_mute()
                # Update button text
                if self.audio_manager.is_sound_muted():
                    self.settings_buttons['sound_mute'].text = "Unmute Sounds"
                else:
                    self.settings_buttons['sound_mute'].text = "Mute Sounds"
            
            elif self.settings_buttons['music_mute'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.audio_manager.toggle_music_mute()
                # Update button text
                if self.audio_manager.is_music_muted():
                    self.settings_buttons['music_mute'].text = "Unmute Music"
                else:
                    self.settings_buttons['music_mute'].text = "Mute Music"
            
            # Check back button
            elif self.settings_buttons['back'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.MENU
    
    def handle_input_level_builder(self, event):
        """Handle input for level builder state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if Environment Randomizer button was clicked
            if self.env_randomizer_button.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.environment.randomize()
                self.env_randomizer_button.start_spin()
                return
            
            # Check back button
            if self.level_builder_back_button.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.MENU
            else:
                # Pass to level builder
                self.level_builder.handle_mouse_down(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            self.level_builder.handle_mouse_up(mouse_pos)
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.level_builder.handle_mouse_motion(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            self.level_builder.handle_key_down(event)
    
    def handle_input_fish_builder(self, event):
        """Handle input for fish builder state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check back button
            if self.fish_builder_back_button.is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.MENU
            else:
                # Pass to fish builder
                self.fish_builder.handle_mouse_down(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            self.fish_builder.handle_mouse_up(mouse_pos)
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.fish_builder.handle_mouse_motion(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            self.fish_builder.handle_key_down(event)
    
    def handle_input_game_over(self, event):
        """Handle input for game over state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check Retry Level button
            if self.game_over_buttons['retry'].is_clicked(mouse_pos):
                # Play click sound for UI interaction
                self.audio_manager.play_sound('click')
                
                # Define retry callback
                def retry_level():
                    # Reset current level
                    self.level_manager.reset_current_level(Ball)
                    self.ball = self.level_manager.ball
                    self.ball_physics = BallPhysics(self.ball, self.wave_simulator)
                    
                    # Update walls, current zones, and whirlpools for ball physics
                    level_data = self.level_manager.get_current_level()
                    self.ball_physics.set_walls(level_data.walls)
                    self.ball_physics.set_current_zones(level_data.current_zones)
                    self.ball_physics.set_whirlpools(level_data.whirlpools)
                    
                    # Reset stones to 10 for retry (not carrying over from previous level)
                    self.level_manager.reset_stones_for_new_game()
                    self.stones_in_flight = []
                    
                    # Clear ripples
                    self.wave_simulator.active_ripples = []
                    
                    # Return to playing state
                    self.state = GameState.PLAYING
                    
                    # Fade in
                    self.fade_transition.start_fade_in(0.3)
                
                # Fade out before retry
                self.fade_transition.start_fade_out(0.3, retry_level)
            
            # Check Return to Menu button
            elif self.game_over_buttons['menu'].is_clicked(mouse_pos):
                # Play click sound for UI interaction
                self.audio_manager.play_sound('click')
                
                # Define menu callback
                def return_to_menu():
                    self.state = GameState.MENU
                    self.fade_transition.start_fade_in(0.3)
                
                # Fade out before returning to menu
                self.fade_transition.start_fade_out(0.3, return_to_menu)
    
    def update_menu(self, dt):
        """Update menu state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons.values():
            button.update(mouse_pos)
    
    def update_level_select(self, dt):
        """Update level selection state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
        # Update card hover states
        mouse_pos = pygame.mouse.get_pos()
        for i, card in enumerate(self.level_cards):
            card.update(mouse_pos)
            card.is_selected = (i == self.selected_level_index)
        
        # Update back button
        self.level_select_back_button.update(mouse_pos)
    
    def update_playing(self, dt):
        """Update playing state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
        # Update tutorial
        mouse_pos = pygame.mouse.get_pos()
        self.tutorial_manager.update(dt, mouse_pos)
        
        # Update environment system
        self.environment.update(dt)
        
        # Update Environment Randomizer button
        self.env_randomizer_button.update(mouse_pos, dt)
        
        # Update Zen Mode checkbox hover state
        self.zen_mode_checkbox.update(mouse_pos)
        
        # Update Hide Trajectory checkbox hover state
        self.hide_trajectory_checkbox.update(mouse_pos)
        
        # Update wave simulator
        self.wave_simulator.update(dt)
        
        # Update stones in flight
        for stone in self.stones_in_flight[:]:
            # Track if stone just landed this frame
            was_in_flight = stone.in_flight
            
            # Update stone
            still_active = stone.update(dt)
            
            # Check if stone just landed (wire stone impact to ripple creation)
            if was_in_flight and stone.has_landed():
                # Play splash sound when stone impacts water
                self.audio_manager.play_sound('splash')
                
                # Create ripple at landing position
                self.wave_simulator.create_ripple(stone.position)
                
                # Play ripple sound when ripple is created
                self.audio_manager.play_sound('ripple')
                
                # Create splash particle effect
                self.particle_system.create_splash_effect(stone.position)
                
                # Trigger screen shake on impact (2-4 pixels, 0.1-0.15s duration, damped oscillation)
                shake_intensity = random.uniform(2.0, 4.0)
                shake_duration = random.uniform(0.1, 0.15)
                self.camera_shake.start_shake(intensity=shake_intensity, duration=shake_duration)
            
            # Remove stone if it's done sinking
            if not still_active:
                self.stones_in_flight.remove(stone)
        
        # Update fish and check for ripple reactions
        for fish in self.fish_list:
            # Check if any ripple is near this fish
            for ripple in self.wave_simulator.active_ripples:
                # Calculate distance from fish to ripple center
                distance = (fish.position - ripple.position).magnitude()
                
                # Threshold distance for reaction (within ripple radius + buffer)
                reaction_threshold = ripple.get_current_radius() + 50
                
                # If ripple is near fish and fish is not already reacting
                if distance < reaction_threshold and not fish.is_reacting:
                    # Get ripple amplitude for scaling reaction
                    ripple_force = ripple.get_current_amplitude()
                    
                    # Make fish react to ripple
                    fish.react_to_ripple(ripple.position, ripple_force)
                    break  # Only react to one ripple at a time
            
            # Update fish movement (pass other fish for schooling behavior)
            fish.update(dt, self.fish_list)
        
        # Update ball physics (wire ripple forces to ball physics updates)
        self.ball_physics.update(dt)
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update camera shake
        self.camera_shake.update(dt)
        
        # Update level complete animation if active
        if self.level_complete_animation.is_animating():
            self.level_complete_animation.update(dt)
        
        # Check level completion (wire ball position to collision detection)
        level_data = self.level_manager.get_current_level()
        distance = (self.ball.position - level_data.target_position).magnitude()
        
        # Wire collision detection to level completion
        if distance < level_data.target_radius and not self.level_complete_animation.is_animating():
            # Play level complete sound when level is completed
            self.audio_manager.play_sound('level_complete')
            
            # Create sparkle effect at target position
            self.particle_system.create_sparkle_effect(level_data.target_position)
            
            # Start level complete animation
            self.level_complete_animation.start()
            
            # Calculate star rating for this level
            self.current_star_rating = self.level_manager.calculate_star_rating(
                self.level_manager.stones_used_this_level
            )
            
            # Reset star animation
            self.star_animation_progress = 0.0
            
            # Transition to level complete state after animation
            def transition_to_complete():
                self.state = GameState.LEVEL_COMPLETE
                self.fade_transition.start_fade_in(0.3)
            
            self.fade_transition.start_fade_out(0.5, transition_to_complete)
        
        # Check whirlpool stuck condition (lose condition)
        for whirlpool in level_data.whirlpools:
            if whirlpool.is_ball_stuck(self.ball.position) and not self.game_over_animation.is_animating():
                # Ball is stuck in whirlpool - game over
                self.game_over_animation.start()
                
                # Transition to game over state after animation
                def transition_to_game_over():
                    self.state = GameState.GAME_OVER
                    self.fade_transition.start_fade_in(0.3)
                
                self.fade_transition.start_fade_out(0.5, transition_to_game_over)
                break
        
        # Check game over condition (out of stones) - but not in Zen mode
        if not self.zen_mode and not self.level_manager.has_stones() and len(self.stones_in_flight) == 0:
            # Check if ball is at target
            if distance >= level_data.target_radius and not self.game_over_animation.is_animating():
                # Start game over animation
                self.game_over_animation.start()
                
                # Transition to game over state after animation
                def transition_to_game_over():
                    self.state = GameState.GAME_OVER
                    self.fade_transition.start_fade_in(0.3)
                
                self.fade_transition.start_fade_out(0.5, transition_to_game_over)
    
    def update_level_complete(self, dt):
        """Update level complete state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
        # Update star animation
        if self.star_animation_progress < 1.0:
            self.star_animation_progress += dt / self.star_animation_duration
            self.star_animation_progress = min(1.0, self.star_animation_progress)
        
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.level_complete_buttons.values():
            button.update(mouse_pos)
    
    def update_settings(self, dt):
        """Update settings state."""
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.settings_buttons.values():
            button.update(mouse_pos)
        
        # Update checkbox hover state
        self.high_contrast_checkbox.update(mouse_pos)
    
    def update_level_builder(self, dt):
        """Update level builder state."""
        # Update environment system
        self.environment.update(dt)
        
        # Update back button hover state
        mouse_pos = pygame.mouse.get_pos()
        self.level_builder_back_button.update(mouse_pos)
        
        # Update Environment Randomizer button
        self.env_randomizer_button.update(mouse_pos, dt)
    
    def update_fish_builder(self, dt):
        """Update fish builder state."""
        # Update back button hover state
        mouse_pos = pygame.mouse.get_pos()
        self.fish_builder_back_button.update(mouse_pos)
    
    def update_game_over(self, dt):
        """Update game over state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
        # Update game over animation
        if self.game_over_animation.is_animating():
            self.game_over_animation.update(dt)
        
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons.values():
            button.update(mouse_pos)
    
    def render_menu(self):
        """Render menu state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render title "Ripple"
        title_font = pygame.font.SysFont('Arial', 72, bold=True)
        title_surface = title_font.render("Ripple", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)
        
        # Render subtitle
        subtitle_font = pygame.font.SysFont('Arial', 24)
        subtitle_surface = subtitle_font.render("A Zen Wave Physics Puzzle", True, (100, 100, 100))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Render menu buttons
        button_font = pygame.font.SysFont('Arial', 28)
        for button in self.menu_buttons.values():
            button.draw(self.screen, button_font)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def render_level_select(self):
        """Render level selection state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render title
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        title_surface = title_font.render("Select Level", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title_surface, title_rect)
        
        # Render level cards
        card_font_large = pygame.font.SysFont('Arial', 36, bold=True)
        card_font_small = pygame.font.SysFont('Arial', 14)
        for card in self.level_cards:
            card.draw(self.screen, card_font_large, card_font_small)
        
        # Render back button
        button_font = pygame.font.SysFont('Arial', 28)
        self.level_select_back_button.draw(self.screen, button_font)
        
        # Render keyboard navigation hint
        hint_font = pygame.font.SysFont('Arial', 18)
        hint_text = "Use Arrow Keys + Enter to navigate, or click a level"
        hint_surface = hint_font.render(hint_text, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
        self.screen.blit(hint_surface, hint_rect)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def render_playing(self):
        """Render playing state."""
        # If camera shake is active, render to temporary surface
        if self.camera_shake.is_shaking():
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            original_screen = self.screen
            self.screen = temp_surface
            self.renderer.screen = temp_surface
        
        # Render frame
        self.renderer.render_frame()
        
        # Get current level data
        level_data = self.level_manager.get_current_level()
        
        # Render entities (in order)
        self.renderer.render_starting_spot(level_data.ball_start)
        self.renderer.render_target_spot(level_data.target_position, level_data.target_radius)
        
        # Render obstacles
        for obstacle in level_data.obstacles:
            self.renderer.render_obstacle(obstacle)
        
        # Render current zones (with animated arrows)
        import time
        for current_zone in level_data.current_zones:
            self.renderer.render_current_zone(current_zone, time.time())
        
        # Render walls
        for wall in level_data.walls:
            self.renderer.render_wall(wall)
        
        # Render whirlpools (before ripples so ripples appear on top)
        import time
        for whirlpool in level_data.whirlpools:
            self.renderer.render_whirlpool(whirlpool, time.time())
        
        # Render ripples (with obstacle clipping)
        self.renderer.render_ripples(self.wave_simulator.active_ripples, level_data.obstacles)
        
        # Render fish (in correct layer order - after ripples, before ball)
        self.renderer.render_fish_list(self.fish_list)
        
        # Render ball with time offset for animation
        import time
        self.renderer.render_ball(self.ball, time.time())
        
        # Render stones in flight
        for stone in self.stones_in_flight:
            self.renderer.render_stone(stone)
        
        # Render particles (after stones, before catapult)
        self.particle_system.render(self.screen)
        
        # Render catapult
        self.renderer.render_catapult(self.catapult)
        
        # Render UI
        # Pass zen_mode flag to stone counter renderer
        self.renderer.render_stone_counter(self.level_manager.get_stones_remaining(), self.zen_mode)
        self.renderer.render_power_meter(self.catapult)
        # Only render trajectory preview if not hidden
        if not self.hide_trajectory:
            self.renderer.render_trajectory_preview(self.catapult)
        
        # Render Zen Mode checkbox
        checkbox_font = pygame.font.SysFont('Arial', 18)
        self.zen_mode_checkbox.draw(self.screen, checkbox_font)
        
        # Render Hide Trajectory checkbox
        self.hide_trajectory_checkbox.draw(self.screen, checkbox_font)
        
        # Render Environment Randomizer button
        button_font = pygame.font.SysFont('Arial', 18)
        self.env_randomizer_button.draw(self.screen, button_font)
        
        # Apply camera shake if active
        if self.camera_shake.is_shaking():
            self.screen = original_screen
            self.renderer.screen = original_screen
            self.camera_shake.apply_to_surface(self.screen, temp_surface)
        
        # Render weather effects (on top of everything except UI)
        self.environment.render_weather(self.screen)
        
        # Render tutorial UI (on top of everything)
        self.tutorial_manager.render(self.screen)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def render_level_complete(self):
        """Render level complete state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render success message with animation
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        title_surface = title_font.render("Level Complete!", True, (70, 180, 70))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # Add subtle bounce animation
        import time
        bounce = abs(math.sin(time.time() * 3)) * 5
        title_rect.y -= int(bounce)
        
        self.screen.blit(title_surface, title_rect)
        
        # Render star rating or "Peace" for Zen mode
        star_y_position = 220
        
        if self.zen_mode:
            # Display "Peace" rating in Zen mode
            self.renderer.render_peace_rating(SCREEN_WIDTH // 2, star_y_position)
        else:
            # Display star rating with animation
            self.renderer.render_star_rating(
                SCREEN_WIDTH // 2, 
                star_y_position, 
                self.current_star_rating,
                self.star_animation_progress
            )
        
        # Display stone usage statistics
        stats_font = pygame.font.SysFont('Arial', 24)
        
        # Stones used this level
        stones_used_text = f"Stones Used This Level: {self.level_manager.stones_used_this_level}"
        stones_surface = stats_font.render(stones_used_text, True, (100, 100, 100))
        stones_rect = stones_surface.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(stones_surface, stones_rect)
        
        # Stones remaining
        remaining_text = f"Stones Remaining: {self.level_manager.get_stones_remaining()}"
        remaining_surface = stats_font.render(remaining_text, True, (100, 100, 100))
        remaining_rect = remaining_surface.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(remaining_surface, remaining_rect)
        
        # Total stones used across all levels
        total_text = f"Total Stones Used: {self.level_manager.get_total_stones_used()}"
        total_surface = stats_font.render(total_text, True, (100, 100, 100))
        total_rect = total_surface.get_rect(center=(SCREEN_WIDTH // 2, 420))
        self.screen.blit(total_surface, total_rect)
        
        # Render buttons
        button_font = pygame.font.SysFont('Arial', 28)
        for button in self.level_complete_buttons.values():
            button.draw(self.screen, button_font)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def render_settings(self):
        """Render settings state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render title
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        title_surface = title_font.render("Settings", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Render sliders
        slider_font = pygame.font.SysFont('Arial', 20)
        self.sound_volume_slider.draw(self.screen, slider_font)
        self.music_volume_slider.draw(self.screen, slider_font)
        
        # Render high-contrast mode checkbox
        checkbox_font = pygame.font.SysFont('Arial', 18)
        self.high_contrast_checkbox.draw(self.screen, checkbox_font)
        
        # Render buttons
        button_font = pygame.font.SysFont('Arial', 20)
        for button in self.settings_buttons.values():
            button.draw(self.screen, button_font)
    
    def render_level_builder(self):
        """Render level builder state."""
        # Draw level builder interface
        self.level_builder.draw()
        
        # Render Environment Randomizer button
        button_font = pygame.font.SysFont('Arial', 18)
        self.env_randomizer_button.draw(self.screen, button_font)
        
        # Render weather effects
        self.environment.render_weather(self.screen)
        
        # Draw back button
        button_font_large = pygame.font.SysFont('Arial', 28)
        self.level_builder_back_button.draw(self.screen, button_font_large)
        
        # Draw grid toggle hint
        hint_font = pygame.font.SysFont('Arial', 16)
        hint_text = "Press G to toggle grid | Delete/Backspace to remove selected obstacle"
        hint_surface = hint_font.render(hint_text, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(hint_surface, hint_rect)
    
    def render_fish_builder(self):
        """Render fish builder state."""
        # Draw fish builder interface
        self.fish_builder.draw()
        
        # Draw back button
        button_font = pygame.font.SysFont('Arial', 28)
        self.fish_builder_back_button.draw(self.screen, button_font)
        
        # Draw keyboard shortcuts hint
        hint_font = pygame.font.SysFont('Arial', 16)
        hint_text = "Ctrl+Z: Undo | Ctrl+Y: Redo | Click color swatches to change color"
        hint_surface = hint_font.render(hint_text, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(hint_surface, hint_rect)
    
    def render_game_over(self):
        """Render game over state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render game over message with fade animation
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        
        # Apply alpha if animation is active
        alpha = self.game_over_animation.get_alpha() if self.game_over_animation.is_animating() else 255
        
        # Create surface with alpha for title
        title_text = "Out of Stones!"
        title_surface = title_font.render(title_text, True, (180, 70, 70))
        
        if alpha < 255:
            # Apply alpha blending
            temp_surface = pygame.Surface(title_surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((255, 255, 255, 0))
            temp_surface.blit(title_surface, (0, 0))
            temp_surface.set_alpha(alpha)
            title_surface = temp_surface
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)
        
        # Display message
        message_font = pygame.font.SysFont('Arial', 28)
        message_text = "You ran out of stones before reaching the target."
        message_surface = message_font.render(message_text, True, (100, 100, 100))
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(message_surface, message_rect)
        
        # Render buttons
        button_font = pygame.font.SysFont('Arial', 28)
        for button in self.game_over_buttons.values():
            button.draw(self.screen, button_font)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def run(self):
        """Main game loop with fixed timestep."""
        while self.running:
            # Calculate delta time for physics updates (in seconds)
            dt = self.clock.get_time() / 1000.0
            
            # Handle Pygame events (quit, mouse, keyboard)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                
                # Route input handling based on current state
                if self.state == GameState.MENU:
                    self.handle_input_menu(event)
                elif self.state == GameState.LEVEL_SELECT:
                    self.handle_input_level_select(event)
                # elif self.state == GameState.LEVEL_BUILDER:
                #     self.handle_input_level_builder(event)
                # elif self.state == GameState.FISH_BUILDER:
                #     self.handle_input_fish_builder(event)
                # elif self.state == GameState.SETTINGS:
                #     self.handle_input_settings(event)
                elif self.state == GameState.PLAYING:
                    self.handle_input_playing(event)
                elif self.state == GameState.LEVEL_COMPLETE:
                    self.handle_input_level_complete(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_input_game_over(event)
            
            # Update based on current state
            if self.state == GameState.MENU:
                self.update_menu(dt)
            elif self.state == GameState.LEVEL_SELECT:
                self.update_level_select(dt)
            # elif self.state == GameState.LEVEL_BUILDER:
            #     self.update_level_builder(dt)
            # elif self.state == GameState.FISH_BUILDER:
            #     self.update_fish_builder(dt)
            # elif self.state == GameState.SETTINGS:
            #     self.update_settings(dt)
            elif self.state == GameState.PLAYING:
                self.update_playing(dt)
            elif self.state == GameState.LEVEL_COMPLETE:
                self.update_level_complete(dt)
            elif self.state == GameState.GAME_OVER:
                self.update_game_over(dt)
            
            # Render based on current state
            if self.state == GameState.MENU:
                self.render_menu()
            elif self.state == GameState.LEVEL_SELECT:
                self.render_level_select()
            # elif self.state == GameState.LEVEL_BUILDER:
            #     self.render_level_builder()
            # elif self.state == GameState.FISH_BUILDER:
            #     self.render_fish_builder()
            # elif self.state == GameState.SETTINGS:
            #     self.render_settings()
            elif self.state == GameState.PLAYING:
                self.render_playing()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.render_level_complete()
            elif self.state == GameState.GAME_OVER:
                self.render_game_over()
            
            # Update display
            pygame.display.flip()
            
            # Maintain target frame rate (60 FPS)
            self.clock.tick(TARGET_FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()


def main():
    """Initialize and run the game"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
