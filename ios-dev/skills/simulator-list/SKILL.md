---
name: simulator-list
description: This skill should be used when the user asks to "list simulators", "show available simulators", "find iOS simulators", "check simulator devices", "get simulator list", "シミュレータ一覧", "利用可能なシミュレータ", or needs to know which iOS/watchOS/tvOS/visionOS simulators are available for testing or running apps.
context: fork
---

# List iOS Simulators

List available iOS, watchOS, tvOS, and visionOS simulators using `xcrun simctl`.

## Purpose

Retrieve a list of available simulators on the system. Use this skill to:
- Find available simulator devices before building or testing
- Filter simulators by device name, OS version, or device type
- Get simulator UDIDs for destination specification
- Check simulator states (Booted/Shutdown)

## Workflow

1. Execute `xcrun simctl list devices available` to get available simulators
2. Apply filter conditions if specified (simulator name, OS version, device type)
3. Return results in a clear, readable format

## Command Reference

### List All Available Simulators

```bash
xcrun simctl list devices available
```

### List with JSON Output (for programmatic processing)

```bash
xcrun simctl list devices available --json
```

### List All Runtimes

```bash
xcrun simctl list runtimes
```

## Filter Patterns

### By Device Name

```bash
xcrun simctl list devices available | grep -i "iPhone 15"
```

### By OS Version

```bash
xcrun simctl list devices available | grep -A 50 "iOS 18"
```

### By Device Type

- iPhone: `grep -i "iPhone"`
- iPad: `grep -i "iPad"`
- Apple Watch: `grep -i "Apple Watch"`
- Apple TV: `grep -i "Apple TV"`
- Apple Vision Pro: `grep -i "Apple Vision"`

### By State

- Booted only: `grep "(Booted)"`
- Shutdown only: `grep "(Shutdown)"`

## Output Format

Present results including:
- Device name (e.g., "iPhone 15 Pro")
- UDID (e.g., "A1B2C3D4-E5F6-7890-ABCD-EF1234567890")
- OS version (from section header, e.g., "iOS 18.2")
- State (Booted/Shutdown)

## Example Output

```
== iOS 18.2 ==
    iPhone 15 (A1B2C3D4-...) (Shutdown)
    iPhone 15 Pro (E5F6G7H8-...) (Booted)
    iPhone 15 Pro Max (I9J0K1L2-...) (Shutdown)
== watchOS 11.2 ==
    Apple Watch Series 9 (45mm) (M3N4O5P6-...) (Shutdown)
```

## Destination String Format

When providing simulator information for build/test commands, format as:

```
-destination 'platform=iOS Simulator,id=<UDID>'
```

Or by name:

```
-destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

## Common Use Cases

### Find booted simulators

```bash
xcrun simctl list devices available | grep "(Booted)"
```

### Get UDID of specific device

```bash
xcrun simctl list devices available --json | jq -r '.devices | to_entries[] | .value[] | select(.name == "iPhone 15 Pro") | .udid'
```

### List device types available for creation

```bash
xcrun simctl list devicetypes
```
