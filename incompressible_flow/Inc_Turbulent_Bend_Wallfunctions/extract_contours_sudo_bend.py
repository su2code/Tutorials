# extract contour plots from the 90 degree bend from Sudo et al. 
# check below the different places to modify the details of the contour

# trace generated using paraview version 5.11.0-RC2

# diameter
D = 0.104
# radius of curvature
R = 0.208
#

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
import numpy as np
import math

# create a new 'XML MultiBlock Data Reader'
sudovtm = XMLMultiBlockDataReader(registrationName='sudo.vtm', FileName=['sudo.vtm'])
sudovtm.PointArrayStatus = ['Pressure', 'Velocity', 'Turb_Kin_Energy', 'Omega', 'Pressure_Coefficient', 'Density', 'Laminar_Viscosity', 'Skin_Friction_Coefficient', 'Heat_Flux', 'Y_Plus', 'Residual_Pressure', 'Residual_Velocity', 'Residual_TKE', 'Residual_Omega', 'Eddy_Viscosity']

# set active source
SetActiveSource(sudovtm)

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# create a new 'Slice'
slice1 = Slice(registrationName='Slice1', Input=sudovtm)
slice1.SliceType = 'Plane'


################################################################################
# ### 1/5 change the location of the slice plane ### #
################################################################################
# CASE 1
# Z/D = -1.0
#slice1.SliceType.Origin = [0.0, 0.0, -0.104]
#slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# CASE 2
# Z/D = 0.0 (phi=0.0)
slice1.SliceType.Origin = [0.208, 0.0, 0.0]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# CASE 3
# phi=30.0
#ALPHA=30.0
#slice1.SliceType.Origin = [0.208, 0.0, 0.0]
#slice1.SliceType.Normal = [np.sin(math.radians(ALPHA)), 0.0, np.cos(math.radians(ALPHA))]

# CASE 4
# phi=60.0
#ALPHA=60
#slice1.SliceType.Origin = [0.208, 0.0, 0.0]
#slice1.SliceType.Normal = [np.sin(math.radians(ALPHA)), 0.0, np.cos(math.radians(ALPHA))]

# CASE 5
# phi = 90.0
#slice1.SliceType.Origin = [0.208, 0.0, 0.0]
#slice1.SliceType.Normal = [1.0, 0.0, 0.0]

# CASE 6
# Z/D = +1.0
#slice1.SliceType.Origin = [0.312, 0.0, 0.0]
#slice1.SliceType.Normal = [1.0, 0.0, 0.0]
################################################################################
################################################################################

# create a new 'Calculator'
calculator1 = Calculator(registrationName='Calculator1', Input=slice1)

# Properties modified on calculator1
################################################################################
# ### 2/5 compute the normalized velocity in the plane ### #
################################################################################
# CASE 1
# Z/D = -1.0
#calculator1.Function = 'Velocity_Z/8.7'

# CASE 2
# Z/D = 0.0 (phi=0)
calculator1.Function = 'Velocity_Z/8.7'

# CASE 3
# phi=30
#calculator1.Function = '(0.5*Velocity_X+0.5*sqrt(3)*Velocity_Z)/(8.7)'

# CASE 4
# phi=60
#calculator1.Function = '(0.5*sqrt(3)*Velocity_X+0.5*Velocity_Z)/(8.7)'

# CASE 5
# phi=90
#calculator1.Function = 'Velocity_X/8.7'

# CASE 6
# Z/D = 1.0
#calculator1.Function = 'Velocity_X/8.7'
################################################################################
################################################################################

# show data in view
calculator1Display = Show(calculator1, renderView1, 'GeometryRepresentation')
# hide color bar/color legend
calculator1Display.SetScalarBarVisibility(renderView1, False)

# get color transfer function/color map for 'Result'
resultLUT = GetColorTransferFunction('Result')
# Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
resultLUT.ApplyPreset('Black-Body Radiation', True)
# Properties modified on resultLUT
resultLUT.NumberOfTableValues = 32

# create a new 'Contour'
contour1 = Contour(registrationName='Contour1', Input=calculator1)
contour1.ContourBy = ['POINTS', 'Result']
# Properties modified on contour1
################################################################################
# ### 3/5 set the specific isocontour lines for the plane ### #
################################################################################

# CASE 1
# Z/D = -1.0
#contour1.Isosurfaces = [0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]

