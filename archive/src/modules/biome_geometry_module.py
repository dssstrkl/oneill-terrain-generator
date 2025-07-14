# biome_geometry_generator.py - Phase 2A Biome Generation System
# MIT License - O'Neill Cylinder Terrain Generator
# Copyright (c) 2025 Paul Ward

"""
Biome Geometry Generator Module

Generates geometry node groups for O'Neill cylinder biomes in Python.
Designed to integrate with Phase 1 terrain painting system for real-time preview.

This module provides:
- Python-generated geometry nodes for 6 biome types
- Integration with Phase 1 painting system
- Real-time terrain preview capabilities
- Clean architecture for Phase 2A development
"""

import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, FloatProperty, EnumProperty
from mathutils import Vector
import bmesh

# Biome type definitions (matches Phase 1 painting system)
BIOME_TYPES = [
    ('archipelago', '🏝️ Archipelago', 'Island chains with water features'),
    ('mountain', '🏔️ Mountain', 'Dramatic peaks with elevation gradients'),
    ('canyon', '🏜️ Canyon', 'Mesa formations with valley cutting'),
    ('rolling_hills', '🏞️ Rolling Hills', 'Gentle terrain for comfortable exploration'),
    ('desert', '🌵 Desert', 'Dune formations with varied texture'),
    ('ocean', '🌊 Ocean', 'Underwater ridges with depth variation')
]

