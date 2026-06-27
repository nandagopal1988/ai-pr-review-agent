"""LLM-based code reviewer using OpenAI or Anthropic."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in minimal environments
    yaml = None

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - exercised in minimal environments
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised in minimal environments
    OpenAI = None


@dataclass
class LLMReviewIssue:
    """Represents an issue found by LLM review."""
    title: str
    severity: str
    description: str
    suggestion: Optional[str] = None
    line: Optional[int] = None


@dataclass
class LLMReviewResult:
    """Result of LLM-based code review."""
    issues: List[LLMReviewIssue]
    recommendations: List[str]
    summary: str
    score: int


class LLMReviewer:
    """Reviews code using LLM (OpenAI or Anthropic)."""

    def __init__(
        self,
        config_path: str,
        review_context: str = "",
        review_focus: str = "",
        service_name: str = "",
        standards: str = "",
    ) -> None:
        """Initialize LLM reviewer.

        Args:
            config_path: Path to LLM configuration YAML
            review_context: Additional prompt context for the review
            review_focus: High-level review focus for the agent
            service_name: Service or repository name to reference in the prompt
            standards: Additional custom standards text
        """
        self.provider = "openai"
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.3
        self.max_tokens = 2000
        self.standards: Dict = {}
        self.review_context = review_context or os.getenv("REVIEW_CONTEXT", "")
        self.review_focus = review_focus or os.getenv("REVIEW_FOCUS", "generic service")
        self.service_name = service_name or os.getenv("SERVICE_NAME", "")
        self.custom_standards = standards or os.getenv("REVIEW_STANDARDS", "")

        self.openai_client: Optional[object] = None
        self.anthropic_client: Optional[object] = None

        self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load LLM configuration.
        
        Args:
            config_path: Path to configuration YAML
        """
        try:
            if not Path(config_path).exists():
                print(f"LLM config not found at {config_path}")
                self.initialize_clients()
                return

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if config and "llm" in config:
                llm_config = config["llm"]
                self.provider = llm_config.get("provider", "openai")
                self.model = llm_config.get("model", "gpt-3.5-turbo")
                self.temperature = llm_config.get("temperature", 0.3)
                self.max_tokens = llm_config.get("max_tokens", 2000)

            if config and "standards" in config:
                self.standards = config["standards"]

            self.initialize_clients()

        except Exception as e:
            print(f"Error loading LLM config: {e}")
            self.initialize_clients()

    def initialize_clients(self) -> None:
        """Initialize API clients."""
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)

    async def review_code(
        self,
        code: str,
        language: str,
        file_name: str = "",
        changed_lines: Optional[List[int]] = None,
    ) -> LLMReviewResult:
        """Review code using LLM.
        
        Args:
            code: Code to review
            language: Programming language
            file_name: Source filename
            changed_lines: List of changed line numbers
            
        Returns:
            LLMReviewResult with findings
        """
        if changed_lines is None:
            changed_lines = []

        prompt = self._build_prompt(
            code=code,
            language=language,
            file_name=file_name,
            changed_lines=changed_lines,
        )

        try:
            if self.provider == "openai" and self.openai_client:
                return await self._review_with_openai(prompt)
            elif self.provider == "anthropic" and self.anthropic_client:
                return await self._review_with_anthropic(prompt)
            else:
                print("No LLM provider configured, returning empty review")
                return LLMReviewResult(
                    issues=[],
                    recommendations=[],
                    summary="LLM review unavailable",
                    score=0,
                )

        except Exception as e:
            print(f"Error reviewing code with LLM: {e}")
            return LLMReviewResult(
                issues=[],
                recommendations=[],
                summary="Error during LLM review",
                score=0,
            )

    def _build_prompt(
        self,
        code: str,
        language: str,
        file_name: str = "",
        changed_lines: Optional[List[int]] = None,
    ) -> str:
        """Build a review prompt that can be reused across repositories and services."""
        standards_text = self._format_standards_for_prompt()
        changed_line_context = (
            f"Changed lines: {', '.join(map(str, changed_lines))}"
            if changed_lines
            else "Review the entire code"
        )

        service_context = []
        if self.service_name:
            service_context.append(f"Service: {self.service_name}")
        if self.review_focus:
            service_context.append(f"Review focus: {self.review_focus}")
        if self.review_context:
            service_context.append(f"Review context: {self.review_context}")

        service_context_text = "\n".join(service_context) if service_context else "Generic pull request review"

        return f"""You are an expert code reviewer specializing in {language} and service-oriented pull request reviews.

{changed_line_context}
File: {file_name}

{service_context_text}

Coding Standards to Check:
{standards_text}

Code to Review:
```{language}
{code}
```

Provide your review in JSON format with:
- issues: array of {{title, severity, description, suggestion, line}}
- recommendations: array of actionable suggestions
- summary: brief overall assessment
- score: quality score from 0-100"""

    async def _review_with_openai(self, prompt: str) -> LLMReviewResult:
        """Review using OpenAI API.
        
        Args:
            prompt: Review prompt
            
        Returns:
            LLMReviewResult
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code reviewer. Provide reviews in valid JSON format only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        content = response.choices[0].message.content or ""
        return self._parse_review_response(content)

    async def _review_with_anthropic(self, prompt: str) -> LLMReviewResult:
        """Review using Anthropic API.
        
        Args:
            prompt: Review prompt
            
        Returns:
            LLMReviewResult
        """
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text if response.content else ""
        return self._parse_review_response(content)

    @staticmethod
    def _parse_review_response(content: str) -> LLMReviewResult:
        """Parse LLM review response.
        
        Args:
            content: Response content
            
        Returns:
            LLMReviewResult
        """
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r"\{[\s\S]*\}", content)
            json_str = json_match.group(0) if json_match else content

            parsed = json.loads(json_str)

            issues = [
                LLMReviewIssue(**issue) for issue in parsed.get("issues", [])
            ]
            recommendations = parsed.get("recommendations", [])
            summary = parsed.get("summary", "")
            score = parsed.get("score", 0)

            return LLMReviewResult(
                issues=issues,
                recommendations=recommendations,
                summary=summary,
                score=score,
            )

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return LLMReviewResult(
                issues=[],
                recommendations=[],
                summary="Error parsing review response",
                score=0,
            )

    def _format_standards_for_prompt(self) -> str:
        """Format coding standards for prompt.
        
        Returns:
            Formatted standards text
        """
        lines = []

        for standard, details in self.standards.items():
            if isinstance(details, dict):
                lines.append(f"\n## {standard}")
                lines.append(details.get("description", ""))

                if "rules" in details and isinstance(details["rules"], list):
                    for rule in details["rules"]:
                        lines.append(f"  - {rule}")

        return "\n".join(lines)
