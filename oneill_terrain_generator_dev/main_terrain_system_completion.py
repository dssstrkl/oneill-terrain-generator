            if current_hash and current_hash != self.last_canvas_hash:
                self.change_count += 1
                print(f"🎨 Real-time change #{self.change_count} detected")
                
                # Apply biomes using paint detection
                result = bpy.ops.oneill.detect_paint_apply_previews()
                if result == {'FINISHED'}:
                    print(f"✅ Real-time terrain update applied")
                
                self.last_canvas_hash = current_hash
            
            return self.update_interval  # Continue monitoring
            
        except Exception as e:
            print(f"❌ Real-time error: {e}")
            return self.update_interval

# Create global monitor instance
PHASE2A_MONITOR = Phase2ARealtimeMonitor()

class ONEILL_OT_StartRealtimeMonitoring(bpy.types.Operator):
    """Start Phase 2A Real-Time Paint Monitoring - WORKING ARCHIVE VERSION"""
    bl_idname = "oneill.start_realtime_monitoring"
    bl_label = "🚀 Start Real-Time Mode"
    bl_description = "Activate automatic paint detection and terrain updates"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR
        
        if PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode already active")
            return {'CANCELLED'}
        
        PHASE2A_MONITOR.last_canvas_hash = PHASE2A_MONITOR.get_canvas_hash()
        PHASE2A_MONITOR.active = True
        PHASE2A_MONITOR.change_count = 0
        PHASE2A_MONITOR.total_updates = 0
        
        timer_register(PHASE2A_MONITOR.realtime_callback)
        context.scene.oneill_props.realtime_mode_active = True
        
        self.report({'INFO'}, "Real-Time Mode Started! Paint and see instant terrain updates.")
        return {'FINISHED'}

class ONEILL_OT_StopRealtimeMonitoring(bpy.types.Operator):
    """Stop Phase 2A Real-Time Paint Monitoring - WORKING ARCHIVE VERSION"""
    bl_idname = "oneill.stop_realtime_monitoring"
    bl_label = "⏸️ Stop Real-Time Mode"
    bl_description = "Return to manual terrain painting mode"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        global PHASE2A_MONITOR
        
        if not PHASE2A_MONITOR.active:
            self.report({'WARNING'}, "Real-time mode not active")
            return {'CANCELLED'}
        
        PHASE2A_MONITOR.active = False
        context.scene.oneill_props.realtime_mode_active = False
        
        message = f"Real-time mode stopped. Processed {PHASE2A_MONITOR.change_count} changes."
        self.report({'INFO'}, message)
        return {'FINISHED'}

# ========================= UI PANEL (FROM ARCHIVE) =========================

class ONEILL_PT_MainPanel(Panel):
    """Main O'Neill Terrain Generator panel - WORKING ARCHIVE VERSION"""
    bl_label = "O'Neill Terrain Generator v2.3.1 - RESTORED"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw_enhanced_painting_controls(self, context, layout):
        """Enhanced painting controls with Phase 2A real-time integration"""
        props = context.scene.oneill_props
        
        # Check for flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            layout.label(text="❌ No flat objects found", icon='ERROR')
            layout.label(text="Complete steps 1-3 first")
            return
        
        # Canvas status check
        canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
        
        if canvas and len(canvas.pixels) > 0:
            aspect_ratio = canvas.size[0] / canvas.size[1] if canvas.size[1] > 0 else 1
            if aspect_ratio > 10 or aspect_ratio < 0.1:
                layout.label(text="❌ Canvas needs recreation", icon='ERROR')
            else:
                layout.label(text=f"✅ Canvas: {canvas.size[0]}x{canvas.size[1]}", icon='CHECKMARK')
        else:
            layout.label(text="❌ No canvas found", icon='ERROR')
        
        if not props.painting_mode:
            # NOT PAINTING: Show start button
            layout.operator("oneill.start_terrain_painting", text="🎨 Start Terrain Painting")
            
            # Optional: Show old Generate Terrain for backwards compatibility
            layout.separator()
            layout.label(text="OR use procedural generation:", icon='MODIFIER')
            row = layout.row()
            row.prop(props, "terrain_scale")
            row.prop(props, "noise_scale")
            layout.operator("oneill.generate_terrain")
            
        else:
            # PAINTING MODE ACTIVE: Show enhanced controls
            
            # Real-time mode status
            status_box = layout.box()
            if props.realtime_mode_active:
                status_box.label(text="🟢 REAL-TIME MODE ACTIVE", icon='REC')
                status_box.label(text="Paint automatically applies!")
            else:
                status_box.label(text="⚪ REAL-TIME MODE OFF", icon='PAUSE')
            
            # Real-time controls
            control_row = layout.row(align=True)
            if props.realtime_mode_active:
                control_row.operator("oneill.stop_realtime_monitoring", icon='PAUSE')
            else:
                control_row.operator("oneill.start_realtime_monitoring", icon='PLAY')
            
            # Manual detection fallback
            layout.separator()
            layout.label(text="Manual Controls:")
            layout.operator("oneill.detect_paint_apply_previews", icon='BRUSH_DATA')
            
            # Existing biome selection buttons (keep for manual mode)
            layout.separator()
            col = layout.column(align=True)
            col.label(text="Biome Selection (Manual):", icon='BRUSH_DATA')
            
            # Current biome display
            current_biome_display = get_biome_display_name(props.current_biome)
            col.label(text=f"Current: {current_biome_display}")
            
            # Individual biome buttons (preserve existing functionality)
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
            
            col.separator()
            
            # Preview system controls
            col.label(text="Apply Biome Previews:", icon='MODIFIER')
            preview_row = col.row(align=True)
            op = preview_row.operator("oneill.apply_biome_preview", text="Mountains")
            op.biome_type = 'MOUNTAINS'
            op = preview_row.operator("oneill.apply_biome_preview", text="Ocean") 
            op.biome_type = 'OCEAN'
            
            col.separator()
            
            # Control buttons
            col.operator("oneill.remove_all_previews")
            col.separator()
            col.operator("oneill.finish_terrain_painting")
            col.operator("oneill.exit_painting_mode")
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Status indicator
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
        box.prop(props, "subdivision_levels")
        box.operator("oneill.unwrap_to_flat") 
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Paint Terrain Biomes (Enhanced with Phase 2A)
        box = layout.box()
        box.label(text="4. Paint Terrain Biomes", icon='BRUSH_DATA')
        
        # Use the enhanced painting controls
        self.draw_enhanced_painting_controls(context, box)
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")

# ========================= REGISTRATION (FROM ARCHIVE) =========================

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
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize grid overlay
    global grid_overlay
    grid_overlay = TerrainPaintingGridOverlay()
    
    print("="*60)
    print("O'Neill Terrain Generator v2.3.1 - WORKING WORKFLOW RESTORED")
    print("✅ Archive implementation successfully loaded")
    print("🎯 Steps 1-4 now functional with complete logic")
    print("🏔️ Complex displacement and preview systems active")
    print("🎨 Canvas management and split workspace ready")
    print("⚡ Real-time paint monitoring available")
    print("="*60)

def unregister():
    """Unregister all classes and properties"""
    # Disable grid overlay
    global grid_overlay
    if grid_overlay:
        grid_overlay.disable()
        
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Remove scene property
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    print("O'Neill Terrain Generator v2.3.1 - RESTORED VERSION unregistered")

if __name__ == "__main__":
    register()
