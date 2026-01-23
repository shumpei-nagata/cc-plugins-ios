---
name: build-test
description: This skill should be used when the user asks to "run tests", "execute tests", "run unit tests", "run UI tests", "test the app", "xcodebuild test", or needs to run Xcode tests for an iOS, watchOS, tvOS, or visionOS app.
context: fork
---

# Test iOS App

Run tests for an iOS, watchOS, tvOS, or visionOS app using `xcodebuild test`.

## Purpose

Execute Xcode tests with specified configuration. Use this skill to:
- Run unit tests and UI tests
- Run specific test classes or methods
- Parse xcresult for detailed test results

## Usage

Run the test script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project <path> \
    --scheme <scheme-name> \
    --destination <destination>
```

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--project` | Path to .xcodeproj, .xcworkspace, or directory | `./MyApp.xcworkspace` |
| `--scheme` | Scheme name containing tests | `MyApp` |
| `--destination` | Test destination | `platform=iOS Simulator,name=iPhone 15 Pro` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--test-plan` | Test plan name | None (use scheme default) |
| `--only-testing` | Run specific tests only | None (all tests) |
| `--skip-testing` | Skip specific tests | None |
| `--parallel` | Enable parallel testing | False |
| `--result-path` | Path for xcresult bundle | Auto-generated |

## Examples

### Run All Tests

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro"
```

### Run Specific Test Class

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro" \
    --only-testing "MyAppTests/LoginTests"
```

### Run Specific Test Method

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro" \
    --only-testing "MyAppTests/LoginTests/testValidLogin"
```

### Run UI Tests Only

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyAppUITests \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro"
```

### Run Tests in Parallel

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro" \
    --parallel
```

### Skip Specific Tests

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-test/scripts/test.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS Simulator,name=iPhone 15 Pro" \
    --skip-testing "MyAppTests/SlowTests"
```

## Test Identifier Format

Test identifiers follow this format:
- **Test bundle**: `MyAppTests`
- **Test class**: `MyAppTests/LoginTests`
- **Test method**: `MyAppTests/LoginTests/testValidLogin`

Multiple tests can be specified by repeating `--only-testing`:

```bash
--only-testing "MyAppTests/LoginTests" --only-testing "MyAppTests/SignupTests"
```

## Output

The script outputs JSON with test results:

### Success
```json
{
  "success": true,
  "duration_seconds": 120.5,
  "test_summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0
  },
  "failed_tests": [
    {
      "name": "testInvalidLogin",
      "class": "LoginTests",
      "bundle": "MyAppTests",
      "failure_message": "XCTAssertEqual failed: (\"error\") is not equal to (\"success\")"
    }
  ],
  "xcresult_path": "/path/to/Test.xcresult"
}
```

### Failure
```json
{
  "success": false,
  "error": "Tests failed",
  "test_summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0
  },
  "failed_tests": [...],
  "xcresult_path": "/path/to/Test.xcresult"
}
```

## xcresult Analysis

The script automatically parses the xcresult bundle using `xcresulttool` to extract:
- Total test count
- Passed/failed/skipped counts
- Failed test details with failure messages
- Test duration

For deeper analysis of xcresult, use:

```bash
xcrun xcresulttool get --path /path/to/Test.xcresult --format json
```

## Auto-Detection Workflow

If project path is not specified:

1. Search for `.xcworkspace` files (preferred)
2. Search for `.xcodeproj` files
3. Check for `Package.swift` (Swift Package)

Use the `list-xcode-schemes` skill to find available test schemes.
