# AERVA VISION API DIAGNOSTIC
#
# Purpose:
#   Inspect the Vision framework and the exact methods exposed
#   by your installed PyObjC version.
#
# We are NOT running OCR yet.

import Vision
import objc


print("🔍 Aerva Vision Diagnostic")
print("-------------------------")

# Show the installed PyObjC version.
print("PyObjC version:", objc.__version__)

# Show the Vision framework location.
print("Vision module:", Vision.__file__)

# Check that the OCR request exists.
print(
    "VNRecognizeTextRequest:",
    hasattr(Vision, "VNRecognizeTextRequest")
)

# Check the image request handler.
print(
    "VNImageRequestHandler:",
    hasattr(Vision, "VNImageRequestHandler")
)

handler_class = Vision.VNImageRequestHandler

print("\n📋 Available initializer methods:\n")

# Print every method related to initialization.
for name in dir(handler_class):

    if "initWith" in name:
        print(name)

print("\n📋 OCR request initializer methods:\n")

request_class = Vision.VNRecognizeTextRequest

for name in dir(request_class):

    if "initWith" in name:
        print(name)