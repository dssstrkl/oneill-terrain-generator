bl_info = {
    "name": "O'Neill Cylinder Alignment & Terrain",
    "author": "Assistant",
    "version": (3, 0, 1),
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
    
    strength: bpy.props.FloatProperty(name="Strength", default=2.5, min=0.1, max=5.0)
    heightmap_resolution: bpy.props.EnumProperty(
        name="Resolution",
        items=[('512', "512x512", ""), ('1024', "1024x1024", ""), ('2048', "2048x2048", "")],
        default='1024'
    )

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
    bl_description = "Create flat objects from cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Select cylinder objects to unwrap")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            bpy.ops.mesh.primitive_grid_add(
                size=4, x_subdivisions=30, y_subdivisions=60,
                location=(obj.location.x, obj.location.y + 6, obj.location.z)
            )
            
            flat_obj = context.active_object
            flat_obj.name = f"{obj.name}_flat"
            flat_obj["is_unwrapped"] = True
            flat_obj["original_object"] = obj.name
            obj.hide_viewport = True
        
        self.report({'INFO'}, f"Unwrapped {len(selected_objects)} cylinders")
        return {'FINISHED'}

class ONEILL_OT_create_heightmap_canvas(bpy.types.Operator):
    bl_idname = "oneill.create_heightmap_canvas"
    bl_label = "Create Heightmap"
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
            if heightmap_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[heightmap_name])
            
            heightmap = bpy.data.images.new(heightmap_name, width=resolution, height=resolution, alpha=False, float_buffer=True)
            pixels = [0.5] * (resolution * resolution * 4)
            heightmap.pixels = pixels
            heightmap.update()
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
            bpy.ops.mesh.primitive_cylinder_add(
                radius=2.0, depth=4.0, vertices=32,
                location=(flat_obj.location.x + 8, flat_obj.location.y, flat_obj.location.z)
            )
            
            cylinder_obj = context.active_object
            cylinder_obj.name = f"{original_name}_terrain"
            cylinder_obj["is_terrain_cylinder"] = True
        
        self.report({'INFO'}, f"Rewrapped {len(flat_objects)} objects to cylinders")
        return {'FINISHED'}

# ========================= UI PANELS =========================

class ONEILL_PT_main(bpy.types.Panel):
    bl_label = "O'Neill Cylinder Terrain"
    bl_idname = "ONEILL_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    
    def draw(self, context):
        layout = self.layout
        
        # Status
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("is_aligned")]
        flat_objects = [obj for obj in bpy.data.objects if obj.get("is_unwrapped")]
        
        box = layout.box()
        box.label(text="O'Neill Terrain System", icon='INFO')
        box.label(text=f"Aligned: {len(aligned_objects)}")
        box.label(text=f"Flat Objects: {len(flat_objects)}")
        
        # Workflow buttons
        layout.separator()
        layout.label(text="Workflow:", icon='SEQUENCE')
        
        col = layout.column(align=True)
        col.operator("oneill.align_cylinders", text="1. Align Cylinders", icon='ALIGN')
        col.operator("oneill.unwrap_cylinder", text="2. Unwrap to Flat", icon='MOD_MESHDEFORM')
        col.operator("oneill.create_heightmap_canvas", text="3. Create Heightmap", icon='IMAGE_DATA')
        col.operator("oneill.rewrap_cylinder", text="4. Rewrap to Cylinder", icon='MESH_CYLINDER')

class ONEILL_PT_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "ONEILL_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    bl_parent_id = "ONEILL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_alignment_props
        
        col = layout.column()
        col.prop(props, "alignment_axis")
        col.prop(props, "heightmap_resolution")
        col.prop(props, "strength")

# ========================= REGISTRATION =========================

classes = [
    ONEILL_biome_properties,
    ONEILL_alignment_properties,
    ONEILL_OT_align_cylinders,
    ONEILL_OT_unwrap_cylinder,
    ONEILL_OT_create_heightmap_canvas,
    ONEILL_OT_rewrap_cylinder,
    ONEILL_PT_main,
    ONEILL_PT_settings,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.oneill_alignment_props = bpy.props.PointerProperty(type=ONEILL_alignment_properties)
    bpy.types.Scene.oneill_biomes = bpy.props.CollectionProperty(type=ONEILL_biome_properties)
    print("O'Neill Cylinder Terrain System registered successfully")

def unregister():
    if hasattr(bpy.types.Scene, 'oneill_alignment_props'):
        del bpy.types.Scene.oneill_alignment_props
    if hasattr(bpy.types.Scene, 'oneill_biomes'):
        del bpy.types.Scene.oneill_biomes
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("O'Neill Cylinder Terrain System unregistered")

if __name__ == "__main__":
    register()
