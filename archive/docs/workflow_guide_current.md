# O'Neill Terrain Generator - User Workflow Guide
*Updated: 2025-06-21*

## 🎯 Complete 5-Step Workflow

### **Before You Start**
- **Save your .blend file** - Required for archipelago asset loading
- **Import your O'Neill cylinder segments** into Blender
- **Install the add-on** from `/src/dev/oneill_heightmap_terrain_dev.py`
- **Find the panel** in 3D Viewport sidebar under "ONeill" tab

---

## 📋 Main Workflow Sequence

### **Step 1: Align Cylinders** 🎯
**Purpose:** Ensure all cylinder segments are perfectly aligned for seamless terrain
**When to use:** When you have multiple cylinder segments that need to connect

1. **Select all cylinder objects** you want to align
2. **Choose alignment axis** (usually X-axis for length-wise cylinders)
3. **Click "Align Cylinders"**
4. **Result:** All segments aligned along chosen axis

**Settings:**
- **Alignment Axis:** X/Y/Z axis selection
- **Precision Threshold:** Gap tolerance for alignment

---

### **Step 2: Unwrap to Flat** 📐
**Purpose:** Create flat grid objects that preserve the actual interior surface area
**When to use:** After alignment, before creating terrain

1. **Select aligned cylinder objects**
2. **Click "Unwrap to Flat"** 
3. **Choose subdivision levels** (4 is usually good)
4. **Result:** Flat grid objects created, originals hidden

**What happens:**
- Calculates exact cylinder dimensions (radius × circumference)
- Creates high-resolution flat grids
- Stores metadata for perfect reconstruction
- Original cylinders hidden but preserved

---

### **Step 3: Create Heightmaps** 🖼️
**Purpose:** Generate raster images for terrain painting or procedural generation
**When to use:** After unwrapping, before terrain editing

1. **Select unwrapped flat objects**
2. **Set heightmap resolution** (1024×1024 recommended)
3. **Click "Create Heightmaps"**
4. **Result:** Heightmap images created with proper materials

**Settings:**
- **Resolution:** 512×512 (fast) to 2048×2048 (detailed)
- **Automatic material setup** with UV mapping

---

### **Step 4: Edit/Generate Terrain** 🏔️
**Purpose:** Create terrain through manual painting or procedural generation
**When to use:** After heightmaps are created

#### **Option A: Manual Terrain Painting** (Recommended)
1. **Select flat object** with heightmap
2. **Click "Edit Heightmap"** 
   - Automatically opens Image Editor with correct file
   - Sets proper colorspace for editing
   - Switches to paint mode
3. **Paint your terrain** using Blender's brush tools
4. **Click "Return to 3D"** when finished
   - Returns to 3D viewport
   - Updates all heightmaps

#### **Option B: Procedural Generation**
1. **Select flat objects**
2. **Adjust settings:**
   - **Terrain Strength:** How pronounced the terrain is
   - **Noise Scale:** Size of terrain features  
   - **Random Seed:** For repeatable results
3. **Click "Generate Noise Terrain"**

#### **Option C: Advanced Archipelago Terrain**
1. **Click "Load Archipelago Assets"** (once per session)
2. **Select flat objects**
3. **Click "Apply Archipelago Terrain"**
4. **Result:** Advanced island/water patterns via geometry nodes

---

### **Step 5: Rewrap to Cylinders** 🔄
**Purpose:** Convert terrain back to cylinder form with exact original dimensions
**When to use:** After terrain is completed

1. **Select flat objects** with terrain/heightmaps
2. **Click "Rewrap to Cylinders"**
3. **Set terrain scale** (2.0 is usually good)
4. **Result:** Terrain cylinders created with exact original positioning

**What happens:**
- Duplicates original cylinder geometry exactly
- Applies heightmap displacement to interior surface
- Preserves all transform properties
- Creates "_terrain" versions of objects

---

## 🎨 Heightmap Editing Tips

### **Image Editor Workflow**
- **Use "Edit Heightmap" button** - Automatically sets up everything correctly
- **Paint in grayscale** - White = raised terrain, Black = recessed, Gray = neutral
- **Use soft brushes** for natural terrain transitions
- **Save frequently** - Heightmaps are stored in the .blend file

### **Brush Settings**
- **Size:** Start with large brushes for major features, smaller for details
- **Strength:** 0.3-0.7 for subtle changes, higher for dramatic terrain
- **Falloff:** Smooth falloff for natural-looking terrain

