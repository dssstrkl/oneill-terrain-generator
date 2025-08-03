                closest_biome = None
                min_distance = float('inf')
                
                for biome, color in biome_colors.items():
                    distance = sum((a - b) ** 2 for a, b in zip(pixel_color, color)) ** 0.5
                    if distance < min_distance and distance < 0.3:  # Tolerance for color matching
                        min_distance = distance
                        closest_biome = biome
                
                if closest_biome:
                    detected_biomes[closest_biome] = detected_biomes.get(closest_biome, 0) + 1
        
        return detected_biomes

# ========================= SESSION 10 RECOVERY OPERATORS =========================

class ONEILL_OT_RecoverSession10Biomes(Operator):
    """Recover Session 10 biome systems"""
    bl_idname = "oneill.recover_session10_biomes"
    bl_label = "🔄 Recover Session 10 Biomes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        biome_gen = get_session10_biome_generator()
        if biome_gen:
            self.report({'INFO'}, "Session 10 biome system available and ready")
            print("✅ Session 10 BiomeGeometryGenerator recovered successfully")
        else:
            self.report({'WARNING'}, "Session 10 biome system unavailable - using fallback")
            print("⚠️ Session 10 recovery failed - fallback displacement system will be used")
        
        return {'FINISHED'}

class ONEILL_OT_TestSession10Integration(Operator):
    """Test Session 10 integration status"""
    bl_idname = "oneill.test_session10_integration"
    bl_label = "🧪 Test Session 10 Integration"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Test Session 10 biome generator
        biome_gen = get_session10_biome_generator()
        biome_status = "✅ Available" if biome_gen else "❌ Unavailable"
        
        # Test enhanced spatial mapping
        enhanced_mapper = get_enhanced_spatial_mapping()
        mapping_status = "✅ Available" if enhanced_mapper else "❌ Unavailable"
        
        # Test canvas persistence
        canvas_manager = get_canvas_persistence_manager()
        canvas_status = "✅ Available" if canvas_manager else "❌ Unavailable"
        
        message = f"Session 10 Status:\nBiomes: {biome_status}\nSpatial Mapping: {mapping_status}\nCanvas Manager: {canvas_status}"
        
        self.report({'INFO'}, message.replace('\n', ' | '))
        print(f"\n=== SESSION 10 INTEGRATION TEST ===")
        print(message)
        print("=== END TEST ===")
        
        return {'FINISHED'}

# ========================= CANVAS MANAGEMENT =========================

class CanvasManager:
    """Enhanced canvas management with workspace splitting"""
    
    def __init__(self):
        self.active_canvas = None
        
    def setup_split_workspace_for_painting(self, context, canvas):
        """Set up split workspace with 3D View and Image Editor"""
        try:
            # Find the largest area to split
            largest_area = None
            largest_size = 0
            
            for area in context.screen.areas:
                area_size = area.width * area.height
                if area_size > largest_size:
                    largest_size = area_size
                    largest_area = area
            
            if largest_area and largest_area.type == 'VIEW_3D':
                # Split the area 60/40
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.6)
                
                # Set the new area to Image Editor
                for area in context.screen.areas:
                    if area != largest_area and area.type == 'VIEW_3D':
                        area.type = 'IMAGE_EDITOR'
                        
                        # Load the canvas in Image Editor
                        for space in area.spaces:
                            if space.type == 'IMAGE_EDITOR':
                                space.image = canvas
                                space.mode = 'PAINT'
                                break
                        break
                
                self.active_canvas = canvas
                print(f"✅ Set up split workspace with canvas: {canvas.name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Workspace split failed: {e}")
            
        return False
    
    def calculate_canvas_dimensions(self, flat_objects):
        """Calculate optimal canvas dimensions based on flat objects"""
        if not flat_objects:
            return 1024, 1024
            
        total_width = sum(obj.get("cylinder_length", 2.0) for obj in flat_objects)
        max_height = max(2 * math.pi * obj.get("cylinder_radius", 1.0) for obj in flat_objects)
        
        # Convert to pixel dimensions (roughly 100 pixels per unit)
        canvas_width = max(512, min(4096, int(total_width * 100)))
        canvas_height = max(512, min(2048, int(max_height * 100)))
        
        return canvas_width, canvas_height

