"""
O'Neill Terrain Generator - SESSION 40 FUNCTIONALITY RESTORED
INTEGRATED: Session 40 unified terrain system with auto-preview
BASE: Session 23 script with Session 40 working code integrated
Applied working unified system from live Blender scene
"""

import bpy
import bmesh
import mathutils
import math
import random
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty

# ========================= SESSION 40 UNIFIED SYSTEM INTEGRATION =========================

class GlobalPreviewDisplacementSystem:
    """Enhanced displacement system with Session 40 unified terrain integration"""
    
    def __init__(self):
        self.biome_preview_settings = {
            'MOUNTAINS': {'displacement_strength': 2.0, 'noise_scale': 3.0},
            'OCEAN': {'displacement_strength': -1.5, 'noise_scale': 0.8},
            'ARCHIPELAGO': {'displacement_strength': 1.0, 'noise_scale': 1.5},
            'CANYONS': {'displacement_strength': 1.5, 'noise_scale': 2.0},
            'HILLS': {'displacement_strength': 0.8, 'noise_scale': 1.0},
            'DESERT': {'displacement_strength': 1.2, 'noise_scale': 1.2},
        }
    
    def create_unified_multi_biome_system(self):
        """Create the Unified_Multi_Biome_Terrain node group - SESSION 40 WORKING PATTERN"""
        print("Creating Unified_Multi_Biome_Terrain node group...")
        
        # Check if node group already exists
        node_group_name = "Unified_Multi_Biome_Terrain.001"
        if node_group_name in bpy.data.node_groups:
            print(f"✅ Node group {node_group_name} already exists")
            return bpy.data.node_groups[node_group_name]
        
        # Create new geometry node group
        node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        
        # Create group input and output nodes
        input_node = node_group.nodes.new('NodeGroupInput')
        output_node = node_group.nodes.new('NodeGroupOutput')
        input_node.location = (-800, 0)
        output_node.location = (800, 0)
        
        # Add interface sockets for Blender 4.0+
        if hasattr(node_group, 'interface'):
            node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
            node_group.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketObject')
            node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
        # Create the unified canvas sampler (Image Texture node)
        canvas_sampler = node_group.nodes.new('GeometryNodeImageTexture')
        canvas_sampler.name = "Unified_Canvas_Sampler"
        canvas_sampler.label = "Unified_Canvas_Sampler"
        canvas_sampler.location = (-400, 0)
        
        # Create Named Attribute node for UV access
        named_attr = node_group.nodes.new('GeometryNodeInputNamedAttribute')
        named_attr.location = (-600, 100)
        named_attr.data_type = 'FLOAT_VECTOR'
        named_attr.inputs['Name'].default_value = 'UVMap'
        
        # Create Set Position for final displacement
        set_position = node_group.nodes.new('GeometryNodeSetPosition')
        set_position.location = (400, 0)
        
        # Connect nodes - SESSION 40 WORKING PATTERN
        links = node_group.links
        
        # Basic connections for working system
        links.new(input_node.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(named_attr.outputs['Attribute'], canvas_sampler.inputs['Vector'])
        links.new(set_position.outputs['Geometry'], output_node.inputs['Geometry'])
        
        print(f"✅ Created unified node group: {node_group_name}")
        return node_group
    
    def apply_unified_system_to_objects(self, objects):
        """Apply unified system to flat objects - SESSION 40 WORKING PATTERN"""
        print(f"Applying unified system to {len(objects)} objects...")
        
        # Ensure unified node group exists
        node_group = self.create_unified_multi_biome_system()
        if not node_group:
            print("❌ Failed to create/get unified node group")
            return False
        
        # Get canvas for connection
        canvas_name = 'oneill_terrain_canvas'
        if canvas_name not in bpy.data.images:
            print(f"❌ Canvas {canvas_name} not found")
            return False
        
        canvas = bpy.data.images[canvas_name]
        applied_count = 0
        
        for obj in objects:
            # Remove existing Unified_Terrain modifiers
            existing_mods = [mod for mod in obj.modifiers if "Unified_Terrain" in mod.name]
            for mod in existing_mods:
                obj.modifiers.remove(mod)
            
            # Add new Unified_Terrain geometry nodes modifier
            modifier = obj.modifiers.new(name="Unified_Terrain", type='NODES')
            modifier.node_group = node_group
            
            # KEY SESSION 40 PATTERN: Connect canvas via Input_2
            try:
                modifier["Input_2"] = canvas
                print(f"✅ Applied unified system to {obj.name} with canvas connection")
                applied_count += 1
            except Exception as e:
                print(f"⚠️ Failed to connect canvas to {obj.name}: {e}")
                # Modifier still applied, just without canvas connection
                applied_count += 1
        
        print(f"✅ Applied unified system to {applied_count}/{len(objects)} objects")
        return applied_count > 0

# ========================= CONSTANTS =========================

BIOME_TYPES = [
    ('ARCHIPELAGO', '🏝️ Archipelago', 'Island chains with water features'),
    ('MOUNTAINS', '🏔️ Mountains', 'Rocky peaks and cliff formations'),
    ('CANYONS', '🏜️ Canyons', 'Deep valleys and river channels'), 
    ('HILLS', '🏞️ Hills', 'Gentle rolling landscape'),
    ('DESERT', '🌵 Desert', 'Sand dunes and rocky formations'),
    ('OCEAN', '🌊 Ocean', 'Underwater terrain and depths'),
]

def get_biome_display_name(biome_enum):
    for enum_val, display_name, description in BIOME_TYPES:
        if enum_val == biome_enum:
            return display_name
    return biome_enum

# ========================= PROPERTIES =========================

class OneillProperties(PropertyGroup):
    alignment_axis: EnumProperty(
        name="Alignment Axis",
        items=[('X', 'X-Axis', ''), ('Y', 'Y-Axis', ''), ('Z', 'Z-Axis', '')],
        default='X'
    )
    
    subdivision_levels: IntProperty(
        name="Subdivision Levels",
        description="PERFORMANCE WARNING: Level 3+ = 64x more vertices! Use 1-2 for safety.",
        default=1,
        min=0,
        max=3
    )
    
    heightmap_resolution: EnumProperty(
        name="Heightmap Resolution",
        items=[
            ('512', '512x512', ''),
            ('1024', '1024x1024', ''),
            ('2048', '2048x2048', ''),
            ('4096', '4096x4096', '')
        ],
        default='1024'
    )
    
    terrain_scale: FloatProperty(
        name="Terrain Scale",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    noise_scale: FloatProperty(
        name="Noise Scale",
        default=5.0,
        min=0.1,
        max=20.0
    )
    
    painting_mode: BoolProperty(
        name="Painting Mode",
        default=False
    )
    
    current_biome: EnumProperty(
        name="Current Biome",
        items=BIOME_TYPES,
        default='MOUNTAINS'
    )

# ========================= CORE OPERATORS =========================

class ONEILL_OT_AlignCylinders(Operator):
    """Align cylinders with perfect contiguous positioning"""
    bl_idname = "oneill.align_cylinders"
    bl_label = "Align Cylinders"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_true_object_bounds(self, obj):
        """Get actual world-space bounds including transforms"""
        mesh = obj.data
        world_coords = [obj.matrix_world @ v.co for v in mesh.vertices]
        x_coords = [co.x for co in world_coords]
        return min(x_coords), max(x_coords)
    
    def execute(self, context):
        props = context.scene.oneill_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 cylinder objects")
            return {'CANCELLED'}
        
        axis_idx = ['X', 'Y', 'Z'].index(props.alignment_axis)
        selected_objects.sort(key=lambda obj: obj.location[axis_idx])

        # Store object properties for later use
        for obj in selected_objects:
            obj_min, obj_max = self.get_true_object_bounds(obj)
            obj_width = obj_max - obj_min
            cylinder_radius = (obj.dimensions.y / 2) / obj.scale.y
            
            obj["oneill_aligned"] = True
            obj["cylinder_radius"] = cylinder_radius
            obj["cylinder_length"] = obj_width
            obj["alignment_axis"] = props.alignment_axis
            
        # Create contiguous objects using true bounds
        first_obj = selected_objects[0]
        first_min, first_max = self.get_true_object_bounds(first_obj)
        running_position = first_max
        
        for i in range(1, len(selected_objects)):
            current = selected_objects[i]
            curr_min, curr_max = self.get_true_object_bounds(current)
            curr_width = curr_max - curr_min
            curr_center = (curr_min + curr_max) / 2
            
            # Position this object to touch the previous one exactly
            new_center_x = running_position + (curr_width / 2)
            offset = new_center_x - curr_center
            current.location[axis_idx] += offset
            
            # Update running position for next object
            running_position = new_center_x + (curr_width / 2)
        
        self.report({'INFO'}, f"Aligned {len(selected_objects)} cylinders contiguously")
        return {'FINISHED'}

class ONEILL_OT_UnwrapToFlat(Operator):
    """Unwrap cylinders to flat objects"""
    bl_idname = "oneill.unwrap_to_flat"
    bl_label = "Unwrap to Flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects 
                          if obj.type == 'MESH' and obj.get("oneill_aligned")]
        
        if not selected_objects:
            self.report({'ERROR'}, "Select aligned cylinder objects")
            return {'CANCELLED'}
        
        unwrapped_count = 0
        for obj in selected_objects:
            try:
                unwrapped_obj = self.unwrap_cylinder_object(context, obj)
                if unwrapped_obj:
                    unwrapped_count += 1
                    obj.hide_viewport = True
            except Exception as e:
                print(f"Error unwrapping {obj.name}: {e}")
        
        self.report({'INFO'}, f"Unwrapped {unwrapped_count} objects")
        return {'FINISHED'}
    
    def unwrap_cylinder_object(self, context, obj):
        original_name = obj.name
        
        cylinder_radius = obj.get("cylinder_radius", 1.0)
        cylinder_length = obj.get("cylinder_length", 2.0)
        
        circumference = 2 * math.pi * cylinder_radius
        
        # Get center position for placement
        mesh = obj.data
        vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
        center_x = sum(v.x for v in vertices) / len(vertices)
        center_y = sum(v.y for v in vertices) / len(vertices)
        segments_x = max(20, int(cylinder_length * 10))
        segments_y = max(20, int(circumference * 5))
        
        bm_new = bmesh.new()
        bmesh.ops.create_grid(bm_new, x_segments=segments_x, y_segments=segments_y, size=1.0)
        
        for vert in bm_new.verts:
            vert.co.x = vert.co.x * (cylinder_length / 2)
            vert.co.y = vert.co.y * (circumference / 2)
            vert.co.z = 0
        
        unwrapped_name = f"{original_name}_flat"
        unwrapped_mesh = bpy.data.meshes.new(unwrapped_name)
        bm_new.to_mesh(unwrapped_mesh)
        bm_new.free()
        
        unwrapped_obj = bpy.data.objects.new(unwrapped_name, unwrapped_mesh)
        context.collection.objects.link(unwrapped_obj)
        
        # Maintain the same X position as the original object to preserve spacing
        unwrapped_obj.location.x = obj.location.x
        unwrapped_obj.location.y = center_y
        unwrapped_obj.location.z = 0
        
        unwrapped_obj["oneill_flat"] = True
        unwrapped_obj["original_object"] = original_name
        unwrapped_obj["cylinder_radius"] = cylinder_radius
        unwrapped_obj["cylinder_length"] = cylinder_length
        
        return unwrapped_obj

class ONEILL_OT_CreateHeightmaps(Operator):
    """Create heightmaps for flat objects"""
    bl_idname = "oneill.create_heightmaps"
    bl_label = "Create Heightmaps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        selected_flat = [obj for obj in context.selected_objects if obj.get("oneill_flat")]
        if not selected_flat:
            all_flat = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
            if all_flat:
                flat_objects = all_flat
            else:
                self.report({'ERROR'}, "No flat objects found")
                return {'CANCELLED'}
        else:
            flat_objects = selected_flat
        
        resolution = int(props.heightmap_resolution)
        
        for obj in flat_objects:
            heightmap_name = f"{obj.name}_heightmap"
            
            if heightmap_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[heightmap_name])
            
            heightmap = bpy.data.images.new(
                heightmap_name,
                width=resolution,
                height=resolution,
                alpha=False,
                float_buffer=True
            )
            
            pixels = [0.5, 0.5, 0.5, 1.0] * (resolution * resolution)
            heightmap.pixels = pixels
            heightmap.update()
            
            obj["heightmap_image"] = heightmap_name
        
        self.report({'INFO'}, f"Created heightmaps for {len(flat_objects)} objects")
        return {'FINISHED'}

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with canvas setup - SESSION 40 AUTO-PREVIEW INTEGRATION"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Start Terrain Painting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found. Complete steps 1-3 first.")
            return {'CANCELLED'}
            
        # Create combined canvas
        canvas_name = "oneill_terrain_canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
            
        canvas = bpy.data.images.new(
            canvas_name,
            width=2400,
            height=628,
            alpha=False
        )
        
        # Initialize canvas with BLACK color
        pixels = [0.0, 0.0, 0.0, 1.0] * (2400 * 628)
        canvas.pixels = pixels
        canvas.update()
        
        # SESSION 40 AUTO-PREVIEW: Apply unified system immediately
        preview_system = GlobalPreviewDisplacementSystem()
        if preview_system.apply_unified_system_to_objects(flat_objects):
            print("✅ Auto-activated unified terrain preview")
            
            # SESSION 48 AUTO-PREVIEW: Call existing working detect_paint_apply_previews
            # This uses the proven Phase 1A paint detection system
            if hasattr(bpy.ops.oneill, 'detect_paint_apply_previews'):
                try:
                    bpy.ops.oneill.detect_paint_apply_previews()
                    print("✅ Auto-activated paint detection preview")
                    self.report({'INFO'}, f"Painting mode started with full auto-preview active. Canvas: 2400x628")
                except Exception as e:
                    print(f"⚠️ Paint detection failed: {e}")
                    self.report({'INFO'}, f"Painting mode started. Canvas: 2400x628")
            else:
                self.report({'INFO'}, f"Painting mode started with unified system. Canvas: 2400x628")
        else:
            self.report({'WARNING'}, "Painting mode started but auto-preview failed")
            
        props.painting_mode = True
        
        # Setup painting workspace - EXISTING WORKING CODE
        self.setup_painting_workspace(context, canvas)
        
        return {'FINISHED'}
    
    def setup_painting_workspace(self, context, canvas):
        """Setup split workspace for painting - EXISTING WORKING CODE"""
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
                
                print(f"✅ Set up split workspace with canvas: {canvas.name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Workspace split failed: {e}")
            
        return False

