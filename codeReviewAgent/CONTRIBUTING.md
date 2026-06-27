# Contributing

We welcome contributions to the Code Review Agent! Please follow these guidelines:

## Setup

```bash
npm install
npm run build
npm run test
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and add tests
3. Run linting: `npm run lint`
4. Format code: `npm run format`
5. Run tests: `npm run test`
6. Commit with descriptive messages
7. Push and create a Pull Request

## Code Style

- Use TypeScript for all source code
- Follow existing code patterns
- Add JSDoc comments for public APIs
- Write tests for new features

## Testing

- Add unit tests in `src/__tests__/`
- Aim for >70% code coverage
- Test both happy paths and error cases

## Pull Requests

- Reference related issues
- Describe changes and rationale
- Ensure all checks pass
- Request review from maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
