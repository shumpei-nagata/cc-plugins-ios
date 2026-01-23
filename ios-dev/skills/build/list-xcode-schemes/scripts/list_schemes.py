#!/usr/bin/env python3
"""
List available Xcode schemes from a project or workspace.

Usage:
    python3 list_schemes.py <path-to-project-or-workspace>
"""

import json
import subprocess
import sys
from pathlib import Path


def parse_xcodebuild_output(output: str) -> dict:
    """Parse xcodebuild -list output and extract targets, configurations, and schemes."""
    result = {
        "targets": [],
        "configurations": [],
        "schemes": []
    }

    current_section = None

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Targets:"):
            current_section = "targets"
        elif line.startswith("Build Configurations:"):
            current_section = "configurations"
        elif line.startswith("Schemes:"):
            current_section = "schemes"
        elif line.startswith("If no build configuration"):
            current_section = None
        elif line and current_section:
            result[current_section].append(line)

    return result


def list_schemes(project_path: str) -> dict:
    """Run xcodebuild -list and parse the output."""
    path = Path(project_path)

    if not path.exists():
        return {"error": f"Path does not exist: {project_path}"}

    if path.suffix == ".xcodeproj":
        cmd = ["xcodebuild", "-list", "-project", str(path)]
    elif path.suffix == ".xcworkspace":
        cmd = ["xcodebuild", "-list", "-workspace", str(path)]
    else:
        return {"error": f"Invalid path: must be .xcodeproj or .xcworkspace, got {path.suffix}"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            return {"error": f"xcodebuild failed: {result.stderr}"}

        return parse_xcodebuild_output(result.stdout)

    except subprocess.TimeoutExpired:
        return {"error": "xcodebuild timed out"}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 list_schemes.py <path-to-project-or-workspace>", file=sys.stderr)
        sys.exit(1)

    project_path = sys.argv[1]
    result = list_schemes(project_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
