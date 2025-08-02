.outputs["Displacement"], disp_to)
        # create_shader_ui(material, nde, clear=True)
        tt_node.create_shader_ui(clear=True)

    # tt_node.active_texture = active_tt_texture
    tt_node.active_texture = texture_name
    tt_node.set_textures(folder_path, res)

    if tt_node.use_manual_wetmap:
        link_wetmap(tt_node, links)


def update_icon_from_tt_node(self: 'TT4_TextureNode', _context):
    if is_update_a_go():
        active_texture = self.active_subcategory.active_texture
        self.change_texture(
            active_texture.name,
            active_texture.active_viewport_quality_level[0],
            set_icon=False
        )

def update_icon_from_window_manager(self: bpy.types.WindowManager, context):
    if is_update_a_go():
        tt_node:'TT4_TextureNode' = context.object.terrain_settings.active_material.terrain_settings.active_tt_node
        active_texture = tt_node.active_subcategory.active_texture        
        tt_node.change_texture(
            active_texture.name,
            active_texture.active_viewport_quality_level[0],
            set_icon=False
        )



def create_dropdown_ui(dropdown_ui, input):
    ui_drop_bool = dropdown_ui.bool_list.add()
    ui_drop_bool.name = input.name
    ui_drop_bool.value = False
    return ui_drop_bool
def create_on_off_ui(on_off_ui, mat, node, input):
    ui_on_off = on_off_ui.bool_list.add()
    inp_name = input.name
    ui_on_off.name = inp_name
    ui_on_off.material = mat
    ui_on_off.node = node
    ui_on_off.input = input
    ui_on_off.value = True if input.default_value == 1 else False


def create_adv_ui(mat, node, input, current_section):
    ui_adv = current_section.adv_op_inputs.add()
    ui_adv.name = input.name
    ui_adv.section = current_section
def create_bool_list(mat, node, clear=False):
    if clear:
        mat.terrain_settings.ui_dropdowns.clear()
        tt_inp = mat.terrain_settings.ui_dropdowns.add()
        tt_inp.name = node.name
    else:
        if node.name in mat.terrain_settings.ui_dropdowns:
            tt_inp = mat.terrain_settings.ui_dropdowns[node.name]
        else:
            tt_inp = mat.terrain_settings.ui_dropdowns.add()
            tt_inp.name = node.name
    
    for input in node.inputs:
        if input.name.startswith("---"):
            ui_drop_bool = tt_inp.bool_list.add()
            # Input name foramting
            inp_name = input.name.replace("-","")
            if inp_name.startswith(" "):
                inp_name = inp_name[1:]
            if inp_name.endswith(" "):
                inp_name = inp_name[:len(inp_name)-1]

            ui_drop_bool.name = inp_name
            ui_drop_bool.value = False

def create_on_off_list(mat, node, clear=False):
    settings = mat.terrain_settings
    if clear:
        settings.ui_on_offs.clear()
        tt_inp = settings.ui_on_offs.add()
        tt_inp.name = node.name
    else:
        if node.name in settings.ui_on_offs:
            tt_inp = settings.ui_on_offs[node.name]
        else:
            tt_inp = settings.ui_on_offs.add()
            tt_inp.name = node.name
    for input in node.inputs:
        if "on/off" in input.name.lower():
            ui_on_off = tt_inp.bool_list.add()
            inp_name = input.name
            ui_on_off.name = inp_name
            ui_on_off.value = False



@persistent
def update_eevee_fix(value):
    for mat in bpy.data.materials:
        if mat.is_tt:
            if mat.terrain_settings.eevee_fix.input:
                mat.terrain_settings.eevee_fix.set_input_value(value)
                continue
            if eevee_fix_group := mat.node_tree.nodes.get("EEVEE_FIX_GROUP"):
                eevee_fix_group.inputs[0].default_value = value
                mat.terrain_settings.eevee_fix.set_input(
                    eevee_fix_group.inputs[0], mat)
@persistent
def eevee_fix_auto_update(sc,depsgraph):
    settings = sc.terrain_settings
    if settings.current_render_type != sc.render.engine:
        if sc.render.engine == "BLENDER_EEVEE":
            update_eevee_fix(1.0)
            settings.is_eevee = True
        else:
            update_eevee_fix(0.0)
            settings.is_eevee = False
        settings.current_render_type = sc.render.engine
    area = None
    if bpy.context.screen:
        area = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D']
    if area:
        area = area[0]
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        if space.shading.type != settings.current_preview_type:
            if space.shading.type == "MATERIAL":
                update_eevee_fix(1.0)
            elif settings.current_preview_type == "MATERIAL":
                update_eevee_fix(0.0)
            settings.current_preview_type = space.shading.type

