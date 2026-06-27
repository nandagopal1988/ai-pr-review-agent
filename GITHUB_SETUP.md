# GitHub setup for the PR review agent

## 1. Repository secrets
Add these in GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `GITHUB_TOKEN` is provided automatically by GitHub Actions and does not need to be added manually

## 2. Repository variables
Add these in GitHub -> Settings -> Secrets and variables -> Actions -> Variables:
- `SERVICE_NAME` (example: `billing-service`)
- `REVIEW_FOCUS` (example: `spring boot service`)
- `REVIEW_CONTEXT` (example: `Focus on API contracts and transaction boundaries`)
- `REVIEW_STANDARDS` (optional)

## 3. Enable workflows
- Ensure Actions are enabled for the repository.
- Push the workflow file to GitHub.
- Open a pull request to trigger the workflow.

## 4. Copilot agent discovery
- Keep [.agent.md](.agent.md) or [.copilot/codeReviewAgent.md](.copilot/codeReviewAgent.md) in the repository.
- Make sure the repository is accessible to the GitHub account using Copilot.
- Open GitHub Copilot and check the agent picker after the repository is recognized.
