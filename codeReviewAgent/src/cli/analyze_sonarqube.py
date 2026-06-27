#!/usr/bin/env python3
"""Analyze code with SonarQube."""

import sys
import json
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))

from sonarqube_client import SonarQubeClient


def analyze_sonarqube() -> None:
    """Analyze code with SonarQube."""
    host = os.getenv("SONARQUBE_HOST_URL")
    token = os.getenv("SONARQUBE_TOKEN")
    project_key = os.getenv("SONARQUBE_PROJECT_KEY", "default")

    if not host or not token:
        print(
            "Error: Missing SONARQUBE_HOST_URL or SONARQUBE_TOKEN environment variables"
        )
        sys.exit(1)

    try:
        print(f"Analyzing project {project_key} with SonarQube...")

        sonarqube = SonarQubeClient(host, token)

        # Get issues
        issues = sonarqube.get_project_issues(project_key)
        print(f"Found {len(issues)} issues")

        # Get metrics
        metrics = sonarqube.get_code_metrics(project_key)
        print(f"Retrieved {len(metrics)} metrics")

        # Count issues by severity
        by_severity = {}
        by_type = {}

        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_type[issue.type] = by_type.get(issue.type, 0) + 1

        output = {
            "project_key": project_key,
            "timestamp": datetime.now().isoformat(),
            "issues": [
                {
                    "key": i.key,
                    "type": i.type,
                    "severity": i.severity,
                    "message": i.message,
                    "component": i.component,
                    "line": i.line,
                    "rule": i.rule,
                }
                for i in issues
            ],
            "metrics": metrics,
            "summary": {
                "total_issues": len(issues),
                "by_severity": by_severity,
                "by_type": by_type,
            },
        }

        # Output results
        print("\n=== SONARQUBE ANALYSIS RESULTS ===")
        print(json.dumps(output, indent=2))

        # Write to file
        os.makedirs("sonarqube-report", exist_ok=True)
        with open("sonarqube-report/analysis.json", "w") as f:
            json.dump(output, f, indent=2)
        print("\nResults written to sonarqube-report/analysis.json")

        sys.exit(1 if len(issues) > 0 else 0)

    except Exception as e:
        print(f"Error analyzing with SonarQube: {e}")
        sys.exit(1)


if __name__ == "__main__":
    analyze_sonarqube()
