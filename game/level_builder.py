"""
Level Builder module for Ripple game.
Provides a visual interface for creating and editing levels.
"""

import pygame
import math
import json
import copy
from typing import Optional, List, Tuple, Dict, Any
from game.physics import Vector2
from game.level import LevelData, Obstacle, Wall, CurrentZone, Whirlpool
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WATER_POOL_RECT


class ObstacleType:
    """Enumeration of obstacle types available in the level builder."""
    ANTI_RIPPLE = "anti_ripple_zone"
    WALL = "wall"
    CURRENT_ZONE = "current_zone"
    WHIRLPOOL = "whirlpool"


class BuilderObstacle:
    """Wrapper for obstacles in the level builder with selection and editing state."""
    
    def __init__(self, obstacle_type: str, position: Vector2, **kwargs):
        self.type = obstacle_type
        self.position = position.copy()
        self.is_selected = False
        
        # Type-specific properties
        if obstacle_type == ObstacleType.ANTI_RIPPLE:
            self.size = kwargs.get('size', [100, 100])  # [width, height]
        elif obstacle_type == ObstacleType.WALL:
            self.length = kwargs.get('length', 150)
            self.rotation = kwargs.get('rotation', 0.0)  # radians
            self.thickness = 10
        elif obstacle_type == ObstacleType.CURRENT_ZONE:
            self.size = kwargs.get('size', [150, 100])  # [width, height]
            self.strength = kwargs.get('strength', 150)
            self.direction = kwargs.get('direction', Vector2(1, 0))
        elif obstacle_type == ObstacleType.WHIRLPOOL:
            self.radius = kwargs.get('radius', 60)
            self.pull_strength = kwargs.get('pull_strength', 120)
    
    def get_bounds_rect(self) -> pygame.Rect:
        """Get bounding rectangle for this obstacle."""
        if self.type == ObstacleType.ANTI_RIPPLE:
            width, height = self.size
            return pygame.Rect(
                int(self.position.x - width / 2),
                int(self.position.y - height / 2),
                int(width),
                int(height)
            )
        elif self.type == ObstacleType.WALL:
            # Approximate wall as rectangle
            half_length = self.length / 2
            return pygame.Rect(
                int(self.position.x - half_length),
                int(self.position.y - self.thickness / 2),
                int(self.length),
                int(self.thickness)
            )
        elif self.type == ObstacleType.CURRENT_ZONE:
            width, height = self.size
            return pygame.Rect(
                int(self.position.x - width / 2),
                int(self.position.y - height / 2),
                int(width),
                int(height)
            )
        elif self.type == ObstacleType.WHIRLPOOL:
            return pygame.Rect(
                int(self.position.x - self.radius),
                int(self.position.y - self.radius),
                int(self.radius * 2),
                int(self.radius * 2)
            )
        return pygame.Rect(0, 0, 0, 0)
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside this obstacle."""
        if self.type in [ObstacleType.ANTI_RIPPLE, ObstacleType.CURRENT_ZONE]:
            width, height = self.size
            return (abs(point[0] - self.position.x) <= width / 2 and
                    abs(point[1] - self.position.y) <= height / 2)
        elif self.type == ObstacleType.WHIRLPOOL:
            dx = point[0] - self.position.x
            dy = point[1] - self.position.y
            return (dx * dx + dy * dy) <= (self.radius * self.radius)
        elif self.type == ObstacleType.WALL:
            # Simplified: check if point is near wall line
            bounds = self.get_bounds_rect()
            return bounds.collidepoint(point)
        return False


class PaletteButton:
    """Button for selecting obstacle types in the palette."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 obstacle_type: str, label: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.obstacle_type = obstacle_type
        self.label = label
        self.is_hovered = False
        self.is_selected = False
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the palette button."""
        # Determine color based on state
        if self.is_selected:
            color = (100, 170, 220)
            border_color = (70, 140, 190)
        elif self.is_hovered:
            color = (140, 190, 240)
            border_color = (110, 160, 210)
        else:
            color = (160, 200, 240)
            border_color = (130, 170, 210)
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw label
        text_surface = font.render(self.label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Button:
    """Generic button widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int, label: str, 
                 enabled: bool = True):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.is_hovered = False
        self.enabled = enabled
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        if not self.enabled:
            color = (180, 180, 180)
            border_color = (150, 150, 150)
            text_color = (120, 120, 120)
        elif self.is_hovered:
            color = (100, 170, 220)
            border_color = (70, 140, 190)
            text_color = (255, 255, 255)
        else:
            color = (140, 190, 240)
            border_color = (110, 160, 210)
            text_color = (255, 255, 255)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        text_surface = font.render(self.label, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if button was clicked."""
        return self.enabled and self.rect.collidepoint(mouse_pos)


class TextInput:
    """Text input widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 initial_text: str = "", placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text
        self.placeholder = placeholder
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def update(self, dt: float):
        """Update cursor blink."""
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click."""
        self.is_focused = self.rect.collidepoint(mouse_pos)
    
    def handle_key(self, event: pygame.event.Event):
        """Handle keyboard input."""
        if not self.is_focused:
            return
        
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
            self.is_focused = False
        elif event.unicode and len(self.text) < 30:
            self.text += event.unicode
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the text input."""
        # Background
        bg_color = (255, 255, 255) if self.is_focused else (240, 240, 240)
        border_color = (100, 170, 220) if self.is_focused else (180, 180, 180)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=3)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=3)
        
        # Text
        display_text = self.text if self.text else self.placeholder
        text_color = (70, 70, 70) if self.text else (150, 150, 150)
        text_surface = font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Cursor
        if self.is_focused and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, (70, 70, 70), 
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.bottom - 5), 2)


