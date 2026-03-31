---
name: swiftlint
description: This skill should be used when the user asks to "run SwiftLint", "lint Swift code", "fix Swift lint errors", "format Swift code with SwiftLint", "check Swift code style", "auto-fix lint issues", "list SwiftLint rules", "show SwiftLint rule details", or needs to run SwiftLint with --fix, --format, or --rules options. Requires swiftlint_path to be provided by the caller.
context: fork
---

# SwiftLint

Run SwiftLint to analyze and fix Swift code style issues, and inspect available rules.

## Purpose

Execute SwiftLint with various modes including lint-only, auto-fix, fix+format, and rules inspection. Use this skill to:
- Check Swift code for style violations
- Auto-fix correctable issues with `--fix`
- Format code with `--fix --format`
- Run both fix and format together
- List all available SwiftLint rules with `--rules`
- Show detailed information about a specific rule with `--rules --rule-id <rule_id>`

## Prerequisites

- **swiftlint_path**: Path to the SwiftLint executable (required for all modes)
- **config_path**: Path to the SwiftLint configuration file (.swiftlint.yml) — required for lint/fix/format; optional for rules inspection

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
| `--path` | Target path to lint (file or directory). Can be specified multiple times. The script passes these to `swiftlint lint` as positional paths. | Current directory |
| `--fix` | Auto-fix correctable violations | Disabled |
| `--format` | Format code. Requires `--fix` with current SwiftLint versions. | Disabled |
| `--strict` | Treat warnings as errors | Disabled |
| `--quiet` | Only output errors | Disabled |
| `--rules` | List all rules or show details for a specific rule | Disabled |
| `--rule-id` | Rule identifier to inspect (use with `--rules`) | — |

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

### Fix and Format Code

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

### Lint Multiple Paths

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --path ./Sources \
    --path ./Tests
```

### List All Rules

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --rules
```

### List Rules Filtered by Config

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --config-path ./project/.swiftlint.yml \
    --rules
```

### Show Details for a Specific Rule

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/swiftlint/scripts/swiftlint.py \
    --swiftlint-path /opt/homebrew/bin/swiftlint \
    --rules \
    --rule-id trailing_whitespace
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
  "target_path": "./Sources",
  "target_paths": ["./Sources"]
}
```

### Rules Output
```json
{
  "success": true,
  "rule_id": null,
  "output": "+---------------------------+--------+-------------+...\n| identifier ..."
}
```

When `--rule-id` is specified, `output` contains detailed configuration and description for that rule.

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