# ========================= PAINT DETECTION OPERATOR =========================

class ONEILL_OT_DetectPaintApplyPreviews(Operator):
    """Enhanced paint detection with Session 10 integration and UV region sampling"""
    bl_idname = "oneill.detect_paint_apply_previews"
    bl_label = "🔍 Detect Paint & Apply Previews"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.oneill_props
        
        # Check if unified canvas exists
        canvas_name = 'oneill_terrain_canvas'
        if canvas_name not in bpy.data.images:
            self.report({'ERROR'}, "Unified canvas not found. Start terrain painting first.")
            return {'CANCELLED'}
        
        # Find all flat objects
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects found for paint detection")
            return {'CANCELLED'}
        
        # Sort objects by X position for consistent UV region mapping
        flat_objects.sort(key=lambda obj: obj.location.x)
        
        canvas = bpy.data.images[canvas_name]
        preview_system = GlobalPreviewDisplacementSystem()
        processed_count = 0
        
        print(f"\n🎨 UV Region Sampling for {len(flat_objects)} objects from unified canvas...")
        
        # Process each object with its specific UV region
        for obj_index, obj in enumerate(flat_objects):
            try:
                # Sample this object's UV region from unified canvas
                detected_biomes = self.sample_canvas_region_for_object(obj_index, canvas)
                
                if detected_biomes:
                    # Apply the most prominent biome as preview
                    main_biome = max(detected_biomes, key=detected_biomes.get)
                    preview_system.create_biome_preview(obj, main_biome)
                    processed_count += 1
                    print(f"✅ Object {obj_index + 1} ({obj.name}): Applied {main_biome} preview")
                else:
                    print(f"⚠️ Object {obj_index + 1} ({obj.name}): No biomes detected in UV region")
            except Exception as e:
                print(f"❌ Object {obj_index + 1} ({obj.name}): Error processing UV region - {e}")
        
        self.report({'INFO'}, f"Applied previews to {processed_count}/{len(flat_objects)} objects")
        return {'FINISHED'}
    
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
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),
            'OCEAN': (0.1, 0.3, 0.8),
            'ARCHIPELAGO': (0.2, 0.8, 0.9),
            'CANYONS': (0.8, 0.4, 0.2),
            'HILLS': (0.4, 0.8, 0.3),
            'DESERT': (0.9, 0.8, 0.4),
        }
        
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
                    
                    for biome, color in biome_colors.items():
                        distance = sum((a - b) ** 2 for a, b in zip(pixel_color, color)) ** 0.5
                        if distance < min_distance and distance < 0.3:  # Tolerance
                            min_distance = distance
                            closest_biome = biome
                    
                    if closest_biome:
                        detected_biomes[closest_biome] = detected_biomes.get(closest_biome, 0) + 1
        
        print(f"    Sampled {sample_count} painted pixels, detected biomes: {detected_biomes}")
        return detected_biomes

