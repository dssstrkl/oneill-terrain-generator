"""
O'Neill Terrain Generator - Stroke-Based Y-Axis Wrapping System
Natural stroke wrapping without race conditions or artificial tiling zones
Replaces problematic real-time canvas monitoring approach
Minimal dependencies - only uses core Blender functionality
"""

import bpy
import time

class StrokeBasedYWrapping:
    """Unified stroke wrapping + preview monitor - eliminates race conditions"""
    
    def __init__(self):
        self.canvas = None
        self.canvas_width = 0
        self.canvas_height = 0
        self.last_pixel_check = {}
        self.stroke_detection_active = False
        self.timer = None
        self.wrap_history = []  # Track wrapped regions to avoid double-wrapping
        
        # UNIFIED MONITORING - Eliminates race conditions
        self.processing_lock = False  # Prevents simultaneous processing
        self.unified_monitoring = False  # True when handling both stroke + preview
        
        # Natural stroke wrapping settings
        self.boundary_threshold = 5  # pixels from edge for wrap detection
        self.natural_wrapping_active = False
        self.last_canvas_hash = None
        
    def setup_y_wrapping_for_canvas(self, canvas):
        """Set up stroke-based Y-wrapping for a canvas"""
        if not canvas:
            print("❌ No canvas provided for Y-wrapping setup")
            return False
            
        self.canvas = canvas
        self.canvas_width = canvas.size[0]
        self.canvas_height = canvas.size[1]
        
        # Store initial pixel state for change detection
        self.last_pixel_check = self._get_canvas_checksum()
        
        print(f"✅ Y-wrapping setup for canvas: {self.canvas_width}x{self.canvas_height}")
        return True
    
    def start_stroke_monitoring(self):
        """Start monitoring for paint strokes to wrap"""
        if self.stroke_detection_active:
            return True
            
        if not self.canvas:
            print("❌ No canvas available for stroke monitoring")
            return False
        
        # Use a much lighter monitoring approach - just detect changes
        self.timer = bpy.app.timers.register(
            self._check_for_stroke_changes,
            first_interval=0.2,  # Check every 0.2 seconds
            persistent=True
        )
        
        self.stroke_detection_active = True
        print("✅ Stroke-based Y-wrapping monitoring started")
        return True
    
    def stop_stroke_monitoring(self):
        """Stop stroke monitoring"""
        if self.timer:
            try:
                bpy.app.timers.unregister(self.timer)
            except:
                pass
            self.timer = None
        
        self.stroke_detection_active = False
        print("⏹️ Stroke monitoring stopped")
    
    def _get_canvas_checksum(self):
        """Get a lightweight checksum of canvas state"""
        if not self.canvas:
            return {}
            
        try:
            pixels = self.canvas.pixels[:]
            # Sample every 10th pixel for performance
            sample_step = 10
            checksum = {}
            
            for i in range(0, len(pixels), sample_step * 4):
                if i + 3 < len(pixels):
                    pixel_pos = i // 4
                    r, g, b, a = pixels[i:i+4]
                    if r > 0.01 or g > 0.01 or b > 0.01:  # Non-black pixel
                        checksum[pixel_pos] = (r, g, b, a)
            
            return checksum
            
        except Exception as e:
            print(f"⚠️ Checksum calculation error: {e}")
            return {}
    
    def _check_for_stroke_changes(self):
        """Lightweight check for canvas changes and apply Y-wrapping"""
        try:
            if not self.canvas:
                return None  # Stop monitoring
            
            # SESSION 59: Enhanced natural stroke wrapping detection
            if self.natural_wrapping_active:
                return self._natural_stroke_boundary_detection()
            
            # Original method for compatibility
            # Get current canvas state
            current_checksum = self._get_canvas_checksum()
            
            # Find new painted pixels
            new_pixels = {}
            for pos, pixel in current_checksum.items():
                if pos not in self.last_pixel_check:
                    new_pixels[pos] = pixel
            
            # If we found new paint strokes, check for Y-wrapping
            if new_pixels:
                self._apply_natural_y_wrapping(new_pixels)
                self.last_pixel_check = current_checksum
            
            # Continue monitoring
            return 0.2
            
        except Exception as e:
            print(f"❌ Stroke monitoring error: {e}")
            return None  # Stop on error
    
    def _apply_natural_y_wrapping(self, new_pixels):
        """Apply natural Y-axis wrapping for new paint strokes"""
        if not new_pixels:
            return
            
        try:
            # Get canvas dimensions
            width = self.canvas_width
            height = self.canvas_height
            
            # Calculate Y-wrapping parameters
            # Use same 5% overlap as UV mapping
            overlap_ratio = 0.05
            main_height = int(height / (1.0 + overlap_ratio))  # ~597 pixels
            wrap_zone_height = height - main_height  # ~31 pixels
            
            pixels = list(self.canvas.pixels[:])
            wrapped_pixels = []
            
            for pixel_pos, (r, g, b, a) in new_pixels.items():
                x = pixel_pos % width
                y = pixel_pos // width
                
                # Check if this pixel needs Y-wrapping
                wrap_target = None
                
                # Case 1: Bottom edge content wraps to top
                if y >= main_height:
                    # Pixel is in bottom wrap zone, copy to top
                    offset_from_bottom = y - main_height
                    target_y = offset_from_bottom
                    wrap_target = (x, target_y)
                
                # Case 2: Top edge content wraps to bottom
                elif y < wrap_zone_height:
                    # Pixel is in top wrap zone, copy to bottom
                    target_y = main_height + y
                    wrap_target = (x, target_y)
                
                # Apply wrapping if target found
                if wrap_target:
                    target_x, target_y = wrap_target
                    
                    # Bounds check
                    if 0 <= target_x < width and 0 <= target_y < height:
                        target_index = (target_y * width + target_x) * 4
                        
                        if target_index + 3 < len(pixels):
                            # Only wrap if target area is not already painted
                            target_pixel = pixels[target_index:target_index+4]
                            if target_pixel[0] < 0.01 and target_pixel[1] < 0.01 and target_pixel[2] < 0.01:
                                pixels[target_index:target_index+4] = [r, g, b, a]
                                wrapped_pixels.append((target_x, target_y))
            
            # Apply wrapped pixels to canvas if any were created
            if wrapped_pixels:
                self.canvas.pixels = pixels
                self.canvas.update()
                print(f"✅ Applied Y-wrapping to {len(wrapped_pixels)} pixels")
                
        except Exception as e:
            print(f"❌ Y-wrapping application error: {e}")
    
    def apply_manual_y_wrap(self):
        """Manually apply Y-wrapping to current canvas content"""
        if not self.canvas:
            print("❌ No canvas available for manual Y-wrapping")
            return False
            
        try:
            width = self.canvas_width
            height = self.canvas_height
            pixels = list(self.canvas.pixels[:])
            
            # Calculate wrap zone
            overlap_ratio = 0.05
            main_height = int(height / (1.0 + overlap_ratio))
            wrap_zone_height = height - main_height
            
            wrapped_count = 0
            
            # Copy bottom content to top
            for y in range(wrap_zone_height):
                source_y = main_height + y  # Bottom zone
                target_y = y  # Top zone
                
                for x in range(width):
                    source_index = (source_y * width + x) * 4
                    target_index = (target_y * width + x) * 4
                    
                    if (source_index + 3 < len(pixels) and target_index + 3 < len(pixels)):
                        source_pixel = pixels[source_index:source_index+4]
                        
                        # Only copy if source has painted content
                        if source_pixel[0] > 0.01 or source_pixel[1] > 0.01 or source_pixel[2] > 0.01:
                            # And target is empty
                            target_pixel = pixels[target_index:target_index+4]
                            if target_pixel[0] < 0.01 and target_pixel[1] < 0.01 and target_pixel[2] < 0.01:
                                pixels[target_index:target_index+4] = source_pixel
                                wrapped_count += 1
            
            # Copy top content to bottom
            for y in range(wrap_zone_height):
                source_y = y  # Top zone
                target_y = main_height + y  # Bottom zone
                
                for x in range(width):
                    source_index = (source_y * width + x) * 4
                    target_index = (target_y * width + x) * 4
                    
                    if (source_index + 3 < len(pixels) and target_index + 3 < len(pixels)):
                        source_pixel = pixels[source_index:source_index+4]
                        
                        # Only copy if source has painted content
                        if source_pixel[0] > 0.01 or source_pixel[1] > 0.01 or source_pixel[2] > 0.01:
                            # And target is empty
                            target_pixel = pixels[target_index:target_index+4]
                            if target_pixel[0] < 0.01 and target_pixel[1] < 0.01 and target_pixel[2] < 0.01:
                                pixels[target_index:target_index+4] = source_pixel
                                wrapped_count += 1
            
            if wrapped_count > 0:
                self.canvas.pixels = pixels
                self.canvas.update()
                print(f"✅ Manual Y-wrapping applied: {wrapped_count} pixels wrapped")
                return True
            else:
                print("ℹ️ No content to wrap")
                return False
                
        except Exception as e:
            print(f"❌ Manual Y-wrapping error: {e}")
            return False
    
    def start_natural_stroke_wrapping(self):
        """SESSION 61: Start unified stroke wrapping + preview monitoring with race condition elimination"""
        if not self.canvas:
            print("❌ No canvas available for natural stroke wrapping")
            return False
        
        # SESSION 61: Enable unified monitoring mode
        self.unified_monitoring = True
        self.processing_lock = False
        
        # SESSION 61: Clean boundary regions for 100% canvas utilization
        self._eliminate_boundary_regions()
            
        self.natural_wrapping_active = True
        self.last_canvas_hash = self._get_quick_canvas_hash()
        
        # Use lighter monitoring frequency for real-time response
        if self.timer:
            try:
                bpy.app.timers.unregister(self.timer)
            except:
                pass
            
        self.timer = bpy.app.timers.register(
            self._check_for_stroke_changes,
            first_interval=0.1,  # 10 FPS for responsive wrapping
            persistent=True
        )
        
        self.stroke_detection_active = True
        print("🎨 UNIFIED NATURAL STROKE WRAPPING ACTIVE")
        print(f"   Revolutionary feature: Paint off Y-edges for automatic wrapping!")
        print(f"   Boundary detection: {self.boundary_threshold} pixels from top/bottom edges")
        print(f"   ✨ SESSION 61: Race condition elimination with processing locks")
        print(f"   🔗 Unified monitoring: Stroke wrapping → Preview updates")
        return True
    
    def _get_quick_canvas_hash(self):
        """Quick hash for change detection optimized for boundary regions"""
        try:
            pixels = self.canvas.pixels[:]
            sample_data = []
            
            width = self.canvas_width
            height = self.canvas_height
            
            # Sample top boundary region only
            for y in range(min(self.boundary_threshold, height)):
                for x in range(0, width, 20):  # Every 20th pixel for efficiency
                    idx = (y * width + x) * 4
                    if idx + 2 < len(pixels):
                        sample_data.append(int(pixels[idx] * 255))  # R channel
            
            # Sample bottom boundary region only  
            for y in range(max(0, height - self.boundary_threshold), height):
                for x in range(0, width, 20):
                    idx = (y * width + x) * 4
                    if idx + 2 < len(pixels):
                        sample_data.append(int(pixels[idx] * 255))  # R channel
            
            return hash(tuple(sample_data))
            
        except Exception as e:
            print(f"⚠️ Hash calculation error: {e}")
            return 0
    
    def _natural_stroke_boundary_detection(self):
        """SESSION 61: Unified monitoring with race condition elimination"""
        try:
            # RACE CONDITION PREVENTION: Processing lock
            if self.processing_lock:
                return 0.1  # Skip cycle if already processing
            
            # Quick change detection
            current_hash = self._get_quick_canvas_hash()
            if current_hash == self.last_canvas_hash:
                return 0.1  # No changes, continue monitoring
            
            # Set processing lock to prevent race conditions
            self.processing_lock = True
            
            try:
                # PHASE 1: Stroke wrapping (Priority processing)
                wrapped_strokes = self._detect_and_wrap_boundary_strokes()
                
                if wrapped_strokes > 0:
                    print(f"✨ Natural stroke wrapping: {wrapped_strokes} boundary crossings wrapped!")
                    # Force canvas update for immediate visual feedback
                    self.canvas.update()
                
                # PHASE 2: Live preview updates (Secondary processing) 
                if self.unified_monitoring:
                    self._trigger_preview_update()
                
                # PHASE 3: UI refresh
                try:
                    for area in bpy.context.screen.areas:
                        if area.type in {'VIEW_3D', 'IMAGE_EDITOR'}:
                            area.tag_redraw()
                except:
                    pass  # Don't fail on UI refresh errors
                
            finally:
                # Always release processing lock
                self.processing_lock = False
            
            self.last_canvas_hash = current_hash
            return 0.1  # Continue monitoring at 10 FPS
            
        except Exception as e:
            self.processing_lock = False  # Release lock on error
            print(f"❌ Unified monitoring error: {e}")
            return 0.2  # Continue with slower monitoring on error
    
    def _detect_and_wrap_boundary_strokes(self):
        """Revolutionary algorithm: Detect strokes near Y-boundaries and apply natural wrapping"""
        try:
            pixels = list(self.canvas.pixels[:])
            width = self.canvas_width
            height = self.canvas_height
            wrapped_count = 0
            
            # REVOLUTIONARY NATURAL WRAPPING ALGORITHM
            
            # Phase 1: Scan top boundary for strokes that should wrap to bottom
            for y in range(min(self.boundary_threshold, height)):
                for x in range(0, width, 2):  # Every other pixel for efficiency
                    idx = (y * width + x) * 4
                    if idx + 3 < len(pixels):
                        r, g, b, a = pixels[idx:idx+4]
                        
                        # Found painted pixel near top boundary
                        if r > 0.01 or g > 0.01 or b > 0.01:
                            # Calculate natural wrap position at bottom
                            # Stroke at Y=0 wraps to Y=height-1, Y=1 to Y=height-2, etc.
                            wrap_y = height - 1 - y
                            wrap_idx = (wrap_y * width + x) * 4
                            
                            # Apply wrap if target is unpainted and within bounds
                            if (wrap_idx + 3 < len(pixels) and wrap_y < height):
                                target_r, target_g, target_b = pixels[wrap_idx:wrap_idx+3]
                                
                                # Only wrap to unpainted areas (non-interfering)
                                if target_r < 0.01 and target_g < 0.01 and target_b < 0.01:
                                    pixels[wrap_idx:wrap_idx+4] = [r, g, b, a]
                                    wrapped_count += 1
            
            # Phase 2: Scan bottom boundary for strokes that should wrap to top
            for y in range(max(0, height - self.boundary_threshold), height):
                for x in range(0, width, 2):
                    idx = (y * width + x) * 4
                    if idx + 3 < len(pixels):
                        r, g, b, a = pixels[idx:idx+4]
                        
                        # Found painted pixel near bottom boundary
                        if r > 0.01 or g > 0.01 or b > 0.01:
                            # Calculate natural wrap position at top
                            # Stroke at Y=height-1 wraps to Y=0, Y=height-2 to Y=1, etc.
                            wrap_y = (height - 1) - y
                            wrap_idx = (wrap_y * width + x) * 4
                            
                            # Apply wrap if target is unpainted and within bounds
                            if (wrap_idx + 3 < len(pixels) and wrap_y >= 0):
                                target_r, target_g, target_b = pixels[wrap_idx:wrap_idx+3]
                                
                                # Only wrap to unpainted areas (non-interfering)
                                if target_r < 0.01 and target_g < 0.01 and target_b < 0.01:
                                    pixels[wrap_idx:wrap_idx+4] = [r, g, b, a]
                                    wrapped_count += 1
            
            # Apply all wrapped pixels at once for efficiency
            if wrapped_count > 0:
                self.canvas.pixels = pixels
            
            return wrapped_count
            
        except Exception as e:
            print(f"❌ Boundary stroke detection error: {e}")
            return 0
    
    def _trigger_preview_update(self):
        """SESSION 61: Trigger WorkingAutoPreviewSystem update without conflicts"""
        try:
            # Import and use WorkingAutoPreviewSystem for preview updates
            from oneill_terrain_generator_dev.main_terrain_system import WorkingAutoPreviewSystem
            
            preview_system = WorkingAutoPreviewSystem()
            
            # Only trigger if auto preview is active
            if hasattr(preview_system, 'auto_preview_active') and preview_system.auto_preview_active:
                # Use existing monitor_canvas_changes method
                preview_system.monitor_canvas_changes()
                
        except ImportError:
            # WorkingAutoPreviewSystem not available - skip preview updates
            pass
        except Exception as e:
            # Don't let preview errors break stroke wrapping
            print(f"⚠️ Preview update error (non-critical): {e}")
    
    def _eliminate_boundary_regions(self):
        """SESSION 61: Eliminate 5% boundary regions for 100% canvas utilization"""
        try:
            # Clear any gray boundary regions that prevent 100% canvas use
            pixels = list(self.canvas.pixels[:])
            width = self.canvas_width
            height = self.canvas_height
            
            # Convert all gray boundary pixels to pure black (unpainted)
            boundary_cleared = 0
            
            for y in range(height):
                for x in range(width):
                    idx = (y * width + x) * 4
                    if idx + 3 < len(pixels):
                        r, g, b, a = pixels[idx:idx+4]
                        
                        # Clear gray boundary artifacts (typical value 0.18-0.25)
                        if 0.15 < r < 0.3 and 0.15 < g < 0.3 and 0.15 < b < 0.3:
                            pixels[idx:idx+4] = [0.0, 0.0, 0.0, 1.0]  # Pure black
                            boundary_cleared += 1
            
            if boundary_cleared > 0:
                self.canvas.pixels = pixels
                self.canvas.update()
                print(f"✨ Boundary regions eliminated: {boundary_cleared} pixels cleared for 100% canvas use")
            
        except Exception as e:
            print(f"⚠️ Boundary elimination error: {e}")

