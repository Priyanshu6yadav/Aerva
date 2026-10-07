import sounddevice as sd
import numpy as np
from openwakeword.model import Model


# =========================================================
# SETTINGS
# =========================================================

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
WAKE_WORD = "hey_jarvis"
THRESHOLD = 0.7


# =========================================================
# LOAD WAKE WORD MODEL
# =========================================================

print("🧠 Loading wake-word model...")

model = Model(
    wakeword_models=[WAKE_WORD]
)

print("✅ Wake-word model ready.")


# =========================================================
# LISTEN FOR WAKE WORD
# =========================================================

def listen_for_wake_word():

    print(f"👂 Waiting for '{WAKE_WORD}'...")

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
                WAKE_WORD,
                0
            )

            if score >= THRESHOLD:

                print("🔔 Wake word detected!")

                return True


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    listen_for_wake_word()