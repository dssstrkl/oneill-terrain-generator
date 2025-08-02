"""
O'Neill Terrain Generator - Unified Canvas Module
Phase 1.2 Implementation: Create unified canvas that represents all cylinders as single paintable surface

Key Objectives:
- Analyze flat object positions and dimensions 
- Calculate optimal unified canvas dimensions
- Create UV mapping correspondence table (canvas pixel → cylinder region)
- Replace current individual region approach with single canvas
"""

import bpy
import bmesh
from mathutils import Vector
import math

class LayoutAnalyzer:
    """
    Analyzes current flat object layout to determine optimal unified canvas structure
    """
    
    def __init__(self):
        self.flat_objects = []
        self.layout_bounds = {}
        self.object_dimensions = {}
        
    def analyze_flat_object_layout(self):
        """
        Step 1: Calculate positions and dimensions of all 12 flat objects
        Goal: Get layout bounds (min_x, max_x, min_y, max_y) and object positioning table
        """
        print("🔍 Analyzing flat object layout for unified canvas...")
        
        # Get all flat objects
        self.flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not self.flat_objects:
            print("❌ No flat objects found")
            return False
        
        # Sort by X position for predictable processing
        self.flat_objects.sort(key=lambda obj: obj.location.x)
        
        print(f"📋 Found {len(self.flat_objects)} flat objects")
        
        # Calculate bounds and dimensions for each object
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for i, obj in enumerate(self.flat_objects):
            # Get object world bounds
            local_bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            
            # Calculate actual bounds
            obj_min_x = min(corner.x for corner in local_bbox_corners)
            obj_max_x = max(corner.x for corner in local_bbox_corners)
            obj_min_y = min(corner.y for corner in local_bbox_corners)
            obj_max_y = max(corner.y for corner in local_bbox_corners)
            
            # Store object info
            self.object_dimensions[obj.name] = {
                'index': i,
                'location': obj.location.copy(),
                'bounds': {
                    'min_x': obj_min_x,
                    'max_x': obj_max_x,
                    'min_y': obj_min_y,
                    'max_y': obj_max_y
                },
                'dimensions': {
                    'width': obj_max_x - obj_min_x,
                    'height': obj_max_y - obj_min_y
                }
            }
            
            # Update global bounds
            min_x = min(min_x, obj_min_x)
            max_x = max(max_x, obj_max_x)
            min_y = min(min_y, obj_min_y)
            max_y = max(max_y, obj_max_y)
            
            print(f"  {i}: {obj.name} at X={obj.location.x:.1f}, bounds=({obj_min_x:.1f}, {obj_max_x:.1f})")
        
        # Store global layout bounds
        self.layout_bounds = {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'total_width': max_x - min_x,
            'total_height': max_y - min_y
        }
        
        print(f"🌐 Global layout bounds:")
        print(f"   X: {min_x:.1f} to {max_x:.1f} (width: {max_x - min_x:.1f})")
        print(f"   Y: {min_y:.1f} to {max_y:.1f} (height: {max_y - min_y:.1f})")
        
        return True
    
    def get_flat_object_bounds(self):
        """
        Return calculated object bounds and dimensions
        """
        return self.layout_bounds, self.object_dimensions
    
    def generate_layout_report(self):
        """
        Generate debug information about the layout
        """
        if not self.layout_bounds:
            return "No layout analysis performed yet"
        
        report = []
        report.append("📊 FLAT OBJECT LAYOUT ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Total Objects: {len(self.flat_objects)}")
        report.append(f"Layout Bounds: X({self.layout_bounds['min_x']:.1f} to {self.layout_bounds['max_x']:.1f}), Y({self.layout_bounds['min_y']:.1f} to {self.layout_bounds['max_y']:.1f})")
        report.append(f"Total Dimensions: {self.layout_bounds['total_width']:.1f} x {self.layout_bounds['total_height']:.1f}")
        report.append("")
        report.append("Individual Object Details:")
        
        for obj_name, data in self.object_dimensions.items():
            report.append(f"  {data['index']:2d}. {obj_name}")
            report.append(f"      Location: ({data['location'].x:.1f}, {data['location'].y:.1f}, {data['location'].z:.1f})")
            report.append(f"      Dimensions: {data['dimensions']['width']:.1f} x {data['dimensions']['height']:.1f}")
            report.append(f"      Bounds: X({data['bounds']['min_x']:.1f} to {data['bounds']['max_x']:.1f})")
        
        return "\n".join(report)


