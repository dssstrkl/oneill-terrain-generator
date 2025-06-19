bl_info = {
    "name": "O'Neill Cylinder Heightmap Terrain",
    "author": "Assistant",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Clean heightmap-based terrain workflow for O'Neill cylinders",
    "category": "3D View",
}

import bpy
import bmesh
from mathutils import Vector
import math
import random

# ========================= PROPERTIES =========================

class ONeillProperties(bpy.types.PropertyGroup):
    """Main properties for O'Neill terrain system"""
    
    # Alignment
    alignment_axis: bpy.props.EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align along X-axis"),
            ('Y', "Y-Axis", "Align along Y-axis"), 
            ('Z', "Z-Axis", "Align along Z-axis"),
        ],
        default='X'
    )
    
    # Heightmap settings
    heightmap_resolution: bpy.props.EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', "512x512", "Low resolution"),
            ('1024', "1024x1024", "Medium resolution"),
            ('2048', "2048x2048", "High resolution"),
        ],
        default='1024'
    )
    
    # Terrain generation
    terrain_strength: bpy.props.FloatProperty(
        name="Terrain Strength",
        default=2.0,
        min=0.1,
        max=10.0
    )
    
    noise_scale: bpy.props.FloatProperty(
        name="Noise Scale", 
        default=5.0,
        min=0.1,
        max=20.0
    )
    
    random_seed: bpy.props.IntProperty(
        name="Random Seed",
        default=42,
        min=1,
        max=9999
    )

# ========================= OPERATORS =========================

class ONEILL_OT_AlignCylinders(bpy.types.Operator):
    """Align selected cylinder objects along chosen axis"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least 2 mesh objects")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
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
        
        self.report({'INFO'}, f"Aligned {len(selected)} objects")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(bpy.types.Operator):
    """Create flat grid objects from cylinders with UVs preserving surface area"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    subdivision_levels: bpy.props.IntProperty(
        name="Subdivision Levels",
        default=4,
        min=2, max=7
    )
    
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
            
            # Select created objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[-1]
            
            self.report({'INFO'}, f"Unwrapped {len(created)} cylinder objects preserving surface area")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        """Create flat object from cylinder based on alignment axis - preserving actual surface area"""
        original_name = obj.name
        original_location = obj.location.copy()
        
        # Calculate bounds based on alignment axis using world coordinates
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        if alignment_axis == 'X':
            # X is cylinder length, Y/Z determine radius
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
            # Y is cylinder length, X/Z determine radius
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
            # Z is cylinder length, X/Y determine radius
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
        
        # Create high-resolution grid
        segments_x = max(20, int(cylinder_length * 10))
        segments_y = max(20, int(circumference * 5))
        
        # Apply subdivision
        segments_x *= (2 ** (self.subdivision_levels - 2))
        segments_y *= (2 ** (self.subdivision_levels - 2))
        
        # Create flat mesh using bmesh (exact copy of old working method)
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
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
        
        # Position to maintain alignment relationship
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
        
        # Store metadata
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = estimated_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        unwrapped_obj["alignment_axis"] = alignment_axis
        unwrapped_obj["original_location"] = list(original_location)
        unwrapped_obj["original_center"] = [center_x, center_y]
        unwrapped_obj["subdivision_levels"] = self.subdivision_levels
        
        return unwrapped_obj

class ONEILL_OT_CreateHeightmaps(bpy.types.Operator):
    """Create heightmap raster images for selected flat objects"""
    bl_idname = "oneill.create_heightmaps"
    bl_label = "Create Heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.get("oneill_flat")]
        
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
            
            # Initialize with neutral gray
            pixels = [0.5, 0.5, 0.5, 1.0] * (resolution * resolution)
            heightmap.pixels = pixels
            heightmap.update()
            
            # Create material
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
        
        # Create nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_coord = nodes.new('ShaderNodeTexCoord')
        
        # Setup
        tex_image.image = heightmap
        
        # Connect
        links = mat.node_tree.links
        links.new(tex_coord.outputs['UV'], tex_image.inputs['Vector'])
        links.new(tex_image.outputs['Color'], shader.inputs['Base Color'])
        links.new(shader.outputs['BSDF'], output.inputs['Surface'])
        
        # Assign to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

