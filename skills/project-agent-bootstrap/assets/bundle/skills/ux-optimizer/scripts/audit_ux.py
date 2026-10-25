#!/usr/bin/env python3
"""
UX & Accessibility Auditor CLI
Part of the ux-optimizer skill.
Audits frontend code for 2025/2026 UX heuristics, WCAG 2.2 AA accessibility,
and FinTech calibrated friction patterns.
"""

import argparse
import os
import re
import sys
import subprocess
from pathlib import Path

# Common patterns for detection
PATTERNS = [
    {
        "id": "target-size-small",
        "category": "WCAG 2.5.8 Target Size",
        "severity": "WARNING",
        "regex": re.compile(r'(<button|<a|onClick)[^>]*(?:w-[345]\s|h-[345]\s|w-[345]"|h-[345]")[^>]*>', re.IGNORECASE),
        "message": "Interactive element appears smaller than 24x24px (WCAG 2.2 Level AA). Ensure minimum 24x24px bounds (recommended 44x44px for touch).",
        "remediation": "Add min-w-[24px] min-h-[24px] or expand padding (e.g. p-2.5) to satisfy target size."
    },
    {
        "id": "outline-none-suppression",
        "category": "WCAG 2.4.7 Focus Visible",
        "severity": "ERROR",
        "regex": re.compile(r'class(?:Name)?="[^"]*(?:focus:outline-none|outline-none)[^"]*"', re.IGNORECASE),
        "negative_regex": re.compile(r'focus-visible:ring|focus:ring', re.IGNORECASE),
        "message": "Focus indicator suppressed with outline-none without explicit focus-visible ring replacement.",
        "remediation": "Add 'focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none' to ensure keyboard accessibility."
    },
    {
        "id": "icon-button-missing-label",
        "category": "WCAG 4.1.2 Name, Role, Value",
        "severity": "WARNING",
        "regex": re.compile(r'<button(?![^>]*aria-label)[^>]*>\s*<(?:svg|[A-Z][a-zA-Z]+Icon)[^>]*>\s*</button>', re.IGNORECASE | re.DOTALL),
        "message": "Icon-only button missing an aria-label attribute.",
        "remediation": "Add aria-label=\"Action description\" to the button element."
    },
    {
        "id": "sticky-missing-scroll-padding",
        "category": "WCAG 2.4.11 Focus Not Obscured",
        "severity": "INFO",
        "regex": re.compile(r'class(?:Name)?="[^"]*(?:sticky\s+top-0|fixed\s+top-0)[^"]*"', re.IGNORECASE),
        "message": "Sticky header detected. Ensure scrollable container or root has matching scroll-padding-top to prevent obscured focus.",
        "remediation": "Add 'scroll-pt-16' or equivalent scroll padding to avoid covering focused elements during keyboard navigation."
    },
    {
        "id": "hardcoded-dark-light-colors",
        "category": "Design Tokens & Theming",
        "severity": "INFO",
        "regex": re.compile(r'class(?:Name)?="[^"]*(?:bg-slate-900|bg-zinc-900|bg-gray-900|text-black|text-white)[^"]*"', re.IGNORECASE),
        "message": "Hardcoded surface or text colors detected instead of semantic theme tokens.",
        "remediation": "Use semantic tokens: bg-[var(--card)], bg-[var(--background)], text-[var(--foreground)], or Tailwind theme classes."
    },
    {
        "id": "missing-tabular-numbers",
        "category": "FinTech Data Density",
        "severity": "INFO",
        "regex": re.compile(r'(?:[$€£¥]\s*\{?|\bbalance\b|\bamount\b)[^<>\n]*</span>', re.IGNORECASE),
        "negative_regex": re.compile(r'tabular-nums|font-mono', re.IGNORECASE),
        "message": "Financial currency or balance rendered without tabular figures or monospace styling.",
        "remediation": "Apply 'tabular-nums' or 'font-mono' to prevent layout shifts during numerical updates and align decimals."
    }
]

