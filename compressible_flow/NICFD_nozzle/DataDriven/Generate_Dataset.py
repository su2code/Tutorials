#!/usr/bin/env python

## \file Generate_Dataset.py
#  \brief Example python script for generating training data for 
#   data-driven fluid model in SU2
#  \author E.C.Bunschoten
#  \version 7.5.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2023, SU2 Contributors (cf. AUTHORS.md)
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

# make print(*args) function available in PY2.6+, does'nt work on PY < 2.6

import CoolProp
import numpy as np 
from tqdm import tqdm
import csv 

# Name of the fluid in the CoolProp library.
fluidName = 'Air'

# Type of equation of state to be used by CoolProp.
CP_eos = "HEOS"

# Minimum and maximum dataset temperatures [K].
T_min = 280
T_max = 1000

# Minimum and maximum dataset pressures [Pa].
P_min = 5e4
P_max = 2e6

# Number of data points along each axis.
Np_grid = 500

# Fraction of data points to be used as training data for MLP training (0-1).
f_train = 0.8

# Fraction of data poins to be used as test data for MLP validation (0-1).
f_test = 0.1


# Prepare data grid
T_range = np.linspace(T_min, T_max, Np_grid)
P_range = np.linspace(P_min, P_max, Np_grid)

T_grid, P_grid = np.meshgrid(T_range, P_range)

T_dataset = T_grid.flatten()
P_dataset = P_grid.flatten()

density_dataset = np.zeros(np.shape(T_dataset))
energy_dataset = np.zeros(np.shape(T_dataset))
s_dataset = np.zeros(np.shape(T_dataset))
dsde_dataset = np.zeros(np.shape(T_dataset))
dsdrho_dataset = np.zeros(np.shape(T_dataset))
d2sde2_dataset = np.zeros(np.shape(T_dataset))
d2sdedrho_dataset = np.zeros(np.shape(T_dataset))
d2sdrho2_dataset = np.zeros(np.shape(T_dataset))

# Evaluate CoolProp on data grid.
fluid = CoolProp.AbstractState(CP_eos, fluidName)
idx_failed_below = []
idx_failed_above = []
print("Generating CoolProp data set...")
for i in tqdm(range(len(T_dataset))):
    try:
        fluid.update(CoolProp.PT_INPUTS, P_dataset[i], T_dataset[i])

        density_dataset[i] = fluid.rhomass()
        energy_dataset[i] = fluid.umass()
        s_dataset[i] = fluid.smass()
        dsde_dataset[i] = fluid.first_partial_deriv(CoolProp.iSmass, CoolProp.iUmass, CoolProp.iDmass)
        dsdrho_dataset[i] = fluid.first_partial_deriv(CoolProp.iSmass, CoolProp.iDmass, CoolProp.iUmass)
        d2sde2_dataset[i] = fluid.second_partial_deriv(CoolProp.iSmass, CoolProp.iUmass, CoolProp.iDmass, CoolProp.iUmass, CoolProp.iDmass)
        d2sdedrho_dataset[i] = fluid.second_partial_deriv(CoolProp.iSmass, CoolProp.iUmass, CoolProp.iDmass, CoolProp.iDmass, CoolProp.iUmass)
        d2sdrho2_dataset[i] = fluid.second_partial_deriv(CoolProp.iSmass, CoolProp.iDmass, CoolProp.iUmass, CoolProp.iDmass, CoolProp.iUmass)
    except:
        idx_failed_below.append(i)
        print("CoolProp failed at temperature "+str(T_dataset[i]) + ", pressure "+str(P_dataset[i]))
print("Done!")

# Collect all data arrays and fill in failed data points. 
collected_data = np.vstack([density_dataset, 
                                  energy_dataset, 
                                  s_dataset, 
                                  dsde_dataset, 
                                  dsdrho_dataset, 
                                  d2sde2_dataset, 
                                  d2sdedrho_dataset, 
                                  d2sdrho2_dataset]).T
for i_failed in idx_failed_below:
    collected_data[i_failed, :] = 0.5*(collected_data[i_failed+1, :] + collected_data[i_failed-1, :])

# Shuffle data set and extract training, validation, and test data.
np.random.shuffle(collected_data)
np_train = int(f_train*len(density_dataset))
np_val = int(f_test*len(density_dataset))
np_test = len(density_dataset) - np_train - np_val

train_data = collected_data[:np_train, :]
dev_data = collected_data[np_train:(np_train+np_val), :]
test_data = collected_data[(np_train+np_val):, :]

# Write output files.
with open(fluidName + "_dataset_full.csv", "w+") as fid:
    fid.write("Density,Energy,s,dsde_rho,dsdrho_e,d2sde2,d2sdedrho,d2sdrho2\n")
    csvWriter = csv.writer(fid,delimiter=',')
    csvWriter.writerows(collected_data)

with open(fluidName + "_dataset_train.csv", "w+") as fid:
    fid.write("Density,Energy,s,dsde_rho,dsdrho_e,d2sde2,d2sdedrho,d2sdrho2\n")
    csvWriter = csv.writer(fid,delimiter=',')
    csvWriter.writerows(train_data)

with open(fluidName + "_dataset_dev.csv", "w+") as fid:
    fid.write("Density,Energy,s,dsde_rho,dsdrho_e,d2sde2,d2sdedrho,d2sdrho2\n")
    csvWriter = csv.writer(fid,delimiter=',')
    csvWriter.writerows(dev_data)

with open(fluidName + "_dataset_test.csv", "w+") as fid:
    fid.write("Density,Energy,s,dsde_rho,dsdrho_e,d2sde2,d2sdedrho,d2sdrho2\n")
    csvWriter = csv.writer(fid,delimiter=',')
    csvWriter.writerows(test_data)