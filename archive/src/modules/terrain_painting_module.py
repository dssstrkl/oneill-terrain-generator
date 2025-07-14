# terrain_painting.py - Independent Terrain Painting System for O'Neill Terrain Generator
# MIT License - Clean room implementation, no Paint System GPL dependency
# Copyright (c) 2025 Paul Ward

import bpy
from bpy.types import Operator, Panel, PropertyGroup, Context, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty, IntProperty
from mathutils import Vector
import bmesh
import os

# Biome definitions
BIOME_TYPES = [
    ('mountains', '🏔️ Mountains', 'Mountain terrain with peaks and ridges'),
    ('canyons', '🏜️ Canyons', 'Canyon terrain with deep valleys'),
    ('hills', '🏞️ Hills', 'Rolling hills terrain'),
    ('desert', '🌵 Desert', 'Desert terrain with dunes'),
    ('ocean', '🌊 Ocean', 'Ocean terrain with underwater features')
]

class TerrainCanvasBuilder:
    """Creates horizontal concatenated heightmap canvas for unified painting"""
    
    @staticmethod
    def get_flat_objects_with_heightmaps():
        """Find all flat objects that have heightmaps"""
        flat_objects = []
        for obj in bpy.context.scene.objects:
            if (obj.type == 'MESH' and 
                hasattr(obj, 'oneill_flat_object') and 
                obj.oneill_flat_object and
                hasattr(obj, 'oneill_heightmap_name') and
                obj.oneill_heightmap_name):
                flat_objects.append(obj)
        
        # Sort by location X for consistent horizontal ordering
        flat_objects.sort(key=lambda obj: obj.location.x)
        return flat_objects
    
    @staticmethod
    def create_horizontal_canvas(flat_objects):
        """Create horizontal concatenated canvas from heightmaps"""
        if not flat_objects:
            return None
            
        heightmaps = []
        total_width = 0
        max_height = 0
        
        # Collect heightmap data
        for obj in flat_objects:
            heightmap_name = obj.oneill_heightmap_name
            if heightmap_name in bpy.data.images:
                img = bpy.data.images[heightmap_name]
                heightmaps.append(img)
                total_width += img.size[0]
                max_height = max(max_height, img.size[1])
        
        if not heightmaps:
            return None
        
        # Create canvas image
        canvas_name = "TerrainPainting_Canvas"
        if canvas_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[canvas_name])
        
        canvas = bpy.data.images.new(
            canvas_name, 
            width=total_width, 
            height=max_height,
            alpha=False
        )
        
        # Populate canvas with horizontal concatenation
        canvas_pixels = [0.0] * (total_width * max_height * 4)  # RGBA
        current_x = 0
        
        for img in heightmaps:
            img_width, img_height = img.size
            img_pixels = list(img.pixels)
            
            # Copy image data to canvas
            for y in range(img_height):
                for x in range(img_width):
                    img_idx = (y * img_width + x) * 4
                    canvas_idx = (y * total_width + (current_x + x)) * 4
                    
                    # Copy RGBA
                    for channel in range(4):
                        if img_idx + channel < len(img_pixels):
                            canvas_pixels[canvas_idx + channel] = img_pixels[img_idx + channel]
            
            current_x += img_width
        
        canvas.pixels = canvas_pixels
        canvas.update()
        
        return canvas

class BiomeMaskManager:
    """Manages biome painting masks for terrain assignment"""
    
    @staticmethod
    def create_biome_masks(canvas_image):
        """Create mask images for each biome type"""
        if not canvas_image:
            return {}
            
        masks = {}
        width, height = canvas_image.size
        
        for biome_id, biome_name, biome_desc in BIOME_TYPES:
            mask_name = f"TerrainMask_{biome_id.title()}"
            
            # Remove existing mask
            if mask_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[mask_name])
            
            # Create new mask
            mask = bpy.data.images.new(
                mask_name,
                width=width,
                height=height,
                alpha=False
            )
            
            # Initialize to black (no biome assignment)
            mask_pixels = [0.0] * (width * height * 4)
            mask.pixels = mask_pixels
            mask.update()
            
            masks[biome_id] = mask
        
        return masks

class TerrainPaintingProperties(PropertyGroup):
    """Properties for terrain painting system"""
    
    painting_active: BoolProperty(
        name="Painting Active",
        description="Whether terrain painting mode is active",
        default=False
    )
    
    current_biome: EnumProperty(
        name="Current Biome",
        description="Currently selected biome for painting",
        items=BIOME_TYPES,
        default='mountains'
    )
    
    brush_size: FloatProperty(
        name="Brush Size",
        description="Size of the painting brush",
        default=0.1,
        min=0.01,
        max=1.0
    )
    
    brush_strength: FloatProperty(
        name="Brush Strength",
        description="Strength of the painting brush",
        default=1.0,
        min=0.1,
        max=2.0
    )
    
    canvas_image_name: StringProperty(
        name="Canvas Image",
        description="Name of the canvas image for painting"
    )

