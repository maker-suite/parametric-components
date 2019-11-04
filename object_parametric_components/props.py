import bpy


parcomp_modes = [
    ('OBJECT', 'Object', '', 0),
    ('EDIT'  , 'Edit'  , '', 1),
]


def parcomp_objprop_obj_items(self, context):
    actobj = context.active_object
    return [(obj.name, obj.name, '', i) for i, obj in enumerate(actobj.children)]


parcomp_objprop_prop_items = [
    ('location.x'      , 'Location X' , '', 0),
    ('location.y'      , 'Location Y' , '', 1),
    ('location.z'      , 'Location Z' , '', 2),
    ('rotation_euler.x', 'Rotation X' , '', 3),
    ('rotation_euler.y', 'Rotation Y' , '', 4),
    ('rotation_euler.z', 'Rotation Z' , '', 5),
    ('dimensions.x'    , 'Dimension X', '', 6),
    ('dimensions.y'    , 'Dimension Y', '', 7),
    ('dimensions.z'    , 'Dimension Z', '', 8),
]


parcomp_param_type_items = [
    ('FLOAT'  , 'Float'  , '', 0),
    ('INTEGER', 'Integer', '', 1),
    ('BOOLEAN', 'Boolean', '', 2),
    ('STRING' , 'String' , '', 3),
]


def parcomp_param_value_update(self, context):
    actobj = context.active_object
    comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
    comptype = comp.types[actobj.parcomp_component_type]
    for compobj in bpy.data.collections[comptype.collname].objects:
        objitems = compobj.children
        for a in self.assigned_props:
            iobj = a.get('obj', 0)
            iprop = a.get('prop', 0)
            obj = objitems[iobj]
            (prop, axis) = parcomp_objprop_prop_items[iprop][0].split('.')
            attr = getattr(obj, prop)
            setattr(attr, axis, self['value_FLOAT'])


class parcomp_ObjectProperty(bpy.types.PropertyGroup):
    obj: bpy.props.EnumProperty(name='Object', items=parcomp_objprop_obj_items)
    prop: bpy.props.EnumProperty(name='Property', items=parcomp_objprop_prop_items)


class parcomp_Parameter(bpy.types.PropertyGroup):
    ptype:  bpy.props.EnumProperty(name='Parameter Type', items=parcomp_param_type_items)
    name: bpy.props.StringProperty(name='Parameter Name')
    group: bpy.props.StringProperty(name='Parameter Group')
    value_FLOAT: bpy.props.FloatProperty(name='Parameter Value', update=parcomp_param_value_update)
    value_INTEGER: bpy.props.IntProperty(name='Parameter Value')
    value_BOOLEAN: bpy.props.BoolProperty(name='Parameter Value')
    value_STRING: bpy.props.StringProperty(name='Parameter Value')
    assigned_props: bpy.props.CollectionProperty(type=parcomp_ObjectProperty)


