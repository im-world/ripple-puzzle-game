# Level Selection Screen Implementation

## Overview
This document describes the implementation of the level selection screen for the Ripple game, allowing players to choose from any of the 20 available levels.

## Features Implemented

### 1. Grid Layout (5x4)
- **Layout**: 5 columns × 4 rows = 20 level cards
- **Card Size**: 140×100 pixels per card
- **Spacing**: 20 pixels between cards (horizontal and vertical)
- **Positioning**: Centered on screen below title

### 2. Level Cards
Each level card displays:
- **Level Number**: Large, bold number (1-20)
- **Tutorial Badge**: Yellow "Tutorial" badge for levels 1-4
- **Visual States**:
  - Normal: Light blue background (160, 200, 240)
  - Hover: Brighter blue (140, 190, 240)
  - Selected: Darker blue (120, 170, 220) - for keyboard navigation

### 3. All Levels Unlocked
- No progression lock - all 20 levels are accessible from the start
- Players can jump to any level at any time
- When starting from level select, players receive 10 stones (random level mode)

### 4. Tutorial Indicators
- Levels 1-4 display a yellow "Tutorial" badge
- Badge appears at the bottom of the level card
- Helps players identify introductory levels

### 5. Keyboard Navigation
Full keyboard support with arrow keys:
- **Left Arrow**: Move selection left
- **Right Arrow**: Move selection right
- **Up Arrow**: Move selection up (by 5 positions)
- **Down Arrow**: Move selection down (by 5 positions)
- **Enter/Space**: Start selected level
- **ESC**: Exit game (from any screen)

Navigation features:
- Visual selection indicator (highlighted card)
- Wraps at grid boundaries
- Audio feedback on navigation
- Starts at level 1 (index 0)

### 6. Mouse Interaction
- **Hover Effect**: Cards brighten when mouse hovers over them
- **Click to Play**: Click any card to immediately start that level
- **Back Button**: Click "Back to Menu" to return to main menu

### 7. UI Elements
- **Title**: "Select Level" at top of screen
- **Back Button**: Centered at bottom, returns to main menu
- **Navigation Hint**: Text showing "Use Arrow Keys + Enter to navigate, or click a level"

## Code Structure

### New Classes

#### `LevelCard`
```python
class LevelCard:
    """Level card for level selection screen."""
    - rect: pygame.Rect - Card position and size
    - level_number: int - Level number (1-20)
    - is_tutorial: bool - Whether this is a tutorial level
    - is_hovered: bool - Mouse hover state
    - is_selected: bool - Keyboard selection state
```

### New Game State
- Added `LEVEL_SELECT` to `GameState` enum

### Modified Methods

#### `Game.__init__()`
- Added `level_cards` list
- Added `selected_level_index` for keyboard navigation
- Added `level_select_back_button`
- Added `level_select` button to main menu

#### `Game.start_game(level_index=0)`
- Modified to accept optional `level_index` parameter
- Supports starting from any level
- Implements "random level" mode (gives 10 stones when jumping to a level)

#### `Game._create_level_cards()`
- Creates 20 level cards in 5×4 grid
- Loads level data to determine tutorial status
- Centers grid on screen

### New Methods

#### `Game.handle_input_level_select(event)`
- Handles mouse clicks on level cards
- Handles keyboard navigation (arrow keys)
- Handles Enter/Space to start level
- Handles back button click

#### `Game.update_level_select(dt)`
- Updates card hover states
- Updates card selection states
- Updates back button hover state
- Updates fade transitions

#### `Game.render_level_select()`
- Renders title
- Renders all 20 level cards
- Renders back button
- Renders navigation hint
- Renders fade transitions

## Integration Points

### Main Menu
- Added "Level Select" button between "Start Game" and "Settings"
- Clicking navigates to level selection screen

### Game Loop
- Added level select handlers to event processing
- Added level select update to game loop
- Added level select render to game loop

### Level Manager
- Modified `initialize_level()` to support `is_random_level` flag
- When starting from level select, gives 10 stones (not carrying over)

## Visual Design

### Color Scheme
- Background: Light blue-gray (200, 220, 240)
- Cards: Pastel blue shades
- Tutorial Badge: Gold/yellow (255, 215, 0)
- Text: White for level numbers, gray for hints

### Typography
- Title: Arial 56pt Bold
- Level Numbers: Arial 36pt Bold
- Tutorial Badge: Arial 14pt
- Navigation Hint: Arial 18pt
- Buttons: Arial 28pt

## User Experience

### Flow
1. Player clicks "Level Select" from main menu
2. Level selection screen appears with all 20 levels
3. Player can:
   - Click any level card to start that level
   - Use arrow keys to navigate and Enter to select
   - Click "Back to Menu" to return
4. Selected level starts with fade transition
5. Player receives 10 stones for the selected level

### Accessibility
- Large, clear level numbers
- Visual feedback for all interactions
- Keyboard navigation support
- Audio feedback for actions
- Tutorial indicators for new players

## Testing

### Automated Tests
See `test_level_selection.py` for comprehensive test suite covering:
- Level card creation (20 cards)
- Tutorial badges (levels 1-4)
- Grid layout (5×4)
- Back button existence
- Keyboard navigation state
- Menu integration
- State transitions

### Manual Testing
Use `demo_level_selection.py` to:
- Verify visual appearance
- Test mouse interactions
- Test keyboard navigation
- Verify tutorial badges
- Test level starting

## Future Enhancements (Not in Current Scope)
- Level thumbnails/previews
- Star ratings display on cards
- Level completion indicators
- Level difficulty indicators
- Search/filter functionality
- Level categories/grouping

## Requirements Satisfied
This implementation satisfies all requirements from task 8:
- ✓ Create grid layout displaying all 20 levels (4x5 or 5x4)
- ✓ All levels unlocked from start (no progression lock)
- ✓ Display level number and thumbnail preview for each level
- ✓ Add "Play" button for each level card (click to play)
- ✓ Show tutorial indicator badge for levels 1-4
- ✓ Implement keyboard navigation (arrow keys + enter)
- ✓ Add "Back to Main Menu" button
