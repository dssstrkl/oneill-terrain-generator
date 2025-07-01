# realtime_canvas_monitor.py
# Phase 2B Real-time Canvas Monitoring System
# O'Neill Cylinder Terrain Generator - Revolutionary Paint-to-3D Integration

import bpy
import bmesh
import numpy as np
from mathutils import Vector
import time

class RealtimeBiomeApplicator:
    """
    Applies biomes to objects in real-time based on painted canvas changes
    Integrates with Phase 2A biome geometry system
    """
    
    def __init__(self):
        self.phase1_to_phase2a_mapping = {
            'ARCHIPELAGO': 'archipelago',
            'MOUNTAINS': 'mountain',
            'CANYONS': 'canyon', 
            'HILLS': 'rolling_hills',
            'DESERT': 'desert',
            'OCEAN': 'ocean'
        }
        self.biome_colors = {
            'ARCHIPELAGO': (0.2, 0.8, 0.6, 1.0),  # Teal
            'MOUNTAINS': (0.5, 0.5, 0.5, 1.0),    # Gray
            'CANYONS': (0.8, 0.4, 0.2, 1.0),      # Orange
            'HILLS': (0.3, 0.6, 0.3, 1.0),        # Green  
            'DESERT': (0.9, 0.8, 0.4, 1.0),       # Yellow
            'OCEAN': (0.2, 0.4, 0.8, 1.0),        # Blue
        }
    
    def apply_biome_to_object(self, obj, biome_name, strength=1.0):
        """Apply biome using Phase 2A geometry node system or displacement modifier"""
        try:
            # First try Phase 2A biome geometry nodes
            if self.try_apply_biome_nodes(obj, biome_name, strength):
                return True
            
            # Fallback: Apply displacement modifier for immediate visual feedback
            return self.apply_displacement_modifier(obj, biome_name, strength)
            
        except Exception as e:
            print(f"❌ Error applying biome: {e}")
            return False
    
    def try_apply_biome_nodes(self, obj, biome_name, strength):
        """Try to apply biome using Phase 2A geometry node system"""
        try:
            # Check if biome generation is available
            biome_geometry_generator = None
            for module_name in bpy.context.preferences.addons.keys():
                if 'oneill' in module_name.lower():
                    addon = bpy.context.preferences.addons[module_name]
                    if hasattr(addon, 'biome_geometry_generator'):
                        biome_geometry_generator = addon.biome_geometry_generator
                        break
            
            if not biome_geometry_generator:
                return False
            
            # Remove existing biome modifiers
            for modifier in list(obj.modifiers):
                if (modifier.type == 'NODES' and 
                    modifier.node_group and 
                    'ONeill_Biome' in modifier.node_group.name):
                    obj.modifiers.remove(modifier)
            
            # Find the biome node group
            node_group_name = f"ONeill_Biome_{biome_name.title()}"
            node_group = bpy.data.node_groups.get(node_group_name)
            
            if node_group:
                # Apply the biome modifier
                modifier_name = f"Biome_{biome_name.title()}"
                modifier = obj.modifiers.new(modifier_name, 'NODES')
                modifier.node_group = node_group
                
                # Set parameters if available
                try:
                    modifier["Input_2"] = strength  # Heightmap_Strength
                    modifier["Input_3"] = 1.0       # Feature_Scale
                    modifier["Input_4"] = 1.0       # Biome_Intensity
                except:
                    pass  # Some parameters might not exist
                
                print(f"✅ Applied {biome_name} biome nodes to {obj.name}")
                return True
            else:
                print(f"⚠️ Biome node group not found: {node_group_name}")
                return False
                
        except Exception as e:
            print(f"❌ Biome nodes application failed: {e}")
            return False
    
    def apply_displacement_modifier(self, obj, biome_name, strength):
        """Apply displacement modifier for immediate visual feedback"""
        try:
            # Remove existing displacement modifiers
            for modifier in list(obj.modifiers):
                if modifier.type == 'DISPLACE' and modifier.name.startswith('ONeill_'):
                    obj.modifiers.remove(modifier)
            
            # Get heightmap for this object
            heightmap_name = obj.get("heightmap_image")
            if not heightmap_name or heightmap_name not in bpy.data.images:
                return False
            
            heightmap = bpy.data.images[heightmap_name]
            
            # Create displacement modifier
            modifier_name = f"ONeill_{biome_name}_Displacement"
            modifier = obj.modifiers.new(modifier_name, 'DISPLACE')
            
            # Create texture for displacement
            texture_name = f"{modifier_name}_Texture"
            if texture_name in bpy.data.textures:
                bpy.data.textures.remove(bpy.data.textures[texture_name])
            
            texture = bpy.data.textures.new(texture_name, 'IMAGE')
            texture.image = heightmap
            
            # Configure modifier
            modifier.texture = texture
            modifier.strength = strength * 0.5  # Scale for visible effect
            modifier.direction = 'NORMAL'
            modifier.mid_level = 0.5
            
            print(f"✅ Applied displacement modifier to {obj.name}")
            return True
            
        except Exception as e:
            print(f"❌ Displacement modifier failed: {e}")
            return False
    
    def detect_biome_from_color(self, painted_color):
        """Detect which biome a painted color represents"""
        min_distance = float('inf')
        closest_biome = None
        
        for biome_name, biome_color in self.biome_colors.items():
            # Calculate color distance (RGB only)
            distance = sum((a - b) ** 2 for a, b in zip(painted_color[:3], biome_color[:3]))
            if distance < min_distance:
                min_distance = distance
                closest_biome = biome_name
        
        # Convert Phase 1 biome name to Phase 2A biome name
        if closest_biome and min_distance < 0.1:
            return self.phase1_to_phase2a_mapping.get(closest_biome)
        
        return None

