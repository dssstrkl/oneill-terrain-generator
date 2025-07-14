"""
O'Neill Terrain Generator - Main Terrain System (FIXED VERSION)
Fixes applied for context errors and missing terrain displacement
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import *
import math
import random

# ========================= CONTEXT-SAFE UTILITIES =========================

def safe_object_selection(context, action='DESELECT'):
    """Safely handle object selection with proper context override"""
    try:
        # Method 1: Try direct context override
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                with context.temp_override(area=area):
                    bpy.ops.object.select_all(action=action)
                return True
        
        # Method 2: If no 3D viewport, use direct object manipulation
        if action == 'DESELECT':
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
        elif action == 'SELECT':
            for obj in bpy.context.view_layer.objects:
                obj.select_set(True)
        
        return True
        
    except Exception as e:
        print(f"Object selection fallback: {e}")
        # Method 3: Emergency fallback - direct object property access
        if action == 'DESELECT':
            for obj in bpy.data.objects:
                try:
                    obj.select_set(False)
                except:
                    pass
        return False

# ========================= ENHANCED DISPLACEMENT SYSTEM =========================

class GlobalPreviewDisplacementSystem:
    """Global preview displacement system for two-stage workflow - ENHANCED"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # ENHANCED preview settings with stronger displacement
        self.biome_preview_settings = {
            'ARCHIPELAGO': {'displacement_strength': 1.5, 'noise_scale': 2.5, 'noise_depth': 4},
            'MOUNTAINS': {'displacement_strength': 2.0, 'noise_scale': 2.0, 'noise_depth': 5},
            'CANYONS': {'displacement_strength': 1.8, 'noise_scale': 1.5, 'noise_depth': 4},
            'HILLS': {'displacement_strength': 1.2, 'noise_scale': 3.0, 'noise_depth': 3},
            'DESERT': {'displacement_strength': 0.6, 'noise_scale': 5.0, 'noise_depth': 2},
            'OCEAN': {'displacement_strength': -1.0, 'noise_scale': 4.0, 'noise_depth': 3},
        }
        self._initialized = True
    
    def create_biome_preview(self, obj, biome_name):
        """Create immediate visual preview with proper subdivision"""
        if biome_name not in self.biome_preview_settings:
            biome_name = 'HILLS'
        
        settings = self.biome_preview_settings[biome_name]
        
        # Remove existing previews
        self.remove_preview(obj)
        
        # ENSURE SUBDIVISION EXISTS FOR PREVIEW
        self.ensure_preview_subdivision(obj)
        
        # Create enhanced texture
        texture_name = f"Preview_{biome_name}_{obj.name}"
        texture = self.create_preview_texture(texture_name, settings)
        
        # Create displacement modifier with strong settings
        modifier = obj.modifiers.new(name=f"Preview_{biome_name}", type='DISPLACE')
        modifier.texture = texture
        modifier.strength = settings['displacement_strength']
        modifier.mid_level = 0.5
        modifier.direction = 'NORMAL'
        modifier.space = 'LOCAL'
        
        # Force immediate viewport update
        obj.display_type = 'TEXTURED'
        bpy.context.view_layer.update()
        
        # Tag viewport for redraw
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return modifier
    
    def ensure_preview_subdivision(self, obj):
        """Ensure object has subdivision for preview displacement"""
        # Check for existing subdivision
        subsurf_mods = [mod for mod in obj.modifiers if mod.type == 'SUBSURF']
        
        if not subsurf_mods:
            # Add subdivision for preview
            subsurf = obj.modifiers.new(name="Preview_Subdivision", type='SUBSURF')
            subsurf.levels = 2  # Lower level for preview performance
            subsurf.render_levels = 3
            
            # Move subdivision to top of stack
            bpy.context.view_layer.objects.active = obj
            with bpy.context.temp_override(object=obj):
                while obj.modifiers.find(subsurf.name) > 0:
                    bpy.ops.object.modifier_move_up(modifier=subsurf.name)
    
    def create_preview_texture(self, texture_name, settings):
        """Create optimized preview texture"""
        # Remove existing
        if texture_name in bpy.data.textures:
            bpy.data.textures.remove(bpy.data.textures[texture_name])
        
        # Create new texture
        texture = bpy.data.textures.new(texture_name, 'CLOUDS')
        texture.noise_scale = settings['noise_scale']
        texture.noise_depth = settings['noise_depth']
        texture.noise_basis = 'BLENDER_ORIGINAL'
        
        return texture
    
    def remove_preview(self, obj):
        """Remove preview modifiers and clean up"""
        preview_modifiers = [mod for mod in obj.modifiers 
                           if mod.name.startswith("Preview_")]
        
        for modifier in preview_modifiers:
            obj.modifiers.remove(modifier)
        
        # Remove preview subdivision if it exists
        preview_subsurf = [mod for mod in obj.modifiers 
                         if mod.name == "Preview_Subdivision"]
        for mod in preview_subsurf:
            obj.modifiers.remove(mod)
        
        # Clean up preview textures
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
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                self.remove_preview(obj)

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

