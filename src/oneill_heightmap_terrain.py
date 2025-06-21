bl_info = {
    "name": "O'Neill Cylinder Heightmap Terrain",
    "author": "Assistant", 
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Heightmap terrain workflow with modular geometry nodes for O'Neill cylinders",
    "category": "3D View",
}

import bpy
import bmesh
from mathutils import Vector
import math
import random
import os

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
    
    terrain_scale_multiplier: bpy.props.FloatProperty(
        name="Terrain Scale",
        description="Multiplier for terrain displacement visibility",
        default=1.0,
        min=0.1,
        max=5.0
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

# ========================= GEOMETRY NODES ASSET MANAGER =========================

class GeometryNodesAssetManager:
    """Manages loading and using geometry node groups from the assets folder"""
    
    @staticmethod
    def get_asset_folder_path():
        """Get the path to the geometry nodes assets folder in the project structure"""
        current_file = bpy.data.filepath
        if not current_file:
            print("ERROR: Save the .blend file first to use geometry node assets")
            return None
        
        # Get directory of current .blend file
        current_dir = os.path.dirname(current_file)
        print(f"Current .blend file directory: {current_dir}")
        
        # Look for the project root by finding "oneill terrain generator" folder
        project_root = None
        if "oneill terrain generator" in current_dir:
            # Extract the project root path
            parts = current_dir.split("oneill terrain generator")
            project_root = parts[0] + "oneill terrain generator"
            print(f"Found project root: {project_root}")
        
        if not project_root:
            print("Could not find 'oneill terrain generator' project root")
            return None
        
        # The assets are in src/assets/geometry_nodes/
        assets_path = os.path.join(project_root, "src", "assets", "geometry_nodes")
        
        if os.path.exists(assets_path):
            print(f"Found assets folder: {assets_path}")
            return assets_path
        else:
            print(f"Assets folder not found at: {assets_path}")
            return None
    
    @staticmethod
    def get_available_node_assets():
        """Get list of available .blend files in the assets folder"""
        asset_folder = GeometryNodesAssetManager.get_asset_folder_path()
        if not asset_folder:
            return []
        
        assets = []
        try:
            for file in os.listdir(asset_folder):
                if file.endswith('.blend'):
                    assets.append({
                        'name': file[:-6],  # Remove .blend extension
                        'path': os.path.join(asset_folder, file),
                        'description': f"Geometry nodes from {file}"
                    })
            print(f"Found {len(assets)} geometry node assets: {[a['name'] for a in assets]}")
        except Exception as e:
            print(f"Error reading assets folder: {e}")
        
        return assets
    
    @staticmethod
    def import_node_group(asset_name, node_group_name=None):
        """Import a specific node group from an asset file"""
        assets = GeometryNodesAssetManager.get_available_node_assets()
        asset_file = None
        
        # Find the asset file
        for asset in assets:
            if asset['name'] == asset_name:
                asset_file = asset['path']
                break
        
        if not asset_file:
            print(f"Asset '{asset_name}' not found. Available: {[a['name'] for a in assets]}")
            return None
        
        try:
            # Check if the node group already exists
            if node_group_name and node_group_name in bpy.data.node_groups:
                print(f"Node group '{node_group_name}' already exists, using existing")
                return bpy.data.node_groups[node_group_name]
            
            # Import the node group(s) from the asset file
            with bpy.data.libraries.load(asset_file, link=False) as (data_from, data_to):
                # If specific node group name provided, import only that one
                if node_group_name:
                    if node_group_name in data_from.node_groups:
                        data_to.node_groups = [node_group_name]
                        print(f"Importing specific node group: {node_group_name}")
                    else:
                        print(f"Node group '{node_group_name}' not found in {asset_file}")
                        print(f"Available node groups: {data_from.node_groups}")
                        return None
                else:
                    # Import all node groups from the file
                    data_to.node_groups = data_from.node_groups[:]
                    print(f"Importing all node groups: {data_from.node_groups}")
            
            # Return the imported node group
            if node_group_name:
                imported_group = bpy.data.node_groups.get(node_group_name)
                if imported_group:
                    print(f"Successfully imported node group: {node_group_name}")
                    return imported_group
            else:
                # Return first imported node group if no specific name given
                for ng_name in data_from.node_groups:
                    if ng_name in bpy.data.node_groups:
                        print(f"Successfully imported node group: {ng_name}")
                        return bpy.data.node_groups[ng_name]
            
        except Exception as e:
            print(f"Error importing node group from {asset_file}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    @staticmethod
    def get_terrain_displacement_node_group():
        """Get the terrain displacement node group, importing if necessary"""
        # First check if it already exists in the current file
        existing_names = [
            "ONeill_Terrain_Displacement",
            "Terrain_Displacement", 
            "HeightmapDisplacement",
            "terrain_displacement"
        ]
        
        for name in existing_names:
            if name in bpy.data.node_groups:
                print(f"Using existing terrain node group: {name}")
                return bpy.data.node_groups[name]
        
        # Try to import from assets
        print("No existing terrain node group found, importing from assets...")
        
        # Try importing from the terrain displacement asset
        # First try the archipelago asset that exists in your project
        node_group = GeometryNodesAssetManager.import_node_group(
            "archipelago_terrain_generator", 
            "ONeill_Terrain_Displacement"
        )
        
        if node_group:
            return node_group
        
        # Try alternative node group names that might be in the archipelago file
        alternative_names = [
            "Terrain_Displacement",
            "HeightmapDisplacement", 
            "archipelago_terrain_generator",
            "terrain_displacement"
        ]
        
        for alt_name in alternative_names:
            node_group = GeometryNodesAssetManager.import_node_group(
                "archipelago_terrain_generator", 
                alt_name
            )
            if node_group:
                return node_group
        
        # Fallback: try importing any available asset
        assets = GeometryNodesAssetManager.get_available_node_assets()
        for asset in assets:
            print(f"Trying to import from asset: {asset['name']}")
            node_group = GeometryNodesAssetManager.import_node_group(asset['name'])
            if node_group:
                return node_group
        
        # Last resort: create a basic node group
        print("No assets found, creating basic terrain displacement node group...")
        return GeometryNodesAssetManager.create_basic_terrain_nodegroup()
    
    @staticmethod
    def create_basic_terrain_nodegroup():
        """Create a basic terrain displacement node group as fallback"""
        group_name = "ONeill_Terrain_Displacement_Basic"
        
        if group_name in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
        group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
        
        # Create basic nodes for terrain displacement
        input_node = group.nodes.new('NodeGroupInput')
        output_node = group.nodes.new('NodeGroupOutput')
        position_node = group.nodes.new('GeometryNodeInputPosition')
        separate_xyz_node = group.nodes.new('ShaderNodeSeparateXYZ')
        combine_xyz_node = group.nodes.new('ShaderNodeCombineXYZ')
        image_tex_node = group.nodes.new('GeometryNodeImageTexture')
        math_node = group.nodes.new('ShaderNodeMath')
        vector_math_node = group.nodes.new('ShaderNodeVectorMath')
        set_position_node = group.nodes.new('GeometryNodeSetPosition')
        
        # Configure nodes
        math_node.operation = 'SUBTRACT'
        math_node.inputs[1].default_value = 0.5
        vector_math_node.operation = 'MULTIPLY'
        
        # Setup interface
        group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        group.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketImage')  
        group.interface.new_socket('Scale', in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
        # Position nodes
        input_node.location = (-800, 0)
        output_node.location = (600, 0)
        position_node.location = (-600, 100)
        separate_xyz_node.location = (-400, 100)
        combine_xyz_node.location = (-200, 100)
        image_tex_node.location = (-200, -100)
        math_node.location = (0, -100)
        vector_math_node.location = (200, 0)
        set_position_node.location = (400, 0)
        
        # Create connections
        links = group.links
        links.new(input_node.outputs['Geometry'], set_position_node.inputs['Geometry'])
        links.new(set_position_node.outputs['Geometry'], output_node.inputs['Geometry'])
        links.new(position_node.outputs['Position'], separate_xyz_node.inputs['Vector'])
        links.new(separate_xyz_node.outputs['X'], combine_xyz_node.inputs['X'])
        links.new(separate_xyz_node.outputs['Y'], combine_xyz_node.inputs['Y'])
        links.new(input_node.outputs['Image'], image_tex_node.inputs['Image'])
        links.new(combine_xyz_node.outputs['Vector'], image_tex_node.inputs['Vector'])
        links.new(image_tex_node.outputs['Color'], math_node.inputs[0])
        links.new(math_node.outputs['Value'], vector_math_node.inputs[0])
        links.new(input_node.outputs['Scale'], vector_math_node.inputs[1])
        links.new(vector_math_node.outputs['Vector'], set_position_node.inputs['Offset'])
        
        print("Created basic terrain displacement node group as fallback")
        return group

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
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected:
            self.report({'ERROR'}, "Select cylinder objects")
            return {'CANCELLED'}
        
        created = []
        for obj in selected:
            try:
                result = self.unwrap_cylinder_object(obj, context, context.scene.oneill_props.alignment_axis)
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

class ONEILL_OT_SetupGeometryNodes(bpy.types.Operator):
    bl_idname = "oneill.setup_geometry_nodes"
    bl_label = "Setup Geometry Nodes"
    bl_description = "Setup live terrain preview using modular geometry nodes from assets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        try:
            # Use the asset manager to get the terrain displacement node group
            node_group = GeometryNodesAssetManager.get_terrain_displacement_node_group()
            
            if not node_group:
                self.report({'ERROR'}, "Could not load terrain displacement node group")
                return {'CANCELLED'}
            
            setup_count = 0
            for obj in flat_objects:
                heightmap_name = obj.get("heightmap_image")
                if heightmap_name and heightmap_name in bpy.data.images:
                    cylinder_radius = obj.get("cylinder_radius", 3.4)
                    self.add_displacement_modifier(obj, node_group, bpy.data.images[heightmap_name], cylinder_radius)
                    setup_count += 1
            
            self.report({'INFO'}, f"Setup geometry nodes for {setup_count} objects using {node_group.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Geometry nodes setup failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def add_displacement_modifier(self, obj, node_group, heightmap, cylinder_radius):
        # Remove existing displacement modifiers
        modifiers_to_remove = []
        for mod in obj.modifiers:
            if mod.type == 'NODES' and ('terrain' in mod.name.lower() or 'displacement' in mod.name.lower()):
                modifiers_to_remove.append(mod)
        
        for mod in modifiers_to_remove:
            obj.modifiers.remove(mod)
        
        # Add geometry nodes modifier
        modifier = obj.modifiers.new("TerrainDisplacement", 'NODES')
        modifier.node_group = node_group
        
        # Get terrain scale from scene properties
        props = bpy.context.scene.oneill_props
        base_displacement = cylinder_radius * 0.1
        displacement_scale = base_displacement * props.terrain_scale_multiplier
        
        # Set modifier inputs
        if hasattr(modifier, 'node_group') and modifier.node_group:
            try:
                for input_item in modifier.node_group.interface.items_tree:
                    if input_item.name == "Image":
                        modifier[input_item.identifier] = heightmap
                    elif input_item.name == "Scale":
                        modifier[input_item.identifier] = displacement_scale
            except Exception as e:
                print(f"Could not set modifier inputs: {e}")
                try:
                    if len(modifier.node_group.interface.items_tree) >= 3:
                        modifier["Input_2"] = heightmap
                        modifier["Input_3"] = displacement_scale
                except:
                    pass

class ONEILL_OT_UpdateTerrainScale(bpy.types.Operator):
    bl_idname = "oneill.update_terrain_scale"
    bl_label = "Update Terrain Scale"
    bl_description = "Update the terrain displacement scale for all flat objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        updated_count = 0
        for obj in flat_objects:
            for mod in obj.modifiers:
                if mod.type == 'NODES' and 'terrain' in mod.name.lower():
                    cylinder_radius = obj.get("cylinder_radius", 3.4)
                    base_displacement = cylinder_radius * 0.1
                    new_scale = base_displacement * props.terrain_scale_multiplier
                    
                    try:
                        for input_item in mod.node_group.interface.items_tree:
                            if input_item.name == "Scale":
                                mod[input_item.identifier] = new_scale
                                updated_count += 1
                                break
                    except:
                        try:
                            mod["Input_3"] = new_scale
                            updated_count += 1
                        except:
                            pass
                    break
        
        bpy.context.view_layer.update()
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, f"Updated terrain scale for {updated_count} objects")
        return {'FINISHED'}

class ONEILL_OT_GenerateTerrain(bpy.types.Operator):
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        props = context.scene.oneill_props
        generated_count = 0
        
        for obj in flat_objects:
            img_name = obj.get("heightmap_image")
            if img_name and img_name in bpy.data.images:
                self.generate_heightmap(bpy.data.images[img_name], props)
                generated_count += 1
        
        for area in bpy.context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, f"Generated procedural terrain for {generated_count} heightmaps")
        return {'FINISHED'}
    
    def generate_heightmap(self, image, props):
        width, height = image.size
        pixels = []
        
        random.seed(props.random_seed)
        
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                noise_val = self.multi_octave_noise(norm_x * props.noise_scale, norm_y * props.noise_scale)
                height_val = (noise_val + 1.0) * 0.5
                height_val = max(0.0, min(1.0, height_val))
                
                pixels.extend([height_val, height_val, height_val, 1.0])
        
        image.pixels = pixels
        image.update()
        image.update_tag()
        
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()
            elif area.type == 'VIEW_3D':
                area.tag_redraw()
        
        bpy.context.view_layer.update()
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image == image:
                        material.update_tag()
    
    def multi_octave_noise(self, x, y):
        result = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for i in range(6):
            result += math.sin(x * frequency + i * 0.5) * math.cos(y * frequency + i * 0.3) * amplitude
            max_value += amplitude
            amplitude *= 0.5
            frequency *= 2.0
        
        return result / max_value if max_value > 0 else 0

class ONEILL_OT_RewrapToCylinder(bpy.types.Operator):
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
        original_name = flat_obj.get("original_object", "Unknown")
        
        # Find original object
        original_obj = bpy.data.objects.get(original_name)
        if not original_obj:
            return None
        
        # Duplicate original geometry exactly
        original_mesh = original_obj.data
        terrain_mesh = original_mesh.copy()
        terrain_mesh.name = f"{original_name}_terrain_mesh"
        
        terrain_name = f"{original_name}_terrain"
        terrain_obj = bpy.data.objects.new(terrain_name, terrain_mesh)
        context.collection.objects.link(terrain_obj)
        
        # Copy transform exactly
        terrain_obj.location = original_obj.location.copy()
        terrain_obj.rotation_euler = original_obj.rotation_euler.copy()
        terrain_obj.scale = original_obj.scale.copy()
        
        # Apply heightmap displacement
        heightmap_name = flat_obj.get("heightmap_image")
        if heightmap_name and heightmap_name in bpy.data.images:
            alignment_axis = flat_obj.get("alignment_axis", 'X')
            cylinder_radius = flat_obj.get("cylinder_radius", 2.0)
            cylinder_length = flat_obj.get("cylinder_length", 8.0)
            self.apply_heightmap_displacement(terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length)
        
        terrain_obj["oneill_terrain"] = True
        terrain_obj["source_flat"] = flat_obj.name
        terrain_obj["original_cylinder"] = original_name
        terrain_obj["terrain_scale"] = self.terrain_scale
        
        return terrain_obj
    
    def apply_heightmap_displacement(self, terrain_obj, heightmap_name, alignment_axis, cylinder_radius, cylinder_length):
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
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        
        px = int(x * (width - 1)) if width > 1 else 0
        py = int(y * (height - 1)) if height > 1 else 0
        
        pixel_idx = (py * width + px) * 4
        if pixel_idx < len(pixels):
            height_val = pixels[pixel_idx]
            return (height_val - 0.5)
        
        return 0.0

class ONEILL_OT_ListGeometryNodeAssets(bpy.types.Operator):
    bl_idname = "oneill.list_geometry_node_assets"
    bl_label = "List Available Geometry Node Assets"
    bl_description = "Show available geometry node assets in the assets folder"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        assets = GeometryNodesAssetManager.get_available_node_assets()
        
        if not assets:
            self.report({'WARNING'}, "No geometry node assets found. Save the .blend file first and create an assets/geometry_nodes folder.")
            return {'CANCELLED'}
        
        asset_list = "\n".join([f"- {asset['name']}: {asset['description']}" for asset in assets])
        self.report({'INFO'}, f"Found {len(assets)} geometry node assets:\n{asset_list}")
        
        # Print detailed info to console
        print("\n=== AVAILABLE GEOMETRY NODE ASSETS ===")
        for asset in assets:
            print(f"Name: {asset['name']}")
            print(f"Path: {asset['path']}")
            print(f"Description: {asset['description']}")
            print("---")
        
        return {'FINISHED'}

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(bpy.types.Panel):
    bl_label = "O'Neill Terrain Workflow"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Heightmap Workflow", icon='IMAGE_DATA')
        
        # Status info
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
        
        layout.separator()
        layout.label(text="Main Workflow:")
        
        # Workflow steps
        col = layout.column(align=True)
        col.operator("oneill.align_cylinders", text="1. Align Cylinders")
        col.operator("oneill.unwrap_to_flat", text="2. Unwrap to Flat")
        col.operator("oneill.create_heightmaps", text="3. Create Heightmaps")
        
        layout.separator()
        
        # Live preview section
        box = layout.box()
        box.label(text="Live Preview (Geometry Nodes):")
        
        # Check if we have assets
        assets = GeometryNodesAssetManager.get_available_node_assets()
        if assets:
            box.label(text=f"✅ {len(assets)} node assets available", icon='CHECKMARK')
        else:
            box.label(text="⚠️ No node assets found", icon='ERROR')
        
        box.operator("oneill.setup_geometry_nodes", text="4. Setup Live Preview")
        box.operator("oneill.list_geometry_node_assets", text="List Available Assets", icon='PRESET')
        
        # Terrain generation controls
        if flat_objs > 0:
            box = layout.box()
            box.label(text="Terrain Generation:")
            
            props = context.scene.oneill_props
            
            # Scale control with update button
            scale_row = box.row(align=True)
            scale_row.prop(props, "terrain_scale_multiplier", text="Scale")
            scale_row.operator("oneill.update_terrain_scale", text="", icon='FILE_REFRESH')
            
            box.prop(props, "terrain_strength")
            box.prop(props, "noise_scale")
            box.prop(props, "random_seed")
            
            box.operator("oneill.generate_terrain", text="Generate Terrain")
        
        layout.separator()
        layout.operator("oneill.rewrap_to_cylinder", text="5. Rewrap to Cylinders")
        
        # Settings
        layout.separator()
        box = layout.box()
        box.label(text="Settings:")
        box.prop(context.scene.oneill_props, "alignment_axis")
        box.prop(context.scene.oneill_props, "heightmap_resolution")

# ========================= REGISTRATION =========================

classes = [
    ONeillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_SetupGeometryNodes,
    ONEILL_OT_UpdateTerrainScale,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinder,
    ONEILL_OT_ListGeometryNodeAssets,
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
    print("O'Neill Heightmap Terrain System with Modular Geometry Nodes registered successfully!")

def unregister():
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister {cls.__name__}: {e}")

def cleanup_existing():
    """Clean up any existing O'Neill registrations"""
    scene_props = ['oneill_props', 'oneill_alignment_props', 'oneill_heightmap_props']
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