class ONEILL_OT_LoadCanvasManually(Operator):
    """Manually load canvas for painting"""
    bl_idname = "oneill.load_canvas_manually"
    bl_label = "📂 Load Canvas Manually"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found")
            return {'CANCELLED'}
            
        canvas_manager = CanvasManager()
        
        # Find or create combined canvas
        canvas_name = "oneill_terrain_canvas"
        canvas = None
        
        if canvas_name in bpy.data.images:
            canvas = bpy.data.images[canvas_name]
        else:
            # Create new canvas
            canvas_width, canvas_height = canvas_manager.calculate_canvas_dimensions(flat_objects)
            canvas = bpy.data.images.new(
                canvas_name,
                width=canvas_width,
                height=canvas_height,
                alpha=False
            )
            
        # Set up split workspace
        if canvas_manager.setup_split_workspace_for_painting(context, canvas):
            context.scene.oneill_props.painting_mode = True
            self.report({'INFO'}, f"Canvas loaded: {canvas.name} ({canvas.size[0]}x{canvas.size[1]})")
        else:
            self.report({'WARNING'}, "Canvas loaded but workspace split failed")
            
        return {'FINISHED'}

# ========================= TERRAIN PAINTING OPERATORS =========================

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with canvas setup"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Start Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found. Complete steps 1-3 first.")
            return {'CANCELLED'}
            
        # Check if heightmaps exist
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        if not heightmap_objects:
            self.report({'ERROR'}, "No heightmaps found. Run step 3 'Create Heightmaps' first.")
            return {'CANCELLED'}
            
        canvas_manager = CanvasManager()
        canvas_width, canvas_height = canvas_manager.calculate_canvas_dimensions(flat_objects)
        
        # Create combined canvas from heightmaps
        canvas_name = "oneill_terrain_canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
            
        canvas = bpy.data.images.new(
            canvas_name,
            width=canvas_width,
            height=canvas_height,
            alpha=False
        )
        
        # Initialize canvas with neutral color
        pixels = [0.5, 0.5, 0.5, 1.0] * (canvas_width * canvas_height)
        canvas.pixels = pixels
        canvas.update()
        
        # Set up workspace
        if canvas_manager.setup_split_workspace_for_painting(context, canvas):
            props.painting_mode = True
            props.current_biome = 'MOUNTAINS'  # Default biome
            
            # Set initial brush color
            bpy.ops.oneill.select_painting_biome(biome_type='MOUNTAINS')
            
            self.report({'INFO'}, f"Painting mode started. Canvas: {canvas_width}x{canvas_height}")
        else:
            self.report({'WARNING'}, "Painting mode started but workspace setup failed")
            props.painting_mode = True
            
        return {'FINISHED'}

class ONEILL_OT_ValidateTerrainLayout(Operator):
    """Validate terrain layout and object consistency"""
    bl_idname = "oneill.validate_terrain_layout"
    bl_label = "✅ Validate Terrain Layout"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Check alignment
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("oneill_aligned")]
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        
        validation_results = []
        validation_results.append(f"Aligned cylinders: {len(aligned_objects)}")
        validation_results.append(f"Flat objects: {len(flat_objects)}")
        validation_results.append(f"Heightmap objects: {len(heightmap_objects)}")
        
        # Check Session 10 availability
        biome_gen = get_session10_biome_generator()
        enhanced_mapper = get_enhanced_spatial_mapping()
        
        validation_results.append(f"Session 10 biomes: {'✅' if biome_gen else '❌'}")
        validation_results.append(f"Enhanced mapping: {'✅' if enhanced_mapper else '❌'}")
        
        message = " | ".join(validation_results)
        self.report({'INFO'}, message)
        
        print("\n=== TERRAIN LAYOUT VALIDATION ===")
        for result in validation_results:
            print(f"  {result}")
        print("=== END VALIDATION ===")
        
        return {'FINISHED'}

