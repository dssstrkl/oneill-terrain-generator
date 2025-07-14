bl_info = {
    "name": "O'Neill Cylinder Alignment & Terrain",
    "author": "Assistant",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Precision alignment, biome assignment, POI placement, and terrain generation for O'Neill cylinders",
    "category": "3D View",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector, Color
import math
import random
from bpy_extras import view3d_utils
import json

try:
    import noise
    HAS_NOISE = True
except ImportError:
    HAS_NOISE = False

# ========================= PROPERTY GROUPS =========================

class ONEILL_biome_properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Biome Name", default="New Biome")
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.2, 0.8, 0.2),
        min=0.0, max=1.0
    )
    influence: bpy.props.FloatProperty(
        name="Influence",
        default=1.0,
        min=0.0, max=1.0
    )
    biome_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('OCEAN', "Ocean", "Water biome"),
            ('FOREST', "Forest", "Forested area"),
            ('DESERT', "Desert", "Arid region"),
            ('MOUNTAINS', "Mountains", "Highland terrain"),
            ('URBAN', "Urban", "City/developed area"),
            ('AGRICULTURAL', "Agricultural", "Farming region"),
            ('INDUSTRIAL', "Industrial", "Manufacturing zone"),
            ('WASTELAND', "Wasteland", "Barren/damaged area"),
        ],
        default='FOREST'
    )

class ONEILL_poi_properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="POI Name", default="New Location")
    poi_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('CITY', "City", "Major settlement"),
            ('VILLAGE', "Village", "Small settlement"),
            ('OUTPOST', "Outpost", "Remote station"),
            ('INDUSTRIAL', "Industrial", "Factory/mining"),
            ('MILITARY', "Military", "Defense installation"),
            ('SPACEPORT', "Spaceport", "Transportation hub"),
            ('LANDMARK', "Landmark", "Point of interest"),
            ('RESOURCE', "Resource", "Mining/extraction site"),
        ],
        default='VILLAGE'
    )
    population: bpy.props.IntProperty(name="Population", default=1000, min=0)
    faction: bpy.props.StringProperty(name="Faction", default="Neutral")
    importance: bpy.props.EnumProperty(
        name="Importance",
        items=[
            ('LOW', "Low", "Minor location"),
            ('MEDIUM', "Medium", "Notable location"),
            ('HIGH', "High", "Major location"),
            ('CRITICAL', "Critical", "Essential location"),
        ],
        default='MEDIUM'
    )

class ONEILL_alignment_properties(bpy.types.PropertyGroup):
    alignment_axis: bpy.props.EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align along X-axis (default)"),
            ('Y', "Y-Axis", "Align along Y-axis"),
            ('Z', "Z-Axis", "Align along Z-axis"),
        ],
        default='X'
    )
    
    precision_threshold: bpy.props.FloatProperty(
        name="Precision Threshold",
        description="Maximum gap distance for alignment",
        default=0.001,
        min=0.0001,
        max=0.1
    )
    
    # Terrain properties (preserved from original)
    terrain_type: bpy.props.EnumProperty(
        name="Terrain Type",
        items=[
            ('MOUNTAINS', "Mountains", "High peaks"),
            ('HILLS', "Rolling Hills", "Gentle terrain"),
            ('MARSHLAND', "Marshland", "Wetland"),
            ('CANYON', "Canyon", "Deep valleys"),
            ('PLATEAU', "Plateau", "Flat tops"),
            ('DUNES', "Sand Dunes", "Sandy terrain"),
            ('CUSTOM', "Custom Paint", "Manual painting mode"),
        ],
        default='HILLS'
    )
    
    strength: bpy.props.FloatProperty(
        name="Strength",
        default=2.5,
        min=0.1,
        max=5.0
    )
    
    scale: bpy.props.FloatProperty(
        name="Scale",
        default=2.5,
        min=0.1,
        max=5.0
    )
    
    seed: bpy.props.IntProperty(
        name="Seed",
        default=1,
        min=1,
        max=9999
    )
    
    # Biome and POI properties
    active_biome: bpy.props.IntProperty(name="Active Biome", default=0)
    active_poi: bpy.props.IntProperty(name="Active POI", default=0)
    
    # Generation settings
    settlement_density: bpy.props.FloatProperty(
        name="Settlement Density",
        default=0.3,
        min=0.0, max=1.0
    )
    
    road_density: bpy.props.FloatProperty(
        name="Road Density", 
        default=0.5,
        min=0.0, max=1.0
    )
    
    resource_density: bpy.props.FloatProperty(
        name="Resource Density",
        default=0.4,
        min=0.0, max=1.0
    )
    
    procedural_influence: bpy.props.FloatProperty(
        name="Procedural Influence",
        default=0.6,
        min=0.0, max=1.0
    )
    
    respect_constraints: bpy.props.BoolProperty(
        name="Respect Manual Constraints",
        default=True
    )
    
    generation_mode: bpy.props.EnumProperty(
        name="Generation Mode",
        items=[
            ('MANUAL', "Manual", "Manual placement only"),
            ('PROCEDURAL', "Procedural", "Procedural generation only"),
            ('HYBRID', "Hybrid", "Combined manual + procedural"),
        ],
        default='HYBRID'
    )

