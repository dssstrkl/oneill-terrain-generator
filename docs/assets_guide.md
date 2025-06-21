# Project Assets Guide

## Working Components Available (USE THESE FIRST)

### `src/assets/geometry_nodes/`
- **Terrain displacement node groups** - Proven UV mapping and displacement logic
- **Material setups** - Working heightmap materials with proper connections
- **Preset configurations** - Tested parameter sets for different terrain types
- **Usage**: Import via File → Append → NodeGroup, don't recreate from scratch

### `src/assets/presets/`
- **Terrain generation presets** - Proven parameter combinations
- **Workflow configurations** - Tested settings for different cylinder sizes
- **Material presets** - Working shader setups for terrain visualization
- **Usage**: Reference for parameter values, don't guess optimal settings

### `src/previous/`
- **`oneill_heightmap_terrain_final.py`** - Last known fully working version
- **Previous iterations** - Solutions to past issues and working approaches
- **Development history** - Evolution of successful implementations
- **Usage**: Reference for working code patterns, copy proven solutions

### `docs/`
- **`archipelago_generator_guide.md`** - Detailed implementation guide
- **`development_summary.txt`** - Technical history and lessons learned
- **API documentation** - Technical reference for Blender integration
- **Usage**: Understanding context and proven approaches

## Critical Asset Usage Rules:

### 🚨 **ALWAYS DO THIS:**
1. **Check assets directory FIRST** before writing any new code
2. **Import existing geometry nodes** instead of creating new ones
3. **Reference previous working versions** for proven approaches
4. **Use preset configurations** rather than guessing parameters
5. **Build incrementally** on working foundations

### ❌ **NEVER DO THIS:**
1. **Create geometry nodes from scratch** when working ones exist
2. **Rewrite operators** that are already functional
3. **Guess parameter values** when presets are available
4. **Ignore previous solutions** to similar problems
5. **Start development** without checking existing assets

## Asset Import Methods:

### **Geometry Nodes:**
```python
# In Blender Python Console or Script:
import bpy

# Check if node group exists
if "WorkingTerrainDisplacement" in bpy.data.node_groups:
    node_group = bpy.data.node_groups["WorkingTerrainDisplacement"]
else:
    # Import from asset file
    bpy.ops.wm.append(
        filepath="//src/assets/geometry_nodes/terrain_displacement.blend/NodeTree/WorkingTerrainDisplacement",
        directory="src/assets/geometry_nodes/terrain_displacement.blend/NodeTree/",
        filename="WorkingTerrainDisplacement"
    )
```

### **Previous Code Versions:**
```python
# Reference working implementations from src/previous/
# Copy proven functions and adapt rather than rewriting
from src.previous.oneill_heightmap_terrain_final import working_function
```

### **Configuration Presets:**
```python
# Load tested parameter sets
preset_path = "src/assets/presets/terrain_settings.json"
with open(preset_path, 'r') as f:
    proven_settings = json.load(f)
```

## Specific Asset Locations:

### **Working Geometry Nodes:**
- **Location**: `src/assets/geometry_nodes/terrain_displacement.blend`
- **Contains**: Proven UV mapping, heightmap sampling, vertex displacement
- **Use For**: Setup Live Preview step instead of creating new nodes
- **Import Method**: File → Append → NodeGroup → Select working group

### **Terrain Presets:**
- **Location**: `src/assets/presets/`
- **Contains**: Tested scale values, noise parameters, resolution settings
- **Use For**: Default values and proven parameter combinations
- **Access Method**: Load JSON or reference in code comments

### **Previous Working Versions:**
- **Location**: `src/previous/oneill_heightmap_terrain_final.py`
- **Contains**: Last fully functional implementation
- **Use For**: Reference when current version has issues
- **Method**: Compare implementations, copy working functions

### **Implementation Guides:**
- **Location**: `docs/archipelago_generator_guide.md`
- **Contains**: Step-by-step implementation details
- **Use For**: Understanding proven workflow approaches
- **Method**: Follow documented successful patterns

## Asset Quality Indicators:

### ✅ **High Quality (Use These):**
- **Documented in guides** - Has implementation documentation
- **Referenced in previous versions** - Used in working implementations
- **Tested with real geometry** - Proven with actual O'Neill cylinders
- **Has preset configurations** - Includes tested parameter sets

### ⚠️ **Unknown Quality (Investigate First):**
- **No documentation** - Unclear purpose or usage
- **No references** - Not used in working versions
- **Experimental features** - May not be fully functional

### ❌ **Avoid (Unless Specifically Needed):**
- **Placeholder files** - Incomplete implementations
- **Deprecated versions** - Superseded by working solutions
- **Test files** - Not intended for production use

## Development Workflow with Assets:

### 1. **Asset Discovery Phase:**
- Check `src/assets/` for relevant components
- Review `src/previous/` for working implementations
- Read `docs/` guides for context and approaches

### 2. **Asset Integration Phase:**
- Import/reference existing working components
- Adapt proven solutions to current needs
- Test with existing geometry from user's scene

### 3. **Incremental Enhancement Phase:**
- Make minimal changes to working systems
- Add features without breaking existing functionality
- Document new approaches for future reference

### 4. **Asset Update Phase:**
- Update presets with new proven configurations
- Document successful implementations
- Add working examples to asset library

## Troubleshooting with Assets:

### **Issue**: Feature not working
**Solution**: Check if working version exists in `src/assets/` or `src/previous/`

### **Issue**: Geometry nodes failing  
**Solution**: Import proven node group from `src/assets/geometry_nodes/`

### **Issue**: Parameter values unclear
**Solution**: Reference tested presets in `src/assets/presets/`

### **Issue**: Implementation approach uncertain
**Solution**: Follow patterns from `docs/archipelago_generator_guide.md`

---
*Always use existing working assets as foundation rather than building from scratch.*