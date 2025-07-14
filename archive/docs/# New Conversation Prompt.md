# New Conversation Prompt

**O'Neill Terrain Generator Development Session**

GitHub Project: https://github.com/dssstrkl/oneill-terrain-generator

**Instructions:**
1. Check GitHub repo main branch for latest code
2. Base all development on `/src/oneill_heightmap_terrain.py` (main script)
3. Reference `/src/assets/geometry_nodes/` for archipelago terrain assets
4. Review docs, especially troubleshooting patterns in existing documentation
5. Keep responses concise due to conversation limits

**Key Context:**
- Blender add-on for O'Neill cylinder interior terrain using heightmap workflow
- 5-step process: Align → Unwrap → Create Heightmaps → Edit Terrain → Rewrap
- Preserves original geometry exactly while applying terrain displacement
- Built for dssstrkl space habitat game development pipeline

**Common Issues (from troubleshooting docs):**
- UI panel visibility problems (use custom tab, avoid registration conflicts)
- Geometry nodes path detection (requires saved .blend file)
- Heightmap displacement calculation edge cases
- Performance with high-resolution heightmaps

Always check troubleshooting docs first before suggesting solutions that have been tried before.