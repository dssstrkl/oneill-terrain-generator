"""
SESSION 33 - PHASE 1: S31 PAINT DETECTION INTEGRATION FIX
Enhanced paint detection system that uses sophisticated S31 geometry nodes
instead of falling back to old Session 10 approaches.
"""

import bpy

class S31PaintDetectionSystem:
    """
    Enhanced paint detection system that integrates sophisticated S31 geometry nodes
    with the Session 31 UV-Canvas system.
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
        
        # Map biome names to sophisticated S31 node groups
        self.s31_biome_mapping = {
            'ARCHIPELAGO': 'S31_ARCHIPELAGO',
            # Future additions:
            # 'MOUNTAINS': 'S31_MOUNTAINS',
            # 'CANYONS': 'S31_CANYONS',
            # 'HILLS': 'S31_HILLS',
            # 'DESERT': 'S31_DESERT',
            # 'OCEAN': 'S31_OCEAN'
        }
    
    def apply_s31_node_to_object(self, obj, biome_name):
        """Apply sophisticated S31 geometry node to object"""
        s31_node_name = self.s31_biome_mapping.get(biome_name)
        
        if not s31_node_name:
            print(f"⚠️ No S31 node available for {biome_name} yet, skipping sophisticated terrain")
            return None
        
        # Check if S31 node group exists
        if s31_node_name not in bpy.data.node_groups:
            print(f"❌ S31 node group {s31_node_name} not found")
            return None
        
        s31_node_group = bpy.data.node_groups[s31_node_name]
        
        # Remove any existing S31 modifiers on this object
        existing_s31_mods = [mod for mod in obj.modifiers 
                            if mod.type == 'NODES' and mod.name.startswith('S31_')]
        for mod in existing_s31_mods:
            obj.modifiers.remove(mod)
            print(f"  Removed existing S31 modifier: {mod.name}")
        
        # Add new S31 geometry nodes modifier
        modifier_name = f"S31_{biome_name}"
        modifier = obj.modifiers.new(modifier_name, 'NODES')
        modifier.node_group = s31_node_group
        
        # Set sophisticated terrain parameters
        # Note: S31_ARCHIPELAGO uses default inputs from node group
        modifier["Input_2"] = 1.0    # Strength (will be masked by UV-canvas)
        modifier["Input_3"] = 2.0    # Scale  
        
        print(f"✅ Applied {s31_node_name} to {obj.name}")
        return modifier
    
    def sample_canvas_region_for_object(self, object_index, canvas):
        """Sample the UV-mapped region of unified canvas for a specific flat object"""
        canvas_width, canvas_height = canvas.size
        pixels = list(canvas.pixels)
        
        # Calculate UV region for this object (each object gets 1/12th of canvas width)
        num_objects = 12  # Total flat objects
        u_start = object_index / num_objects  # 0.000, 0.083, 0.167, etc.
        u_end = (object_index + 1) / num_objects
        
        # Convert UV coordinates to pixel coordinates
        pixel_x_start = int(u_start * canvas_width)
        pixel_x_end = int(u_end * canvas_width)
        
        print(f"  Object {object_index + 1}: UV region {u_start:.3f}-{u_end:.3f} → pixels {pixel_x_start}-{pixel_x_end}")
        
        # Sample colors within this UV region
        return self.analyze_canvas_colors(pixels, canvas_width, canvas_height, 
                                        pixel_x_start, pixel_x_end)
    
    def analyze_canvas_colors(self, canvas_pixels, canvas_width, canvas_height, 
                            pixel_x_start, pixel_x_end):
        """Analyze canvas region to determine dominant biome"""
        detected_biomes = {}
        sample_count = 0
        
        # Sample pixels within the X range, across the full Y range
        sample_step_x = max(1, (pixel_x_end - pixel_x_start) // 20)  # 20 samples across width
        sample_step_y = max(1, canvas_height // 10)  # 10 samples across height
        
        for x in range(pixel_x_start, pixel_x_end, sample_step_x):
            for y in range(0, canvas_height, sample_step_y):
                pixel_idx = (y * canvas_width + x) * 4
                
                if pixel_idx + 2 < len(canvas_pixels):
                    pixel_color = (canvas_pixels[pixel_idx], 
                                 canvas_pixels[pixel_idx + 1], 
                                 canvas_pixels[pixel_idx + 2])
                    
                    # Skip black/unpainted pixels
                    if sum(pixel_color) < 0.1:
                        continue
                    
                    sample_count += 1
                    
                    # Find closest biome color
                    closest_biome = None
                    min_distance = float('inf')
                    
                    for biome, color in self.biome_colors.items():
                        distance = sum((a - b) ** 2 for a, b in zip(pixel_color, color)) ** 0.5
                        if distance < min_distance and distance < 0.3:  # Tolerance
                            min_distance = distance
                            closest_biome = biome
                    
                    if closest_biome:
                        detected_biomes[closest_biome] = detected_biomes.get(closest_biome, 0) + 1
        
        print(f"    Sampled {sample_count} painted pixels, detected biomes: {detected_biomes}")
        return detected_biomes
    
    def apply_s31_paint_detection(self):
        """Apply sophisticated S31 nodes based on paint detection"""
        # Check if unified canvas exists
        canvas_name = 'oneill_terrain_canvas'
        if canvas_name not in bpy.data.images:
            print("❌ Unified canvas not found")
            return False
        
        # Find all flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            print("❌ No flat objects found")
            return False
        
        # Sort objects by X position for consistent UV region mapping
        flat_objects.sort(key=lambda obj: obj.location.x)
        
        canvas = bpy.data.images[canvas_name]
        processed_count = 0
        s31_applied_count = 0
        
        print(f"\n🎨 S31 Paint Detection for {len(flat_objects)} objects...")
        
        # Process each object with its specific UV region
        for obj_index, obj in enumerate(flat_objects):
            try:
                # Sample this object's UV region from unified canvas
                detected_biomes = self.sample_canvas_region_for_object(obj_index, canvas)
                
                if detected_biomes:
                    # Apply the most prominent biome
                    main_biome = max(detected_biomes, key=detected_biomes.get)
                    
                    # Try to apply sophisticated S31 node
                    s31_modifier = self.apply_s31_node_to_object(obj, main_biome)
                    
                    if s31_modifier:
                        s31_applied_count += 1
                        print(f"✅ Object {obj_index + 1} ({obj.name}): Applied S31 {main_biome}")
                    else:
                        print(f"⚠️ Object {obj_index + 1} ({obj.name}): No S31 node for {main_biome}")
                    
                    processed_count += 1
                else:
                    print(f"⚠️ Object {obj_index + 1} ({obj.name}): No biomes detected in UV region")
            except Exception as e:
                print(f"❌ Object {obj_index + 1} ({obj.name}): Error processing UV region - {e}")
        
        print(f"\n🎉 S31 Paint Detection Complete!")
        print(f"   - Processed: {processed_count}/{len(flat_objects)} objects")
        print(f"   - S31 nodes applied: {s31_applied_count} objects")
        print(f"   - Objects still need Canvas_Displacement: {len(flat_objects)} (all)")
        
        return True

# ========================= ENHANCED PAINT DETECTION OPERATOR =========================

class ONEILL_OT_DetectPaintApplyS31Previews(bpy.types.Operator):
    """PHASE 1 FIX: Enhanced paint detection with S31 integration"""
    bl_idname = "oneill.detect_paint_apply_s31_previews"
    bl_label = "🔍 Detect Paint & Apply S31 Previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Initialize S31 paint detection system
        s31_system = S31PaintDetectionSystem()
        
        try:
            success = s31_system.apply_s31_paint_detection()
            
            if success:
                self.report({'INFO'}, "✅ S31 paint detection complete! Sophisticated terrain applied.")
            else:
                self.report({'ERROR'}, "❌ S31 paint detection failed - check console for details")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"S31 paint detection error: {str(e)}")
            print(f"❌ S31 paint detection error: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# ========================= REGISTRATION =========================

def register():
    """Register S31 paint detection fix"""
    try:
        bpy.utils.register_class(ONEILL_OT_DetectPaintApplyS31Previews)
        print("✅ S31 Paint Detection Fix registered")
    except Exception as e:
        print(f"❌ S31 Paint Detection Fix registration failed: {e}")
        raise

def unregister():
    """Unregister S31 paint detection fix"""
    try:
        bpy.utils.unregister_class(ONEILL_OT_DetectPaintApplyS31Previews)
        print("✅ S31 Paint Detection Fix unregistered")
    except Exception as e:
        print(f"⚠️ S31 Paint Detection Fix unregistration failed: {e}")

if __name__ == "__main__":
    register()
