# ========================= UI PANEL (FIXED) =========================

class ONEILL_PT_MainPanel(Panel):
    """FIXED: Main O'Neill Terrain Generator panel with enhanced diagnostic tools"""
    bl_label = "O'Neill Terrain Generator v2.5.0 - FIXED"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # System Status Box
        status_box = layout.box()
        status_box.label(text="🔧 System Status", icon='SETTINGS')
        
        # Enhanced status indicators
        if props.painting_mode:
            status_box.label(text="🎨 Painting Mode: Active", icon='BRUSH_DATA')
        else:
            status_box.label(text="⚪ Painting Mode: Inactive", icon='RADIOBUT_OFF')
        
        # Check if enhanced spatial mapping is available
        enhanced_mapper = get_enhanced_spatial_mapping()
        if enhanced_mapper:
            status_box.label(text="✅ Enhanced Mapping: Available", icon='CHECKMARK')
        else:
            status_box.label(text="⚠️ Enhanced Mapping: Unavailable", icon='ERROR')
        
        # Canvas persistence status
        persistence_manager = get_canvas_persistence_manager()
        if persistence_manager:
            status_box.label(text="✅ Canvas Persistence: Available", icon='CHECKMARK')
        else:
            status_box.label(text="⚠️ Canvas Persistence: Unavailable", icon='ERROR')
        
        # Quick diagnostic tools
        diagnostic_row = status_box.row(align=True)
        diagnostic_row.operator("oneill.diagnostic_check", text="🔧 Diagnostic", icon='TOOL_SETTINGS')
        diagnostic_row.operator("oneill.reset_system", text="🔄 Reset", icon='FILE_REFRESH')
        
        layout.separator()
        
        # Step 1: Align Cylinders
        box = layout.box()
        box.label(text="1. Align Cylinders", icon='OBJECT_DATA')
        row = box.row()
        row.prop(props, "alignment_axis")
        box.operator("oneill.align_cylinders")
        
        # Step 2: Unwrap to Flat
        box = layout.box()
        box.label(text="2. Unwrap to Flat", icon='MOD_UVPROJECT')
        
        col = box.column()
        col.prop(props, "subdivision_levels")
        if props.subdivision_levels >= 3:
            warning_box = col.box()
            warning_box.label(text="⚠️ DANGER: Level 3 = 69M vertices!", icon='ERROR')
            warning_box.label(text="This may crash Blender!")
        elif props.subdivision_levels >= 2:
            warning_box = col.box()
            warning_box.label(text="⚠️ Level 2: High vertex count", icon='TIME')
            warning_box.label(text="Use with caution")
        else:
            info_box = col.box()
            info_box.label(text="✅ Safe performance level", icon='CHECKMARK')
        
        box.operator("oneill.unwrap_to_flat")
               
        # Step 3: Create Heightmaps
        box = layout.box()
        box.label(text="3. Create Heightmaps", icon='IMAGE_DATA')
        box.prop(props, "heightmap_resolution")
        box.operator("oneill.create_heightmaps")
        
        # Step 4: Enhanced Terrain System
        box = layout.box()
        box.label(text="4. Terrain Generation", icon='BRUSH_DATA')
        
        # Check for flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        
        if not flat_objects:
            box.label(text="❌ No flat objects found", icon='ERROR')
            box.label(text="Complete steps 1-3 first")
        else:
            if not props.painting_mode:
                # Start enhanced terrain painting
                box.operator("oneill.start_terrain_painting", text="🎨 Start Enhanced Terrain Painting", icon='BRUSH_DATA')
                
                # Procedural generation option
                box.separator()
                procedural_box = box.box()
                procedural_box.label(text="OR use procedural generation:", icon='MODIFIER')
                row = procedural_box.row()
                row.prop(props, "terrain_scale")
                row.prop(props, "noise_scale")
                procedural_box.operator("oneill.generate_terrain")
                
            else:
                # Enhanced painting mode controls
                col = box.column(align=True)
                
                # Enhanced mapping status in painting mode
                if props.enhanced_mapping_available:
                    status_label = "✅ Enhanced Mapping Active"
                else:
                    status_label = "⚠️ Using Basic Mapping"
                box.label(text=status_label)
                
                col.operator("oneill.detect_paint_apply_previews", text="🎨 Apply Spatial Mapping", icon='BRUSH_DATA')
                col.separator()
                col.operator("oneill.validate_terrain_layout", text="🔍 Validate Layout", icon='CHECKMARK')
                
                # Canvas info
                canvas = bpy.data.images.get("ONeill_Terrain_Canvas")
                if canvas:
                    info_text = f"Canvas: {canvas.size[0]}x{canvas.size[1]}"
                    box.label(text=info_text, icon='IMAGE_DATA')
        
        # Step 5: Rewrap to Cylinders
        box = layout.box()
        box.label(text="5. Rewrap to Cylinders", icon='MESH_CYLINDER')
        box.operator("oneill.rewrap_to_cylinders")
        
        # Advanced Tools
        layout.separator()
        advanced_box = layout.box()
        advanced_box.label(text="🔧 Advanced Tools", icon='TOOL_SETTINGS')
        
        # Object counts for debugging
        heightmap_objects = [obj for obj in flat_objects if obj.get("heightmap_image")] if flat_objects else []
        advanced_box.label(text=f"Flat objects: {len(flat_objects)}")
        advanced_box.label(text=f"With heightmaps: {len(heightmap_objects)}")

# ========================= REGISTRATION =========================

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_ValidateTerrainLayout,
    ONEILL_OT_GenerateTerrain,
    ONEILL_OT_RewrapToCylinders,
    ONEILL_OT_DiagnosticCheck,
    ONEILL_OT_ResetSystem,
    ONEILL_PT_MainPanel,
]

def register():
    """FIXED: Register all classes with proper error handling"""
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
            
        bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
        
        # Register global function in driver namespace with error handling
        try:
            bpy.app.driver_namespace['apply_enhanced_spatial_mapping'] = apply_enhanced_spatial_mapping_global
            print("✅ Global enhanced mapping function registered")
        except Exception as e:
            print(f"⚠️ Failed to register global function: {e}")
        
        print("="*60)
        print("O'Neill Terrain Generator v2.5.0 - FIXED VERSION")
        print("🔧 FIXED: Enhanced spatial mapping integration issues")
        print("🛡️ ROBUST: Error handling and graceful fallback")
        print("🎯 ENHANCED: True 1:1 spatial canvas-to-object mapping")
        print("🎨 IMPROVED: Multi-biome support with seamless transitions")
        print("🛡️ PROTECTED: Canvas persistence prevents paint data loss")
        print("⚡ SAFE: Performance warnings and diagnostic tools")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Registration failed: {e}")

def unregister():
    """FIXED: Unregister all classes with proper cleanup"""
    try:
        # Clean up global functions
        if 'apply_enhanced_spatial_mapping' in bpy.app.driver_namespace:
            del bpy.app.driver_namespace['apply_enhanced_spatial_mapping']
        
        # Unregister classes
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
            except Exception as e:
                print(f"⚠️ Failed to unregister {cls.__name__}: {e}")
                
        # Remove scene property
        if hasattr(bpy.types.Scene, 'oneill_props'):
            del bpy.types.Scene.oneill_props
            
        print("O'Neill Terrain Generator v2.5.0 - FIXED VERSION unregistered")
        
    except Exception as e:
        print(f"❌ Unregistration failed: {e}")

if __name__ == "__main__":
    register()
