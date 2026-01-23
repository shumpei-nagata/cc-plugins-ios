---
name: simulator-boot
description: This skill should be used when the user asks to "boot simulator", "start simulator", "launch simulator", "shutdown simulator", "stop simulator", "restart simulator", "シミュレータを起動", "シミュレータを終了", "シミュレータを再起動", or needs to control the running state of iOS/watchOS/tvOS/visionOS simulators.
context: fork
---

# Boot/Shutdown iOS Simulators

Control the running state of iOS, watchOS, tvOS, and visionOS simulators using `xcrun simctl`.

## Purpose

Manage simulator lifecycle operations:
- Boot (start) a simulator device
- Shutdown (stop) a running simulator
- Restart a simulator
- Open Simulator.app with a specific device

## Workflow

1. Identify the target simulator by name or UDID
2. Check current state if needed (`xcrun simctl list devices`)
3. Execute boot/shutdown/restart command
4. Verify the operation completed successfully

## Command Reference

### Boot a Simulator

By UDID:
```bash
xcrun simctl boot <UDID>
```

By device name (finds first matching device):
```bash
xcrun simctl boot "iPhone 15 Pro"
```

### Shutdown a Simulator

By UDID:
```bash
xcrun simctl shutdown <UDID>
```

By device name:
```bash
xcrun simctl shutdown "iPhone 15 Pro"
```

Shutdown all booted simulators:
```bash
xcrun simctl shutdown all
```

### Restart a Simulator

Shutdown then boot:
```bash
xcrun simctl shutdown <UDID> && xcrun simctl boot <UDID>
```

### Open Simulator.app

Open Simulator.app with default device:
```bash
open -a Simulator
```

Boot and open specific device:
```bash
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator
```

## Check Current State

List booted simulators:
```bash
xcrun simctl list devices booted
```

Check if specific device is booted:
```bash
xcrun simctl list devices | grep "iPhone 15 Pro"
```

## Common Scenarios

### Boot simulator for testing

```bash
# Boot the simulator
xcrun simctl boot "iPhone 15 Pro"

# Open Simulator.app to see the UI
open -a Simulator
```

### Clean restart

```bash
# Shutdown all, then boot specific device
xcrun simctl shutdown all
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator
```

### Boot multiple simulators

```bash
xcrun simctl boot "iPhone 15 Pro"
xcrun simctl boot "iPad Pro (12.9-inch) (6th generation)"
open -a Simulator
```

## Error Handling

### Already booted

If device is already booted, `simctl boot` returns error. Check state first:
```bash
xcrun simctl list devices booted | grep -q "iPhone 15 Pro" || xcrun simctl boot "iPhone 15 Pro"
```

### Device not found

Verify device exists:
```bash
xcrun simctl list devices available | grep -i "iPhone 15"
```

### Unable to boot

Ensure Xcode command line tools are properly configured:
```bash
xcode-select -p
```

## Erase and Boot

Reset simulator to clean state before booting:
```bash
xcrun simctl erase <UDID>
xcrun simctl boot <UDID>
```

Erase all simulators:
```bash
xcrun simctl erase all
```
