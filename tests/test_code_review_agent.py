"""Python tests for code review agent."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


class TestRuleEngine:
    """Test rule engine."""

    def test_rule_loading(self) -> None:
        """Test that rules are loaded."""
        from rule_engine import RuleEngine

        engine = RuleEngine("config/review-rules.yaml")
        rules = engine.get_all_rules()
        assert len(rules) > 0

    def test_detect_language(self) -> None:
        """Test language detection."""
        from rule_engine import RuleEngine

        assert RuleEngine._detect_language("test.java") == "java"
        assert RuleEngine._detect_language("test.py") == "python"
        assert RuleEngine._detect_language("test.ts") == "typescript"
        assert RuleEngine._detect_language("test.js") == "javascript"


class TestCoverageAnalyzer:
    """Test coverage analyzer."""

    def test_calculate_coverage(self) -> None:
        """Test coverage calculation."""
        from coverage_analyzer import CoverageAnalyzer, CoverageData

        coverage_data = CoverageData(
            file="test.py",
            line_coverage={1: True, 2: True, 3: False, 4: True},
            branches=0,
            branches_covered=0,
            statements=4,
            statements_covered=3,
            functions=0,
            functions_covered=0,
            lines=4,
            lines_covered=3,
        )

        covered, uncovered, percentage = (
            CoverageAnalyzer.calculate_coverage_for_lines(
                coverage_data, [1, 2, 3]
            )
        )

        assert covered == 2
        assert 3 in uncovered
        assert percentage == 67

    def test_zero_coverage(self) -> None:
        """Test zero coverage case."""
        from coverage_analyzer import CoverageAnalyzer, CoverageData

        coverage_data = CoverageData(
            file="test.py",
            line_coverage={},
            branches=0,
            branches_covered=0,
            statements=0,
            statements_covered=0,
            functions=0,
            functions_covered=0,
            lines=0,
            lines_covered=0,
        )

        _, _, percentage = (
            CoverageAnalyzer.calculate_coverage_for_lines(coverage_data, [])
        )

        assert percentage == 0