class BiomeGeometryGenerator:
    """
    Python-based biome geometry generator for O'Neill cylinder terrain.
    Creates geometry node groups programmatically for maximum control and integration.
    """
    
    def __init__(self):
        self.biome_types = [biome[0] for biome in BIOME_TYPES]
        self.generated_node_groups = {}
        self._populate_existing_biomes()
        
    def _populate_existing_biomes(self):
        """Find and register existing biome node groups"""
        for ng_name in bpy.data.node_groups.keys():
            if "ONeill_Biome" in ng_name:
                biome_name = ng_name.split('_')[-1].lower()
                # Handle special cases
                if biome_name == 'rolling':
                    biome_name = 'rolling_hills'
                if biome_name in self.biome_types:
                    self.generated_node_groups[biome_name] = bpy.data.node_groups[ng_name]
        
    def create_biome_node_group(self, biome_name):
        """Create a geometry node group for specified biome"""
        if biome_name not in self.biome_types:
            raise ValueError(f"Biome '{biome_name}' not supported. Available: {self.biome_types}")
            
        node_group_name = f"ONeill_Biome_{biome_name.title().replace('_', '')}"
        
        # Return existing if available
        if node_group_name in bpy.data.node_groups:
            return bpy.data.node_groups[node_group_name]
            
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create input and output nodes
        input_node = node_group.nodes.new('NodeGroupInput')
        output_node = node_group.nodes.new('NodeGroupOutput')
        
        input_node.location = (-400, 0)
        output_node.location = (400, 0)
        
        # Define standard interface for all biomes
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='INPUT')
        node_group.interface.new_socket('Heightmap_Strength', socket_type='NodeSocketFloat', in_out='INPUT')
        node_group.interface.new_socket('Feature_Scale', socket_type='NodeSocketFloat', in_out='INPUT')
        node_group.interface.new_socket('Biome_Intensity', socket_type='NodeSocketFloat', in_out='INPUT')
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='OUTPUT')
        
        # Set default values
        strength_input = node_group.interface.items_tree['Heightmap_Strength']
        strength_input.default_value = 1.0
        strength_input.min_value = 0.0
        strength_input.max_value = 5.0
        
        scale_input = node_group.interface.items_tree['Feature_Scale']
        scale_input.default_value = 1.0
        scale_input.min_value = 0.1
        scale_input.max_value = 10.0
        
        intensity_input = node_group.interface.items_tree['Biome_Intensity']
        intensity_input.default_value = 1.0
        intensity_input.min_value = 0.0
        intensity_input.max_value = 2.0
        
        # Create biome-specific node network
        self._create_biome_nodes(node_group, input_node, output_node, biome_name)
        
        self.generated_node_groups[biome_name] = node_group
        print(f"Created biome node group: {node_group_name}")
        return node_group
    
    def _create_biome_nodes(self, node_group, input_node, output_node, biome_name):
        """Create biome-specific node network with optimized parameters"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Common nodes for all biomes
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 100)
        
        # Primary noise for main terrain features
        noise1 = nodes.new('ShaderNodeTexNoise')
        noise1.location = (-200, 150)
        
        # Secondary noise for surface detail
        noise2 = nodes.new('ShaderNodeTexNoise')
        noise2.location = (-200, 50)
        
        # Biome-specific noise parameters for authentic terrain characteristics
        noise_params = {
            'mountain': {
                'scale1': 3.0, 'detail1': 8.0, 'rough1': 0.8,
                'scale2': 15.0, 'detail2': 4.0, 'rough2': 0.5,
                'mix_factor': 0.4, 'description': 'Dramatic peaks with sharp details'
            },
            'archipelago': {
                'scale1': 1.5, 'detail1': 3.0, 'rough1': 0.6,
                'scale2': 8.0, 'detail2': 6.0, 'rough2': 0.5,
                'mix_factor': 0.2, 'description': 'Island chains with coastal variation'
            },
            'canyon': {
                'scale1': 2.0, 'detail1': 4.0, 'rough1': 0.8,
                'scale2': 6.0, 'detail2': 8.0, 'rough2': 0.6,
                'mix_factor': 0.4, 'description': 'Mesa formations with deep valleys'
            },
            'rolling_hills': {
                'scale1': 1.0, 'detail1': 2.0, 'rough1': 0.3,
                'scale2': 4.0, 'detail2': 4.0, 'rough2': 0.4,
                'mix_factor': 0.2, 'description': 'Gentle undulating terrain'
            },
            'desert': {
                'scale1': 1.2, 'detail1': 3.0, 'rough1': 0.5,
                'scale2': 5.0, 'detail2': 6.0, 'rough2': 0.6,
                'mix_factor': 0.2, 'description': 'Dune formations with wind patterns'
            },
            'ocean': {
                'scale1': 0.8, 'detail1': 2.0, 'rough1': 0.4,
                'scale2': 3.0, 'detail2': 6.0, 'rough2': 0.7,
                'mix_factor': 0.2, 'description': 'Underwater ridges and depth variation'
            }
        }
        
        params = noise_params[biome_name]
        
        # Configure primary noise
        noise1.inputs['Scale'].default_value = params['scale1']
        noise1.inputs['Detail'].default_value = params['detail1']
        noise1.inputs['Roughness'].default_value = params['rough1']
        
        # Configure secondary noise
        noise2.inputs['Scale'].default_value = params['scale2']
        noise2.inputs['Detail'].default_value = params['detail2']
        noise2.inputs['Roughness'].default_value = params.get('rough2', 0.5)
        
        # Scale secondary noise contribution
        scale_noise2 = nodes.new('ShaderNodeMath')
        scale_noise2.location = (-150, 50)
        scale_noise2.operation = 'MULTIPLY'
        scale_noise2.inputs[1].default_value = params['mix_factor']
        
        # Combine noise layers
        add_noise = nodes.new('ShaderNodeMath')
        add_noise.location = (-100, 100)
        add_noise.operation = 'ADD'
        
        # Apply heightmap strength scaling
        multiply_strength = nodes.new('ShaderNodeMath')
        multiply_strength.location = (0, 100)
        multiply_strength.operation = 'MULTIPLY'
        
        # Special handling for ocean biome (negative displacement for underwater effect)
        if biome_name == 'ocean':
            invert = nodes.new('ShaderNodeMath')
            invert.location = (50, 50)
            invert.operation = 'MULTIPLY'
            invert.inputs[1].default_value = -1.0
            links.new(multiply_strength.outputs['Value'], invert.inputs[0])
            height_output = invert.outputs['Value']
        else:
            height_output = multiply_strength.outputs['Value']
        
        # Combine to displacement vector
        combine_xyz = nodes.new('ShaderNodeCombineXYZ')
        combine_xyz.location = (100, 0)
        combine_xyz.inputs['X'].default_value = 0.0
        combine_xyz.inputs['Y'].default_value = 0.0
        
        # Apply displacement to geometry
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Connect the node network
        links.new(position.outputs['Position'], noise1.inputs['Vector'])
        links.new(position.outputs['Position'], noise2.inputs['Vector'])
        links.new(noise2.outputs['Color'], scale_noise2.inputs[0])
        links.new(noise1.outputs['Color'], add_noise.inputs[0])
        links.new(scale_noise2.outputs['Value'], add_noise.inputs[1])
        links.new(add_noise.outputs['Value'], multiply_strength.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], multiply_strength.inputs[1])
        links.new(height_output, combine_xyz.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(combine_xyz.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])
    
    def create_all_biomes(self):
        """Create all 6 biome node groups at once"""
        print("Creating all biome node groups...")
        
        created_count = 0
        for biome_name in self.biome_types:
            try:
                self.create_biome_node_group(biome_name)
                created_count += 1
                print(f"✅ {biome_name.title().replace('_', ' ')} biome ready")
            except Exception as e:
                print(f"❌ Error creating {biome_name} biome: {e}")
        
        print(f"\nCompleted! Created/verified {created_count}/{len(self.biome_types)} biome node groups.")
        return self.generated_node_groups
    
    def get_available_biomes(self):
        """Get list of available biome node groups"""
        return list(self.generated_node_groups.keys())
    
    def get_biome_info(self, biome_name):
        """Get information about a specific biome"""
        if biome_name not in self.biome_types:
            return None
            
        biome_data = next((b for b in BIOME_TYPES if b[0] == biome_name), None)
        node_group = self.generated_node_groups.get(biome_name)
        
        return {
            'name': biome_name,
            'display_name': biome_data[1] if biome_data else biome_name.title(),
            'description': biome_data[2] if biome_data else 'Custom biome',
            'node_group': node_group.name if node_group else None,
            'available': node_group is not None,
            'node_count': len(node_group.nodes) if node_group else 0
        }


class BiomePaintingIntegrator:
    """
    Integrates BiomeGeometryGenerator with Phase 1 terrain painting system.
    Provides real-time biome application based on painted masks.
    """
    
    def __init__(self, biome_generator):
        self.biome_generator = biome_generator
        self.biome_color_mapping = {
            'archipelago': (0.2, 0.8, 0.6, 1.0),  # Teal
            'mountain': (0.5, 0.5, 0.5, 1.0),     # Gray  
            'canyon': (0.8, 0.4, 0.2, 1.0),       # Orange
            'rolling_hills': (0.4, 0.8, 0.3, 1.0), # Green
            'desert': (0.9, 0.7, 0.4, 1.0),       # Sand
            'ocean': (0.1, 0.3, 0.9, 1.0)         # Blue
        }
        
    def apply_biome_to_object(self, obj, biome_name, strength=1.0, scale=1.0, intensity=1.0, replace_existing=True):
        """Apply a specific biome to an object with parameters"""
        
        if biome_name not in self.biome_generator.biome_types:
            raise ValueError(f"Unknown biome: {biome_name}")
        
        # Get or create the biome node group
        if biome_name not in self.biome_generator.generated_node_groups:
            biome_ng = self.biome_generator.create_biome_node_group(biome_name)
        else:
            biome_ng = self.biome_generator.generated_node_groups[biome_name]
        
        # Remove existing biome modifiers if replacing
        if replace_existing:
            for modifier in list(obj.modifiers):
                if (modifier.type == 'NODES' and 
                    modifier.node_group and 
                    'ONeill_Biome' in modifier.node_group.name):
                    obj.modifiers.remove(modifier)
        
        # Add new biome modifier
        modifier_name = f"Biome_{biome_name.title().replace('_', '')}"
        modifier = obj.modifiers.new(modifier_name, 'NODES')
        modifier.node_group = biome_ng
        
        # Set parameters
        modifier["Input_2"] = strength   # Heightmap_Strength
        modifier["Input_3"] = scale      # Feature_Scale
        modifier["Input_4"] = intensity  # Biome_Intensity
        
        print(f"Applied {biome_name} biome to {obj.name} (strength: {strength})")
        return modifier
    
    def get_biome_color(self, biome_name):
        """Get the color associated with a biome for painting"""
        return self.biome_color_mapping.get(biome_name, (0.8, 0.8, 0.8, 1.0))
    
    def detect_painted_biome(self, painted_color):
        """Detect which biome a painted color represents"""
        min_distance = float('inf')
        closest_biome = None
        
        for biome_name, biome_color in self.biome_color_mapping.items():
            # Calculate color distance (simple RGB distance)
            distance = sum((a - b) ** 2 for a, b in zip(painted_color[:3], biome_color[:3]))
            if distance < min_distance:
                min_distance = distance
                closest_biome = biome_name
        
        return closest_biome if min_distance < 0.1 else None  # Threshold for color matching


# Operators for biome management
class ONEILL_OT_CreateAllBiomes(Operator):
    """Create all biome node groups"""
    bl_idname = "oneill.create_all_biomes"
    bl_label = "Create All Biomes"
    bl_description = "Generate all 6 biome node groups for terrain painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            generator = BiomeGeometryGenerator()
            created_biomes = generator.create_all_biomes()
            
            self.report({'INFO'}, f"Created {len(created_biomes)} biome node groups")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error creating biomes: {e}")
            return {'CANCELLED'}


class ONEILL_OT_ApplyBiomeToSelected(Operator):
    """Apply biome to selected objects"""
    bl_idname = "oneill.apply_biome_to_selected"
    bl_label = "Apply Biome to Selected"
    bl_description = "Apply chosen biome to all selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_type: EnumProperty(
        name="Biome Type",
        description="Type of biome to apply",
        items=BIOME_TYPES,
        default='mountain'
    )
    
    strength: FloatProperty(
        name="Strength",
        description="Terrain displacement strength",
        default=1.0,
        min=0.0,
        max=5.0
    )
    
    def execute(self, context):
        try:
            generator = BiomeGeometryGenerator()
            integrator = BiomePaintingIntegrator(generator)
            
            applied_count = 0
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    integrator.apply_biome_to_object(obj, self.biome_type, self.strength)
                    applied_count += 1
            
            if applied_count > 0:
                self.report({'INFO'}, f"Applied {self.biome_type} biome to {applied_count} objects")
                context.view_layer.update()
            else:
                self.report({'WARNING'}, "No mesh objects selected")
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error applying biome: {e}")
            return {'CANCELLED'}


# Panel for biome controls
class ONEILL_PT_BiomeControls(Panel):
    """Panel for biome generation and application controls"""
    bl_label = "🧬 Biome Generation"
    bl_idname = "ONEILL_PT_biome_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill Terrain"
    bl_parent_id = "ONEILL_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        
        # Create all biomes button
        row = layout.row()
        row.scale_y = 1.2
        row.operator("oneill.create_all_biomes", icon='NODETREE')
        
        layout.separator()
        
        # Biome application
        box = layout.box()
        box.label(text="Apply to Selected:", icon='BRUSH_DATA')
        
        row = box.row()
        op = row.operator("oneill.apply_biome_to_selected", text="Mountain", icon='MESH_ICOSPHERE')
        op.biome_type = 'mountain'
        op.strength = 1.5
        
        row = box.row()
        op = row.operator("oneill.apply_biome_to_selected", text="Canyon", icon='MESH_LANDSCAPE')
        op.biome_type = 'canyon'
        op.strength = 1.2
        
        row = box.row()
        op = row.operator("oneill.apply_biome_to_selected", text="Ocean", icon='MOD_OCEAN')
        op.biome_type = 'ocean'
        op.strength = 0.8


# Registration
classes = [
    ONEILL_OT_CreateAllBiomes,
    ONEILL_OT_ApplyBiomeToSelected,
    ONEILL_PT_BiomeControls,
]

def register():
    """Register biome geometry generator module"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("O'Neill Biome Geometry Generator registered")

def unregister():
    """Unregister biome geometry generator module"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("O'Neill Biome Geometry Generator unregistered")

if __name__ == "__main__":
    register()
