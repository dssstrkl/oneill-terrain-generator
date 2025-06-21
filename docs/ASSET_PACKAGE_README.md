# O'Neill Archipelago Terrain Generator - Asset Package

📁 **Location**: `/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator`

## 🚀 Quick Copy Commands

### Option 1: Manual Copy (if you know your project path)
```bash
# Replace with your actual project path
YOUR_PROJECT="/path/to/your/oneill-terrain-generator"

# Copy assets
cp -r "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/assets" "$YOUR_PROJECT/src/"
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/operators/archipelago_operators.py" "$YOUR_PROJECT/src/operators/"
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/src/utils/asset_manager.py" "$YOUR_PROJECT/src/utils/"
cp "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/docs/"*.md "$YOUR_PROJECT/docs/"
```

### Option 2: Use Deployment Script
```bash
# Edit the script to set your project path
nano "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/deploy_assets.sh"
# Then run it
bash "/var/folders/m2/f7jff1ss6cbdwwhpc33t95880000gn/T/oneill_terrain_generator/deploy_assets.sh"
```

## 📦 What's Included

### Core Asset Files:
- **`archipelago_terrain_generator.blend`** (1.2MB) - Main geometry node asset
- **`archipelago_metadata.json`** - Asset information
- **`archipelago_presets.json`** - Terrain configuration presets

### Python Integration:
- **`archipelago_operators.py`** - Blender operators for UI
- **`asset_manager.py`** - Asset loading utilities

### Documentation:
- **`archipelago_generator_guide.md`** - User guide
- **`integration_instructions.md`** - Developer integration steps

## 🎯 Integration Steps

1. **Copy files** to your project (use commands above)
2. **Follow integration guide**: `docs/integration_instructions.md`
3. **Update your main add-on** to include new operators
4. **Test in Blender** with your O'Neill cylinders
5. **Commit to Git** to save your enhanced add-on

## 🌊 Ready for O'Neill Archipelago Generation! 🏝️