def audit_file(filepath: Path):
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return []

    lines = content.splitlines()
    findings = []

    for pattern_def in PATTERNS:
        # Check overall or per-line
        for line_num, line in enumerate(lines, start=1):
            if pattern_def["regex"].search(line):
                neg = pattern_def.get("negative_regex")
                if neg and neg.search(line):
                    continue
                findings.append({
                    "file": str(filepath),
                    "line": line_num,
                    "snippet": line.strip()[:100],
                    "id": pattern_def["id"],
                    "category": pattern_def["category"],
                    "severity": pattern_def["severity"],
                    "message": pattern_def["message"],
                    "remediation": pattern_def["remediation"]
                })
    return findings

def audit_directory(path: Path):
    findings = []
    extensions = {'.tsx', '.jsx', '.html', '.vue', '.svelte'}
    for root, _, files in os.walk(path):
        if 'node_modules' in root or '.git' in root or 'dist' in root or 'build' in root:
            continue
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = Path(root) / file
                findings.extend(audit_file(filepath))
    return findings

def generate_prototype_boilerplate(title: str, output_path: str):
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-4">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-6 shadow-sm max-w-2xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-[var(--border)] pb-4">
      <div>
        <h2 class="text-lg font-semibold tracking-tight text-[var(--foreground)]">{title}</h2>
        <p class="text-xs text-[var(--muted-foreground)]">WCAG 2.2 AA Verified • Calibrated Friction</p>
      </div>
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
        Live Prototype
      </span>
    </div>

    <!-- Interactive Component Card -->
    <div class="space-y-4">
      <div class="p-4 rounded-xl bg-[var(--background)] border border-[var(--border)] space-y-3">
        <div class="flex justify-between items-baseline">
          <span class="text-xs font-medium text-[var(--muted-foreground)] uppercase tracking-wider">Account Overview</span>
          <span class="text-xs font-mono tabular-nums text-emerald-500 font-medium">+2.4% this month</span>
        </div>
        <div class="text-2xl font-bold font-mono tabular-nums text-[var(--foreground)]">
          $12,450.80
        </div>
        <p class="text-xs text-[var(--muted-foreground)]">Available Balance (Instant settlement)</p>
      </div>

      <!-- Action Buttons with Calibrated Friction -->
      <div class="grid grid-cols-2 gap-3">
        <button type="button" class="w-full min-h-[44px] px-4 py-2.5 rounded-xl font-medium text-sm border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] hover:bg-[var(--muted)] focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:outline-none transition-all active:scale-[0.98]">
          Deposit
        </button>
        <button type="button" class="w-full min-h-[44px] px-4 py-2.5 rounded-xl font-medium text-sm bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:outline-none transition-all active:scale-[0.98]">
          Transfer Funds
        </button>
      </div>
    </div>
  </div>
</body>
</html>
"""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(template, encoding='utf-8')
    print(f"Prototype created successfully at: {out_file.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="UX & Accessibility Auditor")
    subparsers = parser.add_subparsers(dest="command")

    audit_parser = subparsers.add_parser("audit", help="Audit a file or directory for UX/a11y issues")
    audit_parser.add_argument("path", help="Path to file or folder to audit")

    proto_parser = subparsers.add_parser("prototype", help="Generate Generative UI prototype boilerplate")
    proto_parser.add_argument("title", help="Title of prototype")
    proto_parser.add_argument("--output", "-o", required=True, help="Destination HTML file path")

    args = parser.parse_args()

    if args.command == "audit":
        target = Path(args.path)
        if not target.exists():
            print(f"Error: Path {target} does not exist", file=sys.stderr)
            sys.exit(1)
        if target.is_file():
            findings = audit_file(target)
        else:
            findings = audit_directory(target)

        print(f"## UX & Accessibility Audit Report for `{target}`")
        print(f"Total findings: **{len(findings)}**\n")

        if not findings:
            print(" No immediate UX anti-patterns or WCAG 2.2 issues flagged.")
            return

        for idx, f in enumerate(findings, 1):
            print(f"### {idx}. [{f['severity']}] {f['category']}: {f['id']}")
            print(f"- **File:** `{f['file']}:{f['line']}`")
            print(f"- **Snippet:** `{f['snippet']}`")
            print(f"- **Issue:** {f['message']}")
            print(f"- **Remediation:** {f['remediation']}\n")

    elif args.command == "prototype":
        generate_prototype_boilerplate(args.title, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
