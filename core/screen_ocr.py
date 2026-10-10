# =========================================================
# AERVA v0.9.3 — LOCAL SCREEN OCR + BOUNDING BOXES
# =========================================================
#
# Purpose:
#   1. Read a macOS screenshot.
#   2. Extract visible text using Apple's Vision framework.
#   3. Record the bounding box of each detected text element.
#
# Output:
#   A list of dictionaries containing text and coordinates.
#
# Processing is local. No cloud OCR service is required.
# =========================================================

from pathlib import Path

import Vision


# ---------------------------------------------------------
# SCREENSHOT PATH
# ---------------------------------------------------------
# This is the screenshot created by screen_capture.py.

SCREENSHOT_PATH = (
    Path(__file__).resolve().parent.parent
    / "screenshots"
    / "screen.png"
)


# ---------------------------------------------------------
# OCR FUNCTION
# ---------------------------------------------------------

def extract_text_from_screen(image_path):
    """
    Extract text and bounding boxes from a screenshot.

    Args:
        image_path: Path to the screenshot.

    Returns:
        list: Each item contains recognized text and its
              normalized bounding box.
    """

    # Create a Path object so we can validate the file.
    image_path = Path(image_path)

    # Stop if the screenshot does not exist.
    if not image_path.exists():
        print(f"❌ Screenshot not found: {image_path}")
        return []

    # Read the screenshot as binary image data.
    # Passing None as Vision's options avoids the PyObjC
    # dictionary issue discovered during our earlier tests.
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    if not image_data:
        print("❌ Screenshot is empty.")
        return []

    # Store OCR results here.
    # Each result will contain text and a bounding box.
    detected_text = []

    # -----------------------------------------------------
    # OCR RESULT CALLBACK
    # -----------------------------------------------------
    # Vision calls this function after processing the image.

    def handle_results(request, error):

        if error:
            print(f"❌ OCR error: {error}")
            return

        # Retrieve all recognized text observations.
        observations = request.results()

        for observation in observations:

            # Get the highest-confidence text candidate.
            candidates = observation.topCandidates_(1)

            if not candidates:
                continue

            text = candidates[0].string()

            if not text:
                continue

            # Get the normalized bounding box.
            # Coordinates range from 0.0 to 1.0.
            bounding_box = observation.boundingBox()

            # Save the text and its position together.
            detected_text.append({
                "text": text,
                "bounding_box": {
                    "x": bounding_box.origin.x,
                    "y": bounding_box.origin.y,
                    "width": bounding_box.size.width,
                    "height": bounding_box.size.height
                }
            })

    # -----------------------------------------------------
    # CREATE OCR REQUEST
    # -----------------------------------------------------
    # Ask Apple's Vision framework to recognize text.

    request = (
        Vision.VNRecognizeTextRequest
        .alloc()
        .initWithCompletionHandler_(handle_results)
    )

    # Accurate mode prioritizes recognition quality.
    request.setRecognitionLevel_(
        Vision.VNRequestTextRecognitionLevelAccurate
    )

    # -----------------------------------------------------
    # CREATE IMAGE HANDLER
    # -----------------------------------------------------
    # IMPORTANT:
    # Use None rather than {} for the options argument.
    # Our diagnostic test confirmed this works in your setup.

    handler = (
        Vision.VNImageRequestHandler
        .alloc()
        .initWithData_options_(
            image_data,
            None
        )
    )

    # -----------------------------------------------------
    # EXECUTE OCR
    # -----------------------------------------------------

    success, error = handler.performRequests_error_(
        [request],
        None
    )

    if not success:
        print(f"❌ OCR request failed: {error}")
        return []

    # Return the complete structured OCR results.
    return detected_text


# ---------------------------------------------------------
# DIRECT TEST
# ---------------------------------------------------------
# Run this file directly to test screen OCR independently.

if __name__ == "__main__":

    print("👁️ Aerva Local OCR + Bounding Boxes")
    print("-----------------------------------")

    # Run OCR before attempting to display its results.
    results = extract_text_from_screen(SCREENSHOT_PATH)

    if results:

        print(f"\n✅ Detected {len(results)} text elements.\n")

        for item in results:

            print(f"Text: {item['text']}")

            box = item["bounding_box"]

            print(
                f"Bounding box: "
                f"x={box['x']:.4f}, "
                f"y={box['y']:.4f}, "
                f"width={box['width']:.4f}, "
                f"height={box['height']:.4f}"
            )

            print()

    else:
        print("⚠️ No text detected.")