#!/usr/bin/env python3
"""Analyze code against custom review rules."""

import sys
import json
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

from pr_analyzer import PRAnalyzer
from rule_engine import RuleEngine


def analyze_rules() -> None:
    """Analyze PR changes against custom rules."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_rules.py <PR_NUMBER>")
        sys.exit(1)

    try:
        pr_number = int(sys.argv[1])
    except ValueError:
        print(f"Invalid PR number: {sys.argv[1]}")
        sys.exit(1)

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    
    if not token or not repository:
        print("Error: Missing GITHUB_TOKEN or GITHUB_REPOSITORY environment variables")
        sys.exit(1)

    parts = repository.split("/")
    owner, repo = parts[0], parts[1]

    try:
        print(f"Analyzing rules for PR #{pr_number}...")

        pr_analyzer = PRAnalyzer(token, owner, repo)
        rule_engine = RuleEngine("config/review-rules.yaml")

        # Get PR changes
        pr_diff = pr_analyzer.get_pr_changes(pr_number)
        print(f"Found {len(pr_diff.files_changed)} changed files")

        all_violations = []

        # Analyze each file
        for file in pr_diff.files_changed:
            if file.status == "removed":
                continue

            print(f"Analyzing {file.filename}...")

            content = pr_analyzer.get_file_content(file.filename)
            if not content:
                print(f"  Warning: Could not fetch content for {file.filename}")
                continue

            violations = rule_engine.analyze_file_content(content, file.filename)

            # Filter violations to only changed lines
            changed_violations = [
                v for v in violations if v.line in file.changed_lines
            ]

            all_violations.extend(changed_violations)
            print(f"  Found {len(changed_violations)} violations")

        # Aggregate results
        aggregated = rule_engine.get_aggregated_violations(all_violations)

        output = {
            "pr_number": pr_number,
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(pr_diff.files_changed),
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "message": v.message,
                    "file": v.file,
                    "line": v.line,
                    "column": v.column,
                }
                for v in all_violations
            ],
            "summary": {
                "total_violations": aggregated["count"],
                "by_severity": {
                    sev: len(vlist)
                    for sev, vlist in aggregated["by_severity"].items()
                },
                "by_file": {
                    fname: len(vlist)
                    for fname, vlist in aggregated["by_file"].items()
                },
            },
        }

        # Output results
        print("\n=== RULE ANALYSIS RESULTS ===")
        print(json.dumps(output, indent=2))

        # Write to file
        os.makedirs(".", exist_ok=True)
        with open("rules-output.json", "w") as f:
            json.dump(output, f, indent=2)
        print("\nResults written to rules-output.json")

        sys.exit(1 if aggregated["count"] > 0 else 0)

    except Exception as e:
        print(f"Error analyzing rules: {e}")
        sys.exit(1)


if __name__ == "__main__":
    analyze_rules()
