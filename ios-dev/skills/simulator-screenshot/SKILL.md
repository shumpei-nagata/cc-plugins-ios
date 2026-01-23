---
name: simulator-screenshot
description: This skill should be used when the user asks to "take screenshot", "capture screen", "record video", "screen recording", "simulator screenshot", "simctl io", "スクリーンショット", "画面キャプチャ", "画面録画", or needs to capture screenshots or record video from iOS/watchOS/tvOS/visionOS simulators.
context: fork
---

# Screenshot and Screen Recording for iOS Simulators

Capture screenshots and record video from iOS, watchOS, tvOS, and visionOS simulators using `xcrun simctl io`.

## Purpose

Capture visual output from simulators:
- Take screenshots in PNG format
- Record screen video in MP4 format
- Capture for documentation, bug reports, or testing

## Workflow

1. Ensure the target simulator is booted
2. Execute screenshot or recording command
3. Save to specified file path
4. Verify the output file

## Command Reference

### Take Screenshot

```bash
xcrun simctl io <UDID> screenshot <output-path.png>
```

Example:
```bash
xcrun simctl io booted screenshot ~/Desktop/screenshot.png
```

### Record Video

Start recording:
```bash
xcrun simctl io <UDID> recordVideo <output-path.mp4>
```

Stop recording: Press `Ctrl+C`

Example:
```bash
xcrun simctl io booted recordVideo ~/Desktop/recording.mp4
```

## Using "booted" Keyword

Use `booted` instead of UDID to target the currently booted simulator:

```bash
# Screenshot of booted simulator
xcrun simctl io booted screenshot output.png

# Video of booted simulator
xcrun simctl io booted recordVideo output.mp4
```

## Screenshot Options

### Specify display type

```bash
xcrun simctl io booted screenshot --type=png output.png
```

Supported types: `png`, `tiff`, `bmp`, `gif`, `jpeg`

### External display (for CarPlay, etc.)

```bash
xcrun simctl io booted screenshot --display=external carplay.png
```

## Video Recording Options

### Specify codec

```bash
xcrun simctl io booted recordVideo --codec=h264 output.mp4
```

Available codecs: `h264`, `hevc`

### Mask options

```bash
# Include device mask (rounded corners, notch)
xcrun simctl io booted recordVideo --mask=black output.mp4

# No mask
xcrun simctl io booted recordVideo --mask=ignored output.mp4
```

### Force overwrite

```bash
xcrun simctl io booted recordVideo --force output.mp4
```

## Common Scenarios

### Quick screenshot to Desktop

```bash
xcrun simctl io booted screenshot ~/Desktop/screenshot_$(date +%Y%m%d_%H%M%S).png
```

### Screenshot with timestamp

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
xcrun simctl io booted screenshot "screenshot_${TIMESTAMP}.png"
```

### Record app demo

```bash
# Start recording
xcrun simctl io booted recordVideo --codec=hevc demo.mp4
# Perform actions in simulator
# Press Ctrl+C to stop
```

### Capture specific simulator

```bash
# Get UDID of specific device
UDID=$(xcrun simctl list devices booted --json | jq -r '.devices | to_entries[] | .value[] | select(.name == "iPhone 15 Pro") | .udid')

# Take screenshot
xcrun simctl io "$UDID" screenshot iphone15pro.png
```

## Multiple Booted Simulators

When multiple simulators are booted, specify the exact UDID:

```bash
# List booted simulators with UDIDs
xcrun simctl list devices booted

# Screenshot specific device
xcrun simctl io A1B2C3D4-E5F6-7890-ABCD-EF1234567890 screenshot output.png
```

## Output Formats

### Screenshots
- **PNG** (default) - Best quality, lossless
- **JPEG** - Smaller file size, lossy
- **TIFF** - High quality, large files
- **BMP** - Uncompressed
- **GIF** - Limited colors

### Videos
- **MP4 with H.264** - Wide compatibility
- **MP4 with HEVC** - Better compression, newer devices

## Error Handling

### No booted simulator

```bash
# Check for booted simulators
xcrun simctl list devices booted

# Boot a simulator first
xcrun simctl boot "iPhone 15 Pro"
```

### Permission denied

Ensure the output directory is writable:
```bash
mkdir -p ~/Screenshots
xcrun simctl io booted screenshot ~/Screenshots/output.png
```

### File already exists

Use `--force` to overwrite:
```bash
xcrun simctl io booted recordVideo --force existing.mp4
```

## Integration with Testing

### Capture on test failure

In test scripts:
```bash
if [ $? -ne 0 ]; then
  xcrun simctl io booted screenshot "failure_$(date +%s).png"
fi
```

### Automated screenshot capture

```bash
for device in "iPhone 15 Pro" "iPad Pro (12.9-inch)"; do
  xcrun simctl boot "$device"
  sleep 5
  xcrun simctl io booted screenshot "${device// /_}.png"
  xcrun simctl shutdown "$device"
done
```
