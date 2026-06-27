import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from utils.llm_reviewer import LLMReviewer
except Exception as exc:  # pragma: no cover - defensive fallback
    print(f"LLM reviewer import failed: {exc}")
    LLMReviewer = None


def main() -> None:
    review_context = os.getenv("REVIEW_CONTEXT", "Review this pull request for correctness and service reliability")
    review_focus = os.getenv("REVIEW_FOCUS", "generic service")
    service_name = os.getenv("SERVICE_NAME", "generic-service")
    standards = os.getenv("REVIEW_STANDARDS", "")

    if LLMReviewer is None:
        result = None
    else:
        reviewer = LLMReviewer(
            "config/llm-config.yaml",
            review_context=review_context,
            review_focus=review_focus,
            service_name=service_name,
            standards=standards,
        )

        sample_code = """
@Service
public class DemoService {
    public String process(String input) {
        return input.toUpperCase();
    }
}
"""

        result = asyncio.run(
            reviewer.review_code(
                code=sample_code,
                language="java",
                file_name="DemoService.java",
                changed_lines=[1, 2, 3],
            )
        )

    with open("llm-review.md", "w", encoding="utf-8") as handle:
        handle.write("## 🤖 LLM Review\n\n")
        if result is None:
            handle.write("- LLM review skipped because the reviewer could not be initialized.\n")
        else:
            handle.write(f"**Summary:** {result.summary}\n\n")
            if result.issues:
                handle.write("### Issues\n")
                for issue in result.issues:
                    handle.write(f"- **{issue.severity}** {issue.title}: {issue.description}\n")
                handle.write("\n")
            if result.recommendations:
                handle.write("### Recommendations\n")
                for recommendation in result.recommendations:
                    handle.write(f"- {recommendation}\n")
                handle.write("\n")
            handle.write(f"**Score:** {result.score}/100\n")

    print("LLM review written to llm-review.md")


if __name__ == "__main__":
    main()
