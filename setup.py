from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pr-review-agent",
    version="1.0.0",
    author="Your Team",
    author_email="your.email@example.com",
    description="AI-powered code review agent with GitHub Copilot integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nandagopal1988/ai-pr-review-agent",

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    python_requires=">=3.9",

    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "PyGithub>=2.1.1",
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "python-dotenv>=1.0.0",
    ],

    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },

    entry_points={
        "console_scripts": [
            "ai-pr-review=ai_pr_review.cli:main",
        ],
    },
)