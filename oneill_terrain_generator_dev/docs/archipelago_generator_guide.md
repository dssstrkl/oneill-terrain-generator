# Archipelago Terrain Generator - Asset Documentation

## Overview
The Archipelago Terrain Generator is a modular geometry node asset for creating realistic island chains and coastal terrain within O'Neill cylinder interiors.

## File Structure
```
src/
├── assets/
│   ├── geometry_nodes/
│   │   ├── archipelago_terrain_generator.blend    # Main asset file
│   │   └── archipelago_metadata.json             # Asset metadata
│   └── presets/
│       └── archipelago_presets.json              # Configuration presets
├── operators/
│   └── archipelago_operators.py                  # Blender operators
└── utils/
    └── asset_manager.py                          # Asset loading utilities
```

## Integration with Existing Add-on

### 1. Add to Main Add-on File
Add these imports to your `oneill_heightmap_terrain.py`:

```python
from .operators.archipelago_operators import (
    ONEILL_OT_ApplyArchipelago,
    ONEILL_OT_LoadArchipelagoAsset
)
```

### 2. Update Registration
Add the operators to your classes list:

```python
classes = [
    # ... existing classes ...
    ONEILL_OT_ApplyArchipelago,
    ONEILL_OT_LoadArchipelagoAsset,
]
```

### 3. Add UI Integration
Add to your terrain panel:

```python
class ONEILL_PT_terrain_panel(bpy.types.Panel):
    # ... existing code ...
    
    def draw(self, context):
        layout = self.layout
        
        # ... existing terrain options ...
        
        # Add archipelago section
        box = layout.box()
        box.label(text="Archipelago Terrain:", icon='WORLD')
        box.operator("oneill.apply_archipelago", text="Apply Archipelago")
        box.operator("oneill.load_archipelago_asset", text="Load Asset")
```

## Usage Workflow

### Current O'Neill Workflow Enhancement:
1. **Align Cylinders** → `oneill.align_cylinders`
2. **Unwrap to Flat** → `oneill.unwrap_to_flat`  
3. **Choose Terrain Type:**
   - **Heightmap Painting** → `oneill.create_heightmaps`
   - **Archipelago Generation** → `oneill.apply_archipelago` ✨ NEW
4. **Rewrap to Cylinders** → `oneill.rewrap_to_cylinder`

### Archipelago-Specific Workflow:
1. Select unwrapped flat objects (from step 2)
2. Click "Apply Archipelago" button
3. Choose preset: Dense/Sparse/Game Optimized
4. Proceed to rewrap step

## Technical Details

### Asset Requirements:
- **Blender Version**: 3.0+
- **Input Geometry**: High-subdivision mesh (256x256+ recommended)
- **Memory**: ~100MB for high-resolution generation
- **Export Compatible**: Yes (game engines)

### Presets Available:
- **Dense Archipelago**: Many small islands, detailed coastlines
- **Sparse Islands**: Few large islands, simple coastlines  
- **Game Optimized**: Balanced performance for real-time rendering

### Performance Notes:
- Use subdivision before archipelago for best results
- 513x513 vertex grids provide excellent detail
- Compatible with LOD generation for games
- Optimized for Unreal Engine export

## Best Practices

### For Game Development:
1. Apply archipelago to highest LOD level first
2. Generate lower LOD levels using decimation
3. Use collision mesh generation for physics
4. Bake textures for performance optimization

### For O'Neill Cylinders:
1. Apply to unwrapped cylinder sections
2. Ensure consistent scale between sections
3. Consider biome transitions at section boundaries
4. Integrate with existing POI/settlement systems

## Troubleshooting

### Common Issues:
- **"Asset not found"**: Ensure archipelago_terrain_generator.blend is in assets/geometry_nodes/
- **Low detail**: Increase base mesh subdivision before applying
- **Performance issues**: Use lower preset or reduce base mesh resolution
- **Export problems**: Apply modifier before exporting to game engine

### Asset Validation:
```python
# Check if asset is properly loaded
if "ONeill_Archipelago_Terrain_Generator" in bpy.data.node_groups:
    print("✅ Archipelago asset loaded successfully")
else:
    print("❌ Archipelago asset not found")
```

## Future Enhancements
- Biome-specific island generation
- Integration with water level systems
- Automatic settlement placement on islands
- Real-time parameter adjustment
- Multi-resolution asset variants
