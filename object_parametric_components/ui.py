import bpy
from .props import *


class VIEW3D_PT_parcomp_components(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_parcomp_components"
    bl_label = "Components"
    bl_category = "Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    #@classmethod
    #def poll(cls, context):
    #    return True

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        actobj = context.active_object
        layout.prop(world, 'parcomp_mode', expand=True)
        editmode = (parcomp_modes[world.get('parcomp_mode') or 0][0] == 'EDIT')
        if editmode:
            layout.operator('object.parcomp_component_create')
            if (actobj is None) or (not actobj.get('parcomp_is_parametric')):
                return
            layout.operator('object.parcomp_duplicate_component')
            layout.operator('object.parcomp_duplicate_comptype')
            row = layout.row(align=True)
            row.prop(actobj, 'parcomp_component_name_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'parcomp_component_name', text='')
            row = layout.row(align=True)
            row.prop(actobj, 'parcomp_component_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'parcomp_component_type', text='')
            row = layout.row(align=True)
            row.operator('object.parcomp_component_addparam')
            row.operator('object.parcomp_component_addparam', text='', icon='PLUS')
            comp = world.parcomp_components[actobj.parcomp_component_name]
            for i, param in enumerate(comp.params):
                row = layout.row()
                row.column().prop(param, 'name', text='')
                row = row.column().row(align=True)
                op = row.operator('object.parcomp_component_editparam', text='Edit')
                op.index = i
                op = row.operator('object.parcomp_component_delparam', text='', icon='CANCEL')
                op.index = i
                row = layout.row(align=True)
                op = row.operator('object.parcomp_component_assignparam', text='', icon='PLUS')
                op.index = i
                for j, prop in enumerate(param.assigned_props):
                    row = layout.row(align=True)
                    row.prop(prop, 'obj', text='')
                    row.prop(prop, 'prop', text='')
                    op = row.operator('object.parcomp_component_unassignparam', text='', icon='CANCEL')
                    op.index = i
                    op.propindex = j
        else:
            row = layout.row(align=True)
            row.operator('object.parcomp_component_add')
            row.operator('object.parcomp_component_add', text='', icon='PLUS')
            if (actobj is None) or (not actobj.get('parcomp_is_parametric')):
                return
            layout.prop(actobj, 'parcomp_component_name_sel', text='')
            layout.prop(actobj, 'parcomp_component_type_sel', text='')
            #layout.template_ID(context.scene.objects, 'parcomp_test') # TODO
            comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
            for param in comp.params:
                pname = param.get('name')
                if not pname:
                    continue
                layout.prop(param, 'value_%s' % (param.ptype,), text=pname)


class VIEW3D_OT_parcomp_component_select(bpy.types.Operator):
    bl_idname = 'view3d.parcomp_component_select'
    bl_label = 'Select Component'

    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()

    def execute(self, context):
        bpy.ops.view3d.select(location=(self.x, self.y))
        if not context.active_object:
            return {'FINISHED'}
        if context.mode != 'OBJECT':
            return {'FINISHED'}
        editmode = (parcomp_modes[bpy.context.scene.world.get('parcomp_mode') or 0][0] == 'EDIT')
        if editmode:
            return {'FINISHED'}
        bpy.ops.object.select_hierarchy()
        bpy.ops.object.select_more()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.x = event.mouse_region_x
        self.y = event.mouse_region_y
        return self.execute(context)
