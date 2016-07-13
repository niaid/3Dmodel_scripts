# For license and additional information about this code, please refer to https://github.com/niaid/3Dmodel_scripts/blob/master/README.md
# This script runs in UCSF Chimera, an Extensible Molecular Modeling System from the Resource for Biocomputing, Visualization, and Informatics at UCSF.
# For additional information about Chimera, visit their home page: http://www.rbvi.ucsf.edu/chimera/ 

import os, sys, getopt

def usage():
    print ("")
    print ("Chimera_Volumetric.py: a Python script to be executed in Chimera")
    print ("")
    print ("""Usage: chimera --script "path/to/Chimera_Volumetric.py -f <file> | -c <code> [-l <num>]" """)
    print ("")
    print ("    -h, --help           This help message")
    print ("    -f string            File designation")
    print ("    -c string            EMDB 4-digit accession code")
    print ("    -l float             A recommended contour level (optional)")
    print ("")

try:
    from chimera import runCommand as rc # use 'rc' as shorthand for runCommand                   
except ImportError:
    usage()
    sys.exit(2)

# Parse the command line arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hf:c:l:", [ "help" ] )
except getopt.GetoptError, err:
    print (str(err))
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c"):
        EMDBcode = a
    elif o in ("-f"):
        infile = a
    elif o in ("-l"):
        contourLevel = a
    else:
        assert False, "unhandled options"

def export_scene(root):
    root_name = input_name + "-" + root
    png_name = root_name + ".png"
    rc("copy file " + png_name + " width 512 height 512 supersample 3")
    rc("export format x3d " + root_name)

os.chdir(".")

# open the file
try:
    EMDBcode
except NameError:
    rc("open " + infile)
    input_name, ext  = os.path.splitext(infile)
else:
    fetch_name = "emdbID:" + EMDBcode
    rc("open " + fetch_name)
    input_name = EMDBcode

# Setup the lighting
rc("windowsize 512 512")
rc("background solid white")
rc("lighting mode three-point")
rc("lighting brightness 1.0")
rc("lighting contrast 0.85")
rc("lighting ratio 2.25")
rc("lighting sharpness 62")
rc("lighting reflectivity 0.3")
rc("lighting key direction 0 0 1")
rc("lighting fill direction 0.8 0.3 .2")
rc("lighting back direction -0.5 -0.5 -1")

rc("colordef NIH_blue 0.125 0.333 0.541")


# CONTOUR THE MESH
try:
    contourLevel
except NameError:
    rc("volume #0 step 1 limitVoxelCount false")
else:
    if contourLevel != '':
        rc("volume #0 level " + contourLevel + " limitVoxelCount true voxelLimit 8")
    else:
        rc("volume #0 limitVoxelCount true voxelLimit 8")

# MESH CLEANING
rc("sop hideDust #0 size 1 metric sizeRank")

rc("color white")

# RADIAL COLORING
rc("scolor #0 geometry radial cmap rainbow")
export_scene("surf-radial")

# MONOCHROME
rc("color NIH_blue")
export_scene("surf")

rc("stop now")
