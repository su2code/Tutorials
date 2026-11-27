# ParaView Programmable Filter script (Output Data Set Type: Same as Input or vtkPolyData), for 2D cases.
#
# Draws the metric of one sensor (point array AdaptiveMetric_<SENSOR> written by SU2) as an unfilled
# ellipse at every vertex. The ellipse axes are the eigenvectors of the metric, and its diameters are the
# requested cell sizes h = 1/sqrt(lambda) (SCALE = 0.5). With SCALE = 1, each ellipse is the unit ball of
# the metric (semi-axes h). The point arrays of the input are copied to the ellipses, so they can be
# colored by any field, e.g. Mach.
#
# If the filter fails with "module 'numpy' has no attribute 'in1d'" (ParaView builds that use NumPy 2.4 or
# later), run "import numpy; numpy.in1d = numpy.isin" in View -> Python Shell, then delete the filter and
# add it again.

import numpy as np
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import VTK_POLY_LINE, vtkCellArray
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

SENSOR = "Pressure"  # sensor name as written in the output, e.g. Pressure, Mach, Total_pressure
SCALE = 0.5          # 0.5: diameters equal to the requested sizes; 1: unit ball of the metric
NSEG = 64            # segments per ellipse

inp = inputs[0]
center = np.asarray(inp.Points)
metrics = [name[len("AdaptiveMetric_"):] for name in inp.PointData.keys() if name.startswith("AdaptiveMetric_")]
if SENSOR not in metrics:
    raise ValueError('No array AdaptiveMetric_{} in the input. Set SENSOR to one of: {}'.format(SENSOR, ", ".join(metrics) or "none (is the input flow.vtu?)"))
values = np.asarray(inp.PointData["AdaptiveMetric_" + SENSOR])
n = center.shape[0]

# In-plane part of the metric; XML (.vtu) files store xx, yy, zz, xy, yz, xz, legacy (.vtk) files all 9.
metric = np.empty((n, 2, 2))
if values.shape[1] == 6:
    metric[:, 0, 0], metric[:, 1, 1] = values[:, 0], values[:, 1]
    metric[:, 0, 1] = metric[:, 1, 0] = values[:, 3]
else:
    metric[:] = values.reshape(n, 3, 3)[:, :2, :2]

eigval, eigvec = np.linalg.eigh(metric)
h = 1.0 / np.sqrt(np.maximum(eigval, np.finfo(float).tiny))

# Ellipse points: center + SCALE * (h_1 cos(theta) v_1 + h_2 sin(theta) v_2).
theta = np.linspace(0.0, 2.0 * np.pi, NSEG, endpoint=False)
offset = SCALE * (np.cos(theta)[None, :, None] * (h[:, 0, None] * eigvec[:, :, 0])[:, None, :]
                  + np.sin(theta)[None, :, None] * (h[:, 1, None] * eigvec[:, :, 1])[:, None, :])
xyz = np.repeat(center[:, None, :], NSEG, axis=1)
xyz[:, :, :2] += offset
points = vtkPoints()
points.SetData(numpy_to_vtk(xyz.reshape(-1, 3).copy(), deep=True))

# One closed polyline per vertex.
first = np.arange(n) * NSEG
connectivity = (first[:, None] + np.r_[np.arange(NSEG), 0][None, :]).ravel()
offsets = np.arange(n + 1) * (NSEG + 1)
lines = vtkCellArray()
lines.SetData(numpy_to_vtkIdTypeArray(offsets.astype(np.int64), deep=True),
              numpy_to_vtkIdTypeArray(connectivity.astype(np.int64), deep=True))

grid = output.VTKObject
grid.SetPoints(points)
if hasattr(grid, "SetLines"):  # vtkPolyData output
    grid.SetLines(lines)
else:                          # unstructured grid output (Same as Input)
    grid.SetCells(VTK_POLY_LINE, lines)
for name in inp.PointData.keys():
    output.PointData.append(np.repeat(np.asarray(inp.PointData[name]), NSEG, axis=0), name)
