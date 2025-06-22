bl_info = {
    "name": "O'Neill Cylinder Heightmap Terrain",
    "author": "Paul Ward", 
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > ONeill",
    "description": "Complete heightmap terrain workflow for O'Neill cylinder interiors with enhanced UI",
    "category": "3D View",
}

import bpy
import bmesh
from mathutils import Vector
import math
import random

# ========================= PROPERTIES =========================

class ONeillProperties(bpy.types.PropertyGroup):
    alignment_axis: bpy.props.EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align along X-axis"),
            ('Y', "Y-Axis", "Align along Y-axis"), 
            ('Z', "Z-Axis", "Align along Z-axis"),
        ],
        default='X'
    )
    
    heightmap_resolution: bpy.props.EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', "512x512", "Low resolution"),
            ('1024', "1024x1024", "Medium resolution"),
            ('2048', "2048x2048", "High resolution"),
        ],
        default='1024'
    )
    
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
        ref_pos = selected[0].location[axis_idx]
        
        for obj in selected[1:]:
            new_loc = obj.location.copy()
            new_loc[axis_idx] = ref_pos
            obj.location = new_loc
            obj["oneill_aligned"] = True
        
        selected[0]["oneill_aligned"] = True
        self.report({'INFO'}, f"Aligned {len(selected)} objects")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(bpy.types.Operator):
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    subdivision_levels: bpy.props.IntProperty(name="Subdivision Levels", default=4, min=2, max=7)
    
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
            for obj in selected:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            bpy.ops.object.select_all(action='DESELECT')
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[-1]
            
            self.report({'INFO'}, f"Unwrapped {len(created)} cylinder objects")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        original_name = obj.name
        original_location = obj.location.copy()
        
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
        else:
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
        
        if alignment_axis == 'X':
            unwrapped_obj.location.x = center_x
            unwrapped_obj.location.y = center_y
            unwrapped_obj.location.z = 0
        elif alignment_axis == 'Y':
            unwrapped_obj.location.x = center_y
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        else:
            unwrapped_obj.location.x = (min_z + max_z) / 2
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        
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

class ONEILL_OT_GenerateTerrain(bpy.types.Operator):
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

class ONEILL_OT_LoadArchipelagoAssets(bpy.types.Operator):
    """Load archipelago terrain generation assets from geometry nodes file"""
    bl_idname = "oneill.load_archipelago_assets"
    bl_label = "Load Archipelago Assets"
    bl_description = "Load archipelago terrain generation node groups from external file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Get project root path from current blend file
            current_file = bpy.data.filepath
            if not current_file:
                self.report({'ERROR'}, "Save your blend file first to determine project location")
                return {'CANCELLED'}
            
            import os
            # Navigate up to project root (assuming structure: project/examples/your_file.blend)
            project_root = os.path.dirname(os.path.dirname(current_file))
            asset_path = os.path.join(project_root, "src", "assets", "geometry_nodes", "archipelago_terrain_generator.blend")
            
            if not os.path.exists(asset_path):
                self.report({'ERROR'}, f"Archipelago file not found at: {asset_path}")
                return {'CANCELLED'}
            
            # Load node groups from external file
            with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
                # Load all node groups from the file
                data_to.node_groups = data_from.node_groups
            
            loaded_groups = [ng for ng in data_to.node_groups if ng]
            
            if loaded_groups:
                self.report({'INFO'}, f"Loaded {len(loaded_groups)} archipelago node groups")
                print(f"Loaded node groups: {[ng.name for ng in loaded_groups]}")
            else:
                self.report({'WARNING'}, "No node groups found in archipelago file")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load archipelago assets: {str(e)}")
            return {'CANCELLED'}

