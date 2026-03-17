import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np

# Krumhansl-Schmuckler key profiles
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.6, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_tempo_and_key(audio_path: Path):
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Key estimation via chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    # Normalize profiles for correlation
    major = MAJOR_PROFILE / MAJOR_PROFILE.sum()
    minor = MINOR_PROFILE / MINOR_PROFILE.sum()
    chroma_norm = chroma_mean / (chroma_mean.sum() + 1e-9)

    scores_major = [np.corrcoef(chroma_norm, np.roll(major, i))[0, 1] for i in range(12)]
    scores_minor = [np.corrcoef(chroma_norm, np.roll(minor, i))[0, 1] for i in range(12)]

    best_major = int(np.argmax(scores_major))
    best_minor = int(np.argmax(scores_minor))

    if scores_major[best_major] >= scores_minor[best_minor]:
        key = NOTE_NAMES[best_major]
        scale = "major"
        confidence = float(scores_major[best_major])
    else:
        key = NOTE_NAMES[best_minor]
        scale = "minor"
        confidence = float(scores_minor[best_minor])

    return float(tempo), key, scale, confidence


def run_demucs(audio_path: Path, out_dir: Path, model: str):
    cmd = [
        sys.executable,
        "-m",
        "demucs",
        "-n",
        model,
        "-o",
        str(out_dir),
        str(audio_path),
    ]
    subprocess.check_call(cmd)


def convert_stems_to_mp3(stems_dir: Path):
    # Requires ffmpeg on PATH
    for wav in stems_dir.glob("*.wav"):
        mp3 = wav.with_suffix(".mp3")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(wav),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(mp3),
        ]
        subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Free stem splitter + tempo/key finder")
    parser.add_argument("input", help="Input audio file (mp3 or wav)")
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument("--model", default="htdemucs", help="Demucs model name")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3"], help="Output format for stems")
    parser.add_argument("--json", action="store_true", help="Print tempo/key as JSON")
    args = parser.parse_args()

    audio_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not audio_path.exists():
        print(f"Input file not found: {audio_path}")
        sys.exit(1)

    tempo, key, scale, conf = estimate_tempo_and_key(audio_path)

    # Run Demucs
    run_demucs(audio_path, out_dir, args.model)

    # Demucs output path: out_dir/model_name/track_name
    track_name = audio_path.stem
    stems_dir = out_dir / args.model / track_name

    if args.format == "mp3":
        convert_stems_to_mp3(stems_dir)

    result = {
        "tempo_bpm": tempo,
        "key": key,
        "scale": scale,
        "confidence": conf,
        "stems_dir": str(stems_dir),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Tempo: {tempo:.2f} BPM")
        print(f"Key: {key} {scale} (confidence {conf:.3f})")
        print(f"Stems saved in: {stems_dir}")


if __name__ == "__main__":
    main()
