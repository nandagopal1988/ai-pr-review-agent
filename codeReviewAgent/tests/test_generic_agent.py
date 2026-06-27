from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_agent_builds_generic_review_context(monkeypatch):
    from code_review_agent import CodeReviewAgent

    monkeypatch.setenv("REVIEW_FOCUS", "spring boot service")
    monkeypatch.setenv("SERVICE_NAME", "billing-service")
    monkeypatch.setenv("REVIEW_CONTEXT", "Focus on API contracts and transaction boundaries")

    agent = CodeReviewAgent()

    assert agent.service_name == "billing-service"
    assert agent.review_focus == "spring boot service"
    assert "API contracts" in agent.review_context


def test_llm_reviewer_uses_custom_context():
    from utils.llm_reviewer import LLMReviewer

    reviewer = LLMReviewer(
        "config/llm-config.yaml",
        review_context="Review this Spring Boot PR for resilience and API compatibility",
    )

    prompt = reviewer._build_prompt(
        code="@Service\npublic class DemoService {}",
        language="java",
        file_name="DemoService.java",
        changed_lines=[1, 2],
    )

    assert "Spring Boot PR" in prompt
    assert "resilience" in prompt
