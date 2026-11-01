#!/usr/bin/env python3
"""
Master E2E Test Suite Runner for HSC 2026 Narail District Results System.
Discovers and executes all 4-Tier test suites, verifies 100% pass rate,
and outputs a comprehensive executive verification summary.

Usage:
    python3 /media/sanglap/Movies/2026results/tests/run_e2e_tests.py
Exit code:
    0 if all tests pass
    1 if any test fails or errors
"""
import os
import sys
import time
import unittest
from typing import Dict, Any, List

# Ensure tests root and workspace root are in Python path
TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(TESTS_ROOT, ".."))
if TESTS_ROOT not in sys.path:
    sys.path.insert(0, TESTS_ROOT)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

TIERS = [
    {
        "tier": "Tier 1",
        "name": "Feature Coverage (F1 - F11)",
        "dir": os.path.join(TESTS_ROOT, "tier1_features"),
        "pattern": "test_*.py"
    },
    {
        "tier": "Tier 2",
        "name": "Boundary & Corner Cases (B1 - B6)",
        "dir": os.path.join(TESTS_ROOT, "tier2_boundaries"),
        "pattern": "test_*.py"
    },
    {
        "tier": "Tier 3",
        "name": "Cross-Feature Combinations (C1 - C4)",
        "dir": os.path.join(TESTS_ROOT, "tier3_combinations"),
        "pattern": "test_*.py"
    },
    {
        "tier": "Tier 4",
        "name": "Real-World Application Scenarios (R1 - R4)",
        "dir": os.path.join(TESTS_ROOT, "tier4_real_world"),
        "pattern": "test_*.py"
    },
    {
        "tier": "Tier 5",
        "name": "Adversarial Hardening & Stress Testing (Challenger 1)",
        "dir": os.path.join(TESTS_ROOT, "tier5_adversarial"),
        "pattern": "test_*.py"
    }
]

def print_header(title: str):
    width = 78
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)

def print_section(title: str):
    width = 78
    print("-" * width)
    print(f"[*] {title}")
    print("-" * width)

def run_suite() -> int:
    start_time = time.time()
    print("\n")
    print_header("HSC 2026 NARAIL DISTRICT RESULTS — E2E TEST RUNNER")
    print(f"Target Directory: {WORKSPACE_ROOT}")
    print(f"Test Suite Directory: {TESTS_ROOT}")
    print(f"Start Timestamp: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}")
    print("=" * 78)

    loader = unittest.TestLoader()
    tier_results = []
    total_run = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0

    for item in TIERS:
        tier_name = item["tier"]
        tier_desc = item["name"]
        tier_dir = item["dir"]
        pattern = item["pattern"]

        print(f"\n>> Executing {tier_name}: {tier_desc}")
        suite = loader.discover(start_dir=tier_dir, pattern=pattern, top_level_dir=WORKSPACE_ROOT)
        test_count = suite.countTestCases()

        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        t_start = time.time()
        result = runner.run(suite)
        t_duration = round(time.time() - t_start, 3)

        passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        tier_results.append({
            "tier": tier_name,
            "description": tier_desc,
            "total": result.testsRun,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "duration": t_duration
        })

        total_run += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_skipped += len(result.skipped)

    total_duration = round(time.time() - start_time, 3)
    total_passed = total_run - total_failures - total_errors - total_skipped

    print("\n")
    print_header("EXECUTIVE TEST RUN SUMMARY")
    print(f"{'Tier':<10} | {'Scope':<38} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Time (s)'}")
    print("-" * 78)
    for r in tier_results:
        print(f"{r['tier']:<10} | {r['description']:<38} | {r['total']:<6} | {r['passed']:<6} | {r['failed'] + r['errors']:<6} | {r['duration']}s")
    print("-" * 78)
    print(f"{'TOTAL':<10} | {'All 5 Verification Tiers':<38} | {total_run:<6} | {total_passed:<6} | {total_failures + total_errors:<6} | {total_duration}s")
    print("=" * 78)

    if total_failures == 0 and total_errors == 0:
        print("\n [SUCCESS] ALL E2E TESTS PASSED WITH 100% SUCCESS RATE (EXIT CODE 0)\n")
        return 0
    else:
        print(f"\n [FAILURE] {total_failures} failures and {total_errors} errors detected (EXIT CODE 1)\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_suite())
