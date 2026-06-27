---
name: codeReview
title: Generic PR Review Agent
description: Reusable AI code review agent for GitHub Copilot that can review Spring Boot services or any other pull request with custom rules and service-specific context
provider: github
version: 1.1.0
availability: public
---

# Generic PR Review Agent

A reusable code review agent integrated with GitHub Copilot that can review Spring Boot services or other backend services by adapting to repository-specific focus, context, and standards.

## Capabilities

### 🔍 Code Analysis
- **PR Change Detection**: Identifies and analyzes only changed code
- **Custom Rules**: Enforces organization-specific coding standards
- **Pattern Matching**: Detects security issues, best practices violations
- **Language Support**: Java, Python, TypeScript, JavaScript, C#, Go, and more

### 📊 Metrics & Coverage
- **Code Coverage Analysis**: Tracks test coverage for changed lines
- **Coverage Impact**: Shows covered vs uncovered changes
- **Quality Metrics**: Coverage trends and thresholds

### 🛡️ Security & Quality
- **SonarQube Integration**: Runs static analysis and quality gates
- **Vulnerability Detection**: Identifies security issues
- **Code Smells**: Detects maintainability issues

### 🤖 LLM-Based Review
- **AI Analysis**: GPT-4 or Claude powered code review
- **Standards Verification**: Checks adherence to coding standards
- **Suggestions**: Provides refactoring and improvement suggestions

## Usage Examples

```
@codeReview analyze PR #123 for security issues

@codeReview what's the coverage impact of the recent changes?

@codeReview list all critical violations in this pull request

@codeReview suggest refactoring for this code snippet

@codeReview show code quality metrics

@codeReview check for performance issues in the changed code

@codeReview review against our coding standards
```

## Features

### Automatic PR Reviews
The agent automatically reviews pull requests when enabled:
- Analyzes changed code only
- Runs custom rule validation
- Checks code coverage
- Performs SonarQube analysis
- Generates LLM-based review
- Posts comprehensive feedback as PR comments

### Interactive Queries
Ask questions about:
- Recent PR findings
- Code quality metrics
- Coverage reports
- Specific security concerns
- Refactoring suggestions
- Coding standard compliance

## Output

### PR Comment Review
```
🤖 AI Code Review Analysis

📊 Code Coverage
- Coverage: 85%
- Lines covered: 38 of 45 changed lines

📋 Custom Rule Violations
- [CRITICAL] Hardcoded credentials detected
- [MEDIUM] Function exceeds complexity threshold

🔍 Code Quality Issues
- Missing error handling in exception path
- Potential SQL injection risk detected

💡 Recommendations
- Extract database password to environment variable
- Add null-safety checks before operations

✅ Summary
- Files analyzed: 5
- Issues found: 12
- Blockers: 1
```

## Configuration

The agent is configured via:
- `.github/copilot-instructions.md` - Integration guide
- `config/review-rules.yaml` - Custom rules
- `config/sonarqube-config.yml` - SonarQube settings
- `config/llm-config.yaml` - LLM configuration
- `.github/workflows/code-review.yml` - GitHub Actions workflow

## Privacy & Security

- Only analyzes code from pull requests
- Respects repository access controls
- Does not store sensitive information
- LLM data handled per API provider's policy
- Complies with organizational security policies

## Supported Languages

- Java
- Python
- TypeScript / JavaScript
- C#
- Go
- Ruby
- PHP
- Swift
- Kotlin

## Related Documentation

- [Setup Guide](.github/copilot-instructions.md)
- [Configuration](config/review-rules.yaml)
- [GitHub Actions Workflow](.github/workflows/code-review.yml)

## Support

For issues or questions:
- Check [README.md](README.md) for setup instructions
- Review configuration files for examples
- Check GitHub Actions logs for workflow errors
