# GitHub Copilot agent setup for sng-product-service

## 1. Copy these files into the target repository
- `.agent.md`
- `.github/workflows/code-review.yml`

## 2. Configure repository variables
In GitHub -> Settings -> Secrets and variables -> Actions -> Variables, add:
- `SERVICE_NAME=sng-product-service`
- `REVIEW_FOCUS=spring boot service`
- `REVIEW_CONTEXT=Focus on API contracts, transaction boundaries, and service reliability.`
- `REVIEW_STANDARDS` (optional)

## 3. Add secrets
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` if you later connect the agent to an LLM-backed review step

## 4. Push and test
- Commit and push the files
- Open a pull request
- Check the Actions tab and the PR comment

## 5. Copilot availability
- Keep `.agent.md` in the repository root so GitHub Copilot can discover the agent
- Make sure the repository is accessible to the GitHub account using Copilot