# ========================= UTILITY FUNCTIONS =========================

def get_object_bounds_on_axis(obj, axis):
    """Get min/max bounds of object on specified axis"""
    if axis == 'X':
        return min(v.co.x for v in obj.data.vertices), max(v.co.x for v in obj.data.vertices)
    elif axis == 'Y':
        return min(v.co.y for v in obj.data.vertices), max(v.co.y for v in obj.data.vertices)
    elif axis == 'Z':
        return min(v.co.z for v in obj.data.vertices), max(v.co.z for v in obj.data.vertices)

def create_poi_empty(name, location, poi_props):
    """Create an empty object for POI with custom properties"""
    empty = bpy.data.objects.new(name, None)
    empty.location = location
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 2.0
    
    # Store POI properties
    empty["poi_type"] = poi_props.poi_type
    empty["population"] = poi_props.population
    empty["faction"] = poi_props.faction
    empty["importance"] = poi_props.importance
    empty["is_oneill_poi"] = True
    
    bpy.context.collection.objects.link(empty)
    return empty

def get_biome_material(biome_props):
    """Get or create material for biome"""
    mat_name = f"Biome_{biome_props.name}"
    mat = bpy.data.materials.get(mat_name)
    
    if not mat:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        
        # Set up basic material with biome color
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        
        shader.inputs['Base Color'].default_value = (*biome_props.color, 1.0)
        
        mat.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# ========================= OPERATORS =========================

class ONEILL_OT_align_cylinders(bpy.types.Operator):
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinder Objects"
    bl_description = "Precision align selected cylinder objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 mesh objects to align")
            return {'CANCELLED'}
        
        try:
            aligned_count = self.align_objects_on_axis(selected_objects, props.alignment_axis, props.precision_threshold)
            self.report({'INFO'}, f"Aligned {aligned_count} objects on {props.alignment_axis}-axis")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Alignment failed: {str(e)}")
            return {'CANCELLED'}
    
    def align_objects_on_axis(self, objects, axis, threshold):
        """Perform vertex-level alignment on specified axis"""
        aligned_count = 0
        
        # Get bounds for all objects with world matrix applied
        object_bounds = []
        for obj in objects:
            # Apply world transform to get actual world-space bounds
            world_bounds = []
            for vertex in obj.data.vertices:
                world_pos = obj.matrix_world @ vertex.co
                if axis == 'X':
                    world_bounds.append(world_pos.x)
                elif axis == 'Y':
                    world_bounds.append(world_pos.y)
                elif axis == 'Z':
                    world_bounds.append(world_pos.z)
            
            min_val = min(world_bounds)
            max_val = max(world_bounds)
            object_bounds.append((obj, min_val, max_val))
        
        # Sort objects by position on alignment axis (by minimum value)
        object_bounds.sort(key=lambda x: x[1])
        
        # Align adjacent objects by moving each subsequent object to touch the previous one
        for i in range(len(object_bounds) - 1):
            current_obj, current_min, current_max = object_bounds[i]
            next_obj, next_min, next_max = object_bounds[i + 1]
            
            # Calculate the gap between objects
            gap = next_min - current_max
            
            # If there's a gap larger than threshold, close it
            if abs(gap) > threshold:
                # Move the next object to touch the current object
                # The offset should eliminate the gap
                offset = -gap
                
                # Apply offset to next object
                if axis == 'X':
                    next_obj.location.x += offset
                elif axis == 'Y':
                    next_obj.location.y += offset
                elif axis == 'Z':
                    next_obj.location.z += offset
                
                # Update bounds for subsequent calculations
                object_bounds[i + 1] = (next_obj, next_min + offset, next_max + offset)
                
                aligned_count += 1
        
        return aligned_count

