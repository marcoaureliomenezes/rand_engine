
## Release Process

To create a new release, simply create and push a git tag with semantic versioning:



```bash
git tag 0.4.1 && git push origin --tags
```

The GitHub Actions workflow will automatically:
- Build and test the package
- Publish to PyPI
- Create a GitHub Release
- Update the Homebrew formula (if configured)