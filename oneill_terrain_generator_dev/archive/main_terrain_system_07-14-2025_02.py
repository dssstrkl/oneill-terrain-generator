"""
O'Neill Terrain Generator - Critical Fixes for Phase 1 Issues
Addresses: UI duplicates, missing biome selection, canvas loading, state management
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

# ========================= ENHANCED DISPLACEMENT SYSTEM =========================

class GlobalPreviewDisplacementSystem:
    """Enhanced preview displacement system - CORRECTED VERSION"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Enhanced preview settings with STRONG, VISIBLE displacement
        self.biome_preview_settings = {
            'ARCHIPELAGO': {'displacement_strength': 2.0, 'noise_scale': 2.5, 'noise_depth': 4},
            'MOUNTAINS': {'displacement_strength': 3.0, 'noise_scale': 2.0, 'noise_depth': 5},
            'CANYONS': {'displacement_strength': 2.5, 'noise_scale': 1.5, 'noise_depth': 4},
            'HILLS': {'displacement_strength': 1.5, 'noise_scale': 3.0, 'noise_depth': 3},
            'DESERT': {'displacement_strength': 0.8, 'noise_scale': 5.0, 'noise_depth': 2},
            'OCEAN': {'displacement_strength': -1.5, 'noise_scale': 4.0, 'noise_depth': 3},
        }
        self._initialized = True
    
    def create_biome_preview(self, obj, biome_name):
        """Create enhanced biome preview with VISIBLE displacement"""
        if biome_name not in self.biome_preview_settings:
            print(f"⚠️ Unknown biome {biome_name}, using HILLS")
            biome_name = 'HILLS'
        
        settings = self.biome_preview_settings[biome_name]
        
        # Remove existing previews first
        self.remove_preview(obj)
        
        # CRITICAL: Ensure subdivision exists
        self.ensure_preview_subdivision(obj)
        
        # Create displacement texture
        texture = self.create_preview_texture(biome_name, settings, obj)
        
        # Create displacement modifier with STRONG settings
        modifier = obj.modifiers.new(name=f"Preview_{biome_name}", type='DISPLACE')
        modifier.texture = texture
        modifier.strength = settings['displacement_strength']  # Strong displacement
        modifier.mid_level = 0.5
        modifier.direction = 'NORMAL'
        modifier.space = 'LOCAL'
        
        # Force immediate viewport update
        obj.display_type = 'TEXTURED'
        bpy.context.view_layer.update()
        
        # Tag all 3D viewports for redraw
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        print(f"✅ Applied {biome_name} preview to {obj.name} (strength: {settings['displacement_strength']})")
        return modifier
    
    def ensure_preview_subdivision(self, obj):
        """Ensure object has subdivision for displacement visibility"""
        # Check for existing subdivision
        subsurf_mods = [mod for mod in obj.modifiers if mod.type == 'SUBSURF']
        
        if not subsurf_mods:
            # Add subdivision for preview
            subsurf = obj.modifiers.new(name="Preview_Subdivision", type='SUBSURF')
            subsurf.levels = 3  # Higher level for visible displacement
            subsurf.render_levels = 4
            
            # Move subdivision to top of stack (BEFORE displacement)
            bpy.context.view_layer.objects.active = obj
            with bpy.context.temp_override(object=obj):
                while obj.modifiers.find(subsurf.name) > 0:
                    bpy.ops.object.modifier_move_up(modifier=subsurf.name)
            
            print(f"✅ Added subdivision to {obj.name} for displacement")
        else:
            print(f"✅ {obj.name} already has subdivision")
    
    def create_preview_texture(self, biome_name, settings, obj):
        """Create optimized displacement texture for preview"""
        texture_name = f"Preview_{biome_name}_{obj.name}"
        
        # Remove existing texture
        if texture_name in bpy.data.textures:
            bpy.data.textures.remove(bpy.data.textures[texture_name])
        
        # Create procedural texture
        texture = bpy.data.textures.new(texture_name, 'CLOUDS')
        texture.noise_scale = settings['noise_scale']
        texture.noise_depth = settings['noise_depth']
        texture.noise_basis = 'BLENDER_ORIGINAL'
        
        return texture
    
    def remove_preview(self, obj):
        """Remove preview modifiers and textures"""
        # Remove preview modifiers
        preview_modifiers = [mod for mod in obj.modifiers 
                           if mod.name.startswith("Preview_")]
        
        for modifier in preview_modifiers:
            print(f"🗑️ Removing preview modifier: {modifier.name}")
            obj.modifiers.remove(modifier)
        
        # Remove preview textures
        preview_textures = [tex for tex in bpy.data.textures 
                          if tex.name.startswith(f"Preview_") and obj.name in tex.name]
        for tex in preview_textures:
            bpy.data.textures.remove(tex)
        
        # Force viewport update
        bpy.context.view_layer.update()
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
    def remove_all_previews(self):
        """Remove all preview modifiers from all objects"""
        removed_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                preview_mods = [mod for mod in obj.modifiers if mod.name.startswith("Preview_")]
                if preview_mods:
                    self.remove_preview(obj)
                    removed_count += len(preview_mods)
        
        print(f"✅ Removed {removed_count} preview modifiers")

# ========================= ENHANCED TERRAIN APPLICATOR =========================