class ONEILL_OT_unwrap_cylinder(bpy.types.Operator):
    bl_idname = "oneill.unwrap_cylinder"
    bl_label = "Unwrap Cylinders"
    bl_description = "Create flat objects from cylinder objects for terrain editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    subdivision_levels: bpy.props.IntProperty(
        name="Subdivision Levels",
        default=4,
        min=2, max=7
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Select cylinder objects to unwrap")
            return {'CANCELLED'}
        
        processed_objects = []
        
        for obj in selected_objects:
            try:
                result = self.unwrap_cylinder_object(obj, context, props.alignment_axis)
                if result:
                    processed_objects.append(result)
            except Exception as e:
                self.report({'WARNING'}, f"Failed to unwrap {obj.name}: {str(e)}")
        
        if processed_objects:
            # Hide original objects
            for obj in selected_objects:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            # Select unwrapped objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in processed_objects:
                obj.select_set(True)
            context.view_layer.objects.active = processed_objects[-1]
            
            self.report({'INFO'}, f"Unwrapped {len(processed_objects)} cylinder objects")
        
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, obj, context, alignment_axis):
        """Create flat object from cylinder based on alignment axis"""
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
        
        # Create flat mesh
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
        
        # Position to maintain X-axis alignment relationship
        if alignment_axis == 'X':
            # Preserve X position from original object center
            unwrapped_obj.location.x = center_x
            unwrapped_obj.location.y = center_y
            unwrapped_obj.location.z = 0  # Place on ground plane
        elif alignment_axis == 'Y':
            # For Y-axis alignment, map Y to X for flat layout
            unwrapped_obj.location.x = center_y  # Y becomes X in flat layout
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        else:  # Z-axis
            # For Z-axis alignment, map Z to X for flat layout
            unwrapped_obj.location.x = (min_z + max_z) / 2  # Z becomes X in flat layout
            unwrapped_obj.location.y = center_x
            unwrapped_obj.location.z = 0
        
        # Store metadata
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["is_unwrapped"] = True
        unwrapped_obj["cylinder_radius"] = estimated_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        unwrapped_obj["alignment_axis"] = alignment_axis
        unwrapped_obj["original_location"] = list(original_location)
        unwrapped_obj["original_center"] = [center_x, center_y]
        unwrapped_obj["subdivision_levels"] = self.subdivision_levels
        
        return unwrapped_obj

class ONEILL_OT_generate_terrain(bpy.types.Operator):
    bl_idname = "oneill.generate_terrain"
    bl_label = "Generate Terrain"
    bl_description = "Generate procedural terrain on flat objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        unwrapped_objects = [obj for obj in context.selected_objects 
                           if obj.type == 'MESH' and obj.get("is_unwrapped")]
        
        if not unwrapped_objects:
            self.report({'ERROR'}, "Select unwrapped flat objects")
            return {'CANCELLED'}
        
        try:
            random.seed(props.seed)
            processed_count = 0
            
            for obj in unwrapped_objects:
                self.generate_terrain_for_object(obj, props)
                processed_count += 1
            
            self.report({'INFO'}, f"Generated terrain on {processed_count} objects")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Terrain generation failed: {str(e)}")
            return {'CANCELLED'}
    
    def generate_terrain_for_object(self, obj, props):
        """Generate terrain using improved noise"""
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Get mesh bounds
        min_x = min(v.co.x for v in bm.verts)
        max_x = max(v.co.x for v in bm.verts)
        min_y = min(v.co.y for v in bm.verts)
        max_y = max(v.co.y for v in bm.verts)
        
        x_range = max_x - min_x
        y_range = max_y - min_y
        
        # Apply terrain to each vertex
        for vert in bm.verts:
            norm_x = (vert.co.x - min_x) / x_range if x_range > 0 else 0
            norm_y = (vert.co.y - min_y) / y_range if y_range > 0 else 0
            
            height = self.get_terrain_height(norm_x, norm_y, props)
            vert.co.z = height * (props.strength / 5.0)
        
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.update()
    
    def get_terrain_height(self, x, y, props):
        """Generate terrain height using noise"""
        if HAS_NOISE:
            try:
                return noise.pnoise2(
                    x * props.scale, y * props.scale,
                    octaves=6, persistence=0.5, lacunarity=2.0,
                    base=props.seed
                )
            except:
                pass
        
        # Fallback noise
        x_int = int(x * 1000)
        y_int = int(y * 1000)
        n = (x_int * 1619 + y_int * 31337 + props.seed * 6971) % 2147483647
        n = (n * 16807) % 2147483647
        return (n / 2147483647.0) - 0.5