# Global instance for integration
_stroke_wrapper = None

def get_stroke_wrapper():
    """Get global stroke wrapper instance"""
    global _stroke_wrapper
    if _stroke_wrapper is None:
        _stroke_wrapper = StrokeBasedYWrapping()
    return _stroke_wrapper

def setup_stroke_based_y_wrapping(canvas):
    """Setup stroke-based Y-wrapping for a canvas"""
    wrapper = get_stroke_wrapper()
    return wrapper.setup_y_wrapping_for_canvas(canvas)

def start_y_wrapping_monitoring():
    """Start Y-wrapping monitoring"""
    wrapper = get_stroke_wrapper()
    return wrapper.start_stroke_monitoring()

def stop_y_wrapping_monitoring():
    """Stop Y-wrapping monitoring"""
    wrapper = get_stroke_wrapper()
    wrapper.stop_stroke_monitoring()

def apply_manual_y_wrap():
    """Apply manual Y-wrapping to current canvas"""
    wrapper = get_stroke_wrapper()
    return wrapper.apply_manual_y_wrap()

def start_natural_stroke_wrapping():
    """SESSION 59: Start revolutionary natural stroke wrapping"""
    wrapper = get_stroke_wrapper()
    canvas = bpy.data.images.get("oneill_terrain_canvas")
    if canvas and not wrapper.canvas:
        wrapper.setup_y_wrapping_for_canvas(canvas)
    return wrapper.start_natural_stroke_wrapping()