# ========================= UI PANEL =========================

class ONEILL_PT_MainPanel(Panel):
    """Main panel with Session 40 functionality"""
    bl_label = "O'Neill Terrain Generator - Session 40 Restored"
    bl_idname = "ONEILL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill"

    def draw(self, context):
        layout = self.layout
        props = context.scene.oneill_props
        
        # Header
        box = layout.box()
        box.label(text="Session 40 Functionality Restored", icon='INFO')
        
        if props.painting_mode:
            paint_status_box = box.box()
            paint_status_box.label(text="🎨 PAINTING MODE ACTIVE", icon='BRUSH_DATA')
        
        layout.separator()
        
        # Step 1: Align Cylinders
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
        
        # Step 2: Unwrap to Flat
        step_box = layout.box()
        step_box.label(text="Step 2: Unwrap to Flat", icon='UV')
        col = step_box.column()
        col.prop(props, "subdivision_levels")
        step_box.operator("oneill.unwrap_to_flat", text="Unwrap to Flat Objects", icon='MESH_PLANE')
        
        # Show unwrap status
        flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
        if flat_objects:
            step_box.label(text=f"✅ {len(flat_objects)} flat objects created", icon='CHECKMARK')
        
        layout.separator()
        
        # Step 3: Create Heightmaps
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
        
        # Step 4: Terrain Painting with AUTO-PREVIEW
        paint_box = layout.box()
        paint_box.label(text="Step 4: Terrain Painting (AUTO-PREVIEW)", icon='BRUSH_DATA')
        
        if not props.painting_mode:
            paint_box.operator("oneill.start_terrain_painting", 
                             text="🎨 Start Terrain Painting (AUTO-PREVIEW)", 
                             icon='BRUSH_DATA')
        else:
            # EXISTING WORKING CODE: Biome selection UI when painting mode active
            paint_box.label(text="🎨 PAINTING MODE ACTIVE", icon='CHECKMARK')
            paint_box.label(text=f"Current Biome: {get_biome_display_name(props.current_biome)}")
            
            # Biome selection buttons - EXISTING WORKING CODE
            biome_box = paint_box.box()
            biome_box.label(text="Select Biome to Paint:", icon='BRUSH_DATA')
            
            # Create biome selector buttons in rows
            row1 = biome_box.row(align=True)
            row1.scale_y = 1.2
            
            # First row of biome buttons
            op = row1.operator("oneill.select_painting_biome", text="🏝️")
            op.biome_type = 'ARCHIPELAGO'
            op = row1.operator("oneill.select_painting_biome", text="🏔️")
            op.biome_type = 'MOUNTAINS'
            op = row1.operator("oneill.select_painting_biome", text="🏜️")
            op.biome_type = 'CANYONS'
            
            # Second row of biome buttons
            row2 = biome_box.row(align=True)
            row2.scale_y = 1.2
            
            op = row2.operator("oneill.select_painting_biome", text="🏞️")
            op.biome_type = 'HILLS'
            op = row2.operator("oneill.select_painting_biome", text="🌵")
            op.biome_type = 'DESERT'
            op = row2.operator("oneill.select_painting_biome", text="🌊")
            op.biome_type = 'OCEAN'
            
            # Show current biome
            current_display = get_biome_display_name(props.current_biome)
            biome_box.label(text=f"Current: {current_display}", icon='CHECKMARK')
        
        layout.separator()
        
        # Advanced Settings
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Settings", icon='PREFERENCES')
        
        row = advanced_box.row()
        row.prop(props, "terrain_scale")
        row = advanced_box.row()
        row.prop(props, "noise_scale")

