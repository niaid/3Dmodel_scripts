###################################################################################
# For license and additional information about this code, please refer to https://github.com/niaid/3Dmodel_scripts/blob/master/README.md
# This script runs in UCSF Chimera, an Extensible Molecular Modeling System from the Resource for Biocomputing, Visualization, and Informatics at UCSF.
# For additional information about Chimera, visit their home page: http://www.rbvi.ucsf.edu/chimera/ 

# Script name: Chimera_Molecular.py
#
# Version 2.2
# Comments:
#
# Handle situation of large (>250,000 atoms) structures from a submitted PDB file (-f option).  Can't assume that all information for "sym" command will be present.
# Make range for mapping colors to surfaces consistent across all methods.
#
# Version 2.1
# Comments:
#
# Changes to allow more than 64 chains.
# Added resolution argument to the sym command for large surfaces. First try resolution 4 and if that fails will try resolution 8.
# Version 2.0
#
# Comments:
#
# Changed the increase in ion radius from 1.8 to 0.8
# Restricted the presence of nucleotide ladders to common nucleobases (DNA and RNA) only
# Added hydrogen bonds as struts, restricted to hbonds between exposed atoms, ribbons, nucleotide backbone only.  Hbond are colored white.
# Changed pseudobond display from dashes to cylinders.  Coordination bonds and missing segments will now be included in the model.
# Missing segment radius increased relative to other pseudobonds
# Atoms in disufide bonds are displayed to act as additional struts
# Changes to arbitrary struts; loop length increased to 70, radius deceased to 0.75, color changed from white to light grey
# Ribbon cross section changed from octagon to hexadecagon, increasing number of faces
# Ribbon thickness increased in the preferences file
# All displayed carbon atoms are now colored dark grey
# All other displayed atoms are always colored by element (including ions, which were previously colored white)
# Thick ribbon models have been commented out
#
# Input:  Either a 4 character PDB accession code or a molecule file designation.
#         Allowed file types: .pdb .pdb1 .cif .fchk .gro .mae .mol .mol2 .sdf .ent
#
# Output: .png and .x3d files in the current directory for the 8 different molecular
#         representations described below.
#
# In the following file name descriptions, "bn" corresponds to the name of the 
# molecule, either the PDB code or the input file name.
#
# bn-ribbon-secondary    ribbon representation, colored by secondary structure
#
# bn-ribbon-rainbow      ribbon representation, colored by rainbow, N-terminus blue
#                        to C-terminus red 
#
# bn-ribbon-bychain      ribbon representation, colored by chain
#
# bn-ribbon              ribbon representation, monochrome
#
# bn-surf                surface representation, monochrome
#
# bn-surf-coulombic      surface representation, colored by coulombic, 
#                        negative red to positive blue
#
# bn-surf-hydropathy     surface representation, Kyte-Doolittle hydrophobicity coloring
#
# bn-surf-bychain        surface representation, colored by chain
#
# bn-surf-lipophilic     (future enhancement)
#
# bn-surf-electrostatic  (future enhancement)
#
###################################################################################
import os, sys, subprocess, getopt, math

def usage():
  print ("")
  print ("Chimera_Molecular.py: a Chimera Python script")
  print ("")
  print ("""Usage: chimera --script "Chimera_Molecular.py -f <file> | -c <code>  [yesRibbon/noRibbon]" """)
  print ("")
  print ("    -h, --help               This help message")
  print ("    -f string                File designation")
  print ("    -c string                PDB 4-digit accession code")
  print ("    yesRibbon/noRibbon       Toggle optional forcing/disabling ribbon generation")
  print ("                             By default, ribbons not produced if >25000 atoms")
  print ("")

try:
    from chimera import runCommand as rc # use 'rc' as shorthand for runCommand
    from chimera import openModels, Molecule, selection
except ImportError:
    usage()
    sys.exit(2)

# Parse the command line arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hf:c:", ["yesRibbon", "noRibbon", "help"])
except getopt.GetoptError, err:
    print (str(err))
    usage()
    sys.exit(2)
    
infile = "default"  #Will stay "default" if -c PDB code is used    

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c"):
        PDBcode = a.upper()
    elif o in ("-f"):
        infile = a
    else:
        assert False, "unhandled options"
