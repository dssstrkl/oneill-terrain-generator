# Development Workflow Guide

## Daily Development Workflow

### Making Changes
```bash
# 1. Check status
git status

# 2. Make your changes to files
# (edit code, add features, fix bugs)

# 3. Stage changes
git add .                    # Stage all changes
# OR
git add src/specific_file.py # Stage specific files

# 4. Commit with descriptive message
git commit -m "Add feature: terrain smoothing algorithm"

# 5. Push to GitHub
git push
```

### Branch-Based Development
```bash
# Create feature branch
git checkout -b feature/new-terrain-types
# Make changes...
git add .
git commit -m "Add mountain terrain type"
git push -u origin feature/new-terrain-types

# Switch back to main
git checkout main

# Merge feature (or use GitHub PR)
git merge feature/new-terrain-types
git push
```

### Common Git Commands
```bash
git status              # Check current status
git log --oneline       # View commit history
git diff                # See unstaged changes
git diff --staged       # See staged changes
git branch -a           # List all branches
git checkout main       # Switch to main branch
git pull                # Get latest changes from GitHub
```

### Release Management
```bash
# Tag a release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# List tags
git tag -l
```

## GitHub Features to Use

### Issues & Project Management
- 🐛 **Bug Reports**: Document issues and track fixes
- ✨ **Feature Requests**: Plan new functionality
- 📝 **Documentation**: Track documentation improvements
- 🏷️ **Labels**: Organize issues (bug, enhancement, documentation)

### Releases
- 📦 **GitHub Releases**: Package stable versions
- 📋 **Release Notes**: Document changes between versions
- 📁 **Assets**: Attach .py files for easy download

### GitHub Actions (Future)
- ✅ **Automated Testing**: Test add-on with different Blender versions
- 📦 **Automated Packaging**: Create release packages
- 🚀 **Deployment**: Auto-update documentation

## File Organization Best Practices

```
oneill terrain generator/
├── src/                          # Source code
│   └── oneill_heightmap_terrain.py
├── docs/                         # Documentation
│   ├── development_summary.txt
│   ├── api.md
│   └── user_guide.md
├── examples/                     # Example files
│   ├── sample_cylinders.blend
│   └── terrain_examples/
├── tests/                        # Test files
│   └── test_terrain_generation.py
├── .github/                      # GitHub configuration
│   └── workflows/
│       └── test.yml
├── README.md                     # Main documentation
├── LICENSE                       # License file
├── .gitignore                    # Git ignore patterns
└── setup_git.sh                 # Setup script
```

## Version Numbering
Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Examples:
- v1.0.0: Initial release
- v1.1.0: Add new terrain types
- v1.1.1: Fix alignment bug
- v2.0.0: Complete workflow redesign

## Backup Strategy
- ✅ **GitHub**: Primary backup and collaboration
- ✅ **Local Git**: Full history on your machine
- ✅ **Tags**: Stable version snapshots
- 📁 **Manual**: Keep .blend example files separate

## Next Development Priorities

1. **Testing**: Create test cases for each workflow step
2. **Documentation**: User guide with screenshots
3. **Examples**: Sample O'Neill cylinder .blend files
4. **Performance**: Optimize for large cylinder counts
5. **Features**: Additional terrain types and generators