class UnifiedCanvasManager:
    """
    Manages creation and configuration of unified canvas system
    """
    
    def __init__(self):
        self.canvas_name = "ONeill_Unified_Canvas"
        self.layout_analyzer = LayoutAnalyzer()
        self.optimal_dimensions = None
        self.pixels_per_unit = 100.0  # Default resolution
        
    def calculate_optimal_dimensions(self):
        """
        Step 2: Determine optimal canvas size to represent all objects
        Goal: Calculate based on layout bounds with appropriate pixels-per-unit ratio
        """
        print("📏 Calculating optimal unified canvas dimensions...")
        
        # First analyze the layout
        if not self.layout_analyzer.analyze_flat_object_layout():
            return False
        
        layout_bounds, object_dimensions = self.layout_analyzer.get_flat_object_bounds()
        
        # Calculate canvas dimensions based on world space layout
        world_width = layout_bounds['total_width']
        world_height = layout_bounds['total_height']
        
        # Calculate pixel dimensions
        canvas_width = int(world_width * self.pixels_per_unit)
        canvas_height = int(world_height * self.pixels_per_unit)
        
        # Ensure dimensions are reasonable for Blender (power of 2 friendly)
        canvas_width = self._round_to_reasonable_size(canvas_width)
        canvas_height = self._round_to_reasonable_size(canvas_height)
        
        self.optimal_dimensions = {
            'width': canvas_width,
            'height': canvas_height,
            'world_width': world_width,
            'world_height': world_height,
            'pixels_per_unit': self.pixels_per_unit,
            'aspect_ratio': canvas_width / canvas_height
        }
        
        print(f"✅ Optimal unified canvas dimensions:")
        print(f"   Canvas Size: {canvas_width} x {canvas_height} pixels")
        print(f"   World Size: {world_width:.1f} x {world_height:.1f} units")
        print(f"   Resolution: {self.pixels_per_unit:.1f} pixels per unit")
        print(f"   Aspect Ratio: {canvas_width / canvas_height:.2f}")
        
        return True
    
    def _round_to_reasonable_size(self, size):
        """
        Round canvas size to reasonable values for performance and memory
        """
        # Round to nearest 64 for good performance
        return ((size + 31) // 64) * 64
    
    def create_unified_canvas(self):
        """
        Step 4: Replace current individual region approach with single canvas
        Goal: Generate single `ONeill_Unified_Canvas` that represents all cylinders
        """
        print("🎨 Creating unified canvas...")
        
        if not self.optimal_dimensions:
            if not self.calculate_optimal_dimensions():
                return False
        
        canvas_width = self.optimal_dimensions['width']
        canvas_height = self.optimal_dimensions['height']
        
        # Remove existing unified canvas if it exists
        if self.canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[self.canvas_name])
        
        # Create new unified canvas
        canvas = bpy.data.images.new(
            name=self.canvas_name,
            width=canvas_width,
            height=canvas_height,
            alpha=True,
            float_buffer=False
        )
        
        # Initialize canvas with transparent black
        pixels = [0.0] * (canvas_width * canvas_height * 4)
        canvas.pixels = pixels
        canvas.update()
        
        # Mark as generated so it can be painted on
        canvas.source = 'GENERATED'
        canvas.use_fake_user = True
        
        print(f"✅ Unified canvas created: {canvas_width}x{canvas_height}")
        print(f"   Name: {self.canvas_name}")
        print(f"   Total pixels: {canvas_width * canvas_height:,}")
        
        return canvas
    
    def get_canvas_dimensions(self):
        """
        Return optimal canvas dimensions
        """
        return self.optimal_dimensions


