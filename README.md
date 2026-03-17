# Free Stem Splitter + Tempo/Key Finder

This project splits any song into stems for free using **Demucs** (open source) and also finds **tempo (BPM)** and **key/scale** using **librosa**.

## Features
- Input: MP3 or WAV
- Output: WAV stems (default) or MP3 stems (optional)
- Tempo & key detection
- 100% free, open-source stack

## Requirements
- Python 3.9+
- FFmpeg (only required if you want MP3 output)

## Install
```bash
pip install -r requirements.txt
```

If you want MP3 output, install ffmpeg and make sure it is on PATH.

## No-Install Option (Google Colab)
If you don’t want to install anything on your PC, run it in **Google Colab**.
Create a new Colab notebook and run these cells:

**Cell 1: Install dependencies (on Colab only)**
```bash
!pip -q install demucs librosa numpy soundfile
```

**Cell 2: Upload `app.py` and your song**
```python
from google.colab import files
uploaded = files.upload()
```

**Cell 3: Run the splitter**
```python
import os, sys, json
from pathlib import Path

!python app.py "song.mp3" --out outputs --format wav
```

**Cell 4: Download stems**
```python
import shutil
from google.colab import files

shutil.make_archive("stems", "zip", "outputs")
files.download("stems.zip")
```

## Usage
```bash
python app.py "input_song.mp3" --out outputs --format wav
```

MP3 stems:
```bash
python app.py "input_song.mp3" --out outputs --format mp3
```

JSON output:
```bash
python app.py "input_song.mp3" --json
```

## Output
Demucs outputs stems in:
```
outputs/<model>/<track_name>/
```

## Models
Default model: `htdemucs`
You can change it:
```bash
python app.py "song.mp3" --model htdemucs
```

## Notes
- Tempo/key detection is an estimate.
- Only process audio you own or have rights to.

## License
MIT
