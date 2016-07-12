import os, sys, getopt

# It takes an X3D file and exports a preview PNG for it, an STL with the same model, and a preview PNG for the STL in the "NIH blue" color

def usage():
    print ("")
    print ("Blender_PNG_from_X3D.py: a Python script to be executed in Blender")
    print ("")
    print ("""Usage: blender --background --factory-startup --python Blender_PNG_from_X3D.py -- <X3D_file>""")
    print ("")

try:
    import bpy
except ImportError:
    usage()
    sys.exit(2)

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

# open the file
if len(args) == 1:
    X3D_file = args[0]
    input_name, ext  = os.path.splitext(X3D_file)
    PNG_file = input_name + ".png"
else:
    print("\nError: You must specify a single X3D file")
    usage()
    sys.exit(2)


os.chdir(".")
 
# CLEAN UP INITIAL VIEW
bpy.ops.object.select_by_type(extend=False, type='MESH')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='LAMP')
bpy.ops.object.delete(use_global=False)

# IMPORT THE MESH
print("importing " + X3D_file + "\n")
bpy.ops.import_scene.x3d(filepath = X3D_file)

# DELETE THE OTHER IMPORTED OBJECTS
print("Deleting the imported lamps and curves\n")
bpy.ops.object.select_by_type(extend=False, type='LAMP')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_by_type(extend=False, type='CURVE')
bpy.ops.object.delete(use_global=False)

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
#        else:
#            print(str(mesh_object) + " has material(s); turning off vertex coloring")
#            for mesh_object_material in mesh_object.data.materials.values():
#                bpy.data.materials[mesh_object_material.name].use_vertex_color_paint = False
#                print(str(mesh_object) + " has material " + str(mesh_object_material) + " ; turning off vertex coloring")
    else:
        for mesh_object_material in mesh_object.data.materials.values():
            bpy.data.materials[mesh_object_material.name].use_vertex_color_paint = False
#            print(str(mesh_object) + " has material " + str(mesh_object_material) + " ; turning off vertex coloring")

# CAMERA
print("Setting camera\n")
bpy.ops.object.select_by_type(extend=False, type='MESH')
bpy.context.scene.camera = bpy.data.objects['Camera']
bpy.ops.view3d.camera_to_view_selected()
bpy.data.cameras['Camera'].clip_end = 1000000
  
# SET SCENE
print("Setting the background color\n")
bpy.data.worlds['World'].horizon_color[0]=1
bpy.data.worlds['World'].horizon_color[1]=1
bpy.data.worlds['World'].horizon_color[2]=1
bpy.data.worlds['World'].light_settings.use_ambient_occlusion = True
bpy.data.worlds['World'].light_settings.gather_method = 'APPROXIMATE'

# SAVE PNG
print("Rendering " + PNG_file +"\n")
bpy.data.scenes['Scene'].render.resolution_x = 500
bpy.data.scenes['Scene'].render.resolution_y = 500
bpy.data.scenes['Scene'].render.resolution_percentage = 100
bpy.data.scenes['Scene'].render.filepath = PNG_file
bpy.ops.render.render(write_still=True)

# EXPORT X3D
print("Exporting " + X3D_file +"\n")
bpy.ops.export_scene.x3d(filepath=X3D_file)

# SAVE .BLEND
print("Saving .blend file")
bpy.ops.wm.save_as_mainfile(filepath = input_name + ".blend", check_existing = False)

# ------------------------------------
# NOW WE NEED TO MAKE AN STL OUT OF IT
# ------------------------------------

# RECOLOR TO NIH BLUE
mat = bpy.data.materials.new("NIH_blue")
mat.diffuse_color = (0.20,0.38,0.60)
mat.diffuse_shader = 'LAMBERT' 
mat.diffuse_intensity = 1.0 
mat.specular_color = (1,1,1)
mat.specular_shader = 'COOKTORR'
mat.specular_intensity = 0.5
mat.alpha = 1
mat.ambient = 1
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        o.data.materials.clear()
        o.data.materials.append(mat)
        
# EXPORT STL
print("Exporting STL file\n")
bpy.ops.export_mesh.stl(filepath=input_name + "-mono.stl")

# SAVE MONOCHROME PNG
print("Rendering monochrome PNG\n")
bpy.data.scenes['Scene'].render.filepath = input_name + "-mono.png"
bpy.ops.render.render(write_still=True)

# SAVE OUT X3D
print("Exporting cleaned monochrome X3D file")
bpy.ops.export_scene.x3d(filepath=input_name + "-mono.x3d")

# SAVE .BLEND
print("Saving monochrome .blend file")
bpy.ops.wm.save_as_mainfile(filepath = input_name + "-mono.blend", check_existing = False)

# QUIT
print("Quitting Blender")
bpy.ops.wm.quit_blender()
sys.exit(0)