class ONEILL_OT_rewrap_cylinder(bpy.types.Operator):
    bl_idname = "oneill.rewrap_cylinder"
    bl_label = "Re-wrap to Cylinders"
    bl_description = "Convert flat objects back to cylinders with terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    terrain_scale: bpy.props.FloatProperty(name="Terrain Scale", default=2.0, min=0.1, max=10.0)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        unwrapped_objects = [obj for obj in context.selected_objects 
                           if obj.type == 'MESH' and obj.get("is_unwrapped")]
        
        if not unwrapped_objects:
            self.report({'ERROR'}, "Select unwrapped flat objects")
            return {'CANCELLED'}
        
        processed_objects = []
        
        for obj in unwrapped_objects:
            try:
                result = self.rewrap_to_cylinder(obj, context)
                if result:
                    processed_objects.append(result)
            except Exception as e:
                self.report({'WARNING'}, f"Failed to rewrap {obj.name}: {str(e)}")
        
        if processed_objects:
            # Hide flat objects
            for obj in unwrapped_objects:
                obj.hide_set(True)
                obj.hide_viewport = True
            
            # Select terrain objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in processed_objects:
                obj.select_set(True)
            context.view_layer.objects.active = processed_objects[-1]
            
            self.report({'INFO'}, f"Re-wrapped {len(processed_objects)} objects")
        
        return {'FINISHED'}
    
    def rewrap_to_cylinder(self, flat_obj, context):
        """Convert flat object back to cylinder with terrain displacement"""
        original_name = flat_obj.get("original_object", "Unknown")
        cylinder_radius = flat_obj.get("cylinder_radius", 1.0)
        cylinder_length = flat_obj.get("cylinder_length", 1.0)
        alignment_axis = flat_obj.get("alignment_axis", 'X')
        original_location = Vector(flat_obj.get("original_location", [0, 0, 0]))
        
        # Create cylinder mesh
        bm = bmesh.new()
        bmesh.ops.create_cylinder(
            bm,
            vertices=32,
            depth=cylinder_length,
            radius=cylinder_radius,
            cap_ends=True
        )
        
        # Build terrain lookup from flat object
        terrain_lookup = self.build_terrain_lookup(flat_obj)
        
        # Apply terrain displacement
        for vert in bm.verts:
            if alignment_axis == 'X':
                # X is length, use Y/Z for radius calculation
                rel_pos = (vert.co.x + cylinder_length/2) / cylinder_length
                angle = math.atan2(vert.co.z, vert.co.y)
                if angle < 0:
                    angle += 2 * math.pi
                circumference_pos = angle / (2 * math.pi)
                
                terrain_height = self.sample_terrain(rel_pos, circumference_pos, terrain_lookup)
                displacement = -terrain_height * self.terrain_scale
                
                current_radius = math.sqrt(vert.co.y**2 + vert.co.z**2)
                new_radius = max(current_radius + displacement, cylinder_radius * 0.1)
                
                vert.co.y = new_radius * math.cos(angle)
                vert.co.z = new_radius * math.sin(angle)
        
        # Create terrain object
        terrain_name = f"{original_name}_terrain"
        terrain_mesh = bpy.data.meshes.new(terrain_name)
        bm.to_mesh(terrain_mesh)
        bm.free()
        
        terrain_obj = bpy.data.objects.new(terrain_name, terrain_mesh)
        context.collection.objects.link(terrain_obj)
        terrain_obj.location = original_location
        
        return terrain_obj
    
    def build_terrain_lookup(self, flat_obj):
        """Build lookup table from flat object's vertex heights"""
        terrain_data = {}
        mesh = flat_obj.data
        
        for vert in mesh.vertices:
            x, y, z = vert.co
            # Normalize coordinates
            key = (round(x * 100), round(y * 100))
            terrain_data[key] = z
        
        return terrain_data
    
    def sample_terrain(self, x, y, terrain_lookup):
        """Sample terrain height from lookup table"""
        key = (round(x * 100), round(y * 100))
        return terrain_lookup.get(key, 0.0)

