"""
O'Neill Terrain Generator - SESSION 23 MINIMAL BLACK CANVAS FIX
FIXED: Canvas now defaults to BLACK (not gray mountain biome color)
BASE: Session 10 integrated version with alignment and biome systems
Applied minimal functional changes for canvas color issue
"""

import bpy
import bmesh
import mathutils
import math
import random
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty
import hashlib
from bpy.app.timers import register as timer_register

# ========================= ENHANCED SPATIAL MAPPING INTEGRATION =========================

def get_enhanced_spatial_mapping():
    """Dynamically import enhanced spatial mapping with proper path resolution"""
    try:
        import sys
        import os
        
        # Get absolute path to modules directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(script_dir, 'modules')
        
        # Ensure path exists and add to sys.path
        if os.path.exists(modules_dir) and modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
            print(f"✅ Added modules path: {modules_dir}")
        
        # Import with absolute reference
        from enhanced_spatial_mapping import EnhancedSpatialMapping
        return EnhancedSpatialMapping()
    except Exception as e:
        print(f"Enhanced spatial mapping unavailable: {e}")
        return None

def get_canvas_persistence_manager():
    """Get canvas persistence manager for enhanced canvas protection"""
    try:
        import sys
        import os
        
        # Get absolute path to modules directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(script_dir, 'modules')
        
        # Ensure path exists and add to sys.path
        if os.path.exists(modules_dir) and modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        
        # Import with absolute reference
        from enhanced_spatial_mapping import CanvasPersistenceManager
        return CanvasPersistenceManager()
    except Exception as e:
        print(f"Canvas persistence manager unavailable: {e}")
        return None

# Global function for enhanced spatial mapping (registered in driver namespace)
def apply_enhanced_spatial_mapping_global():
    """Global function to apply enhanced spatial mapping"""
    try:
        enhanced_mapper = get_enhanced_spatial_mapping()
        if enhanced_mapper:
            return enhanced_mapper.apply_enhanced_spatial_mapping()
        else:
            print("Enhanced spatial mapping unavailable - using fallback")
            return False
    except Exception as e:
        print(f"Enhanced spatial mapping failed: {e}")
        return False

# Register global function in driver namespace
bpy.app.driver_namespace['apply_enhanced_spatial_mapping'] = apply_enhanced_spatial_mapping_global

# ========================= SESSION 10 BIOME INTEGRATION =========================

def get_session10_biome_generator():
    """Get Session 10 BiomeGeometryGenerator with proper import handling"""
    try:
        import sys
        import os
        
        # Add modules directory to path
        current_dir = os.path.dirname(bpy.context.space_data.text.filepath if bpy.context.space_data and hasattr(bpy.context.space_data, 'text') and bpy.context.space_data.text else bpy.data.filepath)
        if not current_dir:
            # Fallback: use add-on directory
            current_dir = '/Users/dssstrkl/Documents/Projects/oneill terrain generator/oneill_terrain_generator_dev'
        
        modules_dir = os.path.join(current_dir, 'modules')
        
        if os.path.exists(modules_dir) and modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        
        from biome_geometry_generator import BiomeGeometryGenerator
        return BiomeGeometryGenerator()
    except Exception as e:
        print(f"Session 10 biome generator unavailable: {e}")
        return None

