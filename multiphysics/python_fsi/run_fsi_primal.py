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
import pysu2
from mpi4py import MPI

def main():
  
  # Define the input file names
  flow_filename = "config_channel.cfg"
  fea_filename = "config_cantilever.cfg"
  
  # Import communicators to run with parallel version of SU2
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()

  # Initialize the flow driver of SU2, this includes solver preprocessing
  FlowDriver = pysu2.CSinglezoneDriver(flow_filename, 1, comm);
  FlowMarkerID = None
  FlowMarkerName = 'flowbound'                                        # FSI marker (flow side)
  FlowMarkerList = FlowDriver.GetAllBoundaryMarkersTag()              # Get all the flow boundary tags
  FlowMarkerIDs = FlowDriver.GetAllBoundaryMarkers()                  # Get all the associated indices to the flow markers
  if FlowMarkerName in FlowMarkerList and FlowMarkerName in FlowMarkerIDs.keys():
    FlowMarkerID = FlowMarkerIDs[FlowMarkerName]                      # Check if the flow FSI marker exists
  nVertex_Marker_Flow = FlowDriver.GetNumberVertices(FlowMarkerID)    # Get the number of vertices of the flow FSI marker
    
  # Initialize the corresponding driver of SU2, this includes solver preprocessing
  FEADriver = pysu2.CSinglezoneDriver(fea_filename, 1, comm);
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
        
  # We limit the loop to the number of iterations to convergence required by the SU2 native FSI tutorial
  for i in range(17):   
  
    # Flow solution
    FlowDriver.ResetConvergence()
    FlowDriver.Preprocess(0)
    FlowDriver.Run()
    FlowDriver.Postprocess() 
    stopCalc = FlowDriver.Monitor(0)
    
    # Recover the flow loads
    flow_loads=[]
    for j in range(nVertex_Marker_Flow):
      vertexLoad = FlowDriver.GetFlowLoad(FlowMarkerID, j)
      flow_loads.append(vertexLoad)

    # Set the flow loads to the FEA nodes (vertex IDs are matching by construction except for vertex 0 and 1)
    # To check the positions of the flow vertices use FlowDriver.GetVertexCoordX(FlowMarkerID, iVertex), FlowDriver.GetVertexCoordY(FlowMarkerID, iVertex), 
    # To check the positions of the structural vertices use FEADriver.GetVertexCoordX(FEAMarkerID, iVertex), FEADriver.GetVertexCoordY(FEAMarkerID, iVertex)
    FEADriver.SetFEA_Loads(FEAMarkerID,0,flow_loads[1][0],flow_loads[1][1],0)
    FEADriver.SetFEA_Loads(FEAMarkerID,1,flow_loads[0][0],flow_loads[0][1],0)
    for j in range(2, nVertex_Marker_FEA):
      FEADriver.SetFEA_Loads(FEAMarkerID,j,flow_loads[j][0],flow_loads[j][1],0)
      
    # FEA solution
    FEADriver.ResetConvergence()
    FEADriver.Preprocess(0)  
    FEADriver.Run()
    FEADriver.Postprocess() 
    stopCalc = FEADriver.Monitor(0)
    
    # Recover the structural displacements
    fea_disp=[]
    for j in range(nVertex_Marker_FEA):
      vertexDisp = FEADriver.GetFEA_Displacements(FEAMarkerID,j)
      fea_disp.append(vertexDisp)
      
    # Set the structural displacements to the flow nodes (vertex IDs are matching by construction except for vertex 0 and 1)
    FlowDriver.SetMeshDisplacement(FlowMarkerID,0,fea_disp[1][0],fea_disp[1][1],0)
    FlowDriver.SetMeshDisplacement(FlowMarkerID,1,fea_disp[0][0],fea_disp[0][1],0)
    for j in range(2, nVertex_Marker_FEA):
      FlowDriver.SetMeshDisplacement(FlowMarkerID,j,fea_disp[j][0],fea_disp[j][1],0)
    
  # Print out the flow and FEA solutions
  FlowDriver.Output(0)
  FEADriver.Output(0)

if __name__ == '__main__':
    main()  
