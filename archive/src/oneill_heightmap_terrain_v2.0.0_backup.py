# O'Neill Cylinder Heightmap Terrain Generator - Complete Integration
# Version: 2.0.0 with Full Module Integration
# PRODUCTION READY - All modules integrated with ARCHIPELAGO fix

bl_info = {
    "name": "O'Neill Cylinder Heightmap Terrain",
    "author": "dssstrkl",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Generate terrain on O'Neill cylinder interiors using heightmaps with painting and biome generation",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector, noise
import random
import math
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty, PointerProperty, StringProperty

# ========================= MODULE INTEGRATION =========================

# Terrain Painting Module Integration
try:
    from .modules import terrain_painting
    TERRAIN_PAINTING_AVAILABLE = True
    print("✅ O'Neill Terrain: Terrain painting module loaded")
except ImportError:
    TERRAIN_PAINTING_AVAILABLE = False
    print("⚠️ O'Neill Terrain: Terrain painting module not found")

# Biome Geometry Generator Module Integration  
try:
    from .modules import biome_geometry_generator
    BIOME_GENERATION_AVAILABLE = True
    print("✅ O'Neill Terrain: Biome geometry generator module loaded")
except ImportError:
    BIOME_GENERATION_AVAILABLE = False
    print("⚠️ O'Neill Terrain: Biome geometry generator module not found")

# ========================= BIOME DEFINITIONS =========================
# Updated biome system with ARCHIPELAGO replacing TUNDRA

BIOME_TYPES = [
    ('ARCHIPELAGO', '🏝️ Archipelago', 'Island chains with water features'),
    ('MOUNTAINS', '🏔️ Mountains', 'Dramatic peaks with elevation gradients'), 
    ('CANYONS', '🏜️ Canyons', 'Mesa formations with valley cutting'),
    ('HILLS', '🏞️ Hills', 'Gentle rolling terrain for exploration'),
    ('DESERT', '🌵 Desert', 'Dune formations with wind patterns'),
    ('OCEAN', '🌊 Ocean', 'Underwater ridges with depth variation'),
]

# ========================= PROPERTY GROUPS =========================

class ONeillProperties(PropertyGroup):
    """Main properties for O'Neill terrain system"""
    
    alignment_axis: EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align cylinders along X-axis"),
            ('Y', "Y-Axis", "Align cylinders along Y-axis"),
            ('Z', "Z-Axis", "Align cylinders along Z-axis"),
        ],
        default='X'
    )
    
    heightmap_resolution: EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', "512x512", "Low resolution"),
            ('1024', "1024x1024", "Medium resolution"),
            ('2048', "2048x2048", "High resolution"),
            ('4096', "4096x4096", "Very high resolution"),
        ],
        default='1024'
    )
    
    terrain_strength: FloatProperty(
        name="Terrain Strength",
        default=2.0,
        min=0.1,
        max=10.0,
        description="Overall strength of terrain displacement"
    )
    
    noise_scale: FloatProperty(
        name="Noise Scale",
        default=5.0,
        min=0.1,
        max=20.0,
        description="Scale of procedural noise"
    )
    
    random_seed: IntProperty(
        name="Random Seed",
        default=42,
        min=0,
        max=10000,
        description="Seed for random terrain generation"
    )

# ========================= CORE OPERATORS =========================