class TerrainApplicator:
    """Applies final terrain after lock-in conversion - ENHANCED"""
    
    def __init__(self):
        # Enhanced biome settings with stronger displacement
        self.biome_settings = {
            'ARCHIPELAGO': {'noise_scale': 2.2, 'strength': 1.8, 'detail': 4},
            'MOUNTAINS': {'noise_scale': 1.5, 'strength': 2.5, 'detail': 4},
            'CANYONS': {'noise_scale': 2.0, 'strength': 2.0, 'detail': 5},
            'HILLS': {'noise_scale': 3.0, 'strength': 1.5, 'detail': 3},
            'DESERT': {'noise_scale': 4.0, 'strength': 0.8, 'detail': 2},
            'OCEAN': {'noise_scale': 3.5, 'strength': -1.2, 'detail': 3},
        }
    
    def apply_terrain_to_object(self, obj, biome_name):
        """Apply final terrain with proper subdivision and displacement"""
        try:
            # 1. ENSURE SUFFICIENT SUBDIVISION FIRST
            self.ensure_object_subdivision(obj)
            
            # 2. REMOVE ANY EXISTING TERRAIN MODIFIERS
            existing_terrain_mods = [mod for mod in obj.modifiers 
                                   if mod.name.startswith(("Terrain_", "Preview_"))]
            for mod in existing_terrain_mods:
                obj.modifiers.remove(mod)
            
            # 3. CREATE DISPLACEMENT TEXTURE
            texture = self.create_displacement_texture(biome_name, obj)
            
            # 4. CREATE DISPLACEMENT MODIFIER WITH STRONG SETTINGS
            modifier = obj.modifiers.new(name=f"Terrain_{biome_name}", type='DISPLACE')
            modifier.texture = texture
            modifier.strength = self.get_biome_strength(biome_name)  # Stronger values
            modifier.mid_level = 0.5
            modifier.direction = 'NORMAL'
            modifier.space = 'LOCAL'
            
            # 5. ENSURE VIEWPORT SHOWS DISPLACEMENT
            obj.display_type = 'TEXTURED'
            
            # 6. FORCE VIEWPORT UPDATE
            bpy.context.view_layer.update()
            
            return True
            
        except Exception as e:
            print(f"Error applying terrain to {obj.name}: {e}")
            return False
    
    def ensure_object_subdivision(self, obj):
        """Ensure object has enough geometry for displacement"""
        # Check if object already has subdivision
        subsurf_mods = [mod for mod in obj.modifiers if mod.type == 'SUBSURF']
        
        if not subsurf_mods:
            # Add subdivision surface modifier BEFORE displacement
            subsurf = obj.modifiers.new(name="Subdivision_For_Terrain", type='SUBSURF')
            subsurf.levels = 3  # Viewport subdivision level
            subsurf.render_levels = 4  # Render subdivision level
            
            # Move to top of modifier stack
            bpy.context.view_layer.objects.active = obj
            with bpy.context.temp_override(object=obj):
                while obj.modifiers.find(subsurf.name) > 0:
                    bpy.ops.object.modifier_move_up(modifier=subsurf.name)
    
    def create_displacement_texture(self, biome_name, obj):
        """Create optimized displacement texture"""
        texture_name = f"Terrain_{biome_name}_{obj.name}"
        
        # Remove existing texture
        if texture_name in bpy.data.textures:
            bpy.data.textures.remove(bpy.data.textures[texture_name])
        
        # Create new texture
        texture = bpy.data.textures.new(texture_name, 'CLOUDS')
        
        # Biome-specific settings for visible displacement
        settings = self.get_biome_texture_settings(biome_name)
        texture.noise_scale = settings['noise_scale']
        texture.noise_depth = settings['noise_depth']
        texture.noise_basis = settings.get('noise_basis', 'BLENDER_ORIGINAL')
        
        return texture
    
    def get_biome_strength(self, biome_name):
        """Get displacement strength values that are actually visible"""
        strength_map = {
            'MOUNTAINS': 2.5,    # Very strong displacement
            'CANYONS': 2.0,      # Strong displacement  
            'HILLS': 1.5,        # Moderate displacement
            'ARCHIPELAGO': 1.8,  # Island-like displacement
            'DESERT': 0.8,       # Subtle dune displacement
            'OCEAN': -1.2,       # Negative for underwater terrain
        }
        return strength_map.get(biome_name, 1.5)
    
    def get_biome_texture_settings(self, biome_name):
        """Get texture settings optimized for each biome"""
        settings_map = {
            'MOUNTAINS': {'noise_scale': 1.5, 'noise_depth': 4},
            'CANYONS': {'noise_scale': 2.0, 'noise_depth': 5},
            'HILLS': {'noise_scale': 3.0, 'noise_depth': 3},
            'ARCHIPELAGO': {'noise_scale': 2.2, 'noise_depth': 4},
            'DESERT': {'noise_scale': 4.0, 'noise_depth': 2},
            'OCEAN': {'noise_scale': 3.5, 'noise_depth': 3},
        }
        return settings_map.get(biome_name, {'noise_scale': 2.5, 'noise_depth': 3})
    
    def batch_apply_terrain(self, painted_objects, progress_callback=None):
        """Apply terrain to multiple objects with progress reporting"""
        results = {'successful': 0, 'failed': 0, 'errors': []}
        
        # Remove all previews first
        preview_system = GlobalPreviewDisplacementSystem()
        preview_system.remove_all_previews()
        
        total_objects = len(painted_objects)
        for i, obj_data in enumerate(painted_objects):
            if progress_callback:
                progress_callback(i, total_objects, obj_data['object_name'])
            
            success = self.apply_terrain_to_object(obj_data['object'], obj_data['biome'])
            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to apply terrain to {obj_data['object_name']}")
        
        return results

# ========================= CANVAS ANALYZER =========================

class SimpleCanvasAnalyzer:
    """Analyzes canvas for painted terrain regions"""
    
    def analyze_for_conversion(self, canvas):
        """Find objects that need terrain conversion based on previews"""
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        painted_objects = []
        
        # Check which objects have preview modifiers
        for obj in flat_objects:
            preview_modifiers = [mod for mod in obj.modifiers if mod.name.startswith("Preview_")]
            if preview_modifiers:
                # Extract biome from modifier name
                modifier = preview_modifiers[0]
                biome = modifier.name.split("_")[1] if "_" in modifier.name else 'HILLS'
                
                painted_objects.append({
                    'object': obj,
                    'object_name': obj.name,
                    'biome': biome,
                    'has_paint': True,
                    'paint_intensity': 0.8
                })
        
        return painted_objects

# ========================= CONSTANTS =========================

# Biome types for terrain painting - INCLUDING ARCHIPELAGO
BIOME_TYPES = [
    ('ARCHIPELAGO', '🏝️ Archipelago', 'Island chains with water features'),
    ('MOUNTAINS', '🏔️ Mountains', 'Rocky peaks and cliff formations'),
    ('CANYONS', '🏜️ Canyons', 'Deep valleys and river channels'), 
    ('HILLS', '🏞️ Hills', 'Gentle rolling landscape'),
    ('DESERT', '🌵 Desert', 'Sand dunes and rocky formations'),
    ('OCEAN', '🌊 Ocean', 'Underwater terrain and depths'),
]

