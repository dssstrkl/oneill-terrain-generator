# Integration Instructions - Archipelago Terrain Generator

## Project Information
**Target Project**: `/Documents/Project/oneill terrain generator`
**Asset Package**: Archipelago terrain generation for O'Neill cylinders

## Quick Integration Steps

### 1. Copy Asset Files
```bash
# Navigate to asset package
cd /var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator

# Copy to your project (verify path exists)
TARGET="/Documents/Project/oneill terrain generator"

# Copy assets
cp -r src/assets "$TARGET/src/"
cp src/operators/archipelago_operators.py "$TARGET/src/operators/"
cp src/utils/asset_manager.py "$TARGET/src/utils/"
cp docs/*.md "$TARGET/docs/"
```

### 2. Update Main Add-on File
In your `/Documents/Project/oneill terrain generator/src/oneill_heightmap_terrain.py`:

```python
# Add imports at the top
try:
    from .operators.archipelago_operators import (
        ONEILL_OT_ApplyArchipelago,
        ONEILL_OT_LoadArchipelagoAsset
    )
    HAS_ARCHIPELAGO = True
except ImportError:
    HAS_ARCHIPELAGO = False
    print("Archipelago operators not available")

# Add to your classes list
classes = [
    # ... existing classes ...
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_PT_MainPanel,
]

# Add archipelago classes if available
if HAS_ARCHIPELAGO:
    classes.extend([
        ONEILL_OT_ApplyArchipelago,
        ONEILL_OT_LoadArchipelagoAsset,
    ])
```

### 3. Add UI Integration
Update your terrain panel in the main add-on:

```python
class ONEILL_PT_terrain_panel(bpy.types.Panel):
    # ... existing code ...
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # ... existing terrain options ...
        
        # Add archipelago section
        if HAS_ARCHIPELAGO:
            flat_objects = [obj for obj in context.selected_objects 
                           if obj.get("oneill_flat")]
            
            layout.separator()
            box = layout.box()
            box.label(text="🌊 Archipelago Terrain:", icon='WORLD')
            
            if flat_objects:
                box.operator("oneill.apply_archipelago", 
                            text=f"Apply to {len(flat_objects)} Objects")
            else:
                row = box.row()
                row.operator("oneill.apply_archipelago", text="Apply Archipelago")
                row.enabled = False
                box.label(text="(Select unwrapped flat objects)", icon='INFO')
            
            box.operator("oneill.load_archipelago_asset", text="Load Asset")
```

### 4. Enhanced Workflow Integration
Your updated O'Neill workflow becomes:

```
1. Align Cylinders     → oneill.align_cylinders
2. Unwrap to Flat      → oneill.unwrap_to_flat
3. Choose Terrain:
   📐 Heightmap Paint  → oneill.create_heightmaps + manual painting
   🌊 Archipelago Gen  → oneill.apply_archipelago (NEW!)
4. Rewrap to Cylinders → oneill.rewrap_to_cylinder
```

### 5. Update README.md
Add the content from `README_APPENDIX.md` to your existing project README.

### 6. Test Integration
1. Restart Blender and reload your add-on
2. Create/import O'Neill cylinder segments
3. Use "Align Cylinders" and "Unwrap to Flat"
4. Select unwrapped objects
5. Use "Apply Archipelago" with different presets
6. Test "Rewrap to Cylinders"

## Preset Configurations

### Available Presets:
- **Dense Archipelago**: Many small islands, perfect for dssstrkl settlements
- **Sparse Islands**: Few large islands, ideal for major settlements
- **Game Optimized**: Balanced for real-time rendering performance
- **dssstrkl Habitat**: Tailored for alien raptor civilization needs

## Troubleshooting

### Asset Not Found
```bash
# Verify asset file exists
ls -la "/Documents/Project/oneill terrain generator/src/assets/geometry_nodes/"
# Should show: archipelago_terrain_generator.blend
```

### Import Errors
- Ensure all Python files are in correct locations
- Check that `__init__.py` files exist in operator/utils directories
- Restart Blender after copying files

### Performance Issues
- Use "Game Optimized" preset for better performance
- Ensure input mesh has adequate subdivision (100k+ vertices recommended)
- Apply to one object at a time for testing

