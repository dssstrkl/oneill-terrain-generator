# SESSION 55 AUTO-PREVIEW INTEGRATION - WORKING NODE GROUP ONLY
# Minimal integration of proven SESSION 42 working node group

def create_session_42_working_node_group():
    """
    Create the exact working node group from SESSION 42
    11 nodes, 10 connections - proven to work with paint-to-terrain auto-preview
    """
    import bpy
    
    # Check if node group already exists
    node_group_name = "Unified_Multi_Biome_Terrain.001"
    if node_group_name in bpy.data.node_groups:
        print(f"✅ Working node group {node_group_name} already exists")
        return bpy.data.node_groups[node_group_name]
    
    # Create new geometry node group
    node_group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
    
    # Create nodes in exact order from SESSION 42
    group_input = node_group.nodes.new('NodeGroupInput')
    group_input.name = "Group Input"
    group_input.location = (-800.0, 0.0)
    
    group_output = node_group.nodes.new('NodeGroupOutput')
    group_output.name = "Group Output"
    group_output.location = (600.0, 0.0)
    
    named_attr = node_group.nodes.new('GeometryNodeInputNamedAttribute')
    named_attr.name = "Named Attribute"
    named_attr.location = (-700.0, -200.0)
    named_attr.data_type = 'FLOAT_VECTOR'
    named_attr.inputs['Name'].default_value = 'UVMap'
    
    canvas_sampler = node_group.nodes.new('GeometryNodeImageTexture')
    canvas_sampler.name = "Unified_Canvas_Sampler"
    canvas_sampler.location = (-500.0, -200.0)
    
    separate_xyz = node_group.nodes.new('ShaderNodeSeparateXYZ')
    separate_xyz.name = "Separate XYZ"
    separate_xyz.location = (-300.0, -200.0)
    
    color_ramp = node_group.nodes.new('ShaderNodeValToRGB')
    color_ramp.name = "Color Ramp"
    color_ramp.location = (-100.0, -200.0)
    
    noise_texture = node_group.nodes.new('ShaderNodeTexNoise')
    noise_texture.name = "Noise Texture"
    noise_texture.location = (-300.0, 100.0)
    
    position = node_group.nodes.new('GeometryNodeInputPosition')
    position.name = "Position"
    position.location = (-300.0, 300.0)
    
    math = node_group.nodes.new('ShaderNodeMath')
    math.name = "Math"
    math.location = (0.0, 0.0)
    math.operation = 'MULTIPLY'
    
    combine_xyz = node_group.nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.name = "Combine XYZ"
    combine_xyz.location = (200.0, 100.0)
    
    set_position = node_group.nodes.new('GeometryNodeSetPosition')
    set_position.name = "Set Position"
    set_position.location = (400.0, 0.0)
    
    # Create exact links from SESSION 42
    links = node_group.links
    
    # Link sequence from working system
    links.new(named_attr.outputs['Attribute'], canvas_sampler.inputs['Vector'])
    links.new(canvas_sampler.outputs['Color'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
    links.new(position.outputs['Position'], noise_texture.inputs['Vector'])
    links.new(noise_texture.outputs['Fac'], math.inputs[0])  # Value
    links.new(math.outputs['Value'], combine_xyz.inputs['Z'])
    links.new(group_input.outputs['Geometry'], set_position.inputs['Geometry'])
    links.new(combine_xyz.outputs['Vector'], set_position.inputs['Offset'])
    links.new(set_position.outputs['Geometry'], group_output.inputs['Geometry'])
    links.new(color_ramp.outputs['Color'], math.inputs[1])  # Value_001
    
    print(f"✅ Created SESSION 42 working node group: {node_group_name}")
    print(f"   - {len(node_group.nodes)} nodes")
    print(f"   - {len(node_group.links)} links")
    
    return node_group

def apply_session_42_modifiers(flat_objects, canvas):
    """
    Apply the exact SESSION 42 working modifier stack to flat objects
    """
    import bpy
    
    # Get or create the working node group
    working_node_group = create_session_42_working_node_group()
    
    applied_count = 0
    for obj in flat_objects:
        try:
            # Remove existing modifiers
            existing_mods = [mod for mod in obj.modifiers if mod.name in ["Preview_Subdivision", "Unified_Terrain"]]
            for mod in existing_mods:
                obj.modifiers.remove(mod)
            
            # Apply SESSION 42 working modifier stack
            
            # 1. Preview_Subdivision (SUBSURF) - levels=2
            subsurf = obj.modifiers.new(name="Preview_Subdivision", type='SUBSURF')
            subsurf.levels = 2
            
            # 2. Unified_Terrain (NODES) - working node group
            geo_nodes = obj.modifiers.new(name="Unified_Terrain", type='NODES')
            geo_nodes.node_group = working_node_group
            
            # 3. Connect canvas using SESSION 42 method
            img_tex_node = working_node_group.nodes.get("Unified_Canvas_Sampler")
            if img_tex_node and 'Image' in img_tex_node.inputs:
                img_tex_node.inputs['Image'].default_value = canvas
                
            applied_count += 1
            print(f"✅ Applied SESSION 42 modifiers to {obj.name}")
            
        except Exception as e:
            print(f"❌ Failed to apply modifiers to {obj.name}: {e}")
    
    print(f"✅ Applied SESSION 42 modifier stack to {applied_count}/{len(flat_objects)} objects")
    return applied_count > 0

# Usage example:
# working_node_group = create_session_42_working_node_group()
# flat_objects = [obj for obj in bpy.data.objects if obj.get("oneill_flat")]
# canvas = bpy.data.images.get("oneill_terrain_canvas")
# apply_session_42_modifiers(flat_objects, canvas)
