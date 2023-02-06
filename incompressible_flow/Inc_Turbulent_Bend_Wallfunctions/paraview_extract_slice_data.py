# trace generated using paraview version 5.11.0-RC2

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'XML MultiBlock Data Reader'
sudovtm = XMLMultiBlockDataReader(registrationName='sudo.vtm', FileName=['sudo.vtm'])
sudovtm.PointArrayStatus = ['Pressure', 'Velocity', 'Turb_Kin_Energy', 'Omega', 'Pressure_Coefficient', 'Density', 'Laminar_Viscosity', 'Skin_Friction_Coefficient', 'Heat_Flux', 'Y_Plus', 'Residual_Pressure', 'Residual_Velocity', 'Residual_TKE', 'Residual_Omega', 'Eddy_Viscosity']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# set active source
SetActiveSource(sudovtm)

# create a new 'Extract Block'
extractBlock1 = ExtractBlock(registrationName='ExtractBlock1', Input=sudovtm)
# Properties modified on extractBlock1
extractBlock1.Selectors = ['/Root/Zone0IncompFluid/Internal']

# create a new 'Slice'
slice1 = Slice(registrationName='Slice1', Input=extractBlock1)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]
# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [0.598, 0.026, -0.13]
# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice1.HyperTreeGridSlicer.Origin = [0.598, 0.026, -0.13]
# Properties modified on slice1.SliceType
slice1.SliceType.Normal = [0.0, 0.0, 1.0]
# show data in view
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

# update the view to ensure updated data information
renderView1.Update()

# save data
SaveData('inlet.csv', proxy=slice1, ChooseArraysToWrite=1,
    PointDataArrays=['Omega', 'Turb_Kin_Energy', 'Velocity'],
    UseScientificNotation=1)
