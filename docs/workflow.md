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

### Development Branch Workflow - Updated June 21, 2025

#### **Daily Development Workflow - Enhanced**

##### **Development Environment Setup**
```bash
cd "/Users/dssstrkl/Documents/Projects/oneill terrain generator"

# Create feature branch for new development
git checkout -b feature/modular-geometry-nodes

# Development files are in src/dev/
# Stable files remain in src/
```

##### **Development File Structure**
```
oneill terrain generator/
├── src/
│   ├── oneill_heightmap_terrain.py          # ← STABLE VERSION (production)
│   └── dev/
│       └── oneill_heightmap_terrain_dev.py  # ← DEVELOPMENT VERSION (testing)
├── .gitignore                               # ← Updated for dev files
└── [rest of project]
```

##### **Development Version Features**
- **Clear Identification**: Add-on name shows "[DEV]" suffix
- **Visual Warnings**: Red alert box in UI showing development status
- **Console Logging**: Enhanced registration messages with file path info
- **Debug Information**: UI shows version, branch, and asset system status

##### **Making Changes - Enhanced Workflow**
```bash
# 1. Work in development version
# Edit: src/dev/oneill_heightmap_terrain_dev.py

# 2. Test in Blender
# Install from: /Users/dssstrkl/Documents/Projects/oneill terrain generator/src/dev/oneill_heightmap_terrain_dev.py

# 3. Commit development changes
git add src/dev/oneill_heightmap_terrain_dev.py
git commit -m "dev: test unified heightmap system"

# 4. When stable, promote to main version
cp src/dev/oneill_heightmap_terrain_dev.py src/oneill_heightmap_terrain.py
git add src/oneill_heightmap_terrain.py
git commit -m "feat: v2.1 - unified heightmap system"

# 5. Push and merge
git push origin feature/modular-geometry-nodes
```

#### **Version Control Best Practices - Updated**

##### **Branch Strategy**
- **main**: Stable, production-ready versions only
- **feature/[name]**: Development branches for new features
- **src/dev/**: Development files that can be safely modified

##### **File Safety Rules**
- ✅ **Safe to modify**: `src/dev/oneill_heightmap_terrain_dev.py`
- ⚠️ **Careful with**: `src/oneill_heightmap_terrain.py` (stable version)
- ✅ **Test with**: Any .blend files in examples/

##### **Development Indicators**
When working with development version, you'll see:
- **Blender Add-on Name**: "O'Neill Cylinder Heightmap Terrain [DEV]"
- **UI Warning**: Red alert box showing "🚧 DEVELOPMENT VERSION v2.0"
- **Console Messages**: "🚧 This is a DEVELOPMENT version for testing"
- **Debug Info**: Version, branch, and asset system status in UI

##### **Testing Workflow**
```bash
# Always test development version first
1. Install src/dev/oneill_heightmap_terrain_dev.py in Blender
2. Verify red development warning appears in UI
3. Test new features thoroughly
4. Commit development changes with "dev:" prefix
5. Only promote to stable when thoroughly tested
```

#### **Safety Features**
- **Visual Separation**: Impossible to confuse dev vs stable versions
- **Console Warnings**: Clear development status during registration
- **File Structure**: Clean separation prevents accidental overwrites
- **Git Workflow**: Feature branches protect main branch stability

This enhanced workflow ensures safe development while maintaining a stable production version.