for o in args:
    if o in ("--yesRibbon"):
        rib = 1
    elif o in ("--noRibbon"):
        rib = 0
        
def export_scene(root):
    root_name = input_name + "-" + root
    png_name = root_name + ".png"
    rc("copy file " + png_name + " width 512 height 512 supersample 3")
    rc("export format x3d " + root_name)
    
os.chdir(".")

# open the file
try:
    PDBcode
except NameError:
    rc("open " + infile)
    input_name, ext  = os.path.splitext(infile)
else:
    try:
        fetch_name = "biounitID:" + PDBcode + ".1"
        rc("open " + fetch_name)
    except:
        try:
           fetch_name = "cifID:" + PDBcode
           rc("open " + fetch_name)
#Next 3 lines for getting rid of multiple NMR structures
           numSubmodels = len(openModels.list(modelTypes=[Molecule]))
           if numSubmodels > 1:
              rc("close #0.2-" + str(numSubmodels))
        except:
           fetch_name = "pdbID:" + PDBcode
           rc("open " + fetch_name)
           numSubmodels = len(openModels.list(modelTypes=[Molecule]))
           if numSubmodels > 1:
              rc("close #0.2-" + str(numSubmodels))
    # Grab data from PDB
    input_name = PDBcode

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
rc("colordef Struts_grey 0.480 0.480 0.480")
rc("colordef Carbon_grey 0.222 0.222 0.222")


# initial processing
rc("delete solvent")    # remove water
rc("delete element.H")  # remove hydrogens
rc("delete @.B")        # remove alternate conformations

# Scaling for Surface Grid Size based on atom count before adding H
# Maximum grid size is 2.5, minimum grid size is 0.5.
numAtoms = sum([len(m.atoms) for m in openModels.list(modelTypes=[Molecule])])
#numAtoms = len(openModels.list(modelTypes=[Molecule])[0].atoms)
lognumAtoms = math.log10(numAtoms)
gridSize = lognumAtoms - 2.5
if gridSize > 2.5: 
   gridSize = 2.5
if gridSize < 0.5:
   gridSize = 0.5

#gridSize = 0.5  #Uncomment this line to force a specific grid size for testing

#outFile = open('grid.txt', 'w')
#outFile.write(str(gridSize))
#outFile.close()

#Make ribbons only if fewer than 25000 atoms
try:
 rib
except NameError:
 rib = 2
if rib == 0:
   pass   # Always skip ribbons if rib flag is set to 0
elif (numAtoms < 25000) or (rib == 1):

   if len([m for m in openModels.list(modelTypes=[Molecule])]) > 1:
      rc("combine #0 newchainids true modelID 0 close true")

# make ribbon ready for 3D printing
   rc("setattr m stickScale 4 #0")
   rc("vdwdef +0.8 ions")
#   rc("nucleotides sidechain tube/slab thickness 1")
   rc("ribbon nucleic acid")      # fixes bug in representing some NA chains
   rc("select :/type=A | :/type=U | :/type=C | :/type=G | :/type=DA | :/type=DT | :/type=DG | :/type=DC") #restricts nucleic acid ladder to known nucleic acids (not ATP etc)
   rc("nucleotides sidechain ladder radius 1.2 sel")
   rc("~select :all")
   rc("select backbone.full & protein | nucleic acid & backbone.minimal | ions | ligand | ligand zr< 5 &~nucleic acid") #restricts the addition of hydrogen bonds to backbone atoms, ions, ligands, and atoms within 5A of ligands (but not nucleobases within 5A of ligands)
   rc("hbond color white selRestrict both")
   rc("setattr p drawMode 1") #changes pseudobonds from lines to sticks
   rc("setattr g stickScale 3") #increases pseudobond stick scale
   rc("setattr g stickScale 5.5 @c,n") #increases missing segment pseudobond stick scale relative to hbond
   rc("setattr g stickScale 5.5 @n,n") #increases missing segment pseudobond stick scale relative to hbond
   rc("~select :all")
   rc("select disulfide") #displays disulfide bonds at sticks (extra struts)
   rc("select up")
   rc("display sel")
   rc("bondrepr stick sel")
   rc("~select :all")
   rc("struts @ca|ligand|element.P|#/numAtoms<500 length 8 loop 60 rad 0.75 color Struts_grey") #adds struts to P atoms
   rc("~struts @PB,PG")
   rc("~struts \"nucleoside base.all of the above\"")
   rc("ribscale 3d_print #0")     # fixes bug in struts command, need "3d_print" definition in preferences file
   rc("ribrepr hexadecagon #0") # reduces ribbon complexity, need "hexadecagon" definition in preferences file
   rc("set subdivisionPixels 10") # reduces ribbon complexity
