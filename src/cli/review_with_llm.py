#!/usr/bin/env python3
"""Review code with LLM."""

import sys
import json
import os
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

from pr_analyzer import PRAnalyzer
from llm_reviewer import LLMReviewer


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
    return "review-output.json"


async def review_with_llm() -> None:
    """Review code with LLM."""
    pr_number = extract_pr_number(sys.argv)
    output_file = get_output_file(sys.argv)

    if not pr_number:
        print("Usage: python review_with_llm.py --pr-number <PR_NUMBER> [--output <FILE>]")
        sys.exit(1)

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")

    if not token or not repository:
        print("Error: Missing GITHUB_TOKEN or GITHUB_REPOSITORY environment variables")
        sys.exit(1)

    parts = repository.split("/")
    owner, repo = parts[0], parts[1]

    try:
        print(f"Running LLM-based review for PR #{pr_number}...")

        pr_analyzer = PRAnalyzer(token, owner, repo)
        llm_reviewer = LLMReviewer("config/llm-config.yaml")

        # Get PR changes
        pr_diff = pr_analyzer.get_pr_changes(pr_number)
        print(f"Found {pr_diff.total_changes} total changes")

        all_issues = []
        all_recommendations = set()
        total_score = 0
        reviews_performed = 0

        # Review first 5 files to avoid token overuse
        files_to_review = [
            f for f in pr_diff.files_changed if f.status != "removed"
        ][:5]

        for file in files_to_review:
            print(f"Reviewing {file.filename}...")

            content = pr_analyzer.get_file_content(file.filename)
            if not content:
                print(f"  Warning: Could not fetch content for {file.filename}")
                continue

            review = await llm_reviewer.review_code(
                content,
                detect_language(file.filename),
                file.filename,
                file.changed_lines,
            )

            if review.issues:
                for issue in review.issues:
                    all_issues.append(
                        {
                            "title": issue.title,
                            "severity": issue.severity,
                            "description": issue.description,
                            "suggestion": issue.suggestion,
                            "file": file.filename,
                        }
                    )

            if review.recommendations:
                all_recommendations.update(review.recommendations)

            total_score += review.score
            reviews_performed += 1

            print(f"  Found {len(review.issues)} issues")

        average_score = (
            total_score // reviews_performed if reviews_performed > 0 else 0
        )

        output = {
            "pr_number": pr_number,
            "timestamp": datetime.now().isoformat(),
            "files_reviewed": reviews_performed,
            "issues": all_issues,
            "recommendations": list(all_recommendations),
            "summary": {
                "total_issues": len(all_issues),
                "by_severity": {
                    sev: sum(1 for i in all_issues if i["severity"] == sev)
                    for sev in ["critical", "high", "medium", "low"]
                },
                "average_score": average_score,
            },
        }

        # Output results
        print("\n=== LLM REVIEW RESULTS ===")
        print(json.dumps(output, indent=2))

        # Write to file
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to {output_file}")

        sys.exit(1 if len(all_issues) > 0 else 0)

    except Exception as e:
        print(f"Error reviewing with LLM: {e}")
        sys.exit(1)


def detect_language(filename: str) -> str:
    """Detect language from filename."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    lang_map = {
        "java": "java",
        "py": "python",
        "ts": "typescript",
        "tsx": "typescript",
        "js": "javascript",
        "jsx": "javascript",
        "cs": "csharp",
        "go": "go",
        "rb": "ruby",
        "php": "php",
        "swift": "swift",
        "kt": "kotlin",
    }

    return lang_map.get(ext, "unknown")


if __name__ == "__main__":
    asyncio.run(review_with_llm())
