"""
O'Neill Terrain Generator - SESSION 40 FUNCTIONALITY RESTORED
INTEGRATED: Session 40 unified terrain system with auto-preview
BASE: Session 23 script with Session 40 working code integrated
Applied working unified system from live Blender scene
"""

import bpy
import bmesh
import mathutils
import math
import random
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty

# ========================= SESSION 55 AUTO-PREVIEW SYSTEM INTEGRATION =========================

class WorkingAutoPreviewSystem:
    """SESSION 42 working auto-preview system integration - PHASE 2"""
    
    def __init__(self):
        self.auto_preview_active = False
        self.monitored_objects = []
    
    def load_working_components(self):
        """Load the proven working node group and canvas from SESSION 42"""
        working_asset_path = '/Users/dssstrkl/Documents/Projects/oneill terrain generator/oneill_terrain_generator_dev/assets/working_auto_preview_system.blend'
        
        try:
            # Append the working node group from the asset file
            with bpy.data.libraries.load(working_asset_path, link=False) as (data_from, data_to):
                # Load the working node group
                if "Unified_Multi_Biome_Terrain.001" in data_from.node_groups:
                    data_to.node_groups = ["Unified_Multi_Biome_Terrain.001"]
                    print("✅ Loaded working node group from SESSION 42")
                else:
                    print("❌ Working node group not found in asset file")
                    return False
                
                # Load the canvas if it exists
                if "oneill_terrain_canvas" in data_from.images:
                    data_to.images = ["oneill_terrain_canvas"]
                    print("✅ Loaded working canvas from SESSION 42")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load working components: {e}")
            return False
    
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
    
    def apply_working_modifier_stack(self, flat_objects):
        """Apply SESSION 42 proven modifier stack to flat objects"""
        print(f"Applying working modifier stack to {len(flat_objects)} objects...")
        
        # Ensure working node group is available
        working_node_group = bpy.data.node_groups.get("Unified_Multi_Biome_Terrain.001")
        if not working_node_group:
            if not self.load_working_components():
                print("❌ Cannot load working components")
                return False
            working_node_group = bpy.data.node_groups.get("Unified_Multi_Biome_Terrain.001")
        
        if not working_node_group:
            print("❌ Working node group still not available")
            return False
        
        # Get or create canvas
        canvas = bpy.data.images.get("oneill_terrain_canvas")
        if not canvas:
            print("❌ Canvas not found")
            return False
        
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
                
                # Connect canvas using SESSION 42 method
                self.connect_canvas_to_node_group(working_node_group, canvas)
                
                applied_count += 1
                print(f"✅ Applied working modifiers to {obj.name}")
                
            except Exception as e:
                print(f"❌ Failed to apply modifiers to {obj.name}: {e}")
        
        print(f"✅ Applied working modifier stack to {applied_count}/{len(flat_objects)} objects")
        return applied_count > 0
    
    def connect_canvas_to_node_group(self, node_group, canvas):
        """Connect canvas using SESSION 42 proven method"""
        img_tex_node = node_group.nodes.get("Unified_Canvas_Sampler")
        if img_tex_node and 'Image' in img_tex_node.inputs:
            img_tex_node.inputs['Image'].default_value = canvas
            print(f"✅ Connected canvas to {img_tex_node.name}")
            return True
        else:
            print("❌ Image Texture node or Image input not found")
            return False
    
    def monitor_canvas_changes(self):
        """Monitor canvas using CORRECT evaluated mesh approach from SESSION 54"""
        if not self.auto_preview_active:
            return False
        
        displacement_detected = False
        for obj in self.monitored_objects:
            try:
                # CORRECT method: Use evaluated mesh, not base mesh
                depsgraph = bpy.context.evaluated_depsgraph_get()
                eval_obj = obj.evaluated_get(depsgraph)
                
                if eval_obj.data.vertices:
                    z_coords = [v.co.z for v in eval_obj.data.vertices]
                    displacement_range = max(z_coords) - min(z_coords)
                    
                    if displacement_range > 0.001:
                        displacement_detected = True
                        print(f"✅ Displacement detected on {obj.name}: {displacement_range:.3f}")
                        break
                        
            except Exception as e:
                print(f"⚠️ Monitoring error for {obj.name}: {e}")
        
        return displacement_detected
    
    def setup_auto_preview_monitoring(self, flat_objects):
        """Set up real-time canvas-to-terrain monitoring"""
        self.monitored_objects = flat_objects
        self.auto_preview_active = True
        print(f"✅ Auto-preview monitoring enabled for {len(flat_objects)} objects")
        return True

