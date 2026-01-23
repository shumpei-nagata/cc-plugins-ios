---
name: delete-simulator
description: This skill should be used when the user asks to "delete simulator", "remove simulator", "clean up simulators", "delete unavailable simulators", "シミュレータを削除", "シミュレータを消す", "不要なシミュレータを削除", or needs to remove simulator devices or clean up unavailable/orphaned simulators.
---

# Delete iOS Simulators

Delete iOS, watchOS, tvOS, and visionOS simulator devices using `xcrun simctl`.

## Purpose

Remove simulator devices from the system:
- Delete specific simulator by name or UDID
- Clean up unavailable (orphaned) simulators
- Remove all simulators of a specific device type
- Free up disk space by removing unused simulators

## Workflow

1. Identify simulators to delete (list current devices first)
2. Confirm the target devices
3. Execute delete command
4. Verify deletion completed

## Command Reference

### Delete Specific Simulator

By UDID:
```bash
xcrun simctl delete <UDID>
```

By device name:
```bash
xcrun simctl delete "iPhone 15 Pro"
```

### Delete Unavailable Simulators

Remove all simulators that reference unavailable runtimes:
```bash
xcrun simctl delete unavailable
```

### Delete All Simulators

**Warning: This removes ALL simulator devices**
```bash
xcrun simctl delete all
```

## Safe Deletion Workflow

### Step 1: List current simulators

```bash
xcrun simctl list devices
```

### Step 2: Identify unavailable simulators

Look for devices marked as `(unavailable)` or under runtimes that are no longer installed.

### Step 3: Delete unavailable devices

```bash
xcrun simctl delete unavailable
```

### Step 4: Verify deletion

```bash
xcrun simctl list devices
```

## Common Scenarios

### Clean up after Xcode update

After upgrading Xcode, old runtime simulators become unavailable:
```bash
# Show unavailable devices
xcrun simctl list devices unavailable

# Remove them
xcrun simctl delete unavailable
```

### Remove duplicate simulators

Find duplicates by name, then delete by UDID:
```bash
# List all devices with UDIDs
xcrun simctl list devices available

# Delete specific duplicate by UDID
xcrun simctl delete A1B2C3D4-E5F6-7890-ABCD-EF1234567890
```

### Free up disk space

Simulator data can consume significant disk space:
```bash
# Delete unavailable simulators
xcrun simctl delete unavailable

# Check remaining simulators
xcrun simctl list devices
```

## Data Location

Simulator data is stored in:
```
~/Library/Developer/CoreSimulator/Devices/
```

Each simulator has a directory named by its UDID. Deleting a simulator removes this directory.

## Warning

- Deleted simulators cannot be recovered
- App data and settings in the simulator are lost
- Always verify the target device before deletion
- Consider using `simctl erase` to reset a simulator instead of deleting it

## Checking Disk Usage

View disk usage by simulator:
```bash
du -sh ~/Library/Developer/CoreSimulator/Devices/*
```

Total simulator storage:
```bash
du -sh ~/Library/Developer/CoreSimulator/
```
