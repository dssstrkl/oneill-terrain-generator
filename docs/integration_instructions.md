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
