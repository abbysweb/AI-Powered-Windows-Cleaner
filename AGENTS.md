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

# ==========================================================
# TESTING STANDARDS
# ==========================================================

Testing is mandatory.

Every feature must include appropriate automated tests.

No feature is complete without passing all required tests.

---

# Testing Pyramid

                    E2E Tests
                 Integration Tests
                  Component Tests
                    Unit Tests

Follow the testing pyramid.

Prefer many fast unit tests.

Use integration and end-to-end tests where appropriate.

---

# Required Test Types

## 1. Unit Testing

Purpose

Verify individual functions and classes.

Examples

✓ Scanner methods

✓ File validator

✓ Risk calculator

✓ AI response parser

✓ Configuration loader

✓ Path validator

---

## 2. Integration Testing

Purpose

Verify modules work together.

Examples

Scanner → Analyzer

Analyzer → Cleaner

Cleaner → Rollback

GUI → Services

AI → Recommendation Engine

SQLite → Repository

---

## 3. End-to-End Testing (E2E)

Purpose

Simulate complete user workflows.

Examples

Launch application

↓

Scan system

↓

Review recommendations

↓

Clean selected files

↓

Rollback

↓

Verify logs

---

## 4. System Testing

Purpose

Test the complete application as a whole.

Verify

Installation

Startup

Shutdown

GUI

AI

Database

Filesystem

Logging

Recovery

---

## 5. Acceptance Testing

Purpose

Verify feature satisfies business requirements.

Examples

User can safely recover disk space.

User receives AI explanations.

Rollback works.

No user files deleted.

---

## 6. Regression Testing

Purpose

Ensure existing functionality still works.

Run after every feature.

Run after every bug fix.

Run before every release.

---

## 7. Smoke Testing

Purpose

Quickly verify major functionality.

Examples

Application launches

Database connects

GUI opens

Scan works

Exit works

---

## 8. Sanity Testing

Purpose

Verify specific bug fixes.

Ensure related functionality still works.

---

## 9. Functional Testing

Verify every requirement.

Examples

Temp scan

Recycle Bin cleaning

AI recommendation

Scheduler

Settings

Rollback

---

## 10. Non-Functional Testing

Verify

Performance

Security

Scalability

Reliability

Usability

Maintainability

---

# Performance Testing

## Load Testing

Large folders

Millions of files

Large cache

Large databases

---

## Stress Testing

Low memory

High CPU

Low disk space

Many simultaneous scans

---

## Endurance Testing

Run scans continuously.

Verify no leaks.

Verify stable memory.

---

## Scalability Testing

Test

10 files

1,000 files

100,000 files

1,000,000 files

Measure performance.

---

# Security Testing

Verify

Path traversal

Shell injection

Privilege escalation

Unsafe deletes

Symlink attacks

Junction attacks

Configuration tampering

AI prompt injection

Malicious JSON

Malicious filenames

Unauthorized file access

Sensitive data exposure

---

# Filesystem Testing

Test

Read-only files

Hidden files

System files

Locked files

Symbolic links

Network drives

External drives

NTFS junctions

Long paths

Unicode filenames

Invalid filenames

Permission denied

Disk full

---

# Windows Compatibility Testing

Windows 10

Windows 11

Administrator

Standard User

SSD

HDD

Multiple drives

Different languages

Different screen resolutions

High DPI

Dark mode

Light mode

---

# AI Testing

Verify

Prompt generation

JSON schema validation

Invalid responses

Empty responses

Hallucinated fields

Malformed JSON

Timeouts

Offline mode

Provider switching

Risk score accuracy

Recommendation consistency

---

# Database Testing

Verify

CRUD

Transactions

Rollback

Concurrency

Migration

Corrupted database

Recovery

Backup

Restore

---

# GUI Testing

Verify

Buttons

Dialogs

Navigation

Progress bars

Responsive layout

Keyboard shortcuts

Accessibility

