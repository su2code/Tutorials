# trace generated using paraview version 5.11.0-RC2

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'XML MultiBlock Data Reader'
sudovtm = XMLMultiBlockDataReader(registrationName='sudo.vtm', FileName=['/home/nijso/simulations/sudo_90degree/verycoarse_tutorial/sudo.vtm'])
sudovtm.PointArrayStatus = ['Pressure', 'Velocity', 'Turb_Kin_Energy', 'Omega', 'Pressure_Coefficient', 'Density', 'Laminar_Viscosity', 'Skin_Friction_Coefficient', 'Heat_Flux', 'Y_Plus', 'Residual_Pressure', 'Residual_Velocity', 'Residual_TKE', 'Residual_Omega', 'Eddy_Viscosity']

# create a new 'Plot Over Line'
plotOverLine1 = PlotOverLine(registrationName='PlotOverLine1', Input=sudovtm)
plotOverLine1.Resolution = 500
plotOverLine1.Point1 = [0.208, 0.0, 0.156]
plotOverLine1.Point2 = [0.208, 0.0, 0.26]

# save data
SaveData('/home/nijso/simulations/sudo_90degree/verycoarse_tutorial/plotline.csv', proxy=plotOverLine1, ChooseArraysToWrite=1,
    PointDataArrays=['Density', 'Eddy_Viscosity', 'Heat_Flux', 'Laminar_Viscosity', 'Omega', 'Pressure', 'Pressure_Coefficient', 'Residual_Omega', 'Residual_Pressure', 'Residual_TKE', 'Residual_Velocity', 'Skin_Friction_Coefficient', 'Turb_Kin_Energy', 'Velocity', 'Y_Plus', 'arc_length', 'vtkValidPointMask'],
    CellDataArrays=['Density', 'Eddy_Viscosity', 'Heat_Flux', 'Laminar_Viscosity', 'Omega', 'Pressure', 'Pressure_Coefficient', 'Residual_Omega', 'Residual_Pressure', 'Residual_TKE', 'Residual_Velocity', 'Skin_Friction_Coefficient', 'Turb_Kin_Energy', 'Velocity', 'Y_Plus', 'arc_length', 'vtkValidPointMask'])
