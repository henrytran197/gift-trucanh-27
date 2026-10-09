#!/usr/bin/env python3
"""
Master E2E Automated Test Runner for gift_trucanh_27
Executes 4-Tier Opaque-Box Test Suite with Rich Diagnostic Reporting.
"""

import sys
import os
import time
import argparse
import unittest
from pathlib import Path

# Add tests directory to sys.path
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR.parent))

from tests.test_tier1_features import TestTier1FeatureCoverage
from tests.test_tier2_boundaries import TestTier2BoundariesAndCornerCases
from tests.test_tier3_interactions import TestTier3CrossFeatureInteractions
from tests.test_tier4_scenarios import TestTier4RealWorldScenarios
from tests.test_tier5_adversarial import TestTier5AdversarialStress


# ANSI formatting codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def format_status(status: str) -> str:
    if status == "PASS":
        return f"{Colors.GREEN}{Colors.BOLD}[PASS]{Colors.RESET}"
    elif status == "FAIL":
        return f"{Colors.RED}{Colors.BOLD}[FAIL]{Colors.RESET}"
    elif status == "ERROR":
        return f"{Colors.YELLOW}{Colors.BOLD}[ERROR]{Colors.RESET}"
    return f"[{status}]"


class DetailedTestResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.results = []  # list of (test, status, err_msg)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.results.append((test, "PASS", ""))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        msg = self._exc_info_to_string(err, test)
        self.results.append((test, "FAIL", msg))

    def addError(self, test, err):
        super().addError(test, err)
        msg = self._exc_info_to_string(err, test)
        self.results.append((test, "ERROR", msg))


def run_tier(tier_name: str, test_class) -> dict:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_class)
    result = DetailedTestResult()
    
    start_time = time.time()
    suite.run(result)
    elapsed = time.time() - start_time

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== {tier_name} ==={Colors.RESET}")
    for test, status, err_msg in result.results:
        doc = test._testMethodDoc or test.id().split(".")[-1]
        doc = doc.strip().split("\n")[0]
        status_badge = format_status(status)
        print(f"  {status_badge} {test._testMethodName:<42} - {doc}")
        if status in ("FAIL", "ERROR") and err_msg:
            # Print indented first line of failure
            lines = err_msg.strip().split("\n")
            first_err = lines[-1] if lines else "Unknown error"
            print(f"         {Colors.RED}-> {first_err}{Colors.RESET}")

    passed = len([r for r in result.results if r[1] == "PASS"])
    failed = len(result.failures)
    errors = len(result.errors)
    total = result.testsRun

    return {
        "name": tier_name,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "elapsed": elapsed,
        "failures_details": result.failures + result.errors,
    }


def main():
    parser = argparse.ArgumentParser(description="E2E Test Runner for gift_trucanh_27")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5], help="Run only specific tier (1-5)")
    parser.add_argument("--verbose", action="store_true", help="Print full failure stack traces")
    args = parser.parse_args()

    print(f"{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}  gift_trucanh_27 - E2E Automated Test Suite Runner (Tiers 1 - 5){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}  Target: Trúc Anh (Na) 27th Birthday Static Web Album & Certificate{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.RESET}")

    tiers_to_run = []
    if args.tier is None or args.tier == 1:
        tiers_to_run.append(("Tier 1: Feature Coverage (Unit / Isolation)", TestTier1FeatureCoverage))
    if args.tier is None or args.tier == 2:
        tiers_to_run.append(("Tier 2: Boundary & Corner Cases", TestTier2BoundariesAndCornerCases))
    if args.tier is None or args.tier == 3:
        tiers_to_run.append(("Tier 3: Cross-Feature Interactions", TestTier3CrossFeatureInteractions))
    if args.tier is None or args.tier == 4:
        tiers_to_run.append(("Tier 4: Real-World Scenarios (End-to-End)", TestTier4RealWorldScenarios))
    if args.tier is None or args.tier == 5:
        tiers_to_run.append(("Tier 5: Adversarial Stress & Hardening", TestTier5AdversarialStress))

    tier_summaries = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    start_all = time.time()

    for tier_name, test_class in tiers_to_run:
        summary = run_tier(tier_name, test_class)
        tier_summaries.append(summary)
        total_tests += summary["total"]
        total_passed += summary["passed"]
        total_failed += summary["failed"]
        total_errors += summary["errors"]

    total_time = time.time() - start_all

    print(f"\n{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}                       TEST EXECUTION SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.RESET}")
    print(f"{'Tier':<45} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Error':<6} | {'Rate':<7}")
    print("-" * 84)

    for s in tier_summaries:
        rate = (s["passed"] / s["total"] * 100) if s["total"] > 0 else 0
        rate_str = f"{rate:5.1f}%"
        color = Colors.GREEN if s["failed"] == 0 and s["errors"] == 0 else Colors.RED
        print(f"{s['name']:<45} | {s['total']:<6} | {s['passed']:<6} | {s['failed']:<6} | {s['errors']:<6} | {color}{rate_str}{Colors.RESET}")

    print("-" * 84)
    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    overall_color = Colors.GREEN if total_failed == 0 and total_errors == 0 else Colors.RED
    print(f"{Colors.BOLD}{'OVERALL TOTALS':<45} | {total_tests:<6} | {total_passed:<6} | {total_failed:<6} | {total_errors:<6} | {overall_color}{overall_rate:5.1f}%{Colors.RESET}")
    print(f"Total Execution Time: {total_time:.3f}s")
    print(f"{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.RESET}")

    if args.verbose:
        for s in tier_summaries:
            if s["failures_details"]:
                print(f"\n{Colors.BOLD}{Colors.RED}Detailed Failure Diagnostics for {s['name']}:{Colors.RESET}")
                for test, trace in s["failures_details"]:
                    print(f"\n--- {test.id()} ---")
                    print(trace)

    if total_failed > 0 or total_errors > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}[STATUS] TDD RED PHASE: {total_failed + total_errors} test(s) failing (Waiting for worker milestones).{Colors.RESET}")
        return 1
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[STATUS] 100% ALL TESTS PASSING! System ready for delivery.{Colors.RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
