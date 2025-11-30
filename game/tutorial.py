"""
Tutorial module for Ripple game.
Handles tutorial tooltips for levels 1-4.
"""

import pygame
import time
from typing import List, Optional, Tuple
from game.physics import Vector2


class Tooltip:
    """Individual tooltip with text, position, and pointer arrow."""
    
    def __init__(self, text: str, position: Vector2, pointer_direction: str = "down",
                 auto_dismiss_time: float = 10.0):
        """
        Initialize a tooltip.
        
        Args:
            text: Tooltip text content
            position: Position where tooltip should appear
            pointer_direction: Direction of pointer arrow ("up", "down", "left", "right")
            auto_dismiss_time: Time in seconds before auto-dismiss (default 10.0)
        """
        self.text = text
        self.position = position.copy()
        self.pointer_direction = pointer_direction
        self.auto_dismiss_time = auto_dismiss_time
        self.creation_time = time.time()
        self.is_dismissed = False
        
        # Visual properties
        self.padding = 15
        self.pointer_size = 12
        self.font = pygame.font.SysFont('Arial', 18)
        self.max_width = 300
        
        # Wrap text to fit max width
        self.wrapped_lines = self._wrap_text(text, self.max_width)
        
        # Calculate tooltip dimensions
        self.width, self.height = self._calculate_dimensions()
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, (0, 0, 0))
            
            if test_surface.get_width() <= max_width - self.padding * 2:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _calculate_dimensions(self) -> Tuple[int, int]:
        """Calculate tooltip panel dimensions based on text."""
        # Calculate width based on longest line
        max_line_width = 0
        for line in self.wrapped_lines:
            line_surface = self.font.render(line, True, (0, 0, 0))
            max_line_width = max(max_line_width, line_surface.get_width())
        
        width = max_line_width + self.padding * 2
        
        # Calculate height based on number of lines
        line_height = self.font.get_height()
        height = len(self.wrapped_lines) * line_height + self.padding * 2
        
        return width, height
    
    def should_auto_dismiss(self) -> bool:
        """Check if tooltip should be auto-dismissed."""
        elapsed = time.time() - self.creation_time
        return elapsed >= self.auto_dismiss_time
    
    def dismiss(self):
        """Manually dismiss the tooltip."""
        self.is_dismissed = True
    
    def is_active(self) -> bool:
        """Check if tooltip is still active."""
        return not self.is_dismissed and not self.should_auto_dismiss()
    
    def render(self, screen: pygame.Surface):
        """Render the tooltip on screen."""
        if not self.is_active():
            return
        
        # Calculate panel position based on pointer direction
        panel_x = int(self.position.x - self.width // 2)
        panel_y = int(self.position.y)
        
        if self.pointer_direction == "down":
            panel_y = int(self.position.y - self.height - self.pointer_size)
        elif self.pointer_direction == "up":
            panel_y = int(self.position.y + self.pointer_size)
        elif self.pointer_direction == "left":
            panel_x = int(self.position.x + self.pointer_size)
            panel_y = int(self.position.y - self.height // 2)
        elif self.pointer_direction == "right":
            panel_x = int(self.position.x - self.width - self.pointer_size)
            panel_y = int(self.position.y - self.height // 2)
        
        # Create semi-transparent surface for tooltip panel
        tooltip_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw panel background (semi-transparent white)
        pygame.draw.rect(tooltip_surface, (255, 255, 255, 230), 
                        tooltip_surface.get_rect(), border_radius=8)
        
        # Draw border
        pygame.draw.rect(tooltip_surface, (100, 150, 200), 
                        tooltip_surface.get_rect(), 2, border_radius=8)
        
        # Render text lines
        line_height = self.font.get_height()
        for i, line in enumerate(self.wrapped_lines):
            text_surface = self.font.render(line, True, (50, 50, 50))
            text_x = self.padding
            text_y = self.padding + i * line_height
            tooltip_surface.blit(text_surface, (text_x, text_y))
        
        # Blit tooltip panel to screen
        screen.blit(tooltip_surface, (panel_x, panel_y))
        
        # Draw pointer arrow
        self._draw_pointer(screen, panel_x, panel_y)
    
    def _draw_pointer(self, screen: pygame.Surface, panel_x: int, panel_y: int):
        """Draw pointer arrow pointing to target."""
        pointer_color = (255, 255, 255, 230)
        border_color = (100, 150, 200)
        
        if self.pointer_direction == "down":
            # Arrow pointing down from panel
            tip = (int(self.position.x), int(self.position.y))
            left = (int(self.position.x - self.pointer_size), panel_y + self.height)
            right = (int(self.position.x + self.pointer_size), panel_y + self.height)
            
            # Draw filled triangle
            pygame.draw.polygon(screen, pointer_color, [tip, left, right])
            # Draw border
            pygame.draw.polygon(screen, border_color, [tip, left, right], 2)
            
        elif self.pointer_direction == "up":
            # Arrow pointing up from panel
            tip = (int(self.position.x), int(self.position.y))
            left = (int(self.position.x - self.pointer_size), panel_y)
            right = (int(self.position.x + self.pointer_size), panel_y)
            
            pygame.draw.polygon(screen, pointer_color, [tip, left, right])
            pygame.draw.polygon(screen, border_color, [tip, left, right], 2)
            
        elif self.pointer_direction == "left":
            # Arrow pointing left from panel
            tip = (int(self.position.x), int(self.position.y))
            top = (panel_x, int(self.position.y - self.pointer_size))
            bottom = (panel_x, int(self.position.y + self.pointer_size))
            
            pygame.draw.polygon(screen, pointer_color, [tip, top, bottom])
            pygame.draw.polygon(screen, border_color, [tip, top, bottom], 2)
            
        elif self.pointer_direction == "right":
            # Arrow pointing right from panel
            tip = (int(self.position.x), int(self.position.y))
            top = (panel_x + self.width, int(self.position.y - self.pointer_size))
            bottom = (panel_x + self.width, int(self.position.y + self.pointer_size))
            
            pygame.draw.polygon(screen, pointer_color, [tip, top, bottom])
            pygame.draw.polygon(screen, border_color, [tip, top, bottom], 2)


class TutorialButton:
    """Button for dismissing tooltips or skipping tutorial."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """Initialize tutorial button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 16)
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update button hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)
    
    def render(self, screen: pygame.Surface):
        """Render button on screen."""
        # Button colors
        if self.is_hovered:
            bg_color = (120, 170, 220, 200)
            border_color = (80, 130, 180)
        else:
            bg_color = (100, 150, 200, 180)
            border_color = (70, 120, 170)
        
        # Create semi-transparent surface
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, bg_color, button_surface.get_rect(), border_radius=5)
        pygame.draw.rect(button_surface, border_color, button_surface.get_rect(), 2, border_radius=5)
        
        screen.blit(button_surface, self.rect.topleft)
        
        # Render text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class TutorialManager:
    """Manages tutorial tooltips for levels 1-4."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize tutorial manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active_tooltips: List[Tooltip] = []
        self.current_level = 0
        self.tutorial_skipped = False
        self.current_tooltip_index = 0
        
        # Skip Tutorial button (bottom-right)
        button_width = 120
        button_height = 35
        button_x = screen_width - button_width - 20
        button_y = screen_height - button_height - 20
        self.skip_button = TutorialButton(button_x, button_y, button_width, button_height, "Skip Tutorial")
        
        # Got it! button (appears with each tooltip)
        self.got_it_button: Optional[TutorialButton] = None
    
    def start_tutorial(self, level_number: int, level_data):
        """
        Start tutorial for the specified level.
        
        Args:
            level_number: Level number (1-4 for tutorial levels)
            level_data: Level data object with positions
        """
        self.current_level = level_number
        self.tutorial_skipped = False
        self.current_tooltip_index = 0
        self.active_tooltips = []
        
        # Only show tutorial for levels 1-4
        if level_number < 1 or level_number > 4:
            return
        
        # Create tooltips based on level
        if level_number == 1:
            self._create_level_1_tooltips(level_data)
        elif level_number == 2:
            self._create_level_2_tooltips(level_data)
        elif level_number == 3:
            self._create_level_3_tooltips(level_data)
        elif level_number == 4:
            self._create_level_4_tooltips(level_data)
        
        # Show first tooltip
        if self.active_tooltips:
            self._show_next_tooltip()
    
    def _create_level_1_tooltips(self, level_data):
        """Create tooltips for Level 1: Basic catapult mechanics."""
        # Tooltip 1: Catapult interaction
        catapult_pos = Vector2(self.screen_width // 2, self.screen_height - 150)
        tooltip1 = Tooltip(
            "Click and drag the catapult to aim. Pull back to increase power.",
            catapult_pos,
            "up",
            auto_dismiss_time=10.0
        )
        
        # Tooltip 2: Trajectory preview
        tooltip2 = Tooltip(
            "The dotted line shows where your stone will land. Use it to aim precisely.",
            Vector2(self.screen_width // 2, self.screen_height // 2),
            "down",
            auto_dismiss_time=10.0
        )
        
        # Tooltip 3: Ripple creation
        tooltip3 = Tooltip(
            "When the stone hits the water, it creates ripples that push the ball toward the target.",
            Vector2(self.screen_width // 2, 200),
            "down",
            auto_dismiss_time=10.0
        )
        
        self.active_tooltips = [tooltip1, tooltip2, tooltip3]
    
    def _create_level_2_tooltips(self, level_data):
        """Create tooltips for Level 2: Anti-ripple zones."""
        # Tooltip about anti-ripple obstruction
        if level_data.obstacles:
            obstacle_pos = level_data.obstacles[0].position
            tooltip = Tooltip(
                "Gray zones block ripples. Plan your stone placement to work around them.",
                obstacle_pos,
                "up",
                auto_dismiss_time=10.0
            )
            self.active_tooltips = [tooltip]
    
    def _create_level_3_tooltips(self, level_data):
        """Create tooltips for Level 3: Wall reflection."""
        # Tooltip about wall reflection
        if level_data.walls:
            wall_pos = level_data.walls[0].position
            tooltip = Tooltip(
                "Walls reflect ripples at an angle. Use them to redirect ripples and bounce the ball.",
                wall_pos,
                "up",
                auto_dismiss_time=10.0
            )
            self.active_tooltips = [tooltip]
    
    def _create_level_4_tooltips(self, level_data):
        """Create tooltips for Level 4: Whirlpools and current zones."""
        tooltips = []
        
        # Tooltip about whirlpools
        if level_data.whirlpools:
            whirlpool_pos = level_data.whirlpools[0].position
            tooltip1 = Tooltip(
                "Whirlpools pull the ball toward their center. If the ball gets too close, you lose!",
                whirlpool_pos,
                "up",
                auto_dismiss_time=10.0
            )
            tooltips.append(tooltip1)
        
        # Tooltip about current zones
        if level_data.current_zones:
            current_pos = level_data.current_zones[0].position
            tooltip2 = Tooltip(
                "Current zones push the ball in the direction of the arrows. Use them to your advantage.",
                current_pos,
                "up",
                auto_dismiss_time=10.0
            )
            tooltips.append(tooltip2)
        
        self.active_tooltips = tooltips
    
    def _show_next_tooltip(self):
        """Show the next tooltip in sequence."""
        if self.current_tooltip_index < len(self.active_tooltips):
            # Create "Got it!" button for current tooltip
            current_tooltip = self.active_tooltips[self.current_tooltip_index]
            
            # Position button near tooltip
            button_width = 80
            button_height = 30
            button_x = int(current_tooltip.position.x - button_width // 2)
            if current_tooltip.position.y > self.screen_height // 2:
                button_y = int(current_tooltip.position.y + 100)
            else:    
                button_y = int(current_tooltip.position.y + 40)
            
            self.got_it_button = TutorialButton(button_x, button_y, button_width, button_height, "Got it!")
    
    def is_tutorial_active(self) -> bool:
        """Check if tutorial is currently active."""
        return (self.current_level >= 1 and self.current_level <= 4 and 
                not self.tutorial_skipped and 
                self.current_tooltip_index < len(self.active_tooltips))
    
    def skip_tutorial(self):
        """Skip the tutorial."""
        self.tutorial_skipped = True
        self.active_tooltips = []
        self.got_it_button = None
    
    def dismiss_current_tooltip(self):
        """Dismiss the current tooltip and show next one."""
        if self.current_tooltip_index < len(self.active_tooltips):
            self.active_tooltips[self.current_tooltip_index].dismiss()
            self.current_tooltip_index += 1
            
            if self.current_tooltip_index < len(self.active_tooltips):
                self._show_next_tooltip()
            else:
                self.got_it_button = None
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update tutorial state."""
        if not self.is_tutorial_active():
            return
        
        # Update skip button
        self.skip_button.update(mouse_pos)
        
        # Update got it button
        if self.got_it_button:
            self.got_it_button.update(mouse_pos)
        
        # Check for auto-dismiss
        if self.current_tooltip_index < len(self.active_tooltips):
            current_tooltip = self.active_tooltips[self.current_tooltip_index]
            if current_tooltip.should_auto_dismiss():
                self.dismiss_current_tooltip()
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle mouse click on tutorial UI elements.
        
        Returns:
            True if click was handled by tutorial UI, False otherwise
        """
        if not self.is_tutorial_active():
            return False
        
        # Check skip button
        if self.skip_button.is_clicked(mouse_pos):
            self.skip_tutorial()
            return True
        
        # Check got it button
        if self.got_it_button and self.got_it_button.is_clicked(mouse_pos):
            self.dismiss_current_tooltip()
            return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """Render tutorial UI."""
        if not self.is_tutorial_active():
            return
        
        # Render current tooltip
        if self.current_tooltip_index < len(self.active_tooltips):
            current_tooltip = self.active_tooltips[self.current_tooltip_index]
            current_tooltip.render(screen)
        
        # Render skip button
        self.skip_button.render(screen)
        
        # Render got it button
        if self.got_it_button:
            self.got_it_button.render(screen)
