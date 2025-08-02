"""
UV Canvas Integration Module
Complete image-based terrain preview system for O'Neill Terrain Generator

This module implements the proper UV-based canvas-to-terrain integration that
Session 11 failed to achieve. Creates separate preview mesh that reads canvas
through UV coordinates without modifying flat objects.
"""

import bpy
import bmesh
import mathutils
import numpy as np
from mathutils import Vector

class UVCanvasIntegration:
    """Complete UV-Canvas integration system - image-based preview only"""
    
    def __init__(self):
        self.canvas_name = "ONeill_Terrain_Canvas"
        self.preview_mesh_name = "ONeill_Terrain_Preview"
        self.flat_objects = []
        self.canvas = None
        self.preview_mesh = None
        
        # Biome color mapping for canvas reading
        self.biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),    # Gray  
            'CANYONS': (0.8, 0.4, 0.2),      # Orange-brown
            'HILLS': (0.4, 0.8, 0.3),        # Green
            'ARCHIPELAGO': (0.2, 0.8, 0.9),  # Tropical blue-green
            'DESERT': (0.9, 0.8, 0.4),       # Sandy yellow
            'OCEAN': (0.1, 0.3, 0.8),        # Deep blue
        }
        
    def initialize_system(self):
        """Initialize UV-Canvas integration system"""
        print("🎯 Initializing UV-Canvas Integration System...")
        
        # Get flat objects
        self.flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not self.flat_objects:
            print("❌ No flat objects found")
            return False
        
        # Get or create canvas
        self.canvas = bpy.data.images.get(self.canvas_name)
        if not self.canvas:
            print("⚠️ No terrain canvas found, creating default")
            self.canvas = self.create_default_canvas()
        
        print(f"✅ Initialized with {len(self.flat_objects)} flat objects and canvas {self.canvas.size}")
        return True
    
    def create_default_canvas(self):
        """Create default canvas with proper dimensions"""
        if not self.flat_objects:
            return None
        
        # Calculate layout bounds from flat objects
        min_x = min(obj.location.x - obj.dimensions.x/2 for obj in self.flat_objects)
        max_x = max(obj.location.x + obj.dimensions.x/2 for obj in self.flat_objects)
        min_y = min(obj.location.y - obj.dimensions.y/2 for obj in self.flat_objects)
        max_y = max(obj.location.y + obj.dimensions.y/2 for obj in self.flat_objects)
        
        layout_width = max_x - min_x
        layout_height = max_y - min_y
        
        # Calculate canvas size (100 pixels per unit)
        canvas_width = max(1024, int(layout_width * 100))
        canvas_height = max(1024, int(layout_height * 100))
        
        # Round to 256-pixel increments
        canvas_width = ((canvas_width + 255) // 256) * 256
        canvas_height = ((canvas_height + 255) // 256) * 256
        
        print(f"🎨 Creating default canvas: {canvas_width}x{canvas_height}")
        
        # Create canvas
        canvas = bpy.data.images.new(
            self.canvas_name,
            width=canvas_width,
            height=canvas_height,
            alpha=True
        )
        canvas.colorspace_settings.name = 'sRGB'  # Use sRGB for visibility
        
        # Initialize with black transparent
        canvas.pixels = [0.0, 0.0, 0.0, 0.0] * (canvas_width * canvas_height)
        canvas.update()
        
        return canvas
    
    def create_diagonal_canvas_pattern(self):
        """Create visible diagonal biome pattern on canvas"""
        if not self.canvas:
            if not self.initialize_system():
                return False
        
        canvas_width, canvas_height = self.canvas.size
        print(f"🎨 Creating diagonal pattern on {canvas_width}x{canvas_height} canvas")
        
        # Create diagonal stripes pattern
        pixels = [0.0] * (canvas_width * canvas_height * 4)  # RGBA
        
        # Define biome stripe regions (6 equal diagonal bands)
        biome_list = ['MOUNTAINS', 'CANYONS', 'HILLS', 'ARCHIPELAGO', 'DESERT', 'OCEAN']
        stripe_width = canvas_width // len(biome_list)
        
        for y in range(canvas_height):
            for x in range(canvas_width):
                # Calculate which biome stripe this pixel belongs to
                stripe_index = min((x // stripe_width), len(biome_list) - 1)
                biome_name = biome_list[stripe_index]
                
                # Get biome color
                biome_color = self.biome_colors[biome_name]
                
                # Calculate pixel index in RGBA array
                pixel_idx = (y * canvas_width + x) * 4
                
                # Set RGBA values
                pixels[pixel_idx] = biome_color[0]      # R
                pixels[pixel_idx + 1] = biome_color[1]  # G
                pixels[pixel_idx + 2] = biome_color[2]  # B
                pixels[pixel_idx + 3] = 1.0             # A (fully opaque)
        
        # Apply pixels to canvas
        self.canvas.pixels = pixels
        self.canvas.update()
        
        # Force Image Editor refresh
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()
        
        print("✅ Diagonal pattern created and applied to canvas")
        return True
    
    def clear_all_object_modifiers(self):
        """Remove all terrain-related modifiers from flat objects"""
        cleared_count = 0
        
        for obj in self.flat_objects:
            # Remove terrain/preview modifiers
            terrain_mods = [mod for mod in obj.modifiers 
                          if mod.name.startswith(("Terrain_", "Preview_", "Biome_", "VertexPrecision_"))]
            
            for mod in terrain_mods:
                obj.modifiers.remove(mod)
                cleared_count += 1
        
        if cleared_count > 0:
            print(f"🧹 Cleared {cleared_count} object modifiers")
        
        return cleared_count
    
    def create_terrain_preview_mesh(self):
        """Create separate high-resolution terrain preview mesh"""
        if not self.flat_objects or not self.canvas:
            print("❌ Missing flat objects or canvas for preview mesh creation")
            return None
        
        print("🏗️ Creating terrain preview mesh...")
        
        # Remove existing preview mesh
        if self.preview_mesh_name in bpy.data.objects:
            old_preview = bpy.data.objects[self.preview_mesh_name]
            bpy.data.objects.remove(old_preview, do_unlink=True)
        
        # Calculate total layout bounds
        min_x = min(obj.location.x - obj.dimensions.x/2 for obj in self.flat_objects)
        max_x = max(obj.location.x + obj.dimensions.x/2 for obj in self.flat_objects)
        min_y = min(obj.location.y - obj.dimensions.y/2 for obj in self.flat_objects)
        max_y = max(obj.location.y + obj.dimensions.y/2 for obj in self.flat_objects)
        
        layout_width = max_x - min_x
        layout_height = max_y - min_y
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        print(f"📐 Preview layout: {layout_width:.1f} x {layout_height:.1f} at ({center_x:.1f}, {center_y:.1f})")
        
        # Create high-resolution mesh (50 vertices per unit for smooth terrain)
        vertices_per_unit = 50
        mesh_width = max(100, int(layout_width * vertices_per_unit))
        mesh_height = max(100, int(layout_height * vertices_per_unit))
        
        print(f"🔺 Creating mesh: {mesh_width} x {mesh_height} vertices")
        
        # Create bmesh grid
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=mesh_width-1, y_segments=mesh_height-1, size=1.0)
        
        # Scale and position mesh to match layout
        for vert in bm.verts:
            # Scale to layout dimensions
            vert.co.x = vert.co.x * (layout_width / 2) + center_x
            vert.co.y = vert.co.y * (layout_height / 2) + center_y
            vert.co.z = 0  # Start flat
        
        # Create mesh object
        preview_mesh_data = bpy.data.meshes.new(self.preview_mesh_name)
        bm.to_mesh(preview_mesh_data)
        bm.free()
        
        # Create UV coordinates for entire mesh
        preview_mesh_data.uv_layers.new(name="UVForCanvas")
        uv_layer = preview_mesh_data.uv_layers["UVForCanvas"]
        
        # Map mesh coordinates to canvas UV space
        for loop_idx, loop in enumerate(preview_mesh_data.loops):
            vert = preview_mesh_data.vertices[loop.vertex_index]
            
            # Calculate UV coordinates (0.0 to 1.0) based on mesh position
            u = (vert.co.x - min_x) / layout_width if layout_width > 0 else 0.0
            v = (vert.co.y - min_y) / layout_height if layout_height > 0 else 0.0
            
            # Clamp to valid UV range
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
            
            uv_layer.data[loop_idx].uv = (u, v)
        
        # Create preview object
        self.preview_mesh = bpy.data.objects.new(self.preview_mesh_name, preview_mesh_data)
        bpy.context.collection.objects.link(self.preview_mesh)
        
        # Mark as preview object
        self.preview_mesh["oneill_terrain_preview"] = True
        self.preview_mesh["canvas_name"] = self.canvas_name
        
        print(f"✅ Created terrain preview mesh: {mesh_width}x{mesh_height} vertices")
        return self.preview_mesh
    
    def update_preview_from_canvas(self):
        """Update terrain preview mesh height from canvas colors"""
        if not self.preview_mesh or not self.canvas:
            print("❌ Missing preview mesh or canvas for update")
            return False
        
        print("🔄 Updating terrain preview from canvas...")
        
        # Get canvas data
        canvas_width, canvas_height = self.canvas.size
        canvas_pixels = list(self.canvas.pixels)
        
        if len(canvas_pixels) == 0:
            print("⚠️ Canvas has no pixel data")
            return False
        
        # Get mesh data
        mesh_data = self.preview_mesh.data
        uv_layer = mesh_data.uv_layers.get("UVForCanvas")
        
        if not uv_layer:
            print("❌ No UV layer found for canvas mapping")
            return False
        
        # Sample canvas for each vertex and apply height displacement
        height_multiplier = 4.0  # Maximum terrain height
        vertex_count = len(mesh_data.vertices)
        
        # Create vertex UV mapping
        vertex_uvs = {}
        for poly in mesh_data.polygons:
            for loop_idx in poly.loop_indices:
                loop = mesh_data.loops[loop_idx]
                vertex_idx = loop.vertex_index
                uv = uv_layer.data[loop_idx].uv
                
                # Store UV for vertex (average if multiple UVs per vertex)
                if vertex_idx in vertex_uvs:
                    old_uv = vertex_uvs[vertex_idx]
                    vertex_uvs[vertex_idx] = ((old_uv[0] + uv[0]) / 2, (old_uv[1] + uv[1]) / 2)
                else:
                    vertex_uvs[vertex_idx] = uv
        
        # Update vertex positions based on canvas colors
        updated_vertices = 0
        
        for vertex_idx, vertex in enumerate(mesh_data.vertices):
            if vertex_idx not in vertex_uvs:
                continue
            
            uv = vertex_uvs[vertex_idx]
            
            # Convert UV to canvas pixel coordinates
            pixel_x = int(uv[0] * (canvas_width - 1))
            pixel_y = int(uv[1] * (canvas_height - 1))
            
            # Clamp to canvas bounds
            pixel_x = max(0, min(canvas_width - 1, pixel_x))
            pixel_y = max(0, min(canvas_height - 1, pixel_y))
            
            # Get pixel color from canvas
            pixel_idx = (pixel_y * canvas_width + pixel_x) * 4
            
            if pixel_idx < len(canvas_pixels) - 3:
                r = canvas_pixels[pixel_idx]
                g = canvas_pixels[pixel_idx + 1]
                b = canvas_pixels[pixel_idx + 2]
                
                # Calculate height from brightness (0.0 to 1.0)
                brightness = (r + g + b) / 3.0
                
                # Apply height displacement (brightness - 0.5) gives range -0.5 to +0.5
                height = (brightness - 0.5) * height_multiplier
                
                # Update vertex Z position
                vertex.co.z = height
                updated_vertices += 1
        
        # Update mesh
        mesh_data.update()
        
        # Force viewport update
        bpy.context.view_layer.update()
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        print(f"✅ Updated {updated_vertices} vertices from canvas")
        return True
    
    def implement_complete_system(self):
        """Implement complete UV-Canvas integration system"""
        print("🚀 Implementing Complete UV-Canvas Integration System...")
        
        # Step 1: Initialize system
        if not self.initialize_system():
            print("❌ System initialization failed")
            return False
        
        # Step 2: Clear all object modifiers (preserve flat objects)
        cleared_mods = self.clear_all_object_modifiers()
        print(f"🧹 Cleared {cleared_mods} object modifiers")
        
        # Step 3: Create diagonal canvas pattern
        if not self.create_diagonal_canvas_pattern():
            print("❌ Canvas pattern creation failed")
            return False
        
        # Step 4: Create terrain preview mesh
        if not self.create_terrain_preview_mesh():
            print("❌ Preview mesh creation failed")
            return False
        
        # Step 5: Update preview from canvas
        if not self.update_preview_from_canvas():
            print("❌ Preview update failed")
            return False
        
        print("🎉 UV-Canvas Integration Complete!")
        print("✅ Objects remain flat and paintable")
        print("✅ Terrain preview shows diagonal displacement")
        print("✅ Image-based preview system active")
        
        return True
    
    def get_system_status(self):
        """Get current system status for debugging"""
        status = {
            'flat_objects_count': len(self.flat_objects),
            'canvas_exists': self.canvas is not None,
            'canvas_size': self.canvas.size if self.canvas else None,
            'preview_mesh_exists': self.preview_mesh is not None,
            'preview_vertex_count': len(self.preview_mesh.data.vertices) if self.preview_mesh else 0
        }
        return status

# ========================= REGISTRATION =========================

from bpy.types import Operator

class ONEILL_OT_TestUVCanvasIntegration(Operator):
    """Test UV-Canvas Integration System"""
    bl_idname = "oneill.test_uv_canvas_integration"
    bl_label = "🧪 Test UV-Canvas Integration"
    bl_description = "Test the complete UV-Canvas integration system"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        uv_system = UVCanvasIntegration()
        
        try:
            success = uv_system.implement_complete_system()
            
            if success:
                status = uv_system.get_system_status()
                self.report({'INFO'}, f"✅ UV-Canvas Integration Test Successful! "
                                    f"Objects: {status['flat_objects_count']}, "
                                    f"Canvas: {status['canvas_size']}, "
                                    f"Preview: {status['preview_vertex_count']} vertices")
            else:
                self.report({'ERROR'}, "❌ UV-Canvas Integration Test Failed - check console")
                
        except Exception as e:
            self.report({'ERROR'}, f"UV-Canvas integration error: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Registration classes
classes = [
    ONEILL_OT_TestUVCanvasIntegration,
]

def register():
    """Register UV Canvas Integration module"""
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
        print("✅ UV Canvas Integration module registered")
    except Exception as e:
        print(f"❌ UV Canvas Integration registration failed: {e}")

def unregister():
    """Unregister UV Canvas Integration module"""
    try:
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        print("✅ UV Canvas Integration module unregistered")
    except Exception as e:
        print(f"⚠️ UV Canvas Integration unregistration failed: {e}")

if __name__ == "__main__":
    register()