# Biome color mapping for painting
BIOME_COLORS = {
    'ARCHIPELAGO': (0.2, 0.8, 0.9, 1.0),  # Tropical blue-green
    'MOUNTAINS': (0.5, 0.5, 0.5, 1.0),    # Gray  
    'CANYONS': (0.8, 0.4, 0.2, 1.0),      # Orange-brown
    'HILLS': (0.4, 0.8, 0.3, 1.0),        # Green
    'DESERT': (0.9, 0.8, 0.4, 1.0),       # Sandy yellow
    'OCEAN': (0.1, 0.3, 0.8, 1.0),        # Deep blue
}

# FIXED: Biome helper functions now properly handle display
def get_biome_display_name(biome_enum):
    """Get display name for biome enum value - FIXED"""
    for enum_val, display_name, description in BIOME_TYPES:
        if enum_val == biome_enum:
            return display_name
    return biome_enum  # Fallback to enum value if not found

def get_biome_description(biome_enum):
    """Get description for biome enum value - FIXED"""
    for enum_val, display_name, description in BIOME_TYPES:
        if enum_val == biome_enum:
            return description
    return ""  # Fallback to empty string

# ========================= GRID OVERLAY SYSTEM =========================

class TerrainPaintingGridOverlay:
    """Simple grid overlay for precision painting in Image Editor"""
    
    def __init__(self):
        self.draw_handler = None
        self.is_enabled = False
        
    def enable(self):
        """Enable grid overlay drawing"""
        if not self.is_enabled:
            self.draw_handler = bpy.types.SpaceImageEditor.draw_handler_add(
                self.draw_callback, (), 'WINDOW', 'POST_PIXEL'
            )
            self.is_enabled = True
            
    def disable(self):
        """Disable grid overlay drawing"""
        if self.is_enabled and self.draw_handler:
            bpy.types.SpaceImageEditor.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
            self.is_enabled = False
            
    def create_grid_lines(self, context):
        """Create grid line coordinates"""
        props = context.scene.oneill_props
        divisions = props.grid_divisions
        
        vertices = []
        
        # Vertical lines
        for i in range(divisions + 1):
            x = i / divisions
            vertices.extend([(x, 0.0), (x, 1.0)])
            
        # Horizontal lines  
        for i in range(divisions + 1):
            y = i / divisions
            vertices.extend([(0.0, y), (1.0, y)])
            
        return vertices
        
    def draw_callback(self):
        """Draw grid overlay callback"""
        context = bpy.context
        props = context.scene.oneill_props
        
        if not props.show_grid_overlay or not props.painting_mode:
            return
            
        # Simple grid drawing using built-in GPU functions
        try:
            # Create simple shader
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            
            # Create grid geometry
            vertices = self.create_grid_lines(context)
            
            if vertices:
                # Create batch for lines
                batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
                
                # Set color with opacity
                grid_color = (1.0, 1.0, 1.0, props.grid_opacity)
                
                # Enable blending
                gpu.state.blend_set('ALPHA')
                
                # Draw grid
                shader.bind()
                shader.uniform_float("color", grid_color)
                batch.draw(shader)
                
                # Restore blending
                gpu.state.blend_set('NONE')
                
        except Exception as e:
            # Fallback: disable grid if drawing fails
            print(f"Grid overlay drawing failed: {e}")
            props.show_grid_overlay = False

# Global grid overlay instance
grid_overlay = TerrainPaintingGridOverlay()

# ========================= PROPERTIES =========================