class UnifiedCanvasTerrainSystem:
    """Pure unified canvas-to-terrain system - SESSION 55 INTEGRATION"""
    
    def __init__(self):
        self.auto_preview_system = WorkingAutoPreviewSystem()
    
    def create_unified_multi_biome_system(self):
        """Create the EXACT SESSION 42 working node group - 11 nodes, 10 connections"""
        print("Creating SESSION 42 working node group...")
        
        # Check if node group already exists
        node_group_name = "Unified_Multi_Biome_Terrain.001"
        if node_group_name in bpy.data.node_groups:
            print(f"✅ Working node group {node_group_name} already exists")
            return bpy.data.node_groups[node_group_name]
        
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create nodes in exact order from SESSION 42
        group_input = node_group.nodes.new('NodeGroupInput')
        group_input.name = "Group Input"
        group_input.location = (-800.0, 0.0)
        
        group_output = node_group.nodes.new('NodeGroupOutput')
        group_output.name = "Group Output"
        group_output.location = (600.0, 0.0)
        
        named_attr = node_group.nodes.new('GeometryNodeInputNamedAttribute')
        named_attr.name = "Named Attribute"
        named_attr.location = (-700.0, -200.0)
        named_attr.data_type = 'FLOAT_VECTOR'
        named_attr.inputs['Name'].default_value = 'UVMap'
        
        canvas_sampler = node_group.nodes.new('GeometryNodeImageTexture')
        canvas_sampler.name = "Unified_Canvas_Sampler"
        canvas_sampler.location = (-500.0, -200.0)
        
        separate_xyz = node_group.nodes.new('ShaderNodeSeparateXYZ')
        separate_xyz.name = "Separate XYZ"
        separate_xyz.location = (-300.0, -200.0)
        
        color_ramp = node_group.nodes.new('ShaderNodeValToRGB')
        color_ramp.name = "Color Ramp"
        color_ramp.location = (-100.0, -200.0)
        
        noise_texture = node_group.nodes.new('ShaderNodeTexNoise')
        noise_texture.name = "Noise Texture"
        noise_texture.location = (-300.0, 100.0)
        
        position = node_group.nodes.new('GeometryNodeInputPosition')
        position.name = "Position"
        position.location = (-300.0, 300.0)
        
        math = node_group.nodes.new('ShaderNodeMath')
        math.name = "Math"
        math.location = (0.0, 0.0)
        math.operation = 'MULTIPLY'
        
        combine_xyz = node_group.nodes.new('ShaderNodeCombineXYZ')
        combine_xyz.name = "Combine XYZ"
        combine_xyz.location = (200.0, 100.0)
        
        set_position = node_group.nodes.new('GeometryNodeSetPosition')
        set_position.name = "Set Position"
        set_position.location = (400.0, 0.0)
        
        # Create exact links from SESSION 42
        links = node_group.links
        
        # Link sequence from working system
        links.new(named_attr.outputs['Attribute'], canvas_sampler.inputs['Vector'])
        links.new(canvas_sampler.outputs['Color'], separate_xyz.inputs['Vector'])
        links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
        links.new(position.outputs['Position'], noise_texture.inputs['Vector'])
        links.new(noise_texture.outputs['Fac'], math.inputs[0])  # Value
        links.new(math.outputs['Value'], combine_xyz.inputs['Z'])
        links.new(group_input.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(combine_xyz.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], group_output.inputs['Geometry'])
        links.new(color_ramp.outputs['Color'], math.inputs[1])  # Value_001
        
        print(f"✅ Created SESSION 42 working node group: {node_group_name}")
        print(f"   - {len(node_group.nodes)} nodes")
        print(f"   - {len(node_group.links)} links")
        
        return node_group
    
    def apply_unified_system_to_objects(self, objects):
        """Apply SESSION 55 working auto-preview system to flat objects"""
        print(f"Applying SESSION 55 working auto-preview system to {len(objects)} objects...")
        
        # Use the proven working auto-preview system from SESSION 42
        success = self.auto_preview_system.apply_working_modifier_stack(objects)
        
        if success:
            # Set up monitoring for auto-preview functionality
            self.auto_preview_system.setup_auto_preview_monitoring(objects)
            print("✅ SESSION 55 auto-preview system applied successfully")
        else:
            print("❌ Failed to apply SESSION 55 auto-preview system")
        
        return success

# ========================= CONSTANTS =========================

BIOME_TYPES = [
    ('ARCHIPELAGO', '🏝️ Archipelago', 'Island chains with water features'),
    ('MOUNTAINS', '🏔️ Mountains', 'Rocky peaks and cliff formations'),
    ('CANYONS', '🏜️ Canyons', 'Deep valleys and river channels'), 
    ('HILLS', '🏞️ Hills', 'Gentle rolling landscape'),
    ('DESERT', '🌵 Desert', 'Sand dunes and rocky formations'),
    ('OCEAN', '🌊 Ocean', 'Underwater terrain and depths'),
]