#rc("ribscale for 3Dprint1round")

# output secondary structure color ribbon 3D print
   rc("color white")
   rc("color Marine helix; color Firebrick strand; color Gold coil; color Forest nucleic acid")
   rc("color Grape :/type=A; color Grape :/type=C; color Grape :/type=G; color Grape :/type=U")
   rc("color byatom")
   rc("select C & ligand | C & ligand zr< 5 &~nucleic acid| C & protein| C & disulfide") #restricts atomic selection to displayed Carbon atoms
   rc("color Carbon_grey,a sel") #colors selected residues dark grey
   rc("color byhet,a ligand|protein&side chain/base.without CA/C1'")
   rc("~select :all")
   export_scene("ribbon-secondary")

# output rainbow color 3D print
   rc("color white")
   rc("rainbow @CA")
   rc("color white,a side chain/base.without CA/C1'")
   rc("color byatom")
   rc("select C & ligand | C & ligand zr< 5 &~nucleic acid| C & protein| C & disulfide") #restricts atomic selection to displayed Carbon atoms
   rc("color Carbon_grey,a sel") #colors selected residues dark grey
   rc("color byhet,a ligand|protein&side chain/base.without CA/C1'")
   rc("~select :all")
   export_scene("ribbon-rainbow")

# output colored by chain ribbon 3D print
   if len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 1:
       rc("rainbow chain Marine,Marine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 2:
       rc("rainbow chain Marine,Gold @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 3:
       rc("rainbow chain Marine,Gold,Firebrick @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 4:
       rc("rainbow chain Marine,Gold,Firebrick,Forest @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 5:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 6:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine,Grape @CA")
   else:
       rc("rainbow chain @CA")
   rc("color byatom")
   rc("select C & ligand | C & ligand zr< 5 &~nucleic acid| C & protein| C & disulfide") #restricts atomic selection to displayed Carbon atoms
   rc("color Carbon_grey,a sel") #colors selected residues dark grey
   rc("color byhet,a ligand|protein&side chain/base.without CA/C1'")
   rc("~select :all")
   export_scene("ribbon-bychain")

# output monochrome ribbon 3D print
   rc("color NIH_blue")
   rc("setattr p color NIH_blue")
   export_scene("ribbon")

# output monochrome thick ribbon 3D print
   #rc("~nucleotides")
   #rc("represent sphere")
   #rc("vdwdefine +0.4")
   #rc("ribrepr rounded #0")
   #rc("~struts")
   #rc("struts @ca|ligand|element.P|#/numAtoms<500 length 6.5 color NIH_blue")
   #rc("ribscale thick_ribbon #0") # need "thick_ribbon" definition in preferences file
   #export_scene("ribbon-thick")

######################## SURFACES ###############################################
# Prep for surfaces
rc("close #1")            # close the struts
rc("delete ligand|ions")  # remove ligands and ions
rc("select protein|nucleic acid; select invert sel; delete sel")   # delete everything that isn't amino or nucleic
if numAtoms < 25000:      #Only do slow addition of hydrogens if <25000 atoms
   rc("addh")             # protonate

rc("~select :all")
rc("~nuc")                #hide nucleotide ladders
rc("~ribbon")             # hide the ribbon
rc("~display")            # hide the atoms
#rc("split")

if (numAtoms <250000) or (infile != "default"):
   #If there are submodels, combine them into single new model in #0
   numSubmodelsP = 2
   if len([m for m in openModels.list(modelTypes=[Molecule])]) > 1:
      try:
        rc("combine #0 newchainids true modelID 0 close true")
        numSubmodelsP = 2   #This needs LOTS of testing
      except:
        numSubmodels = len(openModels.list(modelTypes=[Molecule]))
        numSubmodelsP = numSubmodels + 1   #to get loop index range right
   # Generate surface
   gridSizeStr = str(gridSize)
   rc("surface #0 grid " + gridSizeStr + " warnLarge false")
   if numAtoms > 250000:
     chimera.viewer.viewAll()
     rc("scale 0.9")

   # output monochrome surface 3D print
   rc("color NIH_blue")
   export_scene("surf")
   rc("color white")


   # output Coulombic coloring surface 3D print if <25000 atoms
   if numAtoms < 25000:
      description = "coulombicsurf"
      rc("addcharge std")
      rc("coulombic atoms #0 -10 red 0 white 10 blue #1")
      export_scene("surf-coulombic")

   # output Kyte-Doolittle coloring surface 3D print (only works on amino acids)
   # check for protein (only works on amino acids)
   rc("select protein")
   if len(selection.currentAtoms()) > 0:
      rc("~select")
      rc("color magenta #0")
      rc("rangecolor kdHydrophobicity min 0.16,0.67,0.87 max 1.00,0.45,0.00 mid white novalue magenta #0")
   #Need to loop from 1 to numSubmodels and put into scolor #1
   for surfs in range(1, numSubmodelsP):
     try:
       rc("scolor #" + str(surfs) + " zone #0 range 6.0")
     except:
       try:
         rc("scolor #0." + str(surfs) + " zone #0 range 6.0")
       except:
         pass
   export_scene("surf-hydropathy")

   # output colored by chain surface 3D print
   if len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 1:
       rc("rainbow chain Marine,Marine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 2:
       rc("rainbow chain Marine,Gold @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 3:
       rc("rainbow chain Marine,Gold,Firebrick @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 4:
       rc("rainbow chain Marine,Gold,Firebrick,Forest @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 5:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 6:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine,Grape @CA")
   else:
       rc("rainbow chain @CA")
   #rc("color white,a nucleic acid&side chain/base.without CA/C1'")
   #rc("color byhet,a protein&side chain/base.without CA/C1'")
   for surfs in range(1, numSubmodelsP):
#       #rc("scolor #1 zone #0 range 6.0")
       try:
         rc("scolor #" + str(surfs) + " zone #0 range 6.0")
       except:
         try:
           rc("scolor #0." + str(surfs) + " zone #0 range 6.0")
         except:
           print "failed"
   export_scene("surf-bychain")


# lipophilic potential mapping  (MLP only works on amino acids)
#temp_pdb_name = input_name + "-for_MLP.pdb"
#temp_dx_name = input_name + "-for_MLP.dx"
#rc("write #0 " + temp_pdb_name)   # write out a structure for MLP processing
#subprocess.check_call(["pyMLP -i " + temp_pdb_name], shell=True)    # run pyMLP to generate a DX file
#rc("open " + temp_dx_name)                                    # should be model ID #1
#rc("scolor #0 volume #1 cmap 0.0,0.16,0.67,0.87:0.5,white:1.0,1.00,0.45,0.00 cmapRange full")   # Erin
##rc("scolor #0 volume #1 cmap 0,0.086275,0.2,0.764706:0.066666667,0.086275,0.301961,0.682353:0.133333333,0.086275,0.439216,0.619608:0.2,0.156863,0.486275,0.537255:0.266666667,0.219608,0.564706,0.556863:0.333333333,0.411765,0.592157,0.439216:0.4,0.337255,0.556863,0.184314:0.466666667,0.176471,0.54902,0.109804:0.533333333,0,0.67451,0:0.6,0,0.54902,0.219608:0.666666667,0.121569,0.447059,0.094118:0.733333333,0.329412,0.364706,0.094118:0.8,0.529412,0.364706,0.094118:0.866666667,0.439216,0.301961,0.094118:0.933333333,0.376471,0.211765,0.094118:1,0.309804,0.109804,0.07451 cmapRange full")    # SYBYL MLP
#export_scene("surf-lipophilic")
#rc("close #1")
#os.remove(temp_pdb_name)
#os.remove(temp_dx_name)

# electrostatic potential mapping  (PQR only works on proteins)
#temp_pqr_name = input_name + "-from_PDB2PQR.pqr"
#temp_dx_name = input_name + "-from_APBS.dx"
#rc("pdb2pqr pqr " + temp_pqr_name + " wait true")                  # run PDB2PQR to prep for APBS, makes model ID #1
#rc("~ribbon")
#rc("~display")
#rc("apbs molecule #1 output " + temp_dx_name + " wait true")            # potential file is model ID #2
#rc("close #1")
#rc("scolor #0 volume #2 offset 1.4 cmap -10,red:0,white:10,blue")   # default
##rc("scolor #0 volume #2 offset 1.4 cmap -10,0.98,0.01,0.24:0,white:10,0.00,0.60,0.60")  # Erin
##rc("scolor #0 volume #2 offset 1.4 cmap -10,0.321569,0.109804,0.764706:-8.666666667,0.376471,0.164706,1.000000:-7.333333333,0.258824,0.266667,1.000000:-6,0.137255,0.337255,0.737255:-4.666666667,0.094118,0.427451,0.976471:-3.333333333,0.094118,0.556863,0.894118:-2,0.058824,0.701961,0.658824:-0.666666667,0.101961,0.886275,0.701961:0.666666667,0.411765,0.819608,0.568627:2,0.439216,0.701961,0.529412:3.333333333,0.486275,0.674510,0.149020:4.666666667,0.631373,0.631373,0.149020:6,0.631373,0.458824,0.149020:7.333333333,0.631373,0.337255,0.149020:8.666666667,0.631373,0.247059,0.149020:10,0.641844,0.008000,0.224000")   # SYBYL ESP
#export_scene("surf-electrostatic")
#os.remove(temp_pqr_name)
#os.remove(temp_dx_name)

else:     #greater than 250000 atoms and from RCSB
   #close the structure then open the pdb and not bio unit
   rc("close #0")
   try:
      fetch_name = "cifID:" + PDBcode
      rc("open " + fetch_name)
   except:
      fetch_name = "pdbID:" + PDBcode
      rc("open " + fetch_name)

   #delete everything unnecessary
   rc("delete solvent")    # remove water
   rc("delete element.H")  # remove hydrogens
   rc("delete @.B")        # remove alternate conformations
   rc("delete ligand|ions")  # remove ligands and ions
   rc("select protein|nucleic acid; select invert sel; delete sel")   # delete everything that isn't amino or nucleic
   #Use sym command to make surface, analogous to MultiScale 
   try:
     rc("sym #0 surfaces all resolution 4")
   except:
     rc("sym #0 surfaces all resolution 8")
   rc("~ribbon #0")   #turn off ribbon since they may protrude from surface
   rc("~display #0")  #turn off atoms since they may protrude from surface

#  import MultiScale
#  d = MultiScale.show_multiscale_model_dialog()
#  d.make_multimers_cb(molecules=None)
   chimera.viewer.viewAll()
   rc("scale 0.9")    #Fix so sym surfaces fit in .png file scene

   # output monochrome surface 3D print
   rc("color NIH_blue")
   rc("msc #1 #0 6.0")
   export_scene("surf")
   rc("color white") 

   # output Kyte-Doolittle coloring surface 3D print (only works on amino acids)
   rc("color magenta #0")
   rc("rangecolor kdHydrophobicity min 0.16,0.67,0.87 max 1.00,0.45,0.00 mid white novalue magenta #0")
   rc("msc #1 #0 6.0")
   export_scene("surf-hydropathy")

   # output colored by chain surface 3D print
   if len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 1:
       rc("rainbow chain Marine,Marine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 2:
       rc("rainbow chain Marine,Gold @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 3:
       rc("rainbow chain Marine,Gold,Firebrick @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 4:
       rc("rainbow chain Marine,Gold,Firebrick,Forest @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 5:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine @CA")
   elif len(openModels.list(modelTypes=[Molecule])[0].sequences()) == 6:
       rc("rainbow chain Marine,Gold,Firebrick,Forest,Tangerine,Grape @CA")
   else:
       rc("rainbow chain @CA")
   #rc("color white,a nucleic acid&side chain/base.without CA/C1'")
   #rc("color byhet,a protein&side chain/base.without CA/C1'")
   rc("msc #1 #0 6.0")
   export_scene("surf-bychain")

rc("stop now")
