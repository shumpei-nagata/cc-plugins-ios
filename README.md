# cc-plugins-ios

iOS development plugin for Claude Code providing comprehensive skills for building, testing, and managing iOS applications.

## Overview

This repository contains the `ios-dev` plugin - a unified collection of skills that enables Claude Code to assist with iOS development workflows including:

- **Build Management**: Build iOS apps, list Xcode schemes, and run tests
- **Simulator Control**: Create, boot, delete, list, and capture screenshots of iOS simulators
- **Code Quality**: Run SwiftLint for code style checking and auto-fixing

## Plugin Structure

```
ios-dev/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── build-app/
    ├── build-list-schemes/
    ├── build-test/
    ├── simulator-boot/
    ├── simulator-create/
    ├── simulator-delete/
    ├── simulator-list/
    ├── simulator-screenshot/
    └── swiftlint/
```

## Installation

### From Marketplace (Recommended)

1. Add the marketplace:
```
/plugin marketplace add shumpei-nagata/cc-plugins-ios
```

2. Install the plugin:
```
/plugin install ios-dev@cc-plugins-ios
```

### From Local Path

```bash
claude-code plugin add /path/to/cc-plugins-ios/ios-dev
```

## Skills

### Build

- **build-app**: Build iOS applications using xcodebuild
- **build-list-schemes**: List available Xcode schemes in a project
- **build-test**: Run iOS app tests on simulators

### Simulator

- **simulator-boot**: Boot an iOS simulator
- **simulator-create**: Create a new iOS simulator
- **simulator-delete**: Delete an iOS simulator
- **simulator-list**: List all available iOS simulators
- **simulator-screenshot**: Capture screenshots from running simulators

### Code Quality

- **swiftlint**: Run SwiftLint for code style checking, auto-fixing, and formatting

## Requirements

- macOS with Xcode installed
- Xcode Command Line Tools
- Python 3.8+
- Claude Code CLI

## Usage

Once installed, Claude Code can automatically use these skills when helping with iOS development tasks. Simply ask Claude to build your app, run tests, or manage simulators, and it will use the appropriate skills.
