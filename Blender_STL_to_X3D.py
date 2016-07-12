import os, sys, getopt

def usage():
    print ("")
    print ("Blender_STL_to_X3D.py: a Python script to be executed in Blender")
    print ("")
    print ("""Usage: blender --background --factory-startup --python BlenderSTL2X3D.py -- <STL_file>""")
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

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT' 
    mat.diffuse_intensity = 1.0 
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat
 
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)
 
cyan = makeMaterial('Cyan', (0,1,1), (1,1,1), 1)
NIH_blue1 = makeMaterial('NIH_blue1', (0.125,0.333,0.541), (1,1,1), 1)
NIH_blue2 = makeMaterial('NIH_blue2', (0.20,0.38,0.60), (1,1,1), 1)
Erin_blue = makeMaterial('Erin_blue', (0.42,0.64,0.72), (1,1,1), 1)

# open the file
if len(args) == 1:
    STL_file = args[0]
    input_name, ext  = os.path.splitext(STL_file)
    X3D_file = input_name + ".x3d"
    PLY_file = input_name + ".ply"
    PNG_file = input_name + ".png"
else:
    print("\nError: You must specify a single STL file")
    usage()
    sys.exit(2)


os.chdir(".")
 
# CLEAN UP INITIAL VIEW
bpy.ops.object.select_by_type(extend=False, type='MESH')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='LAMP')
bpy.ops.object.delete(use_global=False)

# IMPORT THE MESH
bpy.ops.import_mesh.stl(filepath = STL_file)

# REMOVE DOUBLED VERTICES AND ADJUST NORMALS
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.remove_doubles()
#bpy.ops.mesh.normals_make_consistent()
bpy.ops.object.mode_set(mode='OBJECT')

# CENTER AND COLOR
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
bpy.ops.object.location_clear()
bpy.ops.object.visual_transform_apply()
setMaterial(bpy.context.object, NIH_blue2)
bpy.data.worlds['World'].horizon_color[0]=1
bpy.data.worlds['World'].horizon_color[1]=1
bpy.data.worlds['World'].horizon_color[2]=1
bpy.ops.view3d.camera_to_view_selected()
bpy.data.cameras['Camera'].clip_end = 1000000
bpy.data.worlds['World'].light_settings.use_ambient_occlusion = True
bpy.data.worlds['World'].light_settings.gather_method = 'APPROXIMATE'
bpy.data.scenes['Scene'].render.resolution_x = 500
bpy.data.scenes['Scene'].render.resolution_y = 500
bpy.data.scenes['Scene'].render.resolution_percentage = 100
bpy.data.scenes['Scene'].render.filepath = PNG_file
bpy.ops.render.render(write_still=True)


# EXPORT DIFFERENT FORMATS
bpy.ops.export_scene.x3d(filepath=X3D_file)
#bpy.ops.export_mesh.ply(filepath=PLY_file)

# SAVE .BLEND
print("Saving .blend file")
bpy.ops.wm.save_as_mainfile(filepath = input_name + ".blend", check_existing = False)

# QUIT
bpy.ops.wm.quit_blender()
sys.exit(0)