## File Locations After Integration
```
/Documents/Project/oneill terrain generator/
├── src/
│   ├── oneill_heightmap_terrain.py (UPDATED - main add-on)
│   ├── assets/
│   │   ├── geometry_nodes/
│   │   │   └── archipelago_terrain_generator.blend (NEW)
│   │   └── presets/
│   │       └── archipelago_presets.json (NEW)
│   ├── operators/
│   │   └── archipelago_operators.py (NEW)
│   └── utils/
│       └── asset_manager.py (NEW)
├── docs/
│   ├── archipelago_generator_guide.md (NEW)
│   └── integration_instructions.md (NEW)
└── README.md (UPDATED with archipelago info)
```

Ready to enhance your O'Neill space habitat development! 🚀🌊🏝️

# Heightmap Painting Module - Integration Instructions

## 📦 Integration Package Overview

This document provides complete instructions for integrating the **Heightmap Painting Module** into the existing `oneill_heightmap_terrain.py` add-on.

---

## 🎯 Integration Goal

**Transform step 4 "Generate Terrain"** from procedural-only to include **manual biome painting** capabilities while maintaining full compatibility with the existing workflow.

### **Enhanced Workflow**
```
Before Integration:
4. Generate Terrain → Procedural noise only

After Integration:  
4. Paint Terrain Biomes → Manual biome painting + procedural options
```

---

## 📋 Pre-Integration Checklist

### **Prerequisites**
- [ ] Existing `oneill_heightmap_terrain.py` add-on functional
- [ ] Step 3 "Create Heightmaps" working correctly
- [ ] Step 5 "Rewrap to Cylinders" working correctly
- [ ] Backup of existing add-on file created

---

## 🔧 Integration Steps

### **Step 1: Add Operator Classes**

Add these four operator classes to your existing `oneill_heightmap_terrain.py`:

```python
# Add after existing operator imports
from bpy.types import Operator, Panel
from bpy.props import EnumProperty, BoolProperty

class ONEILL_OT_start_heightmap_painting(Operator):
    """Start terrain biome painting on existing heightmaps"""
    bl_idname = "oneill.start_heightmap_painting"
    bl_label = "Start Terrain Painting"
    bl_description = "Begin painting biome assignments on heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find objects with heightmaps (created by existing step 3)
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects with heightmaps first. Run 'Create Heightmaps' if needed.")
            return {'CANCELLED'}
        
        # Set up painting mode
        context.scene.oneill_painting_mode = True
        context.scene.oneill_current_biome = 'MOUNTAINS'
        
        # Switch to image editor for heightmap painting
        self.setup_painting_workspace(context, flat_objects[0])
        
        self.report({'INFO'}, f"Started biome painting on {len(flat_objects)} heightmaps")
        return {'FINISHED'}
    
    def setup_painting_workspace(self, context, flat_obj):
        """Set up workspace for heightmap painting"""
        heightmap_name = flat_obj.get("heightmap_image")
        heightmap = bpy.data.images.get(heightmap_name)
        
        if heightmap:
            # Find image editor and set the heightmap
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = heightmap
                            space.mode = 'PAINT'
                            return

class ONEILL_OT_select_painting_biome(Operator):
    """Select which biome to paint on heightmaps"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_description = "Choose biome type for painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome: EnumProperty(
        name="Biome Type",
        items=[
            ('MOUNTAINS', "Mountains", "Paint mountain terrain"),
            ('CANYONS', "Canyons", "Paint canyon terrain"),
            ('HILLS', "Hills", "Paint rolling hills"),
            ('DESERT', "Desert", "Paint desert terrain"),
            ('OCEAN', "Ocean", "Paint ocean/water areas"),
        ],
        default='MOUNTAINS'
    )
    
    def execute(self, context):
        context.scene.oneill_current_biome = self.biome
        
        # Set brush color based on biome for visual feedback
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),  # Gray
            'CANYONS': (0.8, 0.4, 0.2),    # Orange/Brown
            'HILLS': (0.3, 0.6, 0.3),      # Green
            'DESERT': (0.9, 0.8, 0.4),     # Yellow
            'OCEAN': (0.2, 0.4, 0.8),      # Blue
        }
        
        if self.biome in biome_colors:
            color = biome_colors[self.biome]
            # Set paint brush color for visual feedback
            if hasattr(context.tool_settings, 'image_paint'):
                brush = context.tool_settings.image_paint.brush
                if brush:
                    brush.color = color
        
        self.report({'INFO'}, f"Selected {self.biome.title()} for painting")
        return {'FINISHED'}

class ONEILL_OT_finish_heightmap_painting(Operator):
    """Finish terrain painting and prepare for rewrap"""
    bl_idname = "oneill.finish_heightmap_painting"
    bl_label = "Finish Terrain Painting"
    bl_description = "Complete painting and prepare heightmaps for rewrap"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find painted heightmaps
        flat_objects = [obj for obj in bpy.data.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        painted_count = 0
        for flat_obj in flat_objects:
            heightmap_name = flat_obj.get("heightmap_image")
            heightmap = bpy.data.images.get(heightmap_name)
            
            if heightmap:
                # Ensure heightmap is saved/updated
                heightmap.update()
                painted_count += 1
        
        # Exit painting mode
        context.scene.oneill_painting_mode = False
        
        self.report({'INFO'}, f"Finished painting {painted_count} heightmaps. Ready for rewrap.")
        return {'FINISHED'}
```