def nde_prop(layout, inputs, input_name, expand=False, slider=False, text=None, icon="NONE", emboss=True, toggle=-1, icon_only=False, invert_checkbox=False, use_template=False):
    prop_text = text if text != None else input_name

    inp = inputs.get(input_name)
    if inp:
        if use_template:
            layout.template_node_view(
                inputs.id_data, inputs[0].node, inp)
        else:
            layout.prop(
                inp,
                "default_value",
                text=prop_text,
                icon=icon,
                expand=expand,
                slider=slider,
                toggle=toggle,
                icon_only=icon_only,
                emboss=emboss,
                invert_checkbox=invert_checkbox
            )


# Append
def appendObj(fpath, name, collectionParent) -> Object:
    use_link = bpy.context.scene.terrain_settings.asset_link_enum == "LINK"
    with bpy.data.libraries.load(fpath, link=use_link) as (data_from, data_to):
        for obj in data_from.objects:
            if obj == name:
                data_to.objects.append(obj)
    for obj in data_to.objects:
        collectionParent.objects.link(obj)
    # if not use_link:
    #     close_library(basename(fpath))
    return data_to.objects[0]
def appendCol(fpath:str, name:str, collectionParent:Collection) -> Collection:
    """Append a collection from the given filepath

    Parameters
    ----------
    fpath : str
        Filepath to a blend file from which to append a collection
    name : str
        Name of the collection to append
    collectionParent : Collection
        The collection to make the newly appended collection a child of

    Returns
    -------
    Collection
        The newly appended collection

    Raises
    ------
    ValueError
        Called if the collection wasn't found
    """
    use_link:bool = bpy.context.scene.terrain_settings.asset_link_enum == "LINK"
    with bpy.data.libraries.load(fpath, link=use_link) as (data_from, data_to):
        for col in data_from.collections:
            if col == name:
                data_to.collections.append(col)
    for col in data_to.collections:
        collectionParent.children.link(col)
    if not use_link:
        close_library(basename(fpath))
    if not data_to.collections:
        raise ValueError(
            f"Did not find a collection called '{name}' in {data_from.collections}  |  Blender file '{fpath}'")
    return data_to.collections[0]
def appendMaterial(fpath, name) -> Material:
    use_link = bpy.context.scene.terrain_settings.asset_link_enum == "LINK"
    with bpy.data.libraries.load(fpath, link=use_link) as (data_from, data_to):
        for mat in data_from.materials:
            if mat == name:
                data_to.materials.append(mat)
    # if not use_link:
    #     close_library(basename(fpath))
    return data_to.materials[0]

def append_assets(blendfile:str, asset_name:str, settings:'TerrainObjectSettings', make_single_user=False) -> bpy.types.Collection:
    col_name = f'{asset_name}_{settings.particleQualityLevel}'
    
    col = bpy.data.collections.get(col_name)
    if col:
        return col
    
    col = appendCol(blendfile, asset_name, bpy.context.collection)
    col.name = col_name
    return col

# Add Group Node
def addGroupNode(groupName: str, nodes: Nodes, make_single_user=False, geo=False, texture=False, procedural=False, water=False, link=True) -> Node:
    """Adds and then returns the desired group node"""
    # Make sure node group is in blend file
    ndegrp = tt.get_node_group(
        groupName, make_single_user=make_single_user, geo=geo, texture=texture, procedural=procedural, water=water, link=link)

    # Add, name, assign correct node group, and return
    group_type = "GeometryNodeGroup" if geo else "ShaderNodeGroup"
    nde = nodes.new(group_type)
    nde.name = groupName
    nde.node_tree = ndegrp
    return nde


def register_class(cls):
    try:
        bpy.utils.register_class(cls)
    except Exception as e:
        print(f" FAILED TO REGISTER {cls.__name__} ".center(100, "*"))  # Keep
        raise ValueError(e) from e
def unregister_class(cls):
    try:
        bpy.utils.unregister_class(cls)
    except Exception as e:
        print(f" FAILED TO UNREGISTER {cls.__name__} ".center(100, "*"))  # Keep
        raise ValueError(e) from e

def reg(classes):
    for cls in classes:
        register_class(cls)
def unreg(classes):
    for cls in reversed(classes):
        unregister_class(cls)

def setup_reg_funcs(classes):
    return reg(classes), unreg(classes)
