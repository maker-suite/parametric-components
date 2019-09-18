bl_info = {
    "name": "Parametric Components",
    "author": "Nesvarbu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Toolbox",
    "warning": "",
    "description": "",
    "wiki_url": "http://wiki.digidone3d.com/index.php/Main_Page",
    "category": "Object",
}

import bpy

from .props import *
from .operators import *
from .ui import *


parcomp_addon_keymaps = []


def register():
    bpy.utils.register_class(parcomp_ObjectProperty)
    bpy.utils.register_class(parcomp_Parameter)
    bpy.utils.register_class(parcomp_ComponentType)
    bpy.utils.register_class(parcomp_ComponentObject)
    bpy.utils.register_class(parcomp_Component)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_create)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_add)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_save)
    bpy.utils.register_class(OBJECT_OT_parcomp_comptype_save)
    bpy.utils.register_class(OBJECT_OT_parcomp_duplicate_component)
    bpy.utils.register_class(OBJECT_OT_parcomp_duplicate_comptype)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_addparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_delparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_editparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_assignparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_unassignparam)
    bpy.utils.register_class(VIEW3D_PT_parcomp_components)
    bpy.utils.register_class(VIEW3D_OT_parcomp_component_select)
    parcomp_props_register()
    kc = bpy.context.window_manager.keyconfigs
    if kc:
        #km = kc.addon.keymaps.new(name='Component Select', space_type='VIEW_3D')
        km = kc.default.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(VIEW3D_OT_parcomp_component_select.bl_idname, 'LEFTMOUSE', 'PRESS', head=True)
        parcomp_addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in parcomp_addon_keymaps:
        km.keymap_items.remove(kmi)
    parcomp_addon_keymaps.clear()
    bpy.utils.unregister_class(parcomp_ObjectProperty)
    bpy.utils.unregister_class(parcomp_Parameter)
    bpy.utils.unregister_class(parcomp_ComponentType)
    bpy.utils.unregister_class(parcomp_ComponentObject)
    bpy.utils.unregister_class(parcomp_Component)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_create)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_add)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_save)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_comptype_save)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_duplicate_component)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_duplicate_comptype)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_addparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_delparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_editparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_assignparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_unassignparam)
    bpy.utils.unregister_class(VIEW3D_PT_parcomp_components)
    bpy.utils.unregister_class(VIEW3D_OT_parcomp_component_select)


if __name__ == "__main__":
    register()