def get_biome_display_name(biome_enum):
    for enum_val, display_name, description in BIOME_TYPES:
        if enum_val == biome_enum:
            return display_name
    return biome_enum

# ========================= PROPERTIES =========================

class OneillProperties(PropertyGroup):
    alignment_axis: EnumProperty(
        name="Alignment Axis",
        items=[('X', 'X-Axis', ''), ('Y', 'Y-Axis', ''), ('Z', 'Z-Axis', '')],
        default='X'
    )
    
    subdivision_levels: IntProperty(
        name="Subdivision Levels",
        description="PERFORMANCE WARNING: Level 3+ = 64x more vertices! Use 1-2 for safety.",
        default=1,
        min=0,
        max=3
    )
    
    heightmap_resolution: EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', '512x512', ''),
            ('1024', '1024x1024', ''),
            ('2048', '2048x2048', ''),
            ('4096', '4096x4096', '')
        ],
        default='1024'
    )
    
    terrain_scale: FloatProperty(
        name="Terrain Scale",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    noise_scale: FloatProperty(
        name="Noise Scale",
        default=5.0,
        min=0.1,
        max=20.0
    )
    
    painting_mode: BoolProperty(
        name="Painting Mode",
        default=False
    )
    
    current_biome: EnumProperty(
        name="Current Biome",
        items=BIOME_TYPES,
        default='MOUNTAINS'
    )

# ========================= CORE OPERATORS =========================

class ONEILL_OT_AlignCylinders(Operator):
    """Align cylinders with perfect contiguous positioning"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_true_object_bounds(self, obj):
        """Get actual world-space bounds including transforms"""
        mesh = obj.data
        world_coords = [obj.matrix_world @ v.co for v in mesh.vertices]
        x_coords = [co.x for co in world_coords]
        return min(x_coords), max(x_coords)
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 cylinder objects")
            return {'CANCELLED'}
        
        axis_idx = ['X', 'Y', 'Z'].index(props.alignment_axis)
        selected_objects.sort(key=lambda obj: obj.location[axis_idx])

        # Store object properties for later use
        for obj in selected_objects:
            obj_min, obj_max = self.get_true_object_bounds(obj)
            obj_width = obj_max - obj_min
            cylinder_radius = (obj.dimensions.y / 2) / obj.scale.y
            
            obj["oneill_aligned"] = True
            obj["cylinder_radius"] = cylinder_radius
            obj["cylinder_length"] = obj_width
            obj["alignment_axis"] = props.alignment_axis
            
        # Create contiguous objects using true bounds
        first_obj = selected_objects[0]
        first_min, first_max = self.get_true_object_bounds(first_obj)
        running_position = first_max
        
        for i in range(1, len(selected_objects)):
            current = selected_objects[i]
            curr_min, curr_max = self.get_true_object_bounds(current)
            curr_width = curr_max - curr_min
            curr_center = (curr_min + curr_max) / 2
            
            # Position this object to touch the previous one exactly
            new_center_x = running_position + (curr_width / 2)
            offset = new_center_x - curr_center
            current.location[axis_idx] += offset
            
            # Update running position for next object
            running_position = new_center_x + (curr_width / 2)
        
        self.report({'INFO'}, f"Aligned {len(selected_objects)} cylinders contiguously")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(Operator):
    """Unwrap cylinders to flat objects"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects 
                          if obj.type == 'MESH' and obj.get("oneill_aligned")]
        
        if not selected_objects:
            self.report({'ERROR'}, "Select aligned cylinder objects")
            return {'CANCELLED'}
        
        unwrapped_count = 0
        for obj in selected_objects:
            try:
                unwrapped_obj = self.unwrap_cylinder_object(context, obj)
                if unwrapped_obj:
                    unwrapped_count += 1
                    obj.hide_viewport = True
            except Exception as e:
                print(f"Error unwrapping {obj.name}: {e}")
        
        self.report({'INFO'}, f"Unwrapped {unwrapped_count} objects")
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, context, obj):
        original_name = obj.name
        
        cylinder_radius = obj.get("cylinder_radius", 1.0)
        cylinder_length = obj.get("cylinder_length", 2.0)
        
        circumference = 2 * math.pi * cylinder_radius
        
        # Get center position for placement
        mesh = obj.data
        vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
        center_x = sum(v.x for v in vertices) / len(vertices)
        center_y = sum(v.y for v in vertices) / len(vertices)
        segments_x = max(20, int(cylinder_length * 10))
        segments_y = max(20, int(circumference * 5))
        
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
        for vert in bm_new.verts:
            vert.co.x = vert.co.x * (cylinder_length / 2)
            vert.co.y = vert.co.y * (circumference / 2)
            vert.co.z = 0
        
        unwrapped_name = f"{original_name}_flat"
        unwrapped_mesh = bpy.data.meshes.new(unwrapped_name)
        bm_new.to_mesh(unwrapped_mesh)
        bm_new.free()
        
        # CRITICAL: Add UV mapping layer - TEMPORARY PLACEHOLDER
        # UV mapping will be fixed after all objects are created
        if not unwrapped_mesh.uv_layers:
            uv_layer = unwrapped_mesh.uv_layers.new(name='UVMap')
            
            # TEMPORARY: Use basic UV mapping that will be corrected later
            # This prevents errors during object creation
            for poly in unwrapped_mesh.polygons:
                for loop_index in poly.loop_indices:
                    loop = unwrapped_mesh.loops[loop_index]
                    vertex = unwrapped_mesh.vertices[loop.vertex_index]
                    
                    # Temporary UV mapping - will be corrected by fix_unified_canvas_uv_mapping
                    local_u = (vertex.co.x + cylinder_length/2) / cylinder_length  # 0-1 within object
                    v = (vertex.co.y + circumference/2) / circumference  # V remains 0-1
                    
                    uv_layer.data[loop_index].uv = (local_u, v)
            
            print(f"✅ Added temporary UV mapping to {unwrapped_name} (will be corrected later)")
        
        unwrapped_obj = bpy.data.objects.new(unwrapped_name, unwrapped_mesh)
        context.collection.objects.link(unwrapped_obj)
        
        # Maintain the same X position as the original object to preserve spacing
        unwrapped_obj.location.x = obj.location.x
        unwrapped_obj.location.y = center_y
        unwrapped_obj.location.z = 0
        
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = cylinder_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        
        return unwrapped_obj

