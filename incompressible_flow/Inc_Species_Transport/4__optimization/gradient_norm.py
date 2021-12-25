# 06.12.2021 T. Kattmann
#
# Compute gradient norm for each design iteration and saves the gradient norm into a csv file.

import numpy as np
import os
import pandas as pd

if __name__ == '__main__':
  # Create list with folder names
  baseFolder = "./"
  sub_folders = [name for name in os.listdir(baseFolder) if os.path.isdir(os.path.join(baseFolder, name))]
  DSN_folders = [folder for folder in sub_folders if 'DSN' in folder]

  # Initialize array of gradient Norms
  gradientNormVector = np.zeros(len(DSN_folders))

  # loop through all Design folder
  for i,folder in enumerate(DSN_folders):
    # check if gradient file exists
    gradFilename = baseFolder + folder + "/DOT/of_grad.csv"
    if os.path.exists(gradFilename):
      # Read the gradient file and store gradient norm
      df = pd.read_csv(gradFilename)
      gradient = df.values
      gradientNormVector[i] = np.linalg.norm(gradient)
    else:
      # Write a NaN as in Paraview these values are omitted
      gradientNormVector[i] = np.nan

  print(gradientNormVector)
  df = pd.DataFrame({"ITER" : range(len(DSN_folders)), "Gradient Norm" : gradientNormVector})
  df.to_csv("gradient_norm.csv", index=False)
