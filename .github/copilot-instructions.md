# AI Code Review Agent - GitHub Copilot Integration

## Project Overview
This is a GitHub Copilot-integrated AI code review agent that can be reused across repositories and services. It automatically reviews pull requests with:
- **PR Change Analysis**: Analyzes only modified code in pull requests
- **Code Coverage Tracking**: Monitors test coverage of changed lines
- **SonarQube Integration**: Runs SonarQube static analysis
- **Custom Rule Engine**: YAML-based customizable review rules
- **LLM Code Review**: GPT/Claude-based coding standard verification
- **Generic Service Context**: Supports Spring Boot services and other backend services via environment variables
- **GitHub Copilot Agent**: Available as a custom agent in GitHub Copilot chat

## Setup Progress
- [x] Create project structure
- [x] Set up configuration files
- [ ] Create GitHub Actions workflows
- [ ] Implement agent logic
- [ ] Configure LLM integration
- [ ] Deploy to GitHub

## Key Files
- `.github/workflows/code-review.yml` - Main PR review workflow
- `config/review-rules.yaml` - Custom review rules
- `config/sonarqube-config.yml` - SonarQube settings
- `src/agents/codeReviewAgent.ts` - Copilot agent implementation
- `.copilot/codeReviewAgent.md` - Agent manifest for GitHub Copilot

## Quick Start
1. Configure GitHub secrets for LLM API keys
2. Set repository variables such as `REVIEW_FOCUS`, `SERVICE_NAME`, and `REVIEW_CONTEXT` to tailor the review to your service
3. Update `config/review-rules.yaml` with custom rules
4. Push to trigger automatic PR reviews
5. Use agent with: `@codeReview` in GitHub Copilot chat
