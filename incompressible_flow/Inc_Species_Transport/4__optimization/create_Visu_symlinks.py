# 06.12.2021 T. Kattmann
#
# Create symlinks for primal solution and FFD-Box of all desings in a separate folder.
# The links are renamed, such that the optimization progress can be visualized as a time series.
# Currently for PARAVIEW_MULTIBLOCK.

import os
import shutil

def make_dst_filename(i, front_string, trailing_string):
  if i<10:
    number= "00" + str(i)
  elif i<100:
    number= "0" + str(i)
  elif i<1000:
    number= str(i)
  else:
    raise ValueError("More than 1000 Designs.")

  return front_string + number + trailing_string

if __name__ == '__main__':
  # create folder to link files into
  dir= "visu_files"
  if os.path.exists(dir):
    shutil.rmtree(dir)
  os.makedirs(dir)

  # create list with folder names
  baseFolder = "./"
  sub_folders = [name for name in os.listdir(baseFolder) if os.path.isdir(os.path.join(baseFolder, name))]
  DSN_folders = [folder for folder in sub_folders if 'DSN' in folder]
  print(DSN_folders)

  # loop trough folders and symlink files
  for i,folder in enumerate(DSN_folders):
    # check if file exists
    sym_file= DSN_folders[i] + "/DIRECT/species3_primitiveVenturi/zone_0/Internal.vtu"
    sym_file2= DSN_folders[i] + "/DEFORM/ffd_boxes_def_0.vtk"
    if os.path.exists(sym_file):
      os.symlink("../" + sym_file, dir + make_dst_filename(i, "/visu_", ".vtu"))
      os.symlink("../" + sym_file2, dir + make_dst_filename(i, "/ffd_", ".vtk"))
