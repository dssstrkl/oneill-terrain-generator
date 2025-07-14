# Sprint Implementation Prompt: Two-Stage Preview → Lock-In Terrain System

## 🎯 Sprint Objective
Implement a two-stage terrain painting system that provides **immediate lightweight previews during painting** and **high-quality lock-in when finishing**, solving the performance vs. quality conflict in real-time terrain generation.

## 📋 Current Status Assessment

### ✅ **Working Components (Build Upon These)**
- Canvas monitoring system (optimized to 2 FPS)
- Canvas-to-flat-object spatial mapping
- Biome color detection from paint strokes
- Individual heightmap system for flat objects
- Biome geometry node generators
- Emergency performance controls

### ❌ **Current Issues (Address These)**
- No visual feedback during painting (too performance-focused)
- All-or-nothing approach (either lag or no previews)
- User uncertainty about paint placement
- Heavy geometry nodes cause lag in real-time

### 🎯 **Target Solution**
Two-stage system where users get **fast visual hints while painting** then **lock in high-quality terrain** when they click "Finish Terrain Painting."

## 🏗️ Implementation Tasks

### **Task 1: Preview System Implementation**
**Objective**: Create lightweight visual feedback during painting

#### **1.1 Preview Displacement Generator**
```python
class PreviewDisplacementSystem:
    def create_biome_preview(self, obj, biome_name):
        """Create fast displacement modifier for immediate preview"""
        # Remove existing preview modifiers
        # Create displacement modifier (not geometry nodes)
        # Apply biome-specific noise texture
        # Set parameters for visual distinction between biomes
        # Return modifier for tracking
        
    def update_preview_real_time(self, obj, biome_name, paint_intensity):
        """Update existing preview based on new paint strokes"""
        # Modify existing displacement strength
        # Adjust texture parameters if needed
        # Ensure no performance impact
        
    def remove_all_previews(self, obj):
        """Clean up preview modifiers before lock-in"""
        # Remove displacement modifiers with "Preview" in name
        # Prepare object for final terrain application
```

#### **1.2 Biome-Specific Preview Parameters**
```python
PREVIEW_SETTINGS = {
    'MOUNTAINS': {
        'displacement_strength': 1.2,
        'noise_scale': 3.0,
        'noise_detail': 2,
        'texture_type': 'CLOUDS'
    },
    'OCEAN': {
        'displacement_strength': -0.4,  # Negative for depressions
        'noise_scale': 1.0,
        'noise_detail': 1,
        'texture_type': 'CLOUDS'
    },
    'HILLS': {
        'displacement_strength': 0.6,
        'noise_scale': 2.0,
        'noise_detail': 3,
        'texture_type': 'CLOUDS'
    },
    # ... continue for all biomes
}
```

#### **1.3 Preview Performance Safeguards**
```python
class PreviewPerformanceManager:
    def __init__(self):
        self.max_preview_objects = 5  # Limit simultaneous previews
        self.update_frequency = 0.4   # 2.5 FPS max
        self.performance_threshold = 50  # Max ms per update
        
    def can_add_preview(self):
        """Check if system can handle another preview"""
        # Count current preview modifiers
        # Check recent performance metrics
        # Return boolean decision
        
    def emergency_preview_cleanup(self):
        """Remove all previews if performance degrades"""
        # Emergency removal of all displacement modifiers
        # Reset to manual-only mode
```

### **Task 2: Lock-In Conversion System**
**Objective**: Convert lightweight previews to high-quality final terrain

#### **2.1 Canvas Analysis Engine**
```python
class CanvasAnalysisEngine:
    def analyze_complete_canvas(self, canvas_image):
        """Scan entire canvas and identify all painted regions"""
        # Full canvas pixel analysis (one-time operation)
        # Identify biome colors and coverage areas  
        # Map painted regions to flat objects
        # Generate conversion queue: [(object, biome, region_coords), ...]
        # Return complete analysis results
        
    def extract_object_paint_region(self, canvas_image, flat_object):
        """Extract painted area for specific flat object"""
        # Use canvas layout cache to find object's region
        # Extract pixel data for that region
        # Convert to heightmap format
        # Return processed region data
        
    def generate_conversion_plan(self, analysis_results):
        """Create step-by-step conversion plan"""
        # Sort objects by priority/complexity
        # Estimate processing time per object
        # Create progress tracking structure
        # Return execution plan
```

#### **2.2 Heightmap Transfer System**
```python
class HeightmapTransferSystem:
    def transfer_canvas_to_heightmap(self, canvas_region, target_heightmap):
        """Transfer painted canvas region to object's heightmap"""
        # Resize canvas region to match heightmap dimensions
        # Convert paint colors/intensity to height values
        # Update target heightmap image data
        # Ensure proper color space and bit depth
        # Return success status
        
    def preserve_existing_heightmap_data(self, heightmap, new_paint_data):
        """Blend new paint with existing heightmap data"""
        # Read current heightmap values
        # Blend with new paint data (additive/replace modes)
        # Preserve unpainted areas
        # Return combined heightmap data
        
    def validate_heightmap_transfer(self, original_canvas_region, final_heightmap):
        """Verify transfer accuracy"""
        # Compare paint intensity to heightmap values
        # Check for data loss or corruption
        # Return validation results
```