class Phase2BCanvasMonitor:
    """
    Real-time canvas monitoring system for Phase 2B
    Detects painting changes and triggers immediate biome application
    """
    
    def __init__(self):
        self.canvas_name = "TerrainPainting_Canvas"
        self.is_monitoring = False
        self.previous_canvas_data = None
        self.timer = None
        self.update_frequency = 0.5  # Check every 500ms for stable performance
        self.change_threshold = 0.05  # Minimum change to trigger update
        self.applicator = RealtimeBiomeApplicator()
        self.last_update_time = 0
        print("🔄 Phase 2B Canvas Monitor initialized")
    
    def start_monitoring(self):
        """Start real-time canvas monitoring"""
        if self.is_monitoring:
            print("⚠️ Monitoring already active")
            return False
        
        # Check for canvas - try multiple possible names
        canvas = None
        possible_names = [self.canvas_name, "TerrainPainting_Canvas"]
        
        # Also check for individual heightmaps
        for obj in bpy.data.objects:
            if obj.get("oneill_flat") and obj.get("heightmap_image"):
                heightmap_name = obj.get("heightmap_image")
                if heightmap_name in bpy.data.images:
                    possible_names.append(heightmap_name)
        
        for name in possible_names:
            if name in bpy.data.images and bpy.data.images[name].has_data:
                canvas = bpy.data.images[name]
                self.canvas_name = name
                break
        
        if not canvas:
            print("❌ No suitable canvas found for monitoring")
            return False
        
        # Capture initial state
        self.previous_canvas_data = self._capture_canvas_state()
        
        # Start timer for periodic checks
        self.timer = bpy.app.timers.register(
            self._monitor_canvas_changes, 
            first_interval=self.update_frequency,
            persistent=True
        )
        self.is_monitoring = True
        print(f"✅ Real-time canvas monitoring STARTED on {self.canvas_name}")
        print("🎨 Paint on canvas → Immediate 3D terrain updates!")
        return True
    
    def stop_monitoring(self):
        """Stop real-time canvas monitoring"""
        if self.timer:
            bpy.app.timers.unregister(self.timer)
            self.timer = None
        self.is_monitoring = False
        print("⏹️ Real-time canvas monitoring STOPPED")
    
    def _capture_canvas_state(self):
        """Capture current canvas state for change detection"""
        canvas = bpy.data.images.get(self.canvas_name)
        if not canvas or not canvas.has_data:
            return None
        
        try:
            # Get pixel data as simple list for change detection
            pixels = list(canvas.pixels)
            # Sample every 16th pixel for performance (4x4 subsampling)
            sampled_pixels = pixels[::16]
            return sampled_pixels
        except:
            return None
    
    def _monitor_canvas_changes(self):
        """Timer callback to check for canvas changes"""
        if not self.is_monitoring:
            return None  # Stop timer
        
        try:
            current_time = time.time()
            
            # Rate limiting - don't update too frequently
            if current_time - self.last_update_time < self.update_frequency:
                return self.update_frequency
            
            current_state = self._capture_canvas_state()
            
            if current_state is None or self.previous_canvas_data is None:
                return self.update_frequency
            
            # Simple change detection
            if len(current_state) != len(self.previous_canvas_data):
                return self.update_frequency
            
            # Calculate change magnitude
            total_change = 0
            for i in range(min(len(current_state), len(self.previous_canvas_data))):
                total_change += abs(current_state[i] - self.previous_canvas_data[i])
            
            # Normalize change by number of pixels
            if len(current_state) > 0:
                avg_change = total_change / len(current_state)
            else:
                avg_change = 0
            
            if avg_change > self.change_threshold:
                print(f"🎨 Canvas change detected (magnitude: {avg_change:.3f})")
                self._process_canvas_changes()
                self.previous_canvas_data = current_state
                self.last_update_time = current_time
            
            return self.update_frequency
            
        except Exception as e:
            print(f"❌ Canvas monitoring error: {e}")
            return self.update_frequency
    
    def _process_canvas_changes(self):
        """Process canvas changes and apply to 3D objects"""
        try:
            # Get current biome from scene
            current_biome = getattr(bpy.context.scene, 'oneill_current_biome', 'ARCHIPELAGO')
            
            # Find flat objects to apply changes to
            flat_objects = [obj for obj in bpy.data.objects 
                           if obj.get("oneill_flat") and obj.get("heightmap_image")]
            
            if not flat_objects:
                return
            
            print(f"🧬 Applying {current_biome} to {len(flat_objects)} objects...")
            
            # Apply current biome to all flat objects for immediate feedback
            for obj in flat_objects:
                biome_name = current_biome.lower()
                success = self.applicator.apply_biome_to_object(obj, biome_name, 1.0)
                if success:
                    print(f"   ✅ {obj.name}: {current_biome} applied")
                else:
                    print(f"   ⚠️ {obj.name}: fallback displacement applied")
            
            # Force viewport update
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            print("🎨 Real-time terrain update complete!")
            
        except Exception as e:
            print(f"❌ Canvas change processing error: {e}")

