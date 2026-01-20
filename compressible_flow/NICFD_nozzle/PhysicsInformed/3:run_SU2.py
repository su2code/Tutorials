#!/usr/bin/env python

## \file 3:run_SU2.py
#  \brief NICFD simulation of supersonic expansion of siloxane MM.
#  \version 8.1.0 "Harrier"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2024, SU2 Contributors (cf. AUTHORS.md)
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

import numpy as np
import gmsh 
import pysu2
import CoolProp.CoolProp as CP
from mpi4py import MPI
from su2dataminer.config import Config_NICFD


def WriteSU2Config(Config:Config_NICFD):
    """
    Write SU2 configuration options.
    """

    # Retrieve critical pressure and critical temperature from the fluid.
    fluid = CP.AbstractState(Config.GetEquationOfState(),Config.GetFluid())
    p_critical, T_critical = fluid.p_critical(), fluid.T_critical()

    p_t_in = p_critical / 1.0716  # Inlet total pressure.
    T_t_in = T_critical / 0.9919  # Inlet total temperature.
    p_ratio = 10                # Total-to-static pressure ratio.
    p_s_out = p_t_in / p_ratio  # Outlet static pressure.

    val_viscosity=1e-5  # Constant viscosity value.
    val_Prandtl=8.25e-1 # Laminar and turbulent Prandtl number.

    # Write ASCII file with MLP weights and biases.
    Config.WriteSU2MLP("MLP_siloxane_MM")

    # SU2 config options for NICFD nozzle simulation.
    su2_options = """ 
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %                                                                              %
    % SU2 configuration file, automatically generated with "3:run_SU2.py"          %
    % Case description: Non-ideal compressible fluid flow in a converging-         %
    %                   diverging supersonic nozzle using a PINN for thermodynamic %
    %                   state calculations.                                        %
    % Author: Evert Bunschoten                                                     %
    % Institution: Delft University of Technology                                  %
    % Date: 2025.3.26                                                              %
    % File Version  8.1.0 "Harrier"                                                %
    %                                                                              %
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%              
    SOLVER= RANS
    KIND_TURB_MODEL= SA
    SA_OPTIONS= NONE
    MATH_PROBLEM= DIRECT
    RESTART_SOL=NO
    MACH_NUMBER= 0.05
    AoA= 0.0

    FREESTREAM_PRESSURE= __Pt_INLET__

    FREESTREAM_TEMPERATURE= __Tt_INLET__

    FREESTREAM_TURBULENCEINTENSITY = 0.1

    FREESTREAM_TURB2LAMVISCRATIO = 100.0

    FREESTREAM_OPTION= TEMPERATURE_FS

    INIT_OPTION= TD_CONDITIONS

    REF_DIMENSIONALIZATION= DIMENSIONAL

    FLUID_MODEL= DATADRIVEN_FLUID
    USE_PINN=YES
    INTERPOLATION_METHOD = MLP
    FILENAMES_INTERPOLATOR = (__PINN_FILENAME__)

    VISCOSITY_MODEL= CONSTANT_VISCOSITY

    MU_CONSTANT= __VAL_MU__

    CONDUCTIVITY_MODEL= CONSTANT_PRANDTL 
    PRANDTL_LAM=__VAL_PRANDTL__
    TURBULENT_CONDUCTIVITY_MODEL=CONSTANT_PRANDTL_TURB
    PRANDTL_TURB=__VAL_PRANDTL__

    MARKER_HEATFLUX= (wall, 0.0)


    MARKER_EULER=(symmetry)

    MARKER_GILES= (inflow, TOTAL_CONDITIONS_PT, __Pt_INLET__, __Tt_INLET__, 1.0, 0.0, 0.0, 0.8, 0.8,\
                outflow, STATIC_PRESSURE,__Ps_OUTLET__, 0.0, 0.0, 0.0, 0.0, 0.8, 0.8)
    SPATIAL_FOURIER=NO
    TURBOMACHINERY_KIND= AXIAL
    TURBO_PERF_KIND=TURBINE
    RAMP_OUTLET=YES
    RAMP_OUTLET_COEFF= (__Pt_INLET__, 10, 200)
    AVERAGE_PROCESS_KIND= AREA
    MIXEDOUT_COEFF=(0.1, 1e-5, 15.0)
    MARKER_TURBOMACHINERY= (inflow, outflow)

    NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES
    CFL_NUMBER= 4
    CFL_ADAPT= YES
    CFL_ADAPT_PARAM= ( 0.99, 1.01, 1.0, 1000.0)

    LINEAR_SOLVER= FGMRES
    LINEAR_SOLVER_PREC= LU_SGS
    LINEAR_SOLVER_ERROR= 1E-5
    LINEAR_SOLVER_ITER= 10


    CONV_NUM_METHOD_FLOW= ROE
    MUSCL_FLOW= NO
    SLOPE_LIMITER_FLOW= VENKATAKRISHNAN
    VENKAT_LIMITER_COEFF=0.5

    TIME_DISCRE_FLOW= EULER_IMPLICIT
    CONV_NUM_METHOD_TURB= SCALAR_UPWIND
    MUSCL_TURB = NO
    SLOPE_LIMITER_TURB= VENKATAKRISHNAN
    TIME_DISCRE_TURB= EULER_IMPLICIT
    CFL_REDUCTION_TURB= 0.1

    ITER=10000

    CONV_RESIDUAL_MINVAL= -16
    CONV_STARTITER= 10
    CONV_CAUCHY_ELEMS= 100
    CONV_CAUCHY_EPS= 1E-6

    MESH_FILENAME= __MESH_FILENAME__

    OUTPUT_WRT_FREQ= 20
    OUTPUT_FILES=RESTART,PARAVIEW_MULTIBLOCK
    SCREEN_OUTPUT= (INNER_ITER, RMS_RES)
    HISTORY_OUTPUT= (INNER_ITER, WALL_TIME, RMS_RES, CFL_NUMBER)
    VOLUME_OUTPUT= (SOLUTION, PRIMITIVE, RESIDUAL, MPI)
    """

    # Set fluid specific quantities in config options.
    su2_options = su2_options.replace("__Pt_INLET__", "%.6e" % p_t_in)
    su2_options = su2_options.replace("__Tt_INLET__", "%.6e" % T_t_in)
    su2_options = su2_options.replace("__Ps_OUTLET__", "%.6e" % p_s_out)
    su2_options = su2_options.replace("__VAL_MU__", "%.1e" % val_viscosity)
    su2_options = su2_options.replace("__VAL_PRANDTL__", "%.2e" % val_Prandtl)
    su2_options = su2_options.replace("__PINN_FILENAME__", "MLP_siloxane_MM.mlp")
    return su2_options