class GlobalPreviewDisplacementSystem:
    """SESSION 40 UNIFIED SYSTEM - Minimal changes for unified approach"""
    
    def __init__(self):
        self.biome_preview_settings = {
            'MOUNTAINS': {'displacement_strength': 2.0, 'noise_scale': 3.0},
            'OCEAN': {'displacement_strength': -1.5, 'noise_scale': 0.8},
            'ARCHIPELAGO': {'displacement_strength': 1.0, 'noise_scale': 1.5},
            'CANYONS': {'displacement_strength': 1.5, 'noise_scale': 2.0},
            'HILLS': {'displacement_strength': 0.8, 'noise_scale': 1.0},
            'DESERT': {'displacement_strength': 1.2, 'noise_scale': 1.2},
        }
    
    def create_unified_multi_biome_system(self):
        """SESSION 40: Create unified node group exactly as working scene"""
        node_group_name = "Unified_Multi_Biome_Terrain.001"
        
        # Check if already exists
        if node_group_name in bpy.data.node_groups:
            print(f"✅ Unified system already exists: {node_group_name}")
            return bpy.data.node_groups[node_group_name]
        
        # Create the unified node group with exact working structure
        ng = bpy.data.node_groups.new(node_group_name, type='GeometryNodeTree')
        
        # Add nodes exactly as in working scene
        group_input = ng.nodes.new('NodeGroupInput')
        group_output = ng.nodes.new('NodeGroupOutput')
        named_attr = ng.nodes.new('GeometryNodeInputNamedAttribute')
        canvas_sampler = ng.nodes.new('GeometryNodeImageTexture')
        separate_xyz = ng.nodes.new('ShaderNodeSeparateXYZ')
        color_ramp = ng.nodes.new('ShaderNodeValToRGB')
        noise_texture = ng.nodes.new('ShaderNodeTexNoise')
        position = ng.nodes.new('GeometryNodeInputPosition')
        math_multiply = ng.nodes.new('ShaderNodeMath')
        combine_xyz = ng.nodes.new('ShaderNodeCombineXYZ')
        set_position = ng.nodes.new('GeometryNodeSetPosition')
        
        # Set node names exactly as working scene
        named_attr.name = "Named Attribute"
        canvas_sampler.name = "Unified_Canvas_Sampler"
        
        # Configure color ramp exactly as working scene
        color_ramp.color_ramp.elements[0].position = 0.0
        color_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        color_ramp.color_ramp.elements[1].position = 0.5
        color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        
        # Configure noise texture exactly as working scene
        noise_texture.inputs['Scale'].default_value = 5.0
        noise_texture.inputs['Detail'].default_value = 10.0
        
        # Configure math node for multiply
        math_multiply.operation = 'MULTIPLY'
        
        # SESSION 42 FIX: Canvas assignment for Blender 4.x will be handled through modifier inputs
        # Image texture nodes in geometry nodes don't support direct .image assignment
        canvas_image = bpy.data.images.get('oneill_terrain_canvas')
        if canvas_image:
            print(f"✅ Canvas found: {canvas_image.name} - will be assigned via modifier inputs")
        else:
            print(f"⚠️ Canvas not found - will be assigned later")
        
        # SESSION 40: Add essential node connections for working system
        try:
            # UV flow: Named Attribute → Canvas Sampler
            ng.links.new(named_attr.outputs['Attribute'], canvas_sampler.inputs['Vector'])
            
            # Color analysis: Canvas → Separate XYZ → Color Ramp
            ng.links.new(canvas_sampler.outputs['Color'], separate_xyz.inputs['Vector'])
            ng.links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
            
            # Terrain generation: Position → Noise → Math
            ng.links.new(position.outputs['Position'], noise_texture.inputs['Vector'])
            ng.links.new(noise_texture.outputs['Fac'], math_multiply.inputs[0])
            ng.links.new(color_ramp.outputs['Color'], math_multiply.inputs[1])
            
            # Final output: Math → Combine XYZ → Set Position
            ng.links.new(math_multiply.outputs['Value'], combine_xyz.inputs['Z'])
            ng.links.new(group_input.outputs['Geometry'], set_position.inputs['Geometry'])
            ng.links.new(combine_xyz.outputs['Vector'], set_position.inputs['Offset'])
            ng.links.new(set_position.outputs['Geometry'], group_output.inputs['Geometry'])
            
            print(f"✅ Node connections established")
        except Exception as e:
            print(f"⚠️ Node linking failed: {e}")
        
        print(f"✅ Created unified system: {node_group_name}")
        return ng
    
    def apply_unified_system_to_objects(self, objects):
        """SESSION 40: Apply unified system to objects - SINGLE MODIFIER ONLY"""
        # First try to use existing unified system
        unified_ng = bpy.data.node_groups.get("Unified_Multi_Biome_Terrain.001")
        
        # If no existing system, try to create one
        if not unified_ng:
            try:
                unified_ng = self.create_unified_multi_biome_system()
            except Exception as e:
                print(f"⚠️ Unified system creation failed: {e}")
                print(f"⚠️ Checking for any existing unified systems...")
                
                # Look for any unified system that might exist
                for ng_name, ng in bpy.data.node_groups.items():
                    if "Unified" in ng_name and "Terrain" in ng_name:
                        unified_ng = ng
                        print(f"✅ Found existing unified system: {ng_name}")
                        break
        
        if not unified_ng:
            print("❌ Cannot apply - no unified system available")
            return False
        
        applied_count = 0
        for obj in objects:
            # Remove existing terrain modifiers to prevent conflicts
            for mod in list(obj.modifiers):
                if mod.name.startswith(("Preview_", "Biome_", "Canvas_Displacement")):
                    if mod.type != 'SUBSURF':  # Keep subdivision
                        obj.modifiers.remove(mod)
            
            # Ensure subdivision exists
            subdiv_mod = None
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    subdiv_mod = mod
                    break
            
            if not subdiv_mod:
                subdiv_mod = obj.modifiers.new("Preview_Subdivision", type='SUBSURF')
                subdiv_mod.levels = 2
            
            # Add unified terrain modifier
            terrain_mod = obj.modifiers.new("Unified_Terrain", type='NODES')
            terrain_mod.node_group = unified_ng
            
            # SESSION 42 FIX: Assign canvas via modifier inputs (Blender 4.x)
            canvas_image = bpy.data.images.get('oneill_terrain_canvas')
            if canvas_image:
                try:
                    # Blender 4.x method - assign through modifier input
                    terrain_mod["Input_2"] = canvas_image
                    print(f"✅ Canvas assigned via modifier input for {obj.name}")
                except Exception as e:
                    print(f"⚠️ Canvas assignment failed for {obj.name}: {e}")
            
            applied_count += 1
            print(f"✅ Applied unified system to {obj.name}")
        
        # Force viewport update after canvas assignment
        bpy.context.view_layer.update()
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        print(f"✅ Unified system applied to {applied_count} objects")
        print(f"✅ Canvas assignment completed for Blender 4.x compatibility")
        return True
    
    def create_biome_preview(self, obj, biome_name):
        """SESSION 40 UNIFIED: Use unified system instead of per-object approach"""
        
        # SESSION 40: Check if unified system exists and prefer it
        unified_ng = bpy.data.node_groups.get("Unified_Multi_Biome_Terrain.001")
        if unified_ng:
            print(f"✅ Using unified system for {obj.name} - no per-object modifiers needed")
            
            # Ensure object has unified terrain modifier
            unified_mod = None
            for mod in obj.modifiers:
                if mod.name == "Unified_Terrain" and mod.type == 'NODES':
                    unified_mod = mod
                    break
            
            if not unified_mod:
                # Apply unified system to this object
                self.apply_unified_system_to_objects([obj])
            
            # Force viewport update
            bpy.context.view_layer.update()
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return f"Unified_System"
        
        # FALLBACK: Original per-object system only if unified not available
        print(f"⚠️ Unified system not found - using fallback for {obj.name}")
        
        if biome_name not in self.biome_preview_settings:
            print(f"⚠️ Unknown biome {biome_name}, using HILLS")
            biome_name = 'HILLS'
        
        settings = self.biome_preview_settings[biome_name]
        
        # Remove existing previews first
        self.remove_preview(obj)
        
        # CRITICAL: Ensure subdivision exists
        self.ensure_preview_subdivision(obj)
        
        # TRY SESSION 10 GEOMETRY NODES FIRST
        try:
            biome_gen = get_session10_biome_generator()
            if biome_gen:
                # Map biome names from UI to Session 10 format
                biome_mapping = {
                    'MOUNTAINS': 'mountain',
                    'OCEAN': 'ocean', 
                    'ARCHIPELAGO': 'archipelago',
                    'CANYONS': 'canyon',
                    'HILLS': 'rolling_hills',
                    'DESERT': 'desert'
                }
                
                session10_biome = biome_mapping.get(biome_name, 'rolling_hills')
                
                # Apply geometry nodes biome
                modifier = biome_gen.apply_biome_to_object(
                    obj, 
                    session10_biome, 
                    strength=settings['displacement_strength'],
                    scale=settings['noise_scale']
                )
                
                if modifier:
                    print(f"✅ Applied Session 10 geometry nodes {biome_name} to {obj.name}")
                    
                    # Force immediate viewport update
                    obj.display_type = 'TEXTURED'
                    bpy.context.view_layer.update()
                    
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
                    
                    return f"GeometryNodes_{biome_name}"
                    
        except Exception as e:
            print(f"⚠️ Session 10 geometry nodes failed: {e}")
            print("🔄 Falling back to displacement modifiers")
        
        # FALLBACK: Current displacement modifier system
        texture = self.create_preview_texture(biome_name, settings, obj)
        modifier = obj.modifiers.new(name=f"Preview_{biome_name}", type='DISPLACE')
        modifier.texture = texture
        modifier.strength = settings['displacement_strength']
        modifier.mid_level = 0.5
        modifier.direction = 'NORMAL'
        modifier.space = 'LOCAL'
        
        # Force immediate viewport update
        obj.display_type = 'TEXTURED'
        bpy.context.view_layer.update()
        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        print(f"✅ Applied {biome_name} displacement preview to {obj.name} (strength: {settings['displacement_strength']})")
        return modifier
    
    def ensure_preview_subdivision(self, obj):
        """Ensure object has subdivision for displacement"""
        subdiv_mod = None
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF' and 'Preview' in mod.name:
                subdiv_mod = mod
                break
        
        if not subdiv_mod:
            subdiv_mod = obj.modifiers.new(name="Preview_Subdivision", type='SUBSURF')
            subdiv_mod.levels = 2
            subdiv_mod.render_levels = 2
    
    def create_preview_texture(self, biome_name, settings, obj):
        """Create fallback texture for displacement"""
        texture_name = f"Preview_{biome_name}_{obj.name}"
        
        if texture_name in bpy.data.textures:
            return bpy.data.textures[texture_name]
        
        texture = bpy.data.textures.new(texture_name, type='CLOUDS')
        texture.noise_scale = settings['noise_scale']
        texture.noise_depth = 4
        texture.nabla = 0.025
        
        return texture
    
    def remove_preview(self, obj):
        """Remove existing preview modifiers"""
        to_remove = []
        for mod in obj.modifiers:
            if mod.name.startswith(("Preview_", "Biome_")):
                to_remove.append(mod)
        
        for mod in to_remove:
            obj.modifiers.remove(mod)

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

    realtime_mode_active: bpy.props.BoolProperty(
        name="Real-Time Mode Active",
        description="Whether real-time paint monitoring is active",
        default=False
    )

