# GitHub Copilot Agent Publish Checklist

## 1. Repository readiness
- Ensure the repository is public or available to the intended GitHub Copilot audience.
- Keep the agent manifest in the repository root as `.agent.md` or in `.copilot/codeReviewAgent.md`.
- Confirm the repository contains clear metadata: name, title, description, provider, and version.

## 2. Local smoke test
- Install Python 3.9+ locally.
- Install dependencies: `pip install -r requirements.txt`
- Run: `python scripts/smoke_test.py`

## 3. GitHub configuration
- Add the LLM API key as a repository secret:
  - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Add optional repository variables for service-specific behavior:
  - `SERVICE_NAME`
  - `REVIEW_FOCUS`
  - `REVIEW_CONTEXT`
  - `REVIEW_STANDARDS`

## 4. Copilot agent visibility
- Push the repository to GitHub.
- In GitHub Copilot, open the agent picker and verify that the agent appears after the repository is recognized.
- If the agent does not appear immediately, ensure the manifest is in the expected location and the repository is accessible to your GitHub account.

## 5. First real review
- Open a pull request in the target repository.
- Invoke the agent in Copilot chat with a prompt such as:
  - `@codeReview review this PR for security and API risks`