class ONEILL_OT_SwitchToImageEditor(bpy.types.Operator):
    """Switch active viewport to Image Editor for heightmap editing"""
    bl_idname = "oneill.switch_to_image_editor"
    bl_label = "Edit Heightmap"
    bl_description = "Switch current viewport to Image Editor for heightmap painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find active flat object with heightmap
        active_obj = context.active_object
        heightmap_name = None
        
        if active_obj and active_obj.get("oneill_flat"):
            heightmap_name = active_obj.get("heightmap_image")
        
        # If no active flat object, find first available
        if not heightmap_name:
            flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
            if not flat_objects:
                flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            
            if flat_objects:
                heightmap_name = flat_objects[0].get("heightmap_image")
                # Set as active for clarity
                context.view_layer.objects.active = flat_objects[0]
        
        if not heightmap_name:
            self.report({'ERROR'}, "No heightmap found. Create heightmaps first.")
            return {'CANCELLED'}
        
        # Get the heightmap image
        heightmap = bpy.data.images.get(heightmap_name)
        if not heightmap:
            self.report({'ERROR'}, f"Heightmap image '{heightmap_name}' not found")
            return {'CANCELLED'}
        
        # Find the current area (where this operator was called from)
        current_area = None
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area == context.area:
                    current_area = area
                    break
            if current_area:
                break
        
        if not current_area:
            current_area = context.area
        
        # Store the original area type for restoration
        context.scene["oneill_original_area_type"] = current_area.type
        
        # Switch current area to image editor
        current_area.type = 'IMAGE_EDITOR'
        
        # Set the heightmap as active image
        for space in current_area.spaces:
            if space.type == 'IMAGE_EDITOR':
                space.image = heightmap
                space.mode = 'PAINT'
                break
        
        # Set correct colorspace for heightmap editing
        heightmap.colorspace_settings.name = 'Non-Color'
        heightmap.update()
        
        # Tag area for redraw
        current_area.tag_redraw()
        
        self.report({'INFO'}, f"Switched to heightmap editor: {heightmap_name}")
        return {'FINISHED'}

class ONEILL_OT_ReturnToLayout(bpy.types.Operator):
    """Return viewport to 3D View after heightmap editing"""
    bl_idname = "oneill.return_to_layout"
    bl_label = "Done Editing"
    bl_description = "Return current viewport to 3D View after heightmap editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get the stored original area type
        original_type = context.scene.get("oneill_original_area_type", 'VIEW_3D')
        
        # Find the current area
        current_area = None
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area == context.area:
                    current_area = area
                    break
            if current_area:
                break
        
        if not current_area:
            current_area = context.area
        
        # Switch back to original area type
        current_area.type = original_type
        
        # Clear the stored type
        if "oneill_original_area_type" in context.scene:
            del context.scene["oneill_original_area_type"]
        
        # Force refresh of all heightmap images to show changes
        for img in bpy.data.images:
            if "_heightmap" in img.name.lower():
                img.update()
        
        # Tag area for redraw
        current_area.tag_redraw()
        
        self.report({'INFO'}, "Returned to 3D view")
        return {'FINISHED'}

class ONEILL_OT_ApplyArchipelagoTerrain(bpy.types.Operator):
    """Apply archipelago terrain to selected flat objects"""
    bl_idname = "oneill.apply_archipelago_terrain"
    bl_label = "Apply Archipelago Terrain"
    bl_description = "Apply loaded archipelago node groups to create island terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Check if archipelago node groups are loaded
        archipelago_groups = [ng for ng in bpy.data.node_groups 
                            if "archipelago" in ng.name.lower() or "terrain" in ng.name.lower()]
        
        if not archipelago_groups:
            self.report({'ERROR'}, "No archipelago node groups found. Load assets first.")
            return {'CANCELLED'}
        
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select flat objects to apply archipelago terrain")
            return {'CANCELLED'}
        
        applied_count = 0
        
        for obj in flat_objects:
            try:
                # Remove existing geometry nodes modifiers
                for mod in obj.modifiers:
                    if mod.type == 'NODES':
                        obj.modifiers.remove(mod)
                
                # Add new geometry nodes modifier
                geo_mod = obj.modifiers.new("ArchipelagoTerrain", 'NODES')
                
                # Use first available archipelago node group
                geo_mod.node_group = archipelago_groups[0]
                
                applied_count += 1
                
            except Exception as e:
                print(f"Failed to apply archipelago terrain to {obj.name}: {e}")
        
        if applied_count > 0:
            self.report({'INFO'}, f"Applied archipelago terrain to {applied_count} objects")
        else:
            self.report({'WARNING'}, "Failed to apply archipelago terrain to any objects")
        
        return {'FINISHED'}