#### **2.3 Final Terrain Application**
```python
class FinalTerrainApplicator:
    def apply_final_biome_terrain(self, flat_object, biome_name, heightmap_image):
        """Apply high-quality biome terrain using proper geometry nodes"""
        # Remove all preview modifiers
        # Create geometry node modifier
        # Load appropriate biome geometry node group
        # Connect heightmap image as input
        # Set biome-specific parameters
        # Return application status
        
    def batch_apply_terrain(self, conversion_plan, progress_callback=None):
        """Process entire conversion plan with progress reporting"""
        # Iterate through conversion plan
        # Apply terrain to each object
        # Report progress via callback
        # Handle errors gracefully
        # Return summary results
```

### **Task 3: Enhanced UI Integration**
**Objective**: Integrate two-stage system into existing UI

#### **3.1 Stage Indicator System**
```python
class TerrainPaintingStageManager:
    def __init__(self):
        self.current_stage = 'INACTIVE'  # INACTIVE, PREVIEW, CONVERTING, FINAL
        self.conversion_progress = 0.0
        self.stage_callbacks = {}
        
    def start_preview_stage(self):
        """Activate preview mode"""
        # Set stage to PREVIEW
        # Start lightweight monitoring
        # Update UI indicators
        # Trigger stage change callbacks
        
    def start_conversion_stage(self, conversion_plan):
        """Begin lock-in conversion"""
        # Set stage to CONVERTING
        # Stop preview monitoring
        # Start progress tracking
        # Update UI with progress bar
        
    def complete_final_stage(self, results):
        """Finish conversion and enter final stage"""
        # Set stage to FINAL
        # Display conversion results
        # Enable next workflow steps
        # Clean up temporary data
```

#### **3.2 Progress Reporting System**
```python
class ConversionProgressReporter:
    def __init__(self, total_objects):
        self.total_objects = total_objects
        self.current_object = 0
        self.current_operation = ""
        self.overall_progress = 0.0
        
    def report_object_start(self, object_name, biome_name):
        """Report starting conversion of specific object"""
        # Update current object counter
        # Set current operation description
        # Calculate overall progress percentage
        # Update UI progress display
        
    def report_operation_progress(self, operation, progress):
        """Report progress within current operation"""
        # Update operation-specific progress
        # Combine with overall progress
        # Update UI elements
        
    def report_completion(self, success_count, failure_count, summary):
        """Report final conversion results"""
        # Display success/failure statistics
        # Show summary of applied biomes
        # Provide next step recommendations
        # Clear progress displays
```

### **Task 4: Enhanced "Finish Terrain Painting" Implementation**
**Objective**: Transform existing button into full lock-in system

#### **4.1 Button Behavior Modification**
```python
class ONEILL_OT_FinishTerrainPainting(bpy.types.Operator):
    """Enhanced finish painting with full lock-in conversion"""
    bl_idname = "oneill.finish_terrain_painting"
    bl_label = "Finish Terrain Painting"
    bl_description = "Convert all previews to final high-quality terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        """Show confirmation dialog with conversion preview"""
        # Analyze current canvas state
        # Count objects that will be processed
        # Estimate conversion time
        # Show confirmation dialog with details
        # Return context.window_manager.invoke_confirm(self, event)
        
    def execute(self, context):
        """Execute full preview-to-final conversion"""
        # Stop all real-time monitoring
        # Analyze complete canvas
        # Generate conversion plan
        # Execute heightmap transfers
        # Apply final geometry nodes
        # Report results to user
        # Update scene properties
        # Return {'FINISHED'}
        
    def modal(self, context, event):
        """Handle long-running conversion with progress updates"""
        # Process conversion in chunks to maintain UI responsiveness
        # Update progress bars
        # Handle cancellation requests
        # Return {'RUNNING_MODAL'} or {'FINISHED'}
```

#### **4.2 Conversion Workflow Implementation**
```python
def execute_full_conversion(self, context):
    """Complete conversion workflow"""
    try:
        # Phase 1: Analysis
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        analysis_engine = CanvasAnalysisEngine()
        analysis_results = analysis_engine.analyze_complete_canvas(canvas)
        
        # Phase 2: Planning
        conversion_plan = analysis_engine.generate_conversion_plan(analysis_results)
        progress_reporter = ConversionProgressReporter(len(conversion_plan))
        
        # Phase 3: Execution
        transfer_system = HeightmapTransferSystem()
        terrain_applicator = FinalTerrainApplicator()
        
        for obj_plan in conversion_plan:
            # Transfer canvas region to heightmap
            transfer_system.transfer_canvas_to_heightmap(obj_plan.canvas_region, obj_plan.heightmap)
            
            # Apply final terrain
            terrain_applicator.apply_final_biome_terrain(obj_plan.object, obj_plan.biome, obj_plan.heightmap)
            
            # Update progress
            progress_reporter.report_object_completion(obj_plan.object.name)
        
        # Phase 4: Completion
        self.report_conversion_summary(analysis_results, success_count, failure_count)
        
    except Exception as e:
        self.report({'ERROR'}, f"Conversion failed: {e}")
        return {'CANCELLED'}
```