class ONEILL_OT_add_biome(bpy.types.Operator):
    bl_idname = "oneill.add_biome"
    bl_label = "Add Biome"
    bl_description = "Add a new biome type"
    
    def execute(self, context):
        scene = context.scene
        
        # Create biome collection if it doesn't exist
        if "oneill_biomes" not in scene:
            scene["oneill_biomes"] = []
        
        biomes = scene.get("oneill_biomes", [])
        new_biome = {
            "name": f"Biome_{len(biomes) + 1}",
            "type": "FOREST",
            "color": [0.2, 0.8, 0.2],
            "influence": 1.0
        }
        biomes.append(new_biome)
        scene["oneill_biomes"] = biomes
        
        self.report({'INFO'}, f"Added biome: {new_biome['name']}")
        return {'FINISHED'}

class ONEILL_OT_place_poi(bpy.types.Operator):
    bl_idname = "oneill.place_poi"
    bl_label = "Place POI"
    bl_description = "Place Point of Interest at 3D cursor"
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        cursor_location = context.scene.cursor.location.copy()
        
        # Create POI empty
        poi_name = f"POI_{len([obj for obj in bpy.data.objects if obj.get('is_oneill_poi')])}"
        empty = bpy.data.objects.new(poi_name, None)
        empty.location = cursor_location
        empty.empty_display_type = 'SPHERE'
        empty.empty_display_size = 1.0
        
        # Store POI properties
        empty["poi_type"] = "VILLAGE"
        empty["population"] = 1000
        empty["faction"] = "Neutral"
        empty["importance"] = "MEDIUM"
        empty["is_oneill_poi"] = True
        
        context.collection.objects.link(empty)
        
        self.report({'INFO'}, f"Placed POI: {poi_name}")
        return {'FINISHED'}

class ONEILL_OT_generate_procedural(bpy.types.Operator):
    bl_idname = "oneill.generate_procedural"
    bl_label = "Generate Procedural Elements"
    bl_description = "Generate settlements, roads, and resources procedurally"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        
        if props.generation_mode == 'MANUAL':
            self.report({'INFO'}, "Manual mode selected - no procedural generation")
            return {'FINISHED'}
        
        try:
            generated_count = 0
            
            # Generate settlements based on density
            if props.settlement_density > 0:
                generated_count += self.generate_settlements(context, props)
            
            # Generate roads
            if props.road_density > 0:
                generated_count += self.generate_roads(context, props)
            
            # Generate resource nodes
            if props.resource_density > 0:
                generated_count += self.generate_resources(context, props)
            
            self.report({'INFO'}, f"Generated {generated_count} procedural elements")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Procedural generation failed: {str(e)}")
            return {'CANCELLED'}
    
    def generate_settlements(self, context, props):
        """Generate settlements based on density and constraints"""
        count = 0
        target_count = int(props.settlement_density * 20)  # Scale factor
        
        for i in range(target_count):
            # Random location within scene bounds
            location = Vector((
                random.uniform(-50, 50),
                random.uniform(-50, 50),
                0
            ))
            
            # Check constraints if enabled
            if props.respect_constraints:
                # Skip if too close to existing POIs
                existing_pois = [obj for obj in bpy.data.objects if obj.get("is_oneill_poi")]
                too_close = any((obj.location - location).length < 5.0 for obj in existing_pois)
                if too_close:
                    continue
            
            # Create settlement
            settlement_name = f"Settlement_{count + 1}"
            empty = bpy.data.objects.new(settlement_name, None)
            empty.location = location
            empty.empty_display_type = 'CUBE'
            empty.empty_display_size = 0.5
            
            # Store properties
            empty["poi_type"] = random.choice(["VILLAGE", "OUTPOST"])
            empty["population"] = random.randint(100, 2000)
            empty["faction"] = random.choice(["Colonial", "Mining Corp", "Free Traders"])
            empty["importance"] = "LOW"
            empty["is_oneill_poi"] = True
            empty["is_procedural"] = True
            
            context.collection.objects.link(empty)
            count += 1
        
        return count
    
    def generate_roads(self, context, props):
        """Generate road network as curve objects"""
        count = 0
        target_count = int(props.road_density * 10)
        
        # Get existing POIs to connect
        pois = [obj for obj in bpy.data.objects if obj.get("is_oneill_poi")]
        
        if len(pois) < 2:
            return 0
        
        for i in range(target_count):
            # Connect random POIs
            poi1, poi2 = random.sample(pois, 2)
            
            # Create curve between POIs
            curve_data = bpy.data.curves.new(f"Road_{count + 1}", type='CURVE')
            curve_data.dimensions = '3D'
            
            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(1)  # Start with 2 points
            
            # Set start and end points
            spline.bezier_points[0].co = poi1.location
            spline.bezier_points[1].co = poi2.location
            
            # Set handle types
            spline.bezier_points[0].handle_right_type = 'AUTO'
            spline.bezier_points[0].handle_left_type = 'AUTO'
            spline.bezier_points[1].handle_right_type = 'AUTO'
            spline.bezier_points[1].handle_left_type = 'AUTO'
            
            # Create object
            curve_obj = bpy.data.objects.new(f"Road_{count + 1}", curve_data)
            curve_obj["is_oneill_road"] = True
            curve_obj["is_procedural"] = True
            
            context.collection.objects.link(curve_obj)
            count += 1
        
        return count
    
    def generate_resources(self, context, props):
        """Generate resource extraction sites"""
        count = 0
        target_count = int(props.resource_density * 15)
        
        resource_types = ["Iron", "Rare Earth", "Water", "Minerals", "Energy"]
        
        for i in range(target_count):
            location = Vector((
                random.uniform(-40, 40),
                random.uniform(-40, 40),
                0
            ))
            
            # Create resource node
            resource_name = f"Resource_{count + 1}"
            empty = bpy.data.objects.new(resource_name, None)
            empty.location = location
            empty.empty_display_type = 'CIRCLE'
            empty.empty_display_size = 1.5
            
            # Store properties
            empty["poi_type"] = "RESOURCE"
            empty["resource_type"] = random.choice(resource_types)
            empty["yield"] = random.uniform(0.1, 1.0)
            empty["extraction_difficulty"] = random.choice(["Easy", "Medium", "Hard"])
            empty["is_oneill_poi"] = True
            empty["is_procedural"] = True
            
            context.collection.objects.link(empty)
            count += 1
        
        return count

