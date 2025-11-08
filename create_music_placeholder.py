"""
Script to create a minimal valid OGG Vorbis file for background music placeholder.
Uses pydub to create a silent audio file and export as OGG.
"""

import os
import wave
import struct


def create_silent_wav_for_conversion(filename, duration_seconds=10, frequency=44100):
    """
    Create a silent WAV file that can be used as music placeholder.
    
    Args:
        filename: Output filename
        duration_seconds: Duration in seconds
        frequency: Sample rate in Hz
    """
    # Calculate number of samples
    num_samples = int(frequency * duration_seconds)
    
    # Create silent audio data (all zeros)
    audio_data = [0] * num_samples
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters: 2 channels (stereo), 2 bytes per sample, sample rate
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(frequency)
        
        # Write audio data (stereo, so write each sample twice)
        for sample in audio_data:
            wav_file.writeframes(struct.pack('hh', sample, sample))
    
    print(f"Created: {filename}")


def main():
    """Create placeholder music file."""
    # Ensure assets directory exists
    os.makedirs('assets', exist_ok=True)
    
    # Create a WAV file as placeholder for music
    # Since OGG encoding requires external libraries, we'll create a WAV
    # and note that it should be converted to OGG
    music_wav = os.path.join('assets', 'background.wav')
    create_silent_wav_for_conversion(music_wav, duration_seconds=10)
    
    print("\nCreated placeholder music file as WAV.")
    print("Note: Pygame can play WAV files as music.")
    print("For production, convert to OGG format for better compression.")
    print("You can use tools like ffmpeg or audacity to convert WAV to OGG.")


if __name__ == "__main__":
    main()