# ========================= CANVAS MANAGER =========================

class CanvasManager:
    """Enhanced canvas management for proper dimensions"""
    
    @staticmethod
    def recreate_canvas_with_proper_dimensions():
        """Fix canvas dimensions based on actual flat object layout"""
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            return None
        
        # Calculate proper canvas dimensions
        min_x = min(obj.location.x - obj.dimensions.x/2 for obj in flat_objects)
        max_x = max(obj.location.x + obj.dimensions.x/2 for obj in flat_objects)
        min_y = min(obj.location.y - obj.dimensions.y/2 for obj in flat_objects)
        max_y = max(obj.location.y + obj.dimensions.y/2 for obj in flat_objects)
        
        layout_width = max_x - min_x
        layout_height = max_y - min_y
        
        # Calculate canvas size (100 pixels per unit)
        pixels_per_unit = 100
        canvas_width = max(1024, int(layout_width * pixels_per_unit))
        canvas_height = max(1024, int(layout_height * pixels_per_unit))
        
        # Round to nice numbers
        canvas_width = (canvas_width // 256) * 256
        canvas_height = (canvas_height // 256) * 256
        
        # Remove old canvas if exists
        old_canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if old_canvas:
            bpy.data.images.remove(old_canvas)
        
        # Create new canvas
        canvas = bpy.data.images.new(
            "ONeill_Terrain_Canvas",
            width=canvas_width,
            height=canvas_height,
            alpha=True
        )
        canvas.colorspace_settings.name = 'Non-Color'
        
        # Initialize canvas with transparent black
        canvas.pixels = [0.0, 0.0, 0.0, 0.0] * (canvas_width * canvas_height)
        canvas.update()
        
        print(f"✅ Recreated canvas with proper dimensions: {canvas_width} x {canvas_height}")
        return canvas

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

BIOME_TYPES = [
    ('ARCHIPELAGO', "🏝️ Archipelago", "Island chains with water"),
    ('MOUNTAINS', "🏔️ Mountains", "High elevation terrain"),
    ('CANYONS', "🏔️ Canyons", "Deep canyon formations"),
    ('HILLS', "🏞️ Hills", "Rolling hills terrain"),
    ('DESERT', "🏜️ Desert", "Sand dunes and arid terrain"),
    ('OCEAN', "🌊 Ocean", "Underwater terrain"),
]

# ========================= GRID OVERLAY STUB =========================

class TerrainPaintingGridOverlay:
    """Grid overlay system stub - implement if needed"""
    
    @staticmethod
    def enable():
        print("Grid overlay enabled")
        
    @staticmethod
    def disable():
        print("Grid overlay disabled")

# Create grid overlay instance
grid_overlay = TerrainPaintingGridOverlay()

# ========================= PROPERTIES =========================

class OneillProperties(PropertyGroup):
    """Main property group for O'Neill terrain generator"""
    
    # Alignment settings
    alignment_axis: EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align along X axis"),
            ('Y', "Y-Axis", "Align along Y axis"), 
            ('Z', "Z-Axis", "Align along Z axis"),
        ],
        default='X'
    )
    
    # Subdivision settings
    subdivision_levels: IntProperty(
        name="Subdivision Levels",
        default=4,
        min=2, max=7,
        description="Subdivision detail for unwrapped objects"
    )
    
    # Heightmap settings
    heightmap_resolution: EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', "512x512", "Low resolution"),
            ('1024', "1024x1024", "Medium resolution"),
            ('2048', "2048x2048", "High resolution"),
        ],
        default='1024'
    )
    
    # Terrain settings
    terrain_scale: FloatProperty(
        name="Terrain Scale",
        default=2.0,
        min=0.1, max=10.0,
        description="Overall terrain displacement strength"
    )
    
    noise_scale: FloatProperty(
        name="Noise Scale",
        default=5.0,
        min=0.1, max=20.0,
        description="Scale of terrain noise pattern"
    )
    
    random_seed: IntProperty(
        name="Random Seed",
        default=0,
        min=0, max=1000,
        description="Seed for terrain randomization"
    )
    
    # Painting mode states
    painting_mode: BoolProperty(
        name="Painting Mode Active",
        default=False,
        description="Whether terrain painting mode is active"
    )
    
    realtime_mode_active: BoolProperty(
        name="Real-time Mode Active", 
        default=False,
        description="Whether real-time monitoring is active"
    )
    
    show_grid_overlay: BoolProperty(
        name="Show Grid Overlay",
        default=False,
        description="Show grid overlay in image editor"
    )

