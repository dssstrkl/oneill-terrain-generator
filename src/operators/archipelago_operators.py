"""
O'Neill Terrain Generator - Archipelago Operators
Blender operators for integrating archipelago generation with O'Neill workflow
"""

import bpy
from ..utils.asset_manager import asset_manager

class ONEILL_OT_ApplyArchipelago(bpy.types.Operator):
    """Apply archipelago terrain generator to selected O'Neill flat objects"""
    bl_idname = "oneill.apply_archipelago"
    bl_label = "Apply Archipelago Terrain"
    bl_description = "Apply procedural archipelago generation to unwrapped O'Neill cylinder objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: bpy.props.EnumProperty(
        name="Preset",
        description="Archipelago terrain preset configuration",
        items=[
            ('dense_archipelago', "Dense Archipelago", "Many small islands with detailed coastlines"),
            ('sparse_islands', "Sparse Islands", "Few large islands with simple coastlines"), 
            ('game_optimized', "Game Optimized", "Balanced for real-time rendering performance"),
        ],
        default='game_optimized'
    )
    
    def execute(self, context):
        # Get O'Neill flat objects (from heightmap workflow)
        flat_objects = [obj for obj in context.selected_objects 
                       if obj.type == 'MESH' and obj.get("oneill_flat")]
        
        if not flat_objects:
            # Also check for any high-subdivision mesh objects
            high_res_objects = [obj for obj in context.selected_objects 
                              if obj.type == 'MESH' and len(obj.data.vertices) > 10000]
            
            if not high_res_objects:
                self.report({'ERROR'}, "Select unwrapped O'Neill flat objects or high-subdivision meshes")
                return {'CANCELLED'}
            else:
                # Use high-res objects as backup
                flat_objects = high_res_objects
                self.report({'INFO'}, f"Applying to {len(flat_objects)} high-resolution objects")
        
        try:
            applied_count = 0
            for obj in flat_objects:
                asset_manager.apply_archipelago_to_object(obj, self.preset_name)
                applied_count += 1
            
            self.report({'INFO'}, f"Applied {self.preset_name} archipelago to {applied_count} objects")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply archipelago: {str(e)}")
            return {'CANCELLED'}

class ONEILL_OT_LoadArchipelagoAsset(bpy.types.Operator):
    """Load archipelago node group asset into Blender"""
    bl_idname = "oneill.load_archipelago_asset"
    bl_label = "Load Archipelago Asset"
    bl_description = "Load the archipelago terrain generator node group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            node_group = asset_manager.load_archipelago_nodegroup()
            self.report({'INFO'}, f"Loaded archipelago asset: {node_group.name}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load archipelago asset: {str(e)}")
            return {'CANCELLED'}

# Registration
classes = [
    ONEILL_OT_ApplyArchipelago,
    ONEILL_OT_LoadArchipelagoAsset,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
