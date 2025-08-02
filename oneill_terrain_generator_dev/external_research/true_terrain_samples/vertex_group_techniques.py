noise_scale']
        noise_node.inputs['Detail'].default_value = config['detail_level']
        noise_node.inputs['Roughness'].default_value = config['roughness']
        
        # Connect position to noise
        from bpy.types import NodeLinks
        links = noise_node.id_data.links
        links.new(position_node.outputs['Position'], noise_node.inputs['Vector'])
        
        # Color Ramp for displacement shaping
        color_ramp = nodes.new('ShaderNodeValToRGB')
        color_ramp.location = (location[0] + 200, location[1])
        
        # Configure color ramp based on biome
        if biome_type == 'Mountains':
            # Sharp peaks
            color_ramp.color_ramp.elements[0].position = 0.3
            color_ramp.color_ramp.elements[1].position = 0.7
        elif biome_type == 'Ocean':
            # Smooth depressions
            color_ramp.color_ramp.elements[0].position = 0.2
            color_ramp.color_ramp.elements[1].position = 0.8
        elif biome_type == 'Canyons':
            # Deep cuts
            color_ramp.color_ramp.elements[0].position = 0.1
            color_ramp.color_ramp.elements[1].position = 0.9
        
        links.new(noise_node.outputs['Fac'], color_ramp.inputs['Fac'])
        
        # Vector Math for displacement direction
        vector_math = nodes.new('ShaderNodeVectorMath')
        vector_math.operation = 'MULTIPLY'
        vector_math.location = (location[0] + 400, location[1])
        
        # Set displacement vector (Z-up for terrain)
        displacement_vector = (0, 0, config['displacement_strength'])
        vector_math.inputs[1].default_value = displacement_vector
        
        links.new(color_ramp.outputs['Color'], vector_math.inputs[0])
        
        return vector_math


class SpatialCoordinateMapping:
    """Spatial coordinate mapping techniques from True Terrain"""
    
    @staticmethod
    def world_to_normalized_coordinate(world_pos, bounds_min, bounds_max):
        """
        Convert world position to normalized coordinate (0-1 range)
        Based on True Terrain's coordinate conversion approach
        """
        normalized = Vector()
        
        for i in range(3):  # X, Y, Z
            if bounds_max[i] != bounds_min[i]:
                normalized[i] = (world_pos[i] - bounds_min[i]) / (bounds_max[i] - bounds_min[i])
            else:
                normalized[i] = 0.5  # Fallback for zero-width bounds
        
        return normalized
    
    @staticmethod
    def calculate_object_bounds_array(objects):
        """
        Calculate combined bounds for array of objects
        Similar to True Terrain's spatial analysis
        """
        if not objects:
            return Vector((0, 0, 0)), Vector((1, 1, 1))
        
        # Initialize with first object bounds
        first_obj = objects[0]
        min_bounds = Vector(first_obj.bound_box[0])
        max_bounds = Vector(first_obj.bound_box[6])
        
        # Transform to world space
        min_bounds = first_obj.matrix_world @ min_bounds
        max_bounds = first_obj.matrix_world @ max_bounds
        
        # Expand bounds to include all objects
        for obj in objects[1:]:
            for corner in obj.bound_box:
                world_corner = obj.matrix_world @ Vector(corner)
                
                for i in range(3):
                    min_bounds[i] = min(min_bounds[i], world_corner[i])
                    max_bounds[i] = max(max_bounds[i], world_corner[i])
        
        return min_bounds, max_bounds


