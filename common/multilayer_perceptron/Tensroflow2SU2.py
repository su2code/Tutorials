#!/usr/bin/env python

## \file Tensroflow2SU2.py
#  \brief Example of converting a trained Tensorflow MLP to SU2 .mlp
#         format.
#  \author E.C.Bunschoten
#  \version 7.5.0 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2022, SU2 Contributors (cf. AUTHORS.md)
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

import tensorflow as tf 
from write_SU2_MLP import *

# Input names for the SU2 MLP. For the CDataDrivenFluid class, these have to be "Density" and "Energy"
MLP_input_names = ["Density", "Energy"]
# The order of the input names should correspond to that of the trained model inputs.

# Optional: give minimum and maximum input normalization values. These are required in case the MLP
# was trained on normalized input data.
input_min = [2.81038e-1, 1.79956e5]
input_max = [2.72979e+01, 4.48318e+05]

# Output names for the SU2 MLP. For the CDataDrivenFluid class, these have to include the following:
MLP_output_names = ["s",        # Entropy
                    "dsde_rho", # First entropy derivative w.r.t static energy
                    "dsdrho_e", # First entropy derivative w.r.t density
                    "d2sde2",   # Second entropy derivative w.r.t static energy
                    "d2sdedrho",# Second entropy derivative w.r.t static energy and density
                    "d2sdrho2"] # Second entropy derivative w.r.t density
# The order of the output names should correspond to that of the trained model outputs.

# Optional: give minimum and maximum output normalization values. These are required in case the MLP
# was trained on normalized training data.
output_min = [ 5.74729e+03,  1.66861e-03, -1.05632e+03, -2.15459e-08,
       -4.20494e-06,  3.96917e-01]

output_max = [ 7.77852e+03,  4.00000e-03, -1.07148e+01, -3.57370e-09,
       -4.93767e-07,  3.75786e+03]

# Saved Tensorflow model file name, saved with the "model.save" function after training.
Tensorflow_model_file = "MLP_Air"

# SU2 MLP output file name (wo extension)
SU2_MLP_output_file = "MLP_Air_SU2"

# Load the MLP trained through Tensorflow
Tensorflow_model = tf.keras.models.load_model(Tensorflow_model_file)

# Write SU2 MLP input file
write_SU2_MLP(SU2_MLP_output_file, MLP_input_names, MLP_output_names, Tensorflow_model, input_min, input_max, output_min, output_max)

