from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic-multi-llm-orchestration-bench",
    version="0.1.0",
    author="Rohan Kataria",
    description="Cost tracking and benchmarking for multi-agent AI workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "crewai": [
            "crewai>=0.1.0",
            "langchain>=0.1.0",
            "langchain-openai>=0.0.5",
        ],
        "langgraph": [
            "langgraph>=0.0.30",
            "langchain>=0.1.0",
            "langchain-openai>=0.0.5",
        ],
        "all": [
            "crewai>=0.1.0",
            "langgraph>=0.0.30",
            "langchain>=0.1.0",
            "langchain-openai>=0.0.5",
            "langchain-community>=0.0.20",
            "tiktoken>=0.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
)