class ONEILL_OT_clear_procedural(bpy.types.Operator):
    bl_idname = "oneill.clear_procedural"
    bl_label = "Clear Procedural Elements"
    bl_description = "Remove all procedurally generated elements"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        removed_count = 0
        
        # Remove procedural objects
        objects_to_remove = [obj for obj in bpy.data.objects if obj.get("is_procedural")]
        
        for obj in objects_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed_count += 1
        
        self.report({'INFO'}, f"Removed {removed_count} procedural elements")
        return {'FINISHED'}

class ONEILL_OT_paint_biome(bpy.types.Operator):
    bl_idname = "oneill.paint_biome"
    bl_label = "Paint Biome"
    bl_description = "Paint biome on selected objects"
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Select mesh objects to paint biome")
            return {'CANCELLED'}
        
        # Get active biome from scene
        biomes = context.scene.get("oneill_biomes", [])
        if not biomes:
            self.report({'ERROR'}, "No biomes defined - add a biome first")
            return {'CANCELLED'}
        
        props = context.scene.oneill_alignment_props
        if props.active_biome >= len(biomes):
            props.active_biome = 0
        
        active_biome = biomes[props.active_biome]
        
        # Apply biome material to selected objects
        for obj in selected_objects:
            # Create or get biome material
            mat_name = f"Biome_{active_biome['name']}"
            mat = bpy.data.materials.get(mat_name)
            
            if not mat:
                mat = bpy.data.materials.new(mat_name)
                mat.use_nodes = True
                mat.diffuse_color = (*active_biome['color'], 1.0)
            
            # Assign material
            if not obj.data.materials:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
            
            # Store biome data
            obj["biome_type"] = active_biome['type']
            obj["biome_name"] = active_biome['name']
        
        self.report({'INFO'}, f"Applied biome '{active_biome['name']}' to {len(selected_objects)} objects")
        return {'FINISHED'}