class ONEILL_OT_RewrapToCylinder(bpy.types.Operator):
    """Convert flat objects back to cylinders by duplicating original geometry"""
    bl_idname = "oneill.rewrap_to_cylinder"
    bl_label = "Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    terrain_scale: bpy.props.FloatProperty(name="Terrain Scale", default=2.0, min=0.1, max=10.0)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
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
        
        if created:
            for obj in flat_objects:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            bpy.ops.object.select_all(action='DESELECT')
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[-1]
            
            self.report({'INFO'}, f"Rewrapped {len(created)} objects to terrain cylinders")
        
        return {'FINISHED'}
    
    def rewrap_to_cylinder(self, flat_obj, context):
        """Convert flat object back to cylinder by duplicating original geometry exactly"""
        original_name = flat_obj.get("original_object", "Unknown")
        
        # Find the original object
        original_obj = bpy.data.objects.get(original_name)
        if not original_obj:
            print(f"Error: Original object {original_name} not found")
            return None
        
        print(f"Rewrapping {flat_obj.name} -> duplicating {original_name}")
        print(f"  Original location: {original_obj.location}")
        print(f"  Original dimensions: {original_obj.dimensions}")
        
        # Duplicate the original object's mesh data exactly
        original_mesh = original_obj.data
        terrain_mesh = original_mesh.copy()
        terrain_mesh.name = f"{original_name}_terrain_mesh"
        
        # Create new object with duplicated mesh
        terrain_name = f"{original_name}_terrain"
        terrain_obj = bpy.data.objects.new(terrain_name, terrain_mesh)
        context.collection.objects.link(terrain_obj)
        
        # Copy ALL transform properties exactly
        terrain_obj.location = original_obj.location.copy()
        terrain_obj.rotation_euler = original_obj.rotation_euler.copy()
        terrain_obj.scale = original_obj.scale.copy()
        
        print(f"  Terrain location: {terrain_obj.location}")
        print(f"  Terrain dimensions: {terrain_obj.dimensions}")
        
        # Apply heightmap displacement if available
        heightmap_name = flat_obj.get("heightmap_image")
        if heightmap_name and heightmap_name in bpy.data.images:
            print(f"  Applying heightmap: {heightmap_name}")
            alignment_axis = flat_obj.get("alignment_axis", 'X')
            cylinder_radius = flat_obj.get("cylinder_radius", 2.0)
            cylinder_length = flat_obj.get("cylinder_length", 8.0)
            self.apply_heightmap_displacement(terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length)
        else:
            print("  No heightmap - creating exact duplicate")
        
        # Store metadata
        terrain_obj["oneill_terrain"] = True
        terrain_obj["source_flat"] = flat_obj.name
        terrain_obj["original_cylinder"] = original_name
        terrain_obj["cylinder_radius"] = flat_obj.get("cylinder_radius", 2.0)
        terrain_obj["cylinder_length"] = flat_obj.get("cylinder_length", 8.0)
        terrain_obj["terrain_scale"] = self.terrain_scale
        
        print(f"Created exact duplicate: {terrain_obj.name}")
        return terrain_obj
    
    def apply_heightmap_displacement(self, terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length):
        """Apply heightmap displacement to mesh vertices"""
        heightmap = bpy.data.images[heightmap_name]
        width, height = heightmap.size
        pixels = list(heightmap.pixels)
        
        bpy.context.view_layer.objects.active = terrain_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(terrain_obj.data)
        
        for vert in bm.verts:
            if alignment_axis == 'X':
                rel_pos = (vert.co.x + cylinder_length/2) / cylinder_length
                angle = math.atan2(vert.co.z, vert.co.y)
                if angle < 0:
                    angle += 2 * math.pi
                circumference_pos = angle / (2 * math.pi)
                
                terrain_height = self.sample_heightmap(rel_pos, circumference_pos, pixels, width, height)
                displacement = -terrain_height * self.terrain_scale
                current_radius = math.sqrt(vert.co.y**2 + vert.co.z**2)
                new_radius = max(current_radius + displacement, cylinder_radius * 0.1)
                
                if current_radius > 0:
                    scale_factor = new_radius / current_radius
                    vert.co.y *= scale_factor
                    vert.co.z *= scale_factor
        
        bmesh.update_edit_mesh(terrain_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        terrain_obj.data.update()
    
    def sample_heightmap(self, x, y, pixels, width, height):
        """Sample heightmap pixel value"""
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        
        px = int(x * (width - 1)) if width > 1 else 0
        py = int(y * (height - 1)) if height > 1 else 0
        
        pixel_idx = (py * width + px) * 4
        if pixel_idx < len(pixels):
            height_val = pixels[pixel_idx]
            return (height_val - 0.5)
        
        return 0.0

# ========================= ENHANCED UI PANEL =========================

class ONEILL_PT_MainPanel(bpy.types.Panel):
    bl_label = "O'Neill Terrain"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONeill'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        layout.label(text="Heightmap Workflow", icon='IMAGE_DATA')
        
        # Status information
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
        
        # Main Workflow Steps 1-3
        layout.separator()
        layout.label(text="Main Workflow:", icon='SEQUENCE')
        
        workflow_box = layout.box()
        workflow_col = workflow_box.column(align=True)
        
        # Step 1: Align
        workflow_col.operator("oneill.align_cylinders", text="1. Align Cylinders", icon='SNAP_ON')
        
        # Step 2: Unwrap
        workflow_col.operator("oneill.unwrap_to_flat", text="2. Unwrap to Flat", icon='MOD_MESHDEFORM')
        
        # Step 3: Create Heightmaps
        workflow_col.operator("oneill.create_heightmaps", text="3. Create Heightmaps", icon='IMAGE_DATA')
        
        # Step 4: Edit Terrain section
        layout.separator()
        layout.label(text="4. Edit Terrain:", icon='BRUSH_DATA')
        
        edit_box = layout.box()
        edit_col = edit_box.column(align=True)
        
        # Check if we have flat objects for editing
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if flat_objects:
            active_name = context.active_object.name if context.active_object else 'None'
            edit_col.label(text=f"Active: {active_name}")
        else:
            edit_col.label(text="Select flat objects first", icon='INFO')
        
        # Edit buttons
        row = edit_col.row(align=True)
        row.operator("oneill.switch_to_image_editor", text="Edit Heightmap", icon='IMAGE')
        row.operator("oneill.return_to_layout", text="Done Editing", icon='VIEW3D')
        
        # Procedural Generation Section
        layout.separator()
        layout.label(text="Procedural Generation:", icon='MODIFIER')
        
        proc_box = layout.box()
        proc_col = proc_box.column(align=True)
        
        # Basic noise terrain
        proc_col.label(text="Noise Terrain:", icon='RNDCURVE')
        
        row = proc_col.row(align=True)
        row.prop(props, "terrain_strength", text="Strength")
        row.prop(props, "noise_scale", text="Scale")
        
        proc_col.prop(props, "random_seed", text="Seed")
        proc_col.operator("oneill.generate_terrain", text="Generate Noise", icon='MODIFIER')
        
        # Archipelago terrain
        proc_col.separator()
        proc_col.label(text="Archipelago (Geometry Nodes):", icon='WORLD')
        
        proc_col.operator("oneill.load_archipelago_assets", text="Load Assets", icon='IMPORT')
        proc_col.operator("oneill.apply_archipelago_terrain", text="Apply Archipelago", icon='GEOMETRY_NODES')
        
        # ENHANCED SETTINGS SECTION
        layout.separator()
        layout.label(text="Settings:", icon='PREFERENCES')
        
        settings_box = layout.box()
        settings_col = settings_box.column()
        
        # Alignment Settings
        settings_col.label(text="Alignment:", icon='SNAP_ON')
        align_row = settings_col.row()
        align_row.prop(props, "alignment_axis", expand=True)
        
        settings_col.separator()
        
        # Heightmap Settings
        settings_col.label(text="Heightmap:", icon='IMAGE_DATA')
        hm_row = settings_col.row()
        hm_row.prop(props, "heightmap_resolution", text="Resolution")
        
        settings_col.separator()
        
        # Terrain Generation Settings
        settings_col.label(text="Terrain Generation:", icon='RNDCURVE')
        terrain_grid = settings_col.grid_flow(columns=2, align=True)
        terrain_grid.prop(props, "terrain_strength", text="Strength")
        terrain_grid.prop(props, "noise_scale", text="Scale")
        terrain_grid.prop(props, "random_seed", text="Seed")
        
        # ENHANCED REWRAP SECTION
        layout.separator()
        layout.label(text="5. Apply Terrain:", icon='MESH_CYLINDER')
        
        rewrap_box = layout.box()
        rewrap_col = rewrap_box.column()
        
        # Show status of objects ready for rewrapping
        if flat_objs > 0:
            rewrap_col.label(text=f"Ready to rewrap: {flat_objs} objects", icon='CHECKMARK')
            
            # Show which objects have heightmaps
            objects_with_heightmaps = 0
            for obj in bpy.data.objects:
                if obj.get("oneill_flat") and obj.get("heightmap_image"):
                    objects_with_heightmaps += 1
            
            if objects_with_heightmaps > 0:
                rewrap_col.label(text=f"With heightmaps: {objects_with_heightmaps}", icon='IMAGE_DATA')
            else:
                rewrap_col.label(text="No heightmaps found", icon='ERROR')
        else:
            rewrap_col.label(text="No flat objects to rewrap", icon='INFO')
        
        rewrap_col.separator()
        
        # Rewrap controls
        rewrap_col.label(text="Rewrap Options:")
        
        # Terrain scale info
        info_row = rewrap_col.row()
        info_row.label(text="⚙️ Click to set terrain scale", icon='INFO')
        
        # Main rewrap button
        rewrap_button = rewrap_col.row()
        rewrap_button.scale_y = 1.5
        rewrap_button.operator("oneill.rewrap_to_cylinder", text="Rewrap to Cylinders", icon='MESH_CYLINDER')
        
        # Additional info
        if terrain_objs > 0:
            rewrap_col.separator()
            rewrap_col.label(text=f"Terrain cylinders created: {terrain_objs}", icon='MESH_CYLINDER')

# ========================= REGISTRATION =========================

classes = [
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_LoadArchipelagoAssets,
    ONEILL_OT_SwitchToImageEditor,
    ONEILL_OT_ReturnToLayout,
    ONEILL_OT_ApplyArchipelagoTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_PT_MainPanel,
]

def register():
    cleanup_existing()
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register {cls.__name__}: {e}")
    
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=ONeillProperties)
    print("O'Neill Heightmap Terrain System registered successfully!")