def GenerateMesh():
    """
    Generate ORCHID nozzle mesh using gmsh
    """

    mesh_filename="nozzle_mesh.su2"
    t_bl = 5e-3             # Boundary layer refinement thickness.
    mesh_size_max = 2e-4    # Maximum cell size.

    # Load ORCHID nozzle curve geometry.
    curve_filename = "nozzle_curve.csv"
    X = np.loadtxt(curve_filename,delimiter=',',skiprows=1)
    x_wall, y_wall = X[:, 0], X[:, 1]
    order = x_wall.argsort()
    x_wall = x_wall[order]
    y_wall = y_wall[order]

    x_max, x_min = max(x_wall), min(x_wall)
    L = x_max - x_min 

    bl_offset = L * t_bl 
    Np_axial = int(L / mesh_size_max)

    # Initialize meshing procedure.
    gmsh.initialize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_max)
    gmsh.option.setNumber("Mesh.SaveAll", 0)
    gmsh.model.add("FLUID")
    factory = gmsh.model.geo

    mesher = gmsh.model.mesh
    wall_pts = []
    for x, y in zip(x_wall, y_wall):
        wall_pts.append(factory.addPoint(x,y,0))
    boundary_curve = factory.addSpline(wall_pts)

    bl_pts = []
    for x, y in zip(x_wall, y_wall):
        bl_pts.append(factory.addPoint(x,y-bl_offset,0))
    bl_curve = factory.addSpline(bl_pts)

    sym_pts = [factory.addPoint(x_min, 0, 0), factory.addPoint(x_max, 0, 0)]
    sym_line = factory.addLine(sym_pts[0], sym_pts[1])

    bl_inlet_crv = factory.addLine(bl_pts[0],wall_pts[0])
    bl_outlet_crv = factory.addLine(bl_pts[-1],wall_pts[-1])

    freeflow_inlet_crv = factory.addLine(sym_pts[0], bl_pts[0])
    freeflow_outlet_crv = factory.addLine(sym_pts[-1], bl_pts[-1])

    curvloop_freeflow = factory.addCurveLoop([sym_line, freeflow_outlet_crv, -bl_curve, -freeflow_inlet_crv])
    curvloop_bl = factory.addCurveLoop([bl_curve, bl_outlet_crv, -boundary_curve, -bl_inlet_crv])

    freeflow_plane = factory.addPlaneSurface([curvloop_freeflow])
    bl_plane = factory.addPlaneSurface([curvloop_bl])

    inlet_tag = factory.addPhysicalGroup(1, [freeflow_inlet_crv, bl_inlet_crv], name="inflow")
    outlet_tag = factory.addPhysicalGroup(1, [freeflow_outlet_crv, bl_outlet_crv], name="outflow")
    sym_tag = factory.addPhysicalGroup(1, [sym_line],name="symmetry")
    wall_tag = factory.addPhysicalGroup(1, [boundary_curve],name="wall")
    fluid_tag = factory.addPhysicalGroup(2, [freeflow_plane,bl_plane],name="fluid")
    factory.synchronize()

    mesher.setTransfiniteCurve(tag=bl_inlet_crv, numNodes=15, coef=0.8)
    mesher.setTransfiniteCurve(tag=bl_outlet_crv, numNodes=15, coef=0.8)
    mesher.setTransfiniteCurve(tag=boundary_curve, numNodes=Np_axial, coef=1.0)
    mesher.setTransfiniteCurve(tag=bl_curve, numNodes=Np_axial, coef=1.0)
    mesher.setTransfiniteCurve(tag=sym_line, numNodes=Np_axial, coef=1.0)

    mesher.setTransfiniteSurface(tag=bl_plane, cornerTags=[bl_pts[0],bl_pts[-1],wall_pts[-1],wall_pts[0]])
    mesher.setRecombine(dim=2,tag=bl_plane)
    gmsh.model.mesh.generate(2)
    gmsh.write(mesh_filename)
    gmsh.finalize()

    return mesh_filename

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    # Load SU2 DataMiner configuration.
    Config = Config_NICFD("SU2DataMiner_MM.cfg")

    # Write SU2 configuration options.
    su2_options = WriteSU2Config(Config)

    # Generate computational mesh.
    mesh_filename = GenerateMesh()
    su2_options = su2_options.replace("__MESH_FILENAME__", mesh_filename)

    # Write SU2 configuration file.
    with open("config_NICFD_PINN.cfg", "w") as fid:
        fid.write(su2_options)
comm.Barrier()

# Initialize NICFD simulation.
driver = pysu2.CSinglezoneDriver("config_NICFD_PINN.cfg",1, comm)
driver.StartSolver()
driver.Finalize()