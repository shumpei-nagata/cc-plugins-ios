---
name: list-xcode-schemes
description: This skill should be used when the user asks to "list schemes", "show available schemes", "find Xcode schemes", "get project schemes", "check workspace schemes", or needs to know which build schemes are available in an Xcode project (.xcodeproj) or workspace (.xcworkspace).
---

# List Xcode Schemes

List available schemes, targets, and build configurations from an Xcode project or workspace.

## Purpose

Retrieve scheme information from Xcode projects. Use this skill to:
- Find available schemes before building or testing
- Discover targets and build configurations
- Identify the correct scheme name for build/test commands

## Usage

Run the script with the path to the project or workspace:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/list-xcode-schemes/scripts/list_schemes.py <path>
```

### Examples

```bash
# For a project
python3 ${CLAUDE_PLUGIN_ROOT}/skills/list-xcode-schemes/scripts/list_schemes.py /path/to/MyApp.xcodeproj

# For a workspace
python3 ${CLAUDE_PLUGIN_ROOT}/skills/list-xcode-schemes/scripts/list_schemes.py /path/to/MyApp.xcworkspace
```

## Output Format

The script outputs JSON with the following structure:

```json
{
  "schemes": ["MyApp", "MyAppTests", "MyAppUITests"],
  "targets": ["MyApp", "MyAppTests", "MyAppUITests"],
  "configurations": ["Debug", "Release"]
}
```

## Error Handling

On error, the script returns:

```json
{
  "error": "Error message describing the issue"
}
```

Common errors:
- Path does not exist
- Invalid path (not .xcodeproj or .xcworkspace)
- xcodebuild command failed

## Auto-Detection

If no project/workspace path is specified, search for them in the current directory:

```bash
# Find .xcworkspace files (prefer workspace over project)
find . -maxdepth 2 -name "*.xcworkspace" -not -path "*/.*"

# Find .xcodeproj files
find . -maxdepth 2 -name "*.xcodeproj" -not -path "*/.*"

# Find Swift Package (Package.swift)
find . -maxdepth 2 -name "Package.swift"
```

Priority order:
1. `.xcworkspace` (may contain multiple projects)
2. `.xcodeproj` (single project)
3. `Package.swift` (Swift Package Manager)
