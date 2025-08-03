"""
O'Neill Terrain Generator - SESSION 10 INTEGRATED VERSION
FIXED: Alignment bug - cylinders now perfectly contiguous
INTEGRATED: Session 10 biome geometry nodes with fallback architecture
Applied true 1:1 spatial canvas-to-object mapping with multi-biome support
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(script_dir, 'modules')
        
        if os.path.exists(modules_dir) and modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        
        from biome_geometry_generator import BiomeGeometryGenerator
        return BiomeGeometryGenerator()
    except Exception as e:
        print(f"Session 10 biome generator unavailable: {e}")
        return None

class GlobalPreviewDisplacementSystem:
    """Enhanced displacement system with Session 10 integration"""
    
    def __init__(self):
        self.biome_preview_settings = {
            'MOUNTAINS': {'displacement_strength': 2.0, 'noise_scale': 3.0},
            'OCEAN': {'displacement_strength': -1.5, 'noise_scale': 0.8},
            'ARCHIPELAGO': {'displacement_strength': 1.0, 'noise_scale': 1.5},
            'CANYONS': {'displacement_strength': 1.5, 'noise_scale': 2.0},
            'HILLS': {'displacement_strength': 0.8, 'noise_scale': 1.0},
            'DESERT': {'displacement_strength': 1.2, 'noise_scale': 1.2},
        }
    
    def create_biome_preview(self, obj, biome_name):
        """Create enhanced biome preview with Session 10 geometry nodes integration"""
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
            cylinder_radius = obj.dimensions.y / 2
            
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
        
        mesh = obj.data
        vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
        
        center_x = sum(v.x for v in vertices) / len(vertices)
        center_y = sum(v.y for v in vertices) / len(vertices)
        
        circumference = 2 * math.pi * cylinder_radius
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

# Rest of operators and UI will be added in the next part...
# This completes the core functionality with the alignment fix and Session 10 integration