# UV Sampling Techniques Extracted from Paint System Addon
# Key methods for vertex-level precision terrain generation

"""
CRITICAL INSIGHTS FROM PAINT SYSTEM ADDON:

1. UV MAPPING INTEGRATION:
   - Uses UVMAP nodes to map vertex positions to texture coordinates
   - TEX_IMAGE nodes sample painted textures at exact UV positions
   - Template system for consistent node group creation

2. LAYER-BASED COMPOSITION:
   - Multiple layers can be combined with opacity and blending
   - Each layer has its own texture sampling and UV mapping
   - Hierarchical system with folders and sub-layers

3. REAL-TIME IMAGE UPDATES:
   - Direct integration with Blender's image painting system
   - Updates textures immediately as user paints
   - Preserves painted data with proper image packing
"""

import bpy
from bpy.types import NodeTree, Node

class UVTexturesampling:
    """UV-based texture sampling techniques from Paint System"""
    
    @staticmethod
    def create_uv_sampling_node_group():
        """
        Create node group that samples texture at UV coordinates
        Based on Paint System's _PS_Layer_Template approach
        """
        node_group = bpy.data.node_groups.new("UV_Texture_Sampling", 'ShaderNodeTree')
        nodes = node_group.nodes
        links = node_group.links
        
        # Group Input
        group_input = nodes.new('NodeGroupInput')
        node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        node_group.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketObject')
        
        # UV Map node - critical for vertex position to UV coordinate mapping
        uv_map_node = nodes.new('ShaderNodeUVMap')
        uv_map_node.uv_map = "UVMap"  # Default UV map
        
        # Image Texture node - samples texture at UV coordinates
        image_texture_node = nodes.new('ShaderNodeTexImage')
        # Image will be set dynamically
        
        # Links
        links.new(uv_map_node.outputs['UV'], image_texture_node.inputs['Vector'])
        
        # Group Output
        group_output = nodes.new('NodeGroupOutput')
        node_group.interface.new_socket('Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        node_group.interface.new_socket('Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        
        links.new(image_texture_node.outputs['Color'], group_output.inputs['Color'])
        links.new(image_texture_node.outputs['Alpha'], group_output.inputs['Alpha'])
        
        return node_group
    
    @staticmethod
    def setup_uv_mapping_for_object(obj, uv_map_name="UVMap"):
        """
        Ensure object has proper UV mapping for texture sampling
        Based on Paint System's UV map management
        """
        if obj.type != 'MESH':
            return False
        
        mesh = obj.data
        
        # Create UV map if it doesn't exist
        if uv_map_name not in mesh.uv_layers:
            mesh.uv_layers.new(name=uv_map_name)
        
        # Set as active UV map
        mesh.uv_layers[uv_map_name].active = True
        
        return True
    
    @staticmethod
    def create_image_layer_template():
        """
        Create image layer template similar to Paint System's approach
        This provides the foundation for canvas sampling
        """
        template_name = "Canvas_Sampling_Template"
        
        if template_name in bpy.data.node_groups:
            return bpy.data.node_groups[template_name]
        
        node_group = bpy.data.node_groups.new(template_name, 'ShaderNodeTree')
        nodes = node_group.nodes
        links = node_group.links
        
        # Group Input
        group_input = nodes.new('NodeGroupInput')
        node_group.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketObject')
        
        # UV Map node
        uv_map_node = nodes.new('ShaderNodeUVMap')
        uv_map_node.location = (-400, 0)
        
        # Image Texture node
        image_texture_node = nodes.new('ShaderNodeTexImage')
        image_texture_node.location = (-200, 0)
        
        # Color Ramp for intensity control
        color_ramp_node = nodes.new('ShaderNodeValToRGB')
        color_ramp_node.location = (0, 0)
        
        # Mix node for opacity control (Paint System pattern)
        mix_node = nodes.new('ShaderNodeMix')
        mix_node.data_type = 'RGBA'
        mix_node.name = 'Opacity'
        mix_node.location = (200, 0)
        
        # Group Output
        group_output = nodes.new('NodeGroupOutput')
        group_output.location = (400, 0)
        node_group.interface.new_socket('Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        node_group.interface.new_socket('Alpha', in_out='OUTPUT', socket_type='NodeSocketFloat')
        
        # Links
        links.new(uv_map_node.outputs['UV'], image_texture_node.inputs['Vector'])
        links.new(image_texture_node.outputs['Color'], color_ramp_node.inputs['Fac'])
        links.new(color_ramp_node.outputs['Color'], mix_node.inputs['Color1'])
        links.new(mix_node.outputs['Result'], group_output.inputs['Color'])
        links.new(image_texture_node.outputs['Alpha'], group_output.inputs['Alpha'])
        
        return node_group


class CanvasImageManagement:
    """Canvas and image management techniques from Paint System"""
    
    @staticmethod
    def create_canvas_image(name, width, height):
        """
        Create canvas image for painting
        Based on Paint System's image creation approach
        """
        if name in bpy.data.images:
            return bpy.data.images[name]
        
        # Create image
        image = bpy.data.images.new(name, width, height)
        
        # Set to RGBA format
        image.generated_color = (0.5, 0.5, 0.5, 1.0)  # Gray default
        
        # Enable painting
        image.use_fake_user = True
        
        return image
    
    @staticmethod
    def setup_image_for_painting(image):
        """
        Configure image for painting workflow
        Based on Paint System's painting setup
        """
        # Enable alpha channel
        image.alpha_mode = 'STRAIGHT'
        
        # Set colorspace for painting
        image.colorspace_settings.name = 'sRGB'
        
        # Pack image to preserve data
        if not image.packed_file:
            image.pack()
        
        return image


class LayerBlendingSystem:
    """Layer blending and composition from Paint System"""
    
    @staticmethod
    def create_layer_blend_nodes(base_layer, overlay_layer, blend_mode='MIX'):
        """
        Create layer blending nodes similar to Paint System's approach
        Useful for combining multiple biome layers
        """
        node_group = bpy.data.node_groups.new("Layer_Blend", 'ShaderNodeTree')
        nodes = node_group.nodes
        links = node_group.links
        
        # Group inputs
        group_input = nodes.new('NodeGroupInput')
        node_group.interface.new_socket('Base Color', in_out='INPUT', socket_type='NodeSocketColor')
        node_group.interface.new_socket('Overlay Color', in_out='INPUT', socket_type='NodeSocketColor')
        node_group.interface.new_socket('Opacity', in_out='INPUT', socket_type='NodeSocketFloat')
        
        # Blend node
        blend_node = nodes.new('ShaderNodeMix')
        blend_node.data_type = 'RGBA'
        blend_node.blend_type = blend_mode
        
        # Group output
        group_output = nodes.new('NodeGroupOutput')
        node_group.interface.new_socket('Result', in_out='OUTPUT', socket_type='NodeSocketColor')
        
        # Links
        links.new(group_input.outputs['Base Color'], blend_node.inputs['Color1'])
        links.new(group_input.outputs['Overlay Color'], blend_node.inputs['Color2'])
        links.new(group_input.outputs['Opacity'], blend_node.inputs['Fac'])
        links.new(blend_node.outputs['Result'], group_output.inputs['Result'])
        
        return node_group


# Key integration insights for O'Neill Terrain Generator:

"""
INTEGRATION STRATEGY FOR O'NEILL PROJECT:

1. UV COORDINATE MAPPING:
   - Use Paint System's UVMAP → TEX_IMAGE pattern
   - Map flat object world positions to canvas UV coordinates
   - Sample canvas colors at vertex UV positions

2. LAYER-BASED BIOME SYSTEM:
   - Each biome becomes a "layer" like Paint System
   - Use layer blending for multi-biome objects
   - Opacity control based on paint intensity

3. REAL-TIME CANVAS UPDATES:
   - Monitor canvas changes like Paint System
   - Update vertex group weights when canvas changes
   - Preserve painted data with proper packing

4. TEMPLATE SYSTEM:
   - Create reusable node group templates
   - Consistent biome displacement patterns
   - Easy to apply across multiple objects

CRITICAL TECHNIQUE: UV-BASED VERTEX SAMPLING
The key breakthrough is using UV coordinates to sample canvas at exact vertex positions,
then using that data to drive vertex group weights for geometry node displacement.
"""
