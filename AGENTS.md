# ==========================================================
# PHASE-BASED DEVELOPMENT LIFECYCLE
# ==========================================================

This project MUST be developed incrementally in well-defined phases.

The AI agent MUST NEVER skip phases.

Each phase must be fully completed, tested, documented, and validated before the next phase begins.

The project should always remain in a working state.

---

# Development Workflow

Every phase MUST follow this workflow:

Requirements

↓

Architecture Design

↓

Implementation

↓

Static Analysis

↓

Unit Tests

↓

Integration Tests

↓

Performance Tests

↓

Security Review

↓

Code Quality Review

↓

Diagnosis Report

↓

Approval

↓

Next Phase

No exceptions.

---

# Phase Completion Rule

A phase is considered COMPLETE only if:

✓ Feature implementation complete

✓ No critical bugs

✓ All tests passing

✓ Security review passed

✓ Performance acceptable

✓ Documentation updated

✓ Diagnosis report generated

✓ Code quality score acceptable

✓ No architectural violations

Only after ALL requirements are satisfied may development continue.

---

# Diagnosis Report

At the end of EVERY phase, generate a diagnosis report.

Report format:

==================================

PHASE REPORT

==================================

Phase Number

Phase Name

Completion Status

Overall Health Score (0-100)

Architecture Score

Code Quality Score

Security Score

Performance Score

Test Coverage

Files Added

Files Modified

Known Issues

Risk Level

Technical Debt

Recommendations

Next Phase Readiness

PASS / FAIL

==================================

If the report status is

FAIL

the AI agent MUST NOT continue.

---

# Mandatory Testing

Each phase must include:

Unit Tests

Integration Tests

Regression Tests

Edge Case Tests

Error Handling Tests

Performance Tests

Security Tests

File Permission Tests

Filesystem Safety Tests

Mock Tests

Every new module requires corresponding tests.

---

# Acceptance Criteria

Each phase must define measurable acceptance criteria.

Example:

✓ Scan completes successfully

✓ UI remains responsive

✓ Test coverage >90%

✓ No memory leaks

✓ No crashes

✓ No security warnings

✓ Logging verified

✓ Rollback verified

If ANY acceptance criterion fails,

the phase fails.

---

# Quality Gates

Every phase must satisfy the following minimum scores:

Architecture

≥95%

Code Quality

≥95%

Security

100%

Test Coverage

≥90%

Linting

100%

Type Checking

100%

Critical Bugs

0

High Severity Bugs

0

Memory Leaks

0

Blocking UI Operations

0

If any requirement is unmet,

development stops.

---

# Static Analysis

Before completing a phase run:

Black

Ruff

MyPy

PyTest

Dead Code Detection

Unused Import Detection

Circular Dependency Detection

Complexity Analysis

Generate a summary in the diagnosis report.

---

# Complexity Analysis

Every phase should measure:

Cyclomatic Complexity

Function Length

Class Size

Dependency Graph

Maintainability Index

Any module exceeding limits should be refactored before approval.

---

# Security Validation

Verify:

No unsafe deletes

No shell injection

No path traversal

No insecure temp files

No privilege escalation

No secrets

No unsafe AI execution

No unsafe file permissions

If security review fails,

phase fails.

---

# Performance Validation

Measure:

Startup Time

Scan Time

Memory Usage

CPU Usage

Disk Reads

Disk Writes

Thread Count

UI Responsiveness

If performance regresses significantly,

refactor before continuing.

---

# Regression Testing

Every completed feature must continue working.

Previously completed phases must never break.

Run the complete regression suite after each phase.

---

# Documentation

Every phase updates:

Architecture documentation

API documentation

Developer documentation

User documentation

Changelog

No undocumented feature is considered complete.

---

# Refactoring Rule

After each phase:

Review duplicated code.

Review architecture.

Review abstractions.

Review naming.

Refactor BEFORE continuing.

Never postpone major refactoring.

---

# Git Workflow

Each phase should correspond to one or more logical commits.

Recommended commit order:

feat:

test:

docs:

refactor:

Final commit:

phase: complete phase X

---

# Phase Approval Checklist

Before moving to the next phase verify:

✓ Requirements implemented

✓ Architecture reviewed

✓ Tests passed

✓ Documentation complete

✓ Security review passed

✓ Performance acceptable

✓ No duplicated code

✓ No TODOs without issue references

✓ No placeholder implementations

✓ Diagnosis report generated

✓ Phase status = PASS

Only then proceed.

---

# AI Agent Rule

The AI agent MUST behave like a senior software engineer and technical lead.

It must continuously evaluate whether the current phase is production-ready.

If quality is below standard,

STOP.

Fix the problems.

Regenerate tests.

Regenerate the diagnosis report.

Only after achieving PASS may the AI continue.

Never continue development after a failed diagnosis report.

---

# Continuous Improvement

At the end of every phase, identify:

Architecture improvements

Performance optimizations

Security improvements

Code simplifications

Potential refactoring

Future enhancements

Record them in the diagnosis report without implementing them automatically unless scheduled for the next phase.

---

# Golden Rule

One Phase.

One Goal.

One Complete Test Suite.

One Diagnosis Report.

PASS before proceeding.

The project must always be in a deployable, production-quality state after every completed phase.