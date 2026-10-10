# AERVA VISION HANDLER TEST
#
# Purpose:
#   Test the Vision image handler independently from OCR.
#   This helps us identify exactly which argument causes
#   the PyObjC exception.

from pathlib import Path

import Vision


# ---------------------------------------------------------
# TEST IMAGE
# ---------------------------------------------------------
# Use the screenshot that we already know exists.
IMAGE_PATH = (
    Path(__file__).resolve().parent.parent
    / "screenshots"
    / "screen.png"
)


print("🔬 Testing Vision image handler")
print("--------------------------------")

if not IMAGE_PATH.exists():
    print(f"❌ Image not found: {IMAGE_PATH}")
    raise SystemExit


# ---------------------------------------------------------
# READ PNG
# ---------------------------------------------------------
with open(IMAGE_PATH, "rb") as file:
    image_data = file.read()

print(f"✅ Image loaded: {len(image_data)} bytes")


# ---------------------------------------------------------
# CREATE HANDLER
# ---------------------------------------------------------
try:

    # None is used instead of {} for the options argument.
    #
    # This is intentional: Vision accepts an optional
    # NSDictionary here, and we want to test whether the
    # empty Python dictionary was causing the exception.
    handler = (
        Vision.VNImageRequestHandler
        .alloc()
        .initWithData_options_(
            image_data,
            None
        )
    )

    print("✅ Vision handler created successfully!")

except Exception as error:

    print("❌ Vision handler creation failed:")
    print(error)