class ONEILL_OT_GenerateTerrain(bpy.types.Operator):
    """Generate procedural terrain into heightmaps"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.get("oneill_flat")]
        
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
        """Generate noise-based heightmap data"""
        width, height = image.size
        pixels = []
        
        random.seed(props.random_seed)
        
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                noise_val = self.noise(norm_x * props.noise_scale, norm_y * props.noise_scale)
                height_val = (noise_val + 1.0) * 0.5
                height_val = max(0.0, min(1.0, height_val))
                
                pixels.extend([height_val, height_val, height_val, 1.0])
        
        image.pixels = pixels
        image.update()
    
    def noise(self, x, y):
        """Simple noise function"""
        result = 0.0
        amplitude = 1.0
        frequency = 1.0
        
        for i in range(4):
            result += math.sin(x * frequency) * math.cos(y * frequency) * amplitude
            amplitude *= 0.5
            frequency *= 2.0
        
        return result

class ONEILL_OT_RewrapToCylinder(bpy.types.Operator):
    """Convert flat objects back to cylinders matching original dimensions with heightmap terrain"""
    bl_idname = "oneill.rewrap_to_cylinder"
    bl_label = "Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    terrain_scale: bpy.props.FloatProperty(
        name="Terrain Scale", 
        default=2.0, 
        min=0.1, 
        max=10.0,
        description="Scale factor for heightmap displacement"
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects")
            return {'CANCELLED'}
        
        created = []
        
        for flat_obj in flat_objects:
            try:
                cylinder_obj = self.rewrap_to_cylinder(flat_obj, context)
                if cylinder_obj:
                    created.append(cylinder_obj)
            except Exception as e:
                self.report({'WARNING'}, f"Failed to rewrap {flat_obj.name}: {str(e)}")
                print(f"Rewrap error: {e}")
                import traceback
                traceback.print_exc()
        
        if created:
            # Hide flat objects
            for obj in flat_objects:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            # Select new terrain cylinders
            bpy.ops.object.select_all(action='DESELECT')
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[-1]
            
            self.report({'INFO'}, f"Rewrapped {len(created)} objects to terrain cylinders")
        
        return {'FINISHED'}
    
    def rewrap_to_cylinder(self, flat_obj, context):
        """Convert flat object back to cylinder matching original dimensions"""
        # Get stored metadata from unwrap process
        original_name = flat_obj.get("original_object", "Unknown")
        cylinder_radius = flat_obj.get("cylinder_radius", 2.0)
        cylinder_length = flat_obj.get("cylinder_length", 8.0)
        alignment_axis = flat_obj.get("alignment_axis", 'X')
        
        # Handle bpy property arrays correctly
        original_location_array = flat_obj.get("original_location", [0, 0, 0])
        if hasattr(original_location_array, '__iter__'):
            original_location = Vector(list(original_location_array))
        else:
            original_location = Vector([0, 0, 0])
        
        print(f"Rewrapping {flat_obj.name}:")
        print(f"  Original: {original_name}")
        print(f"  Radius: {cylinder_radius}, Length: {cylinder_length}")
        print(f"  Location: {original_location}")
        
        # Create cylinder with exact original dimensions using primitive add
        bpy.ops.mesh.primitive_cylinder_add(
            radius=cylinder_radius,
            depth=cylinder_length,
            vertices=64,  # High resolution for smooth terrain
            location=original_location
        )
        
        terrain_obj = context.active_object
        terrain_name = f"{original_name}_terrain"
        terrain_obj.name = terrain_name
        
        # Get heightmap data for displacement
        heightmap_name = flat_obj.get("heightmap_image")
        if heightmap_name and heightmap_name in bpy.data.images:
            print(f"  Applying heightmap: {heightmap_name}")
            self.apply_heightmap_displacement_to_mesh(terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length)
        else:
            print("  No heightmap found, creating basic cylinder")
        
        # Store metadata
        terrain_obj["oneill_terrain"] = True
        terrain_obj["source_flat"] = flat_obj.name
        terrain_obj["original_cylinder"] = original_name
        terrain_obj["cylinder_radius"] = cylinder_radius
        terrain_obj["cylinder_length"] = cylinder_length
        terrain_obj["terrain_scale"] = self.terrain_scale
        terrain_obj["alignment_axis"] = alignment_axis
        
        print(f"Created: {terrain_obj.name} at {terrain_obj.location}")
        return terrain_obj
    
    def apply_heightmap_displacement_to_mesh(self, terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length):
        """Apply heightmap displacement directly to mesh vertices"""
        heightmap = bpy.data.images[heightmap_name]
        width, height = heightmap.size
        pixels = list(heightmap.pixels)
        
        # Switch to edit mode to modify vertices
        bpy.context.view_layer.objects.active = terrain_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Get bmesh representation
        bm = bmesh.from_edit_mesh(terrain_obj.data)
        
        # Apply displacement to each vertex
        for vert in bm.verts:
            if alignment_axis == 'X':
                # X is length axis
                rel_pos = (vert.co.x + cylinder_length/2) / cylinder_length
                angle = math.atan2(vert.co.z, vert.co.y)
                if angle < 0:
                    angle += 2 * math.pi
                circumference_pos = angle / (2 * math.pi)
                
                # Sample heightmap
                terrain_height = self.sample_heightmap(rel_pos, circumference_pos, pixels, width, height)
                
                # Apply inward displacement for interior surface
                displacement = -terrain_height * self.terrain_scale
                current_radius = math.sqrt(vert.co.y**2 + vert.co.z**2)
                new_radius = max(current_radius + displacement, cylinder_radius * 0.1)
                
                if current_radius > 0:
                    scale_factor = new_radius / current_radius
                    vert.co.y *= scale_factor
                    vert.co.z *= scale_factor
        
        # Update mesh
        bmesh.update_edit_mesh(terrain_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        terrain_obj.data.update()
    
    def sample_heightmap(self, x, y, pixels, width, height):
        """Sample heightmap pixel value"""
        # Clamp coordinates
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        
        # Convert to pixel coordinates
        px = int(x * (width - 1)) if width > 1 else 0
        py = int(y * (height - 1)) if height > 1 else 0
        
        # Get pixel value (RGBA format, use R channel)
        pixel_idx = (py * width + px) * 4
        if pixel_idx < len(pixels):
            height_val = pixels[pixel_idx]  # R channel
            # Convert from 0-1 to -0.5 to 0.5 range for terrain
            return (height_val - 0.5)
        
        return 0.0

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(bpy.types.Panel):
    """Main O'Neill terrain panel"""
    bl_label = "O'Neill Terrain"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O'Neill'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Header
        layout.label(text="Heightmap Workflow", icon='IMAGE_DATA')
        
        # Status
        selected = len([obj for obj in context.selected_objects if obj.type == 'MESH'])
        flat_objs = len([obj for obj in bpy.data.objects if obj.get("oneill_flat")])
        heightmaps = len([img for img in bpy.data.images if "_heightmap" in img.name])
        terrain_objs = len([obj for obj in bpy.data.objects if obj.get("oneill_terrain")])
        
        box = layout.box()
        col = box.column()
        col.label(text=f"Selected: {selected}")
        col.label(text=f"Flat Objects: {flat_objs}")
        col.label(text=f"Heightmaps: {heightmaps}")
        col.label(text=f"Terrain Cylinders: {terrain_objs}")
        
        # Main workflow
        layout.separator()
        layout.label(text="Main Workflow:")
        
        col = layout.column(align=True)
        col.operator("oneill.align_cylinders", text="1. Align Cylinders")
        col.operator("oneill.unwrap_to_flat", text="2. Unwrap to Flat")
        col.operator("oneill.create_heightmaps", text="3. Create Heightmaps")
        
        # Terrain generation
        layout.separator()
        box = layout.box()
        box.label(text="Terrain Generation:")
        
        box.prop(props, "terrain_strength")
        box.prop(props, "noise_scale")
        box.prop(props, "random_seed")
        
        box.operator("oneill.generate_terrain", text="Generate Terrain")
        
        # Final step
        layout.separator()
        layout.operator("oneill.rewrap_to_cylinder", text="4. Rewrap to Cylinders")
        
        # Settings
        layout.separator()
        box = layout.box()
        box.label(text="Settings:")
        box.prop(props, "alignment_axis")
        box.prop(props, "heightmap_resolution")

# ========================= REGISTRATION =========================

classes = [
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_PT_MainPanel,
]

def register():
    # Clean up any existing O'Neill classes first
    cleanup_existing()
    
    # Register new classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {e}")
    
    # Register scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(
        type=ONeillProperties
    )
    
    print("O'Neill Heightmap Terrain System registered successfully!")

def unregister():
    # Clean up scene properties
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
            except Exception as e:
                print(f"Could not remove scene property {prop}: {e}")
    
    # Find and unregister any existing O'Neill classes
    existing_classes = []
    for name in dir(bpy.types):
        if 'ONEILL' in name or 'ONeill' in name:
            existing_classes.append(name)
    
    for class_name in existing_classes:
        if hasattr(bpy.types, class_name):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, class_name))
                print(f"Cleaned up existing class: {class_name}")
            except Exception as e:
                print(f"Could not unregister {class_name}: {e}")

if __name__ == "__main__":
    register()