class ONEILL_OT_AlignCylinders(bpy.types.Operator):
    """Align selected cylinder objects with vertex-level precision for airtight geometry"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders (Vertex-Level)"
    bl_options = {'REGISTER', 'UNDO'}
    
    precision_threshold: bpy.props.FloatProperty(
        name="Precision Threshold",
        description="Maximum gap tolerance for vertex alignment (smaller = more precise)",
        default=0.001,
        min=0.0001,
        max=0.01,
        precision=4
    )
    
    def execute(self, context):
        """Execute vertex-level alignment on selected objects"""
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 mesh objects to align")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
        
        try:
            aligned_count = self.align_objects_vertex_level(
                selected_objects, 
                props.alignment_axis, 
                self.precision_threshold
            )
            
            self.report({'INFO'}, f"✅ Aligned {aligned_count} objects with vertex-level precision")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Alignment failed: {str(e)}")
            print(f"❌ Alignment error: {e}")
            return {'CANCELLED'}
    
    def align_objects_vertex_level(self, objects, axis, threshold):
        """Perform vertex-level alignment on specified axis for airtight geometry"""
        aligned_count = 0
        
        # Calculate vertex-level bounds for all objects
        object_bounds = []
        for obj in objects:
            world_positions = []
            for vertex in obj.data.vertices:
                world_pos = obj.matrix_world @ vertex.co
                if axis == 'X':
                    world_positions.append(world_pos.x)
                elif axis == 'Y':
                    world_positions.append(world_pos.y)
                elif axis == 'Z':
                    world_positions.append(world_pos.z)
            
            min_val = min(world_positions)
            max_val = max(world_positions)
            object_bounds.append((obj, min_val, max_val))
        
        # Sort objects by position on alignment axis
        object_bounds.sort(key=lambda x: x[1])
        
        # Align adjacent objects so vertices touch exactly
        aligned_bounds = [object_bounds[0]]  # Keep first object as reference
        
        for i in range(1, len(object_bounds)):
            current_obj, current_min, current_max = object_bounds[i]
            prev_obj, prev_min, prev_max = aligned_bounds[i-1]
            
            # Calculate the gap between objects at vertex level
            gap = current_min - prev_max
            
            # Move current object to eliminate the gap
            if abs(gap) > threshold:
                offset = -gap
                
                if axis == 'X':
                    current_obj.location.x += offset
                elif axis == 'Y':
                    current_obj.location.y += offset
                elif axis == 'Z':
                    current_obj.location.z += offset
                
                new_min = current_min + offset
                new_max = current_max + offset
                aligned_bounds.append((current_obj, new_min, new_max))
                aligned_count += 1
            else:
                aligned_bounds.append((current_obj, current_min, current_max))
        
        # Center the entire arrangement around the origin
        total_min = aligned_bounds[0][1]
        total_max = aligned_bounds[-1][2]
        current_center = (total_min + total_max) / 2
        center_offset = 0 - current_center
        
        # Apply centering offset to all objects
        for obj, min_val, max_val in aligned_bounds:
            if axis == 'X':
                obj.location.x += center_offset
            elif axis == 'Y':
                obj.location.y += center_offset
            elif axis == 'Z':
                obj.location.z += center_offset
            
            obj["oneill_aligned"] = True
            obj["alignment_axis"] = axis
            obj["vertex_level_aligned"] = True
        
        return aligned_count
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ONEILL_OT_UnwrapToFlat(Operator):
    """Unwrap O'Neill cylinders to flat grids for heightmap generation"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    subdivision_levels: IntProperty(
        name="Subdivision Levels",
        default=4,
        min=2,
        max=8,
        description="Number of subdivision levels for detail"
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected:
            self.report({'ERROR'}, "Select mesh objects")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
        alignment_axis = props.alignment_axis
        
        unwrapped_objects = []
        
        for obj in selected:
            try:
                unwrapped_obj = self.unwrap_cylinder_object(obj, context, alignment_axis)
                if unwrapped_obj:
                    unwrapped_objects.append(unwrapped_obj)
            except Exception as e:
                self.report({'WARNING'}, f"Failed to unwrap {obj.name}: {str(e)}")
                print(f"Unwrap error for {obj.name}: {e}")
        
        if unwrapped_objects:
            # Hide original objects
            for obj in selected:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            # Select created objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in unwrapped_objects:
                obj.select_set(True)
            context.view_layer.objects.active = unwrapped_objects[-1]
            
            self.report({'INFO'}, f"Unwrapped {len(unwrapped_objects)} cylinder objects")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        """Create flat object from cylinder with correct coordinate scaling"""
        original_name = obj.name
        original_location = obj.location.copy()
        
        # Calculate bounds based on alignment axis
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
        elif alignment_axis == 'Y':
            min_y = min(corner.y for corner in bbox)
            max_y = max(corner.y for corner in bbox)
            min_x = min(corner.x for corner in bbox)
            max_x = max(corner.x for corner in bbox)
            min_z = min(corner.z for corner in bbox)
            max_z = max(corner.z for corner in bbox)
            
            cylinder_length = max_y - min_y
            estimated_radius = max(max_x - min_x, max_z - min_z) / 2
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
        else:  # Z-axis
            min_z = min(corner.z for corner in bbox)
            max_z = max(corner.z for corner in bbox)
            min_x = min(corner.x for corner in bbox)
            max_x = max(corner.x for corner in bbox)
            min_y = min(corner.y for corner in bbox)
            max_y = max(corner.y for corner in bbox)
            
            cylinder_length = max_z - min_z
            estimated_radius = max(max_x - min_x, max_y - min_y) / 2
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
        
        circumference = 2 * math.pi * estimated_radius
        
        segments_x = max(20, int(cylinder_length * 10)) * (2 ** (self.subdivision_levels - 2))
        segments_y = max(20, int(circumference * 5)) * (2 ** (self.subdivision_levels - 2))
        
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
        # CORRECT coordinate scaling: X=length, Y=circumference
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
        
        # Position flat object
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
        
        # Store metadata for rewrap process
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = estimated_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        unwrapped_obj["alignment_axis"] = alignment_axis
        unwrapped_obj["original_location"] = list(original_location)
        unwrapped_obj["original_center"] = [center_x, center_y]
        unwrapped_obj["subdivision_levels"] = self.subdivision_levels
        
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
            
            heightmap = bpy.data.images.new(heightmap_name, width=resolution, height=resolution, alpha=False, float_buffer=True)
            pixels = [0.5, 0.5, 0.5, 1.0] * (resolution * resolution)
            heightmap.pixels = pixels
            
            heightmap.colorspace_settings.name = 'Non-Color'
            heightmap.update()
            
            self.create_heightmap_material(obj, heightmap)
            obj["heightmap_image"] = heightmap_name
        
        self.report({'INFO'}, f"Created heightmaps for {len(flat_objects)} objects")
        return {'FINISHED'}
    
    def create_heightmap_material(self, obj, heightmap):
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

