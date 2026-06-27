"""Pull Request analyzer for GitHub."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from github import Github, Repository, PullRequest as GithubPullRequest


@dataclass
class ChangedFile:
    """Represents a changed file in a PR."""
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    changed_lines: List[int] = None

    def __post_init__(self) -> None:
        if self.changed_lines is None:
            self.changed_lines = []


@dataclass
class PRDiff:
    """Represents PR changes."""
    pr_number: int
    files_changed: List[ChangedFile]
    total_additions: int
    total_deletions: int
    total_changes: int


class PRAnalyzer:
    """Analyzes pull request changes."""

    def __init__(self, token: str, owner: str, repo: str) -> None:
        """Initialize PR analyzer.
        
        Args:
            token: GitHub API token
            owner: Repository owner
            repo: Repository name
        """
        self.github = Github(token)
        self.owner = owner
        self.repo = repo
        self.repository = self.github.get_user(owner).get_repo(repo)

    def get_pr_changes(self, pr_number: int) -> PRDiff:
        """Get all changes in a pull request.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            PRDiff object with all changes
        """
        try:
            pr = self.repository.get_pull(pr_number)
            files = pr.get_files()

            changed_files = []
            for file in files:
                changed_lines = self._extract_changed_lines(file.patch or "")
                changed_file = ChangedFile(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                    changed_lines=changed_lines,
                )
                changed_files.append(changed_file)

            return PRDiff(
                pr_number=pr_number,
                files_changed=changed_files,
                total_additions=sum(f.additions for f in changed_files),
                total_deletions=sum(f.deletions for f in changed_files),
                total_changes=sum(f.changes for f in changed_files),
            )
        except Exception as e:
            print(f"Error fetching PR changes for PR #{pr_number}: {e}")
            raise

    @staticmethod
    def _extract_changed_lines(patch: str) -> List[int]:
        """Extract line numbers of changed lines from patch.
        
        Args:
            patch: Unified diff patch
            
        Returns:
            List of changed line numbers
        """
        lines = []
        current_line_number = 0

        for line in patch.split("\n"):
            if line.startswith("@@"):
                # Extract starting line number from hunk header
                parts = line.split()
                if len(parts) >= 3:
                    new_range = parts[2]  # e.g., "+42,15"
                    line_num = int(new_range.split(",")[0][1:])
                    current_line_number = line_num
            elif line.startswith("+") and not line.startswith("+++"):
                lines.append(current_line_number)
                current_line_number += 1
            elif not line.startswith("-"):
                current_line_number += 1

        return lines

    def get_file_content(self, filename: str, ref: str = "HEAD") -> str:
        """Get content of a file from repository.
        
        Args:
            filename: File path in repository
            ref: Git reference (branch, tag, or commit)
            
        Returns:
            File content as string
        """
        try:
            content = self.repository.get_contents(filename, ref=ref)
            return content.decoded_content.decode("utf-8")
        except Exception as e:
            print(f"Error fetching content for {filename}: {e}")
            return ""

    def get_changed_code_snippets(self, pr_number: int) -> Dict[str, str]:
        """Get code snippets for all changed files in PR.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dictionary mapping filename to file content
        """
        pr_diff = self.get_pr_changes(pr_number)
        snippets = {}

        for file in pr_diff.files_changed:
            if file.status == "removed":
                continue

            content = self.get_file_content(file.filename)
            if content:
                snippets[file.filename] = content

        return snippets
