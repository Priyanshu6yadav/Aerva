# ---------------------------------------------------------
# AERVA SCREEN CAPTURE
# Version: v0.9
#
# Purpose:
# Capture the current macOS screen so that Aerva can
# eventually understand what is visible on the screen.
#
# Current stage:
# Screenshot only.
#
# Future stages:
# Screenshot → OCR → Vision → Screen Understanding
# ---------------------------------------------------------

from pathlib import Path
import subprocess


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# Store screenshots inside the Aerva project.
SCREENSHOT_DIR = (
    Path(__file__).resolve().parent.parent
    / "screenshots"
)


def capture_screen():
    """
    Capture the current macOS screen.

    Returns:
        str:
            Path to the saved screenshot.
    """

    # Create the screenshot directory if it doesn't exist.
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save the screenshot as screen.png.
    output_path = SCREENSHOT_DIR / "screen.png"

    try:

        # macOS provides the native 'screencapture' command.
        # -x prevents the camera/shutter sound.
        result = subprocess.run(
            [
                "screencapture",
                "-x",
                str(output_path)
            ],
            capture_output=True,
            text=True
        )

        # Check whether macOS successfully created
        # the screenshot.
        if result.returncode != 0:

            print(
                f"❌ Screen capture failed: "
                f"{result.stderr.strip()}"
            )

            return None

        print(
            f"📸 Screenshot captured: {output_path}"
        )

        return str(output_path)

    except Exception as error:

        print(
            f"❌ Screen capture error: {error}"
        )

        return None


# ---------------------------------------------------------
# TEST
#
# This section runs only when this file is executed directly.
# ---------------------------------------------------------

if __name__ == "__main__":

    print("👁️ Aerva Screen Capture Test")
    print("-----------------------------")

    screenshot = capture_screen()

    if screenshot:

        print(
            f"✅ Screenshot saved at:\n{screenshot}"
        )

    else:

        print(
            "❌ Screenshot could not be created."
        )