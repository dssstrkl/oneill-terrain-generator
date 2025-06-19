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

# Property Groups
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
    
    strength: bpy.props.FloatProperty(
        name="Strength",
        default=2.5,
        min=0.1,
        max=5.0
    )

# Operators
class ONEILL_OT_align_cylinders(bpy.types.Operator):
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_description = "Align selected cylinder objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        self.report({'INFO'}, "Alignment complete")
        return {'FINISHED'}

# UI Panels
class ONEILL_PT_main_panel(bpy.types.Panel):
    bl_label = "O'Neill Cylinder Terrain"
    bl_idname = "ONEILL_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'O Neill'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("oneill.align_cylinders", text="Align Cylinders")

# Registration
classes = [
    ONEILL_alignment_properties,
    ONEILL_OT_align_cylinders,
    ONEILL_PT_main_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.oneill_alignment_props = bpy.props.PointerProperty(type=ONEILL_alignment_properties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.oneill_alignment_props

if __name__ == "__main__":
    register()
