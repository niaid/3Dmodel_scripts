# For license and additional information about this code, please refer to https://github.com/niaid/3Dmodel_scripts/blob/master/README.md
# This script runs in Blender: https://www.blender.org/

import os, sys, getopt

def usage():
    print ("")
    print ("Blender_VRML_cleanup.py: a Python script to be executed in Blender")
    print ("")
    print ("""Usage: blender --background --factory-startup --python Blender_VRML_cleanup.py -- <WRL_file>""")
    print ("")

try:
    import bpy
except ImportError:
    usage()
    sys.exit(2)

#print(sys.argv)

# Parse the command line arguments
try:
    opts, args = getopt.getopt(sys.argv[6:], "h", [ "help" ] )
except getopt.GetoptError as err:
    print (str(err))
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    else:
        assert False, "unhandled options"

#print(args)

# open the file
if len(args) == 1:
    WRL_file = args[0]
    input_name, ext  = os.path.splitext(WRL_file)
    X3D_file = input_name + ".x3d"
else:
    print("\nError: You must specify a single WRL file")
    usage()
    sys.exit(2)


os.chdir(".")


# CLEAN UP INITIAL VIEW
bpy.ops.object.select_by_type(extend=False, type='MESH')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='LAMP')
bpy.ops.object.delete(use_global=False)

# IMPORT THE MESH
print("Importing " + WRL_file + "\n")
bpy.ops.import_scene.x3d(filepath=WRL_file)

# CLEAN UP THE OTHER IMPORTED OBJECTS
print("Deleting the imported lamps and curves\n")
bpy.ops.object.select_by_type(extend=False, type='LAMP')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='CAMERA')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='CURVE')
bpy.ops.object.delete(use_global=False)

# JOIN THE SUB-MESHES
print("Joining the sub-meshes\n")
#bpy.ops.object.select_pattern(pattern="Shape*", case_sensitive=False, extend=True)
bpy.ops.object.select_by_type(extend=False, type='MESH')
bpy.context.scene.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.join()

# REMOVE DOUBLED VERTICES AND ADJUST NORMALS
print("Removing doubled vertices")
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.remove_doubles()
#bpy.ops.mesh.normals_make_consistent()
bpy.ops.object.mode_set(mode='OBJECT')

# Decimate
#print("Decimating to ratio 0.375\n")
#bpy.ops.object.modifier_add(type="DECIMATE")
#bpy.context.object.modifiers['Decimate'].ratio = .375
#bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

# REMOVE DOUBLED VERTICES AGAIN
#print("Removing doubled vertices")
#bpy.ops.object.mode_set(mode='EDIT')
#bpy.ops.mesh.remove_doubles()
#bpy.ops.object.mode_set(mode='OBJECT')

# Check to see if each mesh has "Col" vertex group;
# if so, then turn on vertex color
print("Determining if per-vertex coloring is needed")
bpy.ops.object.select_by_type(extend=False, type='MESH')
for mesh_object in bpy.context.selected_objects:
    bpy.context.scene.objects.active = mesh_object
    if len(mesh_object.data.vertex_colors.values()) > 0:
        print(str(mesh_object) + " has vertex colors")
        if len(mesh_object.data.materials.values()) == 0:
            print(str(mesh_object) + " has no material; adding material and turning on vertex coloring")
            mesh_object.data.materials.append(bpy.data.materials.new(mesh_object.name))
            bpy.data.materials[mesh_object.name].use_vertex_color_paint = True
        else:
            print(str(mesh_object) + " has material(s); turning on vertex coloring")
            for mesh_object_material in mesh_object.data.materials.values():
                bpy.data.materials[mesh_object_material.name].use_vertex_color_paint = True
#                print(str(mesh_object) + " has material " + str(mesh_object_material) + " ; turning off vertex coloring")
    else:
        for mesh_object_material in mesh_object.data.materials.values():
            bpy.data.materials[mesh_object_material.name].use_vertex_color_paint = False
#            print(str(mesh_object) + " has material " + str(mesh_object_material) + " ; turning off vertex coloring")

# CENTER
print("Moving object to center\n")
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
bpy.ops.object.location_clear()
bpy.ops.object.visual_transform_apply()

# CAMERA
print("Setting camera\n")
bpy.ops.object.select_by_type(extend=False, type='MESH')
sc = bpy.context.scene
cam = bpy.data.objects.get('Camera')
if not cam:
    # Assume there's a camera but not a scene object around it
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.get("Camera"))
sc.camera = cam 
bpy.ops.view3d.camera_to_view_selected()
bpy.data.cameras['Camera'].clip_end = 1000000


# SET SCENE
print("Setting the background color\n")
bpy.data.worlds['World'].horizon_color[0]=1
bpy.data.worlds['World'].horizon_color[1]=1
bpy.data.worlds['World'].horizon_color[2]=1

# SAVE OUT X3D
print("Exporting " + X3D_file +"\n")
bpy.ops.export_scene.x3d(filepath=X3D_file)

# SAVE .BLEND
print("Saving .blend file")
bpy.ops.wm.save_as_mainfile(filepath=input_name + ".blend", check_existing = False)

# QUIT
print("Quitting Blender")
bpy.ops.wm.quit_blender()
#sys.exit(0)
