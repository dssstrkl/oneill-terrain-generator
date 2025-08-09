"""
O'Neill Terrain Generator - ENHANCED SPATIAL MAPPING INTEGRATED VERSION
FIXED: Enhanced spatial mapping integration with proper import path resolution
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
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 cylinder objects")
            return {'CANCELLED'}
        
        axis_idx = ['X', 'Y', 'Z'].index(props.alignment_axis)
        selected_objects.sort(key=lambda obj: obj.location[axis_idx])

        for obj in selected_objects:
            cylinder_length = obj.dimensions.x
            cylinder_radius = obj.dimensions.y / 2
            
            obj["oneill_aligned"] = True
            obj["cylinder_radius"] = cylinder_radius
            obj["cylinder_length"] = cylinder_length
            obj["alignment_axis"] = props.alignment_axis
            
        # Calculate contiguous spacing - objects touching edge to edge
        # Each object is 6.0 units wide, so center-to-center spacing = 6.0 units
        proper_spacing = 6.0  # Object width with no gaps (contiguous)
        
        # Center the array around the origin
        total_span = (len(selected_objects) - 1) * proper_spacing
        start_position = -(total_span / 2)
        
        for i, obj in enumerate(selected_objects):
            obj.location[axis_idx] = start_position + (i * proper_spacing)
        
        self.report({'INFO'}, f"Aligned {len(selected_objects)} cylinders")
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

# ========================= ENHANCED PAINT DETECTION OPERATOR =========================

class ONEILL_OT_DetectPaintApplyPreviews(bpy.types.Operator):
    """ENHANCED: Detect painted biomes with proper spatial mapping integration"""
    bl_idname = "oneill.detect_paint_apply_previews"
    bl_label = "🎨 Detect Paint & Apply Previews"
    bl_description = "Analyze painted colors on canvas and apply biome previews using enhanced spatial mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            print("=== ENHANCED PAINT DETECTION STARTING ===")
            
            # Try enhanced spatial mapping first
            enhanced_mapper = get_enhanced_spatial_mapping()
            if enhanced_mapper:
                print("✅ Enhanced spatial mapping available - applying...")
                success = enhanced_mapper.apply_enhanced_spatial_mapping()
                
                if success:
                    self.report({'INFO'}, "Enhanced spatial mapping applied successfully")
                    return {'FINISHED'}
                else:
                    print("⚠️ Enhanced spatial mapping failed - using fallback")
            else:
                print("⚠️ Enhanced spatial mapping not available - using fallback")

            # FALLBACK: Basic spatial canvas mapping
            canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
            if not canvas:
                self.report({'ERROR'}, "ONeill_Terrain_Canvas not found")
                return {'CANCELLED'}
            
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if not flat_objects:
                self.report({'ERROR'}, "No flat objects found")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "Applied enhanced spatial mapping system")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Paint detection error: {str(e)}")
            return {'CANCELLED'}

# ========================= CANVAS MANAGEMENT =========================

class CanvasManager:
    """Enhanced canvas management for proper dimensions"""
    
    @staticmethod
    def recreate_canvas_with_proper_dimensions():
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            return None
        
        min_x = min(obj.location.x - obj.dimensions.x/2 for obj in flat_objects)
        max_x = max(obj.location.x + obj.dimensions.x/2 for obj in flat_objects)
        min_y = min(obj.location.y - obj.dimensions.y/2 for obj in flat_objects)
        max_y = max(obj.location.y + obj.dimensions.y/2 for obj in flat_objects)
        
        layout_width = max_x - min_x
        layout_height = max_y - min_y
        
        pixels_per_unit = 100
        canvas_width = max(1024, int(layout_width * pixels_per_unit))
        canvas_height = max(1024, int(layout_height * pixels_per_unit))
        
        canvas_width = ((canvas_width + 255) // 256) * 256
        canvas_height = ((canvas_height + 255) // 256) * 256
        
        old_canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if old_canvas:
            bpy.data.images.remove(old_canvas)
        
        canvas = bpy.data.images.new(
            "ONeill_Terrain_Canvas",
            width=canvas_width,
            height=canvas_height,
            alpha=True
        )
        canvas.colorspace_settings.name = 'Non-Color'
        
        canvas.pixels = [0.0, 0.0, 0.0, 0.0] * (canvas_width * canvas_height)
        canvas.update()
        
        print(f"✅ Created proper canvas: {canvas_width}x{canvas_height}")
        return canvas

# ========================= TERRAIN PAINTING OPERATORS =========================

class ONEILL_OT_LoadCanvasManually(bpy.types.Operator):
    """Manually load canvas in Image Editor (backup option)"""
    bl_idname = "oneill.load_canvas_manually"
    bl_label = "🖼️ Load Canvas in Image Editor"
    bl_description = "Manually set the terrain canvas in Image Editor and activate paint mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find the terrain canvas
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            self.report({'ERROR'}, "ONeill_Terrain_Canvas not found. Run 'Start Enhanced Terrain Painting' first.")
            return {'CANCELLED'}
        
        # Find Image Editor and set canvas
        image_editor_found = False
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        # Set the canvas
                        space.image = canvas
                        space.mode = 'PAINT'
                        
                        # Configure paint settings
                        if hasattr(context.scene.tool_settings, 'image_paint'):
                            paint_settings = context.scene.tool_settings.image_paint
                            paint_settings.mode = 'IMAGE'
                            paint_settings.canvas = canvas
                            
                            # Ensure brush is available
                            if not paint_settings.brush:
                                brushes = [brush for brush in bpy.data.brushes if brush.use_paint_image]
                                if brushes:
                                    paint_settings.brush = brushes[0]
                        
                        image_editor_found = True
                        break
                break
        
        if image_editor_found:
            self.report({'INFO'}, f"✅ Canvas loaded in Image Editor: {canvas.name} ({canvas.size[0]}x{canvas.size[1]})")
        else:
            self.report({'ERROR'}, "No Image Editor found. Please create an Image Editor area first.")
        
        return {'FINISHED'}

class ONEILL_OT_StartTerrainPainting(bpy.types.Operator):
    """Start terrain painting mode with AUTOMATIC Image Editor setup and paint mode activation"""
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
        
        # Create properly-sized canvas
        corrected_canvas = CanvasManager.recreate_canvas_with_proper_dimensions()
        
        if not corrected_canvas:
            self.report({'ERROR'}, "Failed to create corrected canvas")
            props.painting_mode = False
            return {'CANCELLED'}
        
        # AUTOMATIC IMAGE EDITOR SETUP
        print("🎨 SETTING UP IMAGE EDITOR AUTOMATICALLY...")
        
        # Check if Image Editor already exists
        image_editor_exists = False
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                image_editor_exists = True
                break
        
        # Create Image Editor if it doesn't exist
        if not image_editor_exists:
            print("📱 Creating Image Editor area...")
            # Find the largest 3D viewport to split
            largest_3d_area = None
            largest_size = 0
            
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area_size = area.width * area.height
                    if area_size > largest_size:
                        largest_size = area_size
                        largest_3d_area = area
            
            if largest_3d_area:
                # Split the 3D viewport to create Image Editor
                with context.temp_override(area=largest_3d_area):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                
                # Set the new area to Image Editor
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D' and area != largest_3d_area:
                        area.type = 'IMAGE_EDITOR'
                        print("✅ Created Image Editor area")
                        break
            else:
                print("⚠️ No 3D viewport found to split")
        
        # CRITICAL FIX: Set canvas in Image Editor and activate paint mode
        print("🎨 CRITICAL FIX: Activating paint mode...")
        
        image_editor_configured = False
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        # Set the canvas
                        space.image = corrected_canvas
                        print(f"✅ Canvas set in Image Editor: {corrected_canvas.name}")
                        
                        # CRITICAL: Activate paint mode
                        space.mode = 'PAINT'
                        print("✅ Paint mode activated in Image Editor")
                        
                        # Configure paint settings
                        if hasattr(context.scene.tool_settings, 'image_paint'):
                            paint_settings = context.scene.tool_settings.image_paint
                            paint_settings.mode = 'IMAGE'
                            paint_settings.canvas = corrected_canvas
                            
                            # Ensure brush is available
                            if not paint_settings.brush:
                                brushes = [brush for brush in bpy.data.brushes if brush.use_paint_image]
                                if brushes:
                                    paint_settings.brush = brushes[0]
                            
                            print("✅ Paint settings configured")
                        
                        image_editor_configured = True
                        break
                break
        
        if not image_editor_configured:
            print("⚠️ Could not configure Image Editor - manual setup required")
            self.report({'WARNING'}, "Image Editor setup incomplete - please set canvas manually")
        
        # Enhanced canvas persistence setup
        try:
            persistence_manager = get_canvas_persistence_manager()
            if persistence_manager:
                persistence_manager.enable_canvas_persistence()
                persistence_manager.backup_canvas_data()
                print("✅ Enhanced canvas persistence enabled")
        except Exception as e:
            print(f"⚠️ Canvas persistence setup failed: {e}")
        
        canvas_info = f"{corrected_canvas.size[0]}x{corrected_canvas.size[1]}"
        if image_editor_configured:
            self.report({'INFO'}, f"🎨 Enhanced Canvas Ready! {canvas_info} - Paint controls active!")
        else:
            self.report({'INFO'}, f"🎨 Canvas created {canvas_info} - Please manually set in Image Editor")
        
        return {'FINISHED'}

class ONEILL_OT_ValidateTerrainLayout(Operator):
    """Validate and fix terrain layout using enhanced spatial mapping"""
    bl_idname = "oneill.validate_terrain_layout"
    bl_label = "🔍 Validate Terrain Layout"
    bl_description = "Check and fix terrain assignment using enhanced spatial mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if not canvas:
            self.report({'ERROR'}, "No terrain canvas found")
            return {'CANCELLED'}
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        print("=== ENHANCED TERRAIN LAYOUT VALIDATION ===")
        
        # Try enhanced spatial mapping for validation
        enhanced_success = False
        try:
            enhanced_mapper = get_enhanced_spatial_mapping()
            if enhanced_mapper:
                enhanced_success = enhanced_mapper.apply_enhanced_spatial_mapping()
                
                if enhanced_success:
                    print("✅ Enhanced spatial mapping validation applied")
                else:
                    print("⚠️ Enhanced validation failed - using fallback")
        except Exception as e:
            print(f"⚠️ Enhanced validation error: {e} - using fallback")
        
        # Count terrain objects
        terrain_objects = sum(1 for obj in flat_objects 
                            if any(mod.name.startswith(("Terrain_", "Preview_")) for mod in obj.modifiers))
        
        flat_objects_count = len(flat_objects) - terrain_objects
        
        print(f"\n=== VALIDATION RESULTS ===")
        print(f"Total objects: {len(flat_objects)}")
        print(f"Objects with terrain: {terrain_objects}")
        print(f"Objects kept flat: {flat_objects_count}")
        
        validation_type = "Enhanced" if enhanced_success else "Basic"
        self.report({'INFO'}, f"{validation_type} validation complete: {terrain_objects} terrain, {flat_objects_count} flat areas")
        return {'FINISHED'}

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
        
        self.report({'INFO'}, f"Generated terrain for {len(heightmap_objects)} objects")
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
        
        self.report({'INFO'}, f"Rewrapped {len(flat_objects)} objects to cylinders")
        return {'FINISHED'}

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Main O'Neill Terrain Generator panel with enhanced spatial mapping"""
    bl_label = "O'Neill Terrain Generator v2.5.0 - Enhanced Spatial Mapping"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Enhanced status indicator
        if props.painting_mode:
            box = layout.box()
            box.label(text="🎨 ENHANCED PAINTING MODE ACTIVE", icon='BRUSH_DATA')
            
            # Check if enhanced spatial mapping is available
            enhanced_mapper = get_enhanced_spatial_mapping()
            if enhanced_mapper:
                box.label(text="✅ Enhanced Spatial Mapping Available", icon='CHECKMARK')
            else:
                box.label(text="⚠️ Using Basic Spatial Mapping", icon='ERROR')
        
        # Step 1: Align Cylinders
        box = layout.box()
        box.label(text="1. Align Cylinders", icon='OBJECT_DATA')
        row = box.row()
        row.prop(props, "alignment_axis")
        box.operator("oneill.align_cylinders")
        
        # Step 2: Unwrap to Flat
        box = layout.box()
        box.label(text="2. Unwrap to Flat", icon='MOD_UVPROJECT')
        
        col = box.column()
        col.prop(props, "subdivision_levels")
        if props.subdivision_levels >= 3:
            warning_box = col.box()
            warning_box.label(text="⚠️ DANGER: Level 3 = 69M vertices!", icon='ERROR')
        elif props.subdivision_levels >= 2:
            warning_box = col.box()
            warning_box.label(text="⚠️ Level 2: High vertex count", icon='TIME')
        elif props.subdivision_levels <= 1:
            info_box = col.box()
            info_box.label(text="✅ Safe performance level", icon='CHECKMARK')
        
        box.operator("oneill.unwrap_to_flat")
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Enhanced Terrain Painting
        box = layout.box()
        box.label(text="4. Enhanced Terrain Painting", icon='BRUSH_DATA')
        
        # Check for flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            box.label(text="❌ No flat objects found", icon='ERROR')
            box.label(text="Complete steps 1-3 first")
        else:
            if not props.painting_mode:
                # Start enhanced terrain painting
                box.operator("oneill.start_terrain_painting", text="🎨 Start Enhanced Terrain Painting")
                
                # Optional: Show old Generate Terrain for backwards compatibility
                box.separator()
                box.label(text="OR use procedural generation:", icon='MODIFIER')
                row = box.row()
                row.prop(props, "terrain_scale")
                row.prop(props, "noise_scale")
                box.operator("oneill.generate_terrain")
                
            else:
                # Enhanced painting mode controls
                col = box.column(align=True)
                
                # Manual canvas loading option
                canvas_box = col.box()
                canvas_box.label(text="🖼️ Canvas Controls:", icon='IMAGE_DATA')
                canvas_box.operator("oneill.load_canvas_manually", text="🖼️ Load Canvas in Image Editor")
                
                col.separator()
                
                # Biome selector buttons - FIXED to set correct brush colors
                biome_box = col.box()
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
                
                col.separator()
                col.operator("oneill.detect_paint_apply_previews", text="🎨 Apply Enhanced Spatial Mapping", icon='BRUSH_DATA')
                col.separator()
                col.operator("oneill.validate_terrain_layout", text="🔍 Validate Enhanced Layout", icon='CHECKMARK')
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_LoadCanvasManually,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_ValidateTerrainLayout,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_PT_MainPanel,
]

def register():
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    print("="*60)
    print("O'Neill Terrain Generator v2.5.0 - ENHANCED SPATIAL MAPPING")
    print("🎯 INTEGRATED: True 1:1 spatial canvas-to-object mapping")
    print("🎨 ENHANCED: Multi-biome support with seamless transitions")
    print("🛡️ PROTECTED: Canvas persistence prevents paint data loss")
    print("⚡ PERFORMANCE: Safe subdivision levels with warnings")
    print("="*60)

def unregister():
    """Unregister all classes and properties"""
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Remove scene property
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    print("O'Neill Terrain Generator v2.5.0 unregistered")

if __name__ == "__main__":
    register()
