bl_info = {
    "name": "O'Neill Cylinder Alignment & Terrain",
    "author": "Assistant",
    "version": (3, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > O'Neill",
    "description": "Enhanced terrain generation for O'Neill cylinders",
    "category": "3D View",
}

import bpy
import bmesh
from mathutils import Vector
import math
import random

# ========================= PROPERTY GROUPS =========================

class ONEILL_biome_properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Biome Name", default="New Biome")
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.2, 0.8, 0.2),
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
        ],
        default='VILLAGE'
    )
    population: bpy.props.IntProperty(name="Population", default=1000, min=0)
    faction: bpy.props.StringProperty(name="Faction", default="Neutral")

class ONEILL_terrain_layer_properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Layer Name", default="New Layer")
    layer_type: bpy.props.EnumProperty(
        name="Layer Type",
        items=[
            ('HEIGHTMAP', "Heightmap", "Base heightmap layer"),
            ('NOISE', "Procedural Noise", "Generated noise layer"),
            ('EROSION', "Erosion", "Erosion simulation"),
        ],
        default='HEIGHTMAP'
    )
    blend_mode: bpy.props.EnumProperty(
        name="Blend Mode",
        items=[
            ('ADD', "Add", "Additive blending"),
            ('MULTIPLY', "Multiply", "Multiplicative blending"),
            ('OVERLAY', "Overlay", "Overlay blending"),
        ],
        default='ADD'
    )
    weight: bpy.props.FloatProperty(
        name="Weight",
        default=1.0,
        min=0.0, max=2.0
    )
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=True
    )

class ONEILL_alignment_properties(bpy.types.PropertyGroup):
    alignment_axis: bpy.props.EnumProperty(
        name="Alignment Axis",
        items=[
            ('X', "X-Axis", "Align along X-axis"),
            ('Y', "Y-Axis", "Align along Y-axis"),
            ('Z', "Z-Axis", "Align along Z-axis"),
        ],
        default='X'
    )
    
    precision_threshold: bpy.props.FloatProperty(
        name="Precision Threshold",
        default=0.001,
        min=0.0001,
        max=0.1
    )
    
    terrain_type: bpy.props.EnumProperty(
        name="Terrain Type",
        items=[
            ('HEIGHTMAP_PAINT', "Heightmap Painting", "Paint-based terrain"),
            ('MOUNTAINS', "Mountains", "High peaks"),
            ('HILLS', "Rolling Hills", "Gentle terrain"),
            ('CANYON', "Canyon", "Deep valleys"),
        ],
        default='HEIGHTMAP_PAINT'
    )
    
    strength: bpy.props.FloatProperty(
        name="Strength",
        default=2.5,
        min=0.1,
        max=5.0
    )
    
    scale: bpy.props.FloatProperty(
        name="Scale",
        default=5.0,
        min=0.1,
        max=20.0
    )
    
    seed: bpy.props.IntProperty(
        name="Seed",
        default=42,
        min=0
    )
    
    brush_size: bpy.props.FloatProperty(
        name="Brush Size",
        default=50.0,
        min=1.0, max=200.0
    )
    
    brush_strength: bpy.props.FloatProperty(
        name="Brush Strength",
        default=0.5,
        min=0.0, max=2.0
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
    
    # Collections
    terrain_layers: bpy.props.CollectionProperty(type=ONEILL_terrain_layer_properties)
    active_layer_index: bpy.props.IntProperty(name="Active Layer", default=0)

# ========================= OPERATORS =========================

class ONEILL_OT_align_cylinders(bpy.types.Operator):
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_description = "Align selected cylinder objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 cylinder objects")
            return {'CANCELLED'}
        
        props = context.scene.oneill_alignment_props
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[props.alignment_axis]
        
        # Simple alignment along chosen axis
        reference_obj = selected_objects[0]
        reference_pos = reference_obj.location[axis_index]
        
        aligned_count = 0
        for obj in selected_objects[1:]:
            new_location = obj.location.copy()
            new_location[axis_index] = reference_pos
            obj.location = new_location
            obj["is_aligned"] = True
            aligned_count += 1
        
        reference_obj["is_aligned"] = True
        
        self.report({'INFO'}, f"Aligned {aligned_count + 1} objects along {props.alignment_axis}-axis")
        return {'FINISHED'}

