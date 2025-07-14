# O'Neill Cylinder Heightmap Terrain Generator - Integrated with Painting
# Version: 1.2.0 with Heightmap Painting Integration - FIXED UNWRAP COORDINATES

bl_info = {
    "name": "O'Neill Cylinder Heightmap Terrain",
    "author": "dssstrkl",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Generate terrain on O'Neill cylinder interiors using heightmaps with painting",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector, noise
import random
import math
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty, PointerProperty

# Near top of file with other imports
try:
    from .modules import terrain_painting
    TERRAIN_PAINTING_AVAILABLE = True
except ImportError:
    TERRAIN_PAINTING_AVAILABLE = False
    print("O'Neill Terrain: Terrain painting module not found")

# In register() function
def register():
    # ... existing registration code ...
    
    # Register terrain painting system
    if TERRAIN_PAINTING_AVAILABLE:
        terrain_painting.register()

# In unregister() function  
def unregister():
    # Unregister terrain painting system
    if TERRAIN_PAINTING_AVAILABLE:
        terrain_painting.unregister()
    
    # ... existing unregistration code ...

# Modify main panel to include painting button
class ONEILL_PT_MainPanel(Panel):
    def draw(self, context):
        # ... existing UI code ...
        
        # Add after "Create Heightmaps" step
        if TERRAIN_PAINTING_AVAILABLE:
            if any(obj.get('oneill_heightmap_name') for obj in context.scene.objects):
                row = layout.row()
                row.operator("oneill.start_terrain_painting", icon='BRUSH_DATA')

# Near top of file with other imports (after terrain_painting import)
try:
    from .modules import biome_geometry_generator
    BIOME_GENERATION_AVAILABLE = True
except ImportError:
    BIOME_GENERATION_AVAILABLE = False
    print("O'Neill Terrain: Biome geometry generator module not found")

# In register() function
def register():
    # ... existing registration code ...
    
    # Register terrain painting system
    if TERRAIN_PAINTING_AVAILABLE:
        terrain_painting.register()
    
    # Register biome generation system
    if BIOME_GENERATION_AVAILABLE:
        biome_geometry_generator.register()

# In unregister() function  
def unregister():
    # Unregister biome generation system
    if BIOME_GENERATION_AVAILABLE:
        biome_geometry_generator.unregister()
    
    # Unregister terrain painting system
    if TERRAIN_PAINTING_AVAILABLE:
        terrain_painting.unregister()
    
    # ... existing unregistration code ...

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
        default='X'  # FIXED: Default to X for O'Neill cylinders
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
            
            # Success message
            self.report({'INFO'}, f"✅ Aligned {aligned_count} objects with vertex-level precision")
            
            # Log success details
            total_objects = len(selected_objects)
            total_span = self.get_total_span(selected_objects, props.alignment_axis)
            
            print(f"\n🎉 Vertex-Level Alignment Complete!")
            print(f"   Objects processed: {total_objects}")
            print(f"   Objects adjusted: {aligned_count}")
            print(f"   Total span: {total_span:.3f} units")
            print(f"   Axis: {props.alignment_axis}")
            print(f"   Precision: {self.precision_threshold:.4f}")
            print(f"   Status: Ready for airtight joining with Ctrl+J")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Alignment failed: {str(e)}")
            print(f"❌ Alignment error: {e}")
            return {'CANCELLED'}
    
    def align_objects_vertex_level(self, objects, axis, threshold):
        """
        Perform vertex-level alignment on specified axis for airtight geometry.
        
        This implementation ensures that adjacent objects touch exactly at the 
        vertex level, creating geometry that can be joined without gaps.
        
        Args:
            objects: List of mesh objects to align
            axis: 'X', 'Y', or 'Z' - axis along which to align
            threshold: Maximum gap tolerance (0.001 for precision alignment)
            
        Returns:
            int: Number of objects that were moved during alignment
        """
        aligned_count = 0
        
        print(f"\n🔧 Starting vertex-level alignment on {axis}-axis...")
        print(f"   Objects to align: {len(objects)}")
        print(f"   Precision threshold: {threshold:.4f}")
        
        # Step 1: Calculate vertex-level bounds for all objects
        object_bounds = []
        for obj in objects:
            # Get all vertex positions in world space
            world_positions = []
            for vertex in obj.data.vertices:
                world_pos = obj.matrix_world @ vertex.co
                if axis == 'X':
                    world_positions.append(world_pos.x)
                elif axis == 'Y':
                    world_positions.append(world_pos.y)
                elif axis == 'Z':
                    world_positions.append(world_pos.z)
            
            # Calculate actual mesh bounds (not object bounds)
            min_val = min(world_positions)
            max_val = max(world_positions)
            length = max_val - min_val
            
            object_bounds.append((obj, min_val, max_val))
            print(f"   {obj.name}: {axis}={min_val:.3f} to {max_val:.3f} (length={length:.3f})")
        
        # Step 2: Sort objects by position on alignment axis (left to right)
        object_bounds.sort(key=lambda x: x[1])
        
        print(f"\n📊 Sorted order (left to right on {axis}-axis):")
        for i, (obj, min_val, max_val) in enumerate(object_bounds):
            print(f"   {i+1}. {obj.name}: {axis}={min_val:.3f} to {max_val:.3f}")
        
        # Step 3: Align adjacent objects so vertices touch exactly
        print(f"\n🎯 Applying vertex-level alignment...")
        aligned_bounds = [object_bounds[0]]  # Keep first object as reference
        
        for i in range(1, len(object_bounds)):
            current_obj, current_min, current_max = object_bounds[i]
            prev_obj, prev_min, prev_max = aligned_bounds[i-1]
            
            # Calculate the gap between objects at vertex level
            gap = current_min - prev_max
            
            # Move current object to eliminate the gap (make vertices touch exactly)
            if abs(gap) > threshold:
                # Calculate offset needed to make vertices touch
                offset = -gap
                
                # Apply offset to object location
                if axis == 'X':
                    current_obj.location.x += offset
                elif axis == 'Y':
                    current_obj.location.y += offset
                elif axis == 'Z':
                    current_obj.location.z += offset
                
                # Update bounds for the aligned object
                new_min = current_min + offset
                new_max = current_max + offset
                aligned_bounds.append((current_obj, new_min, new_max))
                
                print(f"   ✅ {current_obj.name}: moved by {offset:.4f}, now {axis}={new_min:.3f} to {new_max:.3f}")
                aligned_count += 1
            else:
                # Object is already close enough - no movement needed
                aligned_bounds.append((current_obj, current_min, current_max))
                print(f"   ✓ {current_obj.name}: already aligned (gap={gap:.6f})")
        
        # Step 4: Center the entire arrangement around the origin
        total_min = aligned_bounds[0][1]
        total_max = aligned_bounds[-1][2]
        total_length = total_max - total_min
        
        # Calculate offset to center around origin on the alignment axis
        current_center = (total_min + total_max) / 2
        center_offset = 0 - current_center
        
        print(f"\n🎯 Centering arrangement around origin:")
        print(f"   Current span: {axis}={total_min:.3f} to {total_max:.3f} (length={total_length:.3f})")
        print(f"   Current center: {current_center:.3f}")
        print(f"   Center offset: {center_offset:.3f}")
        
        # Apply centering offset to all objects
        for obj, min_val, max_val in aligned_bounds:
            if axis == 'X':
                obj.location.x += center_offset
            elif axis == 'Y':
                obj.location.y += center_offset
            elif axis == 'Z':
                obj.location.z += center_offset
            
            final_min = min_val + center_offset
            final_max = max_val + center_offset
            print(f"   📍 {obj.name}: final position {axis}={final_min:.3f} to {final_max:.3f}")
            
            # Mark object as aligned for workflow tracking
            obj["oneill_aligned"] = True
            obj["alignment_axis"] = axis
            obj["vertex_level_aligned"] = True  # New flag for vertex-level alignment
        
        print(f"\n✅ Vertex-level alignment complete!")
        print(f"   • {len(objects)} objects aligned with {axis}-axis precision")
        print(f"   • Total span: {total_length:.3f} units, centered at origin")
        print(f"   • Maximum gap: < {threshold:.4f} units")
        print(f"   • Ready for manual joining with Ctrl+J if desired")
        
        return aligned_count
    
    def get_total_span(self, objects, axis):
        """Calculate total span of objects along specified axis"""
        all_positions = []
        for obj in objects:
            for vertex in obj.data.vertices:
                world_pos = obj.matrix_world @ vertex.co
                if axis == 'X':
                    all_positions.append(world_pos.x)
                elif axis == 'Y':
                    all_positions.append(world_pos.y)
                elif axis == 'Z':
                    all_positions.append(world_pos.z)
        
        return max(all_positions) - min(all_positions) if all_positions else 0.0
    
    def invoke(self, context, event):
        """Show precision settings dialog before executing"""
        return context.window_manager.invoke_props_dialog(self)

class ONEILL_OT_UnwrapToFlat(Operator):
    """Unwrap O'Neill cylinders to flat grids for heightmap generation - FIXED COORDINATES"""
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
                import traceback
                traceback.print_exc()
        
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
            
            self.report({'INFO'}, f"Unwrapped {len(unwrapped_objects)} cylinder objects preserving surface area")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        """Create flat object from cylinder based on alignment axis - FIXED COORDINATE SCALING
        
        This version fixes the critical bug where X and Y coordinates were swapped in scaling,
        causing flat objects to have circumference in X-axis and cylinder length in Y-axis
        instead of the correct cylinder length in X-axis and circumference in Y-axis.
        """
        original_name = obj.name
        original_location = obj.location.copy()
        
        # Calculate bounds based on alignment axis using world coordinates
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
        
        # CRITICAL FIX: Correct coordinate scaling
        # X-axis gets cylinder_length (along alignment axis)
        # Y-axis gets circumference (around the cylinder)
        # Previous implementation had these swapped!
        for vert in bm_new.verts:
            vert.co.x = vert.co.x * (cylinder_length / 2)    # CORRECT: cylinder length in X
            vert.co.y = vert.co.y * (circumference / 2)      # CORRECT: circumference in Y
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
        
        # Store complete metadata for rewrap process
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
            
            # Set correct colorspace for heightmap editing
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
        
        # Generate terrain using Blender noise
        for y in range(height):
            for x in range(width):
                # Normalize coordinates
                nx = x / width
                ny = y / height
                
                # Generate multi-octave noise
                noise_value = 0
                frequency = props.noise_scale
                amplitude = 1.0
                
                for octave in range(4):
                    noise_value += noise.noise((nx * frequency, ny * frequency, 0)) * amplitude
                    frequency *= 2
                    amplitude *= 0.5
                
                # Apply terrain strength and normalize to 0-1 range
                height_value = (noise_value * props.terrain_strength + 1.0) / 2.0
                height_value = max(0.0, min(1.0, height_value))
                
                # Set pixel (RGBA format)
                pixel_idx = (y * width + x) * 4
                pixels[pixel_idx] = height_value      # R
                pixels[pixel_idx + 1] = height_value  # G
                pixels[pixel_idx + 2] = height_value  # B
                pixels[pixel_idx + 3] = 1.0           # A
        
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
            # Select new terrain objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in terrain_objects:
                obj.select_set(True)
            context.view_layer.objects.active = terrain_objects[0]
        
        self.report({'INFO'}, f"Created {len(terrain_objects)} terrain cylinders")
        return {'FINISHED'}
    
    def rewrap_to_cylinder(self, context, flat_obj):
        """Rewrap a single flat object to cylinder with terrain"""
        
        # Get stored metadata
        original_name = flat_obj.get("original_object", "Unknown")
        cylinder_radius = flat_obj.get("cylinder_radius", 1.0)
        cylinder_length = flat_obj.get("cylinder_length", 2.0)
        alignment_axis = flat_obj.get("alignment_axis", 'Z')
        original_location = flat_obj.get("original_location", [0, 0, 0])
        
        # Get heightmap
        heightmap_name = flat_obj.get("heightmap_image")
        if not heightmap_name or heightmap_name not in bpy.data.images:
            self.report({'ERROR'}, f"No heightmap found for {flat_obj.name}")
            return None
        
        heightmap = bpy.data.images[heightmap_name]
        width, height = heightmap.size
        pixels = list(heightmap.pixels)
        
        # Create new mesh for terrain cylinder
        terrain_mesh = bpy.data.meshes.new(f"{original_name}_terrain")
        bm = bmesh.new()
        
        # Get subdivision level from flat object
        subdivision_levels = flat_obj.get("subdivision_levels", 4)
        segments = 2 ** subdivision_levels
        
        # Create cylinder vertices with terrain displacement
        for i in range(segments + 1):
            for j in range(segments + 1):
                # Calculate UV coordinates
                u = i / segments
                v = j / segments
                
                # Sample heightmap
                height_value = self.sample_heightmap(u, v, pixels, width, height)
                
                # Calculate cylinder position
                angle = u * 2 * 3.14159
                length_pos = (v - 0.5) * cylinder_length
                
                # Apply terrain displacement
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
        
        # Create object
        terrain_name = f"{original_name}_terrain"
        terrain_obj = bpy.data.objects.new(terrain_name, terrain_mesh)
        context.collection.objects.link(terrain_obj)
        
        # Position at original location
        terrain_obj.location = Vector(original_location)
        terrain_obj["oneill_terrain"] = True
        terrain_obj["source_flat"] = flat_obj.name
        
        return terrain_obj
    
    def sample_heightmap(self, u, v, pixels, width, height):
        """Sample heightmap pixel value"""
        # Clamp coordinates
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        
        # Convert to pixel coordinates
        px = int(u * (width - 1)) if width > 1 else 0
        py = int(v * (height - 1)) if height > 1 else 0
        
        # Get pixel value (RGBA format, use R channel)
        pixel_idx = (py * width + px) * 4
        if pixel_idx < len(pixels):
            height_val = pixels[pixel_idx]  # R channel
            # Convert from 0-1 to -0.5 to 0.5 range for terrain
            return (height_val - 0.5)
        
        return 0.0

# ========================= HEIGHTMAP PAINTING OPERATORS =========================

class ONEILL_OT_start_heightmap_painting(Operator):
    """Start terrain biome painting on existing heightmaps"""
    bl_idname = "oneill.start_heightmap_painting"
    bl_label = "Start Terrain Painting"
    bl_description = "Begin painting biome assignments on heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find flat objects with heightmaps
        flat_objects = [obj for obj in context.scene.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects with heightmaps found. Run 'Create Heightmaps' first.")
            return {'CANCELLED'}
        
        # Create unified canvas from heightmaps
        canvas = self.create_unified_canvas(flat_objects)
        if not canvas:
            self.report({'ERROR'}, "Failed to create painting canvas")
            return {'CANCELLED'}
        
        # Set painting properties
        context.scene.oneill_painting_active = True
        context.scene.oneill_painting_mode = True
        context.scene.oneill_painting_canvas = canvas.name
        
        # Switch to Image Editor and load canvas
        self.setup_painting_workspace(context, canvas)
        
        self.report({'INFO'}, f"Started biome painting on {len(flat_objects)} heightmaps")
        return {'FINISHED'}
    
    def create_unified_canvas(self, flat_objects):
        """Create horizontal concatenated canvas from heightmaps"""
        if not flat_objects:
            return None
        
        # Get heightmap images
        heightmaps = []
        total_width = 0
        max_height = 0
        
        for obj in flat_objects:
            heightmap_name = obj.get("heightmap_image")
            if heightmap_name and heightmap_name in bpy.data.images:
                img = bpy.data.images[heightmap_name]
                heightmaps.append(img)
                total_width += img.size[0]
                max_height = max(max_height, img.size[1])
        
        if not heightmaps:
            return None
        
        # Create canvas image
        canvas_name = "TerrainPainting_Canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
        
        canvas = bpy.data.images.new(
            canvas_name,
            width=total_width,
            height=max_height,
            alpha=False
        )
        
        # Copy heightmap data horizontally
        canvas_pixels = [0.5] * (total_width * max_height * 4)  # RGBA
        current_x = 0
        
        for img in heightmaps:
            img_width, img_height = img.size
            img_pixels = list(img.pixels)
            
            # Copy pixels to canvas
            for y in range(img_height):
                for x in range(img_width):
                    img_idx = (y * img_width + x) * 4
                    canvas_idx = (y * total_width + (current_x + x)) * 4
                    
                    # Copy RGBA
                    for c in range(4):
                        canvas_pixels[canvas_idx + c] = img_pixels[img_idx + c]
            
            current_x += img_width
        
        canvas.pixels = canvas_pixels
        canvas.update()
        return canvas
    
    def setup_painting_workspace(self, context, canvas):
        """Switch to workspace with Image Editor and load canvas"""
        # Try to switch to Texture Paint workspace (has Image Editor)
        if "Texture Paint" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Texture Paint"]
        
        # Find Image Editor and load canvas
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                space = area.spaces.active
                space.image = canvas
                # Enable paint mode
                space.mode = 'PAINT'
                break
        else:
            # If no Image Editor, split current area
            bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
            # Set new area to Image Editor
            context.area.type = 'IMAGE_EDITOR'
            context.space_data.image = canvas
            context.space_data.mode = 'PAINT'

class ONEILL_OT_select_painting_biome(Operator):
    """Select which biome to paint on heightmaps"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_description = "Choose biome type for painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome: EnumProperty(
        name="Biome Type",
        items=[
            ('MOUNTAINS', "Mountains", "Paint mountain terrain"),
            ('CANYONS', "Canyons", "Paint canyon terrain"),
            ('HILLS', "Hills", "Paint rolling hills"),
            ('DESERT', "Desert", "Paint desert terrain"),
            ('OCEAN', "Ocean", "Paint ocean/water areas"),
        ],
        default='MOUNTAINS'
    )
    
    def execute(self, context):
        context.scene.oneill_current_biome = self.biome
        
        # Set brush color based on biome for visual feedback
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),  # Gray
            'CANYONS': (0.8, 0.4, 0.2),    # Orange/Brown
            'HILLS': (0.3, 0.6, 0.3),      # Green
            'DESERT': (0.9, 0.8, 0.4),     # Yellow
            'OCEAN': (0.2, 0.4, 0.8),      # Blue
        }
        
        if self.biome in biome_colors:
            color = biome_colors[self.biome]
            # Set paint brush color for visual feedback
            if hasattr(context.tool_settings, 'image_paint'):
                brush = context.tool_settings.image_paint.brush
                if brush:
                    brush.color = color
        
        self.report({'INFO'}, f"Selected {self.biome.title()} for painting")
        return {'FINISHED'}

class ONEILL_OT_finish_heightmap_painting(Operator):
    """Finish terrain painting and prepare for rewrap"""
    bl_idname = "oneill.finish_heightmap_painting"
    bl_label = "Finish Terrain Painting"
    bl_description = "Complete painting and prepare heightmaps for rewrap"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find painted heightmaps
        flat_objects = [obj for obj in bpy.data.objects 
                    if obj.get("oneill_flat") and obj.get("heightmap_image")]
    
        painted_count = len(flat_objects)
    
        # Exit painting mode - clear BOTH properties
        context.scene.oneill_painting_mode = False
        context.scene.oneill_painting_active = False
        context.scene.oneill_painting_canvas = ""  # Clear canvas name too
    
        # Try to return to Layout workspace
        if "Layout" in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces["Layout"]
    
        self.report({'INFO'}, f"Finished painting {painted_count} heightmaps. Ready for rewrap.")
        return {'FINISHED'}

# ========================= UI PANELS =========================

# Enhanced O'Neill Main Panel with Paint Mode Integration
# Add this enhanced panel class to your oneill_heightmap_terrain_dev.py

class ONEILL_PT_MainPanel(bpy.types.Panel):
    """Enhanced main O'Neill terrain panel with paint mode integration"""
    bl_label = "O'Neill Terrain"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O\'Neill'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Development version warning (if applicable)
        if "dev" in __file__.lower():
            dev_box = layout.box()
            dev_box.label(text="🚧 DEVELOPMENT VERSION", icon='ERROR')
            dev_box.label(text="Testing Phase 2A Integration")
        
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
        
        # Step 1-3: Core O'Neill workflow (preserved from original)
        col.operator("oneill.align_cylinders", text="1. Align Cylinders")
        col.operator("oneill.unwrap_to_flat", text="2. Unwrap to Flat") 
        col.operator("oneill.create_heightmaps", text="3. Create Heightmaps")
        
        layout.separator()
        
        # ======= ENHANCED STEP 4: TERRAIN GENERATION OPTIONS =======
        terrain_box = layout.box()
        terrain_box.label(text="4. Terrain Generation:", icon='BRUSH_DATA')
        
        # Check if we're in painting mode
        painting_active = getattr(context.scene, 'oneill_painting_active', False)
        
        if painting_active:
            # PAINTING MODE ACTIVE - Show painting controls
            paint_col = terrain_box.column()
            paint_col.label(text="🎨 Paint Mode Active", icon='BRUSH_DATA')
            
            # Current biome display
            current_biome = getattr(context.scene, 'oneill_current_biome', 'HILLS')
            paint_col.label(text=f"Current Biome: {current_biome}")
            
            # Biome selection buttons
            paint_col.separator()
            paint_col.label(text="Select Biome to Paint:")
            
            biome_grid = paint_col.grid_flow(columns=2, align=True)
            
            biomes = [
                ('MOUNTAINS', "🏔️ Mountains", 'MESH_ICOSPHERE'),
                ('CANYONS', "🏜️ Canyons", 'MESH_LANDSCAPE'),
                ('HILLS', "🏞️ Hills", 'SURFACE_NCIRCLE'),
                ('DESERT', "🌵 Desert", 'MESH_GRID'),
                ('OCEAN', "🌊 Ocean", 'MOD_FLUIDSIM')
            ]
            
            for biome_id, biome_label, icon in biomes:
                op = biome_grid.operator("oneill.select_painting_biome", text=biome_label, icon=icon)
                op.biome = biome_id
                # Highlight current biome
                if current_biome == biome_id:
                    # Visual indication of current biome (would need custom styling for full effect)
                    pass
            
            # Painting workflow controls
            paint_col.separator()
            paint_col.label(text="Canvas Info:")
            canvas = bpy.data.images.get("Terrain_Painting_Canvas")
            if canvas:
                paint_col.label(text=f"Size: {canvas.size[0]}x{canvas.size[1]}")
            
            # Finish painting
            paint_col.separator()
            finish_row = paint_col.row(align=True)
            finish_row.scale_y = 1.5
            finish_row.operator("oneill.finish_terrain_painting", text="Finish Painting", icon='CHECKMARK')
            
        else:
            # NORMAL MODE - Show terrain generation options
            terrain_col = terrain_box.column()
            
            # Check prerequisites for painting mode
            can_paint = len(heightmap_objects) > 0
            can_generate = len(flat_objects) > 0
            
            if can_paint:
                # PAINT MODE OPTION (Primary recommendation)
                paint_row = terrain_col.row(align=True)
                paint_row.scale_y = 1.5
                paint_row.operator("oneill.start_terrain_painting", 
                                 text="🎨 Paint Terrain Biomes (Manual)", 
                                 icon='BRUSH_DATA')
                
                terrain_col.separator()
                terrain_col.label(text="- OR -")
                terrain_col.separator()
                
                # PROCEDURAL OPTION (Alternative)
                proc_col = terrain_col.column()
                proc_col.label(text="Procedural Generation:")
                proc_col.prop(props, "terrain_strength", text="Strength")
                proc_col.prop(props, "noise_scale", text="Scale")
                proc_col.prop(props, "random_seed", text="Seed")
                proc_col.operator("oneill.generate_terrain", text="Generate Procedural Terrain", icon='MODIFIER')
                
            elif can_generate:
                # Only procedural available
                terrain_col.label(text="Create heightmaps first for painting mode", icon='INFO')
                terrain_col.separator()
                
                terrain_col.prop(props, "terrain_strength")
                terrain_col.prop(props, "noise_scale") 
                terrain_col.prop(props, "random_seed")
                terrain_col.operator("oneill.generate_terrain", text="Generate Terrain", icon='MODIFIER')
                
            else:
                # No terrain generation possible
                terrain_col.label(text="Complete steps 1-3 first", icon='ERROR')
        
        layout.separator()
        
        # Step 5: Final workflow step
        final_box = layout.box()
        if painting_active:
            final_box.label(text="5. Finish painting first", icon='INFO')
        else:
            rewrap_available = len(heightmap_objects) > 0 or len([obj for obj in flat_objects if obj.get("terrain_generated")]) > 0
            
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
        
        # Show painting integration panel when in paint mode
        if painting_active:
            layout.separator()
            paint_panel_box = layout.box()
            paint_panel_box.label(text="Advanced Painting Controls:", icon='TOOL_SETTINGS')
            paint_panel_box.label(text="Switch to Image Editor for canvas painting")
            paint_panel_box.label(text="Use standard Blender paint tools")


# Enhanced painting integration panel (already exists, but ensure it's working)
class ONEILL_PT_HeightmapPaintingIntegration(bpy.types.Panel):
    """Enhanced painting integration panel"""
    bl_label = "Terrain Painting"
    bl_idname = "ONEILL_PT_heightmap_painting_integration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O\'Neill'
    bl_parent_id = "ONEILL_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        # Only show when painting is active
        return getattr(context.scene, 'oneill_painting_active', False)
    
    def draw(self, context):
        layout = self.layout
        
        painting_active = getattr(context.scene, 'oneill_painting_active', False)
        
        if painting_active:
            layout.label(text="🎨 Painting Mode Active", icon='BRUSH_DATA')
            
            # Quick biome switcher
            layout.separator()
            layout.label(text="Quick Biome Switch:")
            
            row = layout.row(align=True)
            for biome_id, emoji in [('MOUNTAINS', '🏔️'), ('CANYONS', '🏜️'), ('HILLS', '🏞️'), ('DESERT', '🌵'), ('OCEAN', '🌊')]:
                op = row.operator("oneill.select_painting_biome", text=emoji)
                op.biome = biome_id
            
            # Canvas management
            layout.separator()
            layout.label(text="Canvas Management:")
            
            canvas = bpy.data.images.get("Terrain_Painting_Canvas")
            if canvas:
                layout.label(text=f"Canvas: {canvas.size[0]}x{canvas.size[1]}")
                
                # Switch to image editor button
                layout.operator("wm.context_set_enum", text="Switch to Image Editor").data_path = "area.type"
                layout.operator("wm.context_set_enum", text="Switch to Image Editor").value = "IMAGE_EDITOR"
            
            layout.separator()
            layout.operator("oneill.finish_terrain_painting", text="Complete Painting", icon='CHECKMARK')
        else:
            layout.label(text="Start terrain painting to access controls")


# Registration update - make sure both panels are registered
enhanced_classes = [
    ONEILL_PT_MainPanel,  # Enhanced main panel
    ONEILL_PT_HeightmapPaintingIntegration,  # Enhanced painting panel
]

def register_enhanced_panels():
    """Register enhanced panels (call this in your main register function)"""
    for cls in enhanced_classes:
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered enhanced panel: {cls.__name__}")
        except Exception as e:
            print(f"⚠️ Enhanced panel registration issue: {e}")

def unregister_enhanced_panels():
    """Unregister enhanced panels (call this in your main unregister function)"""
    for cls in reversed(enhanced_classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass

class ONEILL_PT_heightmap_painting_integration(Panel):
    """Heightmap Painting Integration Panel"""
    bl_label = "Terrain Painting"
    bl_idname = "ONEILL_PT_heightmap_painting_integration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Status with enhanced visual feedback
        if hasattr(scene, 'oneill_painting_mode') and scene.oneill_painting_mode:
            box = layout.box()
            box.alert = True
            row = box.row()
            row.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
        else:
            layout.label(text="4. Paint Terrain Biomes", icon='TEXTURE')
        
        layout.separator()
        
        # Check for objects with heightmaps
        flat_objects = [obj for obj in bpy.data.objects 
                       if obj.get("oneill_flat") and obj.get("heightmap_image")]
        
        if flat_objects:
            # Enhanced status information
            info_box = layout.box()
            info_box.label(text=f"Ready: {len(flat_objects)} heightmaps", icon='IMAGE_DATA')
            
            # Show resolution info
            if flat_objects:
                sample_obj = flat_objects[0]
                heightmap_name = sample_obj.get("heightmap_image")
                if heightmap_name and heightmap_name in bpy.data.images:
                    heightmap = bpy.data.images[heightmap_name]
                    resolution = f"{heightmap.size[0]}x{heightmap.size[1]}"
                    info_box.label(text=f"Resolution: {resolution}", icon='SETTINGS')
        else:
            layout.label(text="Run 'Create Heightmaps' first", icon='ERROR')
            return
        
        # Main painting controls
        if not (hasattr(scene, 'oneill_painting_mode') and scene.oneill_painting_mode):
            col = layout.column()
            col.scale_y = 1.5
            col.operator("oneill.start_heightmap_painting", 
                        text="Start Terrain Painting", 
                        icon='BRUSH_DATA')
            
            # Add helpful instructions
            layout.separator()
            help_box = layout.box()
            help_box.label(text="Instructions:", icon='INFO')
            help_col = help_box.column(align=True)
            help_col.scale_y = 0.8
            help_col.label(text="• Paint directly on heightmaps")
            help_col.label(text="• Different colors = biome types")
            help_col.label(text="• Use Image Editor paint tools")
            
        else:
            # Enhanced biome selection with visual improvements
            biome_box = layout.box()
            biome_box.label(text="Select Biome:", icon='MATERIAL')
            
            current_biome = getattr(scene, 'oneill_current_biome', 'MOUNTAINS')
            current_row = biome_box.row()
            current_row.alert = True
            current_row.label(text=f"Active: {current_biome.title()}", icon='BRUSH_DATA')
            
            layout.separator()
            
            # Organized biome grid with better layout
            biome_grid = layout.grid_flow(columns=2, align=True)
            biome_grid.scale_y = 1.2
            
            # Mountains
            op = biome_grid.operator("oneill.select_painting_biome", text="🏔️ Mountains")
            op.biome = 'MOUNTAINS'
            
            # Canyons  
            op = biome_grid.operator("oneill.select_painting_biome", text="🏜️ Canyons")
            op.biome = 'CANYONS'
            
            # Hills
            op = biome_grid.operator("oneill.select_painting_biome", text="🏞️ Hills")
            op.biome = 'HILLS'
            
            # Desert
            op = biome_grid.operator("oneill.select_painting_biome", text="🌵 Desert")
            op.biome = 'DESERT'
            
            # Ocean (full width)
            col = layout.column()
            col.scale_y = 1.2
            op = col.operator("oneill.select_painting_biome", text="🌊 Ocean")
            op.biome = 'OCEAN'
            
            layout.separator()
            
            # Enhanced finish controls
            finish_box = layout.box()
            finish_box.label(text="Complete Painting:", icon='CHECKMARK')
            col = finish_box.column()
            col.scale_y = 1.4
            col.operator("oneill.finish_heightmap_painting", 
                        text="Finish Painting", 
                        icon='FILE_TICK')
            
            # Add painting tips
            layout.separator()
            tips_box = layout.box()
            tips_box.label(text="Painting Tips:", icon='LIGHTBULB')
            tips_col = tips_box.column(align=True)
            tips_col.scale_y = 0.8
            tips_col.label(text="• Use soft brushes for natural blending")
            tips_col.label(text="• Paint with varying opacity")
            tips_col.label(text="• Combine biomes for realism")

# ========================= REGISTRATION =========================

classes = [
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_OT_start_heightmap_painting,
    ONEILL_OT_select_painting_biome,
    ONEILL_OT_finish_heightmap_painting,
    ONEILL_PT_MainPanel,
    ONEILL_PT_heightmap_painting_integration,
]

def register():
    cleanup_existing()
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {e}")
    
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=ONeillProperties)
    
    # Add painting mode properties
    bpy.types.Scene.oneill_painting_mode = bpy.props.BoolProperty(
        name="Painting Mode Active",
        default=False
    )
    bpy.types.Scene.oneill_current_biome = bpy.props.EnumProperty(
        name="Current Biome",
        items=[
            ('MOUNTAINS', "Mountains", ""),
            ('CANYONS', "Canyons", ""),
            ('HILLS', "Hills", ""),
            ('DESERT', "Desert", ""),
            ('OCEAN', "Ocean", ""),
        ],
        default='MOUNTAINS'
    )
    
    print("O'Neill Heightmap Terrain System with Painting registered successfully!")

def unregister():
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
    if hasattr(bpy.types.Scene, 'oneill_painting_mode'):
        del bpy.types.Scene.oneill_painting_mode
    if hasattr(bpy.types.Scene, 'oneill_current_biome'):
        del bpy.types.Scene.oneill_current_biome
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {e}")

def cleanup_existing():
    """Clean up any existing O'Neill registrations"""
    scene_props = ['oneill_props', 'oneill_alignment_props', 'oneill_heightmap_props', 
                   'oneill_painting_mode', 'oneill_current_biome']
    for prop in scene_props:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except:
                pass
    
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