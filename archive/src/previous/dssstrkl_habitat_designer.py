bl_info = {
    "name": "Dssstrkl Habitat Designer",
    "author": "Your Name", 
    "version": (2, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Dssstrkl",
    "description": "Design O'Neill cylinder habitats for the Dssstrkl space ark with Atlantean technology",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector, noise
import math
import random
import time
from bpy.props import *
from bpy.types import Panel, Operator, PropertyGroup

# ===== CORE DATA STRUCTURES =====

class CivilizationLayer:
    """Represents different layers of civilization development"""
    ATLANTEAN_BASE = "atlantean"
    DSSSTRKL_ADAPTATION = "dssstrkl" 
    SYSTEM_DECAY = "decay"
    CULT_INFILTRATION = "cult"
    EMERGENCY_REPAIRS = "repairs"

class BiomeType:
    """Different biome types for the habitat"""
    CENTRAL_SEA = "central_sea"
    LOW_BIOME = "low_biome"
    TAPER_ZONE = "taper_zone"
    HIGH_BIOME = "high_biome"
    MAINTENANCE_ZONE = "maintenance"

class SettlementType:
    """Types of dssstrkl settlements"""
    ELDER_AERIE = "elder_aerie"
    CLAN_DISTRICT = "clan_district"
    MAINTENANCE_TEMPLE = "maintenance_temple"
    YOUNGLING_SANCTUARY = "youngling_sanctuary"
    AGRICULTURAL_HUB = "agricultural_hub"
    CULT_HIDEOUT = "cult_hideout"

# ===== PROPERTY GROUPS =====

class AtlanteanTechProperties(PropertyGroup):
    tesseract_influence: FloatProperty(
        name="Tesseract Field Strength",
        description="4D hypercube's reality warping effect on terrain geometry",
        default=1.0,
        min=0.0,
        max=2.0
    )
    
    bone_stone_density: FloatProperty(
        name="Bone-Stone Density",
        description="Density of Atlantean bone-stone structures",
        default=0.7,
        min=0.0,
        max=1.0
    )
    
    antigrav_zones: IntProperty(
        name="Antigrav Zones",
        description="Number of antigravity field zones (creates floating terrain)",
        default=3,
        min=0,
        max=10
    )
    
    spectral_intensity: FloatProperty(
        name="Spectral Effects",
        description="Ghostly glow intensity of Atlantean materials",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    decay_level: FloatProperty(
        name="System Decay",
        description="Level of Atlantean technology failure (creates collapsed/dangerous zones)",
        default=0.3,
        min=0.0,
        max=1.0
    )

class DssstrkLAdaptationProperties(PropertyGroup):
    raptor_accessibility: BoolProperty(
        name="Raptor Accessibility",
        description="Design for dssstrkl raptor physiology (perching, climbing)",
        default=True
    )
    
    perching_structures: FloatProperty(
        name="Perching Density",
        description="Density of perching/climbing structures for raptor movement",
        default=0.6,
        min=0.0,
        max=1.0
    )
    
    vertical_navigation: BoolProperty(
        name="Vertical Navigation",
        description="Emphasize vertical movement paths for raptor physiology",
        default=True
    )
    
    clan_territories: IntProperty(
        name="Clan Territories",
        description="Number of distinct family/clan territorial zones",
        default=4,
        min=1,
        max=12
    )
    
    cultural_preservation: FloatProperty(
        name="Cultural Elements",
        description="Density of memorial sites and cultural preservation areas",
        default=0.4,
        min=0.0,
        max=1.0
    )

class CultInfiltrationProperties(PropertyGroup):
    infiltration_level: FloatProperty(
        name="Cult Infiltration",
        description="Death cult penetration into dssstrkl society (affects terrain corruption)",
        default=0.1,
        min=0.0,
        max=0.5
    )
    
    hidden_shrines: IntProperty(
        name="Hidden Shrines",
        description="Number of secret death-worship sites",
        default=2,
        min=0,
        max=8
    )
    
    communication_arrays: BoolProperty(
        name="Communication Arrays",
        description="Include hidden communication systems to contact destroyers",
        default=False
    )
    
    corruption_patterns: FloatProperty(
        name="Tech Corruption",
        description="Level of Atlantean tech corruption by cult (dark veins, geometric scars)",
        default=0.05,
        min=0.0,
        max=0.3
    )

class HeightmapGenerationProperties(PropertyGroup):
    resolution: EnumProperty(
        name="Heightmap Resolution",
        description="Resolution of generated heightmaps",
        items=[
            ('64', "64x64", "Very low resolution for testing"),
            ('128', "128x128", "Low resolution for preview"),
            ('256', "256x256", "Medium resolution"),
            ('512', "512x512", "High resolution"),
            ('1024', "1K", "Very high resolution")
        ],
        default='128'
    )
    
    atlantean_base_scale: FloatProperty(
        name="Atlantean Scale",
        description="Scale of base Atlantean geometric patterns",
        default=10.0,
        min=5.0,
        max=50.0
    )
    
    organic_overlay_scale: FloatProperty(
        name="Organic Overlay Scale", 
        description="Scale of dssstrkl organic modifications",
        default=5.0,
        min=2.0,
        max=25.0
    )
    
    erosion_simulation: BoolProperty(
        name="Erosion Simulation",
        description="Apply realistic erosion patterns",
        default=False  # Disabled by default for performance
    )
    
    generate_normal_maps: BoolProperty(
        name="Generate Normal Maps",
        description="Create normal maps from heightmaps",
        default=False  # Disabled by default for performance
    )

class HabitatDesignProperties(PropertyGroup):
    atlantean_tech: PointerProperty(type=AtlanteanTechProperties)
    dssstrkl_adaptation: PointerProperty(type=DssstrkLAdaptationProperties)
    cult_infiltration: PointerProperty(type=CultInfiltrationProperties)
    heightmap_generation: PointerProperty(type=HeightmapGenerationProperties)
    
    # Global habitat properties
    cylinder_radius: FloatProperty(
        name="Habitat Radius",
        description="Radius of the O'Neill cylinder",
        default=1000.0,
        min=500.0,
        max=5000.0,
        unit='LENGTH'
    )
    
    cylinder_length: FloatProperty(
        name="Habitat Length", 
        description="Length of the O'Neill cylinder",
        default=3000.0,
        min=1000.0,
        max=10000.0,
        unit='LENGTH'
    )
    
    geometry_detail: EnumProperty(
        name="Geometry Detail",
        description="Level of detail for cylinder geometry",
        items=[
            ('LOW', "Low", "32x16 segments - fast preview"),
            ('MEDIUM', "Medium", "64x32 segments - balanced"),
            ('HIGH', "High", "128x64 segments - detailed")
        ],
        default='LOW'
    )

# ===== CLAN TERRITORY SYSTEM =====

class ClanTerritoryManager:
    """Manages clan territorial divisions and their characteristics"""
    
    def __init__(self, num_clans, cylinder_length):
        self.num_clans = num_clans
        self.cylinder_length = cylinder_length
        self.territories = self.generate_clan_territories()
        
    def generate_clan_territories(self):
        """Generate clan territorial boundaries"""
        territories = []
        
        # Divide cylinder length among clans
        territory_length = self.cylinder_length / self.num_clans
        
        for i in range(self.num_clans):
            start_x = -self.cylinder_length/2 + i * territory_length
            end_x = start_x + territory_length
            
            # Each clan gets a different cultural flavor
            clan_traits = {
                'start_x': start_x,
                'end_x': end_x,
                'preferred_elevation': 0.3 + (i / self.num_clans) * 0.4,  # Different elevation preferences
                'architectural_style': i % 3,  # 3 different architectural styles
                'color_scheme': (
                    0.5 + (i * 0.7 / self.num_clans) % 1.0,  # Hue variation
                    0.6 + (i * 0.3 / self.num_clans) % 0.4,  # Saturation
                    0.4 + (i * 0.5 / self.num_clans) % 0.5   # Brightness
                ),
                'clan_id': i,
                'isolation_level': random.uniform(0.1, 0.8)  # How isolated this clan is
            }
            territories.append(clan_traits)
            
        return territories
    
    def get_clan_for_position(self, world_x):
        """Determine which clan territory a world position belongs to"""
        for territory in self.territories:
            if territory['start_x'] <= world_x <= territory['end_x']:
                return territory
        return self.territories[0]  # Fallback

# ===== OPTIMIZED HEIGHTMAP GENERATION =====

class LayeredHeightmapGenerator:
    """Multi-layered heightmap generation with clan territories and cult infiltration"""
    
    def __init__(self, properties):
        self.props = properties
        self.resolution = int(properties.heightmap_generation.resolution)
        self.clan_manager = ClanTerritoryManager(
            properties.dssstrkl_adaptation.clan_territories,
            properties.cylinder_length
        )
        print(f"Initializing layered heightmap generator with {self.resolution}x{self.resolution} resolution")
        print(f"Managing {properties.dssstrkl_adaptation.clan_territories} clan territories")
        
    def generate_complete_heightmap(self):
        """Generate multi-layered heightmap with all civilization layers"""
        print("Starting layered heightmap generation...")
        start_time = time.time()
        
        # Generate each layer
        atlantean_layer = self.generate_atlantean_base_layer()
        dssstrkl_layer = self.apply_dssstrkl_adaptations(atlantean_layer)
        decay_layer = self.apply_system_decay(dssstrkl_layer)
        final_heightmap = self.apply_cult_corruption(decay_layer)
        
        elapsed_time = time.time() - start_time
        print(f"Layered heightmap generation completed in {elapsed_time:.2f} seconds")
        
        return {
            'final': final_heightmap,
            'atlantean_base': atlantean_layer,
            'dssstrkl_adapted': dssstrkl_layer,
            'decay_applied': decay_layer,
            'clan_territories': self.clan_manager.territories
        }
    
    def generate_atlantean_base_layer(self):
        """Generate perfect Atlantean geometric foundation"""
        print("Generating Atlantean base layer...")
        size = self.resolution
        heightmap = [[0.0 for _ in range(size)] for _ in range(size)]
        
        tesseract_power = self.props.atlantean_tech.tesseract_influence
        atlantean_scale = self.props.heightmap_generation.atlantean_base_scale
        
        for y in range(size):
            for x in range(size):
                # Normalized coordinates
                nx = (x / size) * 2 - 1
                ny = (y / size) * 2 - 1
                
                # Tesseract field influence - 4D hypercube reality warping
                distance_from_center = math.sqrt(nx*nx + ny*ny)
                
                # 4D projection effects (impossible geometry)
                tesseract_field = (
                    math.cos(distance_from_center * math.pi * 2) * tesseract_power * 0.3 +
                    math.sin(distance_from_center * math.pi * 4) * tesseract_power * 0.2
                )
                
                # Sacred geometric patterns
                spiral_angle = math.atan2(ny, nx)
                fibonacci_pattern = math.sin(spiral_angle * 8 + distance_from_center * 13) * 0.15
                
                # Perfect crystalline structures
                crystal_grid = (
                    math.sin(nx * atlantean_scale * 0.5) * 
                    math.cos(ny * atlantean_scale * 0.5) * 0.2
                )
                
                # Combine Atlantean patterns
                height = 0.5 + tesseract_field + fibonacci_pattern + crystal_grid
                heightmap[y][x] = max(0.0, min(1.0, height))
        
        return heightmap
    
    def apply_dssstrkl_adaptations(self, base_heightmap):
        """Apply organic dssstrkl modifications with clan territories"""
        print("Applying dssstrkl adaptations with clan territories...")
        size = len(base_heightmap)
        adapted_heightmap = [row[:] for row in base_heightmap]
        
        organic_scale = self.props.heightmap_generation.organic_overlay_scale
        raptor_factor = 1.2 if self.props.dssstrkl_adaptation.raptor_accessibility else 1.0
        
        for y in range(size):
            for x in range(size):
                # Convert heightmap coordinates to world coordinates
                world_x = (x / size) * self.props.cylinder_length - self.props.cylinder_length/2
                clan_territory = self.clan_manager.get_clan_for_position(world_x)
                
                nx = (x / size) * 2 - 1
                ny = (y / size) * 2 - 1
                base_height = base_heightmap[y][x]
                
                # Clan-specific modifications
                clan_preference = clan_territory['preferred_elevation']
                clan_style = clan_territory['architectural_style']
                
                # Organic settlements near clan's preferred elevation
                elevation_affinity = 1.0 - abs(base_height - clan_preference)
                
                # Different architectural styles create different terrain modifications
                if clan_style == 0:  # Mountain dwellers - create terraces
                    terrain_mod = math.sin(base_height * math.pi * 8) * 0.1 * elevation_affinity
                elif clan_style == 1:  # Valley dwellers - smooth terrain
                    terrain_mod = -abs(noise.noise((nx * organic_scale * 0.1, ny * organic_scale * 0.1, clan_territory['clan_id']))) * 0.05
                else:  # Cliff dwellers - create stepped surfaces
                    terrain_mod = math.floor(base_height * 10) / 10 - base_height
                
                # Apply perching structures for raptor physiology
                if self.props.dssstrkl_adaptation.perching_structures > 0.5:
                    perching_mod = math.sin(base_height * math.pi * 12) * 0.05 * raptor_factor
                else:
                    perching_mod = 0
                
                adapted_heightmap[y][x] = max(0.0, min(1.0, 
                    base_height + terrain_mod + perching_mod))
        
        return adapted_heightmap
    
    def apply_system_decay(self, heightmap):
        """Apply Atlantean technology decay and failure"""
        print("Applying system decay...")
        size = len(heightmap)
        decay_heightmap = [row[:] for row in heightmap]
        
        decay_level = self.props.atlantean_tech.decay_level
        
        if decay_level <= 0:
            return decay_heightmap
        
        for y in range(size):
            for x in range(size):
                nx = (x / size) * 2 - 1
                ny = (y / size) * 2 - 1
                base_height = heightmap[y][x]
                
                # System decay creates collapsed areas and unstable zones
                decay_noise = noise.noise((nx * 0.03, ny * 0.03, 123)) * decay_level
                
                # Antigrav field failures create sudden drops
                field_failure = 0.0
                for i in range(self.props.atlantean_tech.antigrav_zones):
                    field_x = math.sin(i * 2.3) * 0.7
                    field_y = math.cos(i * 1.7) * 0.7
                    field_distance = math.sqrt((nx - field_x)**2 + (ny - field_y)**2)
                    
                    if field_distance < 0.3:  # Field failure zone
                        field_failure -= 0.3 * (1 - field_distance / 0.3) * decay_level
                
                # Apply decay
                modified_height = base_height + decay_noise + field_failure
                decay_heightmap[y][x] = max(0.0, min(1.0, modified_height))
        
        return decay_heightmap
    
    def apply_cult_corruption(self, heightmap):
        """Apply cult infiltration effects"""
        print("Applying cult corruption...")
        size = len(heightmap)
        corrupted_heightmap = [row[:] for row in heightmap]
        
        infiltration_level = self.props.cult_infiltration.infiltration_level
        corruption_level = self.props.cult_infiltration.corruption_patterns
        
        if infiltration_level <= 0:
            return corrupted_heightmap
        
        for y in range(size):
            for x in range(size):
                nx = (x / size) * 2 - 1
                ny = (y / size) * 2 - 1
                base_height = heightmap[y][x]
                
                # Cult corruption creates unnatural geometric scars
                corruption_noise = 0.0
                if corruption_level > 0:
                    # Death cult creates angular, unnatural modifications
                    angular_x = abs(nx * 10) % 1.0
                    angular_y = abs(ny * 10) % 1.0
                    
                    if angular_x < 0.1 or angular_y < 0.1:  # Create grid-like scars
                        corruption_noise = -corruption_level * 0.2
                
                # Hidden shrine influence
                shrine_influence = 0.0
                for i in range(self.props.cult_infiltration.hidden_shrines):
                    shrine_x = math.sin(i * 3.7 + 100) * 0.8
                    shrine_y = math.cos(i * 2.1 + 100) * 0.8
                    shrine_distance = math.sqrt((nx - shrine_x)**2 + (ny - shrine_y)**2)
                    
                    if shrine_distance < 0.2:
                        shrine_influence -= 0.15 * (1 - shrine_distance / 0.2) * infiltration_level
                
                modified_height = base_height + corruption_noise + shrine_influence
                corrupted_heightmap[y][x] = max(0.0, min(1.0, modified_height))
        
        return corrupted_heightmap

# ===== OPTIMIZED GEOMETRY GENERATION =====

class OptimizedCylinderGenerator:
    """Performance-optimized cylinder generation with fixed bmesh operations"""
    
    def __init__(self, properties):
        self.props = properties
        
    def create_cylinder_with_heightmap(self, heightmap_data):
        """Create cylinder geometry with heightmap displacement"""
        print("Creating cylinder geometry...")
        start_time = time.time()
        
        # Get geometry detail settings
        detail_settings = {
            'LOW': (32, 16),
            'MEDIUM': (64, 32),
            'HIGH': (128, 64)
        }
        
        segments_circ, segments_length = detail_settings[self.props.geometry_detail]
        print(f"Using {segments_circ}x{segments_length} segments")
        
        radius = self.props.cylinder_radius
        length = self.props.cylinder_length
        
        # Create cylinder using standard mesh operations (avoiding bmesh.ops issue)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=length,
            vertices=segments_circ,
            location=(0, 0, 0)
        )
        
        # Get the created object and convert to bmesh for modification
        cylinder_obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = cylinder_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Subdivide for length segments if needed
        if segments_length > 1:
            bpy.ops.mesh.subdivide(number_cuts=segments_length-1)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Convert to bmesh for displacement
        bm = bmesh.new()
        bm.from_mesh(cylinder_obj.data)
        
        print(f"Created base cylinder with {len(bm.verts)} vertices")
        
        # Apply heightmap displacement
        self.apply_heightmap_displacement(bm, heightmap_data['final'], radius, length)
        
        # Update the mesh
        bm.to_mesh(cylinder_obj.data)
        bm.free()
        
        # Store metadata
        cylinder_obj["heightmap_resolution"] = int(self.props.heightmap_generation.resolution)
        cylinder_obj["clan_territories"] = len(heightmap_data['clan_territories'])
        
        elapsed_time = time.time() - start_time
        print(f"Cylinder generation completed in {elapsed_time:.2f} seconds")
        
        return cylinder_obj
    
    def apply_heightmap_displacement(self, bm, heightmap, radius, length):
        """Apply heightmap displacement to vertices"""
        print("Applying heightmap displacement...")
        
        heightmap_size = len(heightmap)
        displacement_scale = radius * 0.05  # 5% of radius
        
        vertices_processed = 0
        total_vertices = len(bm.verts)
        
        for vert in bm.verts:
            # Convert 3D position to heightmap coordinates
            # X maps to heightmap X (along cylinder length)
            rel_x = (vert.co.x + length/2) / length
            rel_x = max(0.0, min(1.0, rel_x))
            
            # Y,Z maps to heightmap Y (around circumference)
            angle = math.atan2(vert.co.z, vert.co.y)
            if angle < 0:
                angle += 2 * math.pi
            rel_y = angle / (2 * math.pi)
            
            # Sample heightmap
            hm_x = int(rel_x * (heightmap_size - 1))
            hm_y = int(rel_y * (heightmap_size - 1))
            height_value = heightmap[hm_y][hm_x]
            
            # Apply displacement inward (for interior surface)
            current_radius = math.sqrt(vert.co.y*vert.co.y + vert.co.z*vert.co.z)
            displacement = -height_value * displacement_scale
            new_radius = current_radius + displacement
            
            # Prevent collapse
            new_radius = max(new_radius, radius * 0.5)
            
            # Update vertex position
            if current_radius > 0.001:
                scale_factor = new_radius / current_radius
                vert.co.y *= scale_factor
                vert.co.z *= scale_factor
            
            vertices_processed += 1
            if vertices_processed % 1000 == 0:
                progress = int((vertices_processed / total_vertices) * 100)
                print(f"Displacement progress: {progress}%")
        
        print(f"Applied displacement to {vertices_processed} vertices")

# ===== ENHANCED SETTLEMENT PLACEMENT =====

class ClanAwareSettlementPlacer:
    """Settlement placement that respects clan territories and cult infiltration"""
    
    def __init__(self, heightmap_data, properties):
        self.heightmap = heightmap_data['final']
        self.clan_territories = heightmap_data['clan_territories']
        self.props = properties
        self.size = len(self.heightmap)
        
    def place_all_settlements(self):
        """Place all settlement types with clan and cult awareness"""
        settlements = {
            'elder_aeries': [],
            'maintenance_temples': [],
            'clan_districts': [],
            'cult_hideouts': []
        }
        
        # Place clan-specific settlements
        for territory in self.clan_territories:
            clan_settlements = self.place_clan_settlements(territory)
            for settlement_type, locations in clan_settlements.items():
                settlements[settlement_type].extend(locations)
        
        # Place cult hideouts based on infiltration
        cult_settlements = self.place_cult_settlements()
        settlements['cult_hideouts'] = cult_settlements
        
        return settlements
    
    def place_clan_settlements(self, clan_territory):
        """Place settlements for a specific clan territory"""
        clan_settlements = {
            'elder_aeries': [],
            'maintenance_temples': [],
            'clan_districts': []
        }
        
        # Convert clan territory bounds to heightmap coordinates
        start_hm_x = int((clan_territory['start_x'] + self.props.cylinder_length/2) / self.props.cylinder_length * self.size)
        end_hm_x = int((clan_territory['end_x'] + self.props.cylinder_length/2) / self.props.cylinder_length * self.size)
        
        start_hm_x = max(0, min(self.size-1, start_hm_x))
        end_hm_x = max(0, min(self.size-1, end_hm_x))
        
        preferred_elevation = clan_territory['preferred_elevation']
        clan_id = clan_territory['clan_id']
        
        # Search within clan territory bounds
        step = max(1, (end_hm_x - start_hm_x) // 8)
        
        for x in range(start_hm_x, end_hm_x, step):
            for y in range(0, self.size, step):
                height = self.heightmap[y][x]
                elevation_fitness = 1.0 - abs(height - preferred_elevation)
                
                # Elder aerie - highest points in clan territory
                if height > preferred_elevation + 0.2 and elevation_fitness > 0.6:
                    clan_settlements['elder_aeries'].append((x, y, height, clan_id))
                
                # Clan districts - near preferred elevation
                elif elevation_fitness > 0.8:
                    clan_settlements['clan_districts'].append((x, y, height, clan_id))
                
                # Maintenance temples - moderate elevations
                elif 0.3 < height < 0.7:
                    clan_settlements['maintenance_temples'].append((x, y, height, clan_id))
        
        # Limit settlements per clan
        for settlement_type in clan_settlements:
            clan_settlements[settlement_type] = clan_settlements[settlement_type][:3]
        
        return clan_settlements
    
    def place_cult_hideouts(self):
        """Place cult hideouts based on infiltration level"""
        hideouts = []
        
        if self.props.cult_infiltration.infiltration_level <= 0:
            return hideouts
        
        max_hideouts = self.props.cult_infiltration.hidden_shrines
        infiltration = self.props.cult_infiltration.infiltration_level
        
        # Sample locations for cult hideouts
        attempts = 0
        while len(hideouts) < max_hideouts and attempts < 1000:
            x = random.randint(5, self.size - 5)
            y = random.randint(5, self.size - 5)
            height = self.heightmap[y][x]
            
            # High infiltration allows cult sites anywhere
            # Low infiltration restricts to isolated areas
            if infiltration > 0.3:
                # High infiltration - cult can hide anywhere
                hideouts.append((x, y, height, -1))  # -1 indicates cult
            else:
                # Low infiltration - only in isolated low areas
                if height < 0.3:
                    # Check isolation
                    isolation_score = 0
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            if 0 <= y+dy < self.size and 0 <= x+dx < self.size:
                                if self.heightmap[y+dy][x+dx] > height:
                                    isolation_score += 1
                    
                    if isolation_score > 15:  # Well hidden
                        hideouts.append((x, y, height, -1))
            
            attempts += 1
        
        return hideouts

# ===== MAIN OPERATOR =====

class DSSSTRKL_OT_generate_habitat(Operator):
    bl_idname = "dssstrkl.generate_habitat"
    bl_label = "Generate Habitat"
    bl_description = "Generate complete O'Neill cylinder habitat with clan territories and cult infiltration"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.dssstrkl_habitat
        
        print("=== STARTING DSSSTRKL HABITAT GENERATION ===")
        overall_start = time.time()
        
        try:
            # Clear existing habitat objects
            self.clear_existing_habitat(context)
            
            # Generate layered heightmaps
            print("Step 1: Generating layered heightmaps...")
            generator = LayeredHeightmapGenerator(props)
            heightmap_data = generator.generate_complete_heightmap()
            
            # Create cylinder geometry
            print("Step 2: Creating cylinder geometry...")
            cylinder_gen = OptimizedCylinderGenerator(props)
            cylinder_obj = cylinder_gen.create_cylinder_with_heightmap(heightmap_data)
            cylinder_obj.name = "Dssstrkl_Habitat_Main"
            
            # Add materials with clan and spectral effects
            print("Step 3: Creating civilization-aware materials...")
            self.create_civilization_materials(cylinder_obj, props, heightmap_data)
            
            # Place settlements with clan awareness
            print("Step 4: Placing clan-aware settlements...")
            self.place_settlements_with_clans(context, heightmap_data, props)
            
            # Create central features
            print("Step 5: Creating central tesseract and infrastructure...")
            self.create_central_features(context, props)
            
            # Create clan territory markers (for manual editing reference)
            print("Step 6: Creating clan territory markers...")
            self.create_clan_territory_markers(context, heightmap_data, props)
            
            # Store metadata for future manual editing
            cylinder_obj["heightmap_resolution"] = int(props.heightmap_generation.resolution)
            cylinder_obj["clan_territories"] = len(heightmap_data['clan_territories'])
            cylinder_obj["cult_infiltration"] = props.cult_infiltration.infiltration_level
            cylinder_obj["generation_time"] = time.time() - overall_start
            
            overall_time = time.time() - overall_start
            print(f"=== DSSSTRKL HABITAT GENERATION COMPLETE ===")
            print(f"Total time: {overall_time:.2f} seconds")
            print(f"Generated {len(heightmap_data['clan_territories'])} clan territories")
            print(f"Cult infiltration level: {props.cult_infiltration.infiltration_level:.2f}")
            
            self.report({'INFO'}, f"Habitat with {len(heightmap_data['clan_territories'])} clans generated in {overall_time:.1f}s")
            
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def clear_existing_habitat(self, context):
        """Remove existing habitat objects"""
        print("Clearing existing habitat objects...")
        objects_to_remove = [obj for obj in context.scene.objects 
                           if obj.name.startswith("Dssstrkl_")]
        
        for obj in objects_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
        
        print(f"Removed {len(objects_to_remove)} existing objects")
    
    def create_civilization_materials(self, obj, props, heightmap_data):
        """Create materials that reflect civilization layers"""
        # Base Atlantean bone-stone material
        atlantean_mat = bpy.data.materials.new(name="Atlantean_BoneStone")
        atlantean_mat.diffuse_color = (0.9, 0.85, 0.75, 1.0)  # Bone-like color
        atlantean_mat.metallic = 0.1
        atlantean_mat.roughness = 0.3
        
        # Add spectral effects if enabled
        if props.atlantean_tech.spectral_intensity > 0.5:
            atlantean_mat.use_nodes = True
            nodes = atlantean_mat.node_tree.nodes
            principled = nodes.get("Principled BSDF")
            if principled:
                # Ghostly blue-white glow
                principled.inputs['Emission'].default_value = (0.6, 0.8, 1.0, 1.0)
                principled.inputs['Emission Strength'].default_value = props.atlantean_tech.spectral_intensity * 0.5
        
        obj.data.materials.append(atlantean_mat)
        
        # Create clan-specific materials (for future manual assignment)
        for territory in heightmap_data['clan_territories']:
            clan_mat = bpy.data.materials.new(name=f"Clan_{territory['clan_id']}_Material")
            clan_mat.diffuse_color = (*territory['color_scheme'], 1.0)
            clan_mat.metallic = 0.2
            clan_mat.roughness = 0.4
        
        # Create cult corruption material (for manual assignment to corrupted areas)
        if props.cult_infiltration.infiltration_level > 0:
            cult_mat = bpy.data.materials.new(name="Cult_Corruption")
            # Dark, unnatural colors
            cult_mat.diffuse_color = (0.2, 0.1, 0.15, 1.0)
            cult_mat.metallic = 0.8
            cult_mat.roughness = 0.1
            
            if props.cult_infiltration.corruption_patterns > 0.2:
                cult_mat.use_nodes = True
                nodes = cult_mat.node_tree.nodes
                principled = nodes.get("Principled BSDF")
                if principled:
                    # Ominous red glow
                    principled.inputs['Emission'].default_value = (0.8, 0.1, 0.1, 1.0)
                    principled.inputs['Emission Strength'].default_value = props.cult_infiltration.corruption_patterns
        
        print("Created civilization-aware materials")
    
    def place_settlements_with_clans(self, context, heightmap_data, props):
        """Place settlements respecting clan territories"""
        placer = ClanAwareSettlementPlacer(heightmap_data, props)
        all_settlements = placer.place_all_settlements()
        
        total_settlements = 0
        
        # Place each settlement type
        for settlement_type, settlements in all_settlements.items():
            for settlement_data in settlements:
                hm_x, hm_y, height = settlement_data[:3]
                clan_id = settlement_data[3] if len(settlement_data) > 3 else -1
                
                world_pos = self.heightmap_to_world_pos(hm_x, hm_y, height, props)
                settlement_name = f"{settlement_type}_{total_settlements+1}"
                
                self.create_settlement_marker(context, world_pos, settlement_name, 
                                            settlement_type, clan_id, heightmap_data)
                total_settlements += 1
        
        print(f"Placed {total_settlements} clan-aware settlement markers")
    
    def heightmap_to_world_pos(self, hm_x, hm_y, height, props):
        """Convert heightmap coordinates to world position"""
        resolution = int(props.heightmap_generation.resolution)
        
        # X maps to cylinder length
        world_x = (hm_x / resolution) * props.cylinder_length - props.cylinder_length/2
        
        # Y maps to circumference
        angle = (hm_y / resolution) * 2 * math.pi
        surface_radius = props.cylinder_radius - height * props.cylinder_radius * 0.05
        
        world_y = surface_radius * math.cos(angle)
        world_z = surface_radius * math.sin(angle)
        
        return (world_x, world_y, world_z)
    
    def create_settlement_marker(self, context, location, name, settlement_type, clan_id, heightmap_data):
        """Create settlement marker with clan-specific styling"""
        # Choose primitive based on settlement type
        if settlement_type == "elder_aeries":
            bpy.ops.mesh.primitive_cone_add(radius1=50, depth=100, location=location)
            base_color = (0.7, 0.6, 0.4, 1.0)  # Golden
        elif settlement_type == "maintenance_temples":
            bpy.ops.mesh.primitive_cylinder_add(radius=30, depth=60, location=location)
            base_color = (0.5, 0.7, 0.9, 1.0)  # Tech blue
        elif settlement_type == "clan_districts":
            bpy.ops.mesh.primitive_cube_add(size=60, location=location)
            base_color = (0.6, 0.5, 0.3, 1.0)  # Neutral brown
        else:  # cult_hideouts
            bpy.ops.mesh.primitive_ico_sphere_add(radius=25, location=location)
            base_color = (0.3, 0.1, 0.1, 1.0)  # Dark red
        
        marker = context.active_object
        marker.name = f"Dssstrkl_{name}"
        
        # Apply clan-specific coloring if applicable
        if clan_id >= 0 and clan_id < len(heightmap_data['clan_territories']):
            clan_territory = heightmap_data['clan_territories'][clan_id]
            color = (*clan_territory['color_scheme'], 1.0)
            marker["clan_id"] = clan_id
            marker["clan_architecture_style"] = clan_territory['architectural_style']
        else:
            color = base_color
            marker["clan_id"] = -1  # No clan (cult or independent)
        
        # Create material
        mat = bpy.data.materials.new(name=f"{settlement_type}_{name}_material")
        mat.diffuse_color = color
        marker.data.materials.append(mat)
        
        # Store metadata for future manual editing
        marker["settlement_type"] = settlement_type
        marker["heightmap_x"] = location[0]  # For reference
        marker["heightmap_y"] = location[1]
    
    def create_central_features(self, context, props):
        """Create central tesseract and sea"""
        # Create central tesseract core with 4D effects
        bpy.ops.mesh.primitive_uv_sphere_add(radius=150, location=(0, 0, 0))
        tesseract = context.active_object
        tesseract.name = "Dssstrkl_Tesseract_Core"
        
        # Tesseract material with hyperdimensional effects
        mat = bpy.data.materials.new(name="Tesseract_4D_Material")
        mat.diffuse_color = (1.0, 0.9, 0.3, 1.0)
        mat.use_nodes = True
        
        # Intense reality-warping glow
        nodes = mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            glow_intensity = props.atlantean_tech.tesseract_influence * 5.0
            principled.inputs['Emission'].default_value = (1.0, 0.9, 0.3, 1.0)
            principled.inputs['Emission Strength'].default_value = glow_intensity
            
            # Make it slightly transparent for 4D effect
            principled.inputs['Alpha'].default_value = 0.8
        
        mat.blend_method = 'BLEND'
        tesseract.data.materials.append(mat)
        
        # Store tesseract metadata
        tesseract["tesseract_power"] = props.atlantean_tech.tesseract_influence
        tesseract["is_4d_hypercube"] = True
        tesseract["reality_distortion_radius"] = props.cylinder_radius
        
        # Create central sea for water reclamation
        sea_radius = props.cylinder_radius * 0.8
        bpy.ops.mesh.primitive_cylinder_add(radius=sea_radius, depth=50, location=(0, 0, 0))
        sea = context.active_object
        sea.name = "Dssstrkl_Central_Sea"
        
        # Water reclamation system material
        water_mat = bpy.data.materials.new(name="Reclamation_Water")
        water_mat.diffuse_color = (0.1, 0.3, 0.7, 0.8)
        water_mat.metallic = 0.0
        water_mat.roughness = 0.1
        water_mat.blend_method = 'BLEND'
        sea.data.materials.append(water_mat)
        
        sea["water_system"] = props.water_system_complexity
        sea["reclamation_active"] = True
        
        print("Created central tesseract core and water reclamation sea")
    
    def create_clan_territory_markers(self, context, heightmap_data, props):
        """Create visual markers for clan territory boundaries (for manual editing reference)"""
        for i, territory in enumerate(heightmap_data['clan_territories']):
            # Create boundary markers at territory edges
            start_x = territory['start_x']
            end_x = territory['end_x']
            
            # Place markers at territory boundaries
            for x_pos in [start_x, end_x]:
                bpy.ops.mesh.primitive_cube_add(
                    size=100, 
                    location=(x_pos, 0, props.cylinder_radius * 0.9)
                )
                marker = context.active_object
                marker.name = f"Dssstrkl_Territory_Boundary_Clan_{i}"
                marker.display_type = 'WIRE'
                
                # Clan color
                mat = bpy.data.materials.new(name=f"Territory_Boundary_Clan_{i}")
                mat.diffuse_color = (*territory['color_scheme'], 0.5)
                marker.data.materials.append(mat)
                
                # Store clan info for manual editing
                marker["clan_id"] = i
                marker["territory_start"] = territory['start_x']
                marker["territory_end"] = territory['end_x']
                marker["preferred_elevation"] = territory['preferred_elevation']
                marker["architectural_style"] = territory['architectural_style']
                marker["is_territory_marker"] = True
        
        print(f"Created territory boundary markers for {len(heightmap_data['clan_territories'])} clans")

# ===== QUICK TEST OPERATOR =====

class DSSSTRKL_OT_quick_test(Operator):
    bl_idname = "dssstrkl.quick_test"
    bl_label = "Quick Test"
    bl_description = "Generate a simple test habitat quickly"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("Running quick test...")
        
        # Create simple cylinder for testing
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1000,
            depth=3000,
            location=(0, 0, 0)
        )
        
        cylinder = context.active_object
        cylinder.name = "Dssstrkl_Test_Cylinder"
        
        # Add simple material
        mat = bpy.data.materials.new(name="Test_Material")
        mat.diffuse_color = (0.8, 0.7, 0.6, 1.0)
        cylinder.data.materials.append(mat)
        
        self.report({'INFO'}, "Quick test completed!")
        return {'FINISHED'}

# ===== MANUAL EDITING PREPARATION OPERATOR =====

class DSSSTRKL_OT_prepare_manual_editing(Operator):
    bl_idname = "dssstrkl.prepare_manual_editing"
    bl_label = "Prepare Manual Editing"
    bl_description = "Set up scene for manual biome and settlement placement"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("Preparing scene for manual editing...")
        
        # Create collection for manual editing objects
        manual_collection = bpy.data.collections.new("Dssstrkl_Manual_Editing")
        context.scene.collection.children.link(manual_collection)
        
        # Create biome zone templates
        biome_templates = [
            ("High_Biome_Template", (0.7, 0.9, 0.5, 0.8)),  # Green mountain
            ("Taper_Zone_Template", (0.9, 0.7, 0.4, 0.8)),  # Orange transition
            ("Low_Biome_Template", (0.4, 0.6, 0.9, 0.8)),   # Blue valley
            ("Maintenance_Zone_Template", (0.8, 0.8, 0.8, 0.8))  # Gray tech
        ]
        
        for template_name, color in biome_templates:
            bpy.ops.mesh.primitive_cube_add(size=200)
            template = context.active_object
            template.name = f"Dssstrkl_{template_name}"
            template.display_type = 'WIRE'
            
            # Move to manual editing collection
            context.scene.collection.objects.unlink(template)
            manual_collection.objects.link(template)
            
            # Create template material
            mat = bpy.data.materials.new(name=f"{template_name}_Material")
            mat.diffuse_color = color
            mat.blend_method = 'BLEND'
            template.data.materials.append(mat)
            
            template["is_biome_template"] = True
            template["biome_type"] = template_name
        
        # Create settlement templates
        settlement_templates = [
            ("Elder_Aerie_Template", "CONE", (0.8, 0.6, 0.2, 1.0)),
            ("Maintenance_Temple_Template", "CYLINDER", (0.2, 0.6, 0.8, 1.0)),
            ("Cult_Shrine_Template", "ICOSPHERE", (0.6, 0.1, 0.1, 1.0))
        ]
        
        for template_name, primitive_type, color in settlement_templates:
            if primitive_type == "CONE":
                bpy.ops.mesh.primitive_cone_add(radius1=50, depth=100)
            elif primitive_type == "CYLINDER":
                bpy.ops.mesh.primitive_cylinder_add(radius=30, depth=60)
            else:  # ICOSPHERE
                bpy.ops.mesh.primitive_ico_sphere_add(radius=25)
            
            template = context.active_object
            template.name = f"Dssstrkl_{template_name}"
            
            # Move to manual editing collection
            context.scene.collection.objects.unlink(template)
            manual_collection.objects.link(template)
            
            # Create template material
            mat = bpy.data.materials.new(name=f"{template_name}_Material")
            mat.diffuse_color = color
            template.data.materials.append(mat)
            
            template["is_settlement_template"] = True
            template["settlement_type"] = template_name
        
        self.report({'INFO'}, "Manual editing templates created in 'Dssstrkl_Manual_Editing' collection")
        return {'FINISHED'}

# ===== UI PANELS =====

class DSSSTRKL_PT_main_panel(Panel):
    bl_label = "Dssstrkl Habitat Designer"
    bl_idname = "DSSSTRKL_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dssstrkl"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.dssstrkl_habitat
        
        # Header
        box = layout.box()
        box.label(text="🚀 Ancient Atlantean Space Ark", icon='WORLD')
        box.label(text="Dssstrkl Survival Habitat")
        
        # Global settings
        col = layout.column()
        col.prop(props, "cylinder_radius")
        col.prop(props, "cylinder_length")
        col.prop(props, "geometry_detail")
        
        # Performance section
        box = layout.box()
        box.label(text="⚡ Performance Settings")
        box.prop(props.heightmap_generation, "resolution")
        
        # Clan territories info
        box = layout.box()
        box.label(text="🏘️ Clan System")
        box.prop(props.dssstrkl_adaptation, "clan_territories")
        box.label(text=f"Will create {props.dssstrkl_adaptation.clan_territories} distinct territories")
        
        # Cult infiltration warning
        if props.cult_infiltration.infiltration_level > 0.2:
            box = layout.box()
            box.label(text="⚠️ High Cult Infiltration", icon='ERROR')
            box.label(text="Destroyers may detect signals!")
        
        # Generation buttons
        layout.separator()
        col = layout.column()
        
        # Main generation button
        row = col.row()
        row.scale_y = 2.0
        row.operator("dssstrkl.generate_habitat", icon='WORLD_DATA')
        
        # Additional tools
        col.operator("dssstrkl.quick_test", icon='PLAY')
        col.operator("dssstrkl.prepare_manual_editing", icon='TOOL_SETTINGS')

class DSSSTRKL_PT_atlantean_tech(Panel):
    bl_label = "Atlantean Technology"
    bl_idname = "DSSSTRKL_PT_atlantean"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dssstrkl"
    bl_parent_id = "DSSSTRKL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.dssstrkl_habitat.atlantean_tech
        
        col = layout.column()
        col.prop(props, "tesseract_influence")
        col.label(text="4D reality warping effects")
        
        col.separator()
        col.prop(props, "spectral_intensity")
        col.label(text="Ghostly material glow")
        
        col.separator()
        col.prop(props, "decay_level")
        col.label(text="Technology failure zones")
        
        col.separator()
        col.prop(props, "antigrav_zones")

class DSSSTRKL_PT_dssstrkl_adaptation(Panel):
    bl_label = "Dssstrkl Adaptations"
    bl_idname = "DSSSTRKL_PT_dssstrkl"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dssstrkl"
    bl_parent_id = "DSSSTRKL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.dssstrkl_habitat.dssstrkl_adaptation
        
        col = layout.column()
        col.prop(props, "clan_territories")
        col.label(text="Distinct family groups")
        
        col.separator()
        col.prop(props, "raptor_accessibility")
        col.prop(props, "perching_structures")
        col.label(text="Raptor physiology features")
        
        col.separator()
        col.prop(props, "cultural_preservation")

class DSSSTRKL_PT_cult_infiltration(Panel):
    bl_label = "Cult Infiltration"
    bl_idname = "DSSSTRKL_PT_cult"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Dssstrkl"
    bl_parent_id = "DSSSTRKL_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.dssstrkl_habitat.cult_infiltration
        
        col = layout.column()
        col.prop(props, "infiltration_level")
        col.label(text="Death cult society penetration")
        
        col.separator()
        col.prop(props, "hidden_shrines")
        col.label(text="Secret worship sites")
        
        col.separator()
        col.prop(props, "corruption_patterns")
        col.label(text="Atlantean tech corruption")
        
        col.separator()
        col.prop(props, "communication_arrays")
        
        # Warning for high infiltration
        if props.infiltration_level > 0.3:
            box = layout.box()
            box.label(text="⚠️ Extreme Danger", icon='ERROR')
            box.label(text="High infiltration risks")
            box.label(text="attracting the destroyers!")

# ===== REGISTRATION =====

classes = [
    AtlanteanTechProperties,
    DssstrkLAdaptationProperties,
    CultInfiltrationProperties,
    HeightmapGenerationProperties,
    HabitatDesignProperties,
    DSSSTRKL_OT_generate_habitat,
    DSSSTRKL_OT_quick_test,
    DSSSTRKL_OT_prepare_manual_editing,
    DSSSTRKL_PT_main_panel,
    DSSSTRKL_PT_atlantean_tech,
    DSSSTRKL_PT_dssstrkl_adaptation,
    DSSSTRKL_PT_cult_infiltration,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.dssstrkl_habitat = PointerProperty(type=HabitatDesignProperties)
    
    print("Dssstrkl Habitat Designer registered successfully!")
    print("NOTE: Future versions will include manual biome and shrine placement tools")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.dssstrkl_habitat
    
    print("Dssstrkl Habitat Designer unregistered")

if __name__ == "__main__":
    register()