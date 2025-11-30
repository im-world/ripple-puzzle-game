"""
Fish Builder module for Ripple game.
Allows players to create custom fish designs and configure fish behavior.
"""

import pygame
import json
import copy
import os
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT


class DrawingTool:
    """Enumeration of drawing tools."""
    PENCIL = "pencil"
    ERASER = "eraser"
    FILL = "fill"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    LINE = "line"


class FishTemplate:
    """Fish template with design and behavior configuration."""
    
    def __init__(self, name="New Fish"):
        self.name = name
        self.enabled = True
        self.min_count = 0
        self.max_count = 4
        self.pixel_data = [[None for _ in range(32)] for _ in range(32)]  # 32x32 grid
        
        # Behavior properties
        self.behavior_pattern = "Random"  # Schooling, Solo, Circular Patrol, Random
        self.speed = 50.0  # pixels per second
        self.reaction_intensity = 1.0  # multiplier for ripple reactions
        self.size = 15.0  # display size in pixels
    
    def to_dict(self):
        """Convert template to dictionary for saving."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "min_count": self.min_count,
            "max_count": self.max_count,
            "pixel_data": self.pixel_data,
            "behavior_pattern": self.behavior_pattern,
            "speed": self.speed,
            "reaction_intensity": self.reaction_intensity,
            "size": self.size
        }
    
    @staticmethod
    def from_dict(data):
        """Create template from dictionary."""
        template = FishTemplate(data.get("name", "New Fish"))
        template.enabled = data.get("enabled", True)
        template.min_count = data.get("min_count", 0)
        template.max_count = data.get("max_count", 4)
        template.pixel_data = data.get("pixel_data", [[None for _ in range(32)] for _ in range(32)])
        template.behavior_pattern = data.get("behavior_pattern", "Random")
        template.speed = data.get("speed", 50.0)
        template.reaction_intensity = data.get("reaction_intensity", 1.0)
        template.size = data.get("size", 15.0)
        return template


class FishBuilder:
    """Fish builder interface for creating and configuring fish."""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Fish templates list
        self.templates = [
            FishTemplate("Default Fish 1"),
            FishTemplate("Default Fish 2"),
            FishTemplate("Default Fish 3")
        ]
        self.selected_template_index = 0
        
        # Behavior patterns available
        self.behavior_patterns = ["Schooling", "Solo", "Circular Patrol", "Random"]
        
        # Drawing state
        self.current_tool = DrawingTool.PENCIL
        self.current_color = (255, 140, 0)  # Orange
        self.is_drawing = False
        self.last_draw_pos = None
        
        # Undo/Redo stacks (4 steps each)
        self.undo_stack = []
        self.redo_stack = []
        
        # Color palette (16-24 colors)
        self.color_palette = [
            (255, 0, 0),      # Red
            (255, 140, 0),    # Orange
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 255, 255),    # Cyan
            (0, 0, 255),      # Blue
            (128, 0, 255),    # Purple
            (255, 0, 255),    # Magenta
            (255, 192, 203),  # Pink
            (165, 42, 42),    # Brown
            (128, 128, 128),  # Gray
            (0, 0, 0),        # Black
            (255, 255, 255),  # White
            (255, 215, 0),    # Gold
            (64, 224, 208),   # Turquoise
            (255, 105, 180),  # Hot Pink
            (144, 238, 144),  # Light Green
            (173, 216, 230),  # Light Blue
            (240, 230, 140),  # Khaki
            (221, 160, 221),  # Plum
        ]
        
        # UI Layout
        self.left_panel_width = 250
        self.right_panel_width = 300
        self.canvas_size = 512  # 32x32 grid with 16px per cell
        self.pixel_size = self.canvas_size // 32
        
        # Calculate positions
        self.canvas_x = self.left_panel_width + (SCREEN_WIDTH - self.left_panel_width - self.right_panel_width - self.canvas_size) // 2
        self.canvas_y = (SCREEN_HEIGHT - self.canvas_size) // 2
        
        # UI Rects
        self.canvas_rect = pygame.Rect(self.canvas_x, self.canvas_y, self.canvas_size, self.canvas_size)
        
        # Scrolling for template list
        self.template_scroll_offset = 0
        
        # Shape drawing state
        self.shape_start_pos = None
    
    def get_selected_template(self):
        """Get currently selected fish template."""
        if 0 <= self.selected_template_index < len(self.templates):
            return self.templates[self.selected_template_index]
        return None
    
    def save_state_for_undo(self):
        """Save current pixel data state for undo."""
        template = self.get_selected_template()
        if template:
            # Deep copy the pixel data
            state = copy.deepcopy(template.pixel_data)
            self.undo_stack.append(state)
            
            # Limit to 4 steps
            if len(self.undo_stack) > 4:
                self.undo_stack.pop(0)
            
            # Clear redo stack when new action is performed
            self.redo_stack.clear()
    
    def undo(self):
        """Undo last drawing action."""
        if self.undo_stack:
            template = self.get_selected_template()
            if template:
                # Save current state to redo stack
                self.redo_stack.append(copy.deepcopy(template.pixel_data))
                if len(self.redo_stack) > 4:
                    self.redo_stack.pop(0)
                
                # Restore previous state
                template.pixel_data = self.undo_stack.pop()
    
    def redo(self):
        """Redo last undone action."""
        if self.redo_stack:
            template = self.get_selected_template()
            if template:
                # Save current state to undo stack
                self.undo_stack.append(copy.deepcopy(template.pixel_data))
                if len(self.undo_stack) > 4:
                    self.undo_stack.pop(0)
                
                # Restore redo state
                template.pixel_data = self.redo_stack.pop()
    
    def clear_canvas(self):
        """Clear the drawing canvas."""
        template = self.get_selected_template()
        if template:
            self.save_state_for_undo()
            template.pixel_data = [[None for _ in range(32)] for _ in range(32)]
    
    def get_pixel_at_pos(self, mouse_pos):
        """Convert mouse position to pixel grid coordinates."""
        if not self.canvas_rect.collidepoint(mouse_pos):
            return None
        
        rel_x = mouse_pos[0] - self.canvas_x
        rel_y = mouse_pos[1] - self.canvas_y
        
        grid_x = rel_x // self.pixel_size
        grid_y = rel_y // self.pixel_size
        
        if 0 <= grid_x < 32 and 0 <= grid_y < 32:
            return (grid_x, grid_y)
        return None
    
    def draw_pixel(self, grid_pos):
        """Draw a pixel at grid position."""
        template = self.get_selected_template()
        if template and grid_pos:
            x, y = grid_pos
            if self.current_tool == DrawingTool.PENCIL:
                template.pixel_data[y][x] = self.current_color
            elif self.current_tool == DrawingTool.ERASER:
                template.pixel_data[y][x] = None
    
    def flood_fill(self, start_pos):
        """Flood fill algorithm for fill tool."""
        template = self.get_selected_template()
        if not template or not start_pos:
            return
        
        x, y = start_pos
        target_color = template.pixel_data[y][x]
        
        # Don't fill if already the same color
        if target_color == self.current_color:
            return
        
        # BFS flood fill
        queue = [(x, y)]
        visited = set()
        
        while queue:
            cx, cy = queue.pop(0)
            
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= 32 or cy < 0 or cy >= 32:
                continue
            if template.pixel_data[cy][cx] != target_color:
                continue
            
            visited.add((cx, cy))
            template.pixel_data[cy][cx] = self.current_color
            
            # Add neighbors
            queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
    
    def draw_shape(self, start_pos, end_pos):
        """Draw shape from start to end position."""
        template = self.get_selected_template()
        if not template or not start_pos or not end_pos:
            return
        
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        if self.current_tool == DrawingTool.CIRCLE:
            # Draw circle
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            radius = max(abs(x2 - x1), abs(y2 - y1)) // 2
            
            for y in range(32):
                for x in range(32):
                    dist_sq = (x - cx) ** 2 + (y - cy) ** 2
                    if dist_sq <= radius ** 2:
                        template.pixel_data[y][x] = self.current_color
        
        elif self.current_tool == DrawingTool.RECTANGLE:
            # Draw rectangle
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if 0 <= x < 32 and 0 <= y < 32:
                        template.pixel_data[y][x] = self.current_color
        
        elif self.current_tool == DrawingTool.TRIANGLE:
            # Draw triangle (three points: start, end, and third point)
            # For simplicity, use start as apex and end for base
            apex_x, apex_y = x1, y1
            base_x, base_y = x2, y2
            
            # Third point for base (mirror across vertical)
            base_x2 = apex_x - (base_x - apex_x)
            
            # Fill triangle using scanline
            for y in range(32):
                for x in range(32):
                    # Simple triangle fill (barycentric would be better but this is simpler)
                    if self._point_in_triangle(x, y, apex_x, apex_y, base_x, base_y, base_x2, base_y):
                        template.pixel_data[y][x] = self.current_color
        
        elif self.current_tool == DrawingTool.LINE:
            # Draw line using Bresenham's algorithm
            self._draw_line(x1, y1, x2, y2, template)
    
    def _point_in_triangle(self, px, py, x1, y1, x2, y2, x3, y3):
        """Check if point is inside triangle (simple method)."""
        def sign(p1x, p1y, p2x, p2y, p3x, p3y):
            return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)
        
        d1 = sign(px, py, x1, y1, x2, y2)
        d2 = sign(px, py, x2, y2, x3, y3)
        d3 = sign(px, py, x3, y3, x1, y1)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def _draw_line(self, x1, y1, x2, y2, template):
        """Draw line using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < 32 and 0 <= y < 32:
                template.pixel_data[y][x] = self.current_color
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def handle_mouse_down(self, mouse_pos):
        """Handle mouse button down event."""
        # Check toolbar buttons
        if self._check_toolbar_click(mouse_pos):
            return
        
        # Check left panel clicks (template selection, checkboxes, sliders)
        if self._check_left_panel_click(mouse_pos):
            return
        
        # Check right panel clicks (color palette)
        if self._check_right_panel_click(mouse_pos):
            return
        
        # Check if clicking on canvas
        if self.canvas_rect.collidepoint(mouse_pos):
            pixel_pos = self.get_pixel_at_pos(mouse_pos)
            
            if self.current_tool in [DrawingTool.PENCIL, DrawingTool.ERASER]:
                self.save_state_for_undo()
                self.is_drawing = True
                self.draw_pixel(pixel_pos)
                self.last_draw_pos = pixel_pos
            
            elif self.current_tool == DrawingTool.FILL:
                self.save_state_for_undo()
                self.flood_fill(pixel_pos)
            
            elif self.current_tool in [DrawingTool.CIRCLE, DrawingTool.RECTANGLE, DrawingTool.TRIANGLE, DrawingTool.LINE]:
                self.shape_start_pos = pixel_pos
                self.is_drawing = True
    
    def handle_mouse_up(self, mouse_pos):
        """Handle mouse button up event."""
        if self.is_drawing:
            if self.current_tool in [DrawingTool.CIRCLE, DrawingTool.RECTANGLE, DrawingTool.TRIANGLE, DrawingTool.LINE]:
                pixel_pos = self.get_pixel_at_pos(mouse_pos)
                if self.shape_start_pos and pixel_pos:
                    self.save_state_for_undo()
                    self.draw_shape(self.shape_start_pos, pixel_pos)
                self.shape_start_pos = None
            
            self.is_drawing = False
            self.last_draw_pos = None
    
    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion event."""
        if self.is_drawing and self.current_tool in [DrawingTool.PENCIL, DrawingTool.ERASER]:
            pixel_pos = self.get_pixel_at_pos(mouse_pos)
            if pixel_pos and pixel_pos != self.last_draw_pos:
                self.draw_pixel(pixel_pos)
                self.last_draw_pos = pixel_pos
    
    def handle_key_down(self, event):
        """Handle keyboard input."""
        if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.undo()
        elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.redo()
    
    def _check_toolbar_click(self, mouse_pos):
        """Check if toolbar button was clicked."""
        toolbar_height = 60
        
        # Drawing tool buttons
        tools = [
            (DrawingTool.PENCIL, "Pencil"),
            (DrawingTool.ERASER, "Eraser"),
            (DrawingTool.FILL, "Fill"),
            (DrawingTool.CIRCLE, "Circle"),
            (DrawingTool.RECTANGLE, "Rect"),
            (DrawingTool.TRIANGLE, "Triangle"),
            (DrawingTool.LINE, "Line")
        ]
        
        x_offset = 20
        button_width = 70
        button_height = 35
        
        for tool, label in tools:
            button_rect = pygame.Rect(x_offset, SCREEN_HEIGHT - 50, button_width, button_height)
            if button_rect.collidepoint(mouse_pos):
                self.current_tool = tool
                return True
            x_offset += button_width + 10
        
        # Action buttons
        action_buttons = [
            ("Clear", self.clear_canvas),
            ("Undo", self.undo),
            ("Redo", self.redo)
        ]
        x_offset = SCREEN_WIDTH - 250
        
        for label, action in action_buttons:
            button_rect = pygame.Rect(x_offset, SCREEN_HEIGHT - 50, 70, button_height)
            if button_rect.collidepoint(mouse_pos):
                action()
                return True
            x_offset += 80
        
        return False
    
    def _check_left_panel_click(self, mouse_pos):
        """Check if left panel element was clicked."""
        y_offset = 120
        
        for i, template in enumerate(self.templates):
            item_rect = pygame.Rect(20, y_offset, self.left_panel_width - 40, 60)
            
            if item_rect.collidepoint(mouse_pos):
                # Check if clicking on checkbox
                checkbox_rect = pygame.Rect(30, y_offset + 28, 15, 15)
                if checkbox_rect.collidepoint(mouse_pos):
                    template.enabled = not template.enabled
                else:
                    # Select this template
                    self.selected_template_index = i
                return True
            
            y_offset += 70
        
        return False
    
    def _check_right_panel_click(self, mouse_pos):
        """Check if right panel element was clicked (properties and color palette)."""
        panel_x = SCREEN_WIDTH - self.right_panel_width - 10
        template = self.get_selected_template()
        
        if template:
            # Behavior pattern dropdown (y_offset = 110)
            behavior_rect = pygame.Rect(panel_x + 10, 110, self.right_panel_width - 30, 20)
            if behavior_rect.collidepoint(mouse_pos):
                # Cycle through behavior patterns
                current_index = self.behavior_patterns.index(template.behavior_pattern)
                template.behavior_pattern = self.behavior_patterns[(current_index + 1) % len(self.behavior_patterns)]
                return True
            
            # Speed slider (y_offset = 135)
            speed_slider_rect = pygame.Rect(panel_x + 80, 135, 150, 20)
            if speed_slider_rect.collidepoint(mouse_pos):
                # Calculate speed from mouse position (20-100 px/s)
                rel_x = mouse_pos[0] - speed_slider_rect.x
                template.speed = 20 + (rel_x / speed_slider_rect.width) * 80
                template.speed = max(20, min(100, template.speed))
                return True
            
            # Reaction intensity slider (y_offset = 160)
            reaction_slider_rect = pygame.Rect(panel_x + 80, 160, 150, 20)
            if reaction_slider_rect.collidepoint(mouse_pos):
                # Calculate reaction intensity from mouse position (0.5-2.0x)
                rel_x = mouse_pos[0] - reaction_slider_rect.x
                template.reaction_intensity = 0.5 + (rel_x / reaction_slider_rect.width) * 1.5
                template.reaction_intensity = max(0.5, min(2.0, template.reaction_intensity))
                return True
            
            # Size slider (y_offset = 185)
            size_slider_rect = pygame.Rect(panel_x + 80, 185, 150, 20)
            if size_slider_rect.collidepoint(mouse_pos):
                # Calculate size from mouse position (10-30 px)
                rel_x = mouse_pos[0] - size_slider_rect.x
                template.size = 10 + (rel_x / size_slider_rect.width) * 20
                template.size = max(10, min(30, template.size))
                return True
            
            # Save Fish button (y_offset = 220)
            save_button_rect = pygame.Rect(panel_x + 10, 220, 130, 35)
            if save_button_rect.collidepoint(mouse_pos):
                self._save_fish_config()
                return True
            
            # Delete Fish button (y_offset = 220)
            delete_button_rect = pygame.Rect(panel_x + 150, 220, 130, 35)
            if delete_button_rect.collidepoint(mouse_pos):
                self._delete_fish()
                return True
        
        # Color palette starts at y_offset
        y_offset = 270
        
        swatch_size = 35
        spacing = 10
        cols = 4
        
        for i, color in enumerate(self.color_palette):
            row = i // cols
            col = i % cols
            
            swatch_x = panel_x + 10 + col * (swatch_size + spacing)
            swatch_y = y_offset + row * (swatch_size + spacing)
            
            swatch_rect = pygame.Rect(swatch_x, swatch_y, swatch_size, swatch_size)
            
            if swatch_rect.collidepoint(mouse_pos):
                self.current_color = color
                return True
        
        # Template selector at bottom
        template_selector_y = SCREEN_HEIGHT - 120
        for i in range(len(self.templates)):
            template_rect = pygame.Rect(panel_x + 10 + i * 70, template_selector_y, 60, 60)
            if template_rect.collidepoint(mouse_pos):
                self.selected_template_index = i
                return True
        
        return False
    
    def draw(self):
        """Draw the fish builder interface."""
        # Clear screen
        self.screen.fill((220, 230, 240))
        
        # Draw title
        font_title = pygame.font.SysFont('Arial', 36, bold=True)
        title_surface = font_title.render("Fish Builder", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_surface, title_rect)
        
        # Draw panels
        self._draw_left_panel()
        self._draw_canvas()
        self._draw_right_panel()
        self._draw_toolbar()
    
    def _draw_left_panel(self):
        """Draw left panel with fish template list."""
        panel_rect = pygame.Rect(10, 70, self.left_panel_width - 20, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, (240, 245, 250), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 150), panel_rect, 2, border_radius=8)
        
        # Panel title
        font_label = pygame.font.SysFont('Arial', 20, bold=True)
        label_surface = font_label.render("Fish Templates", True, (70, 70, 70))
        self.screen.blit(label_surface, (20, 80))
        
        # Draw template list
        font_item = pygame.font.SysFont('Arial', 16)
        y_offset = 120
        
        for i, template in enumerate(self.templates):
            item_rect = pygame.Rect(20, y_offset, self.left_panel_width - 40, 60)
            
            # Highlight selected template
            if i == self.selected_template_index:
                pygame.draw.rect(self.screen, (180, 200, 220), item_rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), item_rect, border_radius=5)
            
            pygame.draw.rect(self.screen, (150, 150, 150), item_rect, 1, border_radius=5)
            
            # Template name
            name_surface = font_item.render(template.name, True, (50, 50, 50))
            self.screen.blit(name_surface, (30, y_offset + 5))
            
            # Enable/disable checkbox
            checkbox_rect = pygame.Rect(30, y_offset + 28, 15, 15)
            pygame.draw.rect(self.screen, (255, 255, 255), checkbox_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), checkbox_rect, 2)
            
            if template.enabled:
                # Draw checkmark
                pygame.draw.line(self.screen, (0, 150, 0), 
                               (checkbox_rect.left + 3, checkbox_rect.centery),
                               (checkbox_rect.centerx, checkbox_rect.bottom - 3), 3)
                pygame.draw.line(self.screen, (0, 150, 0),
                               (checkbox_rect.centerx, checkbox_rect.bottom - 3),
                               (checkbox_rect.right - 3, checkbox_rect.top + 3), 3)
            
            enabled_text = font_item.render("Enabled", True, (70, 70, 70))
            self.screen.blit(enabled_text, (50, y_offset + 26))
            
            # Min/Max count sliders (simplified display)
            count_text = f"Count: {template.min_count}-{template.max_count}"
            count_surface = font_item.render(count_text, True, (70, 70, 70))
            self.screen.blit(count_surface, (30, y_offset + 45))
            
            y_offset += 70
    
    def _draw_canvas(self):
        """Draw center drawing canvas with pixel grid."""
        # Draw canvas background
        pygame.draw.rect(self.screen, (255, 255, 255), self.canvas_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.canvas_rect, 2)
        
        # Draw grid lines
        for i in range(33):
            # Vertical lines
            x = self.canvas_x + i * self.pixel_size
            pygame.draw.line(self.screen, (220, 220, 220), 
                           (x, self.canvas_y), 
                           (x, self.canvas_y + self.canvas_size))
            
            # Horizontal lines
            y = self.canvas_y + i * self.pixel_size
            pygame.draw.line(self.screen, (220, 220, 220),
                           (self.canvas_x, y),
                           (self.canvas_x + self.canvas_size, y))
        
        # Draw pixels
        template = self.get_selected_template()
        if template:
            for y in range(32):
                for x in range(32):
                    color = template.pixel_data[y][x]
                    if color:
                        pixel_rect = pygame.Rect(
                            self.canvas_x + x * self.pixel_size + 1,
                            self.canvas_y + y * self.pixel_size + 1,
                            self.pixel_size - 1,
                            self.pixel_size - 1
                        )
                        pygame.draw.rect(self.screen, color, pixel_rect)
        
        # Draw shape preview if drawing shape
        if self.is_drawing and self.shape_start_pos and self.current_tool in [DrawingTool.CIRCLE, DrawingTool.RECTANGLE, DrawingTool.TRIANGLE, DrawingTool.LINE]:
            mouse_pos = pygame.mouse.get_pos()
            end_pos = self.get_pixel_at_pos(mouse_pos)
            if end_pos:
                self._draw_shape_preview(self.shape_start_pos, end_pos)
    
    def _draw_shape_preview(self, start_pos, end_pos):
        """Draw preview of shape being drawn."""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Convert to screen coordinates
        screen_x1 = self.canvas_x + x1 * self.pixel_size + self.pixel_size // 2
        screen_y1 = self.canvas_y + y1 * self.pixel_size + self.pixel_size // 2
        screen_x2 = self.canvas_x + x2 * self.pixel_size + self.pixel_size // 2
        screen_y2 = self.canvas_y + y2 * self.pixel_size + self.pixel_size // 2
        
        if self.current_tool == DrawingTool.LINE:
            pygame.draw.line(self.screen, self.current_color, 
                           (screen_x1, screen_y1), (screen_x2, screen_y2), 2)
        
        elif self.current_tool == DrawingTool.RECTANGLE:
            width = abs(screen_x2 - screen_x1)
            height = abs(screen_y2 - screen_y1)
            rect = pygame.Rect(min(screen_x1, screen_x2), min(screen_y1, screen_y2), width, height)
            pygame.draw.rect(self.screen, self.current_color, rect, 2)
        
        elif self.current_tool == DrawingTool.CIRCLE:
            cx = (screen_x1 + screen_x2) // 2
            cy = (screen_y1 + screen_y2) // 2
            radius = max(abs(screen_x2 - screen_x1), abs(screen_y2 - screen_y1)) // 2
            if radius > 0:
                pygame.draw.circle(self.screen, self.current_color, (cx, cy), radius, 2)
    
    def _draw_right_panel(self):
        """Draw right panel with properties and color palette."""
        panel_x = SCREEN_WIDTH - self.right_panel_width - 10
        panel_rect = pygame.Rect(panel_x, 70, self.right_panel_width - 10, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, (240, 245, 250), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 150), panel_rect, 2, border_radius=8)
        
        font_label = pygame.font.SysFont('Arial', 18, bold=True)
        font_text = pygame.font.SysFont('Arial', 14)
        font_small = pygame.font.SysFont('Arial', 12)
        
        y_offset = 80
        
        # Properties section
        props_label = font_label.render("Properties", True, (70, 70, 70))
        self.screen.blit(props_label, (panel_x + 10, y_offset))
        y_offset += 30
        
        template = self.get_selected_template()
        if template:
            # Behavior pattern (clickable dropdown)
            behavior_text = f"Behavior: {template.behavior_pattern}"
            behavior_surface = font_text.render(behavior_text, True, (50, 50, 50))
            behavior_rect = pygame.Rect(panel_x + 10, y_offset, self.right_panel_width - 30, 20)
            pygame.draw.rect(self.screen, (220, 230, 240), behavior_rect, border_radius=3)
            pygame.draw.rect(self.screen, (150, 150, 150), behavior_rect, 1, border_radius=3)
            self.screen.blit(behavior_surface, (panel_x + 15, y_offset + 2))
            y_offset += 25
            
            # Speed slider
            speed_label = font_text.render("Speed:", True, (50, 50, 50))
            self.screen.blit(speed_label, (panel_x + 10, y_offset))
            speed_slider_rect = pygame.Rect(panel_x + 80, y_offset, 150, 20)
            pygame.draw.rect(self.screen, (200, 200, 200), speed_slider_rect, border_radius=3)
            # Draw slider fill
            fill_width = int(((template.speed - 20) / 80) * 150)
            fill_rect = pygame.Rect(panel_x + 80, y_offset, fill_width, 20)
            pygame.draw.rect(self.screen, (100, 150, 200), fill_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), speed_slider_rect, 2, border_radius=3)
            speed_value = font_small.render(f"{template.speed:.0f}", True, (50, 50, 50))
            self.screen.blit(speed_value, (panel_x + 235, y_offset + 3))
            y_offset += 25
            
            # Reaction intensity slider
            reaction_label = font_text.render("Reaction:", True, (50, 50, 50))
            self.screen.blit(reaction_label, (panel_x + 10, y_offset))
            reaction_slider_rect = pygame.Rect(panel_x + 80, y_offset, 150, 20)
            pygame.draw.rect(self.screen, (200, 200, 200), reaction_slider_rect, border_radius=3)
            # Draw slider fill
            fill_width = int(((template.reaction_intensity - 0.5) / 1.5) * 150)
            fill_rect = pygame.Rect(panel_x + 80, y_offset, fill_width, 20)
            pygame.draw.rect(self.screen, (100, 150, 200), fill_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), reaction_slider_rect, 2, border_radius=3)
            reaction_value = font_small.render(f"{template.reaction_intensity:.1f}x", True, (50, 50, 50))
            self.screen.blit(reaction_value, (panel_x + 235, y_offset + 3))
            y_offset += 25
            
            # Size slider
            size_label = font_text.render("Size:", True, (50, 50, 50))
            self.screen.blit(size_label, (panel_x + 10, y_offset))
            size_slider_rect = pygame.Rect(panel_x + 80, y_offset, 150, 20)
            pygame.draw.rect(self.screen, (200, 200, 200), size_slider_rect, border_radius=3)
            # Draw slider fill
            fill_width = int(((template.size - 10) / 20) * 150)
            fill_rect = pygame.Rect(panel_x + 80, y_offset, fill_width, 20)
            pygame.draw.rect(self.screen, (100, 150, 200), fill_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), size_slider_rect, 2, border_radius=3)
            size_value = font_small.render(f"{template.size:.0f}", True, (50, 50, 50))
            self.screen.blit(size_value, (panel_x + 235, y_offset + 3))
            y_offset += 35
            
            # Save and Delete buttons
            save_button_rect = pygame.Rect(panel_x + 10, y_offset, 130, 35)
            pygame.draw.rect(self.screen, (100, 180, 100), save_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (80, 140, 80), save_button_rect, 2, border_radius=5)
            save_text = font_text.render("Save Fish", True, (255, 255, 255))
            save_text_rect = save_text.get_rect(center=save_button_rect.center)
            self.screen.blit(save_text, save_text_rect)
            
            delete_button_rect = pygame.Rect(panel_x + 150, y_offset, 130, 35)
            pygame.draw.rect(self.screen, (200, 100, 100), delete_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (160, 80, 80), delete_button_rect, 2, border_radius=5)
            delete_text = font_text.render("Delete Fish", True, (255, 255, 255))
            delete_text_rect = delete_text.get_rect(center=delete_button_rect.center)
            self.screen.blit(delete_text, delete_text_rect)
            y_offset += 50
        
        # Color palette section
        palette_label = font_label.render("Color Palette", True, (70, 70, 70))
        self.screen.blit(palette_label, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Draw color swatches (4 columns)
        swatch_size = 35
        spacing = 10
        cols = 4
        
        for i, color in enumerate(self.color_palette):
            row = i // cols
            col = i % cols
            
            swatch_x = panel_x + 10 + col * (swatch_size + spacing)
            swatch_y = y_offset + row * (swatch_size + spacing)
            
            swatch_rect = pygame.Rect(swatch_x, swatch_y, swatch_size, swatch_size)
            pygame.draw.rect(self.screen, color, swatch_rect)
            
            # Highlight selected color
            if color == self.current_color:
                pygame.draw.rect(self.screen, (255, 215, 0), swatch_rect, 3)
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), swatch_rect, 2)
        
        # Template selector at bottom
        y_offset = SCREEN_HEIGHT - 120
        selector_label = font_label.render("Templates", True, (70, 70, 70))
        self.screen.blit(selector_label, (panel_x + 10, y_offset - 25))
        
        for i, tmpl in enumerate(self.templates):
            template_rect = pygame.Rect(panel_x + 10 + i * 70, y_offset, 60, 60)
            
            # Highlight selected template
            if i == self.selected_template_index:
                pygame.draw.rect(self.screen, (100, 150, 200), template_rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, (220, 230, 240), template_rect, border_radius=5)
            
            pygame.draw.rect(self.screen, (100, 100, 100), template_rect, 2, border_radius=5)
            
            # Draw mini preview of fish (simplified)
            preview_size = 50
            preview_rect = pygame.Rect(template_rect.x + 5, template_rect.y + 5, preview_size, preview_size)
            
            # Draw a few pixels from the template as preview
            for py in range(0, 32, 4):
                for px in range(0, 32, 4):
                    color = tmpl.pixel_data[py][px]
                    if color:
                        pixel_x = preview_rect.x + (px * preview_size) // 32
                        pixel_y = preview_rect.y + (py * preview_size) // 32
                        pixel_size = max(1, preview_size // 8)
                        pygame.draw.rect(self.screen, color, 
                                       pygame.Rect(pixel_x, pixel_y, pixel_size, pixel_size))
    
    def _save_fish_config(self):
        """Save fish configuration to file."""
        try:
            config_data = {
                "templates": [template.to_dict() for template in self.templates]
            }
            
            # Save to fish_config.json
            with open("fish_config.json", "w") as f:
                json.dump(config_data, f, indent=2)
            
            print("Fish configuration saved successfully!")
        except Exception as e:
            print(f"Error saving fish configuration: {e}")
    
    def _delete_fish(self):
        """Delete the currently selected fish template."""
        if len(self.templates) > 1:  # Keep at least one template
            del self.templates[self.selected_template_index]
            self.selected_template_index = min(self.selected_template_index, len(self.templates) - 1)
            print(f"Fish template deleted. {len(self.templates)} templates remaining.")
        else:
            print("Cannot delete the last fish template!")
    
    def load_fish_config(self):
        """Load fish configuration from file."""
        try:
            if os.path.exists("fish_config.json"):
                with open("fish_config.json", "r") as f:
                    config_data = json.load(f)
                
                if "templates" in config_data:
                    self.templates = [FishTemplate.from_dict(t) for t in config_data["templates"]]
                    self.selected_template_index = 0
                    print("Fish configuration loaded successfully!")
        except Exception as e:
            print(f"Error loading fish configuration: {e}")
    
    def _draw_toolbar(self):
        """Draw toolbar with drawing tools and action buttons."""
        toolbar_height = 60
        toolbar_rect = pygame.Rect(0, SCREEN_HEIGHT - toolbar_height, SCREEN_WIDTH, toolbar_height)
        pygame.draw.rect(self.screen, (200, 210, 220), toolbar_rect)
        pygame.draw.line(self.screen, (150, 150, 150), 
                        (0, SCREEN_HEIGHT - toolbar_height), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - toolbar_height), 2)
        
        font_button = pygame.font.SysFont('Arial', 14)
        
        # Drawing tools
        tools = [
            (DrawingTool.PENCIL, "Pencil"),
            (DrawingTool.ERASER, "Eraser"),
            (DrawingTool.FILL, "Fill"),
            (DrawingTool.CIRCLE, "Circle"),
            (DrawingTool.RECTANGLE, "Rect"),
            (DrawingTool.TRIANGLE, "Triangle"),
            (DrawingTool.LINE, "Line")
        ]
        
        x_offset = 20
        button_width = 70
        button_height = 35
        
        for tool, label in tools:
            button_rect = pygame.Rect(x_offset, SCREEN_HEIGHT - 50, button_width, button_height)
            
            # Highlight selected tool
            if tool == self.current_tool:
                pygame.draw.rect(self.screen, (100, 150, 200), button_rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, (180, 190, 200), button_rect, border_radius=5)
            
            pygame.draw.rect(self.screen, (100, 100, 100), button_rect, 2, border_radius=5)
            
            # Button text
            text_surface = font_button.render(label, True, (255, 255, 255) if tool == self.current_tool else (50, 50, 50))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            x_offset += button_width + 10
        
        # Action buttons (right side)
        action_buttons = ["Clear", "Undo", "Redo"]
        x_offset = SCREEN_WIDTH - 250
        
        for label in action_buttons:
            button_rect = pygame.Rect(x_offset, SCREEN_HEIGHT - 50, 70, button_height)
            pygame.draw.rect(self.screen, (180, 190, 200), button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), button_rect, 2, border_radius=5)
            
            text_surface = font_button.render(label, True, (50, 50, 50))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            x_offset += 80


def load_global_fish_config():
    """
    Load global fish configuration from file.
    Returns list of FishTemplate objects.
    """
    try:
        if os.path.exists("fish_config.json"):
            with open("fish_config.json", "r") as f:
                config_data = json.load(f)
            
            if "templates" in config_data:
                return [FishTemplate.from_dict(t) for t in config_data["templates"]]
    except Exception as e:
        print(f"Error loading global fish configuration: {e}")
    
    # Return default templates if loading fails
    return [
        FishTemplate("Default Fish 1"),
        FishTemplate("Default Fish 2"),
        FishTemplate("Default Fish 3")
    ]
