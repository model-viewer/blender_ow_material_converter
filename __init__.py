bl_info = {
    "name": "Transform OW Materials to GLTF Compatible",
    "author": "Adriano Martins",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Transform OW Materials to GLTF",
    "description": "The shaders created by the OW loader are not exportable to GLTF. This addon converts it to valid ones",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


OWM_SHADER_TO_PRINCIPLED_BSDF = {
    'AO': 'Emission',
    'Color': 'Base Color', # Base Color?
    'Emission': 'Emission',
    'Emission Strength': 'Emission Strength',
    'Alpha': 'Alpha',
    'Normal': 'Normal',
    'Normal Strength': 'Normal Strength',
    'Packed PBR': None,
}

class CUSTOM_OW_MODEL_MATERIAL_import_model(bpy.types.Operator):
    bl_label = "Import .owmdl"
    bl_idname = "mesh.import_owmdl"
    filepath: bpy.props.StringProperty() 
    
    def invoke(self, context, event):

        # Run on all materials and convert old materials to new ones        
        for mat in bpy.data.materials:
            self.report({"INFO"}, "MAT " + mat.name)
            # Update settings to be exported correctly
            mat.blend_method = "OPAQUE"
            mat.use_nodes = True
            # The material that can be exported to GLTF
            principled = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
            
            # The original shader created by the loader
            original = [i for i in mat.node_tree.nodes if 'OWM Shader' in i.label]
            if not original:
                continue
            original = original[0]
            
            for link in mat.node_tree.links:
                # Not sure if we should just ignore this. Maybe we need to do something else
                if link.to_node != original:            
                    continue

                self.report({"INFO"}, "LINK TO SOCKET " + link.to_socket.name)
                # Check if we know the target socket
                target_socket_name = OWM_SHADER_TO_PRINCIPLED_BSDF.get(link.to_socket.name)
                if not target_socket_name:
                    continue
                
                target_socket = principled.inputs.get(target_socket_name)

                # Create the link between the Principled BSDF and the existing thing
                mat.node_tree.links.new(link.from_socket, target_socket)
                
                # Remove the old existing link
                mat.node_tree.links.remove(link)
            
            # Replace the link between the original shader and the new Principled
            mat.node_tree.links.new(principled.outputs.get('BSDF'), original.outputs.get('Shader').links[0].to_socket)
            
            # Remove the original shader
            mat.node_tree.nodes.remove(original)
        
    
        return {"FINISHED"}
    
# Registration
def add_object_button(self, context):
    self.layout.operator(
        CUSTOM_OW_MODEL_MATERIAL_import_model.bl_idname,
        text="Transform OW Materials to GLTF",
        icon='PLUGIN')


def register():
    bpy.utils.register_class(CUSTOM_OW_MODEL_MATERIAL_import_model)
    bpy.types.TOPBAR_MT_file.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(CUSTOM_OW_MODEL_MATERIAL_import_model)
    bpy.types.TOPBAR_MT_file.remove(add_object_button)


if __name__ == "__main__":
    register()
