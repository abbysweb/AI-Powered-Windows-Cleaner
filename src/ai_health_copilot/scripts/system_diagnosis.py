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
            errors="replace",  # nosec B603
        )
        # If return code is 0, it passed (mostly). Ruff returns > 0 on errors. Pytest returns > 0 on failures.
        return (result.returncode == 0, result.stdout + "\n" + result.stderr)
    except Exception as e:
        return (False, str(e))


def check_tests() -> tuple[bool, str, str]:
    print("Running unit tests...")
    success, output = run_command(["python", "-m", "pytest", "tests/"])

    # Extract summary
    matches = re.findall(r"={2,}\s+(.*?)\s+={2,}", output)
    summary = matches[-1] if matches else "Unknown results"

    # Count passed/failed

    return success, summary, output


def check_linting() -> tuple[bool, str, str]:
    print("Running code quality checks (Ruff)...")
    success, output = run_command(["python", "-m", "ruff", "check", "src/", "tests/"])

    lines = output.strip().split("\n")
    if success:
        return True, "No linting errors found", output
    else:
        # Find the line that says "Found X errors."
        summary = next(
            (line for line in reversed(lines) if "Found" in line and "error" in line),
            "Linting errors detected",
        )
        return False, summary, output


def check_type_hints() -> tuple[bool, str, str]:
    print("Running type checker (Mypy)...")
    success, output = run_command(["python", "-m", "mypy", "src/"])
    lines = output.strip().split("\n")
    if success or "Success:" in output:
        return True, "Type checking passed", output
    summary = lines[-1] if lines else "Type errors detected"
    return False, summary, output


def check_complexity() -> tuple[bool, str, str]:
    print("Running complexity analysis (Radon)...")
    success, output = run_command(["python", "-m", "radon", "cc", "src/", "-a", "-nc"])
    if success:
        return True, "Complexity within acceptable limits (A/B grades)", output
    return False, "High complexity detected (C or worse)", output


def main():
    print("=" * 50)
    print(" AI WINDOWS HEALTH COPILOT - FULL SYSTEM DIAGNOSIS ")
    print("=" * 50)

    test_pass, test_msg, _ = check_tests()
    lint_pass, lint_msg, _ = check_linting()
    type_pass, type_msg, _ = check_type_hints()
    complex_pass, complex_msg, _ = check_complexity()

    print("\n" + "=" * 50)
    print(" DIAGNOSIS REPORT")
    print("=" * 50)
    print(f"Code Quality (Ruff)  : [{'PASS' if lint_pass else 'FAIL'}] {lint_msg}")
    print(f"Unit Tests (Pytest)  : [{'PASS' if test_pass else 'FAIL'}] {test_msg}")
    print(f"Architecture (Mypy)  : [{'PASS' if type_pass else 'FAIL'}] {type_msg}")
    print(
        f"Complexity (Radon)   : [{'PASS' if complex_pass else 'FAIL'}] {complex_msg}"
    )
    print("-" * 50)

    score = 0
    if lint_pass:
        score += 25
    if test_pass:
        score += 25
    if type_pass:
        score += 25
    if complex_pass:
        score += 25

    print(f"OVERALL HEALTH SCORE : {score} / 100")
    print("-" * 50)

    if score == 100:
        print("\nAll systems are fully operational and meet industry standards. [OK]")
    else:
        print(
            "\nSystem requires attention before proceeding to the next phase. [FAILED]"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