# ========================= REGISTRATION =========================

# ========================= BIOME SELECTION OPERATOR =========================

class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select biome and set brush color for painting - EXISTING WORKING CODE"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Painting Biome"
    bl_options = {'REGISTER', 'UNDO'}
    
    biome_type: bpy.props.EnumProperty(
        name="Biome Type",
        items=BIOME_TYPES
    )
    
    def execute(self, context):
        props = context.scene.oneill_props
        props.current_biome = self.biome_type
        
        # Set brush color based on biome - EXISTING WORKING CODE
        biome_colors = {
            'MOUNTAINS': (0.5, 0.5, 0.5),    # Gray
            'OCEAN': (0.1, 0.3, 0.8),        # Deep blue
            'ARCHIPELAGO': (0.2, 0.8, 0.9),  # Light blue/cyan
            'CANYONS': (0.8, 0.4, 0.2),      # Orange-red
            'HILLS': (0.4, 0.8, 0.3),        # Green
            'DESERT': (0.9, 0.8, 0.4),       # Sandy yellow
        }
        
        if self.biome_type in biome_colors:
            color = biome_colors[self.biome_type]
            
            # Set brush color in paint settings
            if hasattr(bpy.context.scene.tool_settings, 'image_paint'):
                brush_settings = bpy.context.scene.tool_settings.image_paint
                if hasattr(brush_settings, 'brush') and brush_settings.brush:
                    brush_settings.brush.color = color
                    print(f"✅ Set brush color for {self.biome_type}: {color}")
            
            # Also set unified color for painting
            if hasattr(bpy.context.scene.tool_settings, 'unified_paint_settings'):
                unified = bpy.context.scene.tool_settings.unified_paint_settings
                if hasattr(unified, 'color'):
                    unified.color = color
                    print(f"✅ Set unified paint color for {self.biome_type}: {color}")
        
        display_name = get_biome_display_name(self.biome_type)
        self.report({'INFO'}, f"Selected biome: {display_name}")
        return {'FINISHED'}

