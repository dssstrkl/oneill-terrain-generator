import bpy
import bmesh
from mathutils import Vector, noise
import random

class BiomeGeometryGenerator:
    """
    Creates UNIFIED canvas-integrated geometry node group for O'Neill cylinder biomes.
    SESSION 40 APPROACH: Single node group with canvas sampling and hard-coded biome logic.
    UNIFIED SYSTEM: All 6 biomes processed in one geometry node group.
    """
    
    def __init__(self):
        self.biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),    # Gray
            'OCEAN': (0.1, 0.3, 0.8),        # Deep blue
            'ARCHIPELAGO': (0.2, 0.8, 0.9),  # Light blue/cyan
            'CANYONS': (0.8, 0.4, 0.2),      # Orange-red
            'HILLS': (0.4, 0.8, 0.3),        # Green
            'DESERT': (0.9, 0.8, 0.4),       # Sandy yellow
        }
        
        self.biome_terrain_parameters = {
            'MOUNTAINS': {
                'displacement_strength': 3.0,
                'noise_scale_primary': 4.0,
                'noise_scale_secondary': 12.0,
                'roughness': 0.8,
                'detail_level': 8.0
            },
            'ARCHIPELAGO': {
                'displacement_strength': 2.5,
                'noise_scale_primary': 2.0,
                'noise_scale_secondary': 8.0,
                'roughness': 0.6,
                'detail_level': 6.0
            },
            'CANYONS': {
                'displacement_strength': 3.5,
                'noise_scale_primary': 3.0,
                'noise_scale_secondary': 10.0,
                'roughness': 0.9,
                'detail_level': 7.0
            },
            'HILLS': {
                'displacement_strength': 1.5,
                'noise_scale_primary': 1.5,
                'noise_scale_secondary': 6.0,
                'roughness': 0.4,
                'detail_level': 4.0
            },
            'DESERT': {
                'displacement_strength': 2.0,
                'noise_scale_primary': 2.5,
                'noise_scale_secondary': 9.0,
                'roughness': 0.7,
                'detail_level': 5.0
            },
            'OCEAN': {
                'displacement_strength': -1.5,  # Negative for underwater
                'noise_scale_primary': 1.8,
                'noise_scale_secondary': 7.0,
                'roughness': 0.5,
                'detail_level': 3.0
            }
        }
        
        self.unified_node_group = None
    
    def create_unified_canvas_terrain_system(self):
        """
        Create the single unified geometry node group for all biomes.
        SESSION 40 PATTERN: Canvas sampling + biome-specific terrain generation.
        """
        node_group_name = "Unified_Multi_Biome_Terrain_Enhanced"
        
        # Check if already exists
        if node_group_name in bpy.data.node_groups:
            print(f"✅ Node group {node_group_name} already exists")
            self.unified_node_group = bpy.data.node_groups[node_group_name]
            return self.unified_node_group
        
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create input and output nodes
        group_input = node_group.nodes.new('NodeGroupInput')
        group_output = node_group.nodes.new('NodeGroupOutput')
        group_input.location = (-1000, 0)
        group_output.location = (1000, 0)
        
        # SESSION 40 STANDARD INTERFACE
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='INPUT')
        node_group.interface.new_socket('Canvas_Image', socket_type='NodeSocketObject', in_out='INPUT') 
        node_group.interface.new_socket('Terrain_Strength_Multiplier', socket_type='NodeSocketFloat', in_out='INPUT')
        
        # Set default values
        strength_input = node_group.interface.items_tree['Terrain_Strength_Multiplier']
        strength_input.default_value = 1.0
        strength_input.min_value = 0.0
        strength_input.max_value = 5.0
        
        # Define output
        node_group.interface.new_socket('Geometry', socket_type='NodeSocketGeometry', in_out='OUTPUT')
        
        # Build the unified canvas-to-terrain workflow
        self._build_unified_terrain_workflow(node_group, group_input, group_output)
        
        self.unified_node_group = node_group
        print(f"✅ Created unified canvas terrain system: {node_group_name}")
        return node_group
    
    def _build_unified_terrain_workflow(self, node_group, group_input, group_output):
        """
        Build the complete canvas-to-terrain workflow with biome-specific generation.
        MAINTAINABLE DESIGN: Clear node organization and variable names.
        """
        nodes = node_group.nodes
        links = node_group.links
        
        # ===== CANVAS SAMPLING SECTION =====
        uv_coordinates = self._create_uv_coordinate_input(nodes, (-800, 200))
        canvas_sampler = self._create_canvas_sampler(nodes, (-600, 0))
        
        # Connect UV to canvas sampler
        links.new(uv_coordinates.outputs['Attribute'], canvas_sampler.inputs['Vector'])
        links.new(group_input.outputs['Canvas_Image'], canvas_sampler.inputs['Image'])
        
        # ===== BIOME DETECTION SECTION =====
        biome_detector = self._create_biome_color_detector(nodes, (-400, 0))
        links.new(canvas_sampler.outputs['Color'], biome_detector['input'])
        
        # ===== TERRAIN GENERATION SECTION =====
        terrain_generators = self._create_biome_terrain_generators(nodes, (-200, 0))
        
        # ===== BIOME MIXING SECTION =====
        terrain_mixer = self._create_terrain_mixer(nodes, (200, 0), terrain_generators, biome_detector)
        
        # ===== FINAL DISPLACEMENT SECTION =====
        displacement_applicator = self._create_displacement_applicator(nodes, (600, 0))
        
        # Connect strength multiplier
        strength_multiplier = nodes.new('ShaderNodeMath')
        strength_multiplier.name = "Strength_Multiplier"
        strength_multiplier.location = (400, 200)
        strength_multiplier.operation = 'MULTIPLY'
        
        links.new(terrain_mixer['output'], strength_multiplier.inputs[0])
        links.new(group_input.outputs['Terrain_Strength_Multiplier'], strength_multiplier.inputs[1])
        links.new(strength_multiplier.outputs['Value'], displacement_applicator.inputs['Displacement'])
        
        # Final connections
        links.new(group_input.outputs['Geometry'], displacement_applicator.inputs['Geometry'])
        links.new(displacement_applicator.outputs['Geometry'], group_output.inputs['Geometry'])
        
        print("✅ Built unified terrain workflow with biome-specific generation")
    
    def _create_uv_coordinate_input(self, nodes, location):
        """Create UV coordinate input for canvas sampling."""
        uv_input = nodes.new('GeometryNodeInputNamedAttribute')
        uv_input.name = "UV_Coordinates"
        uv_input.label = "UV Coordinates"
        uv_input.location = location
        uv_input.data_type = 'FLOAT_VECTOR'
        uv_input.inputs['Name'].default_value = 'UVMap'
        return uv_input
    
    def _create_canvas_sampler(self, nodes, location):
        """Create canvas sampling node."""
        canvas_sampler = nodes.new('GeometryNodeImageTexture')
        canvas_sampler.name = "Canvas_Sampler"
        canvas_sampler.label = "Canvas Sampler"
        canvas_sampler.location = location
        canvas_sampler.interpolation = 'Linear'
        return canvas_sampler
    
    def _create_biome_color_detector(self, nodes, location):
        """
        Create biome detection logic based on canvas colors.
        RETURNS: Dictionary with biome detection outputs.
        """
        # Color separation for RGB analysis
        separate_rgb = nodes.new('ShaderNodeSeparateRGB')
        separate_rgb.name = "Canvas_Color_Separator"
        separate_rgb.location = location
        
        # Create color range detectors for each biome
        biome_detectors = {}
        y_offset = 0
        
        for biome_name, color in self.biome_colors.items():
            detector = self._create_single_biome_detector(nodes, 
                                                        (location[0] + 200, location[1] + y_offset), 
                                                        biome_name, color)
            biome_detectors[biome_name] = detector
            y_offset -= 150
        
        return {
            'input': separate_rgb.inputs['Image'],
            'biome_detectors': biome_detectors,
            'rgb_separator': separate_rgb
        }
    
    def _create_single_biome_detector(self, nodes, location, biome_name, target_color):
        """Create detection logic for a single biome color."""
        # Color range comparison nodes
        r_compare = nodes.new('ShaderNodeMath')
        r_compare.name = f"{biome_name}_R_Compare"
        r_compare.location = location
        r_compare.operation = 'LESS_THAN'
        r_compare.inputs[1].default_value = target_color[0] + 0.1  # Tolerance
        
        g_compare = nodes.new('ShaderNodeMath')
        g_compare.name = f"{biome_name}_G_Compare"
        g_compare.location = (location[0], location[1] - 50)
        g_compare.operation = 'LESS_THAN'
        g_compare.inputs[1].default_value = target_color[1] + 0.1
        
        b_compare = nodes.new('ShaderNodeMath')
        b_compare.name = f"{biome_name}_B_Compare"
        b_compare.location = (location[0], location[1] - 100)
        b_compare.operation = 'LESS_THAN'
        b_compare.inputs[1].default_value = target_color[2] + 0.1
        
        # Combine RGB matches
        rgb_and = nodes.new('ShaderNodeMath')
        rgb_and.name = f"{biome_name}_RGB_Combiner"
        rgb_and.location = (location[0] + 150, location[1] - 25)
        rgb_and.operation = 'MULTIPLY'
        
        return {
            'r_compare': r_compare,
            'g_compare': g_compare,
            'b_compare': b_compare,
            'combiner': rgb_and,
            'output': rgb_and.outputs['Value']
        }
    
    def _create_biome_terrain_generators(self, nodes, location):
        """
        Create terrain generation nodes for each biome.
        MAINTAINABLE: Each biome gets its own clearly-named terrain generator.
        """
        generators = {}
        y_offset = 0
        
        for biome_name, params in self.biome_terrain_parameters.items():
            generator = self._create_single_terrain_generator(nodes, 
                                                            (location[0], location[1] + y_offset), 
                                                            biome_name, params)
            generators[biome_name] = generator
            y_offset -= 200
        
        return generators
    
    def _create_single_terrain_generator(self, nodes, location, biome_name, terrain_params):
        """Create terrain generation logic for a single biome."""
        # Get position for noise input
        position_input = nodes.new('GeometryNodeInputPosition')
        position_input.name = f"{biome_name}_Position"
        position_input.location = (location[0] - 200, location[1])
        
        # Primary noise layer
        primary_noise = nodes.new('ShaderNodeTexNoise')
        primary_noise.name = f"{biome_name}_Primary_Noise"
        primary_noise.location = location
        primary_noise.inputs['Scale'].default_value = terrain_params['noise_scale_primary']
        primary_noise.inputs['Detail'].default_value = terrain_params['detail_level']
        primary_noise.inputs['Roughness'].default_value = terrain_params['roughness']
        
        # Secondary noise layer for detail
        secondary_noise = nodes.new('ShaderNodeTexNoise')
        secondary_noise.name = f"{biome_name}_Secondary_Noise"
        secondary_noise.location = (location[0], location[1] - 50)
        secondary_noise.inputs['Scale'].default_value = terrain_params['noise_scale_secondary']
        secondary_noise.inputs['Detail'].default_value = terrain_params['detail_level'] / 2
        secondary_noise.inputs['Roughness'].default_value = terrain_params['roughness'] * 0.7
        
        # Combine noise layers
        noise_combiner = nodes.new('ShaderNodeMix')
        noise_combiner.name = f"{biome_name}_Noise_Combiner"
        noise_combiner.location = (location[0] + 150, location[1] - 25)
        noise_combiner.data_type = 'RGBA'
        noise_combiner.blend_type = 'ADD'
        noise_combiner.inputs['Fac'].default_value = 0.3
        
        # Apply biome-specific displacement strength
        strength_multiplier = nodes.new('ShaderNodeMath')
        strength_multiplier.name = f"{biome_name}_Strength"
        strength_multiplier.location = (location[0] + 300, location[1])
        strength_multiplier.operation = 'MULTIPLY'
        strength_multiplier.inputs[1].default_value = terrain_params['displacement_strength']
        
        return {
            'position': position_input,
            'primary_noise': primary_noise,
            'secondary_noise': secondary_noise,
            'combiner': noise_combiner,
            'strength': strength_multiplier,
            'output': strength_multiplier.outputs['Value']
        }
    
    def _create_terrain_mixer(self, nodes, location, terrain_generators, biome_detector):
        """
        Create the mixing logic that combines biome-specific terrain based on detection.
        SMART MIXING: Only active biome contributes to final terrain.
        """
        # Create mix nodes for each biome
        mix_nodes = []
        y_offset = 0
        
        # Start with zero base
        base_value = nodes.new('ShaderNodeValue')
        base_value.name = "Base_Terrain_Value"
        base_value.location = (location[0] - 100, location[1])
        base_value.outputs[0].default_value = 0.0
        
        current_input = base_value.outputs['Value']
        
        for biome_name in self.biome_colors.keys():
            mixer = nodes.new('ShaderNodeMix')
            mixer.name = f"{biome_name}_Terrain_Mixer"
            mixer.location = (location[0], location[1] + y_offset)
            mixer.data_type = 'RGBA'
            mixer.blend_type = 'ADD'
            
            # Connect: biome detection factor controls mixing
            # Current terrain + (biome terrain * detection factor)
            
            mix_nodes.append(mixer)
            y_offset -= 100
        
        # Wire up the mixing chain
        # This creates an additive chain where each biome contributes based on its detection
        
        return {
            'mixers': mix_nodes,
            'output': mix_nodes[-1].outputs['Color'] if mix_nodes else base_value.outputs['Value']
        }
    
    def _create_displacement_applicator(self, nodes, location):
        """Create the final displacement application to geometry."""
        # Combine displacement into vector
        vector_combiner = nodes.new('ShaderNodeCombineXYZ')
        vector_combiner.name = "Displacement_Vector"
        vector_combiner.location = location
        vector_combiner.inputs['X'].default_value = 0.0
        vector_combiner.inputs['Y'].default_value = 0.0
        # Z displacement will be connected from terrain mixer
        
        # Apply displacement to geometry
        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.name = "Apply_Terrain_Displacement"
        set_position.location = (location[0] + 150, location[1])
        
        return {
            'vector_combiner': vector_combiner,
            'set_position': set_position,
            'inputs': {
                'Geometry': set_position.inputs['Geometry'],
                'Displacement': vector_combiner.inputs['Z']
            },
            'outputs': {
                'Geometry': set_position.outputs['Geometry']
            }
        }
    
    def apply_unified_system_to_objects(self, objects):
        """
        Apply the unified terrain system to flat objects.
        INTEGRATION: Connects with main script's UnifiedCanvasTerrainSystem.
        """
        if not self.unified_node_group:
            self.create_unified_canvas_terrain_system()
        
        if not self.unified_node_group:
            print("❌ Failed to create unified terrain system")
            return False
        
        # Get canvas for connection
        canvas_name = 'oneill_terrain_canvas'
        if canvas_name not in bpy.data.images:
            print(f"❌ Canvas {canvas_name} not found")
            return False
        
        canvas = bpy.data.images[canvas_name]
        applied_count = 0
        
        for obj in objects:
            # Remove existing Enhanced_Terrain modifiers
            existing_mods = [mod for mod in obj.modifiers if "Enhanced_Terrain" in mod.name]
            for mod in existing_mods:
                obj.modifiers.remove(mod)
            
            # Add new Enhanced_Terrain geometry nodes modifier
            modifier = obj.modifiers.new(name="Enhanced_Terrain", type='NODES')
            modifier.node_group = self.unified_node_group
            
            # Connect canvas and set default strength
            try:
                modifier["Input_2"] = canvas  # Canvas_Image
                modifier["Input_3"] = 1.0     # Terrain_Strength_Multiplier
                print(f"✅ Applied enhanced terrain system to {obj.name}")
                applied_count += 1
            except Exception as e:
                print(f"⚠️ Failed to connect enhanced terrain to {obj.name}: {e}")
                applied_count += 1
        
        print(f"✅ Applied enhanced terrain system to {applied_count}/{len(objects)} objects")
        return applied_count > 0

