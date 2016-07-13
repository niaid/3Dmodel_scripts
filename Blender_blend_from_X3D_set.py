# For license and additional information about this code, please refer to https://github.com/niaid/3Dmodel_scripts/blob/master/README.md
# This script runs in Blender: https://www.blender.org/

import os, sys, getopt, bpy

input_name = sys.argv[6]
kinds = sys.argv[7].split(",")

for kind in kinds:
    print("Processing " + kind)
    bpy.ops.wm.read_homefile()
    bpy.ops.import_scene.x3d(filepath = input_name + "-" + kind + ".x3d")
    bpy.ops.wm.save_as_mainfile(filepath = input_name + "-" + kind + ".blend", check_existing = False)

bpy.ops.wm.quit_blender()

