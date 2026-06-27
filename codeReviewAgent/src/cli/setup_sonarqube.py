#!/usr/bin/env python3
"""Extract PR changes."""

import sys
import json
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

from pr_analyzer import PRAnalyzer


def extract_pr_number(args: list) -> int:
    """Extract PR number from arguments."""
    for i, arg in enumerate(args):
        if arg == "--pr-number" and i + 1 < len(args):
            try:
                return int(args[i + 1])
            except ValueError:
                pass
    return 0


def get_output_file(args: list) -> str:
    """Extract output filename from arguments."""
    for i, arg in enumerate(args):
        if arg == "--output" and i + 1 < len(args):
            return args[i + 1]
    return "changed-code.json"


def extract_changes() -> None:
    """Extract changes from PR."""
    pr_number = extract_pr_number(sys.argv)
    output_file = get_output_file(sys.argv)

    if not pr_number:
        print("Usage: python extract_changes.py --pr-number <PR_NUMBER> [--output <FILE>]")
        sys.exit(1)

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")

    if not token or not repository:
        print("Error: Missing GITHUB_TOKEN or GITHUB_REPOSITORY environment variables")
        sys.exit(1)

    parts = repository.split("/")
    owner, repo = parts[0], parts[1]

    try:
        print(f"Extracting changes for PR #{pr_number}...")

        pr_analyzer = PRAnalyzer(token, owner, repo)
        pr_diff = pr_analyzer.get_pr_changes(pr_number)

        output = {
            "pr_number": pr_number,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": len(pr_diff.files_changed),
                "total_additions": pr_diff.total_additions,
                "total_deletions": pr_diff.total_deletions,
                "total_changes": pr_diff.total_changes,
            },
            "files": [
                {
                    "filename": f.filename,
                    "status": f.status,
                    "additions": f.additions,
                    "deletions": f.deletions,
                    "changes": f.changes,
                    "changed_lines": f.changed_lines,
                }
                for f in pr_diff.files_changed
            ],
        }

        # Output results
        print("\n=== EXTRACTED CHANGES ===")
        print(json.dumps(output, indent=2))

        # Write to file
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to {output_file}")

        sys.exit(0)

    except Exception as e:
        print(f"Error extracting changes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    extract_changes()