### **Terrain Planning**
- **Start with major features** - Mountains, valleys, water areas
- **Add medium details** - Hills, ridges, river systems  
- **Finish with fine details** - Small terrain variations

---

## 🔧 Advanced Features

### **Archipelago Terrain System**
- **Load Assets:** Loads sophisticated geometry node groups
- **Island Patterns:** Creates realistic island/water distributions
- **Advanced Control:** More complex than basic noise generation
- **File Requirement:** Needs `/src/assets/geometry_nodes/archipelago_terrain_generator.blend`

### **Multiple Resolution Workflow**
1. **Start with 512×512** for quick iteration
2. **Move to 1024×1024** for detailed work
3. **Use 2048×2048** for final high-quality terrain

### **Batch Processing**
- **Process similar segments together** - Select multiple flat objects
- **Use same settings** for consistent terrain across segments
- **Handle special segments separately** - Central sea, taper zones, etc.

---

## ⚠️ Current Limitations & Workarounds

### **Boundary Gaps** (Major Known Issue)
**Problem:** Visible breaks between terrain on adjacent cylinder segments
**Status:** Major enhancement planned
**Workaround:** 
- Process segments individually
- Manually blend terrain at boundaries in image editor
- Use similar heightmap patterns at segment edges

### **UI Button Order** (Minor Issue)  
**Problem:** Workflow buttons not in perfect sequence
**Status:** Fix pending
**Workaround:** Follow this guide's sequence regardless of button layout

### **Image Editor Workspace** (Minor Issue)
**Problem:** "Edit Heightmap" may switch to Shading workspace
**Status:** Fix pending  
**Workaround:** Manually switch back to Layout if needed

---

## 🎮 Game Development Integration

### **Export Workflow**
1. **Complete terrain generation** using this workflow
2. **Select terrain cylinder objects** (objects ending in "_terrain")
3. **Export to your game engine** as static meshes
4. **Original cylinders remain available** for reference or modification

### **Asset Pipeline**
- **Terrain objects** maintain exact dimensions for asset placement
- **Materials** can be enhanced with additional textures in game engine
- **Heightmaps** can be exported separately for detail texturing
- **UV mapping** preserved for texture application

### **dssstrkl Scale Validation**
- All terrain scaled appropriately for dssstrkl character proportions
- Habitat authenticity maintained (visible artificial structure)
- Game-ready geometry topology

---

## 🚀 Tips for Best Results

### **Performance**
- **Save before major operations** - Complex terrain generation can be memory intensive
- **Start with lower resolutions** - Test workflow with 512×512 before moving to higher resolutions
- **Process in batches** - Don't select too many objects at once
- **Close unnecessary panels** - Free up system resources for terrain processing

### **Terrain Design**
- **Study real space habitats** - Reference O'Neill cylinder concept art for authentic layouts
- **Plan your biomes** - Central sea, agricultural zones, urban areas, natural landscapes
- **Consider artificial elements** - Visible support structures, mechanical systems, artificial lighting
- **Think in 3D** - Remember terrain will wrap around cylinder interior

### **Workflow Efficiency**
- **Use consistent naming** - Keep track of which segments are processed
- **Create templates** - Save heightmap patterns for reuse across similar segments
- **Document your process** - Keep notes on settings that work well
- **Version control** - Save incremental .blend files as you progress

### **Quality Control**
- **Test early and often** - Check terrain results at each step
- **Zoom in to check details** - Ensure terrain quality meets your standards
- **Verify dimensions** - Confirm terrain objects match original cylinder sizes
- **Check for artifacts** - Look for unwanted stretching or distortion

---

## 🔍 Troubleshooting Quick Reference

### **Common Issues**
- **Heightmap appears blank:** Check colorspace (should be "Non-Color")
- **Terrain looks wrong:** Verify heightmap is properly linked to flat object
- **Missing buttons:** Check that add-on is properly installed and enabled
- **Objects don't align:** Ensure you've selected 2+ objects before aligning

### **Console Commands**
```python
# Check flat objects
flat_objs = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
print(f"Flat objects: {[obj.name for obj in flat_objs]}")

# Check heightmaps
heightmaps = [img for img in bpy.data.images if "_heightmap" in img.name]
print(f"Heightmaps: {[img.name for img in heightmaps]}")

# Check terrain objects  
terrain_objs = [obj for obj in bpy.data.objects if obj.get("oneill_terrain")]
print(f"Terrain objects: {[obj.name for obj in terrain_objs]}")
```

