# Compute and print absolute difference between Discrete Adjoint
# and Finite Difference gradient. Prints also percentage difference.
#
# Run this script after `python gradient_validation.py` successfully finished

import pandas as pd
import math

def printGradVal(FDgrad, DAgrad):
  """
  Print Gradient Comparison to screen between DA and FD.

  Input:
  FDgrad: array with the Finite Difference gradient
  DAgrad: array with the Discrete Adjoint gradient
  """
  # Check that both arrays have the same length and deduce a size parameter
  assert(DAgrad.size == FDgrad.size)

  # absolute difference
  absoluteDiff = DAgrad - FDgrad
  # relative difference in percent
  relDiffPercent = (DAgrad - FDgrad)/abs(DAgrad) * 100
  # sign change
  sign = lambda x : math.copysign(1, x)
  signChange = [sign(DA) != sign(FD) for DA,FD in zip(DAgrad,FDgrad)]

  print('+-----------+-------------------+-------------------+-------------------+-------------------+-------------+')
  print('| DV number |       DA gradient |       FD gradient |     absolute diff | relative diff [%] | sign change |')
  print('+-----------+-------------------+-------------------+-------------------+-------------------+-------------+')

  for iDV in range(0, DAgrad.size, 1):
      print('|{0:10d} |{1:18.10f} |{2:18.10f} |{3:18.10f} |{4:18.10f} |{5:12} |'.format(iDV, DAgrad[iDV], FDgrad[iDV], absoluteDiff[iDV], relDiffPercent[iDV], signChange[iDV]))

  print('+-----------+-------------------+-------------------+-------------------+-------------------+-------------+')
# printGradVal

if __name__ == "__main__":

  # FDStep has to match with the value in the gradient_validation script
  FDstep = 1e-8

  # Load Discrete Adjont gradient
  DAvals_specVar = pd.read_csv("DOE/DOT/of_grad.csv")

  DAstring_specVar = 'SURFACE_SPECIES_VARIANCE gradient '

  DAgrad_specVar = DAvals_specVar[DAstring_specVar].values
  nDV = DAgrad_specVar.size

  # Load primal values and create FD gradient
  FDvals = pd.read_csv("doe.csv")

  FDstring_specVar = '  specVar'

  # Note that the FDvals have the baseline value written in its last position
  FDgrad_specVar = (FDvals[FDstring_specVar].values[:nDV] - FDvals[FDstring_specVar].values[nDV]) / FDstep

  # Legend
  print("absolute diff = DAgrad - FDgrad")
  print("relative diff = (DAgrad - FDgrad) / abs(DAgrad) * 100")

  print(DAstring_specVar)
  printGradVal(FDgrad_specVar, DAgrad_specVar)
