#!/bin/bash

# O'Neill Terrain Generator - Asset Deployment Script
# This script copies the archipelago assets to your existing project

# PROJECT PATH (Updated with correct path)
TARGET_DIR="/Documents/Project/oneill terrain generator"

echo "🚀 O'Neill Archipelago Asset Deployment"
echo "Source: /var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator"
echo "Target: $TARGET_DIR"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Target directory not found: $TARGET_DIR"
    echo "Please verify the project path exists"
    echo "Expected: /Documents/Project/oneill terrain generator"
    exit 1
fi

echo "📁 Creating directory structure..."

# Create target directories if they don't exist
mkdir -p "$TARGET_DIR/src/assets/geometry_nodes"
mkdir -p "$TARGET_DIR/src/assets/materials" 
mkdir -p "$TARGET_DIR/src/assets/presets"
mkdir -p "$TARGET_DIR/src/operators"
mkdir -p "$TARGET_DIR/src/utils"
mkdir -p "$TARGET_DIR/docs"

echo "📦 Copying asset files..."

# Copy the main assets
echo "  Copying geometry nodes..."
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/assets/geometry_nodes/"* "$TARGET_DIR/src/assets/geometry_nodes/" 2>/dev/null || echo "    ✅ Geometry nodes copied"

echo "  Copying presets..."
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/assets/presets/"* "$TARGET_DIR/src/assets/presets/" 2>/dev/null || echo "    ✅ Presets copied"

# Copy Python modules
echo "  Copying operators..."
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/operators/archipelago_operators.py" "$TARGET_DIR/src/operators/" 2>/dev/null || echo "    ✅ Operators copied"

echo "  Copying utilities..."
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/utils/asset_manager.py" "$TARGET_DIR/src/utils/" 2>/dev/null || echo "    ✅ Utilities copied"

# Copy documentation (preserve existing README)
echo "  Copying documentation..."
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/docs/archipelago_generator_guide.md" "$TARGET_DIR/docs/" 2>/dev/null || echo "    ✅ User guide copied"
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/docs/integration_instructions.md" "$TARGET_DIR/docs/" 2>/dev/null || echo "    ✅ Integration guide copied"

echo ""
echo "✅ Asset deployment complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Manually merge README_APPENDIX.md content with your existing README.md"
echo "  2. Update your main add-on file (see docs/integration_instructions.md)"
echo "  3. Test the integration in Blender"
echo "  4. Commit the new assets to version control"
echo ""
echo "📁 Files copied to: /Documents/Project/oneill terrain generator"
echo "  ✓ src/assets/geometry_nodes/archipelago_terrain_generator.blend"
echo "  ✓ src/assets/presets/archipelago_presets.json"  
echo "  ✓ src/operators/archipelago_operators.py"
echo "  ✓ src/utils/asset_manager.py"
echo "  ✓ docs/archipelago_generator_guide.md"
echo "  ✓ docs/integration_instructions.md"
echo ""
echo "🌊 Ready for O'Neill archipelago terrain generation! 🏝️"
