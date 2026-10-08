import sounddevice as sd
import numpy as np
from openwakeword.model import Model


from pathlib import Path

# =========================================================
# SETTINGS
# =========================================================

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
WAKE_WORD_LABEL = "Hey Aerva"
WAKE_WORD_KEY = "aerva"
THRESHOLD = 0.75

# Locate models/aerva.onnx reliably whether run from project root or core/
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "aerva.onnx"
if not MODEL_PATH.exists():
    # Fallback to current working directory
    MODEL_PATH = Path("models/aerva.onnx").resolve()

# =========================================================
# LOAD WAKE WORD MODEL
# =========================================================

print("🧠 Loading wake-word model...")

model = Model(
    wakeword_models=[str(MODEL_PATH)],
    inference_framework="onnx"
)

print(f"✅ Wake-word model ready ({WAKE_WORD_LABEL}).")


# =========================================================
# LISTEN FOR WAKE WORD
# =========================================================

def listen_for_wake_word():

    print(f"👂 Waiting for '{WAKE_WORD_LABEL}'...")

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

            audio = np.squeeze(audio)

            prediction = model.predict(audio)

            score = prediction.get(
                WAKE_WORD_KEY,
                0
            )

            if score >= THRESHOLD:

                print(f"🔔 Wake word detected! ({WAKE_WORD_LABEL})")

                return True


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    listen_for_wake_word()