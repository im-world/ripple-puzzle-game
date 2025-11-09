#!/usr/bin/env python3
"""
Ripple - A zen-themed wave physics puzzle game
Main entry point
"""

import sys
import math
from enum import Enum
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, WATER_POOL_RECT, INITIAL_STONES
from game.renderer import Renderer
from game.physics import Vector2, Ball, WaveSimulator, BallPhysics
from game.catapult import Catapult
from game.level import LevelManager, load_levels_with_fallback
from game.audio import AudioManager
from game.fish import spawn_fish
from game.particles import ParticleSystem
from game.transitions import FadeTransition, CameraShake, LevelCompleteAnimation, GameOverAnimation


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
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
        
        # Menu buttons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 50
        
        self.menu_buttons = {
            'start': Button(button_x, start_y, button_width, button_height, "Start Game"),
            'settings': Button(button_x, start_y + 70, button_width, button_height, "Settings"),
            'exit': Button(button_x, start_y + 140, button_width, button_height, "Exit")
        }
        
        # Level complete buttons
        self.level_complete_buttons = {
            'continue': Button(button_x, SCREEN_HEIGHT // 2 + 50, button_width, button_height, "Continue")
        }
        
        # Game over buttons
        self.game_over_buttons = {
            'retry': Button(button_x, SCREEN_HEIGHT // 2 + 30, button_width, button_height, "Retry Level"),
            'menu': Button(button_x, SCREEN_HEIGHT // 2 + 100, button_width, button_height, "Return to Menu")
        }
        
        # Settings UI elements
        slider_width = 300
        slider_x = SCREEN_WIDTH // 2 - slider_width // 2
        
        self.sound_volume_slider = Slider(slider_x, 200, slider_width, 40, 0.0, 1.0, 0.7, "Sound Effects Volume")
        self.music_volume_slider = Slider(slider_x, 280, slider_width, 40, 0.0, 1.0, 0.25, "Music Volume")
        
        # Mute toggle buttons
        toggle_button_width = 150
        toggle_button_x = SCREEN_WIDTH // 2 - toggle_button_width // 2
        
        self.settings_buttons = {
            'sound_mute': Button(toggle_button_x, 360, toggle_button_width, 40, "Mute Sounds", (150, 100, 100), (170, 120, 120)),
            'music_mute': Button(toggle_button_x, 410, toggle_button_width, 40, "Mute Music", (150, 100, 100), (170, 120, 120)),
            'back': Button(button_x, SCREEN_HEIGHT - 120, button_width, button_height, "Back to Menu")
        }
    
    def start_game(self):
        """Initialize game entities and start playing."""
        # Load levels
        levels = load_levels_with_fallback("levels/level_data.json")
        
        # Create game entities
        self.wave_simulator = WaveSimulator()
        # Position catapult at bottom of water pool
        # Players pull down/back to launch stones up/forward into the water
        water_bottom_y = WATER_POOL_RECT[1] + WATER_POOL_RECT[3] - 50  # 50px from bottom
        self.catapult = Catapult(Vector2(SCREEN_WIDTH // 2, water_bottom_y))
        self.level_manager = LevelManager(levels)
        
        # Initialize first level
        self.level_manager.initialize_level(Ball, 0)
        self.ball = self.level_manager.ball
        self.ball_physics = BallPhysics(self.ball, self.wave_simulator)
        
        # Get level data
        level_data = self.level_manager.get_current_level()
        
        # Set obstacles for wave simulator
        self.wave_simulator.set_obstacles(level_data.obstacles)
        
        # Reset stone counter to initial value (10 stones for level 1)
        self.level_manager.reset_stones_for_new_game()
        self.stones_in_flight = []
        
        # Clear particle system
        self.particle_system.clear()
        
        # Spawn fish (2-4 fish at random positions)
        import random
        fish_count = random.randint(2, 4)
        self.fish_list = spawn_fish(fish_count)
        
        # Start background music when game starts
        self.audio_manager.play_music(loops=-1)
        
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
            
            # Check Settings button
            elif self.menu_buttons['settings'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.state = GameState.SETTINGS
            
            # Check Exit button
            elif self.menu_buttons['exit'].is_clicked(mouse_pos):
                self.audio_manager.play_sound('click')
                self.running = False
    
    def handle_input_playing(self, event):
        """Handle input for playing state."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.catapult.start_aiming(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            stone = self.catapult.stop_aiming()
            if stone and self.level_manager.has_stones():
                # Play launch sound when stone is launched
                self.audio_manager.play_sound('launch')
                self.stones_in_flight.append(stone)
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
                        
                        # Update obstacles for wave simulator
                        level_data = self.level_manager.get_current_level()
                        self.wave_simulator.set_obstacles(level_data.obstacles)
                        
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
            # Check mute buttons
            if self.settings_buttons['sound_mute'].is_clicked(mouse_pos):
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
    
    def update_playing(self, dt):
        """Update playing state."""
        # Update fade transition
        self.fade_transition.update(dt)
        
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
                
                # Trigger subtle camera shake on impact
                self.camera_shake.start_shake(intensity=5.0, duration=0.2)
            
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
            
            # Update fish movement
            fish.update(dt)
        
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
            
            # Transition to level complete state after animation
            def transition_to_complete():
                self.state = GameState.LEVEL_COMPLETE
                self.fade_transition.start_fade_in(0.3)
            
            self.fade_transition.start_fade_out(0.5, transition_to_complete)
        
        # Check game over condition
        if not self.level_manager.has_stones() and len(self.stones_in_flight) == 0:
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
        self.renderer.render_stone_counter(self.level_manager.get_stones_remaining())
        self.renderer.render_power_meter(self.catapult)
        self.renderer.render_trajectory_preview(self.catapult)
        
        # Apply camera shake if active
        if self.camera_shake.is_shaking():
            self.screen = original_screen
            self.renderer.screen = original_screen
            self.camera_shake.apply_to_surface(self.screen, temp_surface)
        
        # Render fade transition
        self.fade_transition.render(self.screen)
    
    def render_level_complete(self):
        """Render level complete state."""
        # Clear screen with light background
        self.screen.fill((200, 220, 240))
        
        # Render success message with animation
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        title_surface = title_font.render("Level Complete!", True, (70, 180, 70))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        
        # Add subtle bounce animation
        import time
        bounce = abs(math.sin(time.time() * 3)) * 5
        title_rect.y -= int(bounce)
        
        self.screen.blit(title_surface, title_rect)
        
        # Display stone usage statistics
        stats_font = pygame.font.SysFont('Arial', 28)
        
        # Stones used this level
        stones_used_text = f"Stones Used: {self.level_manager.get_total_stones_used()}"
        stones_surface = stats_font.render(stones_used_text, True, (100, 100, 100))
        stones_rect = stones_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(stones_surface, stones_rect)
        
        # Stones remaining
        remaining_text = f"Stones Remaining: {self.level_manager.get_stones_remaining()}"
        remaining_surface = stats_font.render(remaining_text, True, (100, 100, 100))
        remaining_rect = remaining_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(remaining_surface, remaining_rect)
        
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
        
        # Render buttons
        button_font = pygame.font.SysFont('Arial', 20)
        for button in self.settings_buttons.values():
            button.draw(self.screen, button_font)
    
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
                elif self.state == GameState.SETTINGS:
                    self.handle_input_settings(event)
                elif self.state == GameState.PLAYING:
                    self.handle_input_playing(event)
                elif self.state == GameState.LEVEL_COMPLETE:
                    self.handle_input_level_complete(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_input_game_over(event)
            
            # Update based on current state
            if self.state == GameState.MENU:
                self.update_menu(dt)
            elif self.state == GameState.SETTINGS:
                self.update_settings(dt)
            elif self.state == GameState.PLAYING:
                self.update_playing(dt)
            elif self.state == GameState.LEVEL_COMPLETE:
                self.update_level_complete(dt)
            elif self.state == GameState.GAME_OVER:
                self.update_game_over(dt)
            
            # Render based on current state
            if self.state == GameState.MENU:
                self.render_menu()
            elif self.state == GameState.SETTINGS:
                self.render_settings()
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
