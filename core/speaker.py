import subprocess

def speak(text):

    if not text:
        return

    subprocess.run(
        ["say", text]
    )


if __name__ == "__main__":

    speak("Hello, I am Aerva.")