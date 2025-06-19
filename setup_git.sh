#!/bin/bash

# O'Neill Terrain Generator - Git Setup Script
echo "Setting up git for O'Neill Terrain Generator..."

# Navigate to project directory
cd "$(dirname "$0")"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
else
    echo "Git repository already exists"
fi

# Set up remote origin
echo "Adding remote origin..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/dssstrkl/oneill-terrain-generator.git

# Configure git user (replace with your info)
echo "Configuring git user..."
git config user.name "dssstrkl"
git config user.email "paul@dssstrkl.com"  # Replace with your actual email

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Blender files
*.blend1
*.blend2
*.blend3
__pycache__/
*.pyc
*.pyo

# OS files
.DS_Store
Thumbs.db
*.swp
*.swo

# IDE files
.vscode/
.idea/
*.sublime-*

# Logs
*.log

# Documentation builds
docs/_build/
EOF
fi

# Stage all files
echo "Staging files..."
git add .

# Check if we have any commits
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "Repository has existing commits"
else
    echo "Making initial commit..."
    git commit -m "Initial commit: O'Neill Terrain Generator Blender Add-on

- Complete heightmap-based terrain workflow
- Cylinder alignment and unwrapping functionality  
- Heightmap generation and terrain application
- Preserves original geometry and positioning
- Ready for game development pipeline"
fi

# Set up main branch
echo "Setting up main branch..."
git branch -M main

# Push to GitHub
echo "Pushing to GitHub..."
echo "Note: You may need to authenticate with GitHub"
git push -u origin main

echo ""
echo "✅ Git setup complete!"
echo "Repository: https://github.com/dssstrkl/oneill-terrain-generator"
echo ""
echo "Next steps:"
echo "1. Replace 'your-email@example.com' in this script with your actual email"
echo "2. Run: bash setup_git.sh"
echo "3. Authenticate with GitHub when prompted"
echo ""
echo "Future workflow:"
echo "  git add ."
echo "  git commit -m 'Your commit message'"
echo "  git push"