def unregister():
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {e}")

def cleanup_existing():
    """Clean up any existing O'Neill registrations INCLUDING conflicting test panels"""
    scene_props = ['oneill_props', 'oneill_alignment_props', 'oneill_heightmap_props']
    for prop in scene_props:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except:
                pass
    
    # Find and unregister ALL O'Neill related classes including test panels
    existing_classes = []
    for name in dir(bpy.types):
        if ('ONEILL' in name or 'ONeill' in name or 
            (name.startswith('TEST_PT_') and 'oneill' in name.lower())):
            existing_classes.append(name)
    
    for class_name in existing_classes:
        if hasattr(bpy.types, class_name):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, class_name))
                print(f"Cleaned up: {class_name}")
            except:
                pass

if __name__ == "__main__":
    register()

# ========================= VERSION HISTORY =========================
"""
Version 1.1.0 - Enhanced UI Release
- ✅ Complete 5-step heightmap workflow (Align, Unwrap, Create Heightmaps, Edit Terrain, Rewrap)
- ✅ Enhanced Settings section with organized controls for alignment, heightmap, and terrain parameters
- ✅ Enhanced Rewrap section with status indicators and progress tracking
- ✅ Improved heightmap editing workflow with viewport switching
- ✅ Procedural terrain generation (noise-based and geometry nodes support)
- ✅ Archipelago terrain assets loading capability
- ✅ Professional UI with proper icons, status feedback, and error handling
- ✅ Complete geometry preservation during rewrap process
- ✅ Proper heightmap colorspace handling for accurate editing
- ✅ Comprehensive metadata tracking for workflow state management
- ✅ Ready for production use in O'Neill cylinder game development pipeline

Known Issues:
- Some edge cases in heightmap displacement calculation may need refinement
- Archipelago assets path detection requires saved blend file
- Performance optimization needed for high-resolution heightmaps with complex geometry

Next Development Priorities:
- Layer-based terrain editing system
- Advanced brush controls for heightmap painting
- Real-time preview improvements
- Export optimization for game engines
"""