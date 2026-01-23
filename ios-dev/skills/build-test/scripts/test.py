#!/usr/bin/env python3
"""
Run tests for an iOS app using xcodebuild test.

Usage:
    python3 test.py --project <path> --scheme <name> --destination <dest> [options]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def find_project() -> tuple[str, str] | None:
    """Auto-detect project/workspace in current directory."""
    cwd = Path.cwd()

    # Priority 1: .xcworkspace
    workspaces = list(cwd.glob("*.xcworkspace"))
    if workspaces:
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


def parse_xcresult(xcresult_path: str) -> dict:
    """Parse xcresult bundle to extract test results."""
    try:
        # Get test results using xcresulttool
        result = subprocess.run(
            ["xcrun", "xcresulttool", "get", "--path", xcresult_path, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return {"error": f"Failed to parse xcresult: {result.stderr}"}

        data = json.loads(result.stdout)

        # Extract test summary from actions
        test_summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        failed_tests = []

        # Navigate through the xcresult structure
        actions = data.get("actions", {}).get("_values", [])
        for action in actions:
            action_result = action.get("actionResult", {})
            tests_ref = action_result.get("testsRef", {})

            if tests_ref:
                test_id = tests_ref.get("id", {}).get("_value", "")
                if test_id:
                    # Get detailed test results
                    test_result = subprocess.run(
                        ["xcrun", "xcresulttool", "get", "--path", xcresult_path,
                         "--format", "json", "--id", test_id],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if test_result.returncode == 0:
                        test_data = json.loads(test_result.stdout)
                        parse_test_summaries(test_data, test_summary, failed_tests)

        return {
            "test_summary": test_summary,
            "failed_tests": failed_tests
        }

    except subprocess.TimeoutExpired:
        return {"error": "xcresulttool timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}"}
    except Exception as e:
        return {"error": str(e)}


def parse_test_summaries(data: dict, summary: dict, failed_tests: list, bundle: str = "", class_name: str = ""):
    """Recursively parse test summaries from xcresult data."""
    if not isinstance(data, dict):
        return

    # Check if this is a test summary
    name = data.get("name", {}).get("_value", "")
    identifier = data.get("identifier", {}).get("_value", "")

    # Get subtests
    subtests = data.get("subtests", {}).get("_values", [])

    if subtests:
        # This is a test bundle or class
        current_bundle = bundle
        current_class = class_name

        if not bundle and name:
            current_bundle = name
        elif bundle and name and not class_name:
            current_class = name

        for subtest in subtests:
            parse_test_summaries(subtest, summary, failed_tests, current_bundle, current_class)
    else:
        # This is a test method
        test_status = data.get("testStatus", {}).get("_value", "")

        if test_status:
            summary["total"] += 1

            if test_status == "Success":
                summary["passed"] += 1
            elif test_status == "Failure":
                summary["failed"] += 1

                # Extract failure message
                failure_summaries = data.get("failureSummaries", {}).get("_values", [])
                failure_message = ""
                if failure_summaries:
                    failure_message = failure_summaries[0].get("message", {}).get("_value", "")

                failed_tests.append({
                    "name": name,
                    "class": class_name,
                    "bundle": bundle,
                    "failure_message": failure_message
                })
            elif test_status == "Skipped":
                summary["skipped"] += 1


def run_tests(
    project_path: str,
    scheme: str,
    destination: str,
    test_plan: str | None = None,
    only_testing: list[str] | None = None,
    skip_testing: list[str] | None = None,
    parallel: bool = False,
    result_path: str | None = None
) -> dict:
    """Run xcodebuild test and return results."""
    path = Path(project_path)

    # Determine project type
    if path.suffix == ".xcworkspace":
        project_args = ["-workspace", str(path)]
    elif path.suffix == ".xcodeproj":
        project_args = ["-project", str(path)]
    elif path.is_dir() and (path / "Package.swift").exists():
        project_args = []
    else:
        return {"success": False, "error": f"Invalid project path: {project_path}"}

    # Create result bundle path
    if not result_path:
        result_path = os.path.join(tempfile.gettempdir(), f"Test-{int(time.time())}.xcresult")

    # Build command
    cmd = [
        "xcodebuild",
        *project_args,
        "-scheme", scheme,
        "-destination", destination,
        "-resultBundlePath", result_path,
        "-quiet",
        "test"
    ]

    if test_plan:
        cmd.extend(["-testPlan", test_plan])

    if only_testing:
        for test in only_testing:
            cmd.extend(["-only-testing", test])

    if skip_testing:
        for test in skip_testing:
            cmd.extend(["-skip-testing", test])

    if parallel:
        cmd.append("-parallel-testing-enabled")
        cmd.append("YES")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout for tests
            cwd=str(path) if path.is_dir() and not path.suffix else None
        )

        duration = time.time() - start_time

        # Parse xcresult
        xcresult_data = parse_xcresult(result_path)

        response = {
            "success": result.returncode == 0,
            "duration_seconds": round(duration, 2),
            "xcresult_path": result_path
        }

        if "error" in xcresult_data:
            response["parse_error"] = xcresult_data["error"]
        else:
            response["test_summary"] = xcresult_data.get("test_summary", {})
            response["failed_tests"] = xcresult_data.get("failed_tests", [])

        if result.returncode != 0 and not response.get("test_summary", {}).get("total"):
            response["error"] = "Tests failed"
            response["details"] = result.stderr or result.stdout

        return response

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Tests timed out after 30 minutes"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Run iOS tests using xcodebuild")
    parser.add_argument("--project", help="Path to .xcodeproj, .xcworkspace, or package directory")
    parser.add_argument("--scheme", required=True, help="Scheme name to test")
    parser.add_argument("--destination", required=True, help="Test destination")
    parser.add_argument("--test-plan", help="Test plan name")
    parser.add_argument("--only-testing", action="append", help="Run only specified tests (can be repeated)")
    parser.add_argument("--skip-testing", action="append", help="Skip specified tests (can be repeated)")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel testing")
    parser.add_argument("--result-path", help="Path for xcresult bundle")

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

    result = run_tests(
        project_path=project_path,
        scheme=args.scheme,
        destination=args.destination,
        test_plan=args.test_plan,
        only_testing=args.only_testing,
        skip_testing=args.skip_testing,
        parallel=args.parallel,
        result_path=args.result_path
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