# CASE 2
# Z/D = 0.0
contour1.Isosurfaces = [0.85, 0.9, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]

#CASE 3
# phi = 30.0
#contour1.Isosurfaces = [0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]

# CASE 4
# phi = 60.0
#contour1.Isosurfaces = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]

# CASE 5
# phi = 90.0
#contour1.Isosurfaces = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05]

# CASE 6
# Z/D = +1.0
#contour1.Isosurfaces = [0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15]
################################################################################


# show data in view
contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')
# turn off scalar coloring
ColorBy(contour1Display, None)
# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(resultLUT, renderView1)
# change solid color to black
contour1Display.DiffuseColor = [0.0, 0.0, 0.0]
# increase the line thickness
contour1Display.LineWidth = 2.0

# create a new 'Extract Block'
extractBlock1 = ExtractBlock(registrationName='ExtractBlock1', Input=calculator1)
# Properties modified on extractBlock1
extractBlock1.Selectors = ['/Root/Zone0IncompFluid/Boundary/wall_1', '/Root/Zone0IncompFluid/Boundary/wall_2', '/Root/Zone0IncompFluid/Boundary/wall_bend']
# show data in view
extractBlock1Display = Show(extractBlock1, renderView1, 'GeometryRepresentation')
# change solid color
extractBlock1Display.DiffuseColor = [0.0, 0.0, 0.0]

# Hide orientation axes
renderView1.OrientationAxesVisibility = 0

# reset view to fit data
renderView1.ResetCamera(False)

# get layout
layout1 = GetLayout()

# layout/tab size in pixels
layout1.SetSize(1304, 746)

################################################################################
# 4/5 current camera placement for renderView1, view is distance L before the plane
################################################################################

L = 0.115

# CASE 1
# view for Z/D=-1
#renderView1.CameraFocalPoint = [0.0, 0.026, -0.104]
#renderView1.CameraPosition =   [0.0, 0.026, -0.104-L]

# CASE 2
# view for Z/D=0
renderView1.CameraFocalPoint = [0.0, 0.026,  0.000]
renderView1.CameraPosition =   [0.0, 0.026, -0.000-L]

# CASE 3
# view for phi=30
#ALPHA=30
#X = R - R * np.cos(math.radians(ALPHA))
#Z = R * np.sin(math.radians(ALPHA))
#renderView1.CameraFocalPoint = [X, 0.026,  Z]
#Xp = X - L*np.sin(math.radians(ALPHA))
#Zp = Z - L*np.cos(math.radians(ALPHA))
#renderView1.CameraPosition =   [Xp, 0.026, Zp]

# CASE 4
# view for phi=60
#ALPHA=60
#X = R - R * np.cos(math.radians(ALPHA))
#Z = R * np.sin(math.radians(ALPHA))
#renderView1.CameraFocalPoint = [X, 0.026,  Z]
#Xp = X - L*np.sin(math.radians(ALPHA))
#Zp = Z - L*np.cos(math.radians(ALPHA))
#renderView1.CameraPosition =   [Xp, 0.026, Zp]

# CASE 5
# view for phi=90
#renderView1.CameraFocalPoint = [0.208, 0.026, 0.208]
#renderView1.CameraPosition = [0.208-L, 0.026, 0.208]

# CASE 6
# view for Z/D = +1
#renderView1.CameraFocalPoint = [0.312, 0.026, 0.208]
#renderView1.CameraPosition = [0.312-L, 0.026, 0.208]

#
renderView1.CameraViewUp = [0.0, 1.0, 0.0]
renderView1.CameraParallelScale = 0.058
################################################################################

# update the view to ensure updated data information
renderView1.Update()

# 5/5 save screenshot
# CASE 1
#SaveScreenshot('./slice_ZD_minus_1.png', renderView1, ImageResolution=[1304, 746])
# CASE 2
SaveScreenshot('./slice_ZD_0.png', renderView1, ImageResolution=[1304, 746])
# CASE 3
#SaveScreenshot('./slice_phi_30.png', renderView1, ImageResolution=[1304, 746])
# CASE 4
#SaveScreenshot('./slice_phi_60.png', renderView1, ImageResolution=[1304, 746])
# CASE 5
#SaveScreenshot('./slice_phi_90.png', renderView1, ImageResolution=[1304, 746])
# CASE 1
#SaveScreenshot('./slice_ZD_plus_1.png', renderView1, ImageResolution=[1304, 746])

