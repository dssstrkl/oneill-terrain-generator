# Project Assets Guide - UPDATED

## 🆕 NEW: Mountains Biome Node Available

### `src/assets/geometry_nodes/biomes/mountains.blend` ✅
- **Mountains node group** - Complete mountain terrain generator with elevation gradients and dramatic peaks
- **Test objects** - Pre-configured Mountain_Test_Positive_X and Mountain_Test_Negative_X for verification
- **Documentation** - Built-in Mountains_Documentation text block with usage instructions
- **Materials** - Optimized material setup for mountain terrain visualization
- **Status**: ✅ Production ready, fully tested and verified

#### **Usage Example:**
```python
# Import mountains node group
bpy.ops.wm.append(
    filepath="//src/assets/geometry_nodes/biomes/mountains.blend/NodeTree/mountains",
    directory="src/assets/geometry_nodes/biomes/mountains.blend/NodeTree/",
    filename="mountains"
)

# Apply to object
modifier = obj.modifiers.new("Mountain_Terrain", 'NODES')
modifier.node_group = bpy.data.node_groups["mountains"]

# Configure key parameters
modifier["Input_15"] = 8.0  # Elevation_Gradient (5.0-10.0 recommended)
modifier["Input_9"] = 4.0   # Dramatic_Peak_Height (2.0-5.0 recommended)
```

---

## Working Components Available (USE THESE FIRST)

### `src/assets/geometry_nodes/biomes/` ✅ NEW STRUCTURE
```
biomes/
├── mountains.blend          # ✅ Rocky peaks, cliff formations
├── archipelago.blend        # ✅ Island chains (existing)
├── canyons.blend           # ⏳ Deep valleys (in development)
├── hills.blend             # ⏳ Gentle rolling terrain (planned)
├── forest.blend            # ⏳ Organic terrain with vegetation (planned)
├── desert.blend            # ⏳ Dune formations (planned)
└── ocean.blend             # ⏳ Underwater terrain (planned)
```

**Best Practice**: Import individual biome files as needed rather than loading all biomes simultaneously.

### `src/assets/geometry_nodes/` (Legacy)
- **archipelago_terrain_generator.blend** - Original archipelago system (1.1MB)
- **Status**: ✅ Still functional, but recommend using biomes/archipelago.blend for new projects

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
- **`oneill_biome_system_dev_doc.md`** - Complete biome system documentation
- **`development_summary.txt`** - Technical history and lessons learned
- **Usage**: Understanding context and proven approaches

---

## 🔧 Updated Asset Usage Rules:

### 🚨 **ALWAYS DO THIS:**
1. **Check biomes/ directory FIRST** for modular geometry nodes
2. **Import specific biome files** instead of monolithic assets
3. **Use mountains.blend as template** for creating new biomes
4. **Reference test objects** in biome files for parameter guidance
5. **Follow standardized biome interface** for consistency

### ❌ **NEVER DO THIS:**
1. **Create geometry nodes from scratch** when biome files exist
2. **Mix archipelago and mountains** in same modifier (use biome compositor instead)
3. **Modify biome node groups directly** (create variations instead)
4. **Ignore test object configurations** when applying to new objects
5. **Skip documentation text blocks** in biome files

---

## 🎯 Asset Import Methods Updated:

### **Mountains Biome:**
```python
# Check if mountains node exists
if "mountains" in bpy.data.node_groups:
    mountains_ng = bpy.data.node_groups["mountains"]
else:
    # Import from biome file
    bpy.ops.wm.append(
        filepath="//src/assets/geometry_nodes/biomes/mountains.blend/NodeTree/mountains",
        directory="src/assets/geometry_nodes/biomes/mountains.blend/NodeTree/",
        filename="mountains"
    )
    mountains_ng = bpy.data.node_groups["mountains"]

# Apply mountains terrain
modifier = target_object.modifiers.new("Mountain_Terrain", 'NODES')
modifier.node_group = mountains_ng

# Recommended parameter configuration
modifier["Input_15"] = 8.0   # Elevation_Gradient
modifier["Input_9"] = 4.0    # Dramatic_Peak_Height  
modifier["Input_5"] = 2.0    # Peak_Height
modifier["Input_6"] = 1.5    # Cliff_Steepness
```

### **Multiple Biomes (Future):**
```python
# Load multiple biomes for complex terrain
biomes = ["mountains", "hills", "forest"]
biome_nodes = {}

for biome in biomes:
    if biome not in bpy.data.node_groups:
        bpy.ops.wm.append(
            filepath=f"//src/assets/geometry_nodes/biomes/{biome}.blend/NodeTree/{biome}",
            directory=f"src/assets/geometry_nodes/biomes/{biome}.blend/NodeTree/",
            filename=biome
        )
    biome_nodes[biome] = bpy.data.node_groups[biome]

# Use biome compositor for blending (future implementation)
```

---

## 📊 Asset Quality Indicators Updated:

### ✅ **High Quality (Use These):**
- **mountains.blend** - ✅ Fully tested, production ready
- **archipelago.blend** - ✅ Established, working system  
- **Has test objects** - ✅ Includes verification objects with proper parameters
- **Documented in text blocks** - ✅ Built-in usage instructions
- **Standardized interface** - ✅ Compatible with biome system architecture

### ⚠️ **Development Quality (Use with Caution):**
- **Future biome files** - ⏳ Will be created using mountains template
- **Experimental features** - ⚠️ May not be fully functional until documented
- **Custom modifications** - ⚠️ Test thoroughly before production use

### ❌ **Deprecated (Migrate Away From):**
- **archipelago_terrain_generator.blend** - ⚠️ Use biomes/archipelago.blend instead
- **Monolithic geometry files** - ❌ Prefer modular biome approach
- **Undocumented node groups** - ❌ Risk of parameter confusion

---

## 🚀 Development Workflow with Updated Assets:

### 1. **Asset Discovery Phase:**
- Check `src/assets/geometry_nodes/biomes/` for modular biome files
- Review `mountains.blend` as the gold standard template
- Read built-in documentation text blocks in biome files

### 2. **Asset Integration Phase:**
- Import specific biome node groups as needed
- Use test objects as parameter reference
- Apply standardized biome interface

### 3. **Biome Development Phase (Creating New Biomes):**
- Copy `mountains.blend` as starting template
- Modify noise and elevation parameters for new biome type
- Update documentation text block
- Test with positive/negative X positioning
- Verify standardized input/output interface

### 4. **Asset Update Phase:**
- Save new biome variations as separate .blend files
- Document successful parameter combinations
- Add working examples to biome library

---

## 🔍 Troubleshooting with Updated Assets:

### **Issue**: Mountains terrain not generating correctly
**Solution**: Import `mountains.blend`, check test object parameters, verify Elevation_Gradient (5.0-10.0) and Dramatic_Peak_Height (2.0-5.0)

### **Issue**: Need different mountain style  
**Solution**: Copy `mountains.blend`, modify noise parameters, save as new biome variant

### **Issue**: Gradient direction wrong
**Solution**: Mountains uses X-axis gradient (away from origin = higher). Check object positioning and Elevation_Gradient sign.

### **Issue**: Want to combine biomes
**Solution**: Use individual biome modifiers + biome mask system (Phase 2 development)

---

**Key Update**: Mountains biome now available as standalone, production-ready asset with complete documentation and testing. Use as template for future biome development.

*Updated: 2025-06-24*  
*Next: Canyons biome development using mountains template*