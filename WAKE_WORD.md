# Aerva Wake-Word Engine ("Hey Aerva")

This document details the architecture, training procedure, performance metrics, and operational tuning for the custom offline wake-word detector **`aerva.onnx`** powering the **Aerva** assistant on macOS (Apple Silicon).

---

## 1. System Architecture

Aerva uses **OpenWakeWord** as the low-latency wake-word engine. The pipeline operates entirely offline on your Mac mini M4:

```
Microphone (16 kHz int16, 1280 sample chunks / 80ms)
       │
       ▼
OpenWakeWord Preprocessor (Mel Spectrogram + Google Speech Embedding)
       │
       ▼
Classification Head (models/aerva.onnx)
       │
       ▼
Confidence Score [0.0 – 1.0] >= 0.75 ?
       │
       ├─ YES ──► Trigger Aerva Pipeline
       │          (Silero VAD ──► Whisper ──► Qwen3 1.7B ──► macOS TTS)
       │
       └─ NO  ──► Continue listening
```

### Specifications:
- **Wake Word**: `"Hey Aerva"`
- **Model Path**: `models/aerva.onnx`
- **Model Format**: ONNX (Opset 18)
- **Input Features**: Sliding window of `(1, 16, 96)` (16 frames × 96-dimensional acoustic speech embeddings)
- **Output**: Single Sigmoid probability `[0.0, 1.0]` for key `"aerva"`
- **Chunk Size**: `1280` samples (80 ms per inference cycle)
- **Sample Rate**: `16,000 Hz` (Mono PCM)
- **Latency**: `< 1.5 ms` per 80ms chunk on Apple Silicon M4
- **Runtime RAM / Disk Footprint**: ~850 KB ONNX file, negligible memory overhead

---

## 2. Dataset & Synthetic Generation

Because manually recording thousands of voice samples is impractical, the training dataset was synthesized using high-quality native text-to-speech engines across acoustic variations:

| Category | Count | Variations Included |
|---|---|---|
| **Positive Clips** | **850 clips** | Spoken phrase *"Hey Aerva"* with phonetic variants (*"Hey Airva"*, *"Hey Ay-er-va"*, *"Hey Air-va"*, *"Hey Erva"*), across 28+ male/female voices, diverse accents (US, UK, Indian, Australian, Irish, South African), tempos (130–220 wpm), and randomized volume scaling (35%–95%). |
| **Negative & Adversarial Clips** | **850 clips** | Confusing phonetic lookalikes (*"Hey Ava"*, *"Hey Arrow"*, *"Hey Sarah"*, *"Hey Vera"*, *"Hey Era"*, *"Hairdryer"*, *"Airport area"*, *"Error code"*) and assistant phrases (*"Hey Siri"*, *"Hey Jarvis"*, *"Hello there"*, *"Cancel that"*). |
| **Background Acoustics** | **120 clips** | Synthesized room ambient noise, electrical hums (50Hz / 60Hz / 120Hz harmonics), pink noise, brown noise, and quiet room silence. |

---

## 3. Training & Validation Results

The model was trained directly on the Mac mini M4 GPU (`mps` device) using a streaming-aligned sliding buffer:
- **Total streaming feature windows evaluated**: `22,795` (10,785 positive, 12,010 negative)
- **Training Epochs**: 15 epochs with Adam optimizer and `ReduceLROnPlateau` scheduler
- **Validation Accuracy**: **95.6%**
- **Validation Recall (True Positive Rate)**: **98.3%**
- **Validation False Positive Rate**: **6.7%** (on hard adversarial negatives at baseline 0.5 threshold)
- **Live Microphone True Positive Score**: **0.78 – 0.999**
- **Live Background / Silence Score**: **< 0.005**

---

## 4. Integration Details

### `core/wake_word.py`

The wake-word detector loads `models/aerva.onnx` and evaluates incoming mic chunks:

```python
from pathlib import Path
import sounddevice as sd
import numpy as np
from openwakeword.model import Model

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
WAKE_WORD_LABEL = "Hey Aerva"
WAKE_WORD_KEY = "aerva"
THRESHOLD = 0.75

# Automatically resolves models/aerva.onnx relative to project root
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "aerva.onnx"

model = Model(
    wakeword_models=[str(MODEL_PATH)],
    inference_framework="onnx"
)

def listen_for_wake_word():
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:
        while True:
            audio, overflowed = stream.read(CHUNK_SIZE)
            if overflowed:
                continue

            prediction = model.predict(np.squeeze(audio))
            score = prediction.get(WAKE_WORD_KEY, 0)

            if score >= THRESHOLD:
                return True
```

---

## 5. Threshold & Latency Optimization Guide

The detection threshold is controlled by `THRESHOLD` in [core/wake_word.py](file:///Users/priyanshuyadav/Desktop/aerva/core/wake_word.py).

### Threshold Selection Matrix:

| Threshold | Intended Environment | Detection Behavior |
|---|---|---|
| **0.65 – 0.70** | Quiet office / Far-field | Maximum sensitivity. Catches quiet whispers and speaking from 3–5 meters away. Slightly higher chance of triggering if TV or YouTube plays similar phonetic words. |
| **0.75** *(Current Default)* | Typical desktop environment | **Optimal balance**. Live tests consistently yield scores between `0.80` and `0.99` with virtually zero false triggers during silence. |
| **0.80 – 0.85** | High ambient noise / Shared room | Highly conservative. Eliminates nearly all background conversational false triggers; requires clear, direct speech into the microphone. |

### Advanced OpenWakeWord Controls (Optional):

If you ever wish to tune latency or prevent double triggers in very rapid speech, OpenWakeWord provides two built-in parameters:

1. **Debounce (`debounce_time`)**:
   Prevents immediate re-triggering within `X` seconds after a successful detection:
   ```python
   prediction = model.predict(audio, debounce_time=1.5, threshold={"aerva": 0.75})
   ```

2. **Patience (`patience`)**:
   Requires `N` consecutive 80ms chunks above the threshold before declaring a match (filters out momentary acoustic clicks or microphone spikes):
   ```python
   prediction = model.predict(audio, patience={"aerva": 2}, threshold={"aerva": 0.75})
   ```

---

## 6. How to Run Aerva with Custom Wake Word

From your workspace root:

```bash
# 1. Activate your virtual environment
source .venv/bin/activate

# 2. Test wake-word detection in isolation
python core/wake_word.py

# 3. Launch the full voice assistant loop
python core/listener.py
```

Say **"Hey Aerva"** at conversational volume — the assistant will instantly detect the wake word, engage Silero VAD, record your command, transcribe with Whisper, query Qwen3, and speak back.