class ONEILL_OT_unwrap_cylinder(bpy.types.Operator):
    bl_idname = "oneill.unwrap_cylinder"
    bl_label = "Unwrap Cylinders"
    bl_description = "Create flat objects from cylinders for terrain editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Select cylinder objects to unwrap")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            # Create flat representation
            bpy.ops.mesh.primitive_grid_add(
                size=4,
                x_subdivisions=30,
                y_subdivisions=60,
                location=(obj.location.x, obj.location.y + 6, obj.location.z)
            )
            
            flat_obj = context.active_object
            flat_obj.name = f"{obj.name}_flat"
            flat_obj["is_unwrapped"] = True
            flat_obj["original_object"] = obj.name
            flat_obj["cylinder_radius"] = 2.0
            flat_obj["cylinder_length"] = 4.0
            
            # Hide original
            obj.hide_viewport = True
        
        self.report({'INFO'}, f"Unwrapped {len(selected_objects)} cylinders")
        return {'FINISHED'}

class ONEILL_OT_create_heightmap_canvas(bpy.types.Operator):
    bl_idname = "oneill.create_heightmap_canvas"
    bl_label = "Create Heightmap Canvas"
    bl_description = "Create heightmap for terrain painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_alignment_props
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.type == 'MESH' and obj.get("is_unwrapped")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select unwrapped flat objects")
            return {'CANCELLED'}
        
        resolution = int(props.heightmap_resolution)
        
        for flat_obj in flat_objects:
            heightmap_name = f"{flat_obj.name}_Heightmap"
            
            # Remove existing
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
            
            # Initialize with neutral gray
            pixels = [0.5] * (resolution * resolution * 4)
            heightmap.pixels = pixels
            heightmap.update()
            
            # Link to object
            flat_obj["heightmap_image"] = heightmap.name
        
        self.report({'INFO'}, f"Created heightmaps for {len(flat_objects)} objects")
        return {'FINISHED'}

class ONEILL_OT_rewrap_cylinder(bpy.types.Operator):
    bl_idname = "oneill.rewrap_cylinder"
    bl_label = "Rewrap to Cylinder"
    bl_description = "Convert flat terrain back to cylinder"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.type == 'MESH' and obj.get("is_unwrapped")]
        
        if not flat_objects:
            self.report({'ERROR'}, "Select unwrapped flat objects")
            return {'CANCELLED'}
        
        for flat_obj in flat_objects:
            original_name = flat_obj.get("original_object", "Unknown")
            
            # Create new cylinder
            bpy.ops.mesh.primitive_cylinder_add(
                radius=2.0,
                depth=4.0,
                vertices=32,
                location=(flat_obj.location.x + 8, flat_obj.location.y, flat_obj.location.z)
            )
            
            cylinder_obj = context.active_object
            cylinder_obj.name = f"{original_name}_terrain"
            cylinder_obj["is_terrain_cylinder"] = True
            cylinder_obj["source_flat_object"] = flat_obj.name
        
        self.report({'INFO'}, f"Rewrapped {len(flat_objects)} objects to cylinders")
        return {'FINISHED'}

# ========================= UI PANELS =========================

