import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import torch
from wake_word import listen_for_wake_word
from assistant import route_command
from speaker import speak
import numpy as np
from silero_vad import load_silero_vad


# =========================================================
# WHISPER SETUP
# =========================================================

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

print("🧠 Loading Whisper...")
print("Whisper device:", DEVICE)

model = whisper.load_model(
    "base",
    device=DEVICE
)

print("✅ Whisper ready.")
# =========================================================
# SILERO VAD SETUP
# =========================================================

print("🧠 Loading Silero VAD...")
vad_model = load_silero_vad()
print("✅ Silero VAD ready.")

# =========================================================
# RECORD AUDIO WITH VAD
# =========================================================

def record_audio():

    sample_rate = 16000
    chunk_size = 512

    # VAD settings
    speech_threshold = 0.5
    silence_duration = 0.8
    max_recording_duration = 10

    silence_chunks_required = int(
        silence_duration * sample_rate / chunk_size
    )

    max_chunks = int(
        max_recording_duration * sample_rate / chunk_size
    )

    print("\n🎤 Listening...")

    audio_chunks = []

    speech_started = False
    silence_chunks = 0
    total_chunks = 0

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=chunk_size
    ) as stream:

        while total_chunks < max_chunks:

            audio, overflowed = stream.read(chunk_size)

            if overflowed:
                continue

            audio = np.squeeze(audio)

            audio_tensor = torch.from_numpy(audio)

            speech_probability = vad_model(
                audio_tensor,
                sample_rate
            ).item()

            # -----------------------------------------
            # WAITING FOR SPEECH
            # -----------------------------------------

            if not speech_started:

                if speech_probability >= speech_threshold:

                    print("🗣️ Speech detected!")

                    speech_started = True

                    audio_chunks.append(
                        audio.copy()
                    )

                total_chunks += 1
                continue

            # -----------------------------------------
            # RECORDING SPEECH
            # -----------------------------------------

            audio_chunks.append(
                audio.copy()
            )

            if speech_probability >= speech_threshold:

                silence_chunks = 0

            else:

                silence_chunks += 1

            # -----------------------------------------
            # SPEECH ENDED
            # -----------------------------------------

            if silence_chunks >= silence_chunks_required:

                print("🤫 Silence detected.")
                break

            total_chunks += 1

    # ---------------------------------------------
    # SAVE RECORDING
    # ---------------------------------------------

    if not audio_chunks:
        print("⚠️ No speech detected.")
        return False

    audio_data = np.concatenate(
        audio_chunks
    )

    audio_data = (
        audio_data * 32767
    ).astype(np.int16)

    write(
        "input.wav",
        sample_rate,
        audio_data
    )

    print("✅ Speech recording complete.")
    return True

# =========================================================
# TRANSCRIBE AUDIO
# =========================================================

def transcribe_audio():

    result = model.transcribe(
        "input.wav",
        language="en",
        initial_prompt=(
            "Aerva, Safari, Google Chrome, Chrome, "
            "macOS, open, close, YouTube, Gmail, GitHub."
        )
    )

    text = result["text"].strip()

    print("You:", text)

    return text


# =========================================================
# NORMALIZE COMMAND
# =========================================================

def normalize_command(command):

    return (
        command
        .lower()
        .strip()
        .rstrip(".,!?")
    )


# =========================================================
# CONVERSATION MODE
# =========================================================

def conversation_mode():

    print("\n💬 Conversation mode active.")

    while True:

        recording = record_audio()

        if not recording:
            print("👂 Returning to wake-word mode.")
            break
        command = transcribe_audio()
        if not command:
            continue
        command_clean = normalize_command(command)
        if command_clean in [
            "exit",
            "quit",
            "quite",
            "stop",
            "that's all",
            "that is all"
        ]:
            print("👂 Returning to wake-word mode.")
            break
        response = route_command(command_clean)
        print("Aerva:", response)
        speak(response)

# =========================================================
# MAIN VOICE LOOP
# =========================================================

if __name__ == "__main__":

    while True:

        # Wait for wake word
        listen_for_wake_word()

        # Record command
        recording = record_audio()

        # Nothing spoken
        if not recording:
            continue

        # Convert speech to text
        command = transcribe_audio()

        if not command:
            continue

        command_clean = normalize_command(command)

        # Exit Aerva
        if command_clean in [
            "exit",
            "quit",
            "quite",
            "stop"
        ]:
            print("Aerva: Goodbye!")
            speak("Goodbye!")
            break

        # Process command
        response = route_command(command_clean)

        print("Aerva:", response)

        speak(response)
