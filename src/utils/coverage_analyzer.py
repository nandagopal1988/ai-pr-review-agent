"""Code coverage analyzer."""

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CoverageData:
    """Coverage data for a file."""
    file: str
    line_coverage: Dict[int, bool]
    branches: int
    branches_covered: int
    statements: int
    statements_covered: int
    functions: int
    functions_covered: int
    lines: int
    lines_covered: int


@dataclass
class CoverageSummary:
    """Summary of coverage analysis."""
    overall: int
    new_code: int
    modified_code: int
    uncovered_lines: List[int]
    files: List[CoverageData]


class CoverageAnalyzer:
    """Analyzes code coverage."""

    async def get_coverage_report(self, report_path: str) -> Dict[str, CoverageData]:
        """Load coverage report from LCOV format.
        
        Args:
            report_path: Path to lcov.info file
            
        Returns:
            Dictionary mapping filename to CoverageData
        """
        coverage_map = {}

        if not os.path.exists(report_path):
            print(f"Coverage report not found at {report_path}")
            return coverage_map

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            current_file = ""
            file_data = {}

            for line in lines:
                line = line.strip()

                if line.startswith("SF:"):
                    current_file = line[3:]
                    if current_file not in file_data:
                        file_data[current_file] = {
                            "file": current_file,
                            "line_coverage": {},
                            "branches": 0,
                            "branches_covered": 0,
                            "statements": 0,
                            "statements_covered": 0,
                            "functions": 0,
                            "functions_covered": 0,
                            "lines": 0,
                            "lines_covered": 0,
                        }

                elif line.startswith("DA:") and current_file:
                    parts = line[3:].split(",")
                    line_num = int(parts[0])
                    count = int(parts[1])
                    file_data[current_file]["line_coverage"][line_num] = count > 0
                    file_data[current_file]["lines"] += 1
                    if count > 0:
                        file_data[current_file]["lines_covered"] += 1

                elif line.startswith("LH:") and current_file:
                    file_data[current_file]["lines_covered"] = int(line[3:])

                elif line.startswith("LF:") and current_file:
                    file_data[current_file]["lines"] = int(line[3:])

                elif line.startswith("BRH:") and current_file:
                    file_data[current_file]["branches_covered"] = int(line[4:])

                elif line.startswith("BRF:") and current_file:
                    file_data[current_file]["branches"] = int(line[4:])

            for file, data in file_data.items():
                coverage_map[file] = CoverageData(**data)

        except Exception as e:
            print(f"Error parsing coverage report: {e}")

        return coverage_map

    @staticmethod
    def calculate_coverage_for_lines(
        coverage_data: CoverageData, target_lines: List[int]
    ) -> Tuple[int, List[int], int]:
        """Calculate coverage percentage for specific lines.
        
        Args:
            coverage_data: Coverage data for file
            target_lines: List of line numbers to check
            
        Returns:
            Tuple of (covered_count, uncovered_lines, percentage)
        """
        uncovered = []
        covered = 0

        for line_num in target_lines:
            if line_num in coverage_data.line_coverage:
                if coverage_data.line_coverage[line_num]:
                    covered += 1
                else:
                    uncovered.append(line_num)
            else:
                uncovered.append(line_num)

        percentage = (
            round((covered / len(target_lines)) * 100) if target_lines else 0
        )

        return covered, uncovered, percentage

    async def analyze_pr_coverage(
        self, report_path: str, changed_files: Dict[str, List[int]]
    ) -> CoverageSummary:
        """Analyze coverage for PR changes.
        
        Args:
            report_path: Path to coverage report
            changed_files: Dictionary mapping filename to changed line numbers
            
        Returns:
            CoverageSummary with analysis results
        """
        coverage_map = await self.get_coverage_report(report_path)
        files = []
        total_covered = 0
        total_lines = 0
        all_uncovered = []

        for filename, changed_lines in changed_files.items():
            if filename in coverage_map:
                coverage = coverage_map[filename]
                covered, uncovered, _ = self.calculate_coverage_for_lines(
                    coverage, changed_lines
                )
                total_covered += covered
                total_lines += len(changed_lines)
                all_uncovered.extend(uncovered)
                files.append(coverage)

        overall = self._calculate_overall_coverage(coverage_map)
        new_code_coverage = (
            round((total_covered / total_lines) * 100) if total_lines > 0 else 0
        )

        return CoverageSummary(
            overall=overall,
            new_code=new_code_coverage,
            modified_code=new_code_coverage,
            uncovered_lines=all_uncovered,
            files=files,
        )

    @staticmethod
    def _calculate_overall_coverage(
        coverage_map: Dict[str, CoverageData]
    ) -> int:
        """Calculate overall coverage percentage.
        
        Args:
            coverage_map: Coverage data for all files
            
        Returns:
            Overall coverage percentage
        """
        total_lines = 0
        total_covered = 0

        for coverage in coverage_map.values():
            total_lines += coverage.lines
            total_covered += coverage.lines_covered

        return round((total_covered / total_lines) * 100) if total_lines > 0 else 0
