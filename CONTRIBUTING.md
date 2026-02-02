# Contributing to Nexora Searchengine
Thank you for considering contributing to **Nexora Searchengine**! Your help is highly appreciated.

## 📌 Before You Start
- Read this guide carefully.
- Familiarize yourself with the repository structure and contribution guidelines.


## 🎯 How to Contribute

- **Report Bugs:**  
  Open a [GitHub Issue](https://github.com/Developer012345678910/Searchengine/issues) for any bugs you find, providing as much detail as possible.

- **Suggest Enhancements:**  
  If you have an idea for improvement, please open an issue or discussion first to explain your proposal.

- **Submit Pull Requests:**  
  Feature additions, bug fixes, and documentation improvements are welcome! Read below for submission guidelines.

## 📝 Workflow

1. **Fork the repository** and create your branch from `main`.
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly.

3. **Write clear, concise commit messages** using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `style:` for code style changes
   - `refactor:` for code refactoring
   - `test:` for tests

4. **Push to your fork** and submit a Pull Request.
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Participate in code review** and make any requested changes.

## 💻 Development Setup

### Frontend Development

- **Update styling and behavior**
  • Edit files in the `CSS/` and `JS/` directories to implement new features or bug fixes.

- **Local testing**
  • Run a simple HTTP server with `python -m http.server 8000` and open `http://localhost:8000` in your browser to test changes.

- **Responsive design**
  • Verify that the UI adapts correctly on mobile, tablet, and desktop viewports. Use your webbrowser DevTools device toolbar or similar tools for testing.

### The Webcrawler (How to use it)

```bash
# Install dependencies
pip install -r webcrawler/requirements.txt

# Test the crawler
python webcrawler/webcrawler.py --start-url https://example.com --max-pages 10

# Run with your test data
python webcrawler/webcrawler.py --start-url YOUR_URL --max-pages YOUR_LIMIT --json-file test_data.json
```
# Contributions are welcome! Please submit a pull request with new crawled websites.

## 📋 Code Style Guidelines

### Frontend (JavaScript & CSS)
- Use 2 spaces for indentation
- Use meaningful variable names
- Write comments for complex logic
- Keep CSS organized and DRY (Don't Repeat Yourself)

### Backend (Not Implemented)
This project currently has no backend component. If you have ideas or suggestions for adding one, please open an issue and let us discuss how it could be integrated.


### General
- Write clear, self-documenting code
- Add comments only for "why", not "what"
- Test before submitting

## 🐛 Reporting Bugs

Please include:

- **Descriptive title:** Clearly describe the issue
- **Steps to reproduce:** Detailed steps to replicate the bug
- **Expected behavior:** What should happen
- **Actual behavior:** What actually happened
- **Screenshots/logs:** If applicable
- **Environment:** Browser, OS, Python version, etc.

**Example:**
```
Title: Search results not displaying for GitHub URLs

Steps to Reproduce:
1. Run crawler with --start-url https://github.com --max-pages 5
2. Open index.html
3. Search for "GitHub"

Expected: Search results should show GitHub pages
Actual: No results displayed, console shows error
```

## ✨ Suggesting Enhancements

- Use a descriptive title
- Explain the use case and benefits
- Provide examples if possible
- Reference any related issues

## 📚 Pull Request Process

1. **Update documentation** if you changed functionality
2. **Add tests** if applicable
3. **Ensure your code follows the style guide**
4. **Update the `crawled_data.json`** if testing with new URLs
5. **Link related issues** in your PR description
6. **Be responsive** to feedback during code review

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
Describe how you tested the changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed my own code
- [ ] Tested in multiple browsers (if frontend)
- [ ] Updated documentation
```

## 🔄 Commit Message Examples

```bash
# Feature
git commit -m "feat: add advanced search filters"

# Bug fix
git commit -m "fix: resolve search results not displaying for certain URLs"

# Documentation
git commit -m "docs: update crawler usage instructions"

# Performance
git commit -m "perf: optimize JSON data loading in main.js"
```

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE.md).

## 🙏 Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building this together!

---

**Questions?** Open an issue or start a discussion. We're here to help! 😊
