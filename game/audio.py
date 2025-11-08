"""
Audio manager for Ripple game
Handles sound effects and background music playback
"""

import os
import pygame
from typing import Dict, Optional


class AudioManager:
    """Manages all audio playback including sound effects and music."""
    
    def __init__(self, sound_volume: float = 0.7, music_volume: float = 0.25):
        """
        Initialize the audio manager.
        
        Args:
            sound_volume: Volume for sound effects (0.0 to 1.0)
            music_volume: Volume for background music (0.0 to 1.0)
        """
        # Initialize Pygame mixer with appropriate settings
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Volume settings
        self._sound_volume = sound_volume
        self._music_volume = music_volume
        
        # Sound effects dictionary
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Track playing sounds for limiting simultaneous instances
        self.playing_sounds: Dict[str, list] = {}
        
        # Maximum simultaneous instances per sound type
        self.max_instances = {
            'splash': 3,
            'ripple': 3,
            'launch': 2
        }
        
        # Mute flags
        self._sound_muted = False
        self._music_muted = False
        
        # Track if music is loaded
        self._music_loaded = False
    
    def load_sound_effects(self, sounds_dir: str = "assets"):
        """
        Load all sound effect files.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        # Define sound files to load
        sound_files = {
            'launch': 'launch.wav',
            'splash': 'splash.wav',
            'ripple': 'ripple.wav',
            'ball_move': 'ball_move.wav',
            'level_complete': 'level_complete.wav',
            'click': 'click.wav'
        }
        
        # Load each sound file
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self._sound_volume)
                    self.sounds[sound_name] = sound
                    self.playing_sounds[sound_name] = []
                else:
                    # Create a silent placeholder sound if file doesn't exist
                    print(f"Warning: Sound file not found: {filepath}")
                    # Create minimal silent sound (1 sample at 0 amplitude)
                    sound = pygame.mixer.Sound(buffer=bytes([0] * 4))
                    sound.set_volume(0)
                    self.sounds[sound_name] = sound
                    self.playing_sounds[sound_name] = []
            except Exception as e:
                print(f"Error loading sound {sound_name}: {e}")
                # Create silent placeholder on error
                sound = pygame.mixer.Sound(buffer=bytes([0] * 4))
                sound.set_volume(0)
                self.sounds[sound_name] = sound
                self.playing_sounds[sound_name] = []
    
    def load_music(self, music_file: str = "assets/background.ogg"):
        """
        Load background music file.
        
        Args:
            music_file: Path to music file
        """
        self._music_loaded = False
        
        # Try WAV first (more reliable for placeholder)
        wav_file = music_file.replace('.ogg', '.wav').replace('.mp3', '.wav')
        if os.path.exists(wav_file):
            try:
                pygame.mixer.music.load(wav_file)
                pygame.mixer.music.set_volume(self._music_volume)
                self._music_loaded = True
                print(f"Loaded music: {wav_file}")
                return
            except Exception as e:
                print(f"Error loading WAV music: {e}")
        
        # Try original file
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self._music_volume)
                self._music_loaded = True
                print(f"Loaded music: {music_file}")
            else:
                print(f"Warning: Music file not found: {music_file}")
        except Exception as e:
            print(f"Error loading music: {e}")
    
    def play_sound(self, sound_name: str, limit_instances: bool = True) -> Optional[pygame.mixer.Channel]:
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play
            limit_instances: Whether to limit simultaneous instances
            
        Returns:
            Channel playing the sound, or None if not played
        """
        if self._sound_muted or sound_name not in self.sounds:
            return None
        
        # Check if we should limit instances
        if limit_instances and sound_name in self.max_instances:
            # Clean up finished channels
            self.playing_sounds[sound_name] = [
                ch for ch in self.playing_sounds[sound_name] if ch.get_busy()
            ]
            
            # Check if we've reached the limit
            max_count = self.max_instances[sound_name]
            if len(self.playing_sounds[sound_name]) >= max_count:
                return None
        
        # Play the sound
        try:
            channel = self.sounds[sound_name].play()
            if channel and sound_name in self.playing_sounds:
                self.playing_sounds[sound_name].append(channel)
            return channel
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
            return None
    
    def play_music(self, loops: int = -1):
        """
        Start playing background music.
        
        Args:
            loops: Number of times to loop (-1 for infinite)
        """
        if self._music_loaded and not self._music_muted:
            try:
                pygame.mixer.music.play(loops=loops)
            except Exception as e:
                print(f"Error playing music: {e}")
    
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause background music."""
        pygame.mixer.music.unpause()
    
    def set_sound_volume(self, volume: float):
        """
        Set volume for all sound effects.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self._sound_volume if not self._sound_muted else 0.0)
    
    def set_music_volume(self, volume: float):
        """
        Set volume for background music.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._music_volume if not self._music_muted else 0.0)
    
    def get_sound_volume(self) -> float:
        """Get current sound effects volume."""
        return self._sound_volume
    
    def get_music_volume(self) -> float:
        """Get current music volume."""
        return self._music_volume
    
    def toggle_sound_mute(self):
        """Toggle sound effects mute."""
        self._sound_muted = not self._sound_muted
        for sound in self.sounds.values():
            sound.set_volume(self._sound_volume if not self._sound_muted else 0.0)
    
    def toggle_music_mute(self):
        """Toggle music mute."""
        self._music_muted = not self._music_muted
        pygame.mixer.music.set_volume(self._music_volume if not self._music_muted else 0.0)
    
    def is_sound_muted(self) -> bool:
        """Check if sound effects are muted."""
        return self._sound_muted
    
    def is_music_muted(self) -> bool:
        """Check if music is muted."""
        return self._music_muted
