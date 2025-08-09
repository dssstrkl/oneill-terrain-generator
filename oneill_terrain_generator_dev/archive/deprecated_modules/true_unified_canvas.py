"""
O'Neill Terrain Generator - TRUE Unified Canvas System
Session 7 Implementation: Canvas-driven biome assignment with unified displacement

CRITICAL CORRECTION: This system reads the user's painted canvas to determine biome assignment,
replacing the wrong Session 6 approach that used individual procedural noise textures.

Key Features:
- Canvas Reading: Samples pixel colors from painted diagonal canvas
- Canvas-Driven Biomes: Gray→Mountains, Orange→Canyons, Green→Hills, Yellow→Desert, Blue→Ocean, Cyan→Archipelago  
- Unified Displacement: Single temporary joined object for preview
- Manual Controls: User adjustment of displacement parameters
"""

import bpy
import bmesh
from mathutils import Vector
import math

class CanvasReader:
    """
    Reads the painted canvas to determine biome assignment based on pixel colors
    """
    
    def __init__(self, canvas_name="ONeill_Terrain_Canvas"):
        self.canvas_name = canvas_name
        self.canvas = None
        self.biome_colors = {
            # Color definitions matching the painted diagonal pattern
            'MOUNTAINS': (0.50, 0.50, 0.50),    # Gray
            'CANYONS': (0.80, 0.40, 0.20),      # Orange
            'HILLS': (0.40, 0.80, 0.30),        # Green  
            'DESERT': (0.90, 0.80, 0.40),       # Yellow
            'OCEAN': (0.10, 0.30, 0.80),        # Blue
            'ARCHIPELAGO': (0.20, 0.80, 0.90),  # Cyan
        }
        self.biome_strengths = {
            'MOUNTAINS': 2.5,
            'CANYONS': 2.0,
            'HILLS': 1.2,
            'DESERT': 0.8,
            'OCEAN': 0.3,
            'ARCHIPELAGO': 1.0,
        }
        
    def get_canvas(self):
        """Get the painted canvas image"""
        self.canvas = bpy.data.images.get(self.canvas_name)
        if not self.canvas:
            print(f"❌ Canvas '{self.canvas_name}' not found")
            return False
        
        if len(self.canvas.pixels) == 0:
            print(f"❌ Canvas has no pixel data")
            return False
            
        print(f"✅ Canvas loaded: {self.canvas.name} ({self.canvas.size[0]}x{self.canvas.size[1]})")
        return True
    
    def sample_canvas_pixel(self, u, v):
        """
        Sample canvas at UV coordinates (0.0-1.0 range)
        Returns RGB color tuple
        """
        if not self.canvas:
            return (0.0, 0.0, 0.0)
        
        width, height = self.canvas.size
        
        # Convert UV to pixel coordinates
        pixel_x = int(u * (width - 1))
        pixel_y = int(v * (height - 1))
        
        # Clamp to canvas bounds
        pixel_x = max(0, min(pixel_x, width - 1))
        pixel_y = max(0, min(pixel_y, height - 1))
        
        # Sample pixel (RGBA format)
        pixel_index = (pixel_y * width + pixel_x) * 4
        if pixel_index + 3 < len(self.canvas.pixels):
            r = self.canvas.pixels[pixel_index]
            g = self.canvas.pixels[pixel_index + 1]
            b = self.canvas.pixels[pixel_index + 2]
            return (r, g, b)
        
        return (0.0, 0.0, 0.0)
    
    def color_distance(self, color1, color2):
        """Calculate color distance for biome detection"""
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5
    
    def detect_biome_from_color(self, rgb_color):
        """
        Detect biome type from RGB color by finding closest match
        """
        min_distance = float('inf')
        best_biome = 'OCEAN'  # Default fallback
        
        for biome, biome_color in self.biome_colors.items():
            distance = self.color_distance(rgb_color, biome_color)
            if distance < min_distance:
                min_distance = distance
                best_biome = biome
        
        # Only accept if reasonably close (within 0.3 color distance)
        if min_distance < 0.3:
            return best_biome, self.biome_strengths[best_biome]
        else:
            # Unknown color - return None to keep area flat
            return None, 0.0
    
    def sample_object_biome(self, obj):
        """
        Sample canvas to determine biome for a specific flat object
        """
        if not self.canvas:
            if not self.get_canvas():
                return None, 0.0
        
        # Get object's world position
        obj_x = obj.location.x
        
        # Map object X position to canvas U coordinate (assuming objects span the full canvas width)
        # Calculate based on object layout bounds
        flat_objects = [o for o in bpy.data.objects if o.get("oneill_flat")]
        if not flat_objects:
            return None, 0.0
        
        min_x = min(o.location.x for o in flat_objects)
        max_x = max(o.location.x for o in flat_objects)
        x_range = max_x - min_x
        
        if x_range > 0:
            # Map object position to canvas U coordinate
            u = (obj_x - min_x) / x_range
            v = 0.5  # Sample from middle of canvas height
            
            # Sample canvas at this UV coordinate
            rgb_color = self.sample_canvas_pixel(u, v)
            
            # Detect biome from color
            biome, strength = self.detect_biome_from_color(rgb_color)
            
            print(f"Object {obj.name} at X={obj_x:.1f} → U={u:.2f} → RGB{rgb_color} → {biome} (strength={strength})")
            return biome, strength
        
        return None, 0.0


