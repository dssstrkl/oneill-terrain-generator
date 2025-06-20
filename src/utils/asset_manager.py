"""
O'Neill Terrain Generator - Asset Manager
Handles loading and managing geometry node assets for O'Neill cylinder terrain generation
"""

import bpy
import os
import json
from pathlib import Path

class AssetManager:
    """Manages geometry node assets for the O'Neill Terrain Generator"""
    
    def __init__(self):
        # Asset paths relative to add-on location
        self.addon_path = Path(__file__).parent.parent
        self.assets_path = self.addon_path / "assets"
        self.geometry_nodes_path = self.assets_path / "geometry_nodes"
        self.presets_path = self.assets_path / "presets"
        
        # Project reference for development
        self.project_path = Path("/Documents/Project/oneill terrain generator")
    
    def load_archipelago_nodegroup(self):
        """Load the O'Neill archipelago terrain generator node group"""
        node_group_name = "ONeill_Archipelago_Terrain_Generator"
        
        # Check if already loaded
        if node_group_name in bpy.data.node_groups:
            print(f"Node group '{node_group_name}' already loaded")
            return bpy.data.node_groups[node_group_name]
        
        # Load from asset file
        asset_file = self.geometry_nodes_path / "archipelago_terrain_generator.blend"
        
        if not asset_file.exists():
            raise FileNotFoundError(f"Archipelago asset file not found: {asset_file}")
        
        # Append the node group
        with bpy.data.libraries.load(str(asset_file)) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]
                print(f"Loading node group: {node_group_name}")
        
        if node_group_name in bpy.data.node_groups:
            node_group = bpy.data.node_groups[node_group_name]
            node_group.use_fake_user = True  # Keep it loaded
            print(f"✅ Successfully loaded archipelago node group")
            return node_group
        else:
            raise RuntimeError(f"Failed to load node group: {node_group_name}")
    
    def apply_archipelago_to_object(self, obj, preset_name=None):
        """Apply archipelago terrain to an O'Neill cylinder flat object"""
        if obj.type != 'MESH':
            raise ValueError("Object must be a mesh")
        
        # Validate object for archipelago generation
        vertex_count = len(obj.data.vertices)
        if vertex_count < 10000:
            print(f"⚠️  Warning: Object {obj.name} has only {vertex_count:,} vertices.")
            print(f"   Recommend 100k+ vertices for detailed archipelago coastlines.")
        
        # Check if object is from O'Neill workflow
        if obj.get("oneill_flat"):
            print(f"✅ Applying archipelago to O'Neill flat object: {obj.name}")
        
        # Load the node group
        node_group = self.load_archipelago_nodegroup()
        
        # Add archipelago modifier
        modifier_name = "Archipelago_Terrain"
        if modifier_name in obj.modifiers:
            obj.modifiers.remove(obj.modifiers[modifier_name])
        
        modifier = obj.modifiers.new(modifier_name, 'NODES')
        modifier.node_group = node_group
        
        # Mark object with archipelago metadata
        obj["oneill_archipelago"] = True
        obj["archipelago_preset"] = preset_name or "default"
        
        print(f"✅ Archipelago terrain applied to {obj.name}")
        return modifier

# Global asset manager instance
asset_manager = AssetManager()