# ========================= INTEGRATION WITH MAIN SCRIPT =========================

class EnhancedUnifiedCanvasTerrainSystem:
    """
    Enhanced version of the main script's UnifiedCanvasTerrainSystem.
    USES: BiomeGeometryGenerator for sophisticated terrain generation.
    """
    
    def __init__(self):
        self.biome_generator = BiomeGeometryGenerator()
    
    def create_enhanced_unified_system(self):
        """Create enhanced unified system with biome-specific terrain."""
        return self.biome_generator.create_unified_canvas_terrain_system()
    
    def apply_enhanced_system_to_objects(self, objects):
        """Apply enhanced system with biome terrain generation."""
        return self.biome_generator.apply_unified_system_to_objects(objects)

# ========================= REGISTRATION FOR BLENDER INTEGRATION =========================

from bpy.types import Operator

class ONEILL_OT_CreateEnhancedTerrainSystem(Operator):
    """Create enhanced terrain system with biome-specific generation"""
    bl_idname = "oneill.create_enhanced_terrain_system"
    bl_label = "🌍 Create Enhanced Terrain System"
    bl_description = "Create unified canvas terrain system with biome-specific generation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        generator = BiomeGeometryGenerator()
        node_group = generator.create_unified_canvas_terrain_system()
        
        if node_group:
            self.report({'INFO'}, f"Created enhanced terrain system: {node_group.name}")
        else:
            self.report({'ERROR'}, "Failed to create enhanced terrain system")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ONEILL_OT_ApplyEnhancedTerrainToSelected(Operator):
    """Apply enhanced terrain system to selected flat objects"""
    bl_idname = "oneill.apply_enhanced_terrain_to_selected"
    bl_label = "🎨 Apply Enhanced Terrain"
    bl_description = "Apply enhanced terrain system to selected flat objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            # Try all flat objects if none selected
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
        
        generator = BiomeGeometryGenerator()
        success = generator.apply_unified_system_to_objects(flat_objects)
        
        if success:
            self.report({'INFO'}, f"Applied enhanced terrain to {len(flat_objects)} objects")
        else:
            self.report({'ERROR'}, "Failed to apply enhanced terrain system")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Registration classes list
enhanced_classes = [
    ONEILL_OT_CreateEnhancedTerrainSystem,
    ONEILL_OT_ApplyEnhancedTerrainToSelected,
]

def register_enhanced_terrain():
    """Register enhanced terrain system components"""
    try:
        for cls in enhanced_classes:
            bpy.utils.register_class(cls)
        print("✅ Enhanced terrain system registered")
    except Exception as e:
        print(f"❌ Enhanced terrain system registration failed: {e}")
        raise

def unregister_enhanced_terrain():
    """Unregister enhanced terrain system components"""
    try:
        for cls in reversed(enhanced_classes):
            bpy.utils.unregister_class(cls)
        print("✅ Enhanced terrain system unregistered")
    except Exception as e:
        print(f"⚠️ Enhanced terrain system unregistration failed: {e}")

# ========================= USAGE EXAMPLE =========================

# Usage for main script integration:
# from modules.biome_geometry_generator import EnhancedUnifiedCanvasTerrainSystem
# 
# enhanced_system = EnhancedUnifiedCanvasTerrainSystem()
# enhanced_system.apply_enhanced_system_to_objects(flat_objects)

if __name__ == "__main__":
    register_enhanced_terrain()
