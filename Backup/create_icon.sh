#!/bin/bash
# Generate an icns file from a png for macOS application
# Usage: ./create_icon.sh <source_png> <output_icns>

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_png> <output_icns>"
    exit 1
fi

SOURCE_PNG=$1
OUTPUT_ICNS=$2

# Check if source file exists
if [ ! -f "$SOURCE_PNG" ]; then
    echo "Error: Source file $SOURCE_PNG does not exist."
    exit 1
fi

# Create temporary iconset directory
ICONSET="$(mktemp -d)/AppIcon.iconset"
mkdir -p "$ICONSET"

# Generate icon files at various sizes
echo "Generating icons at various sizes..."
sips -z 16 16     "$SOURCE_PNG" --out "${ICONSET}/icon_16x16.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET}/icon_16x16@2x.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET}/icon_32x32.png"
sips -z 64 64     "$SOURCE_PNG" --out "${ICONSET}/icon_32x32@2x.png"
sips -z 128 128   "$SOURCE_PNG" --out "${ICONSET}/icon_128x128.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET}/icon_128x128@2x.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET}/icon_256x256.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET}/icon_256x256@2x.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET}/icon_512x512.png"
sips -z 1024 1024 "$SOURCE_PNG" --out "${ICONSET}/icon_512x512@2x.png"

# Convert the iconset to icns
echo "Converting iconset to icns..."
iconutil -c icns "$ICONSET" -o "$OUTPUT_ICNS"

# Clean up
rm -rf "$(dirname "$ICONSET")"

echo "Icon created successfully at $OUTPUT_ICNS"