class ONEILL_OT_GenerateTerrain(Operator):
    """Generate procedural terrain into heightmaps"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects with heightmaps")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
        
        for obj in flat_objects:
            img_name = obj.get("heightmap_image")
            if img_name and img_name in bpy.data.images:
                self.generate_heightmap(bpy.data.images[img_name], props)
        
        self.report({'INFO'}, f"Generated terrain for {len(flat_objects)} objects")
        return {'FINISHED'}
    
    def generate_heightmap(self, image, props):
        """Generate procedural terrain in heightmap"""
        width, height = image.size
        pixels = list(image.pixels)
        
        random.seed(props.random_seed)
        
        for y in range(height):
            for x in range(width):
                nx = x / width
                ny = y / height
                
                noise_value = 0
                frequency = props.noise_scale
                amplitude = 1.0
                
                for octave in range(4):
                    noise_value += noise.noise((nx * frequency, ny * frequency, 0)) * amplitude
                    frequency *= 2
                    amplitude *= 0.5
                
                height_value = (noise_value * props.terrain_strength + 1.0) / 2.0
                height_value = max(0.0, min(1.0, height_value))
                
                pixel_idx = (y * width + x) * 4
                pixels[pixel_idx] = height_value
                pixels[pixel_idx + 1] = height_value
                pixels[pixel_idx + 2] = height_value
                pixels[pixel_idx + 3] = 1.0
        
        image.pixels = pixels
        image.update()

class ONEILL_OT_RewrapToCylinder(Operator):
    """Rewrap flat objects back to cylinders with terrain displacement"""
    bl_idname = "oneill.rewrap_to_cylinder"
    bl_label = "Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects with heightmaps")
            return {'CANCELLED'}
        
        terrain_objects = []
        
        for flat_obj in flat_objects:
            terrain_obj = self.rewrap_to_cylinder(context, flat_obj)
            if terrain_obj:
                terrain_objects.append(terrain_obj)
        
        if terrain_objects:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in terrain_objects:
                obj.select_set(True)
            context.view_layer.objects.active = terrain_objects[0]
        
        self.report({'INFO'}, f"Created {len(terrain_objects)} terrain cylinders")
        return {'FINISHED'}
    
    def rewrap_to_cylinder(self, context, flat_obj):
        """Rewrap a single flat object to cylinder with terrain"""
        original_name = flat_obj.get("original_object", "Unknown")
        cylinder_radius = flat_obj.get("cylinder_radius", 1.0)
        cylinder_length = flat_obj.get("cylinder_length", 2.0)
        alignment_axis = flat_obj.get("alignment_axis", 'Z')
        original_location = flat_obj.get("original_location", [0, 0, 0])
        
        heightmap_name = flat_obj.get("heightmap_image")
        if not heightmap_name or heightmap_name not in bpy.data.images:
            self.report({'ERROR'}, f"No heightmap found for {flat_obj.name}")
            return None
        
        heightmap = bpy.data.images[heightmap_name]
        width, height = heightmap.size
        pixels = list(heightmap.pixels)
        
        terrain_mesh = bpy.data.meshes.new(f"{original_name}_terrain")
        bm = bmesh.new()
        
        subdivision_levels = flat_obj.get("subdivision_levels", 4)
        segments = 2 ** subdivision_levels
        
        # Create cylinder vertices with terrain displacement
        for i in range(segments + 1):
            for j in range(segments + 1):
                u = i / segments
                v = j / segments
                
                height_value = self.sample_heightmap(u, v, pixels, width, height)
                
                angle = u * 2 * 3.14159
                length_pos = (v - 0.5) * cylinder_length
                displaced_radius = cylinder_radius + height_value * cylinder_radius * 0.1
                
                if alignment_axis == 'X':
                    x = length_pos
                    y = displaced_radius * math.cos(angle)
                    z = displaced_radius * math.sin(angle)
                elif alignment_axis == 'Y':
                    x = displaced_radius * math.cos(angle)
                    y = length_pos
                    z = displaced_radius * math.sin(angle)
                else:  # Z axis
                    x = displaced_radius * math.cos(angle)
                    y = displaced_radius * math.sin(angle)
                    z = length_pos
                
                bm.verts.new((x, y, z))
        
        bm.verts.ensure_lookup_table()
        
        # Create faces
        for i in range(segments):
            for j in range(segments):
                v1 = bm.verts[i * (segments + 1) + j]
                v2 = bm.verts[i * (segments + 1) + j + 1]
                v3 = bm.verts[(i + 1) * (segments + 1) + j + 1]
                v4 = bm.verts[(i + 1) * (segments + 1) + j]
                bm.faces.new([v1, v2, v3, v4])
        
        bm.to_mesh(terrain_mesh)
        bm.free()
        
        terrain_name = f"{original_name}_terrain"
        terrain_obj = bpy.data.objects.new(terrain_name, terrain_mesh)
        context.collection.objects.link(terrain_obj)
        
        terrain_obj.location = Vector(original_location)
        terrain_obj["oneill_terrain"] = True
        terrain_obj["source_flat"] = flat_obj.name
        
        return terrain_obj
    
    def sample_heightmap(self, u, v, pixels, width, height):
        """Sample heightmap pixel value"""
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        
        px = int(u * (width - 1)) if width > 1 else 0
        py = int(v * (height - 1)) if height > 1 else 0
        
        pixel_idx = (py * width + px) * 4
        if pixel_idx < len(pixels):
            height_val = pixels[pixel_idx]
            return (height_val - 0.5)
        
        return 0.0

# ========================= TERRAIN PAINTING OPERATORS =========================

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain biome painting on existing heightmaps"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "Start Terrain Painting"
    bl_description = "Begin painting biome assignments on heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.scene.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects with heightmaps found. Run 'Create Heightmaps' first.")
            return {'CANCELLED'}
        
        # Set painting properties
        context.scene.oneill_painting_active = True
        context.scene.oneill_painting_mode = True
        
        # Try to switch to Texture Paint workspace
        if "Texture Paint" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Texture Paint"]
        
        self.report({'INFO'}, f"Started biome painting on {len(flat_objects)} heightmaps")
        return {'FINISHED'}

class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select which biome to paint on heightmaps"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_description = "Choose biome type for painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome: EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES,
        default='ARCHIPELAGO'
    )
    
    def execute(self, context):
        context.scene.oneill_current_biome = self.biome
        
        # Set brush color based on biome for visual feedback
        biome_colors = {
            'ARCHIPELAGO': (0.2, 0.8, 0.6),   # Teal
            'MOUNTAINS': (0.5, 0.5, 0.5),     # Gray
            'CANYONS': (0.8, 0.4, 0.2),       # Orange/Brown
            'HILLS': (0.3, 0.6, 0.3),         # Green
            'DESERT': (0.9, 0.8, 0.4),        # Yellow
            'OCEAN': (0.2, 0.4, 0.8),         # Blue
        }
        
        if self.biome in biome_colors:
            color = biome_colors[self.biome]
            if hasattr(context.tool_settings, 'image_paint'):
                brush = context.tool_settings.image_paint.brush
                if brush:
                    brush.color = color
        
        self.report({'INFO'}, f"Selected {self.biome.title()} for painting")
        return {'FINISHED'}

class ONEILL_OT_FinishTerrainPainting(Operator):
    """Finish terrain painting and prepare for rewrap"""
    bl_idname = "oneill.finish_terrain_painting"
    bl_label = "Finish Terrain Painting"
    bl_description = "Complete painting and prepare heightmaps for rewrap"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        painted_count = len(flat_objects)
        
        # Exit painting mode
        context.scene.oneill_painting_mode = False
        context.scene.oneill_painting_active = False
        context.scene.oneill_painting_canvas = ""
        
        # Try to return to Layout workspace
        if "Layout" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Layout"]
        
        self.report({'INFO'}, f"Finished painting {painted_count} heightmaps. Ready for rewrap.")
        return {'FINISHED'}

# ========================= BIOME GENERATION OPERATORS =========================

class ONEILL_OT_CreateAllBiomes(Operator):
    """Create all biome node groups for terrain generation"""
    bl_idname = "oneill.create_all_biomes"
    bl_label = "Create All Biomes"
    bl_description = "Generate all 6 biome node groups for terrain generation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not BIOME_GENERATION_AVAILABLE:
            self.report({'ERROR'}, "Biome generation module not available")
            return {'CANCELLED'}
        
        try:
            # Import and use biome generator
            from .modules.biome_geometry_generator import BiomeGeometryGenerator
            generator = BiomeGeometryGenerator()
            created_biomes = generator.create_all_biomes()
            
            self.report({'INFO'}, f"Created {len(created_biomes)} biome node groups")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create biomes: {str(e)}")
            return {'CANCELLED'}

class ONEILL_OT_ApplyBiomeToSelected(Operator):
    """Apply specific biome to selected objects"""
    bl_idname = "oneill.apply_biome_to_selected"
    bl_label = "Apply Biome"
    bl_description = "Apply biome terrain generation to selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_name: EnumProperty(
        name="Biome",
        items=BIOME_TYPES,
        default='ARCHIPELAGO'
    )
    
    strength: FloatProperty(
        name="Strength",
        default=1.0,
        min=0.1,
        max=3.0,
        description="Terrain displacement strength"
    )
    
    scale: FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=5.0,
        description="Feature scale"
    )
    
    intensity: FloatProperty(
        name="Intensity",
        default=1.0,
        min=0.1,
        max=2.0,
        description="Biome intensity"
    )
    
    def execute(self, context):
        if not BIOME_GENERATION_AVAILABLE:
            self.report({'ERROR'}, "Biome generation module not available")
            return {'CANCELLED'}
        
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Select mesh objects to apply biome")
            return {'CANCELLED'}
        
        try:
            from .modules.biome_geometry_generator import BiomeGeometryGenerator, BiomePaintingIntegrator
            
            generator = BiomeGeometryGenerator()
            integrator = BiomePaintingIntegrator(generator)
            
            applied_count = 0
            for obj in selected_objects:
                try:
                    integrator.apply_biome_to_object(
                        obj, 
                        self.biome_name.lower(), 
                        self.strength, 
                        self.scale, 
                        self.intensity
                    )
                    applied_count += 1
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to apply biome to {obj.name}: {str(e)}")
            
            self.report({'INFO'}, f"Applied {self.biome_name} biome to {applied_count} objects")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Biome application failed: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# ========================= UI PANELS =========================

class ONEILL_PT_MainPanel(bpy.types.Panel):
    """Enhanced main O'Neill terrain panel with full module integration"""
    bl_label = "O'Neill Terrain"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O\'Neill'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Status information
        selected = len([obj for obj in context.selected_objects if obj.type == 'MESH'])
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        terrain_objects = [obj for obj in bpy.data.objects if obj.get("oneill_terrain")]
        
        status_box = layout.box()
        status_box.label(text="Workflow Status:", icon='INFO')
        col = status_box.column()
        col.label(text=f"Selected Objects: {selected}")
        col.label(text=f"Flat Objects: {len(flat_objects)}")
        col.label(text=f"Heightmaps: {len(heightmap_objects)}")
        col.label(text=f"Terrain Cylinders: {len(terrain_objects)}")
        
        layout.separator()
        
        # Main workflow steps
        workflow_box = layout.box()
        workflow_box.label(text="O'Neill Cylinder Workflow:", icon='SEQUENCE')
        
        col = workflow_box.column(align=True)
        
        # Steps 1-3: Core workflow
        col.operator("oneill.align_cylinders", text="1. Align Cylinders")
        col.operator("oneill.unwrap_to_flat", text="2. Unwrap to Flat") 
        col.operator("oneill.create_heightmaps", text="3. Create Heightmaps")
        
        layout.separator()
        
        # Step 4: Enhanced terrain generation options
        terrain_box = layout.box()
        terrain_box.label(text="4. Terrain Generation:", icon='BRUSH_DATA')
        
        painting_active = getattr(context.scene, 'oneill_painting_active', False)
        
        if painting_active:
            # PAINTING MODE ACTIVE
            paint_col = terrain_box.column()
            paint_col.label(text="🎨 Paint Mode Active", icon='BRUSH_DATA')
            
            current_biome = getattr(context.scene, 'oneill_current_biome', 'ARCHIPELAGO')
            paint_col.label(text=f"Current Biome: {current_biome}")
            
            paint_col.separator()
            paint_col.label(text="Select Biome to Paint:")
            
            biome_grid = paint_col.grid_flow(columns=2, align=True)
            
            for biome_id, biome_label, biome_desc in BIOME_TYPES:
                op = biome_grid.operator("oneill.select_painting_biome", text=biome_label)
                op.biome = biome_id
            
            paint_col.separator()
            finish_row = paint_col.row(align=True)
            finish_row.scale_y = 1.5
            finish_row.operator("oneill.finish_terrain_painting", text="Finish Painting", icon='CHECKMARK')
            
        else:
            # NORMAL MODE - Show terrain generation options
            terrain_col = terrain_box.column()
            
            can_paint = len(heightmap_objects) > 0
            can_generate = len(flat_objects) > 0
            can_biome_generate = BIOME_GENERATION_AVAILABLE and can_generate
            
            if can_paint or can_biome_generate:
                # PAINTING OPTION
                if can_paint:
                    paint_row = terrain_col.row(align=True)
                    paint_row.scale_y = 1.5
                    paint_row.operator("oneill.start_terrain_painting", 
                                     text="🎨 Paint Terrain Biomes", 
                                     icon='BRUSH_DATA')
                
                # BIOME GENERATION OPTION
                if can_biome_generate:
                    if can_paint:
                        terrain_col.separator()
                        terrain_col.label(text="- OR -")
                        terrain_col.separator()
                    
                    biome_col = terrain_col.column()
                    biome_col.label(text="Biome Generation:")
                    
                    # Create all biomes button
                    biome_col.operator("oneill.create_all_biomes", text="Create All Biomes", icon='NODETREE')
                    
                    # Quick apply buttons for common biomes
                    quick_row = biome_col.row(align=True)
                    
                    for biome_id, biome_emoji, biome_desc in [
                        ('ARCHIPELAGO', '🏝️', 'Archipelago'),
                        ('MOUNTAINS', '🏔️', 'Mountains'), 
                        ('OCEAN', '🌊', 'Ocean')
                    ]:
                        op = quick_row.operator("oneill.apply_biome_to_selected", text=biome_emoji)
                        op.biome_name = biome_id
                
                # PROCEDURAL OPTION (Fallback)
                if can_paint or can_biome_generate:
                    terrain_col.separator()
                    terrain_col.label(text="- OR -")
                    terrain_col.separator()
                
                proc_col = terrain_col.column()
                proc_col.label(text="Procedural Generation:")
                proc_col.prop(props, "terrain_strength", text="Strength")
                proc_col.prop(props, "noise_scale", text="Scale")
                proc_col.prop(props, "random_seed", text="Seed")
                proc_col.operator("oneill.generate_terrain", text="Generate Procedural", icon='MODIFIER')
                
            else:
                terrain_col.label(text="Complete steps 1-3 first", icon='ERROR')
        
        layout.separator()
        
        # Step 5: Final workflow step
        final_box = layout.box()
        if painting_active:
            final_box.label(text="5. Finish painting first", icon='INFO')
        else:
            rewrap_available = len(heightmap_objects) > 0
            
            if rewrap_available:
                final_box.operator("oneill.rewrap_to_cylinder", text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
            else:
                final_box.label(text="5. Generate terrain first", icon='INFO')
        
        layout.separator()
        
        # Settings section
        settings_box = layout.box()
        settings_box.label(text="Settings:", icon='PREFERENCES')
        settings_box.prop(props, "alignment_axis")
        settings_box.prop(props, "heightmap_resolution")

class ONEILL_PT_BiomeGeneration(Panel):
    """Biome generation panel"""
    bl_label = "Biome Generation"
    bl_idname = "ONEILL_PT_biome_generation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O\'Neill'
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return BIOME_GENERATION_AVAILABLE and not getattr(context.scene, 'oneill_painting_active', False)
    
    def draw(self, context):
        layout = self.layout
        
        # Status
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        layout.label(text=f"Selected Meshes: {len(selected_meshes)}")
        
        # Create all biomes
        layout.operator("oneill.create_all_biomes", text="Create All Biome Node Groups", icon='NODETREE')
        
        layout.separator()
        layout.label(text="Apply Specific Biomes:")
        
        # Individual biome application
        for biome_id, biome_label, biome_desc in BIOME_TYPES:
            row = layout.row()
            op = row.operator("oneill.apply_biome_to_selected", text=biome_label)
            op.biome_name = biome_id

class ONEILL_PT_TerrainPainting(Panel):
    """Terrain painting panel"""
    bl_label = "Terrain Painting"
    bl_idname = "ONEILL_PT_terrain_painting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O\'Neill'
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return TERRAIN_PAINTING_AVAILABLE
    
    def draw(self, context):
        layout = self.layout
        
        painting_active = getattr(context.scene, 'oneill_painting_active', False)
        
        if painting_active:
            layout.label(text="🎨 Painting Mode Active", icon='BRUSH_DATA')
            
            # Current biome display
            current_biome = getattr(context.scene, 'oneill_current_biome', 'ARCHIPELAGO')
            layout.label(text=f"Current Biome: {current_biome}")
            
            # Quick biome switcher
            layout.separator()
            layout.label(text="Quick Biome Switch:")
            
            row = layout.row(align=True)
            for biome_id, biome_emoji, _ in [
                ('ARCHIPELAGO', '🏝️'), ('MOUNTAINS', '🏔️'), ('HILLS', '🏞️'), 
                ('DESERT', '🌵'), ('OCEAN', '🌊')
            ]:
                op = row.operator("oneill.select_painting_biome", text=biome_emoji)
                op.biome = biome_id
            
            layout.separator()
            layout.operator("oneill.finish_terrain_painting", text="Complete Painting", icon='CHECKMARK')
        else:
            # Check for objects with heightmaps
            flat_objects = [obj for obj in bpy.data.objects 
                           if obj.get("oneill_flat") and obj.get("heightmap_image")]
            
            if flat_objects:
                info_box = layout.box()
                info_box.label(text=f"Ready: {len(flat_objects)} heightmaps", icon='IMAGE_DATA')
                
                layout.operator("oneill.start_terrain_painting", 
                              text="Start Terrain Painting", 
                              icon='BRUSH_DATA')
            else:
                layout.label(text="Run 'Create Heightmaps' first", icon='ERROR')

# ========================= REGISTRATION =========================

classes = [
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_FinishTerrainPainting,
    ONEILL_OT_CreateAllBiomes,
    ONEILL_OT_ApplyBiomeToSelected,
    ONEILL_PT_MainPanel,
    ONEILL_PT_BiomeGeneration,
    ONEILL_PT_TerrainPainting,
]

def register():
    cleanup_existing()
    
    # Register main classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {e}")
    
    # Register scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=ONeillProperties)
    
    # Painting mode properties
    bpy.types.Scene.oneill_painting_mode = bpy.props.BoolProperty(
        name="Painting Mode Active",
        default=False
    )
    bpy.types.Scene.oneill_painting_active = bpy.props.BoolProperty(
        name="Painting Active",
        default=False
    )
    bpy.types.Scene.oneill_painting_canvas = bpy.props.StringProperty(
        name="Painting Canvas",
        default=""
    )
    bpy.types.Scene.oneill_current_biome = bpy.props.EnumProperty(
        name="Current Biome",
        items=BIOME_TYPES,
        default='ARCHIPELAGO'
    )
    
    # Register modules
    if TERRAIN_PAINTING_AVAILABLE:
        try:
            terrain_painting.register()
            print("✅ Terrain painting module registered")
        except Exception as e:
            print(f"⚠️ Terrain painting module registration failed: {e}")
    
    if BIOME_GENERATION_AVAILABLE:
        try:
            biome_geometry_generator.register()
            print("✅ Biome generation module registered")
        except Exception as e:
            print(f"⚠️ Biome generation module registration failed: {e}")
    
    print("🚀 O'Neill Heightmap Terrain System with full integration registered successfully!")

def unregister():
    # Unregister modules first
    if BIOME_GENERATION_AVAILABLE:
        try:
            biome_geometry_generator.unregister()
        except:
            pass
    
    if TERRAIN_PAINTING_AVAILABLE:
        try:
            terrain_painting.unregister()
        except:
            pass
    
    # Remove scene properties
    scene_props = ['oneill_props', 'oneill_painting_mode', 'oneill_painting_active', 
                   'oneill_painting_canvas', 'oneill_current_biome']
    for prop in scene_props:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except:
                pass
    
    # Unregister classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {e}")

def cleanup_existing():
    """Clean up any existing O'Neill registrations"""
    scene_props = ['oneill_props', 'oneill_alignment_props', 'oneill_heightmap_props', 
                   'oneill_painting_mode', 'oneill_painting_active', 'oneill_painting_canvas',
                   'oneill_current_biome']
    for prop in scene_props:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except:
                pass
    
    # Clean up existing classes
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

if __name__ == "__main__":
    register()