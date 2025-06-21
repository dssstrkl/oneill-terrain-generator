# O'Neill Terrain Generator - Conversation Starter

## Quick Context for AI Assistants:
- **Project Goal**: Blender add-on for O'Neill cylinder interior terrain using heightmap workflow
- **Current Status**: Fully functional 6-step workflow with minor issues
- **Last Updated**: June 21, 2025
- **Working Version**: `src/oneill_heightmap_terrain.py`

## 🚨 CRITICAL RULES - READ FIRST:
1. **NEVER start from scratch** - always use existing working code
2. **Check `src/assets/`** for working geometry nodes and presets
3. **Fix specific issues only** - don't rebuild working systems
4. **Read this entire document** before any development
5. **Use working assets** from project folder instead of creating new

## Current Workflow State:
✅ **Working**: Align, Unwrap, Create Heightmaps, Setup Geometry Nodes, Generate Terrain, Rewrap  
⚠️ **Minor Issue**: Update Scale button visibility  
⚠️ **Minor Issue**: Terrain displacement not visible (geometry nodes UV mapping)

## Working Assets to Use (ALWAYS CHECK THESE FIRST):
- `src/assets/geometry_nodes/` - Proven terrain displacement nodes
- `src/assets/presets/` - Working configuration presets  
- `src/previous/` - Previous working versions
- `docs/archipelago_generator_guide.md` - Implementation reference
- `src/oneill_heightmap_terrain.py` - Current main implementation

## Key Project Context:
- **Worldbuilding**: dssstrkl alien civilization fleeing in O'Neill cylinder space ark
- **Technology**: Atlantean 4D tesseract power, bone-stone materials, antigravity
- **Game Pipeline**: Blender terrain generation → Unreal Engine integration
- **Workflow**: Heightmap-based like True Terrain, preserves original geometry exactly

## Development History Summary:
- ✅ **Resolved**: UI visibility issues, geometry nodes socket errors, heightmap workflow
- ✅ **Working**: Complete 6-step terrain generation pipeline
- ✅ **Enhanced**: Visual progress indicators, real-time scale controls
- ❌ **Current Issues**: Terrain visibility and UI button missing

## Next Steps (Current Issues to Resolve):
1. **Import working geometry nodes** from `src/assets/geometry_nodes/` instead of using created nodes
2. **Fix UV coordinate mapping** for terrain visibility in viewport
3. **Debug update scale button** registration issue
4. **Test complete workflow** with working assets

## Critical Lesson Learned:
**DO NOT create geometry nodes from scratch** - we lost working terrain displacement by rebuilding instead of using proven assets from `src/assets/geometry_nodes/`. Always import and adapt existing working components.

## For Full Context, Read:
- `docs/project_overview.md` - Complete project vision and goals
- `docs/development_summary.txt` - Technical implementation history  
- `docs/current_status.md` - Detailed status of known issues
- `docs/assets_guide.md` - Guide to using existing working components

## Quick Start for AI Assistants:
1. Read this document completely
2. Check `docs/current_status.md` for latest issue details
3. Review `src/assets/` for working components to use
4. Only fix specific issues - don't rebuild working systems
5. Update documentation when issues are resolved

---
*This document ensures conversation continuity and prevents rebuilding working systems from scratch.*