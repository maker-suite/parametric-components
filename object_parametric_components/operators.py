import bpy
from .props import *


class OBJECT_OT_parcomp_component_create(bpy.types.Operator):
    bl_idname = "object.parcomp_component_create"
    bl_label = "Create Component"

    def execute(self, context):
        selobjs = list(context.selected_objects)
        actobj = context.active_object
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            location=tuple(actobj.location),
            rotation=(0, 0, 0),
        )
        actobj = context.active_object
        actobj['parcomp_is_parametric'] = True
        for obj in selobjs:
            obj.select_set(True)
        actobj.select_set(False)
        actobj.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT')
        world = context.scene.world
        comp = world.parcomp_components.add()
        comp.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        world.parcomp_nextcompnum += 1
        actobj.name = comp.name
        actobj['parcomp_component_name_skip'] = True
        actobj.parcomp_component_name = comp.name
        actobj.parcomp_component_name_sel = comp.name
        comptype = comp.types.add()
        comptype.name = 'Type.0'
        comp.nexttypenum = 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        for obj in actobj.children:
            obj.use_fake_user = True
            compobj = comp.objs.add()
            compobj.objtype = obj.type
            if compobj.objtype == 'MESH':
                compobj.objdata = obj.data.name
            compobj.location_x = obj.location.x
            compobj.location_y = obj.location.y
            compobj.location_z = obj.location.z
            compobj.rotation_x = obj.rotation_euler.x
            compobj.rotation_y = obj.rotation_euler.y
            compobj.rotation_z = obj.rotation_euler.z
            compobj.dimension_x = obj.dimensions.x
            compobj.dimension_y = obj.dimensions.y
            compobj.dimension_z = obj.dimensions.z
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_add(bpy.types.Operator):
    bl_idname = "object.parcomp_component_add"
    bl_label = "Add Component"

    comp: bpy.props.EnumProperty(name='Component', items=parcomp_comp_name_items)
    comptype: bpy.props.EnumProperty(name='Type', items=parcomp_comp_type_items)

    def execute(self, context):
        if not self.comp:
            return {'CANCELLED'}
        comp = context.scene.world.parcomp_components[self.comp]
        comptype = comp.types[self.comptype]
        coll = bpy.data.collections[comptype.collname]
        obj = coll.objects[0]
        obj.select_set(True)
        bpy.ops.object.select_more()
        obj.select_set(True)
        bpy.ops.object.duplicate_move_linked()
        obj = context.active_object
        obj.location = context.scene.cursor.location
        coll.objects.link(obj)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_save(bpy.types.Operator):
    bl_idname = "object.parcomp_component_save"
    bl_label = "Save As New Component"

    name: bpy.props.StringProperty(name='Component Name')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        world = context.scene.world
        comp = world.parcomp_components[actobj.parcomp_component_name]
        newcomp = world.parcomp_components.add()
        newcomp.name = self.name
        params = comp.get('params')
        if params:
            newcomp['params'] = params.copy()
        objs = comp.get('objs')
        if objs:
            newcomp['objs'] = objs.copy()
        world.parcomp_nextcompnum += 1
        comptype = comp.types[actobj.parcomp_component_type]
        bpy.data.collections[comptype.collname].objects.unlink(actobj)
        actobj.name = newcomp.name
        actobj['parcomp_component_name_skip'] = True
        actobj.parcomp_component_name = newcomp.name
        actobj.parcomp_component_name_sel = newcomp.name
        comptype = newcomp.types.add()
        comptype.name = 'Type.0'
        newcomp.nexttypenum = 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        self.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_comptype_save(bpy.types.Operator):
    bl_idname = "object.parcomp_comptype_save"
    bl_label = "Save As New Type"

    name: bpy.props.StringProperty(name='Component Type')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
        comptype = comp.types[actobj.parcomp_component_type]
        bpy.data.collections[comptype.collname].objects.unlink(actobj)
        comptype = comp.types.add()
        comptype.name = self.name
        comp.nexttypenum += 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        comp = context.scene.world.parcomp_components[context.active_object.parcomp_component_name]
        self.name = 'Type.%d' % (comp.nexttypenum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_duplicate_component(bpy.types.Operator):
    bl_idname = "object.parcomp_duplicate_component"
    bl_label = "Duplicate Component"

    name: bpy.props.StringProperty(name='Component Name')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        obj = context.active_object
        bpy.ops.object.parcomp_component_add(comp=obj.parcomp_component_name, comptype=obj.parcomp_component_type)
        bpy.ops.object.parcomp_component_save(name=self.name)
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        self.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_duplicate_comptype(bpy.types.Operator):
    bl_idname = "object.parcomp_duplicate_comptype"
    bl_label = "Duplicate Type"

    name: bpy.props.StringProperty(name='Component Type')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        obj = context.active_object
        bpy.ops.object.parcomp_component_add(comp=obj.parcomp_component_name, comptype=obj.parcomp_component_type)
        bpy.ops.object.parcomp_comptype_save(name=self.name)
        return {'FINISHED'}

    def invoke(self, context, event):
        comp = context.scene.world.parcomp_components[context.active_object.parcomp_component_name]
        self.name = 'Type.%d' % (comp.nexttypenum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_addparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params.add()
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_delparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_delparam"
    bl_label = "Remove Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        comp.params.remove(idx)
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_editparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_editparam"
    bl_label = "Edit Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    name: bpy.props.StringProperty(name='Parameter Name')
    ptype:  bpy.props.EnumProperty(name='Parameter Type', items=parcomp_param_type_items)
    group: bpy.props.StringProperty(name='Parameter Group')

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.name = self.name
        param.ptype = self.ptype
        param.group = self.group
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        idx = self.index
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        self.name = param.name
        self.ptype = param.ptype
        self.group = param.group
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_assignparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_assignparam"
    bl_label = "Assign Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.assigned_props.add()
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_unassignparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_unassignparam"
    bl_label = "Remove Parameter Assignment"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    propindex: bpy.props.IntProperty(name='Property Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        pidx = self.propindex
        if (idx < 0) or (pidx < 0):
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.assigned_props.remove(pidx)
        return {'FINISHED'}
