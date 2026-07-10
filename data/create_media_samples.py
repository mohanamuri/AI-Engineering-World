"""
create_media_samples.py — Generate sample files for Media Projects demo.

Run once from the project root:
    python data/create_media_samples.py

Produces:
    data/sample_meeting.wav      — scripted meeting audio (WAV, ~10 s tone)
    data/sample_image.png        — generated scene image with embedded text
    data/sample_document.png     — generated meeting-notes document image
    data/sample_meeting.mp4      — minimal video (requires ffmpeg on PATH)

The upload pages in Media Projects load these files automatically via a
"Load sample" button, so users can demo without uploading their own files
(same pattern as data/loan_eligibility_sample.csv for ML projects).
"""

import math
import os
import struct
import subprocess
import wave
import zlib
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent / "media_docs"
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 1. sample_meeting.wav — 8-second scripted-tone WAV (16 kHz, mono)
#    Whisper will transcribe the silence/tone as minimal text, but the file
#    demonstrates the full upload → transcribe → analyse → export flow.
# ---------------------------------------------------------------------------

def create_sample_wav(path: Path) -> None:
    sample_rate = 16000
    duration_s  = 8
    frequency   = 440  # Hz (A4 tone)

    n_samples = sample_rate * duration_s
    samples = [
        int(8000 * math.sin(2 * math.pi * frequency * t / sample_rate))
        for t in range(n_samples)
    ]

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{n_samples}h", *samples))

    print(f"  ✅ {path.name}  ({path.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# 2 & 3. PNG helpers — pure stdlib, no PIL required
# ---------------------------------------------------------------------------

def _make_png(width: int, height: int, pixels: list[tuple[int, int, int]]) -> bytes:
    """Encode pixels as a valid RGB PNG using only struct + zlib."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    sig  = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))

    raw = bytearray()
    for row in range(height):
        raw += b"\x00"  # filter type: None
        for col in range(width):
            r, g, b = pixels[row * width + col]
            raw += bytes([r, g, b])

    idat = chunk(b"IDAT", zlib.compress(bytes(raw), level=1))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def _fill_rect(pixels, W, x0, y0, x1, y1, colour):
    r, g, b = colour
    for y in range(max(0, y0), min(y1, len(pixels) // W)):
        for x in range(max(0, x0), min(x1, W)):
            pixels[y * W + x] = (r, g, b)


def create_sample_image(path: Path) -> None:
    """Scene with sky, ground, building, car, sun — no external deps."""
    W, H = 400, 280
    sky_blue  = (135, 206, 235)
    green     = (124, 205, 124)
    gray      = (169, 169, 169)
    red       = (200, 50, 50)
    gold      = (255, 215, 0)
    dark      = (40, 40, 40)
    white     = (255, 255, 255)
    navy      = (30, 30, 100)
    lt_blue   = (173, 216, 230)

    pixels = [sky_blue] * (W * H)

    # Ground
    _fill_rect(pixels, W, 0, 160, W, H, green)

    # Sun (circle approximation)
    sx, sy, sr = 350, 40, 30
    for y in range(sy - sr, sy + sr):
        for x in range(sx - sr, sx + sr):
            if (x - sx) ** 2 + (y - sy) ** 2 <= sr ** 2:
                if 0 <= y < H and 0 <= x < W:
                    pixels[y * W + x] = gold

    # Building body
    _fill_rect(pixels, W, 50, 80, 130, 165, gray)
    # Windows (3×2 grid)
    for row in range(2):
        for col in range(3):
            _fill_rect(pixels, W, 56 + col * 23, 85 + row * 25, 72 + col * 23, 103 + row * 25, lt_blue)

    # Car body
    _fill_rect(pixels, W, 175, 130, 300, 165, red)
    _fill_rect(pixels, W, 190, 115, 285, 133, red)
    # Wheels
    for cx, cy in [(195, 165), (280, 165)]:
        for y in range(cy - 12, cy + 12):
            for x in range(cx - 12, cx + 12):
                if (x - cx) ** 2 + (y - cy) ** 2 <= 144:
                    if 0 <= y < H and 0 <= x < W:
                        pixels[y * W + x] = dark

    # Sign board
    _fill_rect(pixels, W, 155, 60, 295, 100, white)
    _fill_rect(pixels, W, 155, 60, 295, 62, navy)   # top border
    _fill_rect(pixels, W, 155, 98, 295, 100, navy)   # bottom border
    # Text rows (block pixels to simulate text)
    for c in range(12):   # "CITY CENTRE" block
        _fill_rect(pixels, W, 162 + c * 9, 67, 168 + c * 9, 74, navy)
    for c in range(14):   # "Speed limit: 30" block
        _fill_rect(pixels, W, 162 + c * 8, 80, 167 + c * 8, 87, (180, 0, 0))

    png_bytes = _make_png(W, H, pixels)
    path.write_bytes(png_bytes)
    print(f"  ✅ {path.name}  ({path.stat().st_size // 1024} KB)")


def create_sample_document(path: Path) -> None:
    """Meeting-notes page layout — no external deps."""
    W, H = 500, 650
    white  = (255, 255, 255)
    navy   = (30, 80, 160)
    dark   = (50, 50, 50)
    light  = (220, 220, 220)
    head_t = (200, 220, 255)

    pixels = [white] * (W * H)

    # Page border
    for x in range(W):
        pixels[10 * W + x] = light
        pixels[(H - 10) * W + x] = light
    for y in range(H):
        pixels[y * W + 10] = light
        pixels[y * W + W - 10] = light

    # Header bar
    _fill_rect(pixels, W, 10, 10, W - 10, 60, navy)
    # Header text blocks (simulate "MEETING NOTES")
    for c in range(13):
        _fill_rect(pixels, W, 25 + c * 12, 20, 32 + c * 12, 33, white)
    # Sub-header text
    for c in range(30):
        _fill_rect(pixels, W, 25 + c * 8, 38, 30 + c * 8, 47, head_t)

    # Section: Attendees
    _fill_rect(pixels, W, 25, 72, 115, 82, navy)   # label block
    for row in range(4):
        for c in range(20):
            _fill_rect(pixels, W, 35 + c * 10, 88 + row * 18, 41 + c * 10, 96 + row * 18, dark)

    # Divider
    _fill_rect(pixels, W, 25, 165, W - 25, 167, light)

    # Section: Agenda
    _fill_rect(pixels, W, 25, 172, 85, 182, navy)
    for row in range(4):
        for c in range(25):
            _fill_rect(pixels, W, 35 + c * 10, 188 + row * 18, 41 + c * 10, 196 + row * 18, dark)

    # Divider
    _fill_rect(pixels, W, 25, 265, W - 25, 267, light)

    # Section: Decisions
    _fill_rect(pixels, W, 25, 272, 110, 282, navy)
    for row in range(3):
        for c in range(28):
            _fill_rect(pixels, W, 35 + c * 10, 288 + row * 22, 41 + c * 10, 298 + row * 22, dark)
        # tick box
        _fill_rect(pixels, W, 25, 288 + row * 22, 33, 298 + row * 22, (0, 150, 0))

    # Divider
    _fill_rect(pixels, W, 25, 360, W - 25, 362, light)

    # Section: Action Items
    _fill_rect(pixels, W, 25, 367, 135, 377, navy)
    for row in range(4):
        for c in range(28):
            _fill_rect(pixels, W, 35 + c * 10, 383 + row * 22, 41 + c * 10, 393 + row * 22, dark)
        # checkbox
        _fill_rect(pixels, W, 25, 383 + row * 22, 33, 393 + row * 22, light)

    # Footer
    _fill_rect(pixels, W, 10, H - 30, W - 10, H - 28, light)
    for c in range(18):
        _fill_rect(pixels, W, 25 + c * 10, H - 22, 31 + c * 10, H - 15, (180, 180, 180))
    for c in range(8):
        _fill_rect(pixels, W, W - 120 + c * 12, H - 22, W - 114 + c * 12, H - 15, (180, 180, 180))

    png_bytes = _make_png(W, H, pixels)
    path.write_bytes(png_bytes)
    print(f"  ✅ {path.name}  ({path.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# 4. sample_meeting.mp4 — minimal video (requires ffmpeg, optional)
# ---------------------------------------------------------------------------

def create_sample_mp4(path: Path, wav_path: Path) -> None:
    if not wav_path.exists():
        print(f"  ⚠ Skipping {path.name} — WAV not found")
        return
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f", "lavfi", "-i", "color=c=navy:s=640x360:r=10",
                "-i", str(wav_path),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
                "-c:a", "aac", "-b:a", "64k",
                "-shortest", "-t", "8",
                str(path), "-y",
            ],
            check=True, capture_output=True,
        )
        print(f"  ✅ {path.name}  ({path.stat().st_size // 1024} KB)")
    except FileNotFoundError:
        print("  ⚠ ffmpeg not found — skipping sample_meeting.mp4 (needed for UC2 demo)")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ ffmpeg error: {e.stderr.decode()[:200]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating Media Projects sample files …\n")

    wav_path = DATA_DIR / "sample_meeting.wav"
    img_path = DATA_DIR / "sample_image.png"
    doc_path = DATA_DIR / "sample_document.png"
    mp4_path = DATA_DIR / "sample_meeting.mp4"

    print("1/4 sample_meeting.wav")
    create_sample_wav(wav_path)

    print("2/4 sample_image.png")
    create_sample_image(img_path)

    print("3/4 sample_document.png")
    create_sample_document(doc_path)

    print("4/4 sample_meeting.mp4")
    create_sample_mp4(mp4_path, wav_path)

    print("\nDone. Files written to:", DATA_DIR)