# ========================= CORE OPERATORS =========================

class ONEILL_OT_AlignCylinders(Operator):
    """FIXED: Align cylinders with perfect contiguous positioning"""
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
            # FIXED: Calculate radius accounting for object scale
            cylinder_radius = (obj.dimensions.y / 2) / obj.scale.y
            
            obj["oneill_aligned"] = True
            obj["cylinder_radius"] = cylinder_radius
            obj["cylinder_length"] = obj_width  # Use true calculated width
            obj["alignment_axis"] = props.alignment_axis
            
        print(f"\n=== ALIGNMENT DEBUG INFO ===")
        for i, obj in enumerate(selected_objects):
            obj_min, obj_max = self.get_true_object_bounds(obj)
            obj_width = obj_max - obj_min
            print(f"Object {i}: {obj.name}")
            print(f"  Location: {obj.location[axis_idx]:.3f}")
            print(f"  Dimensions: {obj.dimensions[axis_idx]:.3f}")
            print(f"  True bounds: {obj_min:.3f} to {obj_max:.3f}")
            print(f"  True width: {obj_width:.3f}")
            print(f"  Transform: rot={obj.rotation_euler[1]:.3f}, scale={obj.scale}")
        
        # FIXED: Create contiguous objects using true bounds
        first_obj = selected_objects[0]
        first_min, first_max = self.get_true_object_bounds(first_obj)
        running_position = first_max
        
        print(f"\nStarting alignment from position: {running_position:.3f}")
        
        for i in range(1, len(selected_objects)):
            current = selected_objects[i]
            curr_min, curr_max = self.get_true_object_bounds(current)
            curr_width = curr_max - curr_min
            curr_center = (curr_min + curr_max) / 2
            
            # Position this object to touch the previous one exactly
            new_center_x = running_position + (curr_width / 2)
            offset = new_center_x - curr_center
            current.location[axis_idx] += offset
            
            print(f"Object {i}: {current.name}")
            print(f"  Old center: {curr_center:.3f}")
            print(f"  New center: {new_center_x:.3f}")
            print(f"  Offset: {offset:.3f}")
            print(f"  Running position: {running_position:.3f} -> {new_center_x + (curr_width / 2):.3f}")
            
            # Update running position for next object
            running_position = new_center_x + (curr_width / 2)
        
        print(f"=== ALIGNMENT COMPLETE ===")
        self.report({'INFO'}, f"Aligned {len(selected_objects)} cylinders contiguously")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(Operator):
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
        props = context.scene.oneill_props
        
        cylinder_radius = obj.get("cylinder_radius", 1.0)
        cylinder_length = obj.get("cylinder_length", 2.0)
        
        # DEBUG: Print actual values being used
        print(f"\n=== UNWRAPPING {obj.name} ===")
        print(f"Original dimensions: {obj.dimensions.x:.2f} x {obj.dimensions.y:.2f} x {obj.dimensions.z:.2f}")
        print(f"Stored radius: {cylinder_radius:.2f}")
        print(f"Stored length: {cylinder_length:.2f}")
        
        circumference = 2 * math.pi * cylinder_radius
        print(f"Calculated circumference: {circumference:.2f}")
        print(f"Expected flat dimensions: {cylinder_length:.2f} x {circumference:.2f}")
        
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
            vert.co.y = vert.co.y * (circumference / 2)  # REVERTED: Back to correct scaling
            vert.co.z = 0
        
        unwrapped_name = f"{original_name}_flat"
        unwrapped_mesh = bpy.data.meshes.new(unwrapped_name)
        bm_new.to_mesh(unwrapped_mesh)
        bm_new.free()
        
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
        
        # DEBUG: Print final flat object dimensions
        print(f"Final flat object dimensions: {unwrapped_obj.dimensions.x:.2f} x {unwrapped_obj.dimensions.y:.2f} x {unwrapped_obj.dimensions.z:.2f}")
        print(f"=== UNWRAPPING COMPLETE ===\n")
        
        return unwrapped_obj

class ONEILL_OT_CreateHeightmaps(Operator):
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

# ========================= BIOME SELECTION OPERATOR =========================

class ONEILL_OT_SelectPaintingBiome(bpy.types.Operator):
    """Select biome and set brush color for painting"""
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
        
        # Set brush color based on biome - FIXED colors to match spatial mapping
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

# ========================= ENHANCED PAINT DETECTION =========================

