Real-time error: {e}")
            return self.update_interval

PHASE2A_MONITOR = Phase2ARealtimeMonitor()

class ONEILL_OT_StartRealtimeMonitoring(bpy.types.Operator):
    """Start real-time monitoring with performance awareness"""
    bl_idname = "oneill.start_realtime_monitoring"
    bl_label = "🚀 Start Real-Time Mode"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR, performance_manager
        
        if PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode already active")
            return {'CANCELLED'}
        
        # Performance check before starting
        if not performance_manager.check_memory_safety():
            self.report({'WARNING'}, "Memory safety concern - real-time mode may be slow")
        
        PHASE2A_MONITOR.last_canvas_hash = PHASE2A_MONITOR.get_canvas_hash()
        PHASE2A_MONITOR.active = True
        PHASE2A_MONITOR.change_count = 0
        
        timer_register(PHASE2A_MONITOR.realtime_callback)
        context.scene.oneill_props.realtime_mode_active = True
        
        vertex_count = performance_manager.estimate_vertex_count()
        self.report({'INFO'}, f"Real-Time Mode Started! Vertices: {vertex_count:,}")
        return {'FINISHED'}

class ONEILL_OT_StopRealtimeMonitoring(bpy.types.Operator):
    """Stop real-time monitoring"""
    bl_idname = "oneill.stop_realtime_monitoring"
    bl_label = "⏸️ Stop Real-Time Mode"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR
        
        if not PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode not active")
            return {'CANCELLED'}
        
        PHASE2A_MONITOR.active = False
        context.scene.oneill_props.realtime_mode_active = False
        
        message = f"Real-time mode stopped. Changes processed: {PHASE2A_MONITOR.change_count}"
        self.report({'INFO'}, message)
        return {'FINISHED'}

