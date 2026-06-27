"""Code Review Agent - AI-powered PR review for Spring Boot microservices."""

__version__ = "1.0.0"
__author__ = "Your Team"
__description__ = "AI code review agent with GitHub Copilot integration for Spring Boot"

from src.code_review_agent import CodeReviewAgent, ReviewRequest, ReviewResult

__all__ = ["CodeReviewAgent", "ReviewRequest", "ReviewResult"]