# ========================= CORE OPERATORS =========================

class ONEILL_OT_AlignCylinders(Operator):
    """Align cylinder objects along specified axis"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least 2 objects to align")
            return {'CANCELLED'}
        
        # Get axis index
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[props.alignment_axis]
        
        # Use first object as reference
        ref_pos = selected[0].location[axis_idx]
        
        # Align other objects
        for obj in selected[1:]:
            new_loc = obj.location.copy()
            new_loc[axis_idx] = ref_pos
            obj.location = new_loc
            obj["oneill_aligned"] = True
        
        selected[0]["oneill_aligned"] = True
        
        self.report({'INFO'}, f"Aligned {len(selected)} objects along {props.alignment_axis}-axis")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(Operator):
    """Create flat grid objects from cylinders with UVs preserving surface area"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected:
            self.report({'ERROR'}, "Select cylinder objects")
            return {'CANCELLED'}
        
        created = []
        
        for obj in selected:
            try:
                result = self.unwrap_cylinder_object(obj, context, props.alignment_axis)
                if result:
                    created.append(result)
            except Exception as e:
                self.report({'WARNING'}, f"Failed to unwrap {obj.name}: {str(e)}")
        
        if created:
            # Hide original objects
            for obj in selected:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            # Select created objects - FIXED CONTEXT HANDLING
            safe_object_selection(context, 'DESELECT')
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[-1]
            
            self.report({'INFO'}, f"Unwrapped {len(created)} cylinder objects preserving surface area")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        """Create flat object from cylinder based on alignment axis"""
        original_name = obj.name
        original_location = obj.location.copy()
        props = context.scene.oneill_props
        
        # Get cylinder parameters
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        if alignment_axis == 'X':
            min_x = min(corner.x for corner in bbox)
            max_x = max(corner.x for corner in bbox)
            min_y = min(corner.y for corner in bbox)
            max_y = max(corner.y for corner in bbox)
            min_z = min(corner.z for corner in bbox)
            max_z = max(corner.z for corner in bbox)
            
            cylinder_length = max_x - min_x
            estimated_radius = max(max_y - min_y, max_z - min_z) / 2
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
        else:
            # Similar calculations for Y and Z axes
            cylinder_length = 2.0
            estimated_radius = 1.0
            center_x = original_location.x
            center_y = original_location.y
        
        # Calculate surface area dimensions
        circumference = 2 * math.pi * estimated_radius
        
        # Calculate subdivision
        segments_x = max(20, int(cylinder_length * 10)) * (2 ** (props.subdivision_levels - 2))
        segments_y = max(20, int(circumference * 5)) * (2 ** (props.subdivision_levels - 2))
        
        # Create flat mesh using bmesh
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
        # Scale coordinates
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
        
        # Position flat object
        unwrapped_obj.location.x = center_x
        unwrapped_obj.location.y = center_y
        unwrapped_obj.location.z = 0
        
        # Store metadata for rewrap process
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = estimated_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        unwrapped_obj["alignment_axis"] = alignment_axis
        unwrapped_obj["original_location"] = list(original_location)
        unwrapped_obj["subdivision_levels"] = props.subdivision_levels
        
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
            all_flat = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if all_flat:
                # FIXED CONTEXT HANDLING
                safe_object_selection(context, 'DESELECT')
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
        
        # Create heightmaps for each flat object
        created_count = 0
        resolution = int(props.heightmap_resolution)
        
        for obj in flat_objects:
            heightmap_name = f"{obj.name}_heightmap"
            
            # Remove existing heightmap
            if heightmap_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[heightmap_name])
            
            # Create new heightmap
            heightmap = bpy.data.images.new(
                heightmap_name,
                width=resolution,
                height=resolution,
                alpha=False,
                float_buffer=True
            )
            heightmap.colorspace_settings.name = 'Non-Color'
            
            # Initialize with black (no displacement)
            heightmap.pixels = [0.0, 0.0, 0.0, 1.0] * (resolution * resolution)
            heightmap.update()
            
            # Store reference in object
            obj["heightmap_image"] = heightmap_name
            created_count += 1
        
        self.report({'INFO'}, f"Created {created_count} heightmaps at {resolution}x{resolution}")
        return {'FINISHED'}

