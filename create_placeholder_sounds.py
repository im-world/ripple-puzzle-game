"""
Script to create placeholder sound files for the Ripple game.
These are minimal silent WAV files that can be replaced with actual sounds later.
"""

import wave
import struct
import os


def create_silent_wav(filename, duration_ms=100, frequency=44100):
    """
    Create a minimal silent WAV file.
    
    Args:
        filename: Output filename
        duration_ms: Duration in milliseconds
        frequency: Sample rate in Hz
    """
    # Calculate number of samples
    num_samples = int(frequency * duration_ms / 1000)
    
    # Create silent audio data (all zeros)
    audio_data = [0] * num_samples
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters: 1 channel (mono), 2 bytes per sample, sample rate
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(frequency)
        
        # Write audio data
        for sample in audio_data:
            wav_file.writeframes(struct.pack('h', sample))
    
    print(f"Created: {filename}")


def create_placeholder_ogg(filename):
    """
    Create a placeholder file for OGG music.
    Note: This creates an empty file. Replace with actual OGG file for music.
    
    Args:
        filename: Output filename
    """
    # For OGG, we'll just create an empty file as a placeholder
    # In practice, you'd need actual OGG audio data
    with open(filename, 'wb') as f:
        f.write(b'')
    print(f"Created placeholder: {filename} (replace with actual OGG file)")


def main():
    """Create all placeholder sound files."""
    # Ensure assets directory exists
    os.makedirs('assets', exist_ok=True)
    
    # Create sound effect files
    sound_files = {
        'launch.wav': 200,      # 200ms for launch sound
        'splash.wav': 300,      # 300ms for splash
        'ripple.wav': 500,      # 500ms for ripple
        'ball_move.wav': 100,   # 100ms for ball movement
        'level_complete.wav': 1000,  # 1 second for completion
        'click.wav': 50         # 50ms for UI click
    }
    
    for filename, duration in sound_files.items():
        filepath = os.path.join('assets', filename)
        create_silent_wav(filepath, duration)
    
    # Create placeholder music file
    music_file = os.path.join('assets', 'background.ogg')
    create_placeholder_ogg(music_file)
    
    print("\nAll placeholder sound files created in 'assets/' directory.")
    print("Replace these with actual sound files for production.")


if __name__ == "__main__":
    main()