class ONEILL_OT_GenerateTerrain(Operator):
    """Generate final terrain with enhanced mapping"""
    bl_idname = "oneill.generate_terrain"
    bl_label = "🏔️ Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for terrain generation")
            return {'CANCELLED'}
            
        # Apply enhanced spatial mapping if available
        enhanced_mapper = get_enhanced_spatial_mapping()
        if enhanced_mapper:
            try:
                enhanced_mapper.apply_enhanced_spatial_mapping()
                print("✅ Applied enhanced spatial mapping for terrain generation")
            except Exception as e:
                print(f"⚠️ Enhanced spatial mapping failed: {e}")
        
        # Apply terrain to objects
        preview_system = GlobalPreviewDisplacementSystem()
        terrain_count = 0
        
        for obj in flat_objects:
            # Convert preview to final terrain
            if props.current_biome:
                preview_system.create_biome_preview(obj, props.current_biome)
                terrain_count += 1
                
        self.report({'INFO'}, f"Generated terrain on {terrain_count} objects")
        return {'FINISHED'}

class ONEILL_OT_RewrapToCylinders(Operator):
    """Enhanced rewrap to cylinders with terrain data"""
    bl_idname = "oneill.rewrap_to_cylinders"
    bl_label = "🔄 Rewrap to Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for rewrapping")
            return {'CANCELLED'}
            
        rewrapped_count = 0
        
        for flat_obj in flat_objects:
            original_name = flat_obj.get("original_object")
            if not original_name or original_name not in bpy.data.objects:
                continue
                
            original_obj = bpy.data.objects[original_name]
            
            # Copy terrain modifiers from flat object to original cylinder
            for modifier in flat_obj.modifiers:
                if modifier.name.startswith(("Preview_", "Biome_")):
                    new_mod = original_obj.modifiers.new(modifier.name, modifier.type)
                    
                    # Copy modifier properties
                    for prop in dir(modifier):
                        if not prop.startswith('_') and hasattr(new_mod, prop):
                            try:
                                setattr(new_mod, prop, getattr(modifier, prop))
                            except:
                                pass
                                
            # Show original object and hide flat object
            original_obj.hide_viewport = False
            flat_obj.hide_viewport = True
            rewrapped_count += 1
            
        # Exit painting mode
        props.painting_mode = False
        
        self.report({'INFO'}, f"Rewrapped {rewrapped_count} cylinders with terrain data")
        return {'FINISHED'}

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Enhanced main panel with Session 10 integration"""
    bl_label = "O'Neill Terrain Generator"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Header with version info
        box = layout.box()
        box.label(text="Session 10 Integrated v2.6.0", icon='INFO')
        
        # Session 10 status indicators
        biome_gen = get_session10_biome_generator()
        enhanced_mapper = get_enhanced_spatial_mapping()
        
        status_box = box.box()
        status_box.label(text="Session 10 Status:", icon='PREFERENCES')
        row = status_box.row()
        row.label(text=f"Biomes: {'✅' if biome_gen else '❌'}")
        row.label(text=f"Enhanced: {'✅' if enhanced_mapper else '❌'}")
        
        layout.separator()
        
        # ========================= STEP 1: ALIGN CYLINDERS =========================
        step_box = layout.box()
        step_box.label(text="Step 1: Align Cylinders", icon='OBJECT_DATA')
        
        row = step_box.row()
        row.prop(props, "alignment_axis")
        
        step_box.operator("oneill.align_cylinders", text="Align Selected Cylinders", icon='SORT_ASC')
        
        # Show alignment status
        aligned_objects = [obj for obj in bpy.data.objects if obj.get("oneill_aligned")]
        if aligned_objects:
            step_box.label(text=f"✅ {len(aligned_objects)} cylinders aligned", icon='CHECKMARK')
        
        layout.separator()
        
        # ========================= STEP 2: UNWRAP TO FLAT =========================
        step_box = layout.box()
        step_box.label(text="Step 2: Unwrap to Flat", icon='UV')
        
        step_box.operator("oneill.unwrap_to_flat", text="Unwrap to Flat Objects", icon='MESH_PLANE')
        
        # Show unwrap status
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if flat_objects:
            step_box.label(text=f"✅ {len(flat_objects)} flat objects created", icon='CHECKMARK')
        
        layout.separator()
        
        # ========================= STEP 3: CREATE HEIGHTMAPS =========================
        step_box = layout.box()
        step_box.label(text="Step 3: Create Heightmaps", icon='IMAGE_DATA')
        
        row = step_box.row()
        row.prop(props, "heightmap_resolution")
        
        step_box.operator("oneill.create_heightmaps", text="Create Heightmaps", icon='TEXTURE')
        
        # Show heightmap status
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")]
        if heightmap_objects:
            step_box.label(text=f"✅ {len(heightmap_objects)} heightmaps created", icon='CHECKMARK')
        
        layout.separator()
        
        # ========================= STEP 4: TERRAIN PAINTING =========================
        if flat_objects and heightmap_objects:
            paint_box = layout.box()
            paint_box.label(text="Step 4: Terrain Painting", icon='BRUSH_DATA')
            
            if not props.painting_mode:
                # Start painting mode
                paint_box.operator("oneill.start_terrain_painting", 
                                 text="🎨 Start Terrain Painting", 
                                 icon='BRUSH_DATA')
                
                # Alternative: Load canvas manually
                paint_box.operator("oneill.load_canvas_manually", 
                                 text="📂 Load Canvas Manually", 
                                 icon='FILE_IMAGE')
            else:
                # Painting mode active - show biome controls
                paint_box.label(text="🎨 Painting Mode Active", icon='CHECKMARK')
                paint_box.label(text=f"Current Biome: {get_biome_display_name(props.current_biome)}")
                
                # Biome selection buttons
                biome_grid = paint_box.grid_flow(columns=3, align=True)
                for biome_enum, display_name, description in BIOME_TYPES:
                    op = biome_grid.operator("oneill.select_painting_biome", 
                                           text=display_name)
                    op.biome_type = biome_enum
                
                paint_box.separator()
                
                # Paint detection and preview controls
                paint_box.operator("oneill.detect_paint_apply_previews", 
                                 text="🔍 Detect Paint & Apply Previews", 
                                 icon='BRUSH_DATA')
                
                paint_box.separator()
                
                # Session 10 recovery controls
                recovery_box = paint_box.box()
                recovery_box.label(text="Session 10 Recovery:", icon='RECOVER_LAST')
                
                row = recovery_box.row()
                row.operator("oneill.recover_session10_biomes", text="🔄 Recover Biomes")
                row.operator("oneill.test_session10_integration", text="🧪 Test Integration")
        
        layout.separator()
        
        # ========================= STEP 5: GENERATE & REWRAP =========================
        if flat_objects:
            final_box = layout.box()
            final_box.label(text="Step 5: Generate & Rewrap", icon='MESH_CYLINDER')
            
            # Validation
            final_box.operator("oneill.validate_terrain_layout", 
                             text="✅ Validate Layout", 
                             icon='CHECKMARK')
            
            # Terrain generation
            final_box.operator("oneill.generate_terrain", 
                             text="🏔️ Generate Terrain", 
                             icon='MODIFIER')
            
            # Final rewrap
            final_box.operator("oneill.rewrap_to_cylinders", 
                             text="🔄 Rewrap to Cylinders", 
                             icon='MESH_CYLINDER')
        
        layout.separator()
        
        # ========================= ADVANCED SETTINGS =========================
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Settings", icon='PREFERENCES')
        
        row = advanced_box.row()
        row.prop(props, "subdivision_levels")
        row = advanced_box.row()
        row.prop(props, "terrain_scale")
        row = advanced_box.row()
        row.prop(props, "noise_scale")
        
        # Real-time mode indicator
        if props.realtime_mode_active:
            advanced_box.label(text="⚡ Real-time monitoring active", icon='TIME')

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_RecoverSession10Biomes,
    ONEILL_OT_TestSession10Integration,
    ONEILL_OT_LoadCanvasManually,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_ValidateTerrainLayout,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_PT_MainPanel,
]

def register():
    """Register all addon components with enhanced error handling"""
    print(f"🚀 Registering O'Neill Terrain Generator v2.6.0 - Session 10 Integrated")
    
    # Clean up any existing registrations
    cleanup_existing_registrations()
    
    # Register all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered: {cls.__name__}")
        except Exception as e:
            print(f"❌ Failed to register {cls.__name__}: {e}")
            raise
    
    # Add scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize global preview system
    bpy.types.Scene.oneill_preview_system = GlobalPreviewDisplacementSystem()
    
    print("🎉 O'Neill Terrain Generator registration complete!")
    print("✅ Alignment bug fixed - cylinders align perfectly contiguously")
    print("✅ Session 10 integration - Enhanced biome geometry nodes available")
    print("✅ Enhanced spatial mapping - Canvas-to-object integration ready")

def cleanup_existing_registrations():
    """Clean up any existing registrations to prevent conflicts"""
    # Remove scene properties first
    scene_props = [
        'oneill_props',
        'oneill_preview_system',
        'oneill_painting_mode',
        'oneill_painting_active',
        'oneill_current_biome',
        'oneill_painting_canvas'
    ]
    
    for prop_name in scene_props:
        if hasattr(bpy.types.Scene, prop_name):
            try:
                delattr(bpy.types.Scene, prop_name)
                print(f"🧹 Cleaned up scene property: {prop_name}")
            except Exception as e:
                print(f"⚠️ Could not clean up {prop_name}: {e}")
    
    # List of potentially conflicting classes
    conflict_classes = [
        'ONEILL_OT_AlignCylinders',
        'ONEILL_OT_UnwrapToFlat', 
        'ONEILL_OT_CreateHeightmaps',
        'ONEILL_OT_SelectPaintingBiome',
        'ONEILL_OT_DetectPaintApplyPreviews',
        'ONEILL_OT_RecoverSession10Biomes',
        'ONEILL_OT_TestSession10Integration',
        'ONEILL_OT_LoadCanvasManually',
        'ONEILL_OT_StartTerrainPainting',
        'ONEILL_OT_ValidateTerrainLayout',
        'ONEILL_OT_GenerateTerrain',
        'ONEILL_OT_RewrapToCylinders',
        'ONEILL_PT_MainPanel',
        'OneillProperties',
        'GlobalPreviewDisplacementSystem'
    ]
    
    for class_name in conflict_classes:
        if hasattr(bpy.types, class_name):
            try:
                cls = getattr(bpy.types, class_name)
                bpy.utils.unregister_class(cls)
                print(f"🧹 Cleaned up existing class: {class_name}")
            except Exception as e:
                print(f"⚠️ Could not clean up {class_name}: {e}")

def unregister():
    """Unregister all addon components with cleanup"""
    print(f"📤 Unregistering O'Neill Terrain Generator v2.6.0")
    
    # Remove scene properties first
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    if hasattr(bpy.types.Scene, 'oneill_preview_system'):
        del bpy.types.Scene.oneill_preview_system
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
            print(f"📤 Unregistered: {cls.__name__}")
        except Exception as e:
            print(f"⚠️ Failed to unregister {cls.__name__}: {e}")
    
    # Clean up driver namespace
    if 'apply_enhanced_spatial_mapping' in bpy.app.driver_namespace:
        del bpy.app.driver_namespace['apply_enhanced_spatial_mapping']
    
    print("✅ O'Neill Terrain Generator unregistration complete")

if __name__ == "__main__":
    register()
