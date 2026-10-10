# ---------------------------------------------------------
# AERVA CUSTOM WAKE-WORD DETECTOR
# Wake phrase: "Hey Aerva"
# Model: models/aerva.onnx
# ---------------------------------------------------------

from pathlib import Path

import sounddevice as sd
import numpy as np
from openwakeword.model import Model


# Audio configuration
# OpenWakeWord expects 16 kHz mono audio.
SAMPLE_RATE = 16000

# 1280 samples at 16 kHz = 80 milliseconds of audio.
# This is the chunk size used for real-time detection.
CHUNK_SIZE = 1280


# Wake-word configuration
WAKE_WORD_LABEL = "Hey Aerva"
WAKE_WORD_KEY = "aerva"

# Detection threshold.
# Higher = fewer false triggers but potentially lower sensitivity.
THRESHOLD = 0.75


# Build the model path relative to the Aerva project.
# This allows the program to work regardless of the current
# terminal directory.
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "aerva.onnx"
)


# Load the custom ONNX wake-word model.
print("🧠 Loading wake-word model...")

model = Model(
    wakeword_models=[str(MODEL_PATH)],
    inference_framework="onnx"
)

print("✅ Wake-word model ready (Hey Aerva).")


def listen_for_wake_word():
    """
    Continuously listen to the microphone until
    the 'Hey Aerva' wake phrase is detected.
    """

    print("👂 Waiting for 'Hey Aerva'...")

    # Open a continuous microphone stream.
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:

        while True:

            # Read one 80 ms audio chunk.
            audio, overflowed = stream.read(CHUNK_SIZE)

            # Ignore the chunk if the audio buffer overflowed.
            if overflowed:
                continue

            # Convert the audio from (1280, 1) to (1280,).
            audio = np.squeeze(audio)

            # Run the audio through the wake-word model.
            prediction = model.predict(audio)

            # Get the confidence score for our custom "aerva" model.
            score = prediction.get(WAKE_WORD_KEY, 0)

            # Trigger Aerva when the confidence exceeds the threshold.
            if score >= THRESHOLD:

                print(
                    f"🔔 Wake word detected! "
                    f"({WAKE_WORD_LABEL})"
                )

                return True


# This allows us to test wake_word.py directly.
# When imported by listener.py, this section will not execute.
if __name__ == "__main__":
    listen_for_wake_word()