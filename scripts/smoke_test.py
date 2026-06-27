import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from code_review_agent import CodeReviewAgent


def main() -> None:
    os.environ.setdefault("SERVICE_NAME", "billing-service")
    os.environ.setdefault("REVIEW_FOCUS", "spring boot service")
    os.environ.setdefault("REVIEW_CONTEXT", "Focus on API contracts and transaction boundaries")

    agent = CodeReviewAgent()
    print("Agent initialized")
    print(f"Service: {agent.service_name}")
    print(f"Focus: {agent.review_focus}")
    print(f"Context: {agent.review_context}")


if __name__ == "__main__":
    main()