class ONEILL_PT_main_panel(bpy.types.Panel):
    bl_label = "O'Neill Cylinder Terrain"
    bl_idname = "ONEILL_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        # Status
        box = layout.box()
        box.label(text="O'Neill Terrain System", icon='INFO')
        
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("is_aligned")]
        flat_objects = [obj for obj in bpy.data.objects if obj.get("is_unwrapped")]
        
        box.label(text=f"Aligned: {len(aligned_objects)}")
        box.label(text=f"Flat Objects: {len(flat_objects)}")
        
        # MAIN WORKFLOW BUTTONS
        layout.separator()
        layout.label(text="Main Workflow:", icon='SEQUENCE')
        
        # Step 1: Alignment
        row = layout.row(align=True)
        row.operator("oneill.align_cylinders", text="1. Align Cylinders", icon='ALIGN')
        
        # Step 2: Unwrapping  
        row = layout.row(align=True)
        row.operator("oneill.unwrap_cylinder", text="2. Unwrap to Flat", icon='MOD_MESHDEFORM')
        
        # Step 3: Heightmap
        row = layout.row(align=True)
        row.operator("oneill.create_heightmap_canvas", text="3. Create Heightmap", icon='IMAGE_DATA')
        
        # Step 4: Rewrap
        row = layout.row(align=True)
        row.operator("oneill.rewrap_cylinder", text="4. Rewrap to Cylinder", icon='MESH_CYLINDER')

class ONEILL_PT_alignment_panel(bpy.types.Panel):
    bl_label = "Alignment Settings"
    bl_idname = "ONEILL_PT_alignment"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    bl_parent_id = "ONEILL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        col = layout.column(align=True)
        col.label(text="Alignment Settings:")
        col.prop(props, "alignment_axis")
        col.prop(props, "precision_threshold")

class ONEILL_PT_terrain_panel(bpy.types.Panel):
    bl_label = "Terrain Settings"
    bl_idname = "ONEILL_PT_terrain"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    bl_parent_id = "ONEILL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        # Terrain settings
        col = layout.column(align=True)
        col.label(text="Terrain Generation:")
        col.prop(props, "terrain_type")
        col.prop(props, "heightmap_resolution")
        col.prop(props, "strength")
        col.prop(props, "brush_size")

# ========================= REGISTRATION =========================

classes = [
    # Property Groups (must be registered first)
    ONEILL_biome_properties,
    ONEILL_poi_properties,
    ONEILL_terrain_layer_properties,
    ONEILL_alignment_properties,
    
    # Operators
    ONEILL_OT_align_cylinders,
    ONEILL_OT_unwrap_cylinder,
    ONEILL_OT_create_heightmap_canvas,
    ONEILL_OT_rewrap_cylinder,
    
    # UI Panels
    ONEILL_PT_main_panel,
    ONEILL_PT_alignment_panel,
    ONEILL_PT_terrain_panel,
]

def register():
    # Register classes first
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Then add scene properties (after classes are registered)
    bpy.types.Scene.oneill_alignment_props = bpy.props.PointerProperty(type=ONEILL_alignment_properties)
    bpy.types.Scene.oneill_biomes = bpy.props.CollectionProperty(type=ONEILL_biome_properties)
    bpy.types.Scene.oneill_pois = bpy.props.CollectionProperty(type=ONEILL_poi_properties)
    bpy.types.Scene.oneill_biomes_index = bpy.props.IntProperty(name="Active Biome Index")
    bpy.types.Scene.oneill_pois_index = bpy.props.IntProperty(name="Active POI Index")
    
    print("O'Neill Cylinder Terrain System registered successfully")

def unregister():
    # Remove scene properties first
    if hasattr(bpy.types.Scene, 'oneill_alignment_props'):
        del bpy.types.Scene.oneill_alignment_props
    if hasattr(bpy.types.Scene, 'oneill_biomes'):
        del bpy.types.Scene.oneill_biomes
    if hasattr(bpy.types.Scene, 'oneill_pois'):
        del bpy.types.Scene.oneill_pois
    if hasattr(bpy.types.Scene, 'oneill_biomes_index'):
        del bpy.types.Scene.oneill_biomes_index
    if hasattr(bpy.types.Scene, 'oneill_pois_index'):
        del bpy.types.Scene.oneill_pois_index
    
    # Then unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("O'Neill Cylinder Terrain System unregistered")

if __name__ == "__main__":
    register()
