#!/usr/bin/env python

## \file run.py
#  \brief simulation of smoke plume over amsterdam 
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

import sys
import pysu2
import numpy as np

# with mpi:
# $ mpirun -n 4 python run.py
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# without mpi:
# $ python run.py
#  rank = 0
#  comm = 0

# ################################################################## #
# Source term for smoke/fire
# ################################################################## #
def smoke(SU2Driver, iPoint, nDim):

    allCoords = SU2Driver.Coordinates()
    coord = allCoords.Get(iPoint)
    x = coord[0]
    y = coord[1]
    R = np.sqrt(x*x + y*y)
    # source size: 10 meter diameter source term located at center (0,0)
    if (R < 5.0):
      # source is kg/m^3.s
      Sc = 0.1
    else:
      Sc = 0.0
    return Sc

# ################################################################## #
# Main routine
# ################################################################## #
def main():

  # Initialize the primal driver of SU2, this includes solver preprocessing.
  try:
    driver = pysu2.CSinglezoneDriver('amsterdam.cfg', 1, comm)
  except TypeError as exception:
    print('A TypeError occured in pysu2.CSinglezoneDriver : ', exception)
    raise

  if rank == 0:
    print("\n------------------------------ Begin Solver -----------------------------")
    sys.stdout.flush()

  nDim = driver.GetNumberDimensions()

  # index to the flow solver
  # C.FLOW
  # INC.FLOW
  # HEAT
  # FLAMELET
  # SPECIES
  # SA
  # SST
  iFLOWSOLVER = driver.GetSolverIndices()['INC.FLOW']
  iSPECIESSOLVER = driver.GetSolverIndices()['SPECIES']
  # all the indices and the map to the names of the primitives
  nElem = driver.GetNumberElements()
  nVars = driver.Solution(iFLOWSOLVER).Shape()[1]
  nVarsSpecies = driver.Solution(iSPECIESSOLVER).Shape()[1]

  # run N iterations
  N = 1000
  for inner_iter in range(N):
    if (rank==0):
      print("python iteration ", inner_iter)

    Source = driver.UserDefinedSource(iSPECIESSOLVER)

    # set the source term, per point
    for i_node in range(driver.GetNumberNodes() - driver.GetNumberHaloNodes()):
      # add source term:
      # default source 
      S = smoke(driver,i_node, nDim)
      Source.Set(i_node,0,S)

    driver.Preprocess(inner_iter)
    driver.Run()

    driver.Postprocess()
    driver.Update()
    # Monitor the solver and output solution to file if required.
    #driver.Monitor(inner_iter)
    # Output the solution to file
    driver.Output(inner_iter)

  # Finalize the solver and exit cleanly.
  driver.Finalize()

if __name__ == '__main__':
  main()
