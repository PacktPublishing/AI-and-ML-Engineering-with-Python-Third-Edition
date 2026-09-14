---
name: security-audit
description: Scans codebases for leaked secrets and unpatched vulnerabilities. Use when a user asks to review code, pushes to staging, or explicitly requests a security audit.
license: Apache-2.0
compatibility: Requires python >=3.10 and git CLI
allowed-tools: read_file run_terminal_command
metadata:
  version: "1.2.0"
---
# Security Audit Protocol

When executing this skill, adhere to the following steps:
1. Run the script found in `./scripts/scan.py`.
2. Cross-reference results with the corporate policy in `./references/policy.md`.
3. Generate a summary inside the terminal.
