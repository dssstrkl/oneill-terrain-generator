import bpy
import bmesh
from mathutils import Vector, noise
import random

class BiomeGeometryGenerator:
    """
    Generates geometry node groups for O'Neill cylinder biomes in Python.
    Designed to integrate with Phase 1 terrain painting system.
    """
    
    def __init__(self):
        self.biome_types = [
            'archipelago',
            'mountain', 
            'canyon',
            'rolling_hills',
            'desert',
            'ocean'
        ]
        self.generated_node_groups = {}
        
    def create_biome_node_group(self, biome_name):
        """Create a geometry node group for specified biome"""
        
        if biome_name not in self.biome_types:
            raise ValueError(f"Biome '{biome_name}' not supported. Available: {self.biome_types}")
            
        node_group_name = f"ONeill_Biome_{biome_name.title()}"
        
        # Check if already exists
        if node_group_name in bpy.data.node_groups:
            print(f"Node group {node_group_name} already exists, using existing")
            return bpy.data.node_groups[node_group_name]
            
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create input and output nodes
        input_node = node_group.nodes.new('NodeGroupInput')
        output_node = node_group.nodes.new('NodeGroupOutput')
        
        input_node.location = (-400, 0)
        output_node.location = (400, 0)
        
        # Define standard inputs for all biomes
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='INPUT')
        node_group.interface.new_socket('Heightmap_Strength', socket_type='NodeSocketFloat', in_out='INPUT')
        node_group.interface.new_socket('Feature_Scale', socket_type='NodeSocketFloat', in_out='INPUT')
        node_group.interface.new_socket('Biome_Intensity', socket_type='NodeSocketFloat', in_out='INPUT')
        
        # Set default values
        heightmap_input = node_group.interface.items_tree['Heightmap_Strength']
        heightmap_input.default_value = 1.0
        heightmap_input.min_value = 0.0
        heightmap_input.max_value = 5.0
        
        scale_input = node_group.interface.items_tree['Feature_Scale']
        scale_input.default_value = 1.0
        scale_input.min_value = 0.1
        scale_input.max_value = 10.0
        
        intensity_input = node_group.interface.items_tree['Biome_Intensity']
        intensity_input.default_value = 1.0
        intensity_input.min_value = 0.0
        intensity_input.max_value = 2.0
        
        # Define output
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='OUTPUT')
        
        # Now create biome-specific node network
        if biome_name == 'mountain':
            self._create_mountain_nodes(node_group, input_node, output_node)
        elif biome_name == 'archipelago':
            self._create_archipelago_nodes(node_group, input_node, output_node)
        elif biome_name == 'canyon':
            self._create_canyon_nodes(node_group, input_node, output_node)
        elif biome_name == 'rolling_hills':
            self._create_rolling_hills_nodes(node_group, input_node, output_node)
        elif biome_name == 'desert':
            self._create_desert_nodes(node_group, input_node, output_node)
        elif biome_name == 'ocean':
            self._create_ocean_nodes(node_group, input_node, output_node)
            
        self.generated_node_groups[biome_name] = node_group
        print(f"Created biome node group: {node_group_name}")
        return node_group
    
    def _create_mountain_nodes(self, node_group, input_node, output_node):
        """Create mountain terrain with dramatic peaks and elevation gradients"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node - get vertex positions
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Noise texture for mountain features
        noise = nodes.new('ShaderNodeTexNoise')
        noise.location = (-200, 300)
        noise.inputs['Scale'].default_value = 3.0
        noise.inputs['Detail'].default_value = 8.0
        noise.inputs['Roughness'].default_value = 0.7
        
        # Secondary noise for fine details  
        noise2 = nodes.new('ShaderNodeTexNoise')
        noise2.location = (-200, 100)
        noise2.inputs['Scale'].default_value = 15.0
        noise2.inputs['Detail'].default_value = 4.0
        noise2.inputs['Roughness'].default_value = 0.5
        
        # Combine noise layers
        mix = nodes.new('ShaderNodeMix')
        mix.location = (-100, 200)
        mix.data_type = 'RGBA'
        mix.blend_type = 'ADD'
        mix.inputs['Fac'].default_value = 0.3
        
        # Separate XYZ to get height gradient
        separate = nodes.new('ShaderNodeSeparateXYZ')
        separate.location = (-200, 0)
        
        # Math node for elevation gradient (X-axis based)
        gradient = nodes.new('ShaderNodeMath')
        gradient.location = (-100, 0)
        gradient.operation = 'MULTIPLY'
        gradient.inputs[1].default_value = 0.5  # Gradient strength
        
        # Combine gradient with noise
        combine_height = nodes.new('ShaderNodeMath')
        combine_height.location = (0, 100)
        combine_height.operation = 'ADD'
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node to displace geometry
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector math to apply Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], noise.inputs['Vector'])
        links.new(position.outputs['Position'], noise2.inputs['Vector'])
        links.new(noise.outputs['Color'], mix.inputs['Color1'])
        links.new(noise2.outputs['Color'], mix.inputs['Color2'])
        
        links.new(position.outputs['Position'], separate.inputs['Vector'])
        links.new(separate.outputs['X'], gradient.inputs[0])
        
        links.new(mix.outputs['Color'], combine_height.inputs[0])
        links.new(gradient.outputs['Value'], combine_height.inputs[1])
        
        links.new(combine_height.outputs['Value'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def _create_archipelago_nodes(self, node_group, input_node, output_node):
        """Create archipelago terrain with island chains and water features"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Large scale noise for island shapes
        island_noise = nodes.new('ShaderNodeTexNoise')
        island_noise.location = (-200, 300)
        island_noise.inputs['Scale'].default_value = 1.5
        island_noise.inputs['Detail'].default_value = 3.0
        island_noise.inputs['Roughness'].default_value = 0.6
        
        # Medium scale for coastal variation
        coastal_noise = nodes.new('ShaderNodeTexNoise')
        coastal_noise.location = (-200, 150)
        coastal_noise.inputs['Scale'].default_value = 8.0
        coastal_noise.inputs['Detail'].default_value = 6.0
        coastal_noise.inputs['Roughness'].default_value = 0.5
        
        # Fine detail for surface texture
        detail_noise = nodes.new('ShaderNodeTexNoise')
        detail_noise.location = (-200, 0)
        detail_noise.inputs['Scale'].default_value = 25.0
        detail_noise.inputs['Detail'].default_value = 2.0
        detail_noise.inputs['Roughness'].default_value = 0.4
        
        # Combine island shape with coastal variation
        mix1 = nodes.new('ShaderNodeMix')
        mix1.location = (-100, 250)
        mix1.data_type = 'RGBA'
        mix1.blend_type = 'MIX'
        mix1.inputs['Fac'].default_value = 0.4
        
        # Add fine detail
        mix2 = nodes.new('ShaderNodeMix')
        mix2.location = (-50, 150)
        mix2.data_type = 'RGBA'
        mix2.blend_type = 'ADD'
        mix2.inputs['Fac'].default_value = 0.2
        
        # ColorRamp for island definition (creates water level)
        color_ramp = nodes.new('ShaderNodeValToRGB')
        color_ramp.location = (0, 100)
        color_ramp.color_ramp.elements[0].position = 0.4  # Water level
        color_ramp.color_ramp.elements[1].position = 0.6  # Land level
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector combine for Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], island_noise.inputs['Vector'])
        links.new(position.outputs['Position'], coastal_noise.inputs['Vector'])
        links.new(position.outputs['Position'], detail_noise.inputs['Vector'])
        
        links.new(island_noise.outputs['Color'], mix1.inputs['Color1'])
        links.new(coastal_noise.outputs['Color'], mix1.inputs['Color2'])
        links.new(mix1.outputs['Color'], mix2.inputs['Color1'])
        links.new(detail_noise.outputs['Color'], mix2.inputs['Color2'])
        
        links.new(mix2.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def _create_canyon_nodes(self, node_group, input_node, output_node):
        """Create canyon terrain with Big Bend-style rolling mesas and valleys"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Large scale noise for mesa formations
        mesa_noise = nodes.new('ShaderNodeTexNoise')
        mesa_noise.location = (-200, 300)
        mesa_noise.inputs['Scale'].default_value = 2.0
        mesa_noise.inputs['Detail'].default_value = 4.0
        mesa_noise.inputs['Roughness'].default_value = 0.8
        
        # Medium scale for canyon cutting
        canyon_noise = nodes.new('ShaderNodeTexNoise')
        canyon_noise.location = (-200, 150)
        canyon_noise.inputs['Scale'].default_value = 6.0
        canyon_noise.inputs['Detail'].default_value = 8.0
        canyon_noise.inputs['Roughness'].default_value = 0.6
        
        # Fine erosion detail
        erosion_noise = nodes.new('ShaderNodeTexNoise')
        erosion_noise.location = (-200, 0)
        erosion_noise.inputs['Scale'].default_value = 20.0
        erosion_noise.inputs['Detail'].default_value = 3.0
        erosion_noise.inputs['Roughness'].default_value = 0.4
        
        # ColorRamp for mesa flatness
        mesa_ramp = nodes.new('ShaderNodeValToRGB')
        mesa_ramp.location = (-100, 300)
        mesa_ramp.color_ramp.elements[0].position = 0.3
        mesa_ramp.color_ramp.elements[1].position = 0.7
        
        # ColorRamp for canyon depth
        canyon_ramp = nodes.new('ShaderNodeValToRGB')
        canyon_ramp.location = (-100, 150)
        canyon_ramp.color_ramp.elements[0].position = 0.2
        canyon_ramp.color_ramp.elements[1].position = 0.8
        
        # Subtract canyons from mesas
        subtract = nodes.new('ShaderNodeMath')
        subtract.location = (0, 200)
        subtract.operation = 'SUBTRACT'
        
        # Add fine erosion
        add_erosion = nodes.new('ShaderNodeMix')
        add_erosion.location = (50, 150)
        add_erosion.data_type = 'RGBA'
        add_erosion.blend_type = 'ADD'
        add_erosion.inputs['Fac'].default_value = 0.15
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector combine for Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], mesa_noise.inputs['Vector'])
        links.new(position.outputs['Position'], canyon_noise.inputs['Vector'])
        links.new(position.outputs['Position'], erosion_noise.inputs['Vector'])
        
        links.new(mesa_noise.outputs['Color'], mesa_ramp.inputs['Fac'])
        links.new(canyon_noise.outputs['Color'], canyon_ramp.inputs['Fac'])
        
        links.new(mesa_ramp.outputs['Color'], subtract.inputs[0])
        links.new(canyon_ramp.outputs['Color'], subtract.inputs[1])
        
        links.new(subtract.outputs['Value'], add_erosion.inputs['Color1'])
        links.new(erosion_noise.outputs['Color'], add_erosion.inputs['Color2'])
        
        links.new(add_erosion.outputs['Color'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def _create_rolling_hills_nodes(self, node_group, input_node, output_node):
        """Create gentle rolling hills terrain for comfortable exploration"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Large scale gentle undulation
        hills_noise = nodes.new('ShaderNodeTexNoise')
        hills_noise.location = (-200, 300)
        hills_noise.inputs['Scale'].default_value = 1.0
        hills_noise.inputs['Detail'].default_value = 2.0
        hills_noise.inputs['Roughness'].default_value = 0.3
        
        # Medium scale for hill variation
        variation_noise = nodes.new('ShaderNodeTexNoise')
        variation_noise.location = (-200, 150)
        variation_noise.inputs['Scale'].default_value = 4.0
        variation_noise.inputs['Detail'].default_value = 4.0
        variation_noise.inputs['Roughness'].default_value = 0.4
        
        # Fine grass-like texture
        grass_noise = nodes.new('ShaderNodeTexNoise')
        grass_noise.location = (-200, 0)
        grass_noise.inputs['Scale'].default_value = 30.0
        grass_noise.inputs['Detail'].default_value = 1.0
        grass_noise.inputs['Roughness'].default_value = 0.2
        
        # Smooth the hills with ColorRamp
        smooth_ramp = nodes.new('ShaderNodeValToRGB')
        smooth_ramp.location = (-100, 300)
        smooth_ramp.color_ramp.interpolation = 'EASE'
        smooth_ramp.color_ramp.elements[0].position = 0.2
        smooth_ramp.color_ramp.elements[1].position = 0.8
        
        # Add variation gently
        add_variation = nodes.new('ShaderNodeMix')
        add_variation.location = (-50, 200)
        add_variation.data_type = 'RGBA'
        add_variation.blend_type = 'ADD'
        add_variation.inputs['Fac'].default_value = 0.3
        
        # Add fine grass texture
        add_grass = nodes.new('ShaderNodeMix')
        add_grass.location = (0, 150)
        add_grass.data_type = 'RGBA'
        add_grass.blend_type = 'ADD'
        add_grass.inputs['Fac'].default_value = 0.05
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector combine for Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], hills_noise.inputs['Vector'])
        links.new(position.outputs['Position'], variation_noise.inputs['Vector'])
        links.new(position.outputs['Position'], grass_noise.inputs['Vector'])
        
        links.new(hills_noise.outputs['Color'], smooth_ramp.inputs['Fac'])
        links.new(smooth_ramp.outputs['Color'], add_variation.inputs['Color1'])
        links.new(variation_noise.outputs['Color'], add_variation.inputs['Color2'])
        
        links.new(add_variation.outputs['Color'], add_grass.inputs['Color1'])
        links.new(grass_noise.outputs['Color'], add_grass.inputs['Color2'])
        
        links.new(add_grass.outputs['Color'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def _create_desert_nodes(self, node_group, input_node, output_node):
        """Create desert terrain with dune formations and rocky outcrops"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Large scale dune formations
        dune_noise = nodes.new('ShaderNodeTexNoise')
        dune_noise.location = (-200, 300)
        dune_noise.inputs['Scale'].default_value = 1.2
        dune_noise.inputs['Detail'].default_value = 3.0
        dune_noise.inputs['Roughness'].default_value = 0.5
        
        # Medium scale for wind patterns
        wind_noise = nodes.new('ShaderNodeTexNoise')
        wind_noise.location = (-200, 150)
        wind_noise.inputs['Scale'].default_value = 5.0
        wind_noise.inputs['Detail'].default_value = 6.0
        wind_noise.inputs['Roughness'].default_value = 0.6
        
        # Rocky outcrops
        rock_noise = nodes.new('ShaderNodeTexNoise')
        rock_noise.location = (-200, 0)
        rock_noise.inputs['Scale'].default_value = 8.0
        rock_noise.inputs['Detail'].default_value = 8.0
        rock_noise.inputs['Roughness'].default_value = 0.9
        
        # Fine sand texture
        sand_noise = nodes.new('ShaderNodeTexNoise')
        sand_noise.location = (-200, -150)
        sand_noise.inputs['Scale'].default_value = 40.0
        sand_noise.inputs['Detail'].default_value = 1.0
        sand_noise.inputs['Roughness'].default_value = 0.3
        
        # Smooth dunes with ColorRamp
        dune_ramp = nodes.new('ShaderNodeValToRGB')
        dune_ramp.location = (-100, 300)
        dune_ramp.color_ramp.interpolation = 'EASE'
        
        # Sharp rocks with ColorRamp
        rock_ramp = nodes.new('ShaderNodeValToRGB')
        rock_ramp.location = (-100, 0)
        rock_ramp.color_ramp.elements[0].position = 0.6
        rock_ramp.color_ramp.elements[1].position = 0.8
        
        # Combine dunes and wind
        combine_dunes = nodes.new('ShaderNodeMix')
        combine_dunes.location = (-50, 250)
        combine_dunes.data_type = 'RGBA'
        combine_dunes.blend_type = 'ADD'
        combine_dunes.inputs['Fac'].default_value = 0.4
        
        # Add rocky outcrops
        add_rocks = nodes.new('ShaderNodeMix')
        add_rocks.location = (0, 150)
        add_rocks.data_type = 'RGBA'
        add_rocks.blend_type = 'LIGHTEN'
        add_rocks.inputs['Fac'].default_value = 0.7
        
        # Add fine sand texture
        add_sand = nodes.new('ShaderNodeMix')
        add_sand.location = (50, 100)
        add_sand.data_type = 'RGBA'
        add_sand.blend_type = 'ADD'
        add_sand.inputs['Fac'].default_value = 0.1
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector combine for Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], dune_noise.inputs['Vector'])
        links.new(position.outputs['Position'], wind_noise.inputs['Vector'])
        links.new(position.outputs['Position'], rock_noise.inputs['Vector'])
        links.new(position.outputs['Position'], sand_noise.inputs['Vector'])
        
        links.new(dune_noise.outputs['Color'], dune_ramp.inputs['Fac'])
        links.new(rock_noise.outputs['Color'], rock_ramp.inputs['Fac'])
        
        links.new(dune_ramp.outputs['Color'], combine_dunes.inputs['Color1'])
        links.new(wind_noise.outputs['Color'], combine_dunes.inputs['Color2'])
        
        links.new(combine_dunes.outputs['Color'], add_rocks.inputs['Color1'])
        links.new(rock_ramp.outputs['Color'], add_rocks.inputs['Color2'])
        
        links.new(add_rocks.outputs['Color'], add_sand.inputs['Color1'])
        links.new(sand_noise.outputs['Color'], add_sand.inputs['Color2'])
        
        links.new(add_sand.outputs['Color'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def _create_ocean_nodes(self, node_group, input_node, output_node):
        """Create ocean terrain with underwater ridges and depth variation"""
        nodes = node_group.nodes
        links = node_group.links
        
        # Position node
        position = nodes.new('GeometryNodeInputPosition')
        position.location = (-300, 200)
        
        # Large scale depth variation
        depth_noise = nodes.new('ShaderNodeTexNoise')
        depth_noise.location = (-200, 300)
        depth_noise.inputs['Scale'].default_value = 0.8
        depth_noise.inputs['Detail'].default_value = 2.0
        depth_noise.inputs['Roughness'].default_value = 0.4
        
        # Medium scale for ridges and trenches
        ridge_noise = nodes.new('ShaderNodeTexNoise')
        ridge_noise.location = (-200, 150)
        ridge_noise.inputs['Scale'].default_value = 3.0
        ridge_noise.inputs['Detail'].default_value = 6.0
        ridge_noise.inputs['Roughness'].default_value = 0.7
        
        # Fine underwater texture
        underwater_noise = nodes.new('ShaderNodeTexNoise')
        underwater_noise.location = (-200, 0)
        underwater_noise.inputs['Scale'].default_value = 15.0
        underwater_noise.inputs['Detail'].default_value = 4.0
        underwater_noise.inputs['Roughness'].default_value = 0.5
        
        # Invert depth (ocean goes down)
        invert_depth = nodes.new('ShaderNodeMath')
        invert_depth.location = (-100, 300)
        invert_depth.operation = 'SUBTRACT'
        invert_depth.inputs[0].default_value = 0.0
        
        # ColorRamp for ridge definition
        ridge_ramp = nodes.new('ShaderNodeValToRGB')
        ridge_ramp.location = (-100, 150)
        ridge_ramp.color_ramp.elements[0].position = 0.4
        ridge_ramp.color_ramp.elements[1].position = 0.6
        
        # Combine depth with ridges
        combine_depth = nodes.new('ShaderNodeMix')
        combine_depth.location = (-50, 200)
        combine_depth.data_type = 'RGBA'
        combine_depth.blend_type = 'ADD'
        combine_depth.inputs['Fac'].default_value = 0.5
        
        # Add underwater detail
        add_detail = nodes.new('ShaderNodeMix')
        add_detail.location = (0, 150)
        add_detail.data_type = 'RGBA'
        add_detail.blend_type = 'ADD'
        add_detail.inputs['Fac'].default_value = 0.2
        
        # Scale by heightmap strength
        strength_mult = nodes.new('ShaderNodeMath')
        strength_mult.location = (100, 100)
        strength_mult.operation = 'MULTIPLY'
        
        # Set position node
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (200, 0)
        
        # Vector combine for Z displacement
        vector_combine = nodes.new('ShaderNodeCombineXYZ')
        vector_combine.location = (100, -50)
        vector_combine.inputs['X'].default_value = 0.0
        vector_combine.inputs['Y'].default_value = 0.0
        
        # Connect the network
        links.new(position.outputs['Position'], depth_noise.inputs['Vector'])
        links.new(position.outputs['Position'], ridge_noise.inputs['Vector'])
        links.new(position.outputs['Position'], underwater_noise.inputs['Vector'])
        
        links.new(depth_noise.outputs['Color'], invert_depth.inputs[1])
        links.new(ridge_noise.outputs['Color'], ridge_ramp.inputs['Fac'])
        
        links.new(invert_depth.outputs['Value'], combine_depth.inputs['Color1'])
        links.new(ridge_ramp.outputs['Color'], combine_depth.inputs['Color2'])
        
        links.new(combine_depth.outputs['Color'], add_detail.inputs['Color1'])
        links.new(underwater_noise.outputs['Color'], add_detail.inputs['Color2'])
        
        links.new(add_detail.outputs['Color'], strength_mult.inputs[0])
        links.new(input_node.outputs['Heightmap_Strength'], strength_mult.inputs[1])
        
        links.new(strength_mult.outputs['Value'], vector_combine.inputs['Z'])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_combine.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])

    def create_all_biomes(self):
        """Create all 6 biome node groups at once"""
        print("Creating all biome node groups...")
        
        for biome_name in self.biome_types:
            try:
                self.create_biome_node_group(biome_name)
                print(f"✅ {biome_name.title()} biome created successfully")
            except Exception as e:
                print(f"❌ Error creating {biome_name} biome: {e}")
        
        print(f"\nCompleted! Created {len(self.generated_node_groups)} biome node groups.")
        return self.generated_node_groups

    def apply_biome_to_object(self, obj, biome_name, strength=1.0, scale=1.0, intensity=1.0):
        """Apply a biome to a specific object"""
        if biome_name not in self.biome_types:
            raise ValueError(f"Biome '{biome_name}' not supported")
        
        # Get or create the biome node group
        if biome_name not in self.generated_node_groups:
            self.create_biome_node_group(biome_name)
        
        node_group = self.generated_node_groups[biome_name]
        
        # Add geometry node modifier
        modifier_name = f"Biome_{biome_name.title()}"
        modifier = obj.modifiers.new(modifier_name, 'NODES')
        modifier.node_group = node_group
        
        # Set parameters
        modifier["Input_2"] = strength  # Heightmap_Strength
        modifier["Input_3"] = scale     # Feature_Scale
        modifier["Input_4"] = intensity # Biome_Intensity
        
        print(f"Applied {biome_name} biome to {obj.name}")
        return modifier

# Usage Example:
# generator = BiomeGeometryGenerator()
# generator.create_all_biomes()
# 
# # Apply to specific object
# obj = bpy.context.active_object
# generator.apply_biome_to_object(obj, 'mountain', strength=2.0)

# ========================= REGISTRATION FUNCTIONS =========================

# Add these classes for UI integration
from bpy.types import Operator, Panel

class ONEILL_OT_CreateAllBiomes(Operator):
    """Create all biome node groups"""
    bl_idname = "oneill.create_all_biomes"
    bl_label = "Create All Biomes"
    bl_description = "Create geometry node groups for all biome types"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        generator = BiomeGeometryGenerator()
        created_biomes = generator.create_all_biomes()
        
        self.report({'INFO'}, f"Created {len(created_biomes)} biome node groups")
        return {'FINISHED'}

class ONEILL_OT_ApplyBiomeToSelected(Operator):
    """Apply biome to selected objects"""
    bl_idname = "oneill.apply_biome_to_selected"
    bl_label = "Apply Biome"
    bl_description = "Apply selected biome to selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_type: bpy.props.StringProperty()
    strength: bpy.props.FloatProperty(default=1.0)
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        generator = BiomeGeometryGenerator()
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                try:
                    generator.apply_biome_to_object(obj, self.biome_type, self.strength)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to apply biome to {obj.name}: {e}")
        
        self.report({'INFO'}, f"Applied {self.biome_type} biome to {len(context.selected_objects)} objects")
        return {'FINISHED'}

# Registration classes list
classes = [
    ONEILL_OT_CreateAllBiomes,
    ONEILL_OT_ApplyBiomeToSelected,
]

def register():
    """Register biome geometry generator module"""
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
        print("✅ Biome geometry generator registered")
    except Exception as e:
        print(f"❌ Biome geometry generator registration failed: {e}")
        raise

def unregister():
    """Unregister biome geometry generator module"""
    try:
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        print("✅ Biome geometry generator unregistered")
    except Exception as e:
        print(f"⚠️ Biome geometry generator unregistration failed: {e}")

if __name__ == "__main__":
    register()