class Dropdown:
    """Dropdown menu widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 options: List[str], selected_index: int = 0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.is_open = False
        self.is_hovered = False
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click. Returns True if an option was selected."""
        if self.rect.collidepoint(mouse_pos):
            self.is_open = not self.is_open
            return False
        
        if self.is_open:
            # Check if clicking on an option
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.rect.height,
                    self.rect.width,
                    self.rect.height
                )
                if option_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    self.is_open = False
                    return True
            
            # Clicked outside - close dropdown
            self.is_open = False
        
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the dropdown."""
        # Main button
        color = (140, 190, 240) if self.is_hovered or self.is_open else (160, 200, 240)
        border_color = (110, 160, 210)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Selected text
        text = self.options[self.selected_index] if self.options else ""
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Arrow
        arrow_x = self.rect.right - 15
        arrow_y = self.rect.centery
        arrow_points = [
            (arrow_x - 5, arrow_y - 3),
            (arrow_x + 5, arrow_y - 3),
            (arrow_x, arrow_y + 3)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)
        
        # Options (if open)
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.rect.height,
                    self.rect.width,
                    self.rect.height
                )
                
                # Check hover
                mouse_pos = pygame.mouse.get_pos()
                is_option_hovered = option_rect.collidepoint(mouse_pos)
                option_color = (120, 180, 230) if is_option_hovered else (160, 200, 240)
                
                pygame.draw.rect(screen, option_color, option_rect)
                pygame.draw.rect(screen, border_color, option_rect, 2)
                
                option_text = font.render(option, True, (255, 255, 255))
                option_text_rect = option_text.get_rect(
                    midleft=(option_rect.x + 5, option_rect.centery))
                screen.blit(option_text, option_text_rect)


class ConfirmDialog:
    """Confirmation dialog widget."""
    
    def __init__(self, message: str, on_confirm, on_cancel):
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.is_visible = False
        
        # Dialog dimensions
        self.width = 400
        self.height = 150
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Buttons
        button_width = 100
        button_height = 35
        button_y = self.y + self.height - button_height - 20
        
        self.confirm_button = Button(
            self.x + self.width // 2 - button_width - 10,
            button_y,
            button_width,
            button_height,
            "Yes"
        )
        
        self.cancel_button = Button(
            self.x + self.width // 2 + 10,
            button_y,
            button_width,
            button_height,
            "No"
        )
    
    def show(self):
        """Show the dialog."""
        self.is_visible = True
    
    def hide(self):
        """Hide the dialog."""
        self.is_visible = False
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update button hover states."""
        if self.is_visible:
            self.confirm_button.update(mouse_pos)
            self.cancel_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click."""
        if not self.is_visible:
            return
        
        if self.confirm_button.is_clicked(mouse_pos):
            self.hide()
            self.on_confirm()
        elif self.cancel_button.is_clicked(mouse_pos):
            self.hide()
            self.on_cancel()
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the dialog."""
        if not self.is_visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Dialog background
        pygame.draw.rect(screen, (240, 240, 240), self.rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 3, border_radius=10)
        
        # Message
        message_font = pygame.font.SysFont('Arial', 18)
        message_lines = self.message.split('\n')
        y_offset = self.y + 30
        for line in message_lines:
            message_surface = message_font.render(line, True, (70, 70, 70))
            message_rect = message_surface.get_rect(centerx=self.rect.centerx, y=y_offset)
            screen.blit(message_surface, message_rect)
            y_offset += 30
        
        # Buttons
        self.confirm_button.draw(screen, font)
        self.cancel_button.draw(screen, font)