Dark mode

Light mode

Window resizing

Multi-monitor

---

# API Testing

If APIs are used

Test

Authentication

Timeouts

Retries

Rate limiting

Offline handling

Error responses

JSON validation

---

# Configuration Testing

Verify

Default settings

Invalid configuration

Missing configuration

Corrupted configuration

Environment variables

Migration

---

# Logging Testing

Verify

Errors logged

Warnings logged

Audit logs

Log rotation

Sensitive data hidden

Log formatting

---

# Recovery Testing

Verify

Rollback

Restore

Interrupted cleanup

Unexpected shutdown

Power failure simulation

Application crash recovery

---

# Installer Testing

Verify

Installation

Upgrade

Repair

Uninstall

Configuration preserved

Logs preserved

Database preserved

---

# Memory Testing

Verify

Memory leaks

Object cleanup

Thread cleanup

Resource disposal

Large scans

Repeated scans

---

# Concurrency Testing

Verify

Thread safety

Race conditions

Deadlocks

Parallel scanning

Background workers

Cancellation

---

# Edge Case Testing

Empty folders

Huge folders

Tiny files

Very large files

Invalid paths

Special characters

Unicode

Emojis

Permission denied

Read-only media

Disk full

Corrupted cache

Interrupted cleanup

---

# Fuzz Testing

Random filenames

Random JSON

Random settings

Random AI responses

Random configuration

Malformed filesystem data

---

# Mutation Testing

Verify tests detect intentional code mutations.

Improve test quality.

---

# Accessibility Testing

Keyboard navigation

Screen reader support

High contrast

Scaling

Focus indicators

---

# Localization Testing

Different locales

Different date formats

Unicode

RTL compatibility (future)

---

# Release Testing

Before every release

✓ All tests pass

✓ No critical bugs

✓ Performance acceptable

✓ Security review passed

✓ Documentation complete

✓ Installer verified

✓ AI validated

✓ Regression passed

---

# Coverage Goals

Unit Test Coverage

≥95%

Integration Coverage

≥90%

Critical Modules

100%

Security Modules

100%

Filesystem Modules

100%

AI JSON Validation

100%

---

# Test Report

Every phase generates

Test Summary

Passed

Failed

Skipped

Coverage

Execution Time

Performance Metrics

Security Findings

Known Issues

Overall Status

PASS / FAIL

Development cannot proceed until

Overall Status = PASS.

# ==========================================================
# BUG MANAGEMENT & DEBUGGING METHODOLOGY
# ==========================================================

Software quality is measured by how bugs are prevented,
detected, diagnosed, fixed, verified, and documented.

The AI agent must follow a structured debugging methodology.

Never apply random fixes.

Never guess.

Always identify the root cause first.

---

# Bug Lifecycle

Every bug follows this lifecycle:

Bug Report

↓

Reproduce

↓

Collect Evidence

↓

Root Cause Analysis

↓

Design Fix

↓

Implement Fix

↓

Regression Testing

↓

Verification

↓

Documentation

↓

Close Bug

Never skip any step.

---

# Bug Severity

Critical

- Data loss
- Unsafe deletion
- Application crash
- Security vulnerability
- Corrupted rollback
- Filesystem damage

Fix immediately.

No further development allowed.

---

High

- Major feature broken
- Rollback failure
- AI produces invalid recommendations
- Database corruption
- Scan failure

Fix before next phase.

---

Medium

- Minor functionality broken
- Incorrect UI behavior
- Performance regression
- Logging issue

Fix before release.

---

Low

- Cosmetic issue
- Documentation issue
- Minor layout issue

Schedule appropriately.

---

# Bug Priority

P0

Immediate

P1

High

P2

Normal

P3

Low

Prioritize by impact,
not by implementation difficulty.

---

# Root Cause Analysis

Never stop after finding the symptom.

Always identify

WHY

the problem occurred.

Use techniques such as:

Five Whys

