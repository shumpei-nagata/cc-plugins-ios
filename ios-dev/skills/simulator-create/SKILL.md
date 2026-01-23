---
name: simulator-create
description: This skill should be used when the user asks to "create simulator", "add simulator", "make new simulator", "create new device", "シミュレータを作成", "シミュレータを追加", "新しいシミュレータ", or needs to create a new iOS/watchOS/tvOS/visionOS simulator device with specific device type and runtime.
context: fork
---

# Create iOS Simulators

Create new iOS, watchOS, tvOS, and visionOS simulator devices using `xcrun simctl`.

## Purpose

Create new simulator devices:
- Create a simulator with specific device type and iOS version
- Clone an existing simulator configuration
- Set up testing environments with multiple device types

## Workflow

1. List available device types and runtimes
2. Select desired device type and runtime
3. Create the simulator with a custom name
4. Verify creation and optionally boot the device

## Command Reference

### Create a New Simulator

```bash
xcrun simctl create "<name>" "<device type>" "<runtime>"
```

Example:
```bash
xcrun simctl create "My iPhone 15" "iPhone 15 Pro" "iOS 18.2"
```

### List Available Device Types

```bash
xcrun simctl list devicetypes
```

Example output:
```
== Device Types ==
iPhone 14 (com.apple.CoreSimulator.SimDeviceType.iPhone-14)
iPhone 14 Plus (com.apple.CoreSimulator.SimDeviceType.iPhone-14-Plus)
iPhone 15 Pro (com.apple.CoreSimulator.SimDeviceType.iPhone-15-Pro)
...
```

### List Available Runtimes

```bash
xcrun simctl list runtimes
```

Example output:
```
== Runtimes ==
iOS 17.5 (17.5 - 21F79) - com.apple.CoreSimulator.SimRuntime.iOS-17-5
iOS 18.2 (18.2 - 22C150) - com.apple.CoreSimulator.SimRuntime.iOS-18-2
...
```

## Using Identifiers

For reliability, use full identifiers instead of display names:

```bash
xcrun simctl create "Test iPhone" \
  com.apple.CoreSimulator.SimDeviceType.iPhone-15-Pro \
  com.apple.CoreSimulator.SimRuntime.iOS-18-2
```

## Common Scenarios

### Create iPhone simulator with latest iOS

```bash
# List device types to find exact name
xcrun simctl list devicetypes | grep -i "iPhone 15"

# List runtimes to find iOS version
xcrun simctl list runtimes | grep -i "iOS 18"

# Create the simulator
xcrun simctl create "Test iPhone 15 Pro" "iPhone 15 Pro" "iOS 18.2"
```

### Create iPad simulator

```bash
xcrun simctl create "Test iPad Pro" "iPad Pro (12.9-inch) (6th generation)" "iOS 18.2"
```

### Create Apple Watch simulator

```bash
xcrun simctl create "Test Watch" "Apple Watch Series 9 (45mm)" "watchOS 11.2"
```

### Create Apple Vision Pro simulator

```bash
xcrun simctl create "Test Vision Pro" "Apple Vision Pro" "visionOS 2.2"
```

### Create and boot immediately

```bash
# Create and capture UDID
UDID=$(xcrun simctl create "My Test Device" "iPhone 15 Pro" "iOS 18.2")

# Boot the new simulator
xcrun simctl boot "$UDID"

# Open Simulator.app
open -a Simulator
```

## Clone Existing Simulator

Clone a simulator to create an identical copy:
```bash
xcrun simctl clone <source-UDID> "<new-name>"
```

Example:
```bash
xcrun simctl clone A1B2C3D4-E5F6-7890-ABCD-EF1234567890 "iPhone 15 Pro Clone"
```

## Verify Creation

After creating, verify the simulator exists:
```bash
xcrun simctl list devices | grep -i "My Test"
```

## Error Handling

### Invalid device type

Check available device types:
```bash
xcrun simctl list devicetypes
```

### Invalid runtime

Check available runtimes:
```bash
xcrun simctl list runtimes
```

### Runtime not installed

Download additional simulators in Xcode:
- Xcode > Settings > Platforms
- Click "+" to add new simulator runtimes

## Naming Conventions

Use descriptive names for easy identification:
- `"Test - iPhone 15 Pro - iOS 18"` - Testing purpose
- `"Debug - iPad Pro"` - Development purpose
- `"CI - iPhone 14"` - CI/CD environment
