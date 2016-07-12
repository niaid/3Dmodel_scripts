#! vtkpython

import sys, getopt

xsize = 500
ysize = 500

def usage():
    print ""
    print "ply2png.py [options] input_ply output_png"
    print ""
    print "    -x int    Window X size"
    print "    -y int    Window Y size"
    print ""

try:
    opts, args = getopt.getopt( sys.argv[1:], "vhx:y:",
                                [ "verbose", "help" ] )

except getopt.GetoptErr, err:
    print (str(err))
    usage()
    sys.exit(1)

for o, a in opts:
    if o in ("-v", "--verbose"):
        verbose = verbose + 1
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-x"):
        xsize = int(a)
    elif o in ("-y"):
        ysize = int(a)
    else:
        assert False, "unhandled options"

if len(args) < 2:
   usage()
   sys.exit(2)

inname = args[0]
outname = args[1]


from vtk import *


reader = vtkPLYReader()
reader.SetFileName(inname)


gf = vtkGraphicsFactory
gf.SetOffScreenOnlyMode(1)
gf.SetUseMesaClasses(1)
if_ = vtkImagingFactory
if_.SetUseMesaClasses(1)

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.SetSize(xsize, ysize)
renderWindow.SetOffScreenRendering(1)
renderWindow.AddRenderer(renderer)
renderer.AddActor(actor)
renderer.SetBackground(1, 1, 1)
renderWindow.Render()

wif = vtkWindowToImageFilter()
wif.SetInput(renderWindow)
wif.Update()

writer = vtkPNGWriter()
writer.SetFileName(outname)
writer.SetInput(wif.GetOutput())
writer.Write()