class OneillProperties(PropertyGroup):
    alignment_axis: EnumProperty(
        name="Alignment Axis",
        items=[('X', 'X-Axis', ''), ('Y', 'Y-Axis', ''), ('Z', 'Z-Axis', '')],
        default='X'
    )
    
    subdivision_levels: IntProperty(
        name="Subdivision Levels",
        default=3,
        min=1,
        max=5
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
    
    noise_strength: FloatProperty(
        name="Noise Strength",
        default=0.5,
        min=0.0,
        max=2.0
    )
    
    # Grid overlay properties
    show_grid_overlay: BoolProperty(
        name="Show Grid Overlay",
        default=False
    )
    
    grid_divisions: IntProperty(
        name="Grid Divisions",
        default=10,
        min=5,
        max=50
    )
    
    grid_opacity: FloatProperty(
        name="Grid Opacity",
        default=0.5,
        min=0.1,
        max=1.0
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

# ========================= WORKING OPERATORS FROM BACKUP =========================

class ONEILL_OT_AlignCylinders(Operator):
    """Align cylinder objects along specified axis with corrected dimensions"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 cylinder objects")
            return {'CANCELLED'}
        
        # Sort by location along alignment axis
        axis_idx = ['X', 'Y', 'Z'].index(props.alignment_axis)
        selected_objects.sort(key=lambda obj: obj.location[axis_idx])

        # Calculate cylinder properties from ACTUAL geometry dimensions
        for obj in selected_objects:
            # Use actual visible geometry dimensions instead of forcing theoretical values
            cylinder_length = obj.dimensions.x  # Use actual visible length  
            cylinder_radius = obj.dimensions.y / 2  # Use actual visible radius
            
            # Store alignment metadata
            obj["oneill_aligned"] = True
            obj["cylinder_radius"] = cylinder_radius
            obj["cylinder_length"] = cylinder_length
            obj["alignment_axis"] = props.alignment_axis
            
        # Fix alignment gaps - ensure proper 2.0 spacing
        for i in range(1, len(selected_objects)):
            current = selected_objects[i]
            previous = selected_objects[i-1]
            
            # Set position to create exact 2.0 gap
            current.location[axis_idx] = previous.location[axis_idx] + 2.0
        
        self.report({'INFO'}, f"Aligned {len(selected_objects)} cylinders with correct O'Neill dimensions")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(Operator):
    """Unwrap selected cylinder objects to flat meshes with CORRECTED implementation"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects 
                          if obj.type == 'MESH' and obj.get("oneill_aligned")]
        
        if not selected_objects:
            self.report({'ERROR'}, "Select aligned cylinder objects")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
        
        unwrapped_count = 0
        for obj in selected_objects:
            try:                
                unwrapped_obj = self.unwrap_cylinder_object(context, obj)
                if unwrapped_obj:
                    unwrapped_count += 1
                    # Hide the original cylinder after successful unwrap
                    obj.hide_viewport = True
                    print(f"Successfully unwrapped {obj.name} -> {unwrapped_obj.name}, hid original")                    
            except Exception as e:
                print(f"Error unwrapping {obj.name}: {e}")
                self.report({'WARNING'}, f"Failed to unwrap {obj.name}: {str(e)}")
        
        self.report({'INFO'}, f"Unwrapped {unwrapped_count} objects")
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, context, obj):
        """Create flat mesh from cylinder object with proper subdivision and metadata"""
        original_name = obj.name
        original_location = obj.location.copy()
        props = context.scene.oneill_props
        
        # Get cylinder parameters from alignment data
        cylinder_radius = obj.get("cylinder_radius", 1.0)
        cylinder_length = obj.get("cylinder_length", 2.0)
        alignment_axis = obj.get("alignment_axis", "X")
        
        print(f"Unwrapping {original_name}: radius={cylinder_radius:.3f}, length={cylinder_length:.3f}, axis={alignment_axis}")
        
        # Calculate mesh dimensions and center
        mesh = obj.data
        vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
        
        center_x = sum(v.x for v in vertices) / len(vertices)
        center_y = sum(v.y for v in vertices) / len(vertices)
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)
        
        # Calculate surface area dimensions
        circumference = 2 * math.pi * cylinder_radius
        
        # Calculate subdivision based on size and detail level
        segments_x = max(20, int(cylinder_length * 10)) * (2 ** (props.subdivision_levels - 2))
        segments_y = max(20, int(circumference * 5)) * (2 ** (props.subdivision_levels - 2))
        
        print(f"Creating grid: {segments_x} x {segments_y} segments")
        
        # Create flat mesh using bmesh
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
        # CORRECT coordinate scaling: X=cylinder_length, Y=circumference
        for vert in bm_new.verts:
            vert.co.x = vert.co.x * (cylinder_length / 2)
            vert.co.y = vert.co.y * (circumference / 2)
            vert.co.z = 0
        
        # Create mesh object
        unwrapped_name = f"{original_name}_flat"
        unwrapped_mesh = bpy.data.meshes.new(unwrapped_name)
        bm_new.to_mesh(unwrapped_mesh)
        bm_new.free()
        
        unwrapped_obj = bpy.data.objects.new(unwrapped_name, unwrapped_mesh)
        context.collection.objects.link(unwrapped_obj)
        
        # Position flat object based on alignment axis
        if alignment_axis == 'X':
            unwrapped_obj.location.x = center_x
            unwrapped_obj.location.y = center_y
            unwrapped_obj.location.z = 0
        elif alignment_axis == 'Y':
            unwrapped_obj.location.x = center_y
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        else:  # Z-axis
            unwrapped_obj.location.x = (min_z + max_z) / 2
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        
        # Store complete metadata for rewrap process
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = cylinder_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        unwrapped_obj["alignment_axis"] = alignment_axis
        unwrapped_obj["original_location"] = list(original_location)
        unwrapped_obj["original_center"] = [center_x, center_y]
        unwrapped_obj["subdivision_levels"] = props.subdivision_levels
        
        print(f"Created flat object: {unwrapped_obj.dimensions} at {unwrapped_obj.location}")
        
        return unwrapped_obj

class ONEILL_OT_CreateHeightmaps(Operator):
    """Create heightmap images for flat objects"""
    bl_idname = "oneill.create_heightmaps"
    bl_label = "Create Heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        # Auto-select flat objects if none are selected
        selected_flat = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        if not selected_flat:
            # Find all flat objects in scene
            all_flat = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if all_flat:
                # Auto-select all flat objects
                bpy.ops.object.select_all(action='DESELECT')
                for obj in all_flat:
                    obj.select_set(True)
                context.view_layer.objects.active = all_flat[0]
                flat_objects = all_flat
                self.report({'INFO'}, f"Auto-selected {len(flat_objects)} flat objects")
            else:
                self.report({'ERROR'}, "No flat objects found. Run 'Unwrap to Flat' first.")
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
            
            self.create_heightmap_material(obj, heightmap)
            obj["heightmap_image"] = heightmap_name
        
        self.report({'INFO'}, f"Created heightmaps for {len(flat_objects)} objects")
        return {'FINISHED'}
    
    def create_heightmap_material(self, obj, heightmap):
        """Create material with heightmap texture"""
        mat_name = f"{obj.name}_heightmap_mat"
        
        if mat_name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[mat_name])
        
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_coord = nodes.new('ShaderNodeTexCoord')
        
        tex_image.image = heightmap
        
        links = mat.node_tree.links
        links.new(tex_coord.outputs['UV'], tex_image.inputs['Vector'])
        links.new(tex_image.outputs['Color'], shader.inputs['Base Color'])
        links.new(shader.outputs['BSDF'], output.inputs['Surface'])
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

