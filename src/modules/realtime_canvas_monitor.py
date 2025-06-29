# Phase 2B Real-time Canvas Monitoring System
# O'Neill Cylinder Terrain Generator - Revolutionary Paint-to-3D Integration
# Implementation Date: June 29, 2025

import bpy
import numpy as np
from mathutils import Vector
import bmesh

class RealtimeBiomeApplicator:
    """
    Applies biomes to objects in real-time based on painted canvas changes
    Integrates with Phase 2A biome geometry system
    """
    
    def __init__(self):
        self.phase1_to_phase2a_mapping = {
            'MOUNTAINS': 'mountain',
            'CANYONS': 'canyon', 
            'HILLS': 'rolling_hills',
            'DESERT': 'desert',
            'OCEAN': 'ocean'
        }
        self.biome_colors = {
            'MOUNTAINS': (0.5, 0.3, 0.1, 1.0),    # Brown
            'CANYONS': (0.8, 0.4, 0.2, 1.0),      # Orange
            'HILLS': (0.2, 0.6, 0.2, 1.0),        # Green  
            'DESERT': (0.9, 0.8, 0.4, 1.0),       # Yellow
            'OCEAN': (0.1, 0.3, 0.8, 1.0),        # Blue
        }
    
    def apply_biome_to_object(self, obj, biome_name, strength=1.0):
        """Apply biome using Phase 2A geometry node system"""
        try:
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
                
                print(f"✅ Applied {biome_name} to {obj.name}")
                return True
            else:
                print(f"⚠️ Biome node group not found: {node_group_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error applying biome: {e}")
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
        self.update_frequency = 0.1  # Check every 100ms for responsive feedback
        self.change_threshold = 0.01  # Minimum change to trigger update
        self.applicator = RealtimeBiomeApplicator()
        print("🔄 Phase 2B Canvas Monitor initialized")
    
    def start_monitoring(self):
        """Start real-time canvas monitoring"""
        if self.is_monitoring:
            print("⚠️ Monitoring already active")
            return False
        
        canvas = bpy.data.images.get(self.canvas_name)
        if not canvas or not canvas.has_data:
            print("❌ No canvas available for monitoring")
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
        print("✅ Real-time canvas monitoring STARTED")
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
        
        # Get pixel data as numpy array for efficient processing
        pixels = np.array(canvas.pixels)
        return pixels.reshape((canvas.size[1], canvas.size[0], 4))
    
    def _monitor_canvas_changes(self):
        """Timer callback to check for canvas changes"""
        if not self.is_monitoring:
            return None  # Stop timer
        
        try:
            current_state = self._capture_canvas_state()
            
            if current_state is None or self.previous_canvas_data is None:
                return self.update_frequency  # Continue monitoring
            
            # Detect changes using numpy for performance
            diff = np.abs(current_state - self.previous_canvas_data)
            changed_pixels = np.any(diff > self.change_threshold, axis=2)
            
            if np.any(changed_pixels):
                print("🎨 Canvas change detected - processing...")
                self._process_canvas_changes(current_state, changed_pixels)
                self.previous_canvas_data = current_state.copy()
            
            return self.update_frequency  # Continue monitoring
            
        except Exception as e:
            print(f"