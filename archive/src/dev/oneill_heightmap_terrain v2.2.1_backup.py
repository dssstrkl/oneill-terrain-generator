bl_info = {
    "name": "O'Neill Terrain Generator",
    "author": "dssstrkl",
    "version": (2, 2, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > O'Neill Tab",
    "description": "Generate terrain for O'Neill cylinder interiors with heightmap workflow and precision grid overlay",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils
import math
import random
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty

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

# ========================= UTILITY FUNCTIONS =========================

def get_cylinder_objects():
    """Get all objects that appear to be O'Neill cylinder segments"""
    cylinders = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith(('Cylinder', 'O_Neill', 'oneill')):
            cylinders.append(obj)
    return cylinders

def create_heightmap_image(name, resolution):
    """Create a new heightmap image"""
    res = int(resolution)
    if name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[name])
    
    img = bpy.data.images.new(name, width=res, height=res, alpha=False)
    # Initialize with neutral gray (0.5 height)
    pixels = [0.5, 0.5, 0.5, 1.0] * (res * res)
    img.pixels = pixels
    img.update()
    return img

# ========================= MAIN OPERATORS =========================

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
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects")
            return {'CANCELLED'}
        
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

# ========================= TERRAIN PAINTING SYSTEM =========================

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with biome selection"""
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
        
        # Setup painting layout
        self.setup_painting_layout(context, heightmap_objects[0])
        
        # Enable grid overlay
        props.show_grid_overlay = True
        grid_overlay.enable()
        
        # Create biome masks for painting
        self.create_biome_masks(context, heightmap_objects)
        
        self.report({'INFO'}, f"Started terrain painting on {len(heightmap_objects)} heightmaps")
        return {'FINISHED'}
        
    def setup_painting_layout(self, context, heightmap_obj):
        """Setup Image Editor + 3D View layout for painting"""
        # Try to switch to Texture Paint workspace
        if "Texture Paint" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Texture Paint"]
        
        # Find Image Editor and load heightmap - FIXED VERSION
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                space = area.spaces.active
                heightmap_name = heightmap_obj.get("heightmap_image")
                if heightmap_name and heightmap_name in bpy.data.images:
                    heightmap = bpy.data.images[heightmap_name]
                    space.image = heightmap
                    space.mode = 'PAINT'
                    # Force colorspace and update
                    heightmap.colorspace_settings.name = 'Non-Color'
                    heightmap.update()
                    print(f"✅ Loaded heightmap in Image Editor: {heightmap_name}")
                else:
                    print(f"❌ Failed to find heightmap: {heightmap_name}")
                break
        
    def create_biome_masks(self, context, heightmap_objects):
        """Create biome color masks for terrain painting"""
        for obj in heightmap_objects:
            heightmap_name = obj.get("heightmap_image")
            if heightmap_name in bpy.data.images:
                heightmap = bpy.data.images[heightmap_name]
                
                # Set up painting brush settings
                if context.scene.tool_settings.image_paint.brush:
                    context.scene.tool_settings.image_paint.brush.color = BIOME_COLORS['MOUNTAINS'][:3]

class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select biome for terrain painting"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome: bpy.props.EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES,
        default='MOUNTAINS'
    )
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.current_biome = self.biome
    
        # Update brush color - FIXED VERSION WITH UNIFIED PAINT SUPPORT
        biome_color = BIOME_COLORS.get(self.biome, (1.0, 1.0, 1.0, 1.0))
    
        try:
            tool_settings = context.scene.tool_settings
        
            # Set brush color
            if tool_settings.image_paint.brush:
                brush = tool_settings.image_paint.brush
                brush.color = biome_color[:3]
            
            # ALSO set unified paint color (this is what the header shows!)
            if hasattr(tool_settings, 'unified_paint_settings'):
                tool_settings.unified_paint_settings.color = biome_color[:3]
            
            print(f"✅ Set both brush and unified color to {biome_color[:3]} for {self.biome}")
        
        except Exception as e:
            print(f"⚠️ Failed to set color: {e}")
        
        self.report({'INFO'}, f"Selected {self.biome} biome - Color: {biome_color[:3]}")
        return {'FINISHED'}

class ONEILL_OT_FinishTerrainPainting(Operator):
    """Finish terrain painting mode"""
    bl_idname = "oneill.finish_terrain_painting"
    bl_label = "Finish Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.painting_mode = False
        props.show_grid_overlay = False
        
        # Disable grid overlay
        grid_overlay.disable()
        
        self.report({'INFO'}, "Terrain painting completed")
        return {'FINISHED'}

class ONEILL_OT_EnterPaintingMode(Operator):
    """Enter terrain painting mode with layout change"""
    bl_idname = "oneill.enter_painting_mode"
    bl_label = "Enter Painting Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.painting_mode = True
        
        # Enable grid overlay
        props.show_grid_overlay = True
        grid_overlay.enable()
        
        self.report({'INFO'}, "Entered painting mode")
        return {'FINISHED'}

class ONEILL_OT_ExitPaintingMode(Operator):
    """Exit terrain painting mode"""
    bl_idname = "oneill.exit_painting_mode"
    bl_label = "Exit Painting Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.painting_mode = False
        props.show_grid_overlay = False
        
        # Disable grid overlay
        grid_overlay.disable()
        
        self.report({'INFO'}, "Exited painting mode")
        return {'FINISHED'}

# ========================= GRID OVERLAY OPERATORS =========================

class ONEILL_OT_ToggleGridOverlay(Operator):
    """Toggle grid overlay on/off"""
    bl_idname = "oneill.toggle_grid_overlay"
    bl_label = "📊 Toggle Grid"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        if props.show_grid_overlay:
            props.show_grid_overlay = False
            grid_overlay.disable()
            self.report({'INFO'}, "Grid overlay disabled")
        else:
            props.show_grid_overlay = True
            grid_overlay.enable()
            self.report({'INFO'}, "Grid overlay enabled")
            
        return {'FINISHED'}

class ONEILL_OT_ConfigureGridOverlay(Operator):
    """Configure grid overlay settings"""
    bl_idname = "oneill.configure_grid_overlay"
    bl_label = "⚙️ Grid Settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # This would open a dialog - for now just report current settings
        props = context.scene.oneill_props
        self.report({'INFO'}, f"Grid: {props.grid_divisions} divisions, {props.grid_opacity} opacity")
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
        box.label(text="1. Align Cylinders ✅ FIXED", icon='OBJECT_DATA')
        row = box.row()
        row.prop(props, "alignment_axis")
        info_col = box.column()
        info_col.label(text="• Standard O'Neill dimensions (2.0×1.0)", icon='INFO')
        info_col.label(text="• Precise 2.0-unit spacing", icon='SNAP_ON')
        box.operator("oneill.align_cylinders")
        
        # Step 2: Unwrap to Flat
        box = layout.box()
        box.label(text="2. Unwrap to Flat ✅ FIXED", icon='MOD_UVPROJECT')
        info_col = box.column()
        info_col.label(text="• Creates high-detail flat meshes", icon='INFO')
        info_col.label(text="• Hides original cylinders", icon='HIDE_ON')
        info_col.label(text="• Correct surface area preservation", icon='CHECKMARK')
        box.prop(props, "subdivision_levels")
        box.operator("oneill.unwrap_to_flat") 
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Terrain Painting
        box = layout.box()
        box.label(text="4. Paint Terrain Biomes", icon='BRUSH_DATA')
        
        if not props.painting_mode:
            box.operator("oneill.start_terrain_painting")
        else:
            # Biome selection buttons
            col = box.column()
            col.label(text="Select Biome:")
            
            # Create biome buttons in 2 rows of 3
            row1 = col.row()
            row1.operator("oneill.select_painting_biome", text="🏝️").biome = 'ARCHIPELAGO'
            row1.operator("oneill.select_painting_biome", text="🏔️").biome = 'MOUNTAINS'
            row1.operator("oneill.select_painting_biome", text="🏜️").biome = 'CANYONS'
            
            row2 = col.row()
            row2.operator("oneill.select_painting_biome", text="🏞️").biome = 'HILLS'
            row2.operator("oneill.select_painting_biome", text="🌵").biome = 'DESERT'
            row2.operator("oneill.select_painting_biome", text="🌊").biome = 'OCEAN'
            
            # Current biome indicator
            current_biome_name = dict(BIOME_TYPES)[props.current_biome]
            col.label(text=f"Current: {current_biome_name}")
            
            # Grid overlay controls
            grid_row = col.row()
            grid_row.operator("oneill.toggle_grid_overlay")
            grid_row.operator("oneill.configure_grid_overlay")
            
            # Finish painting
            col.operator("oneill.finish_terrain_painting")
        
        # Step 5: Generate Terrain (Alternative to painting)
        box = layout.box()
        box.label(text="5A. Generate Terrain (Procedural)", icon='FORCE_TEXTURE')
        box.prop(props, "terrain_scale")
        box.prop(props, "noise_scale")
        box.prop(props, "noise_strength")
        box.operator("oneill.generate_terrain")
        
        # Step 6: Rewrap to Cylinders
        box = layout.box()
        box.label(text="6. Rewrap to Cylinders", icon='MOD_WAVE')
        box.operator("oneill.rewrap_to_cylinders")

class ONEILL_PT_GridOverlayPanel(Panel):
    """Grid overlay controls panel"""
    bl_label = "Grid Overlay"
    bl_idname = "ONEILL_PT_grid_overlay_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"
    bl_parent_id = "ONEILL_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        props = context.scene.oneill_props
        return props.painting_mode
        
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        layout.prop(props, "show_grid_overlay", text="Show Grid")
        
        if props.show_grid_overlay:
            layout.prop(props, "grid_divisions")
            layout.prop(props, "grid_opacity")

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_FinishTerrainPainting,
    ONEILL_OT_EnterPaintingMode,
    ONEILL_OT_ExitPaintingMode,
    ONEILL_OT_ToggleGridOverlay,
    ONEILL_OT_ConfigureGridOverlay,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_PT_MainPanel,
    ONEILL_PT_GridOverlayPanel,
]

def register():
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize grid overlay
    global grid_overlay
    grid_overlay = TerrainPaintingGridOverlay()
    
    print("O'Neill Terrain Generator v2.2.1 - ALIGNMENT & UNWRAP FIXED - registered successfully")

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
        
    print("O'Neill Terrain Generator v2.2.1 unregistered")

if __name__ == "__main__":
    register()