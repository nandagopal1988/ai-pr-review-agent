"""Main code review agent module."""

import asyncio
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .pr_analyzer import PRAnalyzer
from .llm_reviewer import LLMReviewer
from .rule_engine import RuleEngine

from .coverage_analyzer import CoverageAnalyzer
from .sonarqube_client import SonarQubeClient


@dataclass
class ReviewRequest:
    """Code review request."""
    pr_number: int
    owner: str
    repo: str
    base_ref: str
    head_ref: str


@dataclass
class ReviewResult:
    """Code review result."""
    pr_number: int
    rules_violations: List
    coverage_analysis: Dict
    sonarqube_analysis: Optional[Dict] = None
    llm_review: Optional[Dict] = None
    summary: Optional[Dict] = None


class CodeReviewAgent:
    """AI-powered code review agent for GitHub PRs."""

    def __init__(self) -> None:
        """Initialize a generic PR review agent for GitHub Copilot."""
        token = os.getenv("GITHUB_TOKEN", "")
        repository = os.getenv("GITHUB_REPOSITORY", "")
        parts = repository.split("/")

        owner = parts[0] if len(parts) > 0 else ""
        repo = parts[1] if len(parts) > 1 else ""

        self.owner = owner
        self.repo = repo
        self.service_name = os.getenv(
            "SERVICE_NAME",
            os.getenv("REPO_NAME", repo or "generic-service"),
        )
        self.review_focus = os.getenv("REVIEW_FOCUS", "generic service")
        self.review_context = os.getenv(
            "REVIEW_CONTEXT",
            "Review pull requests for correctness, architecture, security, and service compatibility.",
        )
        self.review_standards = os.getenv("REVIEW_STANDARDS", "")

        self.pr_analyzer = PRAnalyzer(token, owner, repo)
        self.coverage_analyzer = CoverageAnalyzer()
        self.rule_engine = RuleEngine("config/review-rules.yaml")
        self.llm_reviewer = LLMReviewer(
            "config/llm-config.yaml",
            review_context=self.review_context,
            review_focus=self.review_focus,
            service_name=self.service_name,
            standards=self.review_standards,
        )

        # Initialize SonarQube if configured
        self.sonarqube_client: Optional[SonarQubeClient] = None
        if (
            os.getenv("SONARQUBE_ENABLED") == "true"
            and os.getenv("SONARQUBE_HOST_URL")
            and os.getenv("SONARQUBE_TOKEN")
        ):
            self.sonarqube_client = SonarQubeClient(
                os.getenv("SONARQUBE_HOST_URL", ""),
                os.getenv("SONARQUBE_TOKEN", ""),
            )

    async def review_pull_request(
        self, request: ReviewRequest
    ) -> ReviewResult:
        """Review a pull request.
        
        Args:
            request: ReviewRequest object
            
        Returns:
            ReviewResult with analysis
        """
        print(f"Starting review for PR #{request.pr_number}...")

        try:
            # Get PR changes
            pr_diff = self.pr_analyzer.get_pr_changes(request.pr_number)
            changed_files = {
                f.filename: f.changed_lines for f in pr_diff.files_changed
            }

            # Analyze with custom rules
            rules_violations = []
            for file in pr_diff.files_changed:
                if file.status == "removed":
                    continue

                content = self.pr_analyzer.get_file_content(file.filename)
                if content:
                    violations = self.rule_engine.analyze_file_content(
                        content, file.filename
                    )
                    rules_violations.extend(violations)

            # Analyze code coverage
            coverage_analysis = await self.coverage_analyzer.analyze_pr_coverage(
                os.getenv("COVERAGE_REPORT_PATH", "coverage/lcov.info"),
                changed_files,
            )

            # Get SonarQube analysis
            sonarqube_analysis = None
            if self.sonarqube_client:
                project_key = os.getenv(
                    "SONARQUBE_PROJECT_KEY", "default"
                )
                issues = self.sonarqube_client.get_project_issues(
                    project_key, request.head_ref
                )
                metrics = self.sonarqube_client.get_code_metrics(project_key)
                sonarqube_analysis = {
                    "issues": [asdict(i) for i in issues],
                    "metrics": metrics,
                }

            # Get LLM review
            llm_review = {"issues": [], "recommendations": [], "score": 0}
            files_reviewed = 0

            for file in pr_diff.files_changed:
                if files_reviewed >= 3:
                    break
                if file.status == "removed":
                    continue

                content = self.pr_analyzer.get_file_content(file.filename)
                if content:
                    review = await self.llm_reviewer.review_code(
                        content,
                        self._detect_language(file.filename),
                        file.filename,
                        file.changed_lines,
                    )

                    if review.issues:
                        llm_review["issues"].extend(
                            [asdict(i) for i in review.issues]
                        )
                    if review.recommendations:
                        llm_review["recommendations"].extend(
                            review.recommendations
                        )
                    if review.score > 0:
                        llm_review["score"] += review.score

                    files_reviewed += 1

            if files_reviewed > 0:
                llm_review["score"] = llm_review["score"] // files_reviewed

            # Calculate summary
            critical_issues = sum(
                1 for v in rules_violations if v.severity == "critical"
            )
            total_issues = len(rules_violations)

            summary = {
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "coverage": coverage_analysis.new_code,
                "score": llm_review.get("score", 0),
            }

            return ReviewResult(
                pr_number=request.pr_number,
                rules_violations=[asdict(v) for v in rules_violations],
                coverage_analysis=asdict(coverage_analysis),
                sonarqube_analysis=sonarqube_analysis,
                llm_review=llm_review,
                summary=summary,
            )

        except Exception as e:
            print(f"Error reviewing PR #{request.pr_number}: {e}")
            raise

    @staticmethod
    def _detect_language(filename: str) -> str:
        """Detect programming language from filename.
        
        Args:
            filename: File path
            
        Returns:
            Language string
        """
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
    agent = CodeReviewAgent()
    print("Code Review Agent initialized successfully")