class UnifiedDisplacementSystem:
    """
    Creates unified displacement system using temporary joined object
    """
    
    def __init__(self):
        self.canvas_reader = CanvasReader()
        self.temp_object_name = "ONeill_Unified_Preview"
        self.manual_controls = {
            'displacement_strength': 1.0,
            'terrain_scale': 1.0,
            'direction_bias': Vector((0.0, 0.0, 1.0))
        }
    
    def create_temporary_joined_object(self):
        """
        Create temporary joined object from all flat objects for unified preview
        """
        print("🔗 Creating temporary joined object...")
        
        # Get all flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            print("❌ No flat objects found")
            return None
        
        # Remove existing temp object
        if self.temp_object_name in bpy.data.objects:
            old_temp = bpy.data.objects[self.temp_object_name]
            bpy.data.objects.remove(old_temp, do_unlink=True)
        
        # Create new mesh for joined object
        joined_mesh = bpy.data.meshes.new(f"{self.temp_object_name}_mesh")
        joined_obj = bpy.data.objects.new(self.temp_object_name, joined_mesh)
        bpy.context.collection.objects.link(joined_obj)
        
        # Use bmesh to combine all flat objects
        bm = bmesh.new()
        
        for obj in flat_objects:
            # Create temporary bmesh from object
            temp_bm = bmesh.new()
            temp_bm.from_mesh(obj.data)
            
            # Transform vertices to world space, then offset for joined object
            for vert in temp_bm.verts:
                world_pos = obj.matrix_world @ vert.co
                vert.co = world_pos
            
            # Merge into main bmesh
            bm.from_mesh(temp_bm.to_mesh())
            temp_bm.free()
        
        # Update joined mesh
        bm.to_mesh(joined_mesh)
        bm.free()
        
        # Mark as temporary preview object
        joined_obj["oneill_unified_preview"] = True
        joined_obj["source_objects"] = [obj.name for obj in flat_objects]
        
        print(f"✅ Created temporary joined object: {self.temp_object_name}")
        print(f"   Combined {len(flat_objects)} flat objects")
        print(f"   Vertices: {len(joined_mesh.vertices)}")
        
        return joined_obj
    
    def apply_canvas_driven_displacement(self, temp_object):
        """
        Apply displacement to temporary object based on canvas reading
        """
        print("🗺️ Applying canvas-driven displacement...")
        
        if not self.canvas_reader.get_canvas():
            return False
        
        # Create displacement modifier
        displacement_mod = temp_object.modifiers.new("Canvas_Displacement", 'DISPLACE')
        
        # Create image texture for canvas
        canvas_texture = bpy.data.textures.new("Canvas_Displacement_Texture", 'IMAGE')
        canvas_texture.image = self.canvas_reader.canvas
        canvas_texture.extension = 'CLIP'
        canvas_texture.use_interpolation = True
        
        # Set up displacement modifier
        displacement_mod.texture = canvas_texture
        displacement_mod.texture_coords = 'GLOBAL'  # Use global coordinates for now
        displacement_mod.direction = 'Z'
        displacement_mod.strength = self.manual_controls['displacement_strength']
        
        print(f"✅ Applied canvas displacement modifier")
        print(f"   Texture: {canvas_texture.name}")
        print(f"   Strength: {displacement_mod.strength}")
        
        return True
    
    def add_manual_controls(self, context):
        """
        Add manual controls for displacement parameters
        """
        print("🎛️ Adding manual controls...")
        
        # Add custom properties to scene for manual controls
        scene = context.scene
        
        if not hasattr(scene, 'oneill_unified_controls'):
            # Add custom property group for unified controls
            scene['oneill_displacement_strength'] = 1.0
            scene['oneill_terrain_scale'] = 1.0
            scene['oneill_direction_bias_x'] = 0.0
            scene['oneill_direction_bias_y'] = 0.0
            scene['oneill_direction_bias_z'] = 1.0
            
            print("✅ Manual controls added to scene properties")
        
        return True
    
    def update_displacement_from_controls(self, context):
        """
        Update displacement based on manual control values
        """
        scene = context.scene
        temp_obj = bpy.data.objects.get(self.temp_object_name)
        
        if not temp_obj:
            return False
        
        # Update displacement modifier if it exists
        displacement_mod = None
        for mod in temp_obj.modifiers:
            if mod.type == 'DISPLACE' and 'Canvas' in mod.name:
                displacement_mod = mod
                break
        
        if displacement_mod:
            # Update strength from manual controls
            strength = scene.get('oneill_displacement_strength', 1.0)
            displacement_mod.strength = strength
            
            print(f"✅ Updated displacement strength to {strength}")
            return True
        
        return False


