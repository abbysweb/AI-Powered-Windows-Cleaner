import re
import subprocess
import sys


def run_command(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace"
        )
        # If return code is 0, it passed (mostly). Ruff returns > 0 on errors. Pytest returns > 0 on failures.
        return (result.returncode == 0, result.stdout + "\n" + result.stderr)
    except Exception as e:
        return (False, str(e))

def check_tests() -> tuple[bool, str, str]:
    print("Running unit tests...")
    success, output = run_command(["python", "-m", "pytest", "tests/"])
    
    # Extract summary
    match = re.search(r"==== (.*?) ====", output.splitlines()[-1] if output else "")
    summary = match.group(1) if match else "Unknown results"
    
    # Count passed/failed
    output.count(" PASSED ")
    output.count(" FAILED ")
    
    return success, summary, output

def check_linting() -> tuple[bool, str, str]:
    print("Running code quality checks (Ruff)...")
    success, output = run_command(["python", "-m", "ruff", "check", "src/", "tests/"])
    
    lines = output.strip().split("\n")
    if success:
        return True, "No linting errors found", output
    else:
        # Find the line that says "Found X errors."
        summary = next((line for line in reversed(lines) if "Found" in line and "error" in line), "Linting errors detected")
        return False, summary, output

def check_type_hints() -> tuple[bool, str, str]:
    print("Running type checker (Mypy)...")
    # We might not have mypy installed or strictly typed, but let's try.
    success, output = run_command(["python", "-m", "mypy", "src/"])
    
    lines = output.strip().split("\n")
    if success or "Success:" in output:
        return True, "Type checking passed", output
    else:
        summary = lines[-1] if lines else "Type errors detected"
        return False, summary, output

def main():
    print("=" * 50)
    print(" AI WINDOWS HEALTH COPILOT - FULL SYSTEM DIAGNOSIS ")
    print("=" * 50)
    
    test_ok, test_summary, _ = check_tests()
    lint_ok, lint_summary, _ = check_linting()
    type_ok, type_summary, _ = check_type_hints()
    
    print("\n" + "=" * 50)
    print(" DIAGNOSIS REPORT")
    print("=" * 50)
    
    print(f"Code Quality (Ruff)  : {'[PASS]' if lint_ok else '[FAIL]'} {lint_summary}")
    print(f"Unit Tests (Pytest)  : {'[PASS]' if test_ok else '[FAIL]'} {test_summary}")
    print(f"Architecture (Mypy)  : {'[PASS]' if type_ok else '[FAIL]'} {type_summary}")
    
    overall_health = 100
    if not lint_ok: overall_health -= 20
    if not test_ok: overall_health -= 50
    if not type_ok: overall_health -= 20
    
    print("-" * 50)
    print(f"OVERALL HEALTH SCORE : {overall_health} / 100")
    print("-" * 50)
    
    if overall_health == 100:
        print("\nAll systems are fully operational and meet industry standards. [OK]")
    else:
        print("\nSystem requires attention before proceeding to the next phase. [FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
