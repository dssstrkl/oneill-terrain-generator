 float, float]): The color to be used in the layer.

        Returns:
            PropertyGroup: The newly created solid color layer.
        """
        # mat = self.get_active_material()
        active_group = self.get_active_group()
        # # Get insertion position
        # parent_id, insert_order = active_group.get_insertion_data()
        # # Adjust existing items' order
        # active_group.adjust_sibling_orders(parent_id, insert_order)

        # solid_color_template = get_nodetree_from_library(
        #     '_PS_Solid_Color_Template', False)
        # solid_color_nt = solid_color_template.copy()
        # solid_color_nt.name = f"PS_IMG {name} (MAT: {mat.name})"
        new_layer = self._add_layer(
            name, f'_PS_Solid_Color_Template', 'SOLID_COLOR', make_copy=True)
        solid_color_nt = new_layer.node_tree
        solid_color_nt.nodes['RGB'].outputs[0].default_value = color

        # Create the new item
        # new_id = active_group.add_item(
        #     name=name,
        #     item_type='SOLID_COLOR',
        #     parent_id=parent_id,
        #     order=insert_order,
        #     node_tree=solid_color_nt,
        # )

        # Update active index
        # if new_id != -1:
        #     flattened = active_group.flatten_hierarchy()
        #     for i, (item, _) in enumerate(flattened):
        #         if item.id == new_id:
        #             active_group.active_index = i
        #             break

        active_group.update_node_tree()

        return new_layer

    def create_folder(self, name: str) -> PropertyGroup:
        """Creates a new folder in the active group.

        Args:
            name (str): The name of the new folder.

        Returns:
            PropertyGroup: The newly created folder.
        """
        # mat = self.get_active_material()
        active_group = self.get_active_group()
        # # Get insertion position
        # parent_id, insert_order = active_group.get_insertion_data()

        # # Adjust existing items' order
        # active_group.adjust_sibling_orders(parent_id, insert_order)

        # folder_template = get_nodetree_from_library(
        #     '_PS_Folder_Template', False)
        # folder_nt = folder_template.copy()
        # folder_nt.name = f"PS_FLD {name} (MAT: {mat.name})"

        new_layer = self._add_layer(
            name, f'_PS_Folder_Template', 'FOLDER', make_copy=True)

        # Create the new item
        # new_id = active_group.add_item(
        #     name=name,
        #     item_type='FOLDER',
        #     parent_id=parent_id,
        #     order=insert_order,
        #     node_tree=folder_nt
        # )

        # Update active index
        # if new_id != -1:
        #     flattened = active_group.flatten_hierarchy()
        #     for i, (item, _) in enumerate(flattened):
        #         if item.id == new_id:
        #             active_group.active_index = i
        #             break

        active_group.update_node_tree()

        return new_layer

    def create_adjustment_layer(self, name: str, adjustment_type: str) -> PropertyGroup:
        """Creates a new adjustment layer in the active group.

        Args:
            name (str): The name of the new adjustment layer.
            adjustment_type (str): The type of adjustment to be applied.

        Returns:
            PropertyGroup: The newly created adjustment layer.
        """
        mat = self.get_active_material()
        active_group = self.get_active_group()
        # # Get insertion position
        # parent_id, insert_order = active_group.get_insertion_data()

        # # Adjust existing items' order
        # active_group.adjust_sibling_orders(parent_id, insert_order)

        # adjustment_template = get_nodetree_from_library(
        #     f'_PS_Adjustment_Template', False)
        # adjustment_nt: NodeTree = adjustment_template.copy()
        # adjustment_nt.name = f"PS_ADJ {name} (MAT: {mat.name})"
        new_layer = self._add_layer(
            name, f'_PS_Adjustment_Template', 'ADJUSTMENT', make_copy=True)
        adjustment_nt = new_layer.node_tree
        nodes = adjustment_nt.nodes
        links = adjustment_nt.links
        # Find Vector Math node
        group_input_node = None
        for node in nodes:
            if node.type == 'GROUP_INPUT':
                group_input_node = node
                break

        # Find Mix node
        mix_node = None
        for node in nodes:
            if node.type == 'MIX' and node.data_type == 'RGBA':
                mix_node = node
                break

        adjustment_node = nodes.new(adjustment_type)
        adjustment_node.label = 'Adjustment'
        adjustment_node.location = mix_node.location + Vector([0, -200])

        # Checks if the adjustment node has a factor input
        if 'Fac' in adjustment_node.inputs:
            # Create a value node
            value_node = nodes.new('ShaderNodeValue')
            value_node.label = 'Factor'
            value_node.outputs[0].default_value = 1.0
            value_node.location = adjustment_node.location + Vector([-200, 0])
            links.new(value_node.outputs['Value'],
                      adjustment_node.inputs['Fac'])

        links.new(adjustment_node.inputs['Color'],
                  group_input_node.outputs['Color'])
        links.new(mix_node.inputs['B'], adjustment_node.outputs['Color'])

        # Create the new item
        # new_id = active_group.add_item(
        #     name=name,
        #     item_type='ADJUSTMENT',
        #     parent_id=parent_id,
        #     order=insert_order,
        #     node_tree=adjustment_nt
        # )

        # Update active index
        # if new_id != -1:
        #     flattened = active_group.flatten_hierarchy()
        #     for i, (item, _) in enumerate(flattened):
        #         if item.id == new_id:
        #             active_group.active_index = i
        #             break

        active_group.update_node_tree()

        return new_layer
    
    def create_gradient_layer(self, name: str, gradient_type: str) -> PropertyGroup:
        """Creates a new gradient layer in the active group.

        Args:
            name (str): The name of the new gradient layer.

        Returns:
            PropertyGroup: The newly created gradient layer.
        """
        obj = self.active_object
        active_group = self.get_active_group()
        view_layer = bpy.context.view_layer
        gradient_type = gradient_type.title()
        
        with bpy.context.temp_override():
            if "Paint System Collection" not in view_layer.layer_collection.collection.children:
                collection = bpy.data.collections.new("Paint System Collection")
                view_layer.layer_collection.collection.children.link(collection)
            else:
                collection = view_layer.layer_collection.collection.children["Paint System Collection"]

            new_layer = self._add_layer(
                name, f'_PS_{gradient_type}_Gradient_Template', 'GRADIENT', make_copy=True)
            empty_object = bpy.data.objects.new(f"{active_group.name} {name}", None)
            collection.objects.link(empty_object)
        empty_object.location = obj.location
        if gradient_type == 'Linear':
            empty_object.empty_display_type = 'SINGLE_ARROW'
        elif gradient_type == 'Radial':
            empty_object.empty_display_type = 'SPHERE'
        empty_object.show_in_front = True
        empty_object.parent = obj
        new_layer.node_tree.nodes["Texture Coordinate"].object = empty_object
        # gradient_nt.nodes['Gradient'].label = name

        # Create the new item
        # new_id = active_group.add_item(
        #     name=name,
        #     item_type='GRADIENT',
        #     parent_id=parent_id,
        #     order=insert_order,
        #     node_tree=gradient_nt
        # )

        # Update active index
        # if new_id != -1:
        #     flattened = active_group.flatten_hierarchy()
        #     for i, (item, _) in enumerate(flattened):
        #         if item.id == new_id:
        #             active_group.active_index = i
        #             break

        active_group.update_node_tree()

        return new_layer

    def create_shader_layer(self, name: str, shader_type: str) -> PropertyGroup:
        active_group = self.get_active_group()
        new_layer = self._add_layer(
            name, shader_type, 'SHADER', sub_type=shader_type, make_copy=True)
        active_group.update_node_tree()
        return new_layer
    
    def create_node_group_layer(self, name: str, node_tree_name: str) -> PropertyGroup:
        active_group = self.get_active_group()
        new_layer = self._add_layer(
            name, node_tree_name, 'NODE_GROUP')
        active_group.update_node_tree()
        return new_layer

    def get_active_material(self) -> Optional[Material]:
        if not self.active_object or self.active_object.type != 'MESH':
            return None

        return self.active_object.active_material

    def get_material_settings(self):
        mat = self.get_active_material()
        if not mat or not hasattr(mat, "paint_system"):
            return None
        return mat.paint_system

    def get_groups(self) -> Optional[PropertyGroup]:
        paint_system = self.get_material_settings()
        if not paint_system:
            return None
        return paint_system.groups

    def get_active_group(self) -> Optional[PropertyGroup]:
        paint_system = self.get_material_settings()
        if not paint_system or len(paint_system.groups) == 0:
            return None
        active_group_idx = int(paint_system.active_group)
        if active_group_idx >= len(paint_system.groups):
            return None  # handle cases where active index is invalid
        return paint_system.groups[active_group_idx]

    def get_active_layer(self) -> Optional[PropertyGroup]:
        active_group = self.get_active_group()
        if not active_group or len(active_group.items) == 0 or active_group.active_index >= len(active_group.items):
            return None

        return active_group.items[active_group.active_index]

    def get_layer_node_tree(self) -> Optional[NodeTree]:
        active_layer = self.get_active_layer()
        if not active_layer:
            return None
        return active_layer.node_tree

    def get_active_layer_node_group(self) -> Optional[Node]:
        active_group = self.get_active_group()
        layer_node_tree = self.get_active_layer().node_tree
        if not layer_node_tree:
            return None
        node_details = {'type': 'GROUP', 'node_tree': layer_node_tree}
        node = self.find_node(active_group.node_tree, node_details)
        return node

    def find_color_mix_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'MIX', 'data_type': 'RGBA'}
        return self.find_node(layer_node_tree, node_details)

    def find_uv_map_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'UVMAP'}
        return self.find_node(layer_node_tree, node_details)

    def find_opacity_mix_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'MIX', 'name': 'Opacity'}
        return self.find_node(layer_node_tree, node_details) or self.find_color_mix_node()

    def find_clip_mix_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'MIX', 'name': 'Clip'}
        return self.find_node(layer_node_tree, node_details)

    def find_image_texture_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'TEX_IMAGE'}
        return self.find_node(layer_node_tree, node_details)

    def find_rgb_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'name': 'RGB'}
        return self.find_node(layer_node_tree, node_details)

    def find_adjustment_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'label': 'Adjustment'}
        return self.find_node(layer_node_tree, node_details)

    def find_node_group(self, node_tree: NodeTree) -> Optional[Node]:
        node_tree = self.get_active_group().node_tree
        for node in node_tree.nodes:
            if hasattr(node, 'node_tree') and node.node_tree and node.node_tree.name == node_tree.name:
                return node
        return None
    
    def find_attribute_node(self) -> Optional[Node]:
        layer_node_tree = self.get_active_layer().node_tree
        node_details = {'type': 'ATTRIBUTE'}
        return self.find_node(layer_node_tree, node_details)
    
    def is_valid_ps_nodetree(self, node_tree: NodeTree):
        # check if the node tree has both Color and Alpha inputs and outputs
        has_color_input = False
        has_alpha_input = False
        has_color_output = False
        has_alpha_output = False
        for interface_item in node_tree.interface.items_tree:
            if interface_item.item_type == "SOCKET":
                # print(interface_item.name, interface_item.socket_type, interface_item.in_out)
                if interface_item.name == "Color" and interface_item.socket_type == "NodeSocketColor":
                    if interface_item.in_out == "INPUT":
                        has_color_input = True
                    else:
                        has_color_output = True
                elif interface_item.name == "Alpha" and interface_item.socket_type == "NodeSocketFloat":
                    if interface_item.in_out == "INPUT":
                        has_alpha_input = True
                    else:
                        has_alpha_output = True
        return has_color_input and has_alpha_input and has_color_output and has_alpha_output
            

    def _update_paintsystem_data(self):
        active_group = self.get_active_group()
        mat = self.get_active_material()
        # active_group.update_node_tree()
        if active_group.node_tree:
            active_group.node_tree.name = f"PS_GROUP {active_group.name} (MAT: {mat.name})"
        for layer in active_group.items:
            if not layer.type == 'NODE_GROUP':
                if layer.node_tree:
                    layer.node_tree.name = f"PS_{layer.type} {active_group.name} {layer.name} (MAT: {mat.name})"
                if layer.image:
                    layer.image.name = f"PS {active_group.name} {layer.name} (MAT: {mat.name})"

    def _add_layer(self, layer_name, tree_name: str, item_type: str, sub_type="", image=None, force_reload=False, make_copy=False) -> NodeTree:
        active_group = self.get_active_group()
        # Get insertion position
        parent_id, insert_order = active_group.get_insertion_data()
        # Adjust existing items' order
        active_group.adjust_sibling_orders(parent_id, insert_order)
        nt = get_nodetree_from_library(
            tree_name, force_reload)
        if make_copy:
            nt = nt.copy()
        # Create the new item
        new_id = active_group.add_item(
            name=layer_name,
            item_type=item_type,
            sub_type=sub_type,
            parent_id=parent_id,
            order=insert_order,
            node_tree=nt,
            image=image,
        )

        # Update active index
        if new_id != -1:
            flattened = active_group.flatten_hierarchy()
            for i, item in enumerate(active_group.items):
                if item.id == new_id:
                    active_group.active_index = i
                    break
        self._update_paintsystem_data()
        return active_group.get_item_by_id(new_id)

    def _value_set(self, obj, path, value):
        if '.' in path:
            path_prop, path_attr = path.rsplit('.', 1)
            prop = obj.path_resolve(path_prop)
        else:
            prop = obj
            path_attr = path
        setattr(prop, path_attr, value)

    def find_node(self, node_tree, node_details):
        if not node_tree:
            return None
        for node in node_tree.nodes:
            match = True
            for key, value in node_details.items():
                if getattr(node, key) != value:
                    match = False
                    break
            if match:
                return node
        return None

    def _create_folder_node_tree(self, folder_name: str, force_reload=False) -> NodeTree:
        mat = self.get_active_material()
        folder_template = get_nodetree_from_library(
            '_PS_Folder_Template', force_reload)
        folder_nt = folder_template.copy()
        folder_nt.name = f"PS {folder_name} (MAT: {mat.name})"
        return folder_nt

    def _create_layer_node_tree(self, layer_name: str, image: Image, uv_map_name: str = None, force_reload=True) -> NodeTree:
        mat = self.get_active_material()
        layer_template = get_nodetree_from_library(
            '_PS_Layer_Template', force_reload)
        layer_nt = layer_template.copy()
        layer_nt.name = f"PS {layer_name} (MAT: {mat.name})"
        # Find the image texture node
        image_texture_node = None
        for node in layer_nt.nodes:
            if node.type == 'TEX_IMAGE':
                image_texture_node = node
                break
        uv_map_node = None
        # Find UV Map node
        for node in layer_nt.nodes:
            if node.type == 'UVMAP':
                uv_map_node = node
                break
        # use uv_map_name or default to first uv map
        if uv_map_name:
            uv_map_node.uv_map = uv_map_name
        else:
            uv_map_node.uv_map = bpy.context.object.data.uv_layers[0].name
        image_texture_node.image = image
        return layer_nt

    def _on_item_delete(self, item):
        if item.node_tree:
            # 2 users: 1 for the node tree, 1 for the datablock
            if item.node_tree.users <= 2:
                # print("Removing node tree")
                bpy.data.node_groups.remove(item.node_tree)

        if item.image:
            # 2 users: 1 for the image datablock, 1 for the panel
            if item.image and item.image.users <= 2:
                # print("Removing image")
                bpy.data.images.remove(item.image)
