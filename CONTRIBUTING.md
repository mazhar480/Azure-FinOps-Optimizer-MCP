# Contributing to Azure FinOps Elite

Thank you for your interest in contributing to Azure FinOps Elite! 🎉

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/YOUR_USERNAME/azure-finops-elite/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, Azure SDK versions)
   - Relevant logs or screenshots

### Suggesting Features

1. Check [Issues](https://github.com/YOUR_USERNAME/azure-finops-elite/issues) for existing feature requests
2. Create a new issue with:
   - Clear use case description
   - Expected behavior
   - Why this would be valuable
   - Any implementation ideas

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new features
   - Update documentation
4. **Test your changes**:
   ```bash
   pytest
   black .
   isort .
   mypy .
   ```
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add: Brief description of changes"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable

## 📝 Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use `black` and `isort`
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain "why", not "what"

### Example:

```python
def calculate_savings(
    current_cost: float,
    optimized_cost: float,
    period: str = "monthly"
) -> Dict[str, float]:
    """
    Calculate cost savings from optimization.
    
    Args:
        current_cost: Current monthly cost in USD
        optimized_cost: Optimized monthly cost in USD
        period: Reporting period ("monthly" or "annual")
    
    Returns:
        Dictionary with savings metrics
    """
    multiplier = 12 if period == "annual" else 1
    savings = (current_cost - optimized_cost) * multiplier
    
    return {
        "savings": savings,
        "percentage": (savings / current_cost) * 100 if current_cost > 0 else 0
    }
```

## 🧪 Testing

- Write tests for all new features
- Ensure existing tests pass
- Aim for >80% code coverage

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📚 Documentation

- Update README.md for user-facing changes
- Update relevant guides (WINDOWS_TESTING.md, WEB_DASHBOARD.md, etc.)
- Add docstrings to all functions and classes
- Include examples in docstrings

## 🔐 Security

- Never commit credentials or secrets
- Use environment variables for configuration
- Follow least-privilege principles
- Report security vulnerabilities privately to: security@example.com

## 🏷️ Commit Message Guidelines

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: Add multi-region cost comparison tool

- Implement region-based pricing lookup
- Add comparison report generator
- Update web dashboard with new tab
```

## 🎯 Development Priorities

Current focus areas:

1. **Performance**: Optimize API calls and caching
2. **Testing**: Increase test coverage
3. **Documentation**: Improve guides and examples
4. **Features**: See [Issues](https://github.com/YOUR_USERNAME/azure-finops-elite/issues) for planned features

## 💰 Financial Contributions

If you can't contribute code but want to support the project:

- [GitHub Sponsors](https://github.com/sponsors/YOUR_USERNAME)
- Star the repository ⭐
- Share with others who might benefit

## 📞 Questions?

- Open a [Discussion](https://github.com/YOUR_USERNAME/azure-finops-elite/discussions)
- Comment on relevant issues
- Check existing documentation

## 🙏 Thank You!

Every contribution, no matter how small, is appreciated! Together we're building better FinOps tools for everyone.

---

**Happy Contributing! 🚀**