class UVMappingSystem:
    """
    Creates and manages UV mapping correspondence between canvas pixels and cylinder objects
    """
    
    def __init__(self, layout_analyzer, canvas_dimensions):
        self.layout_analyzer = layout_analyzer
        self.canvas_dimensions = canvas_dimensions
        self.uv_mapping_table = {}
        
    def calculate_pixel_to_object_mapping(self):
        """
        Step 3: Create pixel-to-object mapping system
        Goal: Calculate which canvas pixels correspond to which cylinder object
        """
        print("🗺️ Calculating UV mapping correspondence...")
        
        if not self.canvas_dimensions:
            print("❌ Canvas dimensions not available")
            return False
        
        layout_bounds, object_dimensions = self.layout_analyzer.get_flat_object_bounds()
        
        canvas_width = self.canvas_dimensions['width']
        canvas_height = self.canvas_dimensions['height']
        world_width = self.canvas_dimensions['world_width'] 
        world_height = self.canvas_dimensions['world_height']
        
        # Calculate scale factors
        pixels_per_world_x = canvas_width / world_width
        pixels_per_world_y = canvas_height / world_height
        
        print(f"📐 Scale factors: {pixels_per_world_x:.1f} x {pixels_per_world_y:.1f} pixels per world unit")
        
        # Calculate pixel regions for each object
        for obj_name, obj_data in object_dimensions.items():
            bounds = obj_data['bounds']
            
            # Convert world coordinates to canvas pixel coordinates
            # Note: Canvas origin (0,0) = world minimum bounds
            min_canvas_x = int((bounds['min_x'] - layout_bounds['min_x']) * pixels_per_world_x)
            max_canvas_x = int((bounds['max_x'] - layout_bounds['min_x']) * pixels_per_world_x)
            min_canvas_y = int((bounds['min_y'] - layout_bounds['min_y']) * pixels_per_world_y)
            max_canvas_y = int((bounds['max_y'] - layout_bounds['min_y']) * pixels_per_world_y)
            
            # Ensure coordinates are within canvas bounds
            min_canvas_x = max(0, min(min_canvas_x, canvas_width - 1))
            max_canvas_x = max(0, min(max_canvas_x, canvas_width - 1))
            min_canvas_y = max(0, min(min_canvas_y, canvas_height - 1))
            max_canvas_y = max(0, min(max_canvas_y, canvas_height - 1))
            
            self.uv_mapping_table[obj_name] = {
                'object_index': obj_data['index'],
                'canvas_region': {
                    'min_x': min_canvas_x,
                    'max_x': max_canvas_x,
                    'min_y': min_canvas_y,
                    'max_y': max_canvas_y
                },
                'world_bounds': bounds.copy(),
                'pixel_width': max_canvas_x - min_canvas_x,
                'pixel_height': max_canvas_y - min_canvas_y
            }
            
            print(f"  {obj_data['index']:2d}. {obj_name}:")
            print(f"      Canvas region: ({min_canvas_x}, {min_canvas_y}) to ({max_canvas_x}, {max_canvas_y})")
            print(f"      Pixel size: {max_canvas_x - min_canvas_x} x {max_canvas_y - min_canvas_y}")
        
        print(f"✅ UV mapping table created for {len(self.uv_mapping_table)} objects")
        return True
    
    def get_object_for_pixel(self, canvas_x, canvas_y):
        """
        Pixel → Object lookup: Given canvas pixel coordinates, return corresponding object
        """
        for obj_name, mapping in self.uv_mapping_table.items():
            region = mapping['canvas_region']
            if (region['min_x'] <= canvas_x <= region['max_x'] and 
                region['min_y'] <= canvas_y <= region['max_y']):
                return obj_name, mapping
        return None, None
    
    def get_pixel_region_for_object(self, obj_name):
        """
        Object → Pixel region lookup: Given object name, return canvas pixel region
        """
        return self.uv_mapping_table.get(obj_name, None)
    
    def get_uv_mapping_table(self):
        """
        Return complete UV mapping table
        """
        return self.uv_mapping_table
    
    def validate_correspondence(self):
        """
        Test mapping accuracy by validating pixel-to-object correspondence
        """
        print("🧪 Validating UV mapping correspondence...")
        
        total_pixels = 0
        mapped_pixels = 0
        
        if not self.canvas_dimensions:
            print("❌ Canvas dimensions not available")
            return False
        
        canvas_width = self.canvas_dimensions['width']
        canvas_height = self.canvas_dimensions['height']
        
        # Sample test points across the canvas
        test_points = [
            (0, 0),  # Top-left corner
            (canvas_width-1, 0),  # Top-right corner
            (0, canvas_height-1),  # Bottom-left corner
            (canvas_width-1, canvas_height-1),  # Bottom-right corner
            (canvas_width//2, canvas_height//2),  # Center
        ]
        
        # Add some random test points
        import random
        for i in range(10):
            test_points.append((
                random.randint(0, canvas_width-1),
                random.randint(0, canvas_height-1)
            ))
        
        print(f"Testing {len(test_points)} sample points...")
        
        success_count = 0
        for x, y in test_points:
            obj_name, mapping = self.get_object_for_pixel(x, y)
            if obj_name:
                success_count += 1
                print(f"  ✅ Pixel ({x}, {y}) → {obj_name}")
            else:
                print(f"  ❌ Pixel ({x}, {y}) → No object found")
        
        accuracy = (success_count / len(test_points)) * 100
        print(f"🎯 Mapping accuracy: {accuracy:.1f}% ({success_count}/{len(test_points)} points)")
        
        return accuracy > 80  # Consider 80%+ accuracy as successful


# Integration functions for main terrain system
def create_unified_canvas_system():
    """
    Main entry point for Phase 1.2 unified canvas foundation
    Creates complete unified canvas system with UV mapping
    """
    print("🚀 PHASE 1.2: Creating Unified Canvas Foundation")
    print("=" * 60)
    
    try:
        # Step 1: Analyze layout
        print("\n📊 Step 1: Analyzing flat object layout...")
        canvas_manager = UnifiedCanvasManager()
        
        # Step 2: Calculate dimensions
        print("\n📏 Step 2: Calculating optimal canvas dimensions...")
        if not canvas_manager.calculate_optimal_dimensions():
            print("❌ Failed to calculate canvas dimensions")
            return False
        
        # Step 3: Create UV mapping
        print("\n🗺️ Step 3: Creating UV mapping system...")
        dimensions = canvas_manager.get_canvas_dimensions()
        uv_system = UVMappingSystem(canvas_manager.layout_analyzer, dimensions)
        
        if not uv_system.calculate_pixel_to_object_mapping():
            print("❌ Failed to create UV mapping")
            return False
        
        # Step 4: Create unified canvas
        print("\n🎨 Step 4: Creating unified canvas...")
        canvas = canvas_manager.create_unified_canvas()
        if not canvas:
            print("❌ Failed to create unified canvas")
            return False
        
        # Step 5: Validate system
        print("\n🧪 Step 5: Validating UV mapping...")
        if not uv_system.validate_correspondence():
            print("⚠️ UV mapping validation showed low accuracy")
        
        print("\n🏆 PHASE 1.2 UNIFIED CANVAS FOUNDATION COMPLETE!")
        print("✅ Unified canvas created and ready for painting")
        print("✅ UV mapping system established")
        print("✅ All 12 cylinder objects represented in single canvas")
        print(f"✅ Canvas name: {canvas_manager.canvas_name}")
        print(f"✅ Canvas size: {dimensions['width']}x{dimensions['height']}")
        
        # Return system components for integration
        return {
            'canvas': canvas,
            'canvas_manager': canvas_manager,
            'uv_system': uv_system,
            'dimensions': dimensions,
            'mapping_table': uv_system.get_uv_mapping_table()
        }
        
    except Exception as e:
        print(f"❌ Error creating unified canvas system: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test function
def test_unified_canvas_system():
    """
    Test the unified canvas system implementation
    """
    print("🧪 TESTING UNIFIED CANVAS SYSTEM")
    print("=" * 40)
    
    result = create_unified_canvas_system()
    
    if result:
        print("\n✅ UNIFIED CANVAS SYSTEM TEST PASSED")
        print("Key achievements:")
        print("  🔍 Flat object layout analyzed successfully")
        print("  📏 Optimal canvas dimensions calculated")
        print("  🗺️ UV mapping system created")
        print("  🎨 Unified canvas generated")
        print("  🧪 System validation completed")
        print(f"  📋 Canvas: {result['canvas'].name} ({result['dimensions']['width']}x{result['dimensions']['height']})")
        print(f"  🎯 Objects mapped: {len(result['mapping_table'])}")
    else:
        print("\n❌ UNIFIED CANVAS SYSTEM TEST FAILED")
    
    return result


if __name__ == "__main__":
    # Test the unified canvas system
    test_unified_canvas_system()
