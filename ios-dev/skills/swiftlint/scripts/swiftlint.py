#!/usr/bin/env python3
"""SwiftLint runner script for Claude Code plugin."""

import argparse
import json
import os
import subprocess
import sys
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


def run_swiftlint_rules(
    swiftlint_path: str,
    config_path: Optional[str] = None,
    rule_id: Optional[str] = None
) -> Dict:
    """Run SwiftLint rules command to list available rules or show rule details."""

    if not os.path.isfile(swiftlint_path):
        return {
            "success": False,
            "error": "SwiftLint executable not found",
            "details": f"Path does not exist: {swiftlint_path}"
        }

    cmd = [swiftlint_path, "rules"]
    if rule_id:
        cmd.append(rule_id)
    if config_path:
        if not os.path.isfile(config_path):
            return {
                "success": False,
                "error": "SwiftLint config not found",
                "details": f"Config file does not exist: {config_path}"
            }
        cmd.extend(["--config", config_path])

    cwd = os.path.dirname(os.path.abspath(config_path)) if config_path else None

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd
        )
        output = result.stdout or result.stderr
        return {
            "success": True,
            "rule_id": rule_id,
            "output": output
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Failed to run SwiftLint rules",
            "details": str(e)
        }


def run_swiftlint(
    swiftlint_path: str,
    config_path: str,
    target_paths: Optional[List[str]] = None,
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

    if format_code and not fix:
        return {
            "success": False,
            "error": "Invalid SwiftLint options",
            "details": "--format requires --fix with current SwiftLint versions"
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
    config_dir = os.path.dirname(os.path.abspath(config_path))
    normalized_paths = target_paths or []

    result = {
        "success": True,
        "mode": mode_str,
        "target_path": normalized_paths[0] if len(normalized_paths) == 1 else ".",
        "target_paths": normalized_paths,
        "violations": [],
        "violations_count": 0,
        "warnings_count": 0,
        "errors_count": 0
    }

    lint_cmd = [
        swiftlint_path,
        "lint",
        "--config",
        config_path,
        "--working-directory",
        config_dir
    ]
    if fix:
        lint_cmd.append("--fix")
        result["fix_applied"] = True
    if format_code:
        lint_cmd.append("--format")
        result["format_applied"] = True
    if strict:
        lint_cmd.append("--strict")
    if quiet:
        lint_cmd.append("--quiet")
    lint_cmd.extend(normalized_paths)

    try:
        lint_result = subprocess.run(
            lint_cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=config_dir
        )

        # Parse violations from stdout
        if lint_result.stdout:
            violations = parse_swiftlint_output(lint_result.stdout)
            result["violations"] = violations
            result["violations_count"] = len(violations)
            result["warnings_count"] = sum(1 for v in violations if v["severity"] == "warning")
            result["errors_count"] = sum(1 for v in violations if v["severity"] == "error")

        if lint_result.returncode != 0 and not result["violations"] and lint_result.stderr:
            return {
                "success": False,
                "error": "Failed to run SwiftLint lint",
                "details": lint_result.stderr.strip()
            }

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
        help="Path to .swiftlint.yml configuration file"
    )
    parser.add_argument(
        "--rules",
        action="store_true",
        help="List available SwiftLint rules (or show details for a specific rule with --rule-id)"
    )
    parser.add_argument(
        "--rule-id",
        help="Show details for a specific rule (use with --rules)"
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="Target path to lint (file or directory). Can be specified multiple times."
    )
    parser.add_argument(
        "positional_paths",
        nargs="*",
        help="Paths to files or directories to lint"
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

    if args.rules:
        result = run_swiftlint_rules(
            swiftlint_path=args.swiftlint_path,
            config_path=args.config_path,
            rule_id=args.rule_id
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result.get("success") else 1)

    if not args.config_path:
        parser.error("--config-path is required when not using --rules")

    target_paths = []
    if args.paths:
        target_paths.extend(args.paths)
    if args.positional_paths:
        target_paths.extend(args.positional_paths)

    result = run_swiftlint(
        swiftlint_path=args.swiftlint_path,
        config_path=args.config_path,
        target_paths=target_paths,
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