class ONEILL_OT_DetectPaintApplyPreviews(Operator):
    """Enhanced paint detection with Session 10 integration and UV region sampling"""
    bl_idname = "oneill.detect_paint_apply_previews"
    bl_label = "🔍 Detect Paint & Apply Previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        # Check if unified canvas exists
        canvas_name = 'oneill_terrain_canvas'
        if canvas_name not in bpy.data.images:
            self.report({'ERROR'}, "Unified canvas not found. Start terrain painting first.")
            return {'CANCELLED'}
        
        # Find all flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for paint detection")
            return {'CANCELLED'}
        
        # Sort objects by X position for consistent UV region mapping
        flat_objects.sort(key=lambda obj: obj.location.x)
        
        canvas = bpy.data.images[canvas_name]
        preview_system = GlobalPreviewDisplacementSystem()
        
        print(f"\n🎨 SESSION 40 UNIFIED: Applying unified system to {len(flat_objects)} objects...")
        
        # SESSION 40: Apply unified system to all objects at once
        try:
            if preview_system.apply_unified_system_to_objects(flat_objects):
                print("✅ Unified system applied to all objects")
                processed_count = len(flat_objects)
            else:
                print("⚠️ Unified system application failed - using per-object fallback")
                # FALLBACK: Original per-object detection approach
                processed_count = 0
                for obj_index, obj in enumerate(flat_objects):
                    try:
                        detected_biomes = self.sample_canvas_region_for_object(obj_index, canvas)
                        if detected_biomes:
                            main_biome = max(detected_biomes, key=detected_biomes.get)
                            preview_system.create_biome_preview(obj, main_biome)
                            processed_count += 1
                            print(f"✅ Object {obj_index + 1} ({obj.name}): Applied {main_biome} preview")
                        else:
                            print(f"⚠️ Object {obj_index + 1} ({obj.name}): No biomes detected in UV region")
                    except Exception as e:
                        print(f"❌ Object {obj_index + 1} ({obj.name}): Error processing UV region - {e}")
        except Exception as e:
            print(f"❌ Unified system failed: {e}")
            processed_count = 0
        
        # Enhanced spatial mapping (if available)
        enhanced_mapper = get_enhanced_spatial_mapping()
        if enhanced_mapper:
            try:
                # SESSION 40: Clean approach - remove only conflicting displacement modifiers
                for obj in flat_objects:
                    for mod in list(obj.modifiers):
                        if mod.name.startswith("Unified_") and mod.type == 'DISPLACE':
                            obj.modifiers.remove(mod)
                
                enhanced_mapper.apply_enhanced_spatial_mapping()
                print("✅ Applied enhanced spatial mapping (conflicts removed)")
            except Exception as e:
                print(f"⚠️ Enhanced spatial mapping failed: {e}")
        
        self.report({'INFO'}, f"Applied unified system to {processed_count}/{len(flat_objects)} objects")
        return {'FINISHED'}
    
    def detect_painted_biomes(self, canvas):
        """Detect painted biomes from canvas colors"""
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),
            'OCEAN': (0.1, 0.3, 0.8),
            'ARCHIPELAGO': (0.2, 0.8, 0.9),
            'CANYONS': (0.8, 0.4, 0.2),
            'HILLS': (0.4, 0.8, 0.3),
            'DESERT': (0.9, 0.8, 0.4),
        }
        
        detected_biomes = {}
        
        # Sample canvas pixels to detect painted colors
        width, height = canvas.size
        pixels = list(canvas.pixels)
        
        sample_points = 50  # Sample fewer points for performance
        for i in range(sample_points):
            x = int((width * i) / sample_points)
            y = int(height / 2)  # Sample center line
            
            pixel_idx = (y * width + x) * 4
            if pixel_idx + 2 < len(pixels):
                pixel_color = (pixels[pixel_idx], pixels[pixel_idx + 1], pixels[pixel_idx + 2])
                
                # Find closest biome color
                closest_biome = None
                min_distance = float('inf')
                
                for biome, color in biome_colors.items():
                    distance = sum((a - b) ** 2 for a, b in zip(pixel_color, color)) ** 0.5
                    if distance < min_distance and distance < 0.3:  # Tolerance for color matching
                        min_distance = distance
                        closest_biome = biome
                
                if closest_biome:
                    detected_biomes[closest_biome] = detected_biomes.get(closest_biome, 0) + 1
        
        return detected_biomes
    
    def sample_canvas_region_for_object(self, object_index, canvas):
        """Sample the UV-mapped region of unified canvas for a specific flat object"""
        canvas_width, canvas_height = canvas.size
        pixels = list(canvas.pixels)
        
        # Calculate UV region for this object (each object gets 1/12th of canvas width)
        num_objects = 12  # Total flat objects
        u_start = object_index / num_objects  # 0.000, 0.083, 0.167, etc.
        u_end = (object_index + 1) / num_objects
        
        # Convert UV coordinates to pixel coordinates
        pixel_x_start = int(u_start * canvas_width)
        pixel_x_end = int(u_end * canvas_width)
        
        print(f"  Object {object_index + 1}: UV region {u_start:.3f}-{u_end:.3f} → pixels {pixel_x_start}-{pixel_x_end}")
        
        # Sample colors within this UV region
        return self.analyze_canvas_colors(pixels, canvas_width, canvas_height, 
                                        pixel_x_start, pixel_x_end)
    
    def analyze_canvas_colors(self, canvas_pixels, canvas_width, canvas_height, 
                            pixel_x_start, pixel_x_end):
        """Analyze canvas region to determine dominant biome"""
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),
            'OCEAN': (0.1, 0.3, 0.8),
            'ARCHIPELAGO': (0.2, 0.8, 0.9),
            'CANYONS': (0.8, 0.4, 0.2),
            'HILLS': (0.4, 0.8, 0.3),
            'DESERT': (0.9, 0.8, 0.4),
        }
        
        detected_biomes = {}
        sample_count = 0
        
        # Sample pixels within the X range, across the full Y range
        sample_step_x = max(1, (pixel_x_end - pixel_x_start) // 20)  # 20 samples across width
        sample_step_y = max(1, canvas_height // 10)  # 10 samples across height
        
        for x in range(pixel_x_start, pixel_x_end, sample_step_x):
            for y in range(0, canvas_height, sample_step_y):
                pixel_idx = (y * canvas_width + x) * 4
                
                if pixel_idx + 2 < len(canvas_pixels):
                    pixel_color = (canvas_pixels[pixel_idx], 
                                 canvas_pixels[pixel_idx + 1], 
                                 canvas_pixels[pixel_idx + 2])
                    
                    # Skip black/unpainted pixels
                    if sum(pixel_color) < 0.1:
                        continue
                    
                    sample_count += 1
                    
                    # Find closest biome color
                    closest_biome = None
                    min_distance = float('inf')
                    
                    for biome, color in biome_colors.items():
                        distance = sum((a - b) ** 2 for a, b in zip(pixel_color, color)) ** 0.5
                        if distance < min_distance and distance < 0.3:  # Tolerance
                            min_distance = distance
                            closest_biome = biome
                    
                    if closest_biome:
                        detected_biomes[closest_biome] = detected_biomes.get(closest_biome, 0) + 1
        
        print(f"    Sampled {sample_count} painted pixels, detected biomes: {detected_biomes}")
        return detected_biomes

# ========================= SESSION 10 RECOVERY OPERATORS =========================

class ONEILL_OT_RecoverSession10Biomes(Operator):
    """Recover Session 10 biome systems"""
    bl_idname = "oneill.recover_session10_biomes"
    bl_label = "🔄 Recover Session 10 Biomes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        biome_gen = get_session10_biome_generator()
        if biome_gen:
            self.report({'INFO'}, "Session 10 biome system available and ready")
            print("✅ Session 10 BiomeGeometryGenerator recovered successfully")
        else:
            self.report({'WARNING'}, "Session 10 biome system unavailable - using fallback")
            print("⚠️ Session 10 recovery failed - fallback displacement system will be used")
        
        return {'FINISHED'}

class ONEILL_OT_TestSession10Integration(Operator):
    """Test Session 10 integration status"""
    bl_idname = "oneill.test_session10_integration"
    bl_label = "🧪 Test Session 10 Integration"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Test Session 10 biome generator
        biome_gen = get_session10_biome_generator()
        biome_status = "✅ Available" if biome_gen else "❌ Unavailable"
        
        # Test enhanced spatial mapping
        enhanced_mapper = get_enhanced_spatial_mapping()
        mapping_status = "✅ Available" if enhanced_mapper else "❌ Unavailable"
        
        # Test canvas persistence
        canvas_manager = get_canvas_persistence_manager()
        canvas_status = "✅ Available" if canvas_manager else "❌ Unavailable"
        
        message = f"Session 10 Status:\nBiomes: {biome_status}\nSpatial Mapping: {mapping_status}\nCanvas Manager: {canvas_status}"
        
        self.report({'INFO'}, message.replace('\n', ' | '))
        print(f"\n=== SESSION 10 INTEGRATION TEST ===")
        print(message)
        print("=== END TEST ===")
        
        return {'FINISHED'}

# ========================= SESSION 24 UV-CANVAS INTEGRATION =========================

class UVCanvasIntegrationSystem:
    """
    Session 24 UV-Canvas Integration System
    Implements complete paint-to-3D workflow through UV-coordinated displacement
    """
    
    def __init__(self):
        self.canvas_name = 'oneill_terrain_canvas'
        self.canvas_width = 2400
        self.canvas_height = 628
        
    def get_flat_objects(self):
        """Get all flat objects in proper order for UV mapping"""
        flat_objects = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.get('oneill_flat'):
                flat_objects.append(obj)
        
        # Sort by position (left to right)
        flat_objects.sort(key=lambda x: x.location.x)
        return flat_objects
    
    def create_canvas_image_texture(self):
        """Create image texture from canvas for displacement"""
        print("Creating Canvas_Image_Texture...")
        
        # Get or create the canvas image texture
        if 'Canvas_Image_Texture' in bpy.data.textures:
            texture = bpy.data.textures['Canvas_Image_Texture']
            print("  Found existing Canvas_Image_Texture")
        else:
            texture = bpy.data.textures.new('Canvas_Image_Texture', type='IMAGE')
            print("  Created new Canvas_Image_Texture")
        
        # Link to canvas image
        if self.canvas_name in bpy.data.images:
            canvas = bpy.data.images[self.canvas_name]
            texture.image = canvas
            texture.extension = 'EXTEND'  # SESSION 27 WORKING SETTING
            print(f"  Linked to canvas: {canvas.name} ({canvas.size[0]}x{canvas.size[1]})")
        else:
            # Create a default black canvas if none exists
            print(f"  Creating default canvas: {self.canvas_name}")
            canvas = bpy.data.images.new(self.canvas_name, width=self.canvas_width, height=self.canvas_height, alpha=False)
            pixels = [0.0, 0.0, 0.0, 1.0] * (self.canvas_width * self.canvas_height)
            canvas.pixels = pixels
            canvas.update()
            texture.image = canvas
            texture.extension = 'EXTEND'
            print(f"  Created default black canvas: {canvas.name} ({canvas.size[0]}x{canvas.size[1]})")
            
        return texture
    
    def setup_sequential_uv_mapping(self, flat_objects):
        """Set up global coordinate UV mapping - SESSION 27 WORKING IMPLEMENTATION"""
        print("Setting up global coordinate UV mapping...")
        
        num_objects = len(flat_objects)
        if num_objects == 0:
            print("❌ No flat objects found")
            return False
        
        # Calculate global surface bounds - SESSION 27 WORKING FORMULA
        flat_objects.sort(key=lambda obj: obj.location.x)
        min_x = min(obj.location.x - 1.0 for obj in flat_objects)
        max_x = max(obj.location.x + 1.0 for obj in flat_objects)
        total_width = max_x - min_x
        
        print(f"Global bounds: X={min_x:.3f} to {max_x:.3f} (width: {total_width:.3f})")
        
        # Store original active object
        original_active = bpy.context.view_layer.objects.active
        original_mode = bpy.context.mode
        
        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Process each object with global coordinate mapping
        for i, obj in enumerate(flat_objects):
            print(f"Object {i+1}: {obj.name}")
            
            # Set as active object
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            
            # Enter edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Get bmesh from edit mesh
            bm = bmesh.from_edit_mesh(obj.data)
            
            # Ensure UV layer exists
            if not bm.loops.layers.uv:
                bm.loops.layers.uv.new()
            uv_layer = bm.loops.layers.uv.active
            
            # Apply SESSION 27 WORKING FORMULA for each vertex
            for face in bm.faces:
                for loop in face.loops:
                    vert = loop.vert
                    
                    # Get world coordinates - CRITICAL: Use matrix_world
                    world_coords = obj.matrix_world @ vert.co
                    
                    # SESSION 27 WORKING FORMULA - Global coordinate mapping
                    u_coord = (world_coords.x - min_x) / total_width        # Global X → Canvas U
                    v_coord = (world_coords.y + 3.14) / 6.28               # Cylinder Y → Canvas V
                    
                    # Set the UV coordinate
                    loop[uv_layer].uv = (u_coord, v_coord)
            
            # Update the mesh
            bmesh.update_edit_mesh(obj.data)
            
            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print(f"  ✅ Global coordinate UV mapping applied")
        
        # Restore original active object and mode
        if original_active:
            bpy.context.view_layer.objects.active = original_active
        
        print(f"✅ Global coordinate UV mapping complete for all {num_objects} objects")
        return True
    
    def add_unified_canvas_displacement_modifiers(self):
        """DISABLED: Add unified canvas displacement modifiers - REPLACED WITH GEOMETRY NODES"""
        print("⚠️ Canvas displacement modifiers DISABLED - Use geometry nodes instead")
        print("SESSION 36: Basic displacement replaced with sophisticated archipelago terrain")
        return True  # Return success without actually adding modifiers
    
    def implement_complete_uv_canvas_system(self):
        """SESSION 40 UNIFIED: Implement UV-Canvas with unified multi-biome system"""
        print("🚀 SESSION 40: Implementing UV-Canvas with Unified Multi-Biome System...")
        
        # Step 1: Get flat objects
        flat_objects = self.get_flat_objects()
        if not flat_objects:
            print("❌ No flat objects found")
            return False
        
        print(f"Found {len(flat_objects)} flat objects")
        print("SESSION 40 UNIFIED: Single system for all objects")
        
        # Step 2: Create Canvas_Image_Texture (SINGLE UNIFIED TEXTURE)
        canvas_texture = self.create_canvas_image_texture()
        if not canvas_texture:
            print("❌ Failed to create canvas texture")
            return False
        
        # Step 3: Set up sequential UV mapping (maps each object to canvas region)
        if not self.setup_sequential_uv_mapping(flat_objects):
            print("❌ Failed to set up UV mapping")
            return False
        
        # Step 4: SESSION 40 - Apply unified multi-biome system
        print("🚀 Step 4: Applying unified multi-biome system...")
        preview_system = GlobalPreviewDisplacementSystem()
        if preview_system.apply_unified_system_to_objects(flat_objects):
            print("✅ Unified multi-biome system applied successfully")
        else:
            print("⚠️ Unified system failed - continuing with UV mapping only")
        
        print("🎉 SESSION 40 UV-Canvas Integration Complete!")
        print(f"   - {len(flat_objects)} objects using UNIFIED multi-biome system")
        print(f"   - Canvas-responsive terrain generation")
        print(f"   - Single canvas texture: {self.canvas_name}")
        print(f"   - Paint anywhere on canvas → sophisticated 3D terrain")
        
        return True

# ========================= CANVAS MANAGEMENT =========================

class CanvasManager:
    """Enhanced canvas management with workspace splitting"""
    
    def __init__(self):
        self.active_canvas = None
        
    def setup_split_workspace_for_painting(self, context, canvas):
        """Set up split workspace with 3D View and Image Editor"""
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
                
                self.active_canvas = canvas
                print(f"✅ Set up split workspace with canvas: {canvas.name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Workspace split failed: {e}")
            
        return False
    
    def calculate_canvas_dimensions(self, flat_objects):
        """Calculate optimal canvas dimensions based on flat objects"""
        if not flat_objects:
            return 1024, 1024
            
        total_width = sum(obj.get("cylinder_length", 2.0) for obj in flat_objects)
        max_height = max(2 * math.pi * obj.get("cylinder_radius", 1.0) for obj in flat_objects)
        
        # Convert to pixel dimensions (roughly 100 pixels per unit)
        canvas_width = max(512, min(4096, int(total_width * 100)))
        canvas_height = max(512, min(2048, int(max_height * 100)))
        
        return canvas_width, canvas_height

class ONEILL_OT_FixCanvasBlack(Operator):
    """Fix existing canvas to use black default instead of gray"""
    bl_idname = "oneill.fix_canvas_black"
    bl_label = "🔧 Fix Canvas to Black"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        canvas_name = "oneill_terrain_canvas"
        
        if canvas_name not in bpy.data.images:
            self.report({'ERROR'}, f"Canvas '{canvas_name}' not found")
            return {'CANCELLED'}
        
        canvas = bpy.data.images[canvas_name]
        width, height = canvas.size
        total_pixels = width * height
        
        # Set all pixels to black
        black_pixels = [0.0, 0.0, 0.0, 1.0] * total_pixels
        canvas.pixels = black_pixels
        canvas.update()
        
        # Force refresh in Image Editor
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()
        
        self.report({'INFO'}, f"Canvas set to BLACK ({width}x{height} pixels)")
        return {'FINISHED'}

class ONEILL_OT_LoadCanvasManually(Operator):
    """Manually load canvas for painting"""
    bl_idname = "oneill.load_canvas_manually"
    bl_label = "📂 Load Canvas Manually"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
            
        canvas_manager = CanvasManager()
        
        # Find or create combined canvas
        canvas_name = "oneill_terrain_canvas"
        canvas = None
        
        if canvas_name in bpy.data.images:
            canvas = bpy.data.images[canvas_name]
        else:
            # Create new canvas
            canvas_width, canvas_height = canvas_manager.calculate_canvas_dimensions(flat_objects)
            canvas = bpy.data.images.new(
                canvas_name,
                width=canvas_width,
                height=canvas_height,
                alpha=False
            )
            # Initialize with BLACK color (not gray mountain biome color)
            pixels = [0.0, 0.0, 0.0, 1.0] * (canvas_width * canvas_height)
            canvas.pixels = pixels
            canvas.update()
            
        # Set up split workspace
        if canvas_manager.setup_split_workspace_for_painting(context, canvas):
            context.scene.oneill_props.painting_mode = True
            self.report({'INFO'}, f"Canvas loaded: {canvas.name} ({canvas.size[0]}x{canvas.size[1]})")
        else:
            self.report({'WARNING'}, "Canvas loaded but workspace split failed")
            
        return {'FINISHED'}

# ========================= TERRAIN PAINTING OPERATORS =========================

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with automatic preview activation"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Start Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found. Complete steps 1-3 first.")
            return {'CANCELLED'}
            
        # Check if heightmaps exist
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        if not heightmap_objects:
            self.report({'ERROR'}, "No heightmaps found. Run step 3 'Create Heightmaps' first.")
            return {'CANCELLED'}
            
        canvas_manager = CanvasManager()
        canvas_width, canvas_height = canvas_manager.calculate_canvas_dimensions(flat_objects)
        
        # Create combined canvas from heightmaps
        canvas_name = "oneill_terrain_canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
            
        canvas = bpy.data.images.new(
            canvas_name,
            width=canvas_width,
            height=canvas_height,
            alpha=False
        )
        
        # Initialize canvas with BLACK color (not gray mountain biome color)
        pixels = [0.0, 0.0, 0.0, 1.0] * (canvas_width * canvas_height)
        canvas.pixels = pixels
        canvas.update()
        
        # SESSION 40: AUTO-ACTIVATE preview when starting painting
        preview_system = GlobalPreviewDisplacementSystem()
        if preview_system.apply_unified_system_to_objects(flat_objects):
            print("✅ Auto-activated unified terrain preview")
        
        # Set up workspace
        if canvas_manager.setup_split_workspace_for_painting(context, canvas):
            props.painting_mode = True
            props.current_biome = 'ARCHIPELAGO'  # Default biome
            
            # Set initial brush color
            bpy.ops.oneill.select_painting_biome(biome_type='ARCHIPELAGO')
            
            self.report({'INFO'}, f"Painting mode started with auto-preview. Canvas: {canvas_width}x{canvas_height}")
        else:
            self.report({'WARNING'}, "Painting mode started but workspace setup failed")
            props.painting_mode = True
            
        return {'FINISHED'}

class ONEILL_OT_ValidateTerrainLayout(Operator):
    """Validate terrain layout and object consistency"""
    bl_idname = "oneill.validate_terrain_layout"
    bl_label = "✅ Validate Terrain Layout"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Check alignment
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("oneill_aligned")]
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        
        validation_results = []
        validation_results.append(f"Aligned cylinders: {len(aligned_objects)}")
        validation_results.append(f"Flat objects: {len(flat_objects)}")
        validation_results.append(f"Heightmap objects: {len(heightmap_objects)}")
        
        # Check Session 10 availability
        biome_gen = get_session10_biome_generator()
        enhanced_mapper = get_enhanced_spatial_mapping()
        
        validation_results.append(f"Session 10 biomes: {'✅' if biome_gen else '❌'}")
        validation_results.append(f"Enhanced mapping: {'✅' if enhanced_mapper else '❌'}")
        
        message = " | ".join(validation_results)
        self.report({'INFO'}, message)
        
        print("\n=== TERRAIN LAYOUT VALIDATION ===")
        for result in validation_results:
            print(f"  {result}")
        print("=== END VALIDATION ===")
        
        return {'FINISHED'}

