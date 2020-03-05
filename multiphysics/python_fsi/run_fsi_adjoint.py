#!/usr/bin/env python

# \file run_fsi_primal.py
# \brief Python script to run FSI cases using SU2 native flow and FEA solvers
# \author Ruben Sanchez
# \version 7.0.2 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation 
# (http://su2foundation.org)
#
# Copyright 2012-2020, SU2 Contributors (cf. AUTHORS.md)
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

import sys
import shutil
import pysu2ad as pysu2          # imports the SU2 adjoint-wrapped module
from mpi4py import MPI

def main():

  # Define the input file names
  flow_filename = "config_channel_ad.cfg"
  fea_filename = "config_cantilever_ad.cfg"
  
  # Import communicators to run with parallel version of SU2
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()

  # Initialize the flow driver of SU2, this includes solver preprocessing
  FlowDriver = pysu2.CDiscAdjSinglezoneDriver(flow_filename, 1, comm);
  FlowMarkerID = None
  FlowMarkerName = 'flowbound'                                        # FSI marker (flow side)
  FlowMarkerList = FlowDriver.GetAllBoundaryMarkersTag()              # Get all the flow boundary tags
  FlowMarkerIDs = FlowDriver.GetAllBoundaryMarkers()                  # Get all the associated indices to the flow markers
  if FlowMarkerName in FlowMarkerList and FlowMarkerName in FlowMarkerIDs.keys():
    FlowMarkerID = FlowMarkerIDs[FlowMarkerName]                      # Check if the flow FSI marker exists
  nVertex_Marker_Flow = FlowDriver.GetNumberVertices(FlowMarkerID)    # Get the number of vertices of the flow FSI marker
    
  # Initialize the corresponding driver of SU2, this includes solver preprocessing
  FEADriver = pysu2.CDiscAdjSinglezoneDriver(fea_filename, 1, comm);
  FEAMarkerID = None
  FEAMarkerName = 'feabound'                                          # FSI marker (FEA side)
  FEAMarkerList = FEADriver.GetAllBoundaryMarkersTag()                # Get all the FEA boundary tags
  feaMarkerIDs = FEADriver.GetAllBoundaryMarkers()                    # Get all the associated indices to the FEA markers
  if FEAMarkerName in FEAMarkerList and FEAMarkerName in feaMarkerIDs.keys():
    FEAMarkerID = feaMarkerIDs[FEAMarkerName]                         # Check if the FEA FSI marker exists
  nVertex_Marker_FEA = FEADriver.GetNumberVertices(FEAMarkerID)       # Get the number of vertices of the FEA FSI marker

  print("\n------------------------------ Begin Solver -----------------------------\n")
  sys.stdout.flush()

  comm.Barrier()
    
  # Initialize the flow source term
  fea_sens=[]
  for iVertex in range(nVertex_Marker_Flow):
    fea_sens.append([0.0, 0.0, 0.0])
    
  for i in range(15):

    # Set the source term from the flow sensitivities into the structural adjoint
    FlowDriver.SetFlowLoad_Adjoint(FlowMarkerID,0,fea_sens[1][0],fea_sens[1][1],0)
    FlowDriver.SetFlowLoad_Adjoint(FlowMarkerID,1,fea_sens[0][0],fea_sens[0][1],0)
    for j in range(2, nVertex_Marker_Flow):
      FlowDriver.SetFlowLoad_Adjoint(FlowMarkerID,j,fea_sens[j][0],fea_sens[j][1],0)
  
    # Time iteration preprocessing
    FlowDriver.ResetConvergence()
    FlowDriver.Preprocess(0)
    FlowDriver.Run()
    FlowDriver.Postprocess() 
    FlowDriver.Update()
    stopCalc = FlowDriver.Monitor(0)
    
    # Recover the flow loads
    flow_loads=[]
    for j in range(nVertex_Marker_Flow):
      vertexLoad = FlowDriver.GetFlowLoad(FlowMarkerID,j)
      flow_loads.append(vertexLoad)
    
    # Set the FEA loads to run the primal simulation for the recording
    FEADriver.SetFEA_Loads(FEAMarkerID,0,flow_loads[1][0],flow_loads[1][1],0)
    FEADriver.SetFEA_Loads(FEAMarkerID,1,flow_loads[0][0],flow_loads[0][1],0)
    for j in range(2, nVertex_Marker_FEA):
      FEADriver.SetFEA_Loads(FEAMarkerID,j,flow_loads[j][0],flow_loads[j][1],0)
    
    # Recover the flow sensitivities
    flow_sens=[]
    for j in range(nVertex_Marker_Flow):
      sensX, sensY, sensZ = FlowDriver.GetMeshDisp_Sensitivity(FlowMarkerID,j)
      flow_sens.append([sensX, sensY, sensZ])
      
    # Set the source term from the flow sensitivities into the structural adjoint
    FEADriver.SetSourceTerm_DispAdjoint(FEAMarkerID,0,flow_sens[1][0],flow_sens[1][1],0)
    FEADriver.SetSourceTerm_DispAdjoint(FEAMarkerID,1,flow_sens[0][0],flow_sens[0][1],0)
    for j in range(nVertex_Marker_FEA):
      FEADriver.SetSourceTerm_DispAdjoint(FEAMarkerID,j,flow_sens[j][0],flow_sens[j][1],0)
    
    FEADriver.ResetConvergence()
    FEADriver.Preprocess(0)  
    FEADriver.Run()
    FEADriver.Postprocess() 
    FEADriver.Update()
    stopCalc = FEADriver.Monitor(0)
    
    # Sensitivities of the marker
    fea_sens=[]
    for iVertex in range(nVertex_Marker_FEA):
      sensX, sensY, sensZ = FEADriver.GetFlowLoad_Sensitivity(FEAMarkerID, iVertex)
      fea_sens.append([sensX, sensY, sensZ])
  
  # Output the solution to file
  FlowDriver.Output(0)
  FEADriver.Output(0)  

# -------------------------------------------------------------------
#  Run Main Program
# -------------------------------------------------------------------

# this is only accessed if running from command prompt
if __name__ == '__main__':
    main()  