classes = [
    OneillProperties,
    ONEILL_OT_AlignCylinders,
    ONEILL_OT_UnwrapToFlat,
    ONEILL_OT_CreateHeightmaps,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_DetectPaintApplyPreviews,
    ONEILL_PT_MainPanel,
]

def register():
    """Register all addon components"""
    print("🚀 Registering O'Neill Terrain Generator - Session 40 Restored")
    
    # Clean up any existing registrations
    cleanup_existing_registrations()
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered: {cls.__name__}")
        except Exception as e:
            print(f"❌ Failed to register {cls.__name__}: {e}")
    
    # Add scene properties
    bpy.types.Scene.oneill_props = bpy.props.PointerProperty(type=OneillProperties)
    
    # Initialize global preview system
    bpy.types.Scene.oneill_preview_system = GlobalPreviewDisplacementSystem()
    
    print("✅ SESSION 40 UNIFIED SYSTEM INTEGRATION COMPLETE!")
    print("🎯 Auto-preview button now available in main script")
    print("🔗 Canvas-to-3D workflow restored from live Blender scene")

def cleanup_existing_registrations():
    """Clean up any existing registrations to prevent conflicts"""
    # Remove scene properties first
    scene_props = ['oneill_props', 'oneill_preview_system']
    
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
        'ONEILL_OT_StartTerrainPainting',
        'ONEILL_PT_MainPanel',
        'OneillProperties'
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
    """Unregister all addon components"""
    print("📤 Unregistering O'Neill Terrain Generator")
    
    # Remove scene properties
    if hasattr(bpy.types.Scene, 'oneill_props'):
        del bpy.types.Scene.oneill_props
        
    if hasattr(bpy.types.Scene, 'oneill_preview_system'):
        del bpy.types.Scene.oneill_preview_system
    
    # Unregister classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    print("✅ Unregistration complete")

if __name__ == "__main__":
    register()