class PropertyPanel:
    """Panel for editing properties of selected obstacle."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected_obstacle: Optional[BuilderObstacle] = None
    
    def set_selected_obstacle(self, obstacle: Optional[BuilderObstacle]):
        """Set the currently selected obstacle."""
        self.selected_obstacle = obstacle
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the property panel."""
        # Draw panel background
        pygame.draw.rect(screen, (240, 240, 240), self.rect)
        pygame.draw.rect(screen, (180, 180, 180), self.rect, 2)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 18, bold=True)
        title_surface = title_font.render("Properties", True, (70, 70, 70))
        screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw properties if obstacle is selected
        if self.selected_obstacle:
            y_offset = 50
            line_height = 25
            
            # Position
            pos_text = f"Position: ({int(self.selected_obstacle.position.x)}, {int(self.selected_obstacle.position.y)})"
            pos_surface = font.render(pos_text, True, (70, 70, 70))
            screen.blit(pos_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += line_height
            
            # Type-specific properties
            if self.selected_obstacle.type in [ObstacleType.ANTI_RIPPLE, ObstacleType.CURRENT_ZONE]:
                size_text = f"Size: {int(self.selected_obstacle.size[0])} x {int(self.selected_obstacle.size[1])}"
                size_surface = font.render(size_text, True, (70, 70, 70))
                screen.blit(size_surface, (self.rect.x + 10, self.rect.y + y_offset))
                y_offset += line_height
                
                if self.selected_obstacle.type == ObstacleType.CURRENT_ZONE:
                    strength_text = f"Strength: {int(self.selected_obstacle.strength)}"
                    strength_surface = font.render(strength_text, True, (70, 70, 70))
                    screen.blit(strength_surface, (self.rect.x + 10, self.rect.y + y_offset))
                    y_offset += line_height
                    
                    dir_text = f"Direction: ({self.selected_obstacle.direction.x:.2f}, {self.selected_obstacle.direction.y:.2f})"
                    dir_surface = font.render(dir_text, True, (70, 70, 70))
                    screen.blit(dir_surface, (self.rect.x + 10, self.rect.y + y_offset))
            
            elif self.selected_obstacle.type == ObstacleType.WALL:
                length_text = f"Length: {int(self.selected_obstacle.length)}"
                length_surface = font.render(length_text, True, (70, 70, 70))
                screen.blit(length_surface, (self.rect.x + 10, self.rect.y + y_offset))
                y_offset += line_height
                
                rotation_deg = math.degrees(self.selected_obstacle.rotation)
                rotation_text = f"Rotation: {int(rotation_deg)}°"
                rotation_surface = font.render(rotation_text, True, (70, 70, 70))
                screen.blit(rotation_surface, (self.rect.x + 10, self.rect.y + y_offset))
            
            elif self.selected_obstacle.type == ObstacleType.WHIRLPOOL:
                radius_text = f"Radius: {int(self.selected_obstacle.radius)}"
                radius_surface = font.render(radius_text, True, (70, 70, 70))
                screen.blit(radius_surface, (self.rect.x + 10, self.rect.y + y_offset))
                y_offset += line_height
                
                strength_text = f"Pull Strength: {int(self.selected_obstacle.pull_strength)}"
                strength_surface = font.render(strength_text, True, (70, 70, 70))
                screen.blit(strength_surface, (self.rect.x + 10, self.rect.y + y_offset))
        else:
            # No selection message
            no_sel_text = "No obstacle selected"
            no_sel_surface = font.render(no_sel_text, True, (150, 150, 150))
            screen.blit(no_sel_surface, (self.rect.x + 10, self.rect.y + 50))


class LevelBuilder:
    """Main level builder interface."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.obstacles: List[BuilderObstacle] = []
        self.selected_obstacle: Optional[BuilderObstacle] = None
        self.selected_palette_type: Optional[str] = None
        
        # Level properties
        self.level_name = "Untitled Level"
        self.ball_start = Vector2(100, 300)
        self.target_position = Vector2(700, 300)
        self.target_radius = 40
        
        # Grid settings
        self.show_grid = True
        self.grid_size = 50
        
        # Dragging state
        self.is_dragging = False
        self.drag_offset = Vector2(0, 0)
        self.is_resizing = False
        self.resize_handle = None  # 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'
        
        # Undo/Redo system (LIFO stack, max 4 actions)
        self.undo_stack: List[List[BuilderObstacle]] = []
        self.redo_stack: List[List[BuilderObstacle]] = []
        self.max_undo_steps = 4
        
        # Test play state
        self.is_test_playing = False
        self.saved_state_for_test = None
        
        # Canvas area (pond area)
        self.canvas_rect = pygame.Rect(*WATER_POOL_RECT)
        
        # Left palette panel
        palette_width = 200
        palette_x = 10
        palette_y = 100
        button_height = 50
        button_spacing = 10
        
        self.palette_buttons = [
            PaletteButton(palette_x, palette_y, palette_width, button_height,
                         ObstacleType.ANTI_RIPPLE, "Anti-Ripple"),
            PaletteButton(palette_x, palette_y + (button_height + button_spacing), 
                         palette_width, button_height,
                         ObstacleType.WALL, "Wall"),
            PaletteButton(palette_x, palette_y + 2 * (button_height + button_spacing),
                         palette_width, button_height,
                         ObstacleType.CURRENT_ZONE, "Current Zone"),
            PaletteButton(palette_x, palette_y + 3 * (button_height + button_spacing),
                         palette_width, button_height,
                         ObstacleType.WHIRLPOOL, "Whirlpool")
        ]
        
        # Right property panel
        property_panel_width = 250
        property_panel_x = SCREEN_WIDTH - property_panel_width - 10
        property_panel_y = 100
        property_panel_height = SCREEN_HEIGHT - property_panel_y - 80
        
        self.property_panel = PropertyPanel(property_panel_x, property_panel_y,
                                           property_panel_width, property_panel_height)
        
        # Top toolbar
        toolbar_y = 10
        toolbar_height = 40
        button_width = 80
        button_spacing = 10
        
        # Level name input
        self.level_name_input = TextInput(
            220, toolbar_y + 5, 200, 30, 
            self.level_name, "Level Name"
        )
        
        # Undo/Redo buttons
        undo_x = 430
        self.undo_button = Button(undo_x, toolbar_y + 5, button_width, 30, "Undo")
        self.redo_button = Button(undo_x + button_width + button_spacing, 
                                  toolbar_y + 5, button_width, 30, "Redo")
        
        # Grid snap toggle
        grid_x = undo_x + 2 * (button_width + button_spacing)
        self.grid_toggle_button = Button(grid_x, toolbar_y + 5, 
                                         button_width + 20, 30, "Grid: ON")
        
        # Test play button
        test_x = grid_x + button_width + 30
        self.test_play_button = Button(test_x, toolbar_y + 5, 
                                       button_width + 20, 30, "Test Play")
        
        # Import/Export buttons
        export_x = test_x + button_width + 30
        self.export_button = Button(export_x, toolbar_y + 5, 
                                    button_width, 30, "Export")
        self.import_button = Button(export_x + button_width + button_spacing, 
                                    toolbar_y + 5, button_width, 30, "Import")
        
        # Bottom toolbar
        bottom_toolbar_y = SCREEN_HEIGHT - 60
        
        # Template dropdown
        template_options = ["Blank", "Maze", "Islands", "Channels"]
        self.template_dropdown = Dropdown(
            220, bottom_toolbar_y + 10, 150, 35, template_options
        )
        
        # Use template button
        self.use_template_button = Button(
            380, bottom_toolbar_y + 10, 120, 35, "Use Template"
        )
        
        # Exit button
        self.exit_button = Button(
            SCREEN_WIDTH - 110, bottom_toolbar_y + 10, 100, 35, "Exit"
        )
        
        # Confirmation dialog
        self.confirm_dialog = ConfirmDialog(
            "Apply template?\nThis will clear current obstacles.",
            self.apply_template,
            lambda: None
        )
        
        # Fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        # Clock for text input cursor
        self.clock = pygame.time.Clock()
        self.dt = 0
    
    def save_state_for_undo(self):
        """Save current state to undo stack."""
        # Deep copy obstacles
        state = [self.copy_obstacle(obs) for obs in self.obstacles]
        self.undo_stack.append(state)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
    
    def copy_obstacle(self, obstacle: BuilderObstacle) -> BuilderObstacle:
        """Create a deep copy of an obstacle."""
        kwargs = {}
        if obstacle.type == ObstacleType.ANTI_RIPPLE:
            kwargs['size'] = obstacle.size.copy()
        elif obstacle.type == ObstacleType.WALL:
            kwargs['length'] = obstacle.length
            kwargs['rotation'] = obstacle.rotation
        elif obstacle.type == ObstacleType.CURRENT_ZONE:
            kwargs['size'] = obstacle.size.copy()
            kwargs['strength'] = obstacle.strength
            kwargs['direction'] = obstacle.direction.copy()
        elif obstacle.type == ObstacleType.WHIRLPOOL:
            kwargs['radius'] = obstacle.radius
            kwargs['pull_strength'] = obstacle.pull_strength
        
        return BuilderObstacle(obstacle.type, obstacle.position.copy(), **kwargs)
    
    def undo(self):
        """Undo last action."""
        if not self.undo_stack:
            return
        
        # Save current state to redo stack
        current_state = [self.copy_obstacle(obs) for obs in self.obstacles]
        self.redo_stack.append(current_state)
        if len(self.redo_stack) > self.max_undo_steps:
            self.redo_stack.pop(0)
        
        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.obstacles = [self.copy_obstacle(obs) for obs in previous_state]
        self.selected_obstacle = None
        self.property_panel.set_selected_obstacle(None)
    
    def redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            return
        
        # Save current state to undo stack
        current_state = [self.copy_obstacle(obs) for obs in self.obstacles]
        self.undo_stack.append(current_state)
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # Restore next state
        next_state = self.redo_stack.pop()
        self.obstacles = [self.copy_obstacle(obs) for obs in next_state]
        self.selected_obstacle = None
        self.property_panel.set_selected_obstacle(None)
    
    def apply_template(self):
        """Apply selected template."""
        self.save_state_for_undo()
        
        template_name = self.template_dropdown.options[self.template_dropdown.selected_index]
        self.obstacles.clear()
        
        if template_name == "Blank":
            # No obstacles
            pass
        
        elif template_name == "Maze":
            # Create maze-like pattern with walls
            walls = [
                (300, 200, 150, 0),
                (300, 400, 150, 0),
                (500, 300, 150, math.pi / 2),
                (700, 200, 150, 0),
                (700, 400, 150, 0),
            ]
            for x, y, length, rotation in walls:
                wall = BuilderObstacle(ObstacleType.WALL, Vector2(x, y), 
                                      length=length, rotation=rotation)
                self.obstacles.append(wall)
        
        elif template_name == "Islands":
            # Create island pattern with anti-ripple zones
            islands = [
                (300, 250, 80, 80),
                (500, 350, 100, 100),
                (700, 250, 80, 80),
            ]
            for x, y, w, h in islands:
                island = BuilderObstacle(ObstacleType.ANTI_RIPPLE, Vector2(x, y), 
                                        size=[w, h])
                self.obstacles.append(island)
        
        elif template_name == "Channels":
            # Create channel pattern with current zones
            channels = [
                (300, 300, 150, 100, Vector2(1, 0)),
                (600, 300, 150, 100, Vector2(-1, 0)),
            ]
            for x, y, w, h, direction in channels:
                channel = BuilderObstacle(ObstacleType.CURRENT_ZONE, Vector2(x, y),
                                         size=[w, h], strength=150, direction=direction)
                self.obstacles.append(channel)
        
        self.selected_obstacle = None
        self.property_panel.set_selected_obstacle(None)
    
    def export_to_json(self) -> str:
        """Export level to JSON string."""
        level_data = {
            "name": self.level_name,
            "ball_start": [self.ball_start.x, self.ball_start.y],
            "target_position": [self.target_position.x, self.target_position.y],
            "target_radius": self.target_radius,
            "obstacles": []
        }
        
        for obstacle in self.obstacles:
            obs_data = {
                "type": obstacle.type,
                "position": [obstacle.position.x, obstacle.position.y]
            }
            
            if obstacle.type == ObstacleType.ANTI_RIPPLE:
                obs_data["size"] = obstacle.size
            elif obstacle.type == ObstacleType.WALL:
                obs_data["length"] = obstacle.length
                obs_data["rotation"] = obstacle.rotation
            elif obstacle.type == ObstacleType.CURRENT_ZONE:
                obs_data["size"] = obstacle.size
                obs_data["strength"] = obstacle.strength
                obs_data["direction"] = [obstacle.direction.x, obstacle.direction.y]
            elif obstacle.type == ObstacleType.WHIRLPOOL:
                obs_data["radius"] = obstacle.radius
                obs_data["pull_strength"] = obstacle.pull_strength
            
            level_data["obstacles"].append(obs_data)
        
        return json.dumps(level_data, indent=2)
    
    def import_from_json(self, json_str: str):
        """Import level from JSON string."""
        try:
            self.save_state_for_undo()
            
            level_data = json.loads(json_str)
            
            # Load level properties
            self.level_name = level_data.get("name", "Imported Level")
            self.level_name_input.text = self.level_name
            
            if "ball_start" in level_data:
                self.ball_start = Vector2(*level_data["ball_start"])
            if "target_position" in level_data:
                self.target_position = Vector2(*level_data["target_position"])
            if "target_radius" in level_data:
                self.target_radius = level_data["target_radius"]
            
            # Load obstacles
            self.obstacles.clear()
            for obs_data in level_data.get("obstacles", []):
                obs_type = obs_data["type"]
                position = Vector2(*obs_data["position"])
                
                kwargs = {}
                if obs_type == ObstacleType.ANTI_RIPPLE:
                    kwargs["size"] = obs_data.get("size", [100, 100])
                elif obs_type == ObstacleType.WALL:
                    kwargs["length"] = obs_data.get("length", 150)
                    kwargs["rotation"] = obs_data.get("rotation", 0.0)
                elif obs_type == ObstacleType.CURRENT_ZONE:
                    kwargs["size"] = obs_data.get("size", [150, 100])
                    kwargs["strength"] = obs_data.get("strength", 150)
                    direction_data = obs_data.get("direction", [1, 0])
                    kwargs["direction"] = Vector2(*direction_data)
                elif obs_type == ObstacleType.WHIRLPOOL:
                    kwargs["radius"] = obs_data.get("radius", 60)
                    kwargs["pull_strength"] = obs_data.get("pull_strength", 120)
                
                obstacle = BuilderObstacle(obs_type, position, **kwargs)
                self.obstacles.append(obstacle)
            
            self.selected_obstacle = None
            self.property_panel.set_selected_obstacle(None)
            
            return True
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return False
    
    def start_test_play(self):
        """Start test play mode."""
        # Save current state
        self.saved_state_for_test = {
            'obstacles': [self.copy_obstacle(obs) for obs in self.obstacles],
            'level_name': self.level_name,
            'ball_start': self.ball_start.copy(),
            'target_position': self.target_position.copy(),
            'target_radius': self.target_radius
        }
        self.is_test_playing = True
        
        # Return level data for testing
        return self.create_level_data()
    
    def exit_test_play(self):
        """Exit test play mode and restore builder state."""
        if self.saved_state_for_test:
            self.obstacles = [self.copy_obstacle(obs) 
                            for obs in self.saved_state_for_test['obstacles']]
            self.level_name = self.saved_state_for_test['level_name']
            self.ball_start = self.saved_state_for_test['ball_start'].copy()
            self.target_position = self.saved_state_for_test['target_position'].copy()
            self.target_radius = self.saved_state_for_test['target_radius']
            
            self.saved_state_for_test = None
        
        self.is_test_playing = False
    
    def create_level_data(self) -> LevelData:
        """Create LevelData object from current builder state."""
        # Separate obstacles by type
        obstacles = []
        walls = []
        current_zones = []
        whirlpools = []
        
        # Convert builder obstacles to game obstacles
        for obs in self.obstacles:
            if obs.type == ObstacleType.ANTI_RIPPLE:
                game_obs = Obstacle(
                    obstacle_type="anti_ripple_zone",
                    position=obs.position.copy(),
                    size=obs.size.copy()
                )
                obstacles.append(game_obs)
            elif obs.type == ObstacleType.WALL:
                game_obs = Wall(
                    position=obs.position.copy(),
                    length=obs.length,
                    rotation=obs.rotation
                )
                walls.append(game_obs)
            elif obs.type == ObstacleType.CURRENT_ZONE:
                game_obs = CurrentZone(
                    position=obs.position.copy(),
                    size=obs.size.copy(),
                    strength=obs.strength,
                    direction=obs.direction.copy()
                )
                current_zones.append(game_obs)
            elif obs.type == ObstacleType.WHIRLPOOL:
                game_obs = Whirlpool(
                    position=obs.position.copy(),
                    radius=obs.radius,
                    pull_strength=obs.pull_strength
                )
                whirlpools.append(game_obs)
        
        # Create LevelData object with all obstacle types
        level_data = LevelData(
            level_id=999,  # Test level ID
            ball_start=self.ball_start.copy(),
            target_position=self.target_position.copy(),
            target_radius=self.target_radius,
            obstacles=obstacles,
            walls=walls,
            current_zones=current_zones,
            whirlpools=whirlpools,
            initial_stones=20  # Test play gets 20 stones
        )
        
        return level_data
    
    def handle_mouse_down(self, mouse_pos: Tuple[int, int]):
        """Handle mouse button down event."""
        # Check confirmation dialog first
        if self.confirm_dialog.is_visible:
            self.confirm_dialog.handle_click(mouse_pos)
            return
        
        # Check text input
        self.level_name_input.handle_click(mouse_pos)
        
        # Check top toolbar buttons
        if self.undo_button.is_clicked(mouse_pos):
            self.undo()
            return
        
        if self.redo_button.is_clicked(mouse_pos):
            self.redo()
            return
        
        if self.grid_toggle_button.is_clicked(mouse_pos):
            self.show_grid = not self.show_grid
            self.grid_toggle_button.label = f"Grid: {'ON' if self.show_grid else 'OFF'}"
            return
        
        if self.test_play_button.is_clicked(mouse_pos):
            # Test play will be handled by main game loop
            return
        
        if self.export_button.is_clicked(mouse_pos):
            json_str = self.export_to_json()
            # Save to file
            try:
                filename = f"levels/{self.level_name.replace(' ', '_')}.json"
                with open(filename, 'w') as f:
                    f.write(json_str)
                print(f"Level exported to {filename}")
            except Exception as e:
                print(f"Error exporting: {e}")
            return
        
        if self.import_button.is_clicked(mouse_pos):
            # Try to import from file
            try:
                filename = f"levels/{self.level_name.replace(' ', '_')}.json"
                with open(filename, 'r') as f:
                    json_str = f.read()
                if self.import_from_json(json_str):
                    print(f"Level imported from {filename}")
                else:
                    print("Import failed")
            except Exception as e:
                print(f"Error importing: {e}")
            return
        
        # Check bottom toolbar
        if self.template_dropdown.handle_click(mouse_pos):
            return
        
        if self.use_template_button.is_clicked(mouse_pos):
            self.confirm_dialog.show()
            return
        
        if self.exit_button.is_clicked(mouse_pos):
            # Exit will be handled by main game loop
            return
        
        # Check palette buttons
        for button in self.palette_buttons:
            if button.rect.collidepoint(mouse_pos):
                # Deselect all buttons
                for b in self.palette_buttons:
                    b.is_selected = False
                # Select clicked button
                button.is_selected = True
                self.selected_palette_type = button.obstacle_type
                return
        
        # Check if clicking in canvas area
        if self.canvas_rect.collidepoint(mouse_pos):
            # Check if clicking on existing obstacle
            clicked_obstacle = None
            for obstacle in reversed(self.obstacles):  # Check from top to bottom
                if obstacle.contains_point(mouse_pos):
                    clicked_obstacle = obstacle
                    break
            
            if clicked_obstacle:
                # Select obstacle
                self.deselect_all()
                clicked_obstacle.is_selected = True
                self.selected_obstacle = clicked_obstacle
                self.property_panel.set_selected_obstacle(clicked_obstacle)
                
                # Check if clicking on resize handle
                handle = self.get_resize_handle_at(mouse_pos, clicked_obstacle)
                if handle:
                    self.is_resizing = True
                    self.resize_handle = handle
                else:
                    # Start dragging
                    self.is_dragging = True
                    self.drag_offset = Vector2(
                        mouse_pos[0] - clicked_obstacle.position.x,
                        mouse_pos[1] - clicked_obstacle.position.y
                    )
            else:
                # Place new obstacle if palette type selected
                if self.selected_palette_type:
                    self.place_obstacle(mouse_pos)
                else:
                    # Deselect all
                    self.deselect_all()
                    self.property_panel.set_selected_obstacle(None)
    
    def handle_mouse_up(self, mouse_pos: Tuple[int, int]):
        """Handle mouse button up event."""
        self.is_dragging = False
        self.is_resizing = False
        self.resize_handle = None
    
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion event."""
        # Update palette button hover states
        for button in self.palette_buttons:
            button.update(mouse_pos)
        
        # Handle dragging
        if self.is_dragging and self.selected_obstacle:
            new_x = mouse_pos[0] - self.drag_offset.x
            new_y = mouse_pos[1] - self.drag_offset.y
            
            # Snap to grid if enabled
            if self.show_grid:
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
            
            # Keep within canvas bounds
            if self.canvas_rect.collidepoint(new_x, new_y):
                self.selected_obstacle.position.x = new_x
                self.selected_obstacle.position.y = new_y
        
        # Handle resizing
        elif self.is_resizing and self.selected_obstacle and self.resize_handle:
            self.resize_obstacle(mouse_pos)
    
    def handle_key_down(self, event: pygame.event.Event):
        """Handle keyboard input."""
        # Handle text input first
        self.level_name_input.handle_key(event)
        
        # Don't process other keys if text input is focused
        if self.level_name_input.is_focused:
            return
        
        if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
            # Delete selected obstacle
            if self.selected_obstacle:
                self.save_state_for_undo()
                self.obstacles.remove(self.selected_obstacle)
                self.selected_obstacle = None
                self.property_panel.set_selected_obstacle(None)
        elif event.key == pygame.K_g:
            # Toggle grid
            self.show_grid = not self.show_grid
            self.grid_toggle_button.label = f"Grid: {'ON' if self.show_grid else 'OFF'}"
        elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Ctrl+Z for undo
            self.undo()
        elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Ctrl+Y for redo
            self.redo()
    
    def place_obstacle(self, position: Tuple[int, int]):
        """Place a new obstacle at the specified position."""
        self.save_state_for_undo()
        
        pos = Vector2(position[0], position[1])
        
        # Snap to grid if enabled
        if self.show_grid:
            pos.x = round(pos.x / self.grid_size) * self.grid_size
            pos.y = round(pos.y / self.grid_size) * self.grid_size
        
        # Create obstacle based on selected type
        if self.selected_palette_type == ObstacleType.ANTI_RIPPLE:
            obstacle = BuilderObstacle(ObstacleType.ANTI_RIPPLE, pos, size=[100, 100])
        elif self.selected_palette_type == ObstacleType.WALL:
            obstacle = BuilderObstacle(ObstacleType.WALL, pos, length=150, rotation=0.0)
        elif self.selected_palette_type == ObstacleType.CURRENT_ZONE:
            obstacle = BuilderObstacle(ObstacleType.CURRENT_ZONE, pos, 
                                      size=[150, 100], strength=150, direction=Vector2(1, 0))
        elif self.selected_palette_type == ObstacleType.WHIRLPOOL:
            obstacle = BuilderObstacle(ObstacleType.WHIRLPOOL, pos, radius=60, pull_strength=120)
        else:
            return
        
        self.obstacles.append(obstacle)
        
        # Select the new obstacle
        self.deselect_all()
        obstacle.is_selected = True
        self.selected_obstacle = obstacle
        self.property_panel.set_selected_obstacle(obstacle)
    
    def deselect_all(self):
        """Deselect all obstacles."""
        for obstacle in self.obstacles:
            obstacle.is_selected = False
        self.selected_obstacle = None
    
    def get_resize_handle_at(self, mouse_pos: Tuple[int, int], 
                            obstacle: BuilderObstacle) -> Optional[str]:
        """Get resize handle at mouse position, if any."""
        if obstacle.type in [ObstacleType.ANTI_RIPPLE, ObstacleType.CURRENT_ZONE]:
            width, height = obstacle.size
            handle_size = 10
            
            # Calculate handle positions
            left = obstacle.position.x - width / 2
            right = obstacle.position.x + width / 2
            top = obstacle.position.y - height / 2
            bottom = obstacle.position.y + height / 2
            
            # Check corner handles
            if abs(mouse_pos[0] - left) < handle_size and abs(mouse_pos[1] - top) < handle_size:
                return 'nw'
            elif abs(mouse_pos[0] - right) < handle_size and abs(mouse_pos[1] - top) < handle_size:
                return 'ne'
            elif abs(mouse_pos[0] - left) < handle_size and abs(mouse_pos[1] - bottom) < handle_size:
                return 'sw'
            elif abs(mouse_pos[0] - right) < handle_size and abs(mouse_pos[1] - bottom) < handle_size:
                return 'se'
            
            # Check edge handles
            elif abs(mouse_pos[0] - left) < handle_size and top < mouse_pos[1] < bottom:
                return 'w'
            elif abs(mouse_pos[0] - right) < handle_size and top < mouse_pos[1] < bottom:
                return 'e'
            elif abs(mouse_pos[1] - top) < handle_size and left < mouse_pos[0] < right:
                return 'n'
            elif abs(mouse_pos[1] - bottom) < handle_size and left < mouse_pos[0] < right:
                return 's'
        
        elif obstacle.type == ObstacleType.WHIRLPOOL:
            # Check if on edge of circle (for radius resize)
            dx = mouse_pos[0] - obstacle.position.x
            dy = mouse_pos[1] - obstacle.position.y
            distance = math.sqrt(dx * dx + dy * dy)
            if abs(distance - obstacle.radius) < 10:
                return 'radius'
        
        return None
    
    def resize_obstacle(self, mouse_pos: Tuple[int, int]):
        """Resize the selected obstacle based on mouse position."""
        if not self.selected_obstacle or not self.resize_handle:
            return
        
        if self.selected_obstacle.type in [ObstacleType.ANTI_RIPPLE, ObstacleType.CURRENT_ZONE]:
            width, height = self.selected_obstacle.size
            center_x = self.selected_obstacle.position.x
            center_y = self.selected_obstacle.position.y
            
            # Calculate new size based on handle
            if 'w' in self.resize_handle:
                new_width = 2 * (center_x - mouse_pos[0])
                width = max(20, new_width)
            elif 'e' in self.resize_handle:
                new_width = 2 * (mouse_pos[0] - center_x)
                width = max(20, new_width)
            
            if 'n' in self.resize_handle:
                new_height = 2 * (center_y - mouse_pos[1])
                height = max(20, new_height)
            elif 's' in self.resize_handle:
                new_height = 2 * (mouse_pos[1] - center_y)
                height = max(20, new_height)
            
            self.selected_obstacle.size = [width, height]
        
        elif self.selected_obstacle.type == ObstacleType.WHIRLPOOL and self.resize_handle == 'radius':
            dx = mouse_pos[0] - self.selected_obstacle.position.x
            dy = mouse_pos[1] - self.selected_obstacle.position.y
            new_radius = math.sqrt(dx * dx + dy * dy)
            self.selected_obstacle.radius = max(20, new_radius)
    
    def update(self, dt: float):
        """Update builder state."""
        self.dt = dt
        self.level_name_input.update(dt)
        
        # Update button states
        mouse_pos = pygame.mouse.get_pos()
        self.undo_button.update(mouse_pos)
        self.redo_button.update(mouse_pos)
        self.grid_toggle_button.update(mouse_pos)
        self.test_play_button.update(mouse_pos)
        self.export_button.update(mouse_pos)
        self.import_button.update(mouse_pos)
        self.use_template_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)
        self.template_dropdown.update(mouse_pos)
        self.confirm_dialog.update(mouse_pos)
        
        # Update undo/redo button enabled state
        self.undo_button.enabled = len(self.undo_stack) > 0
        self.redo_button.enabled = len(self.redo_stack) > 0
        
        # Update level name from input
        if self.level_name_input.text:
            self.level_name = self.level_name_input.text
    
    def draw(self):
        """Draw the level builder interface."""
        # Clear screen
        self.screen.fill((200, 220, 240))
        
        # Draw title
        title_surface = self.title_font.render("Level Builder", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Draw top toolbar background
        toolbar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (220, 230, 240), toolbar_rect)
        pygame.draw.line(self.screen, (180, 180, 180), 
                        (0, 60), (SCREEN_WIDTH, 60), 2)
        
        # Draw top toolbar widgets
        self.level_name_input.draw(self.screen, self.font)
        self.undo_button.draw(self.screen, self.font)
        self.redo_button.draw(self.screen, self.font)
        self.grid_toggle_button.draw(self.screen, self.font)
        self.test_play_button.draw(self.screen, self.font)
        self.export_button.draw(self.screen, self.font)
        self.import_button.draw(self.screen, self.font)
        
        # Draw bottom toolbar background
        bottom_toolbar_y = SCREEN_HEIGHT - 60
        bottom_toolbar_rect = pygame.Rect(0, bottom_toolbar_y, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (220, 230, 240), bottom_toolbar_rect)
        pygame.draw.line(self.screen, (180, 180, 180), 
                        (0, bottom_toolbar_y), (SCREEN_WIDTH, bottom_toolbar_y), 2)
        
        # Draw bottom toolbar widgets
        template_label = self.font.render("Template:", True, (70, 70, 70))
        self.screen.blit(template_label, (230, bottom_toolbar_y + 20))
        self.template_dropdown.draw(self.screen, self.font)
        self.use_template_button.draw(self.screen, self.font)
        self.exit_button.draw(self.screen, self.font)
        
        # Draw canvas (pond area)
        self.draw_canvas()
        
        # Draw palette panel
        self.draw_palette()
        
        # Draw property panel
        self.property_panel.draw(self.screen, self.font)
        
        # Draw obstacles
        self.draw_obstacles()
        
        # Draw ball start and target
        self.draw_level_markers()
        
        # Draw confirmation dialog (on top of everything)
        self.confirm_dialog.draw(self.screen, self.font)
    
    def draw_level_markers(self):
        """Draw ball start position and target."""
        # Draw ball start (red circle)
        pygame.draw.circle(self.screen, (255, 100, 100), 
                          (int(self.ball_start.x), int(self.ball_start.y)), 15)
        pygame.draw.circle(self.screen, (200, 50, 50), 
                          (int(self.ball_start.x), int(self.ball_start.y)), 15, 2)
        
        # Draw target (green circle)
        pygame.draw.circle(self.screen, (100, 255, 100), 
                          (int(self.target_position.x), int(self.target_position.y)), 
                          int(self.target_radius))
        pygame.draw.circle(self.screen, (50, 200, 50), 
                          (int(self.target_position.x), int(self.target_position.y)), 
                          int(self.target_radius), 2)
    
    def draw_canvas(self):
        """Draw the canvas area with grid overlay."""
        # Draw water gradient background
        x, y, width, height = self.canvas_rect
        for i in range(height):
            ratio = i / height
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)
            r = int(173 * (1 - smooth_ratio) + 135 * smooth_ratio)
            g = int(216 * (1 - smooth_ratio) + 206 * smooth_ratio)
            b = int(230 * (1 - smooth_ratio) + 235 * smooth_ratio)
            pygame.draw.line(self.screen, (r, g, b), (x, y + i), (x + width, y + i))
        
        # Draw border
        pygame.draw.rect(self.screen, (120, 180, 200), self.canvas_rect, 3)
        
        # Draw grid if enabled
        if self.show_grid:
            grid_color = (150, 190, 210, 100)
            for gx in range(x, x + width, self.grid_size):
                pygame.draw.line(self.screen, grid_color, (gx, y), (gx, y + height), 1)
            for gy in range(y, y + height, self.grid_size):
                pygame.draw.line(self.screen, grid_color, (x, gy), (x + width, gy), 1)
    
    def draw_palette(self):
        """Draw the palette panel."""
        # Draw palette background
        palette_rect = pygame.Rect(5, 95, 210, 300)
        pygame.draw.rect(self.screen, (240, 240, 240), palette_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), palette_rect, 2)
        
        # Draw title
        title_surface = pygame.font.SysFont('Arial', 18, bold=True).render(
            "Obstacles", True, (70, 70, 70))
        self.screen.blit(title_surface, (15, 105))
        
        # Draw palette buttons
        for button in self.palette_buttons:
            button.draw(self.screen, self.font)
    
    def draw_obstacles(self):
        """Draw all obstacles in the builder."""
        for obstacle in self.obstacles:
            self.draw_obstacle(obstacle)
            
            # Draw selection highlight and resize handles
            if obstacle.is_selected:
                self.draw_selection_highlight(obstacle)
                self.draw_resize_handles(obstacle)
    
    def draw_obstacle(self, obstacle: BuilderObstacle):
        """Draw a single obstacle."""
        if obstacle.type == ObstacleType.ANTI_RIPPLE:
            width, height = obstacle.size
            rect = pygame.Rect(
                int(obstacle.position.x - width / 2),
                int(obstacle.position.y - height / 2),
                int(width),
                int(height)
            )
            # Semi-transparent gray
            temp_surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (100, 100, 100, 100), temp_surface.get_rect())
            pygame.draw.rect(temp_surface, (80, 80, 80), temp_surface.get_rect(), 2)
            self.screen.blit(temp_surface, rect.topleft)
        
        elif obstacle.type == ObstacleType.WALL:
            # Draw wall
            half_length = obstacle.length / 2
            start_x = obstacle.position.x - half_length * math.cos(obstacle.rotation)
            start_y = obstacle.position.y - half_length * math.sin(obstacle.rotation)
            end_x = obstacle.position.x + half_length * math.cos(obstacle.rotation)
            end_y = obstacle.position.y + half_length * math.sin(obstacle.rotation)
            
            pygame.draw.line(self.screen, (139, 119, 101), 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 10)
        
        elif obstacle.type == ObstacleType.CURRENT_ZONE:
            width, height = obstacle.size
            rect = pygame.Rect(
                int(obstacle.position.x - width / 2),
                int(obstacle.position.y - height / 2),
                int(width),
                int(height)
            )
            # Semi-transparent blue
            temp_surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (100, 150, 200, 100), temp_surface.get_rect())
            pygame.draw.rect(temp_surface, (80, 130, 180), temp_surface.get_rect(), 2)
            self.screen.blit(temp_surface, rect.topleft)
            
            # Draw direction arrow
            arrow_length = 40
            arrow_end_x = obstacle.position.x + obstacle.direction.x * arrow_length
            arrow_end_y = obstacle.position.y + obstacle.direction.y * arrow_length
            pygame.draw.line(self.screen, (255, 255, 255),
                           (int(obstacle.position.x), int(obstacle.position.y)),
                           (int(arrow_end_x), int(arrow_end_y)), 3)
        
        elif obstacle.type == ObstacleType.WHIRLPOOL:
            # Draw whirlpool
            pos = (int(obstacle.position.x), int(obstacle.position.y))
            radius = int(obstacle.radius)
            
            # Draw gradient circles
            for i in range(5):
                r = int(radius * (1 - i * 0.2))
                alpha = int(120 * (1 - i * 0.15))
                temp_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (80, 120, 180, alpha), (r, r), r)
                self.screen.blit(temp_surface, (pos[0] - r, pos[1] - r))
            
            pygame.draw.circle(self.screen, (60, 100, 150), pos, radius, 2)
    
    def draw_selection_highlight(self, obstacle: BuilderObstacle):
        """Draw selection highlight around obstacle."""
        bounds = obstacle.get_bounds_rect()
        # Draw dashed border
        pygame.draw.rect(self.screen, (255, 200, 0), bounds.inflate(10, 10), 3)
    
    def draw_resize_handles(self, obstacle: BuilderObstacle):
        """Draw resize handles for selected obstacle."""
        handle_size = 8
        handle_color = (255, 200, 0)
        
        if obstacle.type in [ObstacleType.ANTI_RIPPLE, ObstacleType.CURRENT_ZONE]:
            width, height = obstacle.size
            left = obstacle.position.x - width / 2
            right = obstacle.position.x + width / 2
            top = obstacle.position.y - height / 2
            bottom = obstacle.position.y + height / 2
            
            # Draw corner handles
            handles = [
                (left, top), (right, top), (left, bottom), (right, bottom),
                (left, obstacle.position.y), (right, obstacle.position.y),
                (obstacle.position.x, top), (obstacle.position.x, bottom)
            ]
            
            for hx, hy in handles:
                pygame.draw.rect(self.screen, handle_color,
                               pygame.Rect(int(hx) - handle_size // 2,
                                         int(hy) - handle_size // 2,
                                         handle_size, handle_size))
        
        elif obstacle.type == ObstacleType.WHIRLPOOL:
            # Draw handles on circle edge (4 cardinal directions)
            pos = (int(obstacle.position.x), int(obstacle.position.y))
            radius = int(obstacle.radius)
            
            for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                hx = pos[0] + radius * math.cos(angle)
                hy = pos[1] + radius * math.sin(angle)
                pygame.draw.rect(self.screen, handle_color,
                               pygame.Rect(int(hx) - handle_size // 2,
                                         int(hy) - handle_size // 2,
                                         handle_size, handle_size))