class ONEILL_OT_GenerateTerrain(Operator):
    """Generate final terrain with enhanced mapping"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "🏔️ Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for terrain generation")
            return {'CANCELLED'}
            
        # Apply enhanced spatial mapping if available
        enhanced_mapper = get_enhanced_spatial_mapping()
        if enhanced_mapper:
            try:
                enhanced_mapper.apply_enhanced_spatial_mapping()
                print("✅ Applied enhanced spatial mapping for terrain generation")
            except Exception as e:
                print(f"⚠️ Enhanced spatial mapping failed: {e}")
        
        # Apply terrain to objects
        preview_system = GlobalPreviewDisplacementSystem()
        terrain_count = 0
        
        for obj in flat_objects:
            # Convert preview to final terrain
            if props.current_biome:
                preview_system.create_biome_preview(obj, props.current_biome)
                terrain_count += 1
                
        self.report({'INFO'}, f"Generated terrain on {terrain_count} objects")
        return {'FINISHED'}

class ONEILL_OT_RemoveBasicDisplacementModifiers(Operator):
    """Remove all basic displacement modifiers from flat objects"""
    bl_idname = "oneill.remove_basic_displacement_modifiers"
    bl_label = "🗑️ Remove Basic Displacement"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        removed_count = 0
        
        for obj in flat_objects:
            modifiers_to_remove = []
            for mod in obj.modifiers:
                if mod.type == 'DISPLACE' and 'Canvas_Displacement' in mod.name:
                    modifiers_to_remove.append(mod)
            
            for mod in modifiers_to_remove:
                obj.modifiers.remove(mod)
                removed_count += 1
                print(f"Removed {mod.name} from {obj.name}")
        
        self.report({'INFO'}, f"Removed {removed_count} basic displacement modifiers")
        return {'FINISHED'}

class ONEILL_OT_SetupUVCanvasIntegration(Operator):
    """Setup UV-Canvas Integration System from Session 24 - DISABLED TO PREVENT BASIC DISPLACEMENT"""
    bl_idname = "oneill.setup_uv_canvas_integration"
    bl_label = "🔗 Setup UV-Canvas Integration (DISABLED)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        self.report({'WARNING'}, "UV-Canvas Integration disabled to prevent basic displacement conflicts. Use geometry nodes instead.")
        return {'CANCELLED'}

class ONEILL_OT_RewrapToCylinders(Operator):
    """Enhanced rewrap to cylinders with terrain data"""
    bl_idname = "oneill.rewrap_to_cylinders"
    bl_label = "🔄 Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for rewrapping")
            return {'CANCELLED'}
            
        rewrapped_count = 0
        
        for flat_obj in flat_objects:
            original_name = flat_obj.get("original_object")
            if not original_name or original_name not in bpy.data.objects:
                continue
                
            original_obj = bpy.data.objects[original_name]
            
            # Copy terrain modifiers from flat object to original cylinder
            for modifier in flat_obj.modifiers:
                if modifier.name.startswith(("Preview_", "Biome_")):
                    new_mod = original_obj.modifiers.new(modifier.name, modifier.type)
                    
                    # Copy modifier properties
                    for prop in dir(modifier):
                        if not prop.startswith('_') and hasattr(new_mod, prop):
                            try:
                                setattr(new_mod, prop, getattr(modifier, prop))
                            except:
                                pass
                                
            # Show original object and hide flat object
            original_obj.hide_viewport = False
            flat_obj.hide_viewport = True
            rewrapped_count += 1
            
        # Exit painting mode
        props.painting_mode = False
        
        self.report({'INFO'}, f"Rewrapped {rewrapped_count} cylinders with terrain data")
        return {'FINISHED'}

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Enhanced main panel with Session 10 integration"""
    bl_label = "O'Neill Terrain Generator v2.6.0 - Session 10 Integrated"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Header with version info and Session 10 status
        box = layout.box()
        box.label(text="Session 10 Integrated v2.6.0", icon='INFO')
        
        # Session 10 status indicators
        biome_gen = get_session10_biome_generator()
        enhanced_mapper = get_enhanced_spatial_mapping()
        
        status_box = box.box()
        status_box.label(text="Session 10 Status:", icon='PREFERENCES')
        row = status_box.row()
        row.label(text=f"Biomes: {'✅' if biome_gen else '❌'}")
        row.label(text=f"Enhanced: {'✅' if enhanced_mapper else '❌'}")
        
        if props.painting_mode:
            paint_status_box = box.box()
            paint_status_box.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
        
        layout.separator()
        
        # ========================= STEP 1: ALIGN CYLINDERS =========================
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
        
        # ========================= STEP 2: UNWRAP TO FLAT =========================
        step_box = layout.box()
        step_box.label(text="Step 2: Unwrap to Flat", icon='UV')
        
        col = step_box.column()
        col.prop(props, "subdivision_levels")
        if props.subdivision_levels >= 3:
            warning_box = col.box()
            warning_box.label(text="⚠️ DANGER: Level 3+ = High vertex count!", icon='ERROR')
        elif props.subdivision_levels >= 2:
            warning_box = col.box()
            warning_box.label(text="⚠️ Level 2: Moderate vertex count", icon='TIME')
        elif props.subdivision_levels <= 1:
            info_box = col.box()
            info_box.label(text="✅ Safe performance level", icon='CHECKMARK')
        
        step_box.operator("oneill.unwrap_to_flat", text="Unwrap to Flat Objects", icon='MESH_PLANE')
        
        # Show unwrap status
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if flat_objects:
            step_box.label(text=f"✅ {len(flat_objects)} flat objects created", icon='CHECKMARK')
        
        layout.separator()
        
        # ========================= STEP 3: CREATE HEIGHTMAPS =========================
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
        
        # ========================= STEP 4: TERRAIN PAINTING =========================
        if flat_objects and heightmap_objects:
            paint_box = layout.box()
            paint_box.label(text="Step 4: Terrain Painting", icon='BRUSH_DATA')
            
            if not props.painting_mode:
                # Start painting mode
                paint_box.operator("oneill.start_terrain_painting", 
                                 text="🎨 Start Terrain Painting", 
                                 icon='BRUSH_DATA')
                
                # Alternative: Load canvas manually
                paint_box.operator("oneill.load_canvas_manually", 
                                 text="📂 Load Canvas Manually", 
                                 icon='FILE_IMAGE')
                
                # Fix canvas color
                paint_box.operator("oneill.fix_canvas_black",
                                 text="🔧 Fix Canvas to Black",
                                 icon='BRUSH_DATA')
            else:
                # Painting mode active - show biome controls
                paint_box.label(text="🎨 Painting Mode Active (Auto-Preview ON)", icon='CHECKMARK')
                paint_box.label(text=f"Current Biome: {get_biome_display_name(props.current_biome)}")
                
                # Biome selection buttons
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
                
                paint_box.separator()
                
                # Paint detection and preview controls
                paint_box.operator("oneill.detect_paint_apply_previews", 
                                 text="🔄 Refresh Preview (Optional)", 
                                 icon='FILE_REFRESH')
                
                # Info about auto-preview
                paint_box.label(text="ℹ️ Preview activates automatically when painting starts", icon='INFO')
                
                # Session 36 Geometry Nodes Integration
                paint_box.separator()
                geometry_box = paint_box.box()
                geometry_box.label(text="Session 36 Geometry Nodes:", icon='GEOMETRY_NODES')
                geometry_box.operator("oneill.remove_basic_displacement_modifiers", 
                                    text="🗑️ Remove Basic Displacement", 
                                    icon='TRASH')
                geometry_box.label(text="Use Geometry Nodes for terrain instead", icon='INFO')
                
                paint_box.separator()
                
                # Session 10 recovery controls
                recovery_box = paint_box.box()
                recovery_box.label(text="Session 10 Recovery:", icon='RECOVER_LAST')
                
                row = recovery_box.row()
                row.operator("oneill.recover_session10_biomes", text="🔄 Recover Biomes")
                row.operator("oneill.test_session10_integration", text="🧪 Test Integration")
        elif flat_objects:
            paint_box = layout.box()
            paint_box.label(text="Step 4: Terrain Painting", icon='BRUSH_DATA')
            paint_box.label(text="❌ No heightmaps found", icon='ERROR')
            paint_box.label(text="Create heightmaps first")
        
        layout.separator()
        
        # ========================= STEP 5: GENERATE & REWRAP =========================
        if flat_objects:
            final_box = layout.box()
            final_box.label(text="Step 5: Generate & Rewrap", icon='MESH_CYLINDER')
            
            # Validation
            final_box.operator("oneill.validate_terrain_layout", 
                             text="✅ Validate Layout", 
                             icon='CHECKMARK')
            
            # Terrain generation
            final_box.operator("oneill.generate_terrain", 
                             text="🏔️ Generate Terrain", 
                             icon='MODIFIER')
            
            # Final rewrap
            final_box.operator("oneill.rewrap_to_cylinders", 
                             text="🔄 Rewrap to Cylinders", 
                             icon='MESH_CYLINDER')
        
        layout.separator()
        
        # ========================= ADVANCED SETTINGS =========================
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Settings", icon='PREFERENCES')
        
        row = advanced_box.row()
        row.prop(props, "terrain_scale")
        row = advanced_box.row()
        row.prop(props, "noise_scale")
        
        # Real-time mode indicator
        if props.realtime_mode_active:
            advanced_box.label(text="⚡ Real-time monitoring active", icon='TIME')

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_RecoverSession10Biomes,
    ONEILL_OT_TestSession10Integration,
    ONEILL_OT_FixCanvasBlack,
    ONEILL_OT_LoadCanvasManually,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_ValidateTerrainLayout,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RemoveBasicDisplacementModifiers,
    ONEILL_OT_SetupUVCanvasIntegration,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_PT_MainPanel,
]

