# Troubleshooting Guide

## Before Starting Any Development:
1. **Read** `docs/README_START_HERE.md` completely
2. **Check current status** in `docs/current_status.md`
3. **Look for working assets** in `src/assets/` and `src/previous/`
4. **Review implementation guides** in `docs/archipelago_generator_guide.md`
5. **Never start from scratch** - always use existing working code

## Common Issues & Solutions:

### 🚨 **Critical Issue: "Building from scratch instead of using working code"**

#### ❌ **Wrong Approach:**
- Creating new geometry nodes when working ones exist
- Rewriting operators that are already functional  
- Ignoring existing solutions in project assets
- Starting development without checking `src/assets/`

#### ✅ **Correct Approach:**
- **Import working geometry nodes** from `src/assets/geometry_nodes/`
- **Reference previous working versions** in `src/previous/`
- **Fix specific bugs only** in existing code
- **Build incrementally** on proven foundations

#### **How to Avoid:**
1. Always check `src/assets/geometry_nodes/` before creating nodes
2. Use File → Append → NodeGroup to import working setups
3. Compare with `src/previous/oneill_heightmap_terrain_final.py`
4. Follow patterns from `docs/archipelago_generator_guide.md`

---

## ✅ VERSION 2.0.0 RESOLVED ISSUES

### **Module Integration Complete - All Issues Resolved**
**Date Resolved**: June 30, 2025
**Status**: ✅ PRODUCTION READY

#### **TUNDRA → ARCHIPELAGO Migration - COMPLETE**
- **Issue**: Legacy TUNDRA biome references throughout codebase
- **Resolution**: Complete replacement with ARCHIPELAGO biome
- **Impact**: All biome lists, color mappings, and UI updated
- **Testing**: Full workflow tested with new biome system

#### **Terrain Painting Integration - COMPLETE**
- **Issue**: Manual biome painting system needed integration
- **Resolution**: terrain_painting.py module fully integrated
- **Features**: Canvas creation, biome selection, painting mode
- **Testing**: 12-cylinder heightmap painting workflow validated

#### **Biome Generation Integration - COMPLETE**
- **Issue**: Python-based geometry node system needed integration
- **Resolution**: biome_geometry_generator.py module integrated
- **Features**: Node group creation, biome application, 6-biome system
- **Testing**: All biomes tested and working correctly

#### **Registration Conflicts - RESOLVED**
- **Issue**: Module registration causing scope conflicts
- **Resolution**: Clean registration system with graceful fallback
- **Implementation**: Try/catch blocks for missing modules
- **Result**: Add-on works with or without optional modules

### **Current Status: All Major Issues Resolved**
- ✅ No critical blocking issues remaining
- ✅ Complete workflow functional end-to-end
- ✅ All modules integrated and tested
- ✅ Ready for next development phase

### **Issue: "Terrain not visible in viewport"**

#### **Symptoms:**
- Console shows terrain generation activity
- Scale changes move entire object instead of vertex displacement
- No heightmap-based deformation visible

#### **Root Causes:**
1. **Geometry nodes using object transform instead of vertex displacement**
2. **UV coordinate mapping incorrect for flat grid**
3. **Heightmap not properly connected to displacement chain**
4. **Scale values too small to see effect**

#### **Solutions:**
1. **Import working geometry nodes** from `src/assets/geometry_nodes/`
2. **Check UV mapping**: Position → Separate XYZ → Combine XYZ (X,Y as U,V)
3. **Verify node connections**: Image Texture → Math → Vector Math → Set Position Offset
4. **Test scale values**: Try 1.0, 2.0, 5.0 to see if displacement becomes visible
5. **Check heightmap content**: Open in Image Editor to verify non-uniform patterns

#### **Debugging Steps:**
```python
# In Blender console, check modifier inputs:
obj = bpy.context.active_object
for mod in obj.modifiers:
    if mod.type == 'NODES':
        print(f"Modifier: {mod.name}")
        print(f"Node Group: {mod.node_group.name if mod.node_group else 'None'}")
        # Check inputs
        for item in mod.node_group.interface.items_tree:
            print(f"  Input: {item.name} = {mod.get(item.identifier, 'Not Set')}")
```

---

### **Issue: "UI elements missing"**

