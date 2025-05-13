#!/usr/bin/env python3
"""
Test runner for the Source of Wealth Agent tests.
This script runs all the test files in the tests directory.
"""

import sys
import os
import subprocess
import argparse
from typing import List, Optional

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def run_test(test_file: str, verbose: bool = False) -> bool:
    """Run a single test file and return whether it passed."""
    print(f"{BLUE}Running test: {test_file}{RESET}")
    
    try:
        # Run the test with Python interpreter
        cmd = [sys.executable, test_file]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Print output if verbose or if test failed
        if verbose or result.returncode != 0:
            print(f"{YELLOW}Output:{RESET}\n{result.stdout}")
            if result.stderr:
                print(f"{RED}Errors:{RESET}\n{result.stderr}")
        
        # Report result
        if result.returncode == 0:
            print(f"{GREEN}✓ Test passed: {os.path.basename(test_file)}{RESET}")
            return True
        else:
            print(f"{RED}✗ Test failed: {os.path.basename(test_file)}{RESET}")
            return False
    
    except Exception as e:
        print(f"{RED}Error running test {test_file}: {str(e)}{RESET}")
        return False

def run_all_tests(tests_dir: str, specific_tests: Optional[List[str]] = None, verbose: bool = False) -> None:
    """Run all tests in the tests directory."""
    # Get list of all Python files in the tests directory
    test_files = []
    for filename in os.listdir(tests_dir):
        if filename.endswith('.py') and filename.startswith('test_') and filename != '__pycache__':
            test_files.append(os.path.join(tests_dir, filename))
    
    # Filter tests if specific ones were requested
    if specific_tests:
        test_files = [tf for tf in test_files if any(os.path.basename(tf).startswith(st) for st in specific_tests)]
    
    if not test_files:
        print(f"{YELLOW}No test files found to run.{RESET}")
        return
    
    # Run all tests and track results
    passed = 0
    failed = 0
    
    print(f"{BLUE}Found {len(test_files)} test files to run{RESET}")
    
    for test_file in sorted(test_files):
        if run_test(test_file, verbose):
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\n{BLUE}Test Summary:{RESET}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"Total: {passed + failed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Source of Wealth Agent tests")
    parser.add_argument("tests", nargs="*", help="Specific test files to run (without the .py extension)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output for all tests")
    args = parser.parse_args()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    run_all_tests(tests_dir, args.tests, args.verbose)
