---
name: build-ios-app
description: This skill should be used when the user asks to "build the app", "build iOS app", "compile the project", "run xcodebuild", "build for simulator", "build for device", or needs to build an Xcode project or workspace.
context: fork
---

# Build iOS App

Build an iOS, watchOS, tvOS, or visionOS app using `xcodebuild`.

## Purpose

Execute Xcode builds with specified configuration. Use this skill to:
- Build apps for simulator or device
- Build specific schemes with specific configurations
- Verify code compiles successfully before testing

## Usage

Run the build script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-ios-app/scripts/build.py \
    --project <path> \
    --scheme <scheme-name> \
    --destination <destination>
```

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--project` | Path to .xcodeproj, .xcworkspace, or directory containing Package.swift | `./MyApp.xcworkspace` |
| `--scheme` | Scheme name to build | `MyApp` |
| `--destination` | Build destination | `platform=iOS Simulator,name=iPhone 15 Pro` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--configuration` | Build configuration | `Debug` |
| `--derived-data` | Derived data path | System default |

## Examples

### Build for Simulator

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-ios-app/scripts/build.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro"
```

### Build for Device

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-ios-app/scripts/build.py \
    --project ./MyApp.xcodeproj \
    --scheme MyApp \
    --destination "generic/platform=iOS"
```

### Build Swift Package

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-ios-app/scripts/build.py \
    --project . \
    --scheme MyPackage \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro"
```

### Build with Release Configuration

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-ios-app/scripts/build.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "generic/platform=iOS" \
    --configuration Release
```

## Common Destinations

### iOS Simulator
```
platform=iOS Simulator,name=iPhone 15 Pro
platform=iOS Simulator,id=<UDID>
```

### iOS Device (Generic)
```
generic/platform=iOS
```

### macOS
```
platform=macOS
```

### watchOS Simulator
```
platform=watchOS Simulator,name=Apple Watch Series 9 (45mm)
```

### visionOS Simulator
```
platform=visionOS Simulator,name=Apple Vision Pro
```

## Output

The script outputs JSON:

### Success
```json
{
  "success": true,
  "duration_seconds": 45.2,
  "scheme": "MyApp",
  "configuration": "Debug",
  "destination": "platform=iOS Simulator,name=iPhone 15 Pro"
}
```

### Failure
```json
{
  "success": false,
  "error": "Build failed",
  "details": "error: ...",
  "duration_seconds": 12.5
}
```

## Auto-Detection Workflow

If project path is not specified:

1. Search for `.xcworkspace` files (preferred)
2. Search for `.xcodeproj` files
3. Check for `Package.swift` (Swift Package)

Use the `list-xcode-schemes` skill to find available schemes before building.
