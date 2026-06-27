import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from utils.rule_engine import RuleEngine
except Exception as exc:  # pragma: no cover - defensive fallback
    print(f"Rule engine import failed: {exc}")
    RuleEngine = None


def main() -> None:
    sample_code = """
@Service
public class DemoService {
    public String process(String input) {
        System.out.println("debug");
        return input.toUpperCase();
    }
}
"""

    if RuleEngine is None:
        print("Rule engine unavailable; creating empty review output")
        violations = []
    else:
        engine = RuleEngine("config/review-rules.yaml")
        violations = engine.analyze_code(sample_code, "java", "DemoService.java")

    with open("rule-review.json", "w", encoding="utf-8") as handle:
        json.dump(
            [
                {
                    "rule_id": violation.rule_id,
                    "rule_name": violation.rule_name,
                    "severity": violation.severity,
                    "message": violation.message,
                    "file": violation.file,
                    "line": violation.line,
                }
                for violation in violations
            ],
            handle,
            indent=2,
        )

    print(f"Rule review wrote {len(violations)} violations")


if __name__ == "__main__":
    main()