### **Step 2: Add Scene Properties**

Add these properties after your existing property definitions:

```python
# Add to your property registration section
bpy.types.Scene.oneill_painting_mode = BoolProperty(
    name="Painting Mode Active",
    default=False
)

bpy.types.Scene.oneill_current_biome = EnumProperty(
    name="Current Biome",
    items=[
        ('MOUNTAINS', "Mountains", ""),
        ('CANYONS', "Canyons", ""),
        ('HILLS', "Hills", ""),
        ('DESERT', "Desert", ""),
        ('OCEAN', "Ocean", ""),
    ],
    default='MOUNTAINS'
)
```

### **Step 3: Add UI Panel Integration**

Add this panel class or integrate into your existing terrain panel:

```python
class ONEILL_PT_heightmap_painting_integration(Panel):
    """Heightmap Painting Integration Panel"""
    bl_label = "Terrain Painting"
    bl_idname = "ONEILL_PT_heightmap_painting_integration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill Terrain"  # Same category as your existing panel
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Status
        if hasattr(scene, 'oneill_painting_mode') and scene.oneill_painting_mode:
            layout.alert = True
            layout.label(text="🎨 PAINTING MODE ACTIVE")
        else:
            layout.label(text="4. Paint Terrain Biomes")
        
        layout.separator()
        
        # Check for objects with heightmaps
        flat_objects = [obj for obj in bpy.data.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if flat_objects:
            layout.label(text=f"Ready: {len(flat_objects)} heightmaps", icon='IMAGE_DATA')
        else:
            layout.label(text="Run 'Create Heightmaps' first", icon='ERROR')
            return
        
        # Main painting controls
        if not (hasattr(scene, 'oneill_painting_mode') and scene.oneill_painting_mode):
            col = layout.column()
            col.scale_y = 1.3
            col.operator("oneill.start_heightmap_painting", 
                        text="Start Terrain Painting", 
                        icon='BRUSH_DATA')
        else:
            # Biome selection
            box = layout.box()
            box.label(text="Select Biome:", icon='MATERIAL')
            
            current_biome = getattr(scene, 'oneill_current_biome', 'MOUNTAINS')
            box.label(text=f"Current: {current_biome.title()}")
            
            col = box.column(align=True)
            
            op = col.operator("oneill.select_painting_biome", text="🏔️ Mountains")
            op.biome = 'MOUNTAINS'
            
            op = col.operator("oneill.select_painting_biome", text="🏜️ Canyons")
            op.biome = 'CANYONS'
            
            op = col.operator("oneill.select_painting_biome", text="🏞️ Hills")
            op.biome = 'HILLS'
            
            op = col.operator("oneill.select_painting_biome", text="🌵 Desert")
            op.biome = 'DESERT'
            
            op = col.operator("oneill.select_painting_biome", text="🌊 Ocean")
            op.biome = 'OCEAN'
            
            layout.separator()
            
            # Finish painting
            col = layout.column()
            col.scale_y = 1.3
            col.operator("oneill.finish_heightmap_painting", 
                        text="Finish Painting", 
                        icon='CHECKMARK')
```