### **Task 5: Performance Integration**
**Objective**: Ensure system works smoothly across different hardware

#### **5.1 Adaptive Performance System**
```python
class AdaptivePerformanceManager:
    def __init__(self):
        self.hardware_capability = self.assess_hardware()
        self.current_performance_mode = self.select_optimal_mode()
        
    def assess_hardware(self):
        """Determine system capabilities"""
        # Test simple operations and measure response time
        # Check available memory
        # Estimate geometry processing capability
        # Return capability rating (LOW, MEDIUM, HIGH)
        
    def select_optimal_mode(self):
        """Choose best performance mode for current hardware"""
        # Based on hardware assessment
        # Return recommended settings for preview and final stages
        
    def monitor_conversion_performance(self, operation_times):
        """Adjust settings based on actual performance"""
        # Track conversion operation times
        # Adjust future operations if too slow
        # Recommend user action if performance insufficient
```

#### **5.2 Fallback Systems**
```python
class ConversionFallbackManager:
    def handle_conversion_failure(self, failed_object, error):
        """Provide fallback options when conversion fails"""
        # Log specific error details
        # Attempt simplified conversion
        # Offer manual biome application option
        # Continue with remaining objects
        
    def provide_manual_alternative(self, failed_objects):
        """Guide user through manual terrain application"""
        # Show list of objects that need manual attention
        # Provide step-by-step manual application instructions
        # Offer to apply basic terrain as fallback
```

## 🎯 Success Criteria & Testing

### **Preview Stage Validation**
- [ ] **Immediate Feedback**: Displacement appears within 0.5 seconds of painting
- [ ] **Biome Distinction**: Each biome shows visually different displacement style
- [ ] **Performance**: No lag during painting, Blender remains responsive
- [ ] **Scalability**: Works with 1-20 flat objects without degradation
- [ ] **Memory Stability**: No memory leaks during extended painting sessions

### **Lock-In Stage Validation**
- [ ] **Complete Conversion**: All painted areas successfully convert to final terrain
- [ ] **Accuracy**: Final terrain exactly matches painted regions
- [ ] **Progress Reporting**: User sees clear progress and completion status
- [ ] **Error Handling**: Graceful handling of conversion failures with alternatives
- [ ] **Quality**: Final terrain uses proper heightmaps and geometry nodes

### **Integration Validation**
- [ ] **UI Flow**: Smooth transition from start → preview → finish → final
- [ ] **Workflow Integration**: Seamlessly fits into existing O'Neill workflow
- [ ] **Performance Modes**: System adapts to different hardware capabilities
- [ ] **Reversibility**: Can start new painting session after finishing previous one
- [ ] **Production Ready**: Final output suitable for rewrap to cylinders

### **User Experience Validation**
- [ ] **Intuitive Workflow**: Clear understanding of preview vs. final stages
- [ ] **User Control**: User decides when to commit to heavy processing
- [ ] **Confidence**: User can see results before finalizing
- [ ] **Flexibility**: Can cancel/restart if needed
- [ ] **Feedback**: Clear indication of system state and next steps

## 📋 Implementation Priority

### **Sprint 1: Core Preview System**
1. Implement PreviewDisplacementSystem
2. Add biome-specific preview parameters
3. Create performance safeguards
4. Test with basic displacement previews

### **Sprint 2: Lock-In Conversion**
1. Build CanvasAnalysisEngine
2. Implement HeightmapTransferSystem
3. Create FinalTerrainApplicator
4. Test conversion accuracy

### **Sprint 3: UI Integration**
1. Enhance "Finish Terrain Painting" button
2. Add progress reporting system
3. Implement stage indicators
4. Test complete user workflow

### **Sprint 4: Performance & Polish**
1. Add adaptive performance management
2. Implement fallback systems
3. Performance testing across hardware
4. User experience refinement

## 🚀 Expected Outcome

Upon completion, users will experience:

1. **Smooth Painting**: No lag, immediate visual feedback while painting
2. **Clear Workflow**: Paint → See Previews → Finish → Get Final Terrain
3. **User Control**: Heavy processing only when explicitly requested
4. **High Quality**: Final terrain uses full heightmap-based geometry nodes
5. **Reliable Performance**: Works consistently across different hardware configurations

This implementation transforms the terrain painting experience from a performance compromise into a professional workflow that provides both immediate feedback and production-quality results.