def stop_natural_stroke_wrapping():
    """SESSION 59: Stop natural stroke wrapping"""
    wrapper = get_stroke_wrapper()
    wrapper.natural_wrapping_active = False
    wrapper.stop_stroke_monitoring()

# Blender operator for manual Y-wrapping
class ONEILL_OT_ApplyYWrapping(bpy.types.Operator):
    """Apply Y-axis wrapping to canvas manually"""
    bl_idname = "oneill.apply_y_wrapping"
    bl_label = "Apply Y-Axis Wrapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        canvas = bpy.data.images.get("oneill_terrain_canvas")
        if not canvas:
            self.report({'ERROR'}, "No canvas found")
            return {'CANCELLED'}
        
        wrapper = get_stroke_wrapper()
        if not wrapper.canvas:
            wrapper.setup_y_wrapping_for_canvas(canvas)
        
        success = wrapper.apply_manual_y_wrap()
        
        if success:
            self.report({'INFO'}, "Y-axis wrapping applied successfully")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No content to wrap")
            return {'CANCELLED'}

class ONEILL_OT_StartNaturalStrokeWrapping(bpy.types.Operator):
    """SESSION 59: Start revolutionary natural stroke wrapping"""
    bl_idname = "oneill.start_natural_stroke_wrapping"
    bl_label = "🎨 Start Natural Stroke Wrapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        canvas = bpy.data.images.get("oneill_terrain_canvas")
        if not canvas:
            self.report({'ERROR'}, "No canvas found - start terrain painting first")
            return {'CANCELLED'}
        
        success = start_natural_stroke_wrapping()
        
        if success:
            self.report({'INFO'}, "🎨 Natural stroke wrapping ACTIVE! Paint off Y-edges to see magic!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to start natural stroke wrapping")
            return {'CANCELLED'}

