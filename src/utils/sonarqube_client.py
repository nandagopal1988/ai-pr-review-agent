"""SonarQube client for code analysis."""

import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class SonarQubeIssue:
    """Represents a SonarQube issue."""
    key: str
    type: str
    severity: str
    message: str
    component: str
    line: Optional[int] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    rule: str = ""
    status: str = ""
    effort: Optional[str] = None
    creation_date: str = ""


@dataclass
class SonarQubeAnalysis:
    """SonarQube analysis results."""
    project_key: str
    analysis_date: str
    issues: List[SonarQubeIssue]
    metrics: Dict[str, Any]


class SonarQubeClient:
    """Client for SonarQube API."""

    def __init__(self, host: str, token: str) -> None:
        """Initialize SonarQube client.
        
        Args:
            host: SonarQube host URL
            token: SonarQube API token
        """
        self.host = host
        self.token = token
        self.session = requests.Session()
        self.session.auth = (token, "")

    def get_project_issues(
        self, project_key: str, branch: Optional[str] = None
    ) -> List[SonarQubeIssue]:
        """Get issues for a project.
        
        Args:
            project_key: SonarQube project key
            branch: Optional branch name
            
        Returns:
            List of SonarQubeIssue objects
        """
        try:
            params = {
                "componentKeys": project_key,
                "resolved": False,
                "ps": 500,
            }

            if branch:
                params["branch"] = branch

            url = f"{self.host}/api/issues/search"
            response = self.session.get(url, params=params)
            response.raise_for_status()

            issues = []
            for issue_data in response.json().get("issues", []):
                issue = SonarQubeIssue(
                    key=issue_data["key"],
                    type=issue_data["type"],
                    severity=issue_data["severity"],
                    message=issue_data["message"],
                    component=issue_data["component"],
                    line=issue_data.get("line"),
                    start_line=issue_data.get("startLine"),
                    end_line=issue_data.get("endLine"),
                    rule=issue_data["rule"],
                    status=issue_data["status"],
                    creation_date=issue_data["creationDate"],
                )
                issues.append(issue)

            return issues

        except Exception as e:
            print(f"Error fetching SonarQube issues for {project_key}: {e}")
            return []

    def get_pr_quality_gate(self, project_key: str, pr_key: str) -> bool:
        """Check if PR passes quality gate.
        
        Args:
            project_key: SonarQube project key
            pr_key: Pull request key
            
        Returns:
            True if quality gate passes, False otherwise
        """
        try:
            url = f"{self.host}/api/qualitygates/project_status"
            params = {"projectKey": project_key, "pullRequest": pr_key}
            response = self.session.get(url, params=params)
            response.raise_for_status()

            status = response.json()["projectStatus"]["status"]
            return status == "OK"

        except Exception as e:
            print(f"Error checking quality gate for PR {pr_key}: {e}")
            return False

    def get_code_metrics(self, project_key: str) -> Dict[str, Any]:
        """Get code metrics for a project.
        
        Args:
            project_key: SonarQube project key
            
        Returns:
            Dictionary of metrics
        """
        try:
            metrics_list = [
                "coverage",
                "ncloc",
                "complexity",
                "violations",
                "blocker_violations",
                "critical_violations",
                "bugs",
                "code_smells",
                "vulnerabilities",
            ]

            url = f"{self.host}/api/measures/component"
            params = {
                "component": project_key,
                "metricKeys": ",".join(metrics_list),
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            metrics = {}
            for measure in response.json()["component"].get("measures", []):
                metrics[measure["metric"]] = measure["value"]

            return metrics

        except Exception as e:
            print(f"Error fetching metrics for {project_key}: {e}")
            return {}

    def analyze_file(
        self, project_key: str, file_path: str
    ) -> List[SonarQubeIssue]:
        """Get issues for a specific file.
        
        Args:
            project_key: SonarQube project key
            file_path: File path in project
            
        Returns:
            List of SonarQubeIssue objects
        """
        try:
            file_key = f"{project_key}:{file_path}"
            url = f"{self.host}/api/issues/search"
            params = {
                "componentKeys": file_key,
                "resolved": False,
                "ps": 500,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            issues = []
            for issue_data in response.json().get("issues", []):
                issue = SonarQubeIssue(
                    key=issue_data["key"],
                    type=issue_data["type"],
                    severity=issue_data["severity"],
                    message=issue_data["message"],
                    component=issue_data["component"],
                    line=issue_data.get("line"),
                )
                issues.append(issue)

            return issues

        except Exception as e:
            print(f"Error analyzing file {file_path} in SonarQube: {e}")
            return []

    def trigger_analysis(self, project_key: str) -> str:
        """Trigger analysis for a project.
        
        Args:
            project_key: SonarQube project key
            
        Returns:
            Task ID
        """
        try:
            url = f"{self.host}/api/ce/submit"
            params = {"projectKey": project_key}
            response = self.session.post(url, params=params)
            response.raise_for_status()

            return response.json()["taskId"]

        except Exception as e:
            print(f"Error triggering analysis for {project_key}: {e}")
            raise

    def get_analysis_status(self, task_id: str) -> str:
        """Get status of analysis task.
        
        Args:
            task_id: Task ID from trigger_analysis
            
        Returns:
            Task status
        """
        try:
            url = f"{self.host}/api/ce/activity"
            params = {"id": task_id}
            response = self.session.get(url, params=params)
            response.raise_for_status()

            return response.json()["task"]["status"]

        except Exception as e:
            print(f"Error getting analysis status for task {task_id}: {e}")
            raise
