---
name: swiftlint
description: This skill should be used when the user asks to "run SwiftLint", "lint Swift code", "fix Swift lint errors", "format Swift code with SwiftLint", "check Swift code style", "auto-fix lint issues", or needs to run SwiftLint with --fix or --format options. Requires swiftlint_path and config_path to be provided by the caller.
context: fork
---

# SwiftLint

Run SwiftLint to analyze and fix Swift code style issues.

## Purpose

Execute SwiftLint with various modes including lint-only, auto-fix, and format. Use this skill to:
- Check Swift code for style violations
- Auto-fix correctable issues with `--fix`
- Format code with `--format`
- Run both fix and format together

## Prerequisites

This skill requires two paths to be provided by the caller:
- **swiftlint_path**: Path to the SwiftLint executable
- **config_path**: Path to the SwiftLint configuration file (.swiftlint.yml)

## Usage

Run the SwiftLint script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path <path-to-swiftlint> \
    --config-path <path-to-config> \
    [options]
```

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--swiftlint-path` | Path to SwiftLint executable | `/opt/homebrew/bin/swiftlint` |
| `--config-path` | Path to .swiftlint.yml config file | `./project/.swiftlint.yml` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--path` | Target path to lint (file or directory) | Current directory |
| `--fix` | Auto-fix correctable violations | Disabled |
| `--format` | Format code (whitespace/indentation) | Disabled |
| `--strict` | Treat warnings as errors | Disabled |
| `--quiet` | Only output errors | Disabled |

## Examples

### Lint Only (Check for Issues)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources
```

### Auto-Fix Issues

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources \
    --fix
```

### Format Code

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources \
    --format
```

### Fix and Format Together

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources \
    --fix \
    --format
```

### Lint Single File

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources/MyFile.swift \
    --fix
```

### Strict Mode (Warnings as Errors)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --strict
```

## Output

The script outputs JSON with detailed results:

### Success (No Violations)
```json
{
  "success": true,
  "mode": "lint",
  "violations_count": 0,
  "warnings_count": 0,
  "errors_count": 0,
  "violations": [],
  "target_path": "./Sources"
}
```

### Success with Violations
```json
{
  "success": true,
  "mode": "lint",
  "violations_count": 3,
  "warnings_count": 2,
  "errors_count": 1,
  "violations": [
    {
      "file": "Sources/MyFile.swift",
      "line": 10,
      "column": 5,
      "severity": "warning",
      "rule": "trailing_whitespace",
      "message": "Lines should not have trailing whitespace."
    }
  ],
  "target_path": "./Sources"
}
```

### Fix/Format Mode
```json
{
  "success": true,
  "mode": "fix_and_format",
  "fix_applied": true,
  "format_applied": true,
  "violations_count": 0,
  "violations": [],
  "target_path": "./Sources"
}
```

### Failure
```json
{
  "success": false,
  "error": "SwiftLint executable not found",
  "details": "Path does not exist: /invalid/path/swiftlint"
}
```

## Workflow Recommendations

### Before Committing Code
1. Run with `--fix --format` to auto-correct issues
2. Run lint-only to verify remaining issues
3. Manually fix any issues that couldn't be auto-corrected

### CI/CD Integration
Use `--strict` mode to fail builds on any warnings.

## Common SwiftLint Rules

| Rule | Description | Auto-fixable |
|------|-------------|--------------|
| `trailing_whitespace` | No trailing whitespace | Yes |
| `vertical_whitespace` | Limit blank lines | Yes |
| `opening_brace` | Opening brace spacing | Yes |
| `closing_brace` | Closing brace spacing | Yes |
| `colon` | Colon spacing | Yes |
| `comma` | Comma spacing | Yes |
| `force_cast` | Avoid force casts | No |
| `force_unwrapping` | Avoid force unwraps | No |
| `line_length` | Line length limits | No |