class ONEILL_OT_DetectPaintApplyPreviews(bpy.types.Operator):
    """Detect painted biomes on canvas and apply previews to flat objects"""
    bl_idname = "oneill.detect_paint_apply_previews"
    bl_label = "🎨 Detect Paint & Apply Previews"
    bl_description = "Analyze painted colors on canvas and apply biome previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get the canvas
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            self.report({'ERROR'}, "ONeill_Terrain_Canvas not found")
            return {'CANCELLED'}
        
        # Define biome colors (same as BIOME_COLORS constant)
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),    # Gray
            'OCEAN': (0.1, 0.3, 0.8),        # Blue  
            'HILLS': (0.4, 0.8, 0.3),        # Green
            'DESERT': (0.9, 0.8, 0.4),       # Yellow
            'CANYONS': (0.8, 0.4, 0.2),      # Orange
            'ARCHIPELAGO': (0.2, 0.8, 0.9),  # Tropical blue-green
        }
        
        # Analyze canvas for painted biomes
        pixels = list(canvas.pixels)
        detected_biomes = {}
        
        # Sample pixels for efficiency
        total_pixels = len(pixels) // 4
        sample_step = max(1, total_pixels // 10000)  # Sample up to 10k pixels
        
        for i in range(0, len(pixels), sample_step * 4):
            r, g, b = pixels[i:i+3]
            
            # Check if pixel matches any biome color
            for biome, (target_r, target_g, target_b) in biome_colors.items():
                if (abs(r - target_r) < 0.15 and 
                    abs(g - target_g) < 0.15 and 
                    abs(b - target_b) < 0.15):
                    detected_biomes[biome] = detected_biomes.get(biome, 0) + 1
                    break
        
        if not detected_biomes:
            self.report({'WARNING'}, "No biome colors detected. Paint with specific colors first.")
            return {'CANCELLED'}
        
        # Apply dominant biome to flat objects
        applied_count = 0
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        dominant_biome = max(detected_biomes, key=detected_biomes.get)
        
        for obj in flat_objects:
            try:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                context.scene.oneill_props.current_biome = dominant_biome
                
                result = bpy.ops.oneill.apply_biome_preview()
                if result == {'FINISHED'}:
                    applied_count += 1
                obj.select_set(False)
            except Exception as e:
                print(f"Error applying biome to {obj.name}: {e}")
        
        message = f"Applied {dominant_biome} to {applied_count} objects (detected {len(detected_biomes)} biome types)"
        self.report({'INFO'}, message)
        return {'FINISHED'}


# ========================= ENHANCED CANVAS MANAGER =========================

class CanvasManager:
    """Enhanced canvas management for proper dimensions"""
    
    @staticmethod
    def recreate_canvas_with_proper_dimensions():
        """Fix canvas dimensions based on actual flat object layout - CORRECTED VERSION"""
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            print("❌ No flat objects found for canvas creation")
            return None
        
        # Calculate ACTUAL layout bounds from flat objects
        min_x = min(obj.location.x - obj.dimensions.x/2 for obj in flat_objects)
        max_x = max(obj.location.x + obj.dimensions.x/2 for obj in flat_objects)
        min_y = min(obj.location.y - obj.dimensions.y/2 for obj in flat_objects)
        max_y = max(obj.location.y + obj.dimensions.y/2 for obj in flat_objects)
        
        layout_width = max_x - min_x
        layout_height = max_y - min_y
        
        print(f"📏 Layout analysis: {layout_width:.1f} x {layout_height:.1f} units")
        print(f"📏 Aspect ratio: {layout_width/layout_height:.2f}")
        
        # Calculate canvas size (100 pixels per unit, rounded to 256-pixel increments)
        pixels_per_unit = 100
        canvas_width = max(1024, int(layout_width * pixels_per_unit))
        canvas_height = max(1024, int(layout_height * pixels_per_unit))
        
        # Round to nice numbers (256-pixel increments for efficiency)
        canvas_width = ((canvas_width + 255) // 256) * 256
        canvas_height = ((canvas_height + 255) // 256) * 256
        
        print(f"🎨 Calculated canvas: {canvas_width} x {canvas_height}")
        
        # Remove old malformed canvas
        old_canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if old_canvas:
            print(f"🗑️ Removing malformed canvas: {old_canvas.size[0]}x{old_canvas.size[1]}")
            bpy.data.images.remove(old_canvas)
        
        # Create new properly-sized canvas
        canvas = bpy.data.images.new(
            "ONeill_Terrain_Canvas",
            width=canvas_width,
            height=canvas_height,
            alpha=True
        )
        canvas.colorspace_settings.name = 'Non-Color'
        
        # Initialize with transparent black
        canvas.pixels = [0.0, 0.0, 0.0, 0.0] * (canvas_width * canvas_height)
        canvas.update()
        
        print(f"✅ Created proper canvas: {canvas_width}x{canvas_height} (ratio: {canvas_width/canvas_height:.2f})")
        return canvas

    @staticmethod
    def load_canvas_in_image_editor():
        """Load the corrected canvas in Image Editor for immediate painting"""
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            print("❌ No canvas found to load")
            return False
        
        # Find and load canvas in Image Editor
        canvas_loaded = False
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = canvas
                        if hasattr(space, 'mode'):
                            space.mode = 'PAINT'
                        canvas_loaded = True
                        print(f"✅ Loaded corrected canvas in Image Editor")
                        break
                break
        
        if not canvas_loaded:
            print("⚠️ No Image Editor found - canvas created but not loaded")
        
        return canvas_loaded

    @staticmethod
    def create_combined_canvas(context, heightmap_objects):
        """Create a combined horizontal canvas from all heightmaps"""
        print(f"Creating combined canvas from {len(heightmap_objects)} heightmaps...")
        
        # Get heightmap images
        heightmaps = []
        total_width = 0
        max_height = 0
        
        for obj in heightmap_objects:
            heightmap_name = obj.get("heightmap_image")
            if heightmap_name and heightmap_name in bpy.data.images:
                img = bpy.data.images[heightmap_name]
                heightmaps.append(img)
                total_width += img.size[0]
                max_height = max(max_height, img.size[1])
        
        if not heightmaps:
            return None
        
        # Create combined canvas
        canvas_name = "ONeill_Terrain_Canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
        
        canvas = bpy.data.images.new(
            canvas_name,
            width=total_width,
            height=max_height,
            alpha=False,
            float_buffer=False
        )
        
        # Initialize canvas pixels (start with black)
        canvas_pixels = [0.0] * (total_width * max_height * 4)  # RGBA
        
        # Copy each heightmap horizontally
        current_x = 0
        for img in heightmaps:
            img_width, img_height = img.size
            img_pixels = list(img.pixels)
            
            # Copy image data to canvas at current_x position
            for y in range(img_height):
                for x in range(img_width):
                    src_idx = (y * img_width + x) * 4
                    dst_idx = (y * total_width + (current_x + x)) * 4
                    
                    # Copy RGBA channels
                    for channel in range(4):
                        if src_idx + channel < len(img_pixels):
                            canvas_pixels[dst_idx + channel] = img_pixels[src_idx + channel]
            
            current_x += img_width
        
        # Apply pixels to canvas
        canvas.pixels = canvas_pixels
        canvas.colorspace_settings.name = 'Non-Color'
        canvas.update()
        
        print(f"✅ Created combined canvas: {total_width}x{max_height}")
        return canvas

# ========================= CONSOLIDATED TERRAIN PAINTING OPERATORS =========================

class ONEILL_OT_StartTerrainPainting(bpy.types.Operator):
    """Start terrain painting mode with CORRECTED canvas creation"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Start Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        # Find flat objects with heightmaps
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        
        if not heightmap_objects:
            self.report({'ERROR'}, "No objects with heightmaps found. Create heightmaps first.")
            return {'CANCELLED'}
        
        # Set painting mode
        props.painting_mode = True
        props.realtime_mode_active = True
        
        # CORRECTED: Create properly-sized canvas
        corrected_canvas = CanvasManager.recreate_canvas_with_proper_dimensions()
        
        if not corrected_canvas:
            self.report({'ERROR'}, "Failed to create corrected canvas")
            props.painting_mode = False
            return {'CANCELLED'}
        
        # Load canvas in Image Editor
        canvas_loaded = CanvasManager.load_canvas_in_image_editor()
        
        # Auto-select first flat object
        try:
            bpy.ops.object.select_all(action='DESELECT')
            heightmap_objects[0].select_set(True)
            context.view_layer.objects.active = heightmap_objects[0]
        except Exception as e:
            print(f"Warning: Could not select objects: {e}")
        
        # Enable grid overlay
        props.show_grid_overlay = True
        
        # Success message with canvas info
        canvas_info = f"{corrected_canvas.size[0]}x{corrected_canvas.size[1]}"
        self.report({'INFO'}, f"🎨 Corrected Canvas Ready! {canvas_info} - Perfect for painting!")
        return {'FINISHED'}

# CRITICAL FIX 4: Missing biome selection operator restored
class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select biome for terrain painting - RESTORED FROM BACKUP"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome: EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES,
        default='MOUNTAINS'
    )
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.current_biome = self.biome
    
        # Update brush color for visual feedback
        biome_color = BIOME_COLORS.get(self.biome, (1.0, 1.0, 1.0, 1.0))
    
        try:
            tool_settings = context.scene.tool_settings
        
            # Set brush color
            if tool_settings.image_paint.brush:
                brush = tool_settings.image_paint.brush
                brush.color = biome_color[:3]
            
            # Also set unified paint color
            if hasattr(tool_settings, 'unified_paint_settings'):
                tool_settings.unified_paint_settings.color = biome_color[:3]
        
        except Exception as e:
            print(f"⚠️ Failed to set brush color: {e}")
        
        display_name = get_biome_display_name(self.biome)
        self.report({'INFO'}, f"Selected {display_name} - Color: {biome_color[:3]}")
        return {'FINISHED'}

class ONEILL_OT_ApplyBiomePreview(Operator):
    """Apply biome preview to selected objects"""
    bl_idname = "oneill.apply_biome_preview"
    bl_label = "Apply Biome Preview"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_type: EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES,
        default='MOUNTAINS'
    )
    
    def execute(self, context):
        # Find flat objects (either selected or all if none selected)
        selected_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not selected_objects:
            # If no flat objects selected, use all flat objects
            selected_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            
        if not selected_objects:
            self.report({'WARNING'}, 'No flat objects found')
            return {'CANCELLED'}
        
        preview_system = GlobalPreviewDisplacementSystem()
        applied_count = 0
        
        for obj in selected_objects:
            modifier = preview_system.create_biome_preview(obj, self.biome_type)
            if modifier:
                applied_count += 1
        
        display_name = get_biome_display_name(self.biome_type)
        self.report({'INFO'}, f"Applied {display_name} preview to {applied_count} objects")
        return {'FINISHED'}

class ONEILL_OT_RemoveAllPreviews(Operator):
    """Remove all biome previews"""
    bl_idname = "oneill.remove_all_previews"
    bl_label = "❌ Remove All Previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        preview_system = GlobalPreviewDisplacementSystem()
        preview_system.remove_all_previews()
        
        self.report({'INFO'}, "Removed all biome previews")
        return {'FINISHED'}

class ONEILL_OT_FinishTerrainPainting(Operator):
    """Finish terrain painting with lock-in conversion"""
    bl_idname = "oneill.finish_terrain_painting"
    bl_label = "🔄 Lock-In Final Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        """Show confirmation dialog"""
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            self.report({'ERROR'}, "No terrain canvas found")
            return {'CANCELLED'}
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        """Execute full preview-to-final conversion"""
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            self.report({'ERROR'}, "No terrain canvas found")
            return {'CANCELLED'}
        
        # Analyze canvas for painted regions
        analyzer = SimpleCanvasAnalyzer()
        painted_objects = analyzer.analyze_for_conversion(canvas)
        
        if not painted_objects:
            self.report({'WARNING'}, "No painted terrain found. Apply some previews first.")
            return {'CANCELLED'}
        
        # Convert painted terrain to final terrain
        applicator = TerrainApplicator()
        
        def progress_callback(current, total, object_name):
            print(f"Converting {object_name} ({current+1}/{total})")
        
        results = applicator.batch_apply_terrain(painted_objects, progress_callback)
        
        # Update scene properties
        props = context.scene.oneill_props
        props.painting_mode = False
        props.realtime_mode_active = False
        props.show_grid_overlay = False
        grid_overlay.disable()
        
        success_count = results['successful']
        total_count = len(painted_objects)
        
        if results['errors']:
            error_summary = f"Errors: {'; '.join(results['errors'][:2])}"
            self.report({'WARNING'}, f"Conversion completed with issues: {success_count}/{total_count} successful. {error_summary}")
        else:
            self.report({'INFO'}, f"Terrain conversion complete: {success_count}/{total_count} objects processed successfully")
        
        return {'FINISHED'}

class ONEILL_OT_ExitPaintingMode(Operator):
    """Exit painting mode without applying terrain"""
    bl_idname = "oneill.exit_painting_mode"
    bl_label = "🛑 Exit Painting Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        # Remove all previews
        preview_system = GlobalPreviewDisplacementSystem()
        preview_system.remove_all_previews()
        
        # Disable painting mode
        props.painting_mode = False
        props.realtime_mode_active = False
        props.show_grid_overlay = False
        grid_overlay.disable()
        
        self.report({'INFO'}, "Exited terrain painting mode")
        return {'FINISHED'}

# ========================= TERRAIN GENERATION OPERATORS =========================

class ONEILL_OT_GenerateTerrain(Operator):
    """Generate procedural terrain from heightmaps"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        heightmap_objects = [obj for obj in bpy.data.objects 
                           if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if not heightmap_objects:
            self.report({'ERROR'}, "No heightmap objects found")
            return {'CANCELLED'}
        
        for obj in heightmap_objects:
            self.apply_displacement_modifier(obj, props)
        
        self.report({'INFO'}, f"Generated terrain for {len(heightmap_objects)} objects")
        return {'FINISHED'}
    
    def apply_displacement_modifier(self, obj, props):
        """Apply displacement modifier using heightmap"""
        # Add subdivision for displacement
        if "Subdivision" not in [mod.name for mod in obj.modifiers]:
            subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = props.subdivision_levels
        
        # Add displacement modifier
        if "Displacement" not in [mod.name for mod in obj.modifiers]:
            disp = obj.modifiers.new(name="Displacement", type='DISPLACE')
            
            # Set heightmap texture
            heightmap_name = obj.get("heightmap_image")
            if heightmap_name in bpy.data.images:
                # Create texture
                if heightmap_name not in bpy.data.textures:
                    tex = bpy.data.textures.new(heightmap_name, 'IMAGE')
                    tex.image = bpy.data.images[heightmap_name]
                else:
                    tex = bpy.data.textures[heightmap_name]
                
                disp.texture = tex
                disp.strength = props.terrain_scale
                disp.mid_level = 0.5

class ONEILL_OT_RewrapToCylinders(Operator):
    """Rewrap flat terrain back to cylinder geometry"""
    bl_idname = "oneill.rewrap_to_cylinders"
    bl_label = "Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects to rewrap")
            return {'CANCELLED'}
        
        for flat_obj in flat_objects:
            source_name = flat_obj.get("original_object")
            if source_name and source_name in bpy.data.objects:
                source_cyl = bpy.data.objects[source_name]
                self.apply_terrain_to_cylinder(flat_obj, source_cyl)
        
        self.report({'INFO'}, f"Rewrapped {len(flat_objects)} objects to cylinders")
        return {'FINISHED'}
    
    def apply_terrain_to_cylinder(self, flat_obj, cylinder):
        """Apply terrain displacement to original cylinder"""
        # Copy displacement modifier from flat to cylinder
        for mod in flat_obj.modifiers:
            if mod.type == 'DISPLACE':
                if "Terrain_Displacement" not in [m.name for m in cylinder.modifiers]:
                    new_mod = cylinder.modifiers.new(name="Terrain_Displacement", type='DISPLACE')
                    new_mod.texture = mod.texture
                    new_mod.strength = mod.strength
                    new_mod.mid_level = mod.mid_level
                    new_mod.direction = 'NORMAL'

class ONEILL_OT_StartRealtimeMonitoring(bpy.types.Operator):
    """Start Phase 2A Real-Time Paint Monitoring"""
    bl_idname = "oneill.start_realtime_monitoring"
    bl_label = "🚀 Start Real-Time Mode"
    bl_description = "Activate automatic paint detection and terrain updates"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR
        
        if PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode already active")
            return {'CANCELLED'}
        
        PHASE2A_MONITOR.last_canvas_hash = PHASE2A_MONITOR.get_canvas_hash()
        PHASE2A_MONITOR.active = True
        PHASE2A_MONITOR.change_count = 0
        PHASE2A_MONITOR.total_updates = 0
        
        timer_register(PHASE2A_MONITOR.realtime_callback)
        context.scene.oneill_props.realtime_mode_active = True
        
        self.report({'INFO'}, "Real-Time Mode Started! Paint and see instant terrain updates.")
        return {'FINISHED'}

class ONEILL_OT_StopRealtimeMonitoring(bpy.types.Operator):
    """Stop Phase 2A Real-Time Paint Monitoring"""
    bl_idname = "oneill.stop_realtime_monitoring"
    bl_label = "⏸️ Stop Real-Time Mode"
    bl_description = "Return to manual terrain painting mode"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR
        
        if not PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode not active")
            return {'CANCELLED'}
        
        PHASE2A_MONITOR.active = False
        context.scene.oneill_props.realtime_mode_active = False
        
        message = f"Real-time mode stopped. Processed {PHASE2A_MONITOR.change_count} changes."
        self.report({'INFO'}, message)
        return {'FINISHED'}

# ========================= FIXED UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Main O'Neill Terrain Generator panel - FIXED VERSION"""
    bl_label = "O'Neill Terrain Generator v2.3.1"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw_enhanced_painting_controls(self, context, layout):
        """Enhanced painting controls with Phase 2A real-time integration"""
        props = context.scene.oneill_props
        
        # Check for flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            layout.label(text="❌ No flat objects found", icon='ERROR')
            layout.label(text="Complete steps 1-3 first")
            return
        
        # Canvas status check
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        
        if canvas and len(canvas.pixels) > 0:
            aspect_ratio = canvas.size[0] / canvas.size[1] if canvas.size[1] > 0 else 1
            if aspect_ratio > 10 or aspect_ratio < 0.1:
                layout.label(text="❌ Canvas needs recreation", icon='ERROR')
            else:
                layout.label(text=f"✅ Canvas: {canvas.size[0]}x{canvas.size[1]}", icon='CHECKMARK')
        else:
            layout.label(text="❌ No canvas found", icon='ERROR')
        
        if not props.painting_mode:
            # NOT PAINTING: Show start button
            layout.operator("oneill.start_terrain_painting", text="🎨 Start Terrain Painting")
            
            # Optional: Show old Generate Terrain for backwards compatibility
            layout.separator()
            layout.label(text="OR use procedural generation:", icon='MODIFIER')
            row = layout.row()
            row.prop(props, "terrain_scale")
            row.prop(props, "noise_scale")
            layout.operator("oneill.generate_terrain")
            
        else:
            # PAINTING MODE ACTIVE: Show enhanced controls
            
            # Real-time mode status
            status_box = layout.box()
            if props.realtime_mode_active:
                status_box.label(text="🟢 REAL-TIME MODE ACTIVE", icon='REC')
                status_box.label(text="Paint automatically applies!")
            else:
                status_box.label(text="⚪ REAL-TIME MODE OFF", icon='PAUSE')
            
            # Real-time controls
            control_row = layout.row(align=True)
            if props.realtime_mode_active:
                control_row.operator("oneill.stop_realtime_monitoring", icon='PAUSE')
            else:
                control_row.operator("oneill.start_realtime_monitoring", icon='PLAY')
            
            # Manual detection fallback
            layout.separator()
            layout.label(text="Manual Controls:")
            layout.operator("oneill.detect_paint_apply_previews", icon='BRUSH_DATA')
            
            # Color reference
            layout.separator()
            color_box = layout.box()
            color_box.label(text="🎨 Biome Colors:")
            col = color_box.column(align=True)
            col.label(text="🏝️ Archipelago: Cyan (0.2, 0.8, 0.9)")
            col.label(text="🏔️ Mountains: Gray (0.5, 0.5, 0.5)")
            col.label(text="🏜️ Canyons: Orange (0.8, 0.4, 0.2)")
            col.label(text="🏞️ Hills: Green (0.4, 0.8, 0.3)")
            col.label(text="🌵 Desert: Yellow (0.9, 0.8, 0.4)")
            col.label(text="🌊 Ocean: Blue (0.1, 0.3, 0.8)")
            
            # Existing biome selection buttons (keep for manual mode)
            layout.separator()
            col = layout.column(align=True)
            col.label(text="Biome Selection (Manual):", icon='BRUSH_DATA')
            
            # Current biome display
            current_biome_display = get_biome_display_name(props.current_biome)
            col.label(text=f"Current: {current_biome_display}")
            
            # Individual biome buttons (preserve existing functionality)
            row1 = col.row(align=True)
            op = row1.operator("oneill.select_painting_biome", text="🏝️")
            op.biome = 'ARCHIPELAGO'
            op = row1.operator("oneill.select_painting_biome", text="🏔️")
            op.biome = 'MOUNTAINS'
            op = row1.operator("oneill.select_painting_biome", text="🏜️")
            op.biome = 'CANYONS'
            
            row2 = col.row(align=True)
            op = row2.operator("oneill.select_painting_biome", text="🏞️")
            op.biome = 'HILLS'
            op = row2.operator("oneill.select_painting_biome", text="🌵")
            op.biome = 'DESERT'
            op = row2.operator("oneill.select_painting_biome", text="🌊")
            op.biome = 'OCEAN'
            
            col.separator()
            
            # Preview system controls
            col.label(text="Apply Biome Previews:", icon='MODIFIER')
            preview_row = col.row(align=True)
            op = preview_row.operator("oneill.apply_biome_preview", text="Mountains")
            op.biome_type = 'MOUNTAINS'
            op = preview_row.operator("oneill.apply_biome_preview", text="Ocean") 
            op.biome_type = 'OCEAN'
            
            col.separator()
            
            # Control buttons
            col.operator("oneill.remove_all_previews")
            col.separator()
            col.operator("oneill.finish_terrain_painting")
            col.operator("oneill.exit_painting_mode")
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # CRITICAL FIX 5: Proper status indicator
        if props.painting_mode:
            box = layout.box()
            box.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
            current_biome_display = get_biome_display_name(props.current_biome)
            box.label(text=f"Current: {current_biome_display}")
        
        # Step 1: Align Cylinders
        box = layout.box()
        box.label(text="1. Align Cylinders", icon='OBJECT_DATA')
        row = box.row()
        row.prop(props, "alignment_axis")
        box.operator("oneill.align_cylinders")
        
        # Step 2: Unwrap to Flat
        box = layout.box()
        box.label(text="2. Unwrap to Flat", icon='MOD_UVPROJECT')
        box.prop(props, "subdivision_levels")
        box.operator("oneill.unwrap_to_flat") 
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Paint Terrain Biomes (Enhanced with Phase 2A)
        box = layout.box()
        box.label(text="4. Paint Terrain Biomes", icon='BRUSH_DATA')
        
        # Use the enhanced painting controls
        self.draw_enhanced_painting_controls(context, box)
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")

class Phase2ARealtimeMonitor:
    """Phase 2A Real-time paint monitoring system"""
    
    def __init__(self):
        self.active = False
        self.update_interval = 0.5  # 2 FPS for responsive performance
        self.last_canvas_hash = None
        self.change_count = 0
        self.total_updates = 0
        
    def get_canvas_hash(self):
        """Efficient change detection via sampling"""
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            return None
            
        pixels = list(canvas.pixels)
        sample_size = min(len(pixels), 40000)  # 10k pixels * 4 channels
        sample_step = max(1, len(pixels) // sample_size)
        
        sample_data = bytes(int(pixels[i] * 255) for i in range(0, len(pixels), sample_step))
        return hashlib.md5(sample_data).hexdigest()
    
    def realtime_callback(self):
        """Core Phase 2A timer callback"""
        try:
            if not self.active:
                return None  # Stop timer when inactive
                
            current_hash = self.get_canvas_hash()
            self.total_updates += 1
            
            if current_hash and current_hash != self.last_canvas_hash:
                self.change_count += 1
                print(f"🎨 Real-time change #{self.change_count} detected")
                
                # Apply biomes using paint detection
                result = bpy.ops.oneill.detect_paint_apply_previews()
                if result == {'FINISHED'}:
                    print(f"✅ Real-time terrain update applied")
                
                self.last_canvas_hash = current_hash
            
            return self.update_interval  # Continue monitoring
            
        except Exception as e:
            print(f"❌ Real-time error: {e}")
            return self.update_interval

# Create global monitor instance
PHASE2A_MONITOR = Phase2ARealtimeMonitor()

# ========================= FIXED REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,   # CRITICAL FIX 9: Added missing operator
    ONEILL_OT_ApplyBiomePreview,
    ONEILL_OT_RemoveAllPreviews,
    ONEILL_OT_FinishTerrainPainting,
    ONEILL_OT_ExitPaintingMode,
    ONEILL_PT_MainPanel,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_StartRealtimeMonitoring,
    ONEILL_OT_StopRealtimeMonitoring,
]

def register():
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize grid overlay
    global grid_overlay
    grid_overlay = TerrainPaintingGridOverlay()
    
    print("O'Neill Terrain Generator v2.3.1 - CRITICAL FIXES APPLIED - registered successfully")

def unregister():
    """Unregister all classes and properties"""
    # Disable grid overlay
    global grid_overlay
    if grid_overlay:
        grid_overlay.disable()
        
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Remove scene property
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    print("O'Neill Terrain Generator v2.3.1 unregistered")

if __name__ == "__main__":
    register()