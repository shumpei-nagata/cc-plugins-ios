# ios-build-tools

iOS app build and test execution skills for Claude Code.

## Skills

| Skill | Description |
|-------|-------------|
| `list-ios-simulators` | List available iOS/watchOS/tvOS/visionOS simulators |
| `list-xcode-schemes` | List schemes, targets, and configurations from Xcode projects |
| `build-ios-app` | Build iOS apps using xcodebuild |
| `test-ios-app` | Run tests and parse xcresult for detailed results |

## Requirements

- macOS with Xcode installed
- Python 3.9+
- Xcode Command Line Tools (`xcode-select --install`)

## Installation

### Local Development

```bash
claude --plugin-dir /path/to/ios-build-tools
```

### Project-specific

Copy the plugin to your project's `.claude-plugin/` directory.

## Usage Examples

### List Simulators

Ask Claude: "List available iOS simulators" or "Show me iPhone 15 simulators"

### List Schemes

Ask Claude: "What schemes are available in this project?" or "List Xcode schemes"

### Build App

Ask Claude: "Build the app for iPhone 15 Pro simulator" or "Build MyApp scheme"

### Run Tests

Ask Claude: "Run the tests" or "Run unit tests for LoginTests class"

## Skill Details

### list-ios-simulators

Uses `xcrun simctl list devices available` to retrieve simulator information.

### list-xcode-schemes

Uses Python script to parse `xcodebuild -list` output and return JSON:

```json
{
  "schemes": ["MyApp", "MyAppTests"],
  "targets": ["MyApp", "MyAppTests"],
  "configurations": ["Debug", "Release"]
}
```

### build-ios-app

Executes `xcodebuild build` with specified scheme, destination, and configuration.

Parameters:
- `--project`: Path to .xcodeproj, .xcworkspace, or package directory
- `--scheme`: Scheme name to build
- `--destination`: Build destination (e.g., "platform=iOS Simulator,name=iPhone 15 Pro")
- `--configuration`: Build configuration (default: Debug)

### test-ios-app

Executes `xcodebuild test` and parses xcresult for detailed test results.

Parameters:
- `--project`: Path to .xcodeproj, .xcworkspace, or package directory
- `--scheme`: Scheme name to test
- `--destination`: Test destination
- `--only-testing`: Run specific tests only
- `--skip-testing`: Skip specific tests
- `--parallel`: Enable parallel testing

Output includes:
- Test summary (total, passed, failed, skipped)
- Failed test details with failure messages
- Path to xcresult bundle

## License

MIT
