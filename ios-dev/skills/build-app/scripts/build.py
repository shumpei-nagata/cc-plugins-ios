#!/usr/bin/env python3
"""
Build an iOS app using xcodebuild.

Usage:
    python3 build.py --project <path> --scheme <name> --destination <dest> [options]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def find_project() -> tuple[str, str] | None:
    """Auto-detect project/workspace in current directory."""
    cwd = Path.cwd()

    # Priority 1: .xcworkspace
    workspaces = list(cwd.glob("*.xcworkspace"))
    if workspaces:
        # Exclude .xcworkspace inside .xcodeproj
        workspaces = [w for w in workspaces if ".xcodeproj" not in str(w)]
        if workspaces:
            return str(workspaces[0]), "workspace"

    # Priority 2: .xcodeproj
    projects = list(cwd.glob("*.xcodeproj"))
    if projects:
        return str(projects[0]), "project"

    # Priority 3: Package.swift
    if (cwd / "Package.swift").exists():
        return str(cwd), "package"

    return None


def build_app(
    project_path: str,
    scheme: str,
    destination: str,
    configuration: str = "Debug",
    derived_data: str | None = None
) -> dict:
    """Run xcodebuild to build the app."""
    path = Path(project_path)

    # Determine project type
    if path.suffix == ".xcworkspace":
        project_args = ["-workspace", str(path)]
    elif path.suffix == ".xcodeproj":
        project_args = ["-project", str(path)]
    elif path.is_dir() and (path / "Package.swift").exists():
        # Swift Package - use package path
        project_args = []
    else:
        return {"success": False, "error": f"Invalid project path: {project_path}"}

    # Build command
    cmd = [
        "xcodebuild",
        *project_args,
        "-scheme", scheme,
        "-destination", destination,
        "-configuration", configuration,
        "-quiet",
        "build"
    ]

    if derived_data:
        cmd.extend(["-derivedDataPath", derived_data])

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=str(path) if path.is_dir() and not path.suffix else None
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "scheme": scheme,
                "configuration": configuration,
                "destination": destination
            }
        else:
            return {
                "success": False,
                "error": "Build failed",
                "details": result.stderr or result.stdout,
                "duration_seconds": round(duration, 2)
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Build timed out after 10 minutes"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Build iOS app using xcodebuild")
    parser.add_argument("--project", help="Path to .xcodeproj, .xcworkspace, or package directory")
    parser.add_argument("--scheme", required=True, help="Scheme name to build")
    parser.add_argument("--destination", required=True, help="Build destination")
    parser.add_argument("--configuration", default="Debug", help="Build configuration (default: Debug)")
    parser.add_argument("--derived-data", help="Derived data path")

    args = parser.parse_args()

    # Auto-detect project if not specified
    project_path = args.project
    if not project_path:
        detected = find_project()
        if detected:
            project_path = detected[0]
        else:
            print(json.dumps({
                "success": False,
                "error": "No project found. Specify --project path."
            }, indent=2))
            sys.exit(1)

    result = build_app(
        project_path=project_path,
        scheme=args.scheme,
        destination=args.destination,
        configuration=args.configuration,
        derived_data=args.derived_data
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
