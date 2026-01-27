#!/usr/bin/env python3
"""SwiftLint runner script for Claude Code plugin."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_swiftlint_output(output: str) -> List[Dict]:
    """Parse SwiftLint output into structured violations."""
    violations = []

    for line in output.strip().split('\n'):
        if not line:
            continue

        # SwiftLint format: file:line:column: severity: message (rule_id)
        # Example: /path/file.swift:10:5: warning: Line should not have trailing whitespace (trailing_whitespace)
        try:
            # Split by ': ' but preserve the rest
            parts = line.split(': ', 3)
            if len(parts) < 4:
                continue

            location = parts[0]  # file:line:column
            severity = parts[1]  # warning or error
            rest = parts[2] + ': ' + parts[3] if len(parts) > 3 else parts[2]

            # Parse location
            loc_parts = location.rsplit(':', 2)
            if len(loc_parts) < 3:
                continue

            file_path = loc_parts[0]
            line_num = int(loc_parts[1]) if loc_parts[1].isdigit() else 0
            column = int(loc_parts[2]) if loc_parts[2].isdigit() else 0

            # Parse rule from message
            rule_id = ""
            message = rest
            if ' (' in rest and rest.endswith(')'):
                message, rule_part = rest.rsplit(' (', 1)
                rule_id = rule_part.rstrip(')')

            violations.append({
                "file": file_path,
                "line": line_num,
                "column": column,
                "severity": severity.lower(),
                "rule": rule_id,
                "message": message
            })
        except (ValueError, IndexError):
            continue

    return violations


def run_swiftlint(
    swiftlint_path: str,
    config_path: str,
    target_path: Optional[str] = None,
    fix: bool = False,
    format_code: bool = False,
    strict: bool = False,
    quiet: bool = False
) -> Dict:
    """Run SwiftLint with specified options."""

    # Validate swiftlint path
    if not os.path.isfile(swiftlint_path):
        return {
            "success": False,
            "error": "SwiftLint executable not found",
            "details": f"Path does not exist: {swiftlint_path}"
        }

    # Validate config path
    if not os.path.isfile(config_path):
        return {
            "success": False,
            "error": "SwiftLint config not found",
            "details": f"Config file does not exist: {config_path}"
        }

    # Determine mode
    modes = []
    if fix:
        modes.append("fix")
    if format_code:
        modes.append("format")
    if not modes:
        modes.append("lint")

    mode_str = "_and_".join(modes)

    result = {
        "success": True,
        "mode": mode_str,
        "target_path": target_path or ".",
        "violations": [],
        "violations_count": 0,
        "warnings_count": 0,
        "errors_count": 0
    }

    # Run fix if requested
    if fix:
        fix_cmd = [swiftlint_path, "--fix", "--config", config_path]
        if target_path:
            fix_cmd.extend(["--path", target_path])
        if quiet:
            fix_cmd.append("--quiet")

        try:
            subprocess.run(
                fix_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            result["fix_applied"] = True
        except Exception as e:
            return {
                "success": False,
                "error": "Failed to run SwiftLint --fix",
                "details": str(e)
            }

    # Run format if requested
    if format_code:
        format_cmd = [swiftlint_path, "--format", "--config", config_path]
        if target_path:
            format_cmd.extend(["--path", target_path])
        if quiet:
            format_cmd.append("--quiet")

        try:
            subprocess.run(
                format_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            result["format_applied"] = True
        except Exception as e:
            return {
                "success": False,
                "error": "Failed to run SwiftLint --format",
                "details": str(e)
            }

    # Always run lint to get current state
    lint_cmd = [swiftlint_path, "lint", "--config", config_path]
    if target_path:
        lint_cmd.extend(["--path", target_path])
    if strict:
        lint_cmd.append("--strict")
    if quiet:
        lint_cmd.append("--quiet")

    try:
        lint_result = subprocess.run(
            lint_cmd,
            capture_output=True,
            text=True,
            check=False
        )

        # Parse violations from stdout
        if lint_result.stdout:
            violations = parse_swiftlint_output(lint_result.stdout)
            result["violations"] = violations
            result["violations_count"] = len(violations)
            result["warnings_count"] = sum(1 for v in violations if v["severity"] == "warning")
            result["errors_count"] = sum(1 for v in violations if v["severity"] == "error")

        # Check return code for strict mode
        if strict and lint_result.returncode != 0:
            result["strict_mode_failed"] = True

    except Exception as e:
        return {
            "success": False,
            "error": "Failed to run SwiftLint lint",
            "details": str(e)
        }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run SwiftLint with various options"
    )

    parser.add_argument(
        "--swiftlint-path",
        required=True,
        help="Path to SwiftLint executable"
    )
    parser.add_argument(
        "--config-path",
        required=True,
        help="Path to .swiftlint.yml configuration file"
    )
    parser.add_argument(
        "--path",
        help="Target path to lint (file or directory)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix correctable violations"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        dest="format_code",
        help="Format code (whitespace/indentation)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output errors"
    )

    args = parser.parse_args()

    result = run_swiftlint(
        swiftlint_path=args.swiftlint_path,
        config_path=args.config_path,
        target_path=args.path,
        fix=args.fix,
        format_code=args.format_code,
        strict=args.strict,
        quiet=args.quiet
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Return non-zero exit code on failure or errors
    if not result.get("success"):
        sys.exit(1)
    if result.get("errors_count", 0) > 0:
        sys.exit(1)
    if result.get("strict_mode_failed"):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