class parcomp_ComponentType(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Component Type')
    collname: bpy.props.StringProperty(name='Collection Name')


class parcomp_ComponentObject(bpy.types.PropertyGroup):
    objtype: bpy.props.StringProperty(name='Object Type')
    objdata: bpy.props.StringProperty(name='Object Data')
    location_x: bpy.props.FloatProperty(name='Location X')
    location_y: bpy.props.FloatProperty(name='Location Y')
    location_z: bpy.props.FloatProperty(name='Location Z')
    rotation_x: bpy.props.FloatProperty(name='Rotation X')
    rotation_y: bpy.props.FloatProperty(name='Rotation Y')
    rotation_z: bpy.props.FloatProperty(name='Rotation Z')
    dimension_x: bpy.props.FloatProperty(name='Dimension X')
    dimension_y: bpy.props.FloatProperty(name='Dimension Y')
    dimension_z: bpy.props.FloatProperty(name='Dimension Z')


class parcomp_Component(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Component Name')
    params: bpy.props.CollectionProperty(type=parcomp_Parameter)
    types: bpy.props.CollectionProperty(type=parcomp_ComponentType)
    nexttypenum: bpy.props.IntProperty(name='Next Type Number')
    objs: bpy.props.CollectionProperty(type=parcomp_ComponentObject)


def parcomp_comp_name_items(self, context):
    return [(comp.name, comp.name, '', i) for i, comp in enumerate(context.scene.world.parcomp_components)]


def parcomp_comp_type_items(self, context):
    actobj = context.active_object
    comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
    return [(comptype.name, comptype.name, '', i) for i, comptype in enumerate(comp.types)]


def parcomp_comp_name_select(self, context):
    obj = context.active_object
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    if obj.parcomp_component_name == compname:
        return
    bpy.ops.object.select_more()
    obj.select_set(True)
    loc = tuple(obj.location)
    rot = tuple(obj.rotation_euler)
    bpy.ops.object.delete() # use_global=False/True
    children = []
    comp = context.scene.world.parcomp_components[compname]
    for compobj in comp.objs:
        bpy.ops.object.add(
            type=compobj.objtype,
            location=(compobj.location_x, compobj.location_y, compobj.location_z),
            rotation=(compobj.rotation_x, compobj.rotation_y, compobj.rotation_z),
        )
        obj = context.active_object
        obj.dimensions = (compobj.dimension_x, compobj.dimension_y, compobj.dimension_z)
        if obj.type == 'MESH':
            obj.data = bpy.data.meshes[compobj.objdata]
        children.append(obj)
    bpy.ops.object.empty_add(
        type='PLAIN_AXES',
        align='WORLD',
        location=tuple(children[-1].location),
        rotation=(0, 0, 0),
        #layers=current_layers,
    )
    actobj = context.active_object
    actobj['parcomp_is_parametric'] = True
    for obj in children:
        obj.select_set(True)
    actobj.select_set(False)
    actobj.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT')
    actobj.location = loc
    actobj.rotation_euler = rot
    actobj['parcomp_component_name_skip'] = True
    actobj.parcomp_component_name = compname
    actobj.parcomp_component_name_sel = compname
    comptype = comp.types[0]
    actobj['parcomp_component_type_skip'] = True
    actobj.parcomp_component_type = comptype.name
    actobj.parcomp_component_type_sel = comptype.name
    bpy.data.collections[comptype.collname].objects.link(actobj)


def parcomp_comp_name_update(self, context):
    obj = context.active_object
    if obj['parcomp_component_name_skip']:
        obj['parcomp_component_name_skip'] = False
        return
    scene = context.scene
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    scene.world.parcomp_components[compname].name = obj.parcomp_component_name
    obj.name = obj.parcomp_component_name


def parcomp_comp_type_select(self, context):
    obj = context.active_object
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    comptype = parcomp_comp_type_items(self, context)[obj['parcomp_component_type_sel']][1]
    if obj.parcomp_component_type == comptype:
        return
    bpy.ops.object.select_more()
    obj.select_set(True)
    loc = tuple(obj.location)
    bpy.ops.object.delete() # use_global=False/True
    comp = context.scene.world.parcomp_components[compname]
    obj = bpy.data.collections[comp.types[comptype].collname].objects[0]
    obj.select_set(True)
    bpy.ops.object.select_more()
    obj.select_set(True)
    bpy.ops.object.duplicate_move_linked()
    obj = context.active_object
    obj.location = loc


def parcomp_comp_type_update(self, context):
    obj = context.active_object
    if obj['parcomp_component_type_skip']:
        obj['parcomp_component_type_skip'] = False
        return
    scene = context.scene
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    comptype = parcomp_comp_type_items(self, context)[obj['parcomp_component_type_sel']][1]
    scene.world.parcomp_components[compname].types[comptype].name = obj.parcomp_component_type


def parcomp_props_register():
    bpy.types.World.parcomp_components = bpy.props.CollectionProperty(type=parcomp_Component)
    bpy.types.World.parcomp_nextcompnum = bpy.props.IntProperty(name='Next Component Number')
    bpy.types.World.parcomp_mode = bpy.props.EnumProperty(name='Mode', items=parcomp_modes)
    bpy.types.Object.parcomp_is_parametric = bpy.props.BoolProperty(name='Is Parametric')
    bpy.types.Object.parcomp_component_name_skip = bpy.props.BoolProperty(name='Skip Name Update')
    bpy.types.Object.parcomp_component_name = bpy.props.StringProperty(name='Component Name', update=parcomp_comp_name_update)
    bpy.types.Object.parcomp_component_name_sel = bpy.props.EnumProperty(name='Component Name', items=parcomp_comp_name_items, update=parcomp_comp_name_select)
    bpy.types.Object.parcomp_component_type_skip = bpy.props.BoolProperty(name='Skip Type Update')
    bpy.types.Object.parcomp_component_type = bpy.props.StringProperty(name='Type', update=parcomp_comp_type_update)
    bpy.types.Object.parcomp_component_type_sel = bpy.props.EnumProperty(name='Type', items=parcomp_comp_type_items, update=parcomp_comp_type_select)
