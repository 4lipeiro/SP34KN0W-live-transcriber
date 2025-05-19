# Contributing Guidelines

Thank you for your interest in contributing to SP34KN0W Live Transcriber! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive of all contributors
- Provide constructive feedback and support
- Focus on what is best for the community
- Show empathy towards other community members

## How Can You Contribute?

There are many ways to contribute to SP34KN0W:

1. **Code Contributions**: Implement new features or fix bugs
2. **Documentation**: Improve or expand the documentation
3. **Testing**: Test the application and report issues
4. **Design**: Suggest UI/UX improvements
5. **Translation**: Help translate the application or documentation
6. **Bug Reports**: Submit detailed bug reports
7. **Feature Requests**: Suggest new features or improvements

## Getting Started

### Setting Up a Development Environment

1. **Fork the Repository**:
   - Click the "Fork" button on the GitHub repository page

2. **Clone Your Fork**:
   ```powershell
   git clone https://github.com/4lipeiro/SP34KN0W-live-transcriber.git
   cd SP34KN0W-live-transcriber
   ```

3. **Set Up the Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```

4. **Set Up Development Tools**:
   ```powershell
   pip install black pytest pytest-asyncio pylint
   ```

5. **Create a New Branch**:
   ```powershell
   git checkout -b feature/your-feature-name
   ```

## Development Process

### Coding Standards

SP34KN0W follows these standards:

1. **PEP 8**: Follow Python's PEP 8 style guide
2. **Docstrings**: Use descriptive docstrings for all functions and classes
3. **Type Hints**: Include type hints where appropriate
4. **Comments**: Add comments for complex logic
5. **Naming**:
   - Use `snake_case` for functions and variables
   - Use `CamelCase` for classes
   - Use `UPPER_CASE` for constants

### Pull Request Process

1. **Make Your Changes**: Implement your feature or fix
2. **Test Thoroughly**: Test your changes for all edge cases
3. **Format Your Code**: Run `black` on your changes
4. **Update Documentation**: Update relevant documentation
5. **Commit Your Changes**:
   ```powershell
   git add .
   git commit -m "Add feature: brief description"
   ```
6. **Push to Your Fork**:
   ```powershell
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select "compare across forks"
   - Select your fork and branch
   - Provide a clear description of your changes
   - Submit the pull request

### Pull Request Guidelines

When creating a pull request:

1. **Be Clear**: Clearly describe what your changes do
2. **Be Specific**: List specific changes and their purpose
3. **Reference Issues**: Link any related issues
4. **Include Tests**: Add tests for new functionality
5. **Update Documentation**: Ensure documentation reflects your changes
6. **Keep It Focused**: Address one feature or issue per PR

## Reporting Issues

### Bug Reports

When reporting a bug, please include:

1. **Clear Title**: Brief description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment Information**:
   - OS and version
   - Python version
   - Package versions
   - Hardware details (microphone, etc.)
6. **Screenshots/Logs**: If applicable
7. **Possible Solution**: If you have suggestions

### Feature Requests

When suggesting a feature:

1. **Clear Title**: Brief description of the feature
2. **Detailed Description**: What the feature should do
3. **Use Case**: Why this feature would be valuable
4. **Alternatives**: Other ways to achieve the same goal
5. **Additional Context**: Any other information

## Documentation Contributions

Documentation is crucial to the project. To contribute:

1. **Identify Areas for Improvement**: Find documentation that needs updating
2. **Make Your Changes**: Update or add documentation
3. **Submit a Pull Request**: Follow the same process as code contributions

## Testing

When contributing code:

1. **Add Tests**: Include tests for new functionality
2. **Run Existing Tests**: Ensure all tests pass with your changes
3. **Test Edge Cases**: Consider and test boundary conditions

## Review Process

After submitting a contribution:

1. **Initial Review**: Maintainers will review your submission
2. **Feedback**: You may receive feedback or requests for changes
3. **Revision**: Make any necessary revisions
4. **Approval and Merge**: Once approved, your contribution will be merged

## Recognition

All contributors will be acknowledged in the project. Significant contributors may be invited to join as maintainers.

## Questions?

If you have questions about contributing:

1. **Check Existing Issues**: Search for similar questions
2. **Create a Discussion**: Use GitHub Discussions for general questions
3. **Contact Maintainers**: Reach out directly for specific concerns

Thank you for contributing to SP34KN0W Live Transcriber!
