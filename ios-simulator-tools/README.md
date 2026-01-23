# ios-simulator-tools

iOS Simulator management skills for Claude Code.

## Features

- **list-simulators** - List and filter available iOS/watchOS/tvOS/visionOS simulators
- **boot-simulator** - Boot, shutdown, and restart simulators
- **create-simulator** - Create new simulator devices
- **delete-simulator** - Delete simulators and clean up unavailable devices
- **screenshot-simulator** - Capture screenshots and screen recordings

## Requirements

- macOS with Xcode installed
- `xcrun simctl` command available

## Installation

Add this plugin to your Claude Code configuration:

```bash
cc --plugin-dir /path/to/ios-simulator-tools
```

## Usage

The skills are triggered automatically based on your queries:

- "Show available iPhone simulators"
- "Boot the iPhone 15 Pro simulator"
- "Create a new iPad simulator with iOS 18"
- "Delete all unavailable simulators"
- "Take a screenshot of the booted simulator"

## Skills

### list-simulators

List available simulators with filtering options by device name, OS version, or device type.

### boot-simulator

Boot, shutdown, or restart simulator devices. Supports multiple simulators.

### create-simulator

Create new simulator devices with specified device type and runtime.

### delete-simulator

Delete specific simulators or clean up all unavailable devices.

### screenshot-simulator

Capture screenshots or record video from running simulators.
