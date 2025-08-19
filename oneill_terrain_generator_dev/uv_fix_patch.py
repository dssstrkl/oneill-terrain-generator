# PHASE 2: IMPLEMENT UV MAPPING FIX IN START TERRAIN PAINTING METHOD

# Add UV mapping fix to the apply_session_42_auto_preview method
# This ensures UV mapping is corrected when auto-preview activates

def apply_session_42_auto_preview_with_uv_fix(self, flat_objects, canvas):
    """Apply SESSION 42 auto-preview with UV mapping fix integrated"""
    print(f"Automatically applying SESSION 42 auto-preview to {len(flat_objects)} objects...")
    
    # FIRST: Fix UV mapping using SESSION 42 blueprint
    self.fix_unified_canvas_uv_mapping(flat_objects)
    
    # Get or create the working node group
    working_node_group = self.get_or_create_session_42_node_group()
    if not working_node_group:
        print("❌ Failed to get/create working node group")
        return False
    
    # Connect canvas to node group
    self.connect_canvas_to_node_group(working_node_group, canvas)
    
    # Apply working modifier stack to all flat objects
    applied_count = 0
    for obj in flat_objects:
        try:
            # Remove existing modifiers
            existing_mods = [mod for mod in obj.modifiers if mod.name in ["Preview_Subdivision", "Unified_Terrain"]]
            for mod in existing_mods:
                obj.modifiers.remove(mod)
            
            # Apply SESSION 42 working modifier stack
            
            # 1. Preview_Subdivision (SUBSURF) - levels=2
            subsurf = obj.modifiers.new(name="Preview_Subdivision", type='SUBSURF')
            subsurf.levels = 2
            
            # 2. Unified_Terrain (NODES) - working node group
            geo_nodes = obj.modifiers.new(name="Unified_Terrain", type='NODES')
            geo_nodes.node_group = working_node_group
            
            applied_count += 1
            print(f"✅ Applied SESSION 42 modifiers to {obj.name}")
            
        except Exception as e:
            print(f"❌ Failed to apply modifiers to {obj.name}: {e}")
    
    print(f"✅ SESSION 42 auto-preview applied to {applied_count}/{len(flat_objects)} objects")
    return applied_count > 0

def fix_unified_canvas_uv_mapping(self, flat_objects):
    """Fix UV mapping using exact SESSION 42 blueprint"""
    print(f"\n=== FIXING UV MAPPING USING SESSION 42 BLUEPRINT ===")
    
    # Sort objects by X position to match SESSION 42 layout
    sorted_objects = sorted(flat_objects, key=lambda obj: obj.location.x)
    total_objects = len(sorted_objects)
    
    print(f"Fixing UV mapping for {total_objects} objects...")
    
    for i, obj in enumerate(sorted_objects):
        try:
            mesh = obj.data
            if not mesh.uv_layers:
                print(f"⚠️ No UV layer found on {obj.name}")
                continue
            
            uv_layer = mesh.uv_layers['UVMap']
            
            # Calculate SESSION 42 UV ranges
            # Each object gets exactly 1/total_objects of the canvas width
            u_start = i / total_objects
            u_end = (i + 1) / total_objects
            v_start = 0.0
            v_end = 1.0
            
            print(f"  Object {i+1} ({obj.name}): U=[{u_start:.6f}, {u_end:.6f}]")
            
            # Remap all UV coordinates to the correct canvas portion
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]
                    vertex = mesh.vertices[loop.vertex_index]
                    
                    # Get current UV (0-1 range within object)
                    current_uv = uv_layer.data[loop_index].uv
                    local_u = current_uv[0]  # Already 0-1 from temporary mapping
                    local_v = current_uv[1]  # Already 0-1 from temporary mapping
                    
                    # Map to correct portion of unified canvas
                    global_u = u_start + (local_u * (u_end - u_start))
                    global_v = v_start + (local_v * (v_end - v_start))
                    
                    uv_layer.data[loop_index].uv = (global_u, global_v)
            
            # Update mesh
            mesh.update()
            print(f"✅ Fixed UV mapping for {obj.name} (portion {i+1}/{total_objects})")
            
        except Exception as e:
            print(f"❌ Failed to fix UV mapping for {obj.name}: {e}")
    
    print(f"✅ UV mapping fix complete - SESSION 42 unified canvas layout applied")

# Create patched methods to inject into ONEILL_OT_StartTerrainPainting
print("Creating UV fix methods for injection...")
print("These will be added to the operator to fix unified canvas UV mapping")