Fault Tree Analysis

Cause-and-Effect Analysis

Dependency Analysis

State Analysis

Call Stack Analysis

Filesystem Analysis

Thread Analysis

Memory Analysis

---

# Debugging Workflow

Step 1

Reproduce the bug consistently.

If the bug cannot be reproduced,

collect more evidence.

---

Step 2

Gather diagnostics

Logs

Stack traces

Configuration

OS version

Memory usage

CPU usage

Filesystem state

AI responses

Database state

Screenshots

---

Step 3

Identify root cause.

Never patch symptoms.

---

Step 4

Design the smallest correct fix.

Avoid introducing unrelated changes.

---

Step 5

Implement fix.

Keep architecture clean.

---

Step 6

Run all tests.

Unit

Integration

Regression

Security

Performance

---

Step 7

Verify bug is fixed.

---

Step 8

Ensure no regressions.

---

Step 9

Document

Cause

Fix

Risk

Lessons learned

---

# Bug Report Template

Bug ID

Title

Severity

Priority

Environment

Steps to Reproduce

Expected Result

Actual Result

Root Cause

Fix Implemented

Affected Modules

Tests Added

Regression Status

Resolved By

Resolution Date

---

# Debugging Rules

Never guess.

Never ignore warnings.

Never suppress exceptions.

Never remove logging to hide problems.

Never disable tests to make builds pass.

Never change requirements to hide bugs.

---

# Logging Requirements

Every error should provide

Timestamp

Severity

Module

Function

Exception

Stack Trace

Relevant Context

Suggested Action

Sensitive information must never be logged.

---

# Exception Handling

Catch only expected exceptions.

Always preserve original exception context.

Log before recovery.

Provide meaningful user-facing messages.

Never expose internal stack traces to end users.

---

# Diagnostic Reports

When debugging is complete generate:

==================================

DEBUG REPORT

==================================

Issue ID

Root Cause

Severity

Affected Modules

Reproduction Status

Fix Summary

Files Changed

Tests Added

Regression Result

Performance Impact

Security Impact

Risk Assessment

Overall Status

PASS / FAIL

==================================

---

# Regression Prevention

Every bug must introduce

at least one

new automated test.

A bug without a test
is considered unresolved.

---

# Performance Regression

After every fix verify

Startup Time

Memory Usage

CPU Usage

Disk Activity

Scan Time

Thread Count

If performance worsens,

investigate before merging.

---

# Security Regression

After every fix verify

Path Validation

Delete Safety

Rollback

Permissions

AI Validation

JSON Validation

Input Validation

No new security issues introduced.

---

# Code Review After Bug Fix

Verify

Architecture maintained

No duplicated code

Naming consistent

Tests updated

Documentation updated

No temporary code remains

No debug code remains

No commented-out code remains

---

# Debugging Tools

Preferred tools

Logging

PyTest

Debugger

MyPy

Ruff

Bandit

Coverage

Profilers

Memory Profilers

Static Analysis

Dependency Analysis

Avoid debugging with print().

Use structured logging.

---

# Temporary Debug Code

Temporary debug code

must never

reach production.

Before merge remove

print()

temporary files

debug flags

hardcoded paths

temporary credentials

experimental code

---

# Bug Prevention

Prefer prevention over correction.

Write defensive code.

Validate inputs.

Use type hints.

Fail safely.

Keep modules small.

Write tests first when practical.

Refactor duplicated logic.

---

# AI Agent Responsibilities

The AI agent must:

✔ Reproduce before fixing

✔ Identify root cause

✔ Explain the fix

✔ Add automated tests

✔ Run full regression tests

✔ Generate a debug report

✔ Update documentation

✔ Verify no regressions

Only after all checks pass may the bug be considered resolved.

---

# Golden Rule

Do not fix symptoms.

Fix the root cause.

Every bug should make the codebase stronger than before.

Every bug fix must improve reliability,
maintainability,
and test coverage.