#### **Symptoms:**
- Buttons not appearing in panel
- Operators not registered
- Panel sections empty

#### **Root Causes:**
1. **Operator not in classes list for registration**
2. **Panel draw() method layout errors**
3. **Conditional logic hiding elements**
4. **Script cache not cleared after updates**

#### **Solutions:**
1. **Check registration**: Verify operator in `classes = [...]` list
2. **Simplify panel logic**: Remove try/except blocks and conditionals
3. **Clear cache**: Restart Blender or reload script completely
4. **Debug registration**: Check console for registration errors

#### **Debugging Steps:**
```python
# Check if operator is registered:
print("oneill operators:", dir(bpy.ops.oneill))
print("ONEILL_OT_UpdateTerrainScale in types:", hasattr(bpy.types, 'ONEILL_OT_UpdateTerrainScale'))
```

---

### **Issue: "Geometry nodes socket interface errors"**

#### **Symptoms:**
- Error: "expected Image type, not float"
- Geometry nodes setup fails
- Node group creation crashes

#### **Root Causes:**
1. **Setting default_value on Image sockets** (not supported)
2. **Array index access** instead of storing socket references
3. **Interface setup order** problems

#### **Solutions:**
1. **Store socket references**: `image_input = group.interface.new_socket(...)`
2. **Only set default_value on Float sockets**, never on Image sockets
3. **Add exception handling** around default value setting
4. **Use working node group** from `src/assets/geometry_nodes/`

---

### **Issue: "Heightmap generation no effect"**

#### **Symptoms:**
- Console shows pixel updates
- No visual change in Image Editor
- Terrain doesn't update

#### **Root Causes:**
1. **Image not properly updating in viewport**
2. **Geometry nodes not responding to image changes**
3. **Materials not linked to updated image**

#### **Solutions:**
1. **Force updates**: `image.update_tag()`, `bpy.context.view_layer.update()`
2. **Refresh areas**: Tag Image Editor and 3D Viewport for redraw
3. **Check material links**: Verify heightmap connected to material nodes

---

### **Issue: "Registration conflicts"**

#### **Symptoms:**
- Add-on fails to register
- Duplicate class errors
- UI doesn't appear

#### **Root Causes:**
1. **Previous version still loaded**
2. **Class names conflict**
3. **Scene properties not cleaned**

#### **Solutions:**
1. **Use cleanup_existing() function** before registration
2. **Restart Blender** to clear cache completely
3. **Check for duplicate bl_idname values**

---

## Development Methodology (Prevention-Focused):

### ✅ **Always Do:**
1. **Start with working code** from project assets
2. **Identify specific issue** before making changes
3. **Make minimal changes** to resolve issue only
4. **Test with existing scene files** and geometry
5. **Update documentation** when issue is resolved
6. **Preserve working functionality** while fixing bugs

### ❌ **Never Do:**
1. **Start from scratch** when working code exists
2. **Rewrite entire systems** to fix minor issues
3. **Ignore existing assets** in project folder
4. **Skip documentation** when making changes
5. **Break working features** while adding new ones

### **When Stuck:**
1. **Check `src/previous/`** for working implementations
2. **Reference `docs/archipelago_generator_guide.md`** for proven approaches
3. **Import assets from `src/assets/`** instead of creating new
4. **Test with minimal changes** first
5. **Ask for specific guidance** rather than starting over

---

## Emergency Recovery:

### **If Development Goes Wrong:**
1. **Revert to last working version** from `src/previous/`
2. **Check `docs/current_status.md`** for known good state
3. **Import working assets** from `src/assets/`
4. **Start with minimal fix** rather than major rewrite
5. **Document what went wrong** to prevent repetition

### **Files to Reference for Recovery:**
- `src/previous/oneill_heightmap_terrain_final.py` - Last known working version
- `src/assets/geometry_nodes/` - Working node setups
- `docs/development_summary.txt` - What was working before
- `docs/current_status.md` - Current issue specifics

---
*Prevention is better than cure - always use working assets as foundation.*

## Version 2.0 Troubleshooting Updates

### ✅ RESOLVED ISSUES