class AssetManagementSystem:
    """Asset discovery and management from True Terrain"""
    
    @staticmethod
    def discover_terrain_assets(base_path):
        """
        Discover available terrain assets
        Based on True Terrain's asset discovery system
        """
        assets = {}
        
        if not os.path.exists(base_path):
            return assets
        
        for file in os.listdir(base_path):
            if file.endswith('.blend'):
                asset_name = file[:-6]  # Remove .blend extension
                assets[asset_name] = os.path.join(base_path, file)
        
        return assets
    
    @staticmethod
    def import_node_group_from_asset(asset_path, node_group_name):
        """
        Import node group from asset file
        Based on True Terrain's asset import system
        """
        # Check if node group already exists
        if node_group_name in bpy.data.node_groups:
            return bpy.data.node_groups[node_group_name]
        
        # Import from asset file
        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
        
        return bpy.data.node_groups.get(node_group_name)
    
    @staticmethod
    def setup_terrain_with_asset(obj, asset_path, node_group_name):
        """
        Setup terrain using imported asset
        Complete workflow from True Terrain approach
        """
        # Import node group
        node_group = AssetManagementSystem.import_node_group_from_asset(
            asset_path, node_group_name
        )
        
        if not node_group:
            return False
        
        # Apply geometry nodes modifier
        GeometryNodesTerrainIntegration.apply_geometry_nodes_modifier(obj, node_group)
        
        return True


# Key integration insights for O'Neill Terrain Generator:

"""
INTEGRATION STRATEGY FOR O'NEILL PROJECT:

1. VERTEX GROUP TERRAIN SYSTEM:
   - Create vertex groups for each biome type
   - Assign vertices based on canvas sampling at UV coordinates
   - Use weight-based blending for smooth transitions

2. GEOMETRY NODES ARCHITECTURE:
   - Modular node groups for each biome displacement pattern
   - Named Attribute nodes to read vertex group weights
   - Weighted combination of multiple displacement patterns

3. SPATIAL COORDINATE MAPPING:
   - Convert flat object world positions to canvas UV coordinates
   - Use True Terrain's bounds calculation for accurate mapping
   - Normalize coordinates for consistent canvas sampling

4. ASSET MANAGEMENT:
   - Import proven terrain node groups from project assets
   - Fallback to procedural generation if assets unavailable
   - Consistent application across multiple objects

CRITICAL BREAKTHROUGH COMBINATION:
Paint System's UV sampling + True Terrain's vertex groups + Geometry nodes
= True vertex-level precision for O'Neill terrain generation

IMPLEMENTATION FLOW:
1. Sample canvas at vertex UV positions (Paint System technique)
2. Assign vertices to biome groups with weights (True Terrain technique)
3. Use geometry nodes to apply weighted displacement (Combined approach)
4. Result: Pixel-perfect terrain matching painted canvas patterns
"""