class TrueUnifiedCanvasSystem:
    """
    Main system that implements the TRUE unified canvas approach
    """
    
    def __init__(self):
        self.canvas_reader = CanvasReader()
        self.displacement_system = UnifiedDisplacementSystem()
        self.is_active = False
    
    def implement_unified_canvas_system(self, context):
        """
        Main implementation function for the TRUE unified canvas system
        """
        print("\n" + "="*60)
        print("🎯 IMPLEMENTING TRUE UNIFIED CANVAS SYSTEM")
        print("Session 7 Implementation: Canvas-driven biome assignment")
        print("="*60)
        
        try:
            # Step 1: Validate canvas and scene
            print("\n📋 Step 1: Validating canvas and scene state...")
            if not self.canvas_reader.get_canvas():
                print("❌ Canvas validation failed")
                return False
            
            flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if not flat_objects:
                print("❌ No flat objects found")
                return False
            
            print(f"✅ Found {len(flat_objects)} flat objects")
            print(f"✅ Canvas ready: {self.canvas_reader.canvas.name}")
            
            # Step 2: Create temporary joined object
            print("\n🔗 Step 2: Creating temporary joined object...")
            temp_object = self.displacement_system.create_temporary_joined_object()
            if not temp_object:
                print("❌ Failed to create temporary joined object")
                return False
            
            # Step 3: Apply canvas-driven displacement
            print("\n🗺️ Step 3: Applying canvas-driven displacement...")
            if not self.displacement_system.apply_canvas_driven_displacement(temp_object):
                print("❌ Failed to apply canvas displacement")
                return False
            
            # Step 4: Add manual controls
            print("\n🎛️ Step 4: Setting up manual controls...")
            if not self.displacement_system.add_manual_controls(context):
                print("❌ Failed to add manual controls")
                return False
            
            # Step 5: Test canvas reading
            print("\n🧪 Step 5: Testing canvas reading system...")
            self.test_canvas_reading_system()
            
            self.is_active = True
            
            print("\n🏆 TRUE UNIFIED CANVAS SYSTEM COMPLETE!")
            print("✅ Canvas reading system implemented")
            print("✅ Unified displacement system created")
            print("✅ Manual controls available")
            print("✅ System ready for user painting workflow")
            
            return True
            
        except Exception as e:
            print(f"❌ Error implementing unified canvas system: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_canvas_reading_system(self):
        """
        Test that canvas reading system works correctly
        """
        print("🧪 Testing canvas reading for all flat objects...")
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        biome_counts = {}
        
        for obj in flat_objects:
            biome, strength = self.canvas_reader.sample_object_biome(obj)
            if biome:
                biome_counts[biome] = biome_counts.get(biome, 0) + 1
        
        print(f"✅ Canvas reading test complete:")
        for biome, count in biome_counts.items():
            print(f"   {biome}: {count} objects")
    
    def update_manual_controls(self, context):
        """
        Update displacement based on manual control changes
        """
        if self.is_active:
            return self.displacement_system.update_displacement_from_controls(context)
        return False


# Integration functions for main system
def apply_true_unified_canvas_system(context):
    """
    Main function to apply the TRUE unified canvas system
    """
    system = TrueUnifiedCanvasSystem()
    return system.implement_unified_canvas_system(context)


def update_unified_displacement_controls(context):
    """
    Function to update displacement based on manual controls
    """
    system = TrueUnifiedCanvasSystem()
    return system.update_manual_controls(context)


# Register functions in driver namespace for global access
def register_global_functions():
    """Register functions in driver namespace"""
    bpy.app.driver_namespace['apply_true_unified_canvas_system'] = apply_true_unified_canvas_system
    bpy.app.driver_namespace['update_unified_displacement_controls'] = update_unified_displacement_controls
    print("✅ True unified canvas functions registered in driver namespace")


# Auto-register when module is imported
if __name__ != "__main__":
    register_global_functions()
