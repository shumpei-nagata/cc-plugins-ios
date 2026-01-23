# cc-plugins-ios

iOS development plugin for Claude Code providing comprehensive skills for building, testing, and managing iOS applications.

## Overview

This repository contains the `ios-dev` plugin - a unified collection of skills that enables Claude Code to assist with iOS development workflows including:

- **Build Management**: Build iOS apps, list Xcode schemes, and run tests
- **Simulator Control**: Create, boot, delete, list, and capture screenshots of iOS simulators

## Plugin Structure

```
ios-dev/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── build/
    │   ├── build-ios-app/
    │   ├── list-xcode-schemes/
    │   └── test-ios-app/
    └── simulator/
        ├── boot-simulator/
        ├── create-simulator/
        ├── delete-simulator/
        ├── list-simulators/
        └── screenshot-simulator/
```

## Installation

Install the plugin using Claude Code:

```bash
claude-code plugin add /path/to/cc-plugins-ios/ios-dev
```

## Skills

### Build Category

- **build-ios-app**: Build iOS applications using xcodebuild
- **list-xcode-schemes**: List available Xcode schemes in a project
- **test-ios-app**: Run iOS app tests on simulators

### Simulator Category

- **boot-simulator**: Boot an iOS simulator
- **create-simulator**: Create a new iOS simulator
- **delete-simulator**: Delete an iOS simulator
- **list-simulators**: List all available iOS simulators
- **screenshot-simulator**: Capture screenshots from running simulators

## Requirements

- macOS with Xcode installed
- Xcode Command Line Tools
- Claude Code CLI

## Usage

Once installed, Claude Code can automatically use these skills when helping with iOS development tasks. Simply ask Claude to build your app, run tests, or manage simulators, and it will use the appropriate skills.