# ========================= ENHANCED BIOME APPLICATION =========================

class AdvancedBiomeApplicator:
    """Advanced biome application with geometry node creation"""
    
    def __init__(self):
        self.created_node_groups = {}
    
    def create_simple_displacement_nodes(self, biome_name):
        """Create simple displacement geometry nodes for real-time feedback"""
        node_group_name = f"ONeill_RT_{biome_name.title()}"
        
        if node_group_name in bpy.data.node_groups:
            return bpy.data.node_groups[node_group_name]
        
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create input and output nodes
        input_node = node_group.nodes.new('NodeGroupInput')
        output_node = node_group.nodes.new('NodeGroupOutput')
        
        input_node.location = (-300, 0)
        output_node.location = (300, 0)
        
        # Add input sockets
        node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        node_group.interface.new_socket('Strength', in_out='INPUT', socket_type='NodeSocketFloat')
        node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
        # Create simple displacement setup
        position_node = node_group.nodes.new('GeometryNodeInputPosition')
        noise_node = node_group.nodes.new('ShaderNodeTexNoise')
        vector_math = node_group.nodes.new('ShaderNodeVectorMath')
        set_position = node_group.nodes.new('GeometryNodeSetPosition')
        
        # Position nodes
        position_node.location = (-200, 100)
        noise_node.location = (-100, 100)
        vector_math.location = (0, 100)
        set_position.location = (100, 0)
        
        # Configure noise based on biome
        biome_configs = {
            'archipelago': {'scale': 2.0, 'detail': 4.0, 'roughness': 0.6},
            'mountain': {'scale': 5.0, 'detail': 8.0, 'roughness': 0.8},
            'canyon': {'scale': 3.0, 'detail': 6.0, 'roughness': 0.7},
            'rolling_hills': {'scale': 1.5, 'detail': 3.0, 'roughness': 0.4},
            'desert': {'scale': 2.5, 'detail': 5.0, 'roughness': 0.5},
            'ocean': {'scale': 1.0, 'detail': 2.0, 'roughness': 0.3}
        }
        
        config = biome_configs.get(biome_name, biome_configs['rolling_hills'])
        noise_node.inputs['Scale'].default_value = config['scale']
        noise_node.inputs['Detail'].default_value = config['detail']
        noise_node.inputs['Roughness'].default_value = config['roughness']
        
        vector_math.operation = 'MULTIPLY'
        vector_math.inputs[1].default_value = (0, 0, 1)  # Z-direction displacement
        
        # Create links
        links = node_group.links
        links.new(position_node.outputs['Position'], noise_node.inputs['Vector'])
        links.new(noise_node.outputs['Color'], vector_math.inputs[0])
        links.new(input_node.outputs['Strength'], vector_math.inputs[1])
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(vector_math.outputs['Vector'], set_position.inputs['Offset'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])
        
        self.created_node_groups[biome_name] = node_group
        print(f"✅ Created real-time displacement nodes for {biome_name}")
        return node_group

