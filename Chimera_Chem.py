# For license and additional information about this code, please refer to https://github.com/niaid/3Dmodel_scripts/blob/master/README.md
# This script runs in UCSF Chimera, an Extensible Molecular Modeling System from the Resource for Biocomputing, Visualization, and Informatics at UCSF.
# For additional information about Chimera, visit their home page: http://www.rbvi.ucsf.edu/chimera/ 

import os, sys, subprocess, getopt, math

def usage():
  print ("")
  print ("Chimera_Chem.py: a Chimera Python script")
  print ("")
  print ("""Usage: chimera --script "Chimera_Chem.py -f <file> -c <code>" """)
  print ("")
  print ("    -h, --help           This help message")
  print ("    -f string            File designation")
  print ("    -c string            PubChem accession code")
  print ("")

try:
    from chimera import runCommand as rc # use 'rc' as shorthand for runCommand
    from chimera import openModels, Molecule
except ImportError:
    usage()
    sys.exit(2)

# Parse the command line arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hf:c:", [ "help" ] )
except getopt.GetoptError, err:
    print (str(err))
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c"):
        PubChem_code = a.upper()
    elif o in ("-f"):
        infile = a
    else:
        assert False, "unhandled options"


def export_scene(root):
    root_name = input_name + "-" + root
    png_name = root_name + ".png"
    rc("copy file " + png_name + " width 512 height 512 supersample 3")
    rc("export format x3d " + root_name)

def export_wrl(root):
    root_name = input_name + "-" + root
    rc("export format vrml " + root_name)

def export_stl(root):
    root_name = input_name + "-" + root
    if root == "CPK":
       res = 8
    elif root == "sticks":
       res = 16
    elif root == "bas":
       res = 32
    else:
       res = 8
    resstr = str(res)
    cmd = "x3d2stl -c -r "+resstr +" -o "+root_name +".stl" +" < " +root_name +".x3d"
    os.system( cmd )
#    rc("export format stl " + root_name)

    
os.chdir(".")

# open the file
try:
    PubChem_code
except NameError:
    input_name, ext  = os.path.splitext(infile)
    rc("open " + infile)
else:
    input_name = PubChem_code
    rc("open " + infile)

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

rc("colordef Marine 0.000 0.500 1.000")
rc("colordef Gold 1.000 0.843 0.000")
rc("colordef Firebrick 0.698 0.133 0.133")
rc("colordef Forest 0.133 0.545 0.133")
rc("colordef Tangerine 0.953 0.518 0.000")
rc("colordef Grape 0.643 0.000 0.867")
rc("colordef NIH_blue 0.125 0.333 0.541")
rc("colordef Jmol_carbon 0.565 0.565 0.565")
rc("colordef Bond_purple 0.576 0.439 0.859")

# remove ribbons and nucleotide rungs if input is PDB file
rc("~ribbon")
rc("~nucleotides")
rc("show")

# thicken for 3D printing
rc("setattr m stickScale 4 #0")
rc("~vdwdefine ions")
rc("vdwdefine +0.35 ions")

# Change coordination complex bonds to sticks
rc("setattr p drawMode 1") #changes pseudobonds from lines to sticks
rc("setattr g stickScale 2") #increases pseudobond stick scale

# output color sticks 3D print
rc("color Jmol_carbon")
rc("color byhet,a")
export_scene("sticks-color")
export_wrl("sticks-color")

# output monochrome sticks 3D print
rc("color NIH_blue")
rc("setattr p color NIH_blue")
export_scene("sticks")
export_stl("sticks")

# spheres for 3D printing
rc("represent cpk")
rc("setattr p drawMode 0") #changes pseudobonds from sticks to lines

# output color CPK 3D print
rc("color Jmol_carbon")
rc("color byhet,a")
rc("setattr p color Bond_purple")
rc("vdwdefine +0.15 element.H")  #rescale H atoms to get better-looking balls
export_scene("CPK-color")
export_wrl("CPK-color")

# output monochrome CPK 3D print
rc("color NIH_blue")
rc("setattr p color NIH_blue")
export_scene("CPK")
export_stl("CPK")
rc("~vdwdefine")      #rescale H atoms to default vdw radii

# ball-and-stick representation and scaling
#Default stickScale=1.0 and ballScale=0.25
rc("represent bs")
rc("vdwdefine +0.2 element.H")  #rescale H atoms to look more like balls
rc("~vdwdefine ions")
rc("vdwdefine +1.5 ions")
rc("setattr m stickScale 1.2")
rc("setattr m ballScale 0.3")
rc("setattr p drawMode 1") #changes pseudobonds from lines to sticks
rc("setattr g stickScale 1") #increases pseudobond stick scale

# output color ball-and-stick 3D print
rc("color Jmol_carbon")
rc("color byhet,a")
rc("setattr p color Bond_purple")
export_scene("bas-color")
export_wrl("bas-color")

# output monochrome ball-and-stick 3D print
rc("color NIH_blue")
rc("setattr p color NIH_blue")
export_scene("bas")
export_stl("bas")
rc("~vdwdefine")   #rescale H atoms to default vdw radii

rc("stop now")