### **Reset Workflow**
If something goes wrong:
1. **Unhide original cylinders** - Select in outliner, press Alt+H
2. **Delete problematic objects** - Remove flat/terrain objects if needed
3. **Start fresh** - Begin workflow from Step 1
4. **Check console** - Look for error messages

---

## 🌟 Advanced Techniques

### **Multi-Biome Workflow**
1. **Create separate heightmaps** for different biome types
2. **Use layers in image editor** to combine terrain types
3. **Paint biome boundaries** with careful attention to transitions
4. **Apply different materials** to terrain objects for visual variety

### **Detailed Terrain Features**
- **Rivers and waterways** - Use dark lines in heightmaps for channels
- **Cliff faces** - Sharp black-to-white transitions for dramatic elevation changes
- **Gentle slopes** - Gradual grayscale transitions for rolling hills
- **Flat areas** - Gray values for plains, landing pads, urban zones

### **Archipelago Customization**
- **Load archipelago assets** for advanced island generation
- **Combine with manual painting** - Use archipelago as base, refine manually
- **Experiment with settings** - Geometry nodes offer extensive customization
- **Save successful configurations** - Document node settings that work well

---

## 📚 Integration with dssstrkl Worldbuilding

### **Habitat Zones**
- **Central Sea** - Water reclamation and transportation hub
- **Agricultural Bands** - Food production areas with visible irrigation
- **Urban Districts** - Cliff cities and settlements showing dssstrkl architecture
- **Maintenance Zones** - Access areas revealing artificial nature of habitat
- **Natural Reserves** - Preserved landscape areas for cultural/psychological needs

### **Authentic Details**
- **Visible Infrastructure** - Pipes, support beams, mechanical systems
- **Artificial Lighting** - Consider how artificial sunlight affects terrain shadows
- **Gravity Effects** - Terrain should feel natural despite artificial gravity
- **Scale Appropriateness** - Everything sized for dssstrkl physiology and culture

### **Cultural Elements**
- **Memorial Sites** - Significant locations in dssstrkl history
- **Clan Territories** - Different architectural/terrain styles for different family groups
- **Hidden Elements** - Concealed areas reflecting the death cult infiltration storyline
- **Atlantean Remnants** - Ancient technology integrated into landscape

---

## 🎯 Next Steps After Terrain Generation

### **Post-Processing**
1. **Material Enhancement** - Add detailed textures and materials in Blender or game engine
2. **Lighting Setup** - Create appropriate lighting for space habitat environment  
3. **Asset Population** - Add buildings, vegetation, vehicles, character spawn points
4. **Environmental Effects** - Atmosphere, particle systems, dynamic elements

### **Game Engine Integration**
1. **Export Process** - Transfer terrain meshes to Unreal Engine or other game engine
2. **LOD Setup** - Create level-of-detail versions for performance
3. **Collision Meshes** - Generate simplified collision geometry
4. **Optimization** - Texture streaming, mesh optimization, performance tuning

### **Iteration and Refinement**
- **Playtesting Feedback** - Adjust terrain based on gameplay requirements
- **Performance Optimization** - Refine for target hardware specifications
- **Visual Polish** - Enhance materials, lighting, and atmospheric effects
- **Narrative Integration** - Ensure terrain supports storytelling goals

---

## 🔗 Additional Resources

### **Documentation**
- `/docs/troubleshooting_guide.md` - Comprehensive issue resolution
- `/docs/development_summary.txt` - Technical development details  
- `/docs/project_overview.md` - Complete project context and vision

### **Assets**
- `/src/assets/geometry_nodes/` - Advanced terrain generation node groups
- `/examples/` - Sample O'Neill cylinder .blend files
- Character references for scale validation

### **Development**
- `/src/dev/oneill_heightmap_terrain_dev.py` - Latest development version
- GitHub repository for version control and collaboration
- Issue tracking for bug reports and feature requests

---

*This workflow guide provides complete instructions for creating authentic dssstrkl habitat terrain using the O'Neill Terrain Generator. Follow these steps to build the interior worlds of tomorrow's space habitats with the perfect balance of artificial precision and natural beauty.*