class ONeillVertexPrecisionIntegration:
    """
    Integration class combining Paint System and True Terrain techniques
    for O'Neill Terrain Generator vertex-level precision
    """
    
    def __init__(self):
        self.biome_types = ['Mountains', 'Ocean', 'Hills', 'Desert', 'Canyons', 'Archipelago']
        self.vertex_group_system = VertexGroupTerrainSystem()
        self.geometry_nodes_system = GeometryNodesTerrainIntegration()
    
    def apply_vertex_level_precision(self, obj, canvas_image, canvas_bounds):
        """
        Main integration function: Apply vertex-level precision to object
        
        Combines:
        - Paint System's UV sampling for canvas data
        - True Terrain's vertex groups for selective application
        - Geometry nodes for biome-specific displacement
        """
        # Step 1: Create vertex groups for biomes
        vertex_groups = self.vertex_group_system.create_terrain_vertex_groups(
            obj, self.biome_types
        )
        
        # Step 2: Assign vertices based on canvas sampling
        self._assign_vertices_from_canvas(obj, vertex_groups, canvas_image, canvas_bounds)
        
        # Step 3: Create and apply geometry nodes
        terrain_node_group = self.geometry_nodes_system.create_vertex_group_driven_displacement()
        modifier = self.geometry_nodes_system.apply_geometry_nodes_modifier(obj, terrain_node_group)
        
        return modifier
    
    def _assign_vertices_from_canvas(self, obj, vertex_groups, canvas_image, canvas_bounds):
        """
        Assign vertices to biome groups based on canvas sampling
        Core integration of Paint System UV sampling with True Terrain vertex groups
        """
        if obj.type != 'MESH':
            return
        
        mesh = obj.data
        
        # Ensure object mode for vertex group operations
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Clear existing assignments
        self.vertex_group_system.clear_vertex_group_assignments(obj, vertex_groups)
        
        # Sample canvas for each vertex
        for vertex_idx, vertex in enumerate(mesh.vertices):
            # Get world position
            world_pos = obj.matrix_world @ vertex.co
            
            # Convert to UV coordinate for canvas sampling
            uv_coord = self._world_to_canvas_uv(world_pos, canvas_bounds)
            
            # Sample canvas at UV position
            canvas_color = self._sample_canvas_at_uv(canvas_image, uv_coord)
            
            # Determine biome and weight from canvas data
            biome_type, weight = self._canvas_color_to_biome_weight(canvas_color)
            
            # Assign to vertex group
            if biome_type in vertex_groups and weight > 0.1:
                vertex_groups[biome_type].add([vertex_idx], weight, 'REPLACE')
    
    def _world_to_canvas_uv(self, world_pos, canvas_bounds):
        """Convert world position to canvas UV coordinate"""
        # Based on O'Neill flat object layout and canvas dimensions
        bounds_min, bounds_max = canvas_bounds
        
        u = (world_pos.x - bounds_min.x) / (bounds_max.x - bounds_min.x)
        v = (world_pos.y - bounds_min.y) / (bounds_max.y - bounds_min.y)
        
        # Clamp to 0-1 range
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        
        return (u, v)
    
    def _sample_canvas_at_uv(self, canvas_image, uv_coord):
        """Sample canvas color at UV coordinate"""
        if not canvas_image or not canvas_image.pixels:
            return (0.5, 0.5, 0.5, 1.0)  # Default gray
        
        u, v = uv_coord
        width, height = canvas_image.size
        
        # Convert UV to pixel coordinates
        pixel_x = int(u * (width - 1))
        pixel_y = int(v * (height - 1))
        
        # Sample pixel (RGBA)
        pixel_index = (pixel_y * width + pixel_x) * 4
        
        if pixel_index + 3 < len(canvas_image.pixels):
            r = canvas_image.pixels[pixel_index]
            g = canvas_image.pixels[pixel_index + 1]
            b = canvas_image.pixels[pixel_index + 2]
            a = canvas_image.pixels[pixel_index + 3]
            return (r, g, b, a)
        
        return (0.5, 0.5, 0.5, 1.0)  # Fallback
    
    def _canvas_color_to_biome_weight(self, canvas_color):
        """Convert canvas color to biome type and weight"""
        r, g, b, a = canvas_color
        
        # Color-to-biome mapping (based on O'Neill project color scheme)
        biome_colors = {
            'Mountains': (0.5, 0.5, 0.5),    # Gray
            'Ocean': (0.0, 0.0, 1.0),        # Blue
            'Hills': (0.0, 1.0, 0.0),        # Green
            'Desert': (1.0, 1.0, 0.0),       # Yellow
            'Canyons': (1.0, 0.5, 0.0),      # Orange
            'Archipelago': (0.0, 1.0, 1.0)   # Cyan
        }
        
        # Find closest biome color
        best_biome = 'Mountains'  # Default
        min_distance = float('inf')
        
        for biome, biome_rgb in biome_colors.items():
            distance = sum((c1 - c2) ** 2 for c1, c2 in zip((r, g, b), biome_rgb))
            if distance < min_distance:
                min_distance = distance
                best_biome = biome
        
        # Weight based on alpha and distance
        weight = a * (1.0 - min(1.0, min_distance))
        
        return best_biome, weight


# Export key classes for use in main O'Neill system
__all__ = [
    'VertexGroupTerrainSystem',
    'GeometryNodesTerrainIntegration', 
    'TerrainDisplacementPatterns',
    'SpatialCoordinateMapping',
    'AssetManagementSystem',
    'ONeillVertexPrecisionIntegration'
]