### **Step 4: Update Registration**

Add the new classes to your existing `classes` list:

```python
classes = [
    # ... your existing classes ...
    ONEILL_OT_start_heightmap_painting,
    ONEILL_OT_select_painting_biome, 
    ONEILL_OT_finish_heightmap_painting,
    ONEILL_PT_heightmap_painting_integration,
]
```

---

## 🧪 Testing Integration

### **Test Workflow**
1. **Load O'Neill cylinder objects**
2. **Run steps 1-3** of existing workflow:
   - Align Cylinders
   - Unwrap to Flat  
   - Create Heightmaps
3. **Select flat objects with heightmaps**
4. **Test new painting functionality**:
   - Click "Start Terrain Painting"
   - Select different biomes
   - Test painting workflow
   - Click "Finish Painting"
5. **Continue to step 5** (Rewrap to Cylinders)

### **Validation Checklist**
- [ ] Painting mode activates correctly
- [ ] Biome selection changes brush colors
- [ ] Heightmaps available for painting
- [ ] Painting mode exits cleanly
- [ ] Rewrap step works with painted heightmaps

---

## 🔧 Alternative Integration Methods

### **Option A: Separate Panel (Recommended)**
- Add as new panel in same category
- Keeps existing functionality intact
- Easy to disable if needed

### **Option B: Integrate into Existing Panel**
- Add painting controls to existing terrain panel
- Modify existing step 4 section
- More compact interface

### **Option C: Replace Existing Step 4**
- Completely replace procedural generation
- Use painting as primary method
- Keep procedural as secondary option

---

## 🚨 Troubleshooting

### **Common Issues**

**Issue**: Operators not appearing
**Solution**: Check registration in `classes` list

**Issue**: Properties not found
**Solution**: Verify scene property registration

**Issue**: Panel not showing
**Solution**: Check `bl_category` matches existing panel

**Issue**: Heightmaps not detected
**Solution**: Verify step 3 "Create Heightmaps" working correctly

### **Rollback Plan**
If integration causes issues:
1. Remove new operator classes
2. Remove new scene properties
3. Remove new panel class
4. Remove from registration
5. Restart Blender

---

## 📖 User Documentation Updates

### **Update User Guide**
```
Enhanced Workflow:
1. Align Cylinders
2. Unwrap to Flat
3. Create Heightmaps
4. Paint Terrain Biomes (NEW!)
   - Start Terrain Painting
   - Select biomes (🏔️🏜️🏞️🌵🌊)
   - Paint on heightmaps
   - Finish Painting
5. Rewrap to Cylinders
```

### **Add to Features List**
- Manual biome painting on heightmaps
- 5 biome types with visual feedback
- Professional painting workflow
- Compatible with existing procedural options

---

## 🏆 Integration Success Criteria

### **Functional Requirements**
- [ ] All 4 operators working
- [ ] UI panel appears correctly
- [ ] Painting mode state management working
- [ ] Biome selection functional
- [ ] Compatible with existing workflow

### **Quality Requirements**
- [ ] No conflicts with existing functionality
- [ ] Error handling appropriate
- [ ] User feedback clear and helpful
- [ ] Professional UI appearance
- [ ] Smooth workflow progression

---

## ✅ Post-Integration

### **Immediate Next Steps**
1. Test with real O'Neill cylinder scenes
2. Gather user feedback on painting workflow
3. Document any integration issues
4. Plan Phase 2B surface layer features
5. Consider additional biome types

### **Future Enhancements**
- Advanced brush controls
- Multi-layer painting system
- Real-time 3D preview
- Export enhancements for game engines

---

**Integration Status**: Ready for immediate deployment  
**Estimated Integration Time**: 30-60 minutes  
**Risk Level**: Low (non-destructive integration)

🎯 **Ready to transform your O'Neill add-on with professional terrain painting capabilities!**