class ONEILL_OT_CreateHeightmaps(Operator):
    """Create heightmaps for flat objects"""
    bl_idname = "oneill.create_heightmaps"
    bl_label = "Create Heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        selected_flat = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        if not selected_flat:
            all_flat = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if all_flat:
                flat_objects = all_flat
            else:
                self.report({'ERROR'}, "No flat objects found")
                return {'CANCELLED'}
        else:
            flat_objects = selected_flat
        
        resolution = int(props.heightmap_resolution)
        
        for obj in flat_objects:
            heightmap_name = f"{obj.name}_heightmap"
            
            if heightmap_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[heightmap_name])
            
            heightmap = bpy.data.images.new(
                heightmap_name,
                width=resolution,
                height=resolution,
                alpha=False,
                float_buffer=True
            )
            
            pixels = [0.5, 0.5, 0.5, 1.0] * (resolution * resolution)
            heightmap.pixels = pixels
            heightmap.update()
            
            obj["heightmap_image"] = heightmap_name
        
        self.report({'INFO'}, f"Created heightmaps for {len(flat_objects)} objects")
        return {'FINISHED'}

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with SESSION 42 auto-preview automatically enabled"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Start Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found. Complete steps 1-3 first.")
            return {'CANCELLED'}
        
        # CRITICAL: Apply Session 56 UV mapping fix BEFORE creating canvas
        self.apply_session_56_uv_mapping_fix(flat_objects)
            
        # Create combined canvas
        canvas_name = "oneill_terrain_canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
            
        canvas = bpy.data.images.new(
            canvas_name,
            width=2400,
            height=628,
            alpha=False
        )
        
        # Initialize canvas with BLACK color
        pixels = [0.0, 0.0, 0.0, 1.0] * (2400 * 628)
        canvas.pixels = pixels
        canvas.update()
        
        # Setup painting workspace
        self.setup_painting_workspace(context, canvas)
        
        # Set up canvas monitor to watch for painting activity
        # Auto-preview will activate ONLY when user starts painting
        self.setup_canvas_monitor(flat_objects, canvas)
        
        props.painting_mode = True
        
        self.report({'INFO'}, f"Painting mode active. Auto-preview will activate when you start painting.")
        return {'FINISHED'}
    
    def apply_session_56_uv_mapping_fix(self, flat_objects):
        """Apply Session 56 UV mapping fix - each object gets sequential canvas portion"""
        print("\n=== APPLYING SESSION 56 UV MAPPING FIX ===")
        
        # Sort objects by X position to match Session 56 approach
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
                
                # Calculate SESSION 56 UV ranges - each object gets exactly 1/total_objects of canvas width
                u_start = i / total_objects
                u_end = (i + 1) / total_objects
                u_width = u_end - u_start
                
                print(f"  Object {i+1} ({obj.name}): U=[{u_start:.6f}, {u_end:.6f}]")
                
                # Get the current UV range to normalize from
                current_us = [uv_layer.data[loop_index].uv[0] for loop_index in range(len(uv_layer.data))]
                current_u_min = min(current_us) if current_us else 0.0
                current_u_max = max(current_us) if current_us else 1.0
                current_u_range = current_u_max - current_u_min
                
                # Remap all UV coordinates to the correct canvas portion
                for poly in mesh.polygons:
                    for loop_index in poly.loop_indices:
                        current_uv = uv_layer.data[loop_index].uv
                        local_u = current_uv[0]  # Current U coordinate
                        local_v = current_uv[1]  # V coordinate (keep as-is)
                        
                        # Normalize the local U coordinate (0-1 within object)
                        if current_u_range > 0:
                            normalized_u = (local_u - current_u_min) / current_u_range
                        else:
                            normalized_u = 0.0
                        
                        # Map to correct portion of unified canvas
                        global_u = u_start + (normalized_u * u_width)
                        global_v = local_v  # V stays the same
                        
                        uv_layer.data[loop_index].uv = (global_u, global_v)
                
                # Update mesh
                mesh.update()
                print(f"✅ Fixed UV mapping for {obj.name} (portion {i+1}/{total_objects})")
                
            except Exception as e:
                print(f"❌ Failed to fix UV mapping for {obj.name}: {e}")
        
        print(f"✅ SESSION 56 UV mapping fix complete - unified canvas layout applied")
    
    def setup_canvas_monitor(self, flat_objects, canvas):
        """Set up canvas monitoring to detect when user starts painting"""
        # Store initial canvas state
        initial_pixels = list(canvas.pixels[:])
        auto_preview_activated = [False]  # Use list for mutable reference
        
        def check_canvas_for_painting():
            try:
                # Check if canvas has changed from initial black state
                current_pixels = canvas.pixels[:]
                
                # Look for any non-black pixels (painting detected)
                painting_detected = False
                for i in range(0, len(current_pixels), 4):
                    r, g, b = current_pixels[i:i+3]
                    if r > 0.01 or g > 0.01 or b > 0.01:  # Non-black pixel found
                        painting_detected = True
                        break
                
                if painting_detected and not auto_preview_activated[0]:
                    print("✅ Painting detected! Activating auto-preview system...")
                    auto_preview_activated[0] = True
                    
                    # NOW activate the auto-preview system
                    success = self.apply_session_42_auto_preview(flat_objects, canvas)
                    if success:
                        print("✅ Auto-preview system activated successfully")
                        # Force viewport update
                        bpy.context.view_layer.update()
                        for area in bpy.context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                    else:
                        print("❌ Auto-preview activation failed")
                    
                    return None  # Stop monitoring after activation
                
                # Continue monitoring if no painting detected yet
                return 0.5  # Check again in 0.5 seconds
                
            except Exception as e:
                print(f"❌ Canvas monitoring error: {e}")
                return None  # Stop monitoring on error
        
        # Start the canvas monitor
        bpy.app.timers.register(check_canvas_for_painting, first_interval=1.0)
        print("✅ Canvas monitor started - waiting for painting activity...")
    
    def apply_session_42_auto_preview(self, flat_objects, canvas):
        """Apply the exact SESSION 42 working auto-preview system automatically"""
        print(f"Automatically applying SESSION 42 auto-preview to {len(flat_objects)} objects...")
        
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
    
    def get_or_create_session_42_node_group(self):
        """Get existing or create SESSION 42 working node group"""
        node_group_name = "Unified_Multi_Biome_Terrain.001"
        
        # Check if it already exists
        if node_group_name in bpy.data.node_groups:
            print(f"✅ Using existing working node group: {node_group_name}")
            return bpy.data.node_groups[node_group_name]
        
        # Create the exact SESSION 42 working node group
        print(f"Creating SESSION 42 working node group: {node_group_name}")
        
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # CRITICAL: Create proper interface sockets for the modifier
        if hasattr(node_group, 'interface'):
            # Add Geometry input and output sockets
            node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
            node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
            print("✅ Added proper interface sockets")
        
        # Create nodes in exact order from SESSION 42
        group_input = node_group.nodes.new('NodeGroupInput')
        group_input.name = "Group Input"
        group_input.location = (-800.0, 0.0)
        
        group_output = node_group.nodes.new('NodeGroupOutput')
        group_output.name = "Group Output"
        group_output.location = (600.0, 0.0)
        
        named_attr = node_group.nodes.new('GeometryNodeInputNamedAttribute')
        named_attr.name = "Named Attribute"
        named_attr.location = (-700.0, -200.0)
        named_attr.data_type = 'FLOAT_VECTOR'
        named_attr.inputs['Name'].default_value = 'UVMap'
        
        canvas_sampler = node_group.nodes.new('GeometryNodeImageTexture')
        canvas_sampler.name = "Unified_Canvas_Sampler"
        canvas_sampler.location = (-500.0, -200.0)
        
        separate_xyz = node_group.nodes.new('ShaderNodeSeparateXYZ')
        separate_xyz.name = "Separate XYZ"
        separate_xyz.location = (-300.0, -200.0)
        
        color_ramp = node_group.nodes.new('ShaderNodeValToRGB')
        color_ramp.name = "Color Ramp"
        color_ramp.location = (-100.0, -200.0)
        
        noise_texture = node_group.nodes.new('ShaderNodeTexNoise')
        noise_texture.name = "Noise Texture"
        noise_texture.location = (-300.0, 100.0)
        
        position = node_group.nodes.new('GeometryNodeInputPosition')
        position.name = "Position"
        position.location = (-300.0, 300.0)
        
        math = node_group.nodes.new('ShaderNodeMath')
        math.name = "Math"
        math.location = (0.0, 0.0)
        math.operation = 'MULTIPLY'
        
        combine_xyz = node_group.nodes.new('ShaderNodeCombineXYZ')
        combine_xyz.name = "Combine XYZ"
        combine_xyz.location = (200.0, 100.0)
        
        set_position = node_group.nodes.new('GeometryNodeSetPosition')
        set_position.name = "Set Position"
        set_position.location = (400.0, 0.0)
        
        # Create exact links from SESSION 42 - INCLUDING the required Group Input/Output connections
        links = node_group.links
        
        # Link sequence from working system
        links.new(named_attr.outputs['Attribute'], canvas_sampler.inputs['Vector'])
        links.new(canvas_sampler.outputs['Color'], separate_xyz.inputs['Vector'])
        links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
        links.new(position.outputs['Position'], noise_texture.inputs['Vector'])
        links.new(noise_texture.outputs['Fac'], math.inputs[0])  # Value
        links.new(math.outputs['Value'], combine_xyz.inputs['Z'])
        links.new(combine_xyz.outputs['Vector'], set_position.inputs['Offset'])
        links.new(color_ramp.outputs['Color'], math.inputs[1])  # Value_001
        
        # CRITICAL: Connect Group Input/Output for modifier interface
        # After creating interface sockets, these connections should work
        try:
            links.new(group_input.outputs['Geometry'], set_position.inputs['Geometry'])
            links.new(set_position.outputs['Geometry'], group_output.inputs['Geometry'])
            print("✅ Connected Group Input/Output for modifier interface")
        except Exception as e:
            print(f"⚠️ Failed to connect Group I/O: {e}")
        
        print(f"✅ Created SESSION 42 working node group with {len(node_group.nodes)} nodes, {len(node_group.links)} links")
        return node_group
    
    def connect_canvas_to_node_group(self, node_group, canvas):
        """Connect canvas using SESSION 42 proven method"""
        img_tex_node = node_group.nodes.get("Unified_Canvas_Sampler")
        if img_tex_node and 'Image' in img_tex_node.inputs:
            img_tex_node.inputs['Image'].default_value = canvas
            print(f"✅ Connected canvas to {img_tex_node.name}")
            return True
        else:
            print("❌ Image Texture node or Image input not found")
            return False
    
    def setup_painting_workspace(self, context, canvas):
        """Setup split workspace for painting - EXISTING WORKING CODE"""
        try:
            # Find the largest area to split
            largest_area = None
            largest_size = 0
            
            for area in context.screen.areas:
                area_size = area.width * area.height
                if area_size > largest_size:
                    largest_size = area_size
                    largest_area = area
            
            if largest_area and largest_area.type == 'VIEW_3D':
                # Split the area 60/40
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.6)
                
                # Set the new area to Image Editor
                for area in context.screen.areas:
                    if area != largest_area and area.type == 'VIEW_3D':
                        area.type = 'IMAGE_EDITOR'
                        
                        # Load the canvas in Image Editor
                        for space in area.spaces:
                            if space.type == 'IMAGE_EDITOR':
                                space.image = canvas
                                space.mode = 'PAINT'
                                break
                        break
                
                print(f"✅ Set up split workspace with canvas: {canvas.name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Workspace split failed: {e}")
            
        return False

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Main panel with unified canvas terrain system"""
    bl_label = "O'Neill Terrain Generator - Session 49 Clean"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Header
        box = layout.box()
        box.label(text="Pure Canvas Terrain System", icon='INFO')
        
        if props.painting_mode:
            paint_status_box = box.box()
            paint_status_box.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
        
        layout.separator()
        
        # Step 1: Align Cylinders
        step_box = layout.box()
        step_box.label(text="Step 1: Align Cylinders", icon='OBJECT_DATA')
        row = step_box.row()
        row.prop(props, "alignment_axis")
        step_box.operator("oneill.align_cylinders", text="Align Selected Cylinders", icon='SORT_ASC')
        
        # Show alignment status
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("oneill_aligned")]
        if aligned_objects:
            step_box.label(text=f"✅ {len(aligned_objects)} cylinders aligned", icon='CHECKMARK')
        
        layout.separator()
        
        # Step 2: Unwrap to Flat
        step_box = layout.box()
        step_box.label(text="Step 2: Unwrap to Flat", icon='UV')
        col = step_box.column()
        col.prop(props, "subdivision_levels")
        step_box.operator("oneill.unwrap_to_flat", text="Unwrap to Flat Objects", icon='MESH_PLANE')
        
        # Show unwrap status
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if flat_objects:
            step_box.label(text=f"✅ {len(flat_objects)} flat objects created", icon='CHECKMARK')
        
        layout.separator()
        
        # Step 3: Create Heightmaps
        step_box = layout.box()
        step_box.label(text="Step 3: Create Heightmaps", icon='IMAGE_DATA')
        row = step_box.row()
        row.prop(props, "heightmap_resolution")
        step_box.operator("oneill.create_heightmaps", text="Create Heightmaps", icon='TEXTURE')
        
        # Show heightmap status
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        if heightmap_objects:
            step_box.label(text=f"✅ {len(heightmap_objects)} heightmaps created", icon='CHECKMARK')
        
        layout.separator()
        
        # Step 4: Canvas Terrain Painting (with automatic auto-preview)
        paint_box = layout.box()
        paint_box.label(text="Step 4: Canvas Terrain Painting", icon='BRUSH_DATA')
        
        if not props.painting_mode:
            paint_box.operator("oneill.start_terrain_painting", 
                             text="🎨 Start Canvas Painting", 
                             icon='BRUSH_DATA')
            paint_box.label(text="Auto-preview will activate automatically", icon='INFO')
        else:
            # EXISTING WORKING CODE: Biome selection UI when painting mode active
            paint_box.label(text="🎨 PAINTING MODE ACTIVE", icon='CHECKMARK')
            paint_box.label(text=f"Current Biome: {get_biome_display_name(props.current_biome)}")
            
            # Biome selection buttons - EXISTING WORKING CODE
            biome_box = paint_box.box()
            biome_box.label(text="Select Biome to Paint:", icon='BRUSH_DATA')
            
            # Create biome selector buttons in rows
            row1 = biome_box.row(align=True)
            row1.scale_y = 1.2
            
            # First row of biome buttons
            op = row1.operator("oneill.select_painting_biome", text="🏝️")
            op.biome_type = 'ARCHIPELAGO'
            op = row1.operator("oneill.select_painting_biome", text="🏔️")
            op.biome_type = 'MOUNTAINS'
            op = row1.operator("oneill.select_painting_biome", text="🏜️")
            op.biome_type = 'CANYONS'
            
            # Second row of biome buttons
            row2 = biome_box.row(align=True)
            row2.scale_y = 1.2
            
            op = row2.operator("oneill.select_painting_biome", text="🏞️")
            op.biome_type = 'HILLS'
            op = row2.operator("oneill.select_painting_biome", text="🌵")
            op.biome_type = 'DESERT'
            op = row2.operator("oneill.select_painting_biome", text="🌊")
            op.biome_type = 'OCEAN'
            
            # Show current biome
            current_display = get_biome_display_name(props.current_biome)
            biome_box.label(text=f"Current: {current_display}", icon='CHECKMARK')
        
        layout.separator()
        
        # Advanced Settings
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Settings", icon='PREFERENCES')
        
        row = advanced_box.row()
        row.prop(props, "terrain_scale")
        row = advanced_box.row()
        row.prop(props, "noise_scale")

# ========================= REGISTRATION =========================

# ========================= BIOME SELECTION OPERATOR =========================

class ONEILL_OT_ApplyUVMappingFix(Operator):
    """Manually apply Session 56 UV mapping fix to existing flat objects"""
    bl_idname = "oneill.apply_uv_mapping_fix"
    bl_label = "Apply UV Mapping Fix"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        # Apply the UV mapping fix
        sorted_objects = sorted(flat_objects, key=lambda obj: obj.location.x)
        total_objects = len(sorted_objects)
        
        for i, obj in enumerate(sorted_objects):
            try:
                mesh = obj.data
                if not mesh.uv_layers:
                    continue
                
                uv_layer = mesh.uv_layers['UVMap']
                
                # Calculate UV ranges - each object gets exactly 1/total_objects of canvas width
                u_start = i / total_objects
                u_end = (i + 1) / total_objects
                u_width = u_end - u_start
                
                # Get current UV range
                current_us = [uv_layer.data[loop_index].uv[0] for loop_index in range(len(uv_layer.data))]
                current_u_min = min(current_us) if current_us else 0.0
                current_u_max = max(current_us) if current_us else 1.0
                current_u_range = current_u_max - current_u_min
                
                # Remap UV coordinates
                for poly in mesh.polygons:
                    for loop_index in poly.loop_indices:
                        current_uv = uv_layer.data[loop_index].uv
                        local_u = current_uv[0]
                        local_v = current_uv[1]
                        
                        if current_u_range > 0:
                            normalized_u = (local_u - current_u_min) / current_u_range
                        else:
                            normalized_u = 0.0
                        
                        global_u = u_start + (normalized_u * u_width)
                        uv_layer.data[loop_index].uv = (global_u, local_v)
                
                mesh.update()
                
            except Exception as e:
                print(f"Failed to fix UV mapping for {obj.name}: {e}")
        
        self.report({'INFO'}, f"Applied UV mapping fix to {len(flat_objects)} objects")
        return {'FINISHED'}

class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select biome and set brush color for painting - EXISTING WORKING CODE"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Painting Biome"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_type: bpy.props.EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES
    )
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.current_biome = self.biome_type
        
        # Set brush color based on biome - EXISTING WORKING CODE
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),    # Gray
            'OCEAN': (0.1, 0.3, 0.8),        # Deep blue
            'ARCHIPELAGO': (0.2, 0.8, 0.9),  # Light blue/cyan
            'CANYONS': (0.8, 0.4, 0.2),      # Orange-red
            'HILLS': (0.4, 0.8, 0.3),        # Green
            'DESERT': (0.9, 0.8, 0.4),       # Sandy yellow
        }
        
        if self.biome_type in biome_colors:
            color = biome_colors[self.biome_type]
            
            # Set brush color in paint settings
            if hasattr(bpy.context.scene.tool_settings, 'image_paint'):
                brush_settings = bpy.context.scene.tool_settings.image_paint
                if hasattr(brush_settings, 'brush') and brush_settings.brush:
                    brush_settings.brush.color = color
                    print(f"✅ Set brush color for {self.biome_type}: {color}")
            
            # Also set unified color for painting
            if hasattr(bpy.context.scene.tool_settings, 'unified_paint_settings'):
                unified = bpy.context.scene.tool_settings.unified_paint_settings
                if hasattr(unified, 'color'):
                    unified.color = color
                    print(f"✅ Set unified paint color for {self.biome_type}: {color}")
        
        display_name = get_biome_display_name(self.biome_type)
        self.report({'INFO'}, f"Selected biome: {display_name}")
        return {'FINISHED'}

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_ApplyUVMappingFix,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_PT_MainPanel,
]

def register():
    """Register all addon components"""
    print("🚀 Registering O'Neill Terrain Generator - Session 40 Restored")
    
    # Clean up any existing registrations
    cleanup_existing_registrations()
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered: {cls.__name__}")
        except Exception as e:
            print(f"❌ Failed to register {cls.__name__}: {e}")
    
    # Add scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize unified terrain system
    bpy.types.Scene.oneill_terrain_system = UnifiedCanvasTerrainSystem()
    
    print("✅ SESSION 49 CLEANUP COMPLETE!")
    print("🎨 Pure unified canvas-to-terrain system active")
    print("🔍 No paint detection needed - direct canvas response")

def cleanup_existing_registrations():
    """Clean up any existing registrations to prevent conflicts"""
    # Remove scene properties first
    scene_props = ['oneill_props', 'oneill_terrain_system']
    
    for prop_name in scene_props:
        if hasattr(bpy.types.Scene, prop_name):
            try:
                delattr(bpy.types.Scene, prop_name)
                print(f"🧹 Cleaned up scene property: {prop_name}")
            except Exception as e:
                print(f"⚠️ Could not clean up {prop_name}: {e}")
    
    # List of potentially conflicting classes
    conflict_classes = [
        'ONEILL_OT_AlignCylinders',
        'ONEILL_OT_UnwrapToFlat', 
        'ONEILL_OT_CreateHeightmaps',
        'ONEILL_OT_StartTerrainPainting',
        'ONEILL_PT_MainPanel',
        'OneillProperties'
    ]
    
    for class_name in conflict_classes:
        if hasattr(bpy.types, class_name):
            try:
                cls = getattr(bpy.types, class_name)
                bpy.utils.unregister_class(cls)
                print(f"🧹 Cleaned up existing class: {class_name}")
            except Exception as e:
                print(f"⚠️ Could not clean up {class_name}: {e}")

def unregister():
    """Unregister all addon components"""
    print("📤 Unregistering O'Neill Terrain Generator")
    
    # Remove scene properties
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    if hasattr(bpy.types.Scene, 'oneill_terrain_system'):
        del bpy.types.Scene.oneill_terrain_system
    
    # Unregister classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    print("✅ Unregistration complete")

if __name__ == "__main__":
    register()
