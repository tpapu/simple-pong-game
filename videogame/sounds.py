"""Sound generation for the Pong game."""

import io
import wave
import numpy as np
import pygame


def generate_beep(frequency, duration, volume):
    """Generate a simple beep sound."""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)

    # Generate sine wave
    buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate)
    buf = buf * volume
    buf = (buf * 32767).astype(np.int16)
    buf = np.c_[buf, buf]  # Stereo

    return pygame.sndarray.make_sound(buf)


def generate_score_sound():
    """Generate a rising tone for scoring."""
    sample_rate = 22050
    duration = 0.3
    n_samples = int(duration * sample_rate)

    # Rising frequency
    frequencies = np.linspace(400, 800, n_samples)
    phases = np.cumsum(2 * np.pi * frequencies / sample_rate)
    buf = np.sin(phases)

    # Fade out envelope
    envelope = np.linspace(1.0, 0.0, n_samples)
    buf = buf * envelope * 0.3

    # Convert to pygame format
    buf = (buf * 32767).astype(np.int16)
    buf = np.c_[buf, buf]

    return pygame.sndarray.make_sound(buf)


def generate_bgm():
    """Generate background music."""
    sample_rate = 22050
    duration = 5.0  # 4 second loop
    n_samples = int(duration * sample_rate)

    # simple melody
    melody = [
        (523, 0.5),  # C5
        (587, 0.5),  # D5
        (659, 0.5),  # E5
        (523, 0.5),  # C5
        (659, 0.5),  # E5
        (784, 0.5),  # G5
        (659, 1.0),  # E5 (longer)
        (587, 1.0),  # D5 (longer)
    ]

    # Generate the audio
    audio = np.zeros(n_samples)
    current_sample = 0

    for frequency, note_duration in melody:
        note_samples = int(note_duration * sample_rate)
        if current_sample + note_samples > n_samples:
            break

        # Generate sine wave for this note
        t = np.arange(note_samples)
        note = np.sin(2 * np.pi * frequency * t / sample_rate)

        # Apply envelope (fade in and out)
        envelope = np.ones(note_samples)
        fade_samples = int(0.01 * sample_rate)  # 10ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        note = note * envelope * 0.1  # Low volume

        # Add to audio
        audio[current_sample : current_sample + note_samples] = note
        current_sample += note_samples

    # Convert to pygame format
    audio = (audio * 32767).astype(np.int16)
    audio = np.c_[audio, audio]  # Stereo

    # Create WAV file in memory
    byte_io = io.BytesIO()
    with wave.open(byte_io, "wb") as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    byte_io.seek(0)
    return byte_io


def load_game_sounds():
    """Load all game sounds."""
    sounds = {
        "paddle_hit": generate_beep(800, 0.05, 0.3),
        "wall_hit": generate_beep(600, 0.08, 0.3),
        "score": generate_score_sound(),
        "bgm": generate_bgm(),
    }
    return sounds