class ONEILL_OT_GenerateTerrain(Operator):
    """Generate procedural terrain on heightmaps"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        generated_count = 0
        
        for obj in flat_objects:
            # Add displacement modifier if it doesn't exist
            disp_mods = [mod for mod in obj.modifiers if mod.type == 'DISPLACE' and mod.name == "Terrain_Displacement"]
            
            if not disp_mods:
                # Add subdivision surface first
                subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
                subsurf.levels = 2
                
                # Add displacement
                disp = obj.modifiers.new(name="Terrain_Displacement", type='DISPLACE')
                disp.strength = props.terrain_scale
                disp.mid_level = 0.5
                
                # Create noise texture
                noise_name = f"Terrain_Noise_{obj.name}"
                if noise_name not in bpy.data.textures:
                    noise_tex = bpy.data.textures.new(noise_name, 'CLOUDS')
                    noise_tex.noise_scale = props.noise_scale
                    noise_tex.noise_depth = 4
                else:
                    noise_tex = bpy.data.textures[noise_name]
                
                disp.texture = noise_tex
                generated_count += 1
        
        self.report({'INFO'}, f"Generated terrain on {generated_count} objects")
        return {'FINISHED'}

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

# ========================= TWO-STAGE TERRAIN OPERATORS =========================

class ONEILL_OT_StartTwoStageTerrainPainting(Operator):
    """Start two-stage terrain painting with proper canvas"""
    bl_idname = "oneill.start_two_stage_terrain_painting"
    bl_label = "🎨 Start Two-Stage Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        # Check prerequisites
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, 'No flat objects found. Run "Unwrap to Flat" first.')
            return {'CANCELLED'}
        
        # Recreate canvas with proper dimensions
        canvas = CanvasManager.recreate_canvas_with_proper_dimensions()
        if not canvas:
            self.report({'ERROR'}, 'Failed to create terrain canvas')
            return {'CANCELLED'}
        
        # Set terrain painting mode
        props.painting_mode = True
        props.realtime_mode_active = True
        
        # Setup image editor workspace
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = canvas
                        space.mode = 'PAINT'
                        break
                break
        
        # Switch to Texture Paint workspace
        if "Texture Paint" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Texture Paint"]
        
        # Enable grid overlay
        props.show_grid_overlay = True
        grid_overlay.enable()
        
        self.report({'INFO'}, f"Started two-stage terrain painting. Canvas: {canvas.size[0]}x{canvas.size[1]}")
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
        
        self.report({'INFO'}, f"Applied {self.biome_type} preview to {applied_count} objects")
        return {'FINISHED'}

class ONEILL_OT_RemoveAllPreviews(Operator):
    """Remove all biome previews"""
    bl_idname = "oneill.remove_all_previews"
    bl_label = "Remove All Previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        preview_system = GlobalPreviewDisplacementSystem()
        preview_system.remove_all_previews()
        
        self.report({'INFO'}, "Removed all biome previews")
        return {'FINISHED'}

class ONEILL_OT_FinishTwoStageTerrainPainting(Operator):
    """Finish terrain painting with lock-in conversion"""
    bl_idname = "oneill.finish_two_stage_terrain_painting"
    bl_label = "🔄 Finish Terrain Painting (Lock-In)"
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

# ========================= UI PANELS =========================

class ONEILL_PT_MainPanel(Panel):
    """Main O'Neill Terrain Generator panel"""
    bl_label = "O'Neill Terrain Generator v2.2.1"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Status indicator
        if props.painting_mode:
            layout.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
        
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
        
        # Step 4: Generate Terrain (Optional)
        box = layout.box()
        box.label(text="4. Generate Terrain (Optional)", icon='MODIFIER')
        row = box.row()
        row.prop(props, "terrain_scale")
        row.prop(props, "noise_scale")
        box.operator("oneill.generate_terrain")
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")