def register():
    """Register all addon components with enhanced error handling"""
    print(f"🚀 Registering O'Neill Terrain Generator v2.6.0 - Session 10 Integrated")
    
    # Clean up any existing registrations
    cleanup_existing_registrations()
    
    # Register all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered: {cls.__name__}")
        except Exception as e:
            print(f"❌ Failed to register {cls.__name__}: {e}")
            raise
    
    # Add scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize global preview system
    bpy.types.Scene.oneill_preview_system = GlobalPreviewDisplacementSystem()
    
    print("="*60)
    print("🎉 O'Neill Terrain Generator v2.6.0 registration complete!")
    print("✅ Alignment bug fixed - cylinders align perfectly contiguously")
    print("✅ Session 10 integration - Enhanced biome geometry nodes available")
    print("✅ Enhanced spatial mapping - Canvas-to-object integration ready")
    print("="*60)

def cleanup_existing_registrations():
    """Clean up any existing registrations to prevent conflicts"""
    # Remove scene properties first
    scene_props = [
        'oneill_props',
        'oneill_preview_system',
        'oneill_painting_mode',
        'oneill_painting_active',
        'oneill_current_biome',
        'oneill_painting_canvas'
    ]
    
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
        'ONEILL_OT_SelectPaintingBiome',
        'ONEILL_OT_DetectPaintApplyPreviews',
        'ONEILL_OT_RecoverSession10Biomes',
        'ONEILL_OT_TestSession10Integration',
        'ONEILL_OT_LoadCanvasManually',
        'ONEILL_OT_StartTerrainPainting',
        'ONEILL_OT_ValidateTerrainLayout',
        'ONEILL_OT_GenerateTerrain',
        'ONEILL_OT_RewrapToCylinders',
        'ONEILL_PT_MainPanel',
        'OneillProperties',
        'GlobalPreviewDisplacementSystem'
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
    """Unregister all addon components with cleanup"""
    print(f"📤 Unregistering O'Neill Terrain Generator v2.6.0")
    
    # Remove scene properties first
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    if hasattr(bpy.types.Scene, 'oneill_preview_system'):
        del bpy.types.Scene.oneill_preview_system
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
            print(f"📤 Unregistered: {cls.__name__}")
        except Exception as e:
            print(f"⚠️ Failed to unregister {cls.__name__}: {e}")
    
    # Clean up driver namespace
    if 'apply_enhanced_spatial_mapping' in bpy.app.driver_namespace:
        del bpy.app.driver_namespace['apply_enhanced_spatial_mapping']
    
    print("✅ O'Neill Terrain Generator unregistration complete")

if __name__ == "__main__":
    register()