"""Rule engine for custom code review rules."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class Rule:
    """Represents a review rule."""
    id: str
    name: str
    description: str
    pattern: str
    severity: str
    languages: List[str]
    conditions: Optional[Dict[str, str]] = None
    enabled: bool = True
    fixable: bool = False


@dataclass
class RuleViolation:
    """Represents a rule violation."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    file: str
    line: int
    column: Optional[int] = None
    suggestion: Optional[str] = None


class RuleEngine:
    """Engine for processing review rules."""

    def __init__(self, config_path: str) -> None:
        """Initialize rule engine.
        
        Args:
            config_path: Path to review rules YAML config
        """
        self.rules: Dict[str, Rule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self.load_rules(config_path)

    def load_rules(self, config_path: str) -> None:
        """Load rules from YAML configuration.
        
        Args:
            config_path: Path to review rules YAML config
        """
        try:
            if not Path(config_path).exists():
                print(f"Rule configuration not found at {config_path}")
                return

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if config and "rules" in config:
                for rule_config in config["rules"]:
                    rule = Rule(
                        id=rule_config["id"],
                        name=rule_config["name"],
                        description=rule_config["description"],
                        pattern=rule_config["pattern"],
                        severity=rule_config["severity"],
                        languages=rule_config.get("languages", []),
                        conditions=rule_config.get("conditions"),
                        enabled=rule_config.get("enabled", True),
                        fixable=rule_config.get("fixable", False),
                    )
                    self.rules[rule.id] = rule

            if config and "rule_groups" in config:
                self.rule_groups = config["rule_groups"]

            print(f"Loaded {len(self.rules)} rules")

        except Exception as e:
            print(f"Error loading rules from {config_path}: {e}")

    def analyze_code(
        self, code: str, language: str, filename: str = ""
    ) -> List[RuleViolation]:
        """Analyze code against rules.
        
        Args:
            code: Code to analyze
            language: Programming language
            filename: Source filename
            
        Returns:
            List of RuleViolation objects
        """
        violations = []

        for rule in self.rules.values():
            if not rule.enabled or language not in rule.languages:
                continue

            try:
                regex = re.compile(rule.pattern, re.MULTILINE)

                for match in regex.finditer(code):
                    line_number = code[: match.start()].count("\n") + 1

                    # Check additional conditions
                    if rule.conditions:
                        # TODO: Implement condition checking
                        pass

                    violation = RuleViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.description,
                        file=filename,
                        line=line_number,
                        column=match.start() - code.rfind("\n", 0, match.start()) - 1,
                    )
                    violations.append(violation)

            except Exception as e:
                print(f"Error applying rule {rule.id}: {e}")

        return violations

    def analyze_file_content(
        self, file_content: str, file_path: str
    ) -> List[RuleViolation]:
        """Analyze file content against rules.
        
        Args:
            file_content: Content of file
            file_path: Path to file
            
        Returns:
            List of RuleViolation objects
        """
        language = self._detect_language(file_path)
        return self.analyze_code(file_content, language, file_path)

    @staticmethod
    def _detect_language(filename: str) -> str:
        """Detect programming language from filename.
        
        Args:
            filename: File path/name
            
        Returns:
            Programming language string
        """
        extension_map = {
            ".java": "java",
            ".py": "python",
            ".ts": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".cs": "csharp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        ext = Path(filename).suffix.lower()
        return extension_map.get(ext, "unknown")

    def get_aggregated_violations(
        self, violations: List[RuleViolation]
    ) -> Dict:
        """Aggregate violations by file and severity.
        
        Args:
            violations: List of violations
            
        Returns:
            Dictionary with aggregated violations
        """
        by_file = {}
        by_severity = {}

        for violation in violations:
            if violation.file not in by_file:
                by_file[violation.file] = []
            by_file[violation.file].append(violation)

            if violation.severity not in by_severity:
                by_severity[violation.severity] = []
            by_severity[violation.severity].append(violation)

        return {
            "by_file": by_file,
            "by_severity": by_severity,
            "count": len(violations),
        }

    def get_rules_by_group(self, group_name: str) -> List[Rule]:
        """Get rules in a group.
        
        Args:
            group_name: Rule group name
            
        Returns:
            List of Rule objects
        """
        rule_ids = self.rule_groups.get(group_name, [])
        return [self.rules[rid] for rid in rule_ids if rid in self.rules]

    def get_all_rules(self) -> List[Rule]:
        """Get all rules.
        
        Returns:
            List of all Rule objects
        """
        return list(self.rules.values())

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get specific rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule object or None
        """
        return self.rules.get(rule_id)