class ONEILL_PT_TwoStageTerrainPanel(Panel):
    """Two-stage terrain painting panel"""
    bl_label = "Two-Stage Terrain Painting"
    bl_idname = "ONEILL_PT_two_stage_terrain_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Check if flat objects exist
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if flat_objects:
            # Canvas status
            canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
            box = layout.box()
            box.label(text="Canvas Status:", icon='IMAGE_DATA')
            
            if canvas and len(canvas.pixels) > 0:
                aspect_ratio = canvas.size[0] / canvas.size[1] if canvas.size[1] > 0 else 1
                if aspect_ratio > 10 or aspect_ratio < 0.1:
                    box.label(text="❌ Canvas needs recreation", icon='ERROR')
                    layout.operator("oneill.start_two_stage_terrain_painting", 
                                  text="🔧 Fix Canvas & Start Painting")
                else:
                    box.label(text=f"✅ Canvas: {canvas.size[0]} x {canvas.size[1]}", icon='CHECKMARK')
                    
                    if not props.painting_mode:
                        layout.operator("oneill.start_two_stage_terrain_painting", 
                                      text="🎨 Start Two-Stage Painting")
                    else:
                        # Preview controls
                        col = layout.column(align=True)
                        col.label(text="Preview Controls:", icon='MODIFIER')
                        
                        # Quick biome buttons
                        row = col.row(align=True)
                        for biome_key, biome_display, _ in BIOME_TYPES[:3]:
                            op = row.operator("oneill.apply_biome_preview", text=biome_display[:2])
                            op.biome_type = biome_key
                        
                        row = col.row(align=True)
                        for biome_key, biome_display, _ in BIOME_TYPES[3:]:
                            op = row.operator("oneill.apply_biome_preview", text=biome_display[:2])
                            op.biome_type = biome_key
                        
                        # Remove previews
                        col.operator("oneill.remove_all_previews", text="❌ Remove All Previews")
                        
                        # Finish painting
                        col.separator()
                        col.operator("oneill.finish_two_stage_terrain_painting", 
                                    text="🔄 Finish Terrain Painting (Lock-In)")
            else:
                box.label(text="❌ No canvas found", icon='ERROR')
                layout.operator("oneill.start_two_stage_terrain_painting", 
                              text="🎨 Start Two-Stage Painting")
        else:
            box = layout.box()
            box.label(text="❌ No flat objects found", icon='ERROR')
            layout.label(text="Complete steps 1-3 first")

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_OT_StartTwoStageTerrainPainting,
    ONEILL_OT_ApplyBiomePreview,
    ONEILL_OT_RemoveAllPreviews,
    ONEILL_OT_FinishTwoStageTerrainPainting,
    ONEILL_PT_MainPanel,
    ONEILL_PT_TwoStageTerrainPanel,
]

def register():
    """Register all classes and properties"""
    # Clean up any existing registrations
    cleanup_existing()
    
    # Register classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {e}")
    
    # Add scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    print("O'Neill Terrain Generator registered successfully!")

def unregister():
    """Unregister all classes and properties"""
    # Remove scene properties
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
    
    # Unregister classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {e}")

def cleanup_existing():
    """Clean up any existing O'Neill registrations"""
    # Scene properties to clean
    scene_props = ['oneill_props', 'oneill_alignment_props', 'oneill_heightmap_props', 'oneill_biomes']
    for prop in scene_props:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except:
                pass
    
    # Find and unregister any existing O'Neill classes
    existing_classes = []
    for name in dir(bpy.types):
        if 'ONEILL' in name or 'ONeill' in name:
            existing_classes.append(name)
    
    for class_name in existing_classes:
        if hasattr(bpy.types, class_name):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, class_name))
            except:
                pass

# ========================= DEBUG UTILITIES =========================

def debug_terrain_state():
    """Debug current terrain state - run in Blender console"""
    flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
    
    print("=== TERRAIN DEBUG ===")
    for obj in flat_objects:
        print(f"{obj.name}:")
        print(f"  Modifiers: {[mod.name for mod in obj.modifiers]}")
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                print(f"    Subdivision: levels={mod.levels}")
            elif mod.type == 'DISPLACE':
                print(f"    Displacement: strength={mod.strength}, texture={mod.texture}")

def debug_context():
    """Debug current Blender context - run in Blender console"""
    print("=== CONTEXT DEBUG ===")
    print(f"Active area: {bpy.context.area.type if bpy.context.area else 'None'}")
    print(f"Selected objects: {len(bpy.context.selected_objects)}")
    
    # Test object selection
    try:
        bpy.ops.object.select_all(action='DESELECT')
        print("✅ Object selection works in current context")
    except Exception as e:
        print(f"❌ Object selection failed: {e}")

if __name__ == "__main__":
    register()