#### Geometry Nodes Import Problems - RESOLVED
**Previous Issue:** Geometry nodes setup failing, couldn't load terrain displacement
**Solution Implemented:** GeometryNodesAssetManager with modular import system
- Assets automatically discovered from `src/assets/geometry_nodes/`
- Multiple fallback options for node group names
- Project-aware path detection works from any .blend file location
- Working import from `archipelago_terrain_generator.blend`

#### UI Workflow Clarity - RESOLVED  
**Previous Issue:** No visual feedback for completed workflow steps
**Solution Implemented:** Visual completion indicators
- ✅ Checkmarks for completed steps
- Blue "depressed" button styling for finished operations
- Clear progression through 5-step workflow

#### No Undo for Rewrap - RESOLVED
**Previous Issue:** Couldn't undo rewrap if results unsatisfactory
**Solution Implemented:** ONEILL_OT_UndoRewrap operator
- Removes terrain objects and restores flat objects
- Smart UI integration (undo button appears after rewrap)
- Preserves workflow state for iteration

### 🔧 CURRENT KNOWN ISSUES

#### Issue: Terrain Seams Between Objects (Critical)
**Symptoms:**
- Visible height discontinuities between cylinder segments
- Each object gets separate heightmap causing mismatched terrain
- Breaks realism across multiple O'Neill cylinder sections

**Diagnosis:**
- Heightmaps created per-object without consideration for neighbors
- UV mapping doesn't account for position in overall cylinder sequence
- No coordination between adjacent segment terrain generation

**Workaround:** 
- Use single cylinder object when possible
- Manual heightmap editing to match seams

**Planned Fix:** Unified heightmap system with smart UV subdivision

#### Issue: Terrain on Wrong Surfaces (Critical)
**Symptoms:**
- Displacement applies to both interior AND exterior cylinder surfaces
- Exterior of O'Neill cylinder gets terrain (should remain smooth)
- Breaks the habitat design where terrain should be interior-only

**Diagnosis:**
- Geometry nodes apply to all mesh faces uniformly
- No face selection for interior vs exterior surfaces
- Displacement modifier affects entire mesh

**Workaround:**
- Manual face selection and separate displacement (complex)
- Use separate objects for interior/exterior (not ideal)

**Planned Fix:** Interior surface detection with selective displacement

#### Issue: Asset Discovery Sensitivity
**Symptoms:**
- Asset manager requires specific project folder structure
- Fails if .blend file not saved in project location
- Path detection can be fragile with symlinks/aliases

**Diagnosis:**
- Relies on "oneill terrain generator" string in file path
- Absolute path assumptions may not work across systems

**Workaround:**
- Ensure .blend file saved within project structure
- Use "List Available Assets" to verify detection

**Fix Status:** Working but could be more robust

### 🔍 DEBUGGING TIPS

#### Geometry Nodes Issues:
1. Use "List Available Assets" button to verify asset discovery
2. Check console for detailed import logging
3. Verify `archipelago_terrain_generator.blend` exists in `src/assets/geometry_nodes/`
4. Ensure .blend file saved within project structure

#### Terrain Quality Issues:
1. Check heightmap resolution setting (1024x1024 recommended)
2. Verify terrain scale multiplier not set too high/low
3. Use undo functionality to iterate on terrain settings
4. Monitor viewport performance with high subdivision levels

#### Workflow State Issues:
1. Visual indicators show which steps completed
2. Can restart from any step by selecting appropriate objects
3. Use cleanup_existing() function if registration issues persist
4. Check object custom properties for workflow metadata

### 💡 PERFORMANCE OPTIMIZATION

#### For Large Cylinder Segments:
- Start with lower subdivision levels during testing
- Use 512x512 heightmaps for preview, 2048x2048 for final
- Disable live preview during heavy terrain generation
- Consider breaking very long cylinders into smaller segments

#### Memory Management:
- Remove unused heightmap images periodically
- Use undo sparingly with large meshes
- Monitor Blender memory usage with complex geometry nodes

### 🚀 UPCOMING FIXES

#### v2.1 Priority Fixes:
1. **Unified Heightmap System:** Single heightmap across multiple objects
2. **Interior Surface Detection:** Selective displacement for interior faces only
3. **Enhanced Asset Robustness:** Better path detection and error handling

#### Development Process:
- Each fix will be thoroughly tested with real O'Neill cylinder geometry
- Maintain backward compatibility with existing workflow
- Document any breaking changes in upgrade process