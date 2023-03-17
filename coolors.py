bl_info = {
    "name": "Coolors to Color Ramp",
    "description": "Generate a color ramp from a Coolors URL",
    "author": "Kalmarv",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Shader Node Editor > Sidebar",
    "wiki_url": "https://github.com/Kalmarv/blender-coolors-addon",
    "category": "Material",
}

import bpy


# thank you https://blender.stackexchange.com/a/158902
def create_cols(_url):
    def srgb_to_linearrgb(c):
        if c < 0:
            return 0
        elif c < 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    def hex_to_rgb(h, alpha=1):
        r = (h & 0xFF0000) >> 16
        g = (h & 0x00FF00) >> 8
        b = h & 0x0000FF
        return tuple([srgb_to_linearrgb(c / 0xFF) for c in (r, g, b)] + [alpha])

    slash_index = _url.rfind("/")
    pallate_str = _url[slash_index + 1 :]
    arr = pallate_str.split("-")
    rgba_arr = [hex_to_rgb(int(c, 16)) for c in arr]
    return rgba_arr


class CoolorsPanel(bpy.types.Panel):
    bl_label = "Coolors Panel"
    bl_idname = "OBJECT_PT_coolors_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Coolors"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "coolors_url")
        row = layout.row()
        row.operator("my_addon.print_text")


class GetCoolorsOperator(bpy.types.Operator):
    bl_idname = "my_addon.print_text"
    bl_label = "Create Node"

    def execute(self, context):
        active_material = bpy.context.object.active_material

        if active_material is not None:
            # Color data
            cols_arr = create_cols(context.scene.coolors_url)
            cols_len = len(cols_arr)

            # Selecting node if it already exists, otherwise create a new one
            if active_material.node_tree.nodes.get("generated_coolors") is not None:
                color_ramp_node = active_material.node_tree.nodes.get(
                    "generated_coolors"
                )
            else:
                color_ramp_node = active_material.node_tree.nodes.new(
                    type="ShaderNodeValToRGB"
                )
                # Color Ramp properties
                color_ramp_node.name = "generated_coolors"
                color_ramp_node.label = "Coolors Palette"

            # Remove all colors but one, Blender will not allow you to delete them all
            for i in range(len(color_ramp_node.color_ramp.elements) - 1):
                element = color_ramp_node.color_ramp.elements[0]
                color_ramp_node.color_ramp.elements.remove(element)

            # Set colors, for the last one, instead of creating a new one, use the one
            # we left over in the previous step
            for i in range(cols_len):
                if i != cols_len - 1:
                    element = color_ramp_node.color_ramp.elements.new(
                        (i / (cols_len - 1))
                    )
                    element.color = cols_arr[i]
                else:
                    element = color_ramp_node.color_ramp.elements[
                        len(color_ramp_node.color_ramp.elements) - 1
                    ]
                    element.color = cols_arr[i]
                    # In case the elments were moved
                    element.position = 1.0

            # Create and select node
            active_material.node_tree.nodes.active = color_ramp_node
            color_ramp_node.select = True

            return {"FINISHED"}

        else:
            self.report({"ERROR"}, "No active material")
            return {"FINISHED"}


def register():
    bpy.types.Scene.coolors_url = bpy.props.StringProperty(
        name="URL", description="Enter Coolors palette url"
    )
    bpy.utils.register_class(CoolorsPanel)
    bpy.utils.register_class(GetCoolorsOperator)


def unregister():
    del bpy.types.Scene.coolors_url
    bpy.utils.unregister_class(CoolorsPanel)
    bpy.utils.unregister_class(GetCoolorsOperator)


if __name__ == "__main__":
    register()
