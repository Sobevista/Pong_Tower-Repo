# generate_sounds.py
# ===================
# Generates placeholder .wav files for Pong Tower using only stdlib.
# Run once: python generate_sounds.py

import os
import struct
import math

SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(SOUND_DIR, exist_ok=True)

SAMPLE_RATE = 44100


def _write_wav(path, samples, sample_rate=SAMPLE_RATE, num_channels=1, sample_width=2):
    """Write a raw mono 16-bit PCM WAV file."""
    data = b""
    for s in samples:
        # clamp to 16-bit range
        val = max(-32768, min(32767, int(s * 32767)))
        data += struct.pack("<h", val)

    byte_rate = sample_rate * num_channels * sample_width
    block_align = num_channels * sample_width
    data_size = len(data)
    header = (
        b"RIFF"
        + struct.pack("<I", 36 + data_size)
        + b"WAVE"
        + b"fmt "
        + struct.pack("<IHHIIHH", 16, 1, num_channels, sample_rate, byte_rate, block_align, sample_width * 8)
        + b"data"
        + struct.pack("<I", data_size)
        + data
    )
    with open(path, "wb") as f:
        f.write(header)
    print(f"  Wrote: {path}")


def _tone(freq, duration, wave_type="square", volume=0.4):
    """Generate a tone buffer."""
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        if wave_type == "square":
            s = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave_type == "sawtooth":
            phase = (freq * t) % 1.0
            s = 2.0 * phase - 1.0
        elif wave_type == "sine":
            s = math.sin(2 * math.pi * freq * t)
        else:
            s = 0

        # Envelope: quick attack, quick decay
        env = 1.0
        attack = 0.005
        decay = 0.05
        if t < attack:
            env = t / attack
        elif t > duration - decay:
            env = max(0, (duration - t) / decay)

        samples.append(s * volume * env)
    return samples


# ---- Generate sounds ----
print("Generating sounds...")

# paddle_hit.wav - short high blip
_write_wav(
    os.path.join(SOUND_DIR, "paddle_hit.wav"),
    _tone(freq=680, duration=0.08, wave_type="square", volume=0.35) +
    _tone(freq=340, duration=0.06, wave_type="sine", volume=0.2),
)

# score.wav - two-tone ding
_write_wav(
    os.path.join(SOUND_DIR, "score.wav"),
    _tone(freq=520, duration=0.12, wave_type="square", volume=0.4) +
    _tone(freq=780, duration=0.15, wave_type="sine", volume=0.4),
)

# win.wav - ascending fanfare
_write_wav(
    os.path.join(SOUND_DIR, "win.wav"),
    _tone(freq=392, duration=0.12, wave_type="square", volume=0.4) +
    _tone(freq=523, duration=0.12, wave_type="square", volume=0.4) +
    _tone(freq=659, duration=0.12, wave_type="square", volume=0.4) +
    _tone(freq=784, duration=0.35, wave_type="sine", volume=0.5),
)

print("Done. All sounds generated in:", SOUND_DIR)