class ONEILL_OT_export_data(bpy.types.Operator):
    bl_idname = "oneill.export_data"
    bl_label = "Export O'Neill Data"
    bl_description = "Export POIs, biomes, and terrain data"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            export_data = self.collect_scene_data(context)
            
            with open(self.filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.report({'INFO'}, f"Exported data to {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
    
    def collect_scene_data(self, context):
        """Collect all O'Neill cylinder data from scene"""
        data = {
            "biomes": context.scene.get("oneill_biomes", []),
            "pois": [],
            "roads": [],
            "terrain_objects": [],
            "alignment_settings": {}
        }
        
        # Collect POIs
        for obj in bpy.data.objects:
            if obj.get("is_oneill_poi"):
                poi_data = {
                    "name": obj.name,
                    "location": list(obj.location),
                    "type": obj.get("poi_type", "UNKNOWN"),
                    "population": obj.get("population", 0),
                    "faction": obj.get("faction", "Unknown"),
                    "importance": obj.get("importance", "MEDIUM"),
                    "is_procedural": obj.get("is_procedural", False)
                }
                data["pois"].append(poi_data)
        
        # Collect roads
        for obj in bpy.data.objects:
            if obj.get("is_oneill_road"):
                road_data = {
                    "name": obj.name,
                    "is_procedural": obj.get("is_procedural", False)
                }
                data["roads"].append(road_data)
        
        # Collect terrain objects
        for obj in bpy.data.objects:
            if obj.get("is_unwrapped") or obj.name.endswith("_terrain"):
                terrain_data = {
                    "name": obj.name,
                    "original_object": obj.get("original_object"),
                    "biome_type": obj.get("biome_type"),
                    "biome_name": obj.get("biome_name")
                }
                data["terrain_objects"].append(terrain_data)
        
        return data

# ========================= PANELS =========================

class ONEILL_PT_main_panel(bpy.types.Panel):
    bl_label = "O'Neill Cylinder Manager"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        # Header with mode selector
        box = layout.box()
        box.label(text="Generation Mode:", icon='SCENE_DATA')
        box.prop(props, "generation_mode", expand=True)
        
        layout.separator()

class ONEILL_PT_alignment_panel(bpy.types.Panel):
    bl_label = "Alignment"
    bl_idname = "ONEILL_PT_alignment_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # Alignment settings
        layout.prop(props, "alignment_axis")
        layout.prop(props, "precision_threshold")
        
        # Align button
        col = layout.column()
        if len(selected_meshes) >= 2:
            col.operator("oneill.align_cylinders", 
                        text=f"Align {len(selected_meshes)} Objects", 
                        icon='SNAP_ON')
        else:
            row = col.row()
            row.operator("oneill.align_cylinders", text="Align Objects")
            row.enabled = False
            col.label(text="(Select 2+ mesh objects)", icon='ERROR')

class ONEILL_PT_terrain_panel(bpy.types.Panel):
    bl_label = "Terrain Workflow"
    bl_idname = "ONEILL_PT_terrain_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        unwrapped_objects = [obj for obj in context.selected_objects if obj.get("is_unwrapped")]
        
        # Step 1: Unwrap
        box = layout.box()
        box.label(text="1. Unwrap Cylinders:", icon='MESH_CYLINDER')
        
        if selected_meshes:
            box.operator("oneill.unwrap_cylinder", 
                        text=f"Unwrap {len(selected_meshes)} Objects")
        else:
            row = box.row()
            row.operator("oneill.unwrap_cylinder", text="Unwrap Objects")
            row.enabled = False
        
        # Step 2: Generate terrain
        if unwrapped_objects:
            box = layout.box()
            box.label(text="2. Generate Terrain:", icon='RNDCURVE')
            
            box.prop(props, "terrain_type")
            box.prop(props, "strength")
            box.prop(props, "scale")
            box.prop(props, "seed")
            
            box.operator("oneill.generate_terrain", 
                        text=f"Generate on {len(unwrapped_objects)} Objects")
            
            # Step 3: Re-wrap
            box = layout.box()
            box.label(text="3. Re-wrap to Cylinders:", icon='MESH_CYLINDER')
            box.operator("oneill.rewrap_cylinder", 
                        text=f"Re-wrap {len(unwrapped_objects)} Objects")

class ONEILL_PT_biome_panel(bpy.types.Panel):
    bl_label = "Biome Management"
    bl_idname = "ONEILL_PT_biome_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # Biome list
        biomes = context.scene.get("oneill_biomes", [])
        
        if biomes:
            box = layout.box()
            box.label(text="Active Biome:")
            
            # Biome selector
            row = box.row()
            row.prop(props, "active_biome", text="")
            if props.active_biome < len(biomes):
                active_biome = biomes[props.active_biome]
                row.label(text=active_biome['name'])
            
            # Paint biome button
            if selected_meshes:
                box.operator("oneill.paint_biome", 
                            text=f"Paint on {len(selected_meshes)} Objects",
                            icon='BRUSH_DATA')
        
        # Add biome button
        layout.operator("oneill.add_biome", text="Add New Biome", icon='ADD')

class ONEILL_PT_poi_panel(bpy.types.Panel):
    bl_label = "Points of Interest"
    bl_idname = "ONEILL_PT_poi_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        # Manual POI placement
        if props.generation_mode in ['MANUAL', 'HYBRID']:
            box = layout.box()
            box.label(text="Manual Placement:", icon='OUTLINER_OB_EMPTY')
            box.operator("oneill.place_poi", text="Place POI at Cursor", icon='CURSOR')
        
        # POI statistics
        pois = [obj for obj in bpy.data.objects if obj.get("is_oneill_poi")]
        manual_pois = [obj for obj in pois if not obj.get("is_procedural")]
        procedural_pois = [obj for obj in pois if obj.get("is_procedural")]
        
        if pois:
            box = layout.box()
            box.label(text="POI Statistics:")
            box.label(text=f"Manual: {len(manual_pois)}")
            box.label(text=f"Procedural: {len(procedural_pois)}")
            box.label(text=f"Total: {len(pois)}")

class ONEILL_PT_procedural_panel(bpy.types.Panel):
    bl_label = "Procedural Generation"
    bl_idname = "ONEILL_PT_procedural_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        props = context.scene.oneill_alignment_props
        return props.generation_mode in ['PROCEDURAL', 'HYBRID']
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        # Generation settings
        box = layout.box()
        box.label(text="Generation Settings:", icon='SETTINGS')
        box.prop(props, "settlement_density")
        box.prop(props, "road_density")
        box.prop(props, "resource_density")
        box.prop(props, "procedural_influence")
        box.prop(props, "respect_constraints")
        
        # Generation buttons
        layout.operator("oneill.generate_procedural", 
                       text="Generate Procedural Elements", 
                       icon='MODIFIER')
        layout.operator("oneill.clear_procedural", 
                       text="Clear Procedural Elements", 
                       icon='TRASH')

class ONEILL_PT_export_panel(bpy.types.Panel):
    bl_label = "Export & Data"
    bl_idname = "ONEILL_PT_export_panel"
    bl_parent_id = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        # Export options
        layout.operator("oneill.export_data", 
                       text="Export All Data", 
                       icon='EXPORT')
        
        # Scene statistics
        box = layout.box()
        box.label(text="Scene Statistics:", icon='INFO')
        
        pois = len([obj for obj in bpy.data.objects if obj.get("is_oneill_poi")])
        roads = len([obj for obj in bpy.data.objects if obj.get("is_oneill_road")])
        biomes = len(context.scene.get("oneill_biomes", []))
        terrain_objects = len([obj for obj in bpy.data.objects 
                              if obj.get("is_unwrapped") or obj.name.endswith("_terrain")])
        
        box.label(text=f"POIs: {pois}")
        box.label(text=f"Roads: {roads}")
        box.label(text=f"Biomes: {biomes}")
        box.label(text=f"Terrain Objects: {terrain_objects}")

# ========================= REGISTRATION =========================

classes = [
    ONEILL_biome_properties,
    ONEILL_poi_properties,
    ONEILL_alignment_properties,
    ONEILL_OT_align_cylinders,
    ONEILL_OT_unwrap_cylinder,
    ONEILL_OT_generate_terrain,
    ONEILL_OT_rewrap_cylinder,
    ONEILL_OT_add_biome,
    ONEILL_OT_place_poi,
    ONEILL_OT_generate_procedural,
    ONEILL_OT_clear_procedural,
    ONEILL_OT_paint_biome,
    ONEILL_OT_export_data,
    ONEILL_PT_main_panel,
    ONEILL_PT_alignment_panel,
    ONEILL_PT_terrain_panel,
    ONEILL_PT_biome_panel,
    ONEILL_PT_poi_panel,
    ONEILL_PT_procedural_panel,
    ONEILL_PT_export_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.oneill_alignment_props = bpy.props.PointerProperty(
        type=ONEILL_alignment_properties
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.oneill_alignment_props

if __name__ == "__main__":
    register()