# Contributing Guide

Thank you for considering contributing to the Multi-Agent Workflow Cost Tracing project!

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if it's already reported in [Issues](https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench/issues)
2. If not, create a new issue with:
   - Clear description of the problem/feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/imrohankataria/agentic-multi-llm-orchestration-bench.git
   cd agentic-multi-llm-orchestration-bench
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add docstrings to functions
   - Update documentation if needed

5. **Test your changes**
   ```bash
   # Run the demo to verify core functionality
   python examples/demo_mock_data.py
   
   # If you have API keys, test the examples
   python examples/langgraph_example.py
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to GitHub and create a PR
   - Describe what you changed and why
   - Reference any related issues

## Development Guidelines

### Code Style

- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add type hints where appropriate
- Write docstrings for public functions

Example:
```python
def track_llm_call(
    self,
    agent_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Track an LLM API call with token usage and cost
    
    Args:
        agent_name: Name of the agent making the call
        model: Model identifier (e.g., "gpt-4o-mini")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        duration_ms: Call duration in milliseconds
        metadata: Optional additional information
    """
```

### Adding New Features

#### New Framework Integration

To add support for a new framework (e.g., AutoGen):

1. Create `src/agents/autogen_agents.py`
2. Implement cost tracking hooks
3. Create example in `examples/autogen_example.py`
4. Update README with new framework info

#### New Visualization Type

To add a new visualization:

1. Add method to `CostVisualizer` class in `src/visualizations/charts.py`
2. Use Plotly for interactive charts
3. Save as HTML file
4. Add example to demo script

#### New LLM Provider

To add pricing for a new provider:

1. Update `LLM_PRICING` dict in `src/cost_tracker/core.py`
2. Add model identifiers and pricing
3. Update documentation

Example:
```python
LLM_PRICING["new-provider-model"] = {
    "input": 0.001,   # $ per 1K tokens
    "output": 0.002
}
```

## Testing

Currently, the project focuses on integration examples rather than unit tests.

To test your changes:

1. **Run the demo**:
   ```bash
   python examples/demo_mock_data.py
   ```
   Should complete without errors and generate visualizations.

2. **Test with real LLMs** (if you have API keys):
   ```bash
   export OPENAI_API_KEY='your-key'
   python examples/langgraph_example.py
   ```

3. **Manual verification**:
   - Check that HTML visualizations display correctly
   - Verify cost calculations are accurate
   - Ensure spike detection works as expected

### Future: Adding Tests

We welcome contributions to add proper testing:

- Unit tests for `CostTracker` class
- Integration tests for framework integrations
- Visualization rendering tests
- Mock API response tests

## Documentation

When adding features, update:

1. **README.md** - Main project description and quick start
2. **USAGE.md** - Detailed usage examples
3. **INSTALL.md** - Installation instructions (if dependencies change)
4. **Docstrings** - In-code documentation

## Areas for Contribution

Looking for ways to contribute? Here are some ideas:

### High Priority

- [ ] Add support for more LLM providers (Anthropic, Cohere, etc.)
- [ ] Add support for AutoGen framework
- [ ] Create unit test suite
- [ ] Add real-time cost monitoring dashboard
- [ ] Implement cost budgets and alerts

### Medium Priority

- [ ] Add more visualization types (scatter plots, heatmaps)
- [ ] Export to more formats (PDF, CSV)
- [ ] Historical cost tracking and trends
- [ ] Cost optimization recommendations
- [ ] Token-level analysis and breakdown

### Nice to Have

- [ ] Web-based dashboard (Flask/FastAPI)
- [ ] CI/CD pipeline
- [ ] Docker container
- [ ] Cloud deployment examples
- [ ] Integration with observability tools

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent issues
- Check existing issues and PRs first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