class ONEILL_OT_StartTerrainPainting(Operator):
    """Start terrain painting mode with canvas creation"""
    bl_idname = "oneill.start_terrain_painting"
    bl_label = "🎨 Paint Terrain Biomes"
    bl_description = "Start painting terrain biomes on heightmap canvas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.terrain_painting_props
        
        # Get flat objects with heightmaps
        flat_objects = TerrainCanvasBuilder.get_flat_objects_with_heightmaps()
        if not flat_objects:
            self.report({'ERROR'}, "No flat objects with heightmaps found. Complete steps 1-3 first.")
            return {'CANCELLED'}
        
        # Create horizontal canvas
        canvas = TerrainCanvasBuilder.create_horizontal_canvas(flat_objects)
        if not canvas:
            self.report({'ERROR'}, "Failed to create painting canvas from heightmaps")
            return {'CANCELLED'}
        
        # Create biome masks
        masks = BiomeMaskManager.create_biome_masks(canvas)
        if not masks:
            self.report({'ERROR'}, "Failed to create biome masks")
            return {'CANCELLED'}
        
        # Set up painting properties
        props.painting_active = True
        props.canvas_image_name = canvas.name
        
        # Set up workspace for painting
        self.setup_painting_workspace(context, canvas)
        
        self.report({'INFO'}, f"Terrain painting started. Canvas: {canvas.size[0]}x{canvas.size[1]}")
        return {'FINISHED'}
    
    def setup_painting_workspace(self, context, canvas):
        """Set up the workspace for terrain painting"""
        # Try to set image editor to show canvas
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if hasattr(space, 'image'):
                        space.image = canvas
                        # Set to paint mode if possible
                        if hasattr(context, 'object') and context.object:
                            try:
                                bpy.ops.paint.texture_paint_toggle()
                            except:
                                pass  # Might already be in paint mode
                        break
                break

class ONEILL_OT_SelectPaintingBiome(Operator):
    """Select biome for painting"""
    bl_idname = "oneill.select_painting_biome"
    bl_label = "Select Biome"
    bl_description = "Select biome type for terrain painting"
    bl_options = {'REGISTER'}
    
    biome_type: StringProperty()
    
    def execute(self, context):
        props = context.scene.terrain_painting_props
        props.current_biome = self.biome_type
        
        # Update brush settings for biome
        self.update_brush_for_biome(context, self.biome_type)
        
        self.report({'INFO'}, f"Selected biome: {self.biome_type}")
        return {'FINISHED'}
    
    def update_brush_for_biome(self, context, biome_type):
        """Update brush color/settings for selected biome"""
        # Define biome colors for visual feedback
        biome_colors = {
            'mountains': (0.8, 0.8, 0.9, 1.0),  # Light blue-gray
            'canyons': (0.8, 0.5, 0.3, 1.0),    # Orange-brown
            'hills': (0.4, 0.8, 0.3, 1.0),      # Green
            'desert': (0.9, 0.8, 0.4, 1.0),     # Sandy yellow
            'ocean': (0.2, 0.4, 0.8, 1.0)       # Blue
        }
        
        if biome_type in biome_colors:
            # Try to set brush color
            try:
                if hasattr(bpy.context.tool_settings, 'image_paint'):
                    brush = bpy.context.tool_settings.image_paint.brush
                    if brush:
                        brush.color = biome_colors[biome_type][:3]
            except:
                pass  # Brush might not be available

class ONEILL_OT_FinishTerrainPainting(Operator):
    """Finish terrain painting and process results"""
    bl_idname = "oneill.finish_terrain_painting"
    bl_label = "✅ Finish Painting"
    bl_description = "Finish terrain painting and apply biome assignments"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.terrain_painting_props
        
        if not props.painting_active:
            self.report({'ERROR'}, "Terrain painting is not active")
            return {'CANCELLED'}
        
        # Process painted masks and assign to terrain
        success = self.process_painted_terrain(context)
        
        if success:
            props.painting_active = False
            self.report({'INFO'}, "Terrain painting completed successfully")
            
            # Return to 3D viewport
            self.restore_3d_viewport(context)
        else:
            self.report({'ERROR'}, "Failed to process painted terrain")
        
        return {'FINISHED'}
    
    def process_painted_terrain(self, context):
        """Process the painted masks and create terrain assignments"""
        # This will be expanded to interface with geometry nodes
        # For now, just validate that masks exist
        
        mask_count = 0
        for biome_id, _, _ in BIOME_TYPES:
            mask_name = f"TerrainMask_{biome_id.title()}"
            if mask_name in bpy.data.images:
                mask_count += 1
        
        return mask_count > 0
    
    def restore_3d_viewport(self, context):
        """Restore 3D viewport after painting"""
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.type = 'VIEW_3D'
                break

class ONEILL_PT_TerrainPainting(Panel):
    """Panel for terrain painting controls"""
    bl_label = "Terrain Painting"
    bl_idname = "ONEILL_PT_terrain_painting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "O'Neill Terrain"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.terrain_painting_props
        
        if not props.painting_active:
            # Start painting button
            layout.operator("oneill.start_terrain_painting", icon='BRUSH_DATA')
        else:
            # Painting controls
            box = layout.box()
            box.label(text="🎨 Painting Mode Active", icon='BRUSH_DATA')
            
            # Current biome display
            row = box.row()
            row.label(text=f"Current: {props.current_biome.title()}")
            
            # Biome selection buttons
            col = box.column(align=True)
            for biome_id, biome_name, biome_desc in BIOME_TYPES:
                op = col.operator("oneill.select_painting_biome", text=biome_name)
                op.biome_type = biome_id
                if props.current_biome == biome_id:
                    op.bl_options = {'INTERNAL'}  # Highlight current selection
            
            # Brush controls
            box.separator()
            box.prop(props, "brush_size")
            box.prop(props, "brush_strength")
            
            # Finish button
            box.separator()
            box.operator("oneill.finish_terrain_painting", icon='CHECKMARK')

# Registration
classes = [
    TerrainPaintingProperties,
    ONEILL_OT_StartTerrainPainting,
    ONEILL_OT_SelectPaintingBiome,
    ONEILL_OT_FinishTerrainPainting,
    ONEILL_PT_TerrainPainting,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.terrain_painting_props = bpy.props.PointerProperty(
        type=TerrainPaintingProperties
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    if hasattr(bpy.types.Scene, 'terrain_painting_props'):
        del bpy.types.Scene.terrain_painting_props

if __name__ == "__main__":
    register()
