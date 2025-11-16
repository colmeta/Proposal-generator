# Contributing Guide

Thank you for your interest in contributing to the Proposal Generator! This guide will help you get started.

## How to Contribute

### Reporting Bugs

1. **Check Existing Issues**: Search existing issues to avoid duplicates
2. **Create Issue**: Use the bug report template
3. **Provide Details**:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error messages/logs
   - Screenshots (if applicable)

### Suggesting Features

1. **Check Existing Issues**: Search for similar feature requests
2. **Create Issue**: Use the feature request template
3. **Provide Details**:
   - Description of the feature
   - Use cases
   - Benefits
   - Implementation ideas (optional)

### Code Contributions

1. **Fork Repository**: Fork the repository on GitHub
2. **Create Branch**: Create a feature branch
3. **Make Changes**: Implement your changes
4. **Test**: Ensure all tests pass
5. **Document**: Update documentation if needed
6. **Submit PR**: Create a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Git
- Virtual environment (recommended)

### Setup Steps

1. **Clone Repository**:
```bash
git clone https://github.com/your-repo/proposal-generator.git
cd proposal-generator
```

2. **Create Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Setup Database**:
```bash
createdb proposal_generator_test
alembic upgrade head
```

5. **Run Tests**:
```bash
pytest
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **Imports**: Use absolute imports
- **Docstrings**: Use Google style docstrings

### Formatting

We use `black` for code formatting:

```bash
black .
```

### Linting

We use `flake8` for linting:

```bash
flake8 .
```

### Type Hints

Use type hints for function signatures:

```python
def process_proposal(proposal_id: str) -> Dict[str, Any]:
    """Process a proposal."""
    pass
```

## Testing

### Writing Tests

- Write tests for all new features
- Write tests for bug fixes
- Aim for high test coverage
- Use descriptive test names

### Test Structure

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

## Documentation

### Code Documentation

- Document all public functions and classes
- Use Google style docstrings
- Include parameter descriptions
- Include return value descriptions
- Include example usage when helpful

### User Documentation

- Update user guides for new features
- Add examples and screenshots
- Keep documentation current
- Fix documentation errors

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error responses
- Keep API docs in sync with code

## Pull Request Process

### Before Submitting

1. **Update Tests**: Add tests for new features
2. **Update Documentation**: Update relevant docs
3. **Run Tests**: Ensure all tests pass
4. **Check Style**: Run formatter and linter
5. **Update Changelog**: Add entry to CHANGELOG.md

### PR Description

Include:
- Description of changes
- Related issues
- Testing performed
- Screenshots (if UI changes)
- Breaking changes (if any)

### Review Process

1. **Automated Checks**: CI/CD runs tests and checks
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR is merged

## Project Structure

```
proposal-generator/
├── api/              # API endpoints
├── agents/           # AI agents
├── core/             # Core functionality
├── database/         # Database models and migrations
├── docs/             # Documentation
├── tests/            # Tests
├── utils/            # Utilities
└── web/              # Web interface
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add proposal version comparison feature

- Add version comparison UI component
- Implement diff algorithm
- Add tests for version comparison
- Update documentation

Fixes #123
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information

## Getting Help

### Questions?

- Check documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

### Need Help?

- Open an issue with "question" label
- Ask in GitHub Discussions
- Contact maintainers directly

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Thank you for contributing to the Proposal Generator! Your contributions make this project better for everyone.