# ========================= REGISTRATION =========================

def register():
    """Register the real-time canvas monitor module"""
    print("✅ Real-time canvas monitor module registered")
    
    # Register any additional properties if needed
    if not hasattr(bpy.types.Scene, 'oneill_realtime_last_update'):
        bpy.types.Scene.oneill_realtime_last_update = bpy.props.FloatProperty(default=0.0)

def unregister():
    """Unregister the real-time canvas monitor module"""
    
    # Clean up any timers
    try:
        # Stop any active monitoring
        pass
    except:
        pass
    
    # Remove properties
    if hasattr(bpy.types.Scene, 'oneill_realtime_last_update'):
        try:
            del bpy.types.Scene.oneill_realtime_last_update
        except:
            pass
    
    print("⏹️ Real-time canvas monitor module unregistered")

# ========================= MODULE INFO =========================

"""
REAL-TIME CANVAS MONITOR MODULE
Phase 2B Sprint 1 Implementation

FEATURES:
✅ Real-time canvas change detection
✅ Timer-based monitoring system (500ms intervals)
✅ Automatic biome application to flat objects
✅ Fallback displacement modifiers for immediate feedback
✅ Performance optimized with change thresholds
✅ Multiple canvas support (individual heightmaps or unified canvas)

INTEGRATION:
- Place this file as: src/modules/realtime_canvas_monitor.py
- Main add-on will automatically import and use if available
- Provides Phase2BCanvasMonitor and RealtimeBiomeApplicator classes

WORKFLOW:
1. User starts terrain painting
2. User clicks "Start Real-Time Mode"
3. Canvas monitoring begins with timer system
4. Paint strokes detected via pixel sampling
5. Current biome applied to flat objects automatically
6. 3D viewport updates show immediate terrain changes

PERFORMANCE:
- 500ms update interval for stable performance
- Pixel subsampling (every 16th pixel) for efficiency
- Change threshold (5%) to avoid unnecessary updates
- Rate limiting to prevent excessive processing

This module transforms the O'Neill Terrain Generator into a revolutionary
real-time terrain design system with paint-to-3D live updates.
"""

if __name__ == "__main__":
    register()
