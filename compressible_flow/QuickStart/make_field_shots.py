#!/usr/bin/python3

## \file make_field_shots.py
#  \brief Paraview script for the visualizations in the QuickStart tutorial
#  \author F. Poli
#  \version 7.5.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2023, SU2 Contributors (cf. AUTHORS.md)
#
# SU2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# SU2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SU2. If not, see <http://www.gnu.org/licenses/>.

import paraview.simple as pvs

# load data file
flowdata = pvs.OpenDataFile('flow.vtu')

# create rendering view
renderview = pvs.GetActiveViewOrCreate('RenderView')
renderview.SetPropertyWithName('UseFXAA', 0)
pvs.SetActiveView(renderview)

# set 2D mode and camera
renderview.InteractionMode = '2D'
renderview.CameraFocalPoint = [0.4, 0.16, 0.0]
renderview.CameraParallelScale = 1.0

# set layout
layout = pvs.GetLayout()
layout.SetSize(820, 620)

# set quantity to be shown
flowdisplay = pvs.Show()
pvs.ColorBy(flowdisplay, ('POINTS', 'Pressure'))

# set range and color preset for quantity
pressurelut = pvs.GetColorTransferFunction('Pressure')
pressurelut.RescaleTransferFunction(50000.0, 155000.0)
pressurelut.NumberOfTableValues = 21
pressurelut.ApplyPreset('Jet', True)

# enable colorbar legend
flowdisplay.SetScalarBarVisibility(renderview, True)

# customize colorbar legend
pressurelutbar = pvs.GetScalarBar(pressurelut, renderview)
pressurelutbar.WindowLocation = 'Upper Right Corner'
pressurelutbar.Title = 'Pressure [Pa]'
pressurelutbar.AutomaticLabelFormat = 0
pressurelutbar.LabelFormat = '%-#.1f'
pressurelutbar.RangeLabelFormat = '%-#.1f'

# create contours
pressurecontour = pvs.Contour(registrationName='pContour', Input=flowdata)
pressurecontour.ContourBy = ['POINTS', 'Pressure']
pressurecontour.Isosurfaces = \
  [ 50e3,  55e3,  60e3,  65e3,  70e3,  75e3,  80e3,  85e3,  90e3,  95e3, 100e3,
   105e3, 110e3, 115e3, 120e3, 125e3, 130e3, 135e3, 140e3, 145e3, 150e3, 155e3]
pcontourdisplay = pvs.Show(pressurecontour, renderview,
                           'GeometryRepresentation')

# save screenshot
pvs.SaveScreenshot('NACA0012_pressure_field.png', renderview,
                   ImageResolution=[665, 500])

# hide what we no longer need
pvs.Hide(pressurecontour)
flowdisplay.SetScalarBarVisibility(renderview, False)

# set quantity to be shown
pvs.ColorBy(flowdisplay, ('POINTS', 'Mach'))

# set range and color preset for quantity
machlut = pvs.GetColorTransferFunction('Mach')
machlut.RescaleTransferFunction(0.0, 2.0)
machlut.NumberOfTableValues = 20
machlut.ApplyPreset('Blue Orange (divergent)', True)

# enable colorbar legend
flowdisplay.SetScalarBarVisibility(renderview, True)

# customize colorbar legend
machlutbar = pvs.GetScalarBar(machlut, renderview)
machlutbar.WindowLocation = 'Upper Right Corner'
machlutbar.Title = 'Mach number'
machlutbar.AutomaticLabelFormat = 0
machlutbar.LabelFormat = '%-#.1f'
machlutbar.RangeLabelFormat = '%-#.1f'

# create contours
machcontour = pvs.Contour(registrationName='mContour', Input=flowdata)
machcontour.ContourBy = ['POINTS', 'Mach']
machcontour.Isosurfaces = \
  [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0 ]
mcontourdisplay = pvs.Show(machcontour, renderview,
                           'GeometryRepresentation')

# save screenshot
pvs.SaveScreenshot('NACA0012_mach_field.png', renderview,
                   ImageResolution=[665, 500])