# ========================= PERFORMANCE-AWARE UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Main panel with performance monitoring and controls"""
    bl_label = "O'Neill Terrain Generator v2.4.0 - Performance Optimized"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw_performance_status(self, context, layout):
        """Draw performance status and controls"""
        global performance_manager
        
        # Performance status box
        perf_box = layout.box()
        perf_box.label(text="⚡ Performance Status", icon='SYSTEM')
        
        # Current performance mode
        props = context.scene.oneill_props
        perf_box.prop(props, "performance_mode")
        
        # Vertex count and memory safety
        try:
            vertex_count = performance_manager.estimate_vertex_count()
            is_safe = performance_manager.check_memory_safety()
            
            if is_safe:
                perf_box.label(text=f"✅ Vertices: {vertex_count:,}", icon='CHECKMARK')
            else:
                perf_box.label(text=f"⚠️ Vertices: {vertex_count:,} (HIGH)", icon='ERROR')
                perf_box.label(text="Consider reducing subdivision", icon='INFO')
        except:
            perf_box.label(text="Performance data unavailable", icon='QUESTION')
        
        # Performance tips
        if props.performance_mode == 'maximum_quality':
            perf_box.label(text="💎 Maximum quality may be slow", icon='TIME')
        elif props.performance_mode == 'viewport_preview':
            perf_box.label(text="🚀 Optimized for speed", icon='PLAY')

    def draw_enhanced_painting_controls(self, context, layout):
        """Enhanced painting controls with performance integration"""
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            layout.label(text="❌ No flat objects found", icon='ERROR')
            layout.label(text="Complete steps 1-3 first")
            return
        
        # Canvas status
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        if canvas and len(canvas.pixels) > 0:
            memory_mb = (canvas.size[0] * canvas.size[1] * 4) / (1024 * 1024)
            layout.label(text=f"✅ Canvas: {canvas.size[0]}x{canvas.size[1]} ({memory_mb:.1f}MB)", icon='CHECKMARK')
        else:
            layout.label(text="❌ No canvas found", icon='ERROR')
        
        if not props.painting_mode:
            # Start painting button
            layout.operator("oneill.start_terrain_painting", text="🎨 Start Terrain Painting")
            
            # Backwards compatibility
            layout.separator()
            layout.label(text="OR use procedural generation:", icon='MODIFIER')
            row = layout.row()
            row.prop(props, "terrain_scale")
            row.prop(props, "noise_scale")
            layout.operator("oneill.generate_terrain")
            
        else:
            # Active painting mode controls
            status_box = layout.box()
            if props.realtime_mode_active:
                status_box.label(text="🟢 REAL-TIME MODE ACTIVE", icon='REC')
            else:
                status_box.label(text="⚪ REAL-TIME MODE OFF", icon='PAUSE')
            
            # Real-time controls
            control_row = layout.row(align=True)
            if props.realtime_mode_active:
                control_row.operator("oneill.stop_realtime_monitoring", icon='PAUSE')
            else:
                control_row.operator("oneill.start_realtime_monitoring", icon='PLAY')
            
            # Manual controls
            layout.separator()
            layout.label(text="Manual Controls:")
            layout.operator("oneill.detect_paint_apply_previews", icon='BRUSH_DATA')
            
            # Biome selection
            layout.separator()
            col = layout.column(align=True)
            col.label(text="Biome Selection:", icon='BRUSH_DATA')
            
            current_biome_display = get_biome_display_name(props.current_biome)
            col.label(text=f"Current: {current_biome_display}")
            
            # Biome buttons
            row1 = col.row(align=True)
            op = row1.operator("oneill.select_painting_biome", text="🏝️")
            op.biome = 'ARCHIPELAGO'
            op = row1.operator("oneill.select_painting_biome", text="🏔️")
            op.biome = 'MOUNTAINS'
            op = row1.operator("oneill.select_painting_biome", text="🏜️")
            op.biome = 'CANYONS'
            
            row2 = col.row(align=True)
            op = row2.operator("oneill.select_painting_biome", text="🏞️")
            op.biome = 'HILLS'
            op = row2.operator("oneill.select_painting_biome", text="🌵")
            op.biome = 'DESERT'
            op = row2.operator("oneill.select_painting_biome", text="🌊")
            op.biome = 'OCEAN'
            
            # Preview controls
            col.separator()
            col.label(text="Apply Biome Previews:", icon='MODIFIER')
            preview_row = col.row(align=True)
            op = preview_row.operator("oneill.apply_biome_preview", text="Mountains")
            op.biome_type = 'MOUNTAINS'
            op = preview_row.operator("oneill.apply_biome_preview", text="Ocean") 
            op.biome_type = 'OCEAN'
            
            col.separator()
            col.operator("oneill.remove_all_previews")
            col.separator()
            col.operator("oneill.finish_terrain_painting")
            col.operator("oneill.exit_painting_mode")
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Performance status at top
        self.draw_performance_status(context, layout)
        
        # Painting mode indicator
        if props.painting_mode:
            box = layout.box()
            box.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
            current_biome_display = get_biome_display_name(props.current_biome)
            box.label(text=f"Current: {current_biome_display}")
        
        # Step 1: Align Cylinders
        box = layout.box()
        box.label(text="1. Align Cylinders", icon='OBJECT_DATA')
        row = box.row()
        row.prop(props, "alignment_axis")
        box.operator("oneill.align_cylinders")
        
        # Step 2: Unwrap to Flat
        box = layout.box()
        box.label(text="2. Unwrap to Flat", icon='MOD_UVPROJECT')
        
        # Performance warning for subdivision levels
        col = box.column()
        col.prop(props, "subdivision_levels")
        if props.subdivision_levels >= 3:
            warning_box = col.box()
            warning_box.label(text="⚠️ Level 3: Very high vertex count!", icon='ERROR')
            warning_box.label(text="May cause memory issues", icon='INFO')
        elif props.subdivision_levels >= 2:
            warning_box = col.box()
            warning_box.label(text="⚠️ Level 2: High vertex count", icon='TIME')
        
        box.operator("oneill.unwrap_to_flat") 
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Paint Terrain Biomes
        box = layout.box()
        box.label(text="4. Paint Terrain Biomes", icon='BRUSH_DATA')
        self.draw_enhanced_painting_controls(context, box)
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_ApplyBiomePreview,
    ONEILL_OT_RemoveAllPreviews,
    ONEILL_OT_FinishTerrainPainting,
    ONEILL_OT_ExitPaintingMode,
    ONEILL_PT_MainPanel,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_StartRealtimeMonitoring,
    ONEILL_OT_StopRealtimeMonitoring,
]

def register():
    """Register all classes and initialize performance systems"""
    global performance_manager, smart_canvas_manager, grid_overlay
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize performance systems
    performance_manager = ProfessionalPerformanceManager()
    smart_canvas_manager = SmartCanvasManager()
    grid_overlay = TerrainPaintingGridOverlay()
    
    # Set to safe performance mode
    performance_manager.set_performance_mode('viewport_preview')
    
    print("=" * 60)
    print("O'Neill Terrain Generator v2.4.0 - PERFORMANCE OPTIMIZED")
    print("🎯 FIXED: 69.7M vertex subdivision issue (was 25GB RAM)")
    print("⚡ Professional LOD system applied")
    print("📊 Memory-safe subdivision management")
    print("🎨 Smart canvas management")
    print("=" * 60)

def unregister():
    """Unregister classes and cleanup performance systems"""
    global grid_overlay
    
    if grid_overlay:
        grid_overlay.disable()
        
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    print("O'Neill Terrain Generator v2.4.0 unregistered")

if __name__ == "__main__":
    register()