class ONEILL_OT_StopNaturalStrokeWrapping(bpy.types.Operator):
    """SESSION 59: Stop natural stroke wrapping"""
    bl_idname = "oneill.stop_natural_stroke_wrapping"
    bl_label = "⏹️ Stop Natural Stroke Wrapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        stop_natural_stroke_wrapping()
        self.report({'INFO'}, "Natural stroke wrapping stopped")
        return {'FINISHED'}

def register():
    """Register stroke-based Y-wrapping operators"""
    try:
        bpy.utils.register_class(ONEILL_OT_ApplyYWrapping)
        bpy.utils.register_class(ONEILL_OT_StartNaturalStrokeWrapping)
        bpy.utils.register_class(ONEILL_OT_StopNaturalStrokeWrapping)
        print("✅ Stroke-based Y-wrapping module registered with SESSION 59 natural wrapping")
    except Exception as e:
        print(f"❌ Registration error: {e}")

def unregister():
    """Unregister stroke-based Y-wrapping operators"""
    try:
        # Stop any active monitoring
        stop_natural_stroke_wrapping()
        
        bpy.utils.unregister_class(ONEILL_OT_ApplyYWrapping)
        bpy.utils.unregister_class(ONEILL_OT_StartNaturalStrokeWrapping)
        bpy.utils.unregister_class(ONEILL_OT_StopNaturalStrokeWrapping)
        print("⏹️ Stroke-based Y-wrapping module unregistered")
    except Exception as e:
        print(f"⚠️ Unregistration error: {e}")

if __name__ == "__main__":
    register()
