---
title: Data-Driven Fluid Model
permalink: /SU2_CFD/src/fluid/CDataDrivenFluid.cpp
---
# Using Data-Driven Fluid Models in SU2
Modeling non-ideal fluid behavior can be difficult when limited to model equations or can be time consuming when performing large-scale simulations using the CoolProp fluid model. The data-driven fluid model class allows for the equation of state to be defined through a look-up table (LUT) or a set of multi-layer perceptrons (MLP), using an entropy-based equation of state. Given enough reference data and careful tuning of the initial conditions, it is possible to attain similar accuracies as the CoolProp library, while being compatible with the SU2 adjoint solver and a faster iteration time.  

## Data-Driven Fluid Model Class

The data-driven fluid model class allows for the use of LUT or MLP to interpolate the entropy and its partial derivatives for a given density and static energy. This type of fluid model can be used as an alternative to the CoolProp fluid model if the fluid in question is not included in the CoolProp library, adjoint capability is required, or when computational performance is important. 

The data-driven fluid model is enabled through the config option ```DATADRIVEN_FLUID```. The option ```INTERPOLATION_METHOD``` refers to which kind of interpolator is used for thermodynamic state evaluation. The available methods here are ```LUT``` for a look-up table based approach, or ```MLP``` for the use of an MLP. Information on these two regression methods is provided in later paragraphs.

The datadriven fluid model in SU2 uses a general, entropic equation of state to calculate the primary and secondary flow variables. The fluid entropy and its first and second partial derivatives are determined through the interpolation algorithm (LUT or MLP) given the controlling variables density and static energy. The user should therefore supply an MLP or LUT that uses inputs density and static energy and predicts the fluid entropy and its first and second partial derivatives with respect to the inputs. 
The controlling variables for the MLP should be named "Density" and "Energy". The output variables should be named:

1. "s": fluid entropy
2. "dsde_rho": first entropy derivative w.r.t. static energy
3. "dsdrho_e": first entropy derivative w.r.t. density
4. "d2sdedrho": second entropy derivative w.r.t density and static energy
5. "d2sde2": second entropy derivative w.r.t. static energy
6. "d2sdrho2": second entropy derivative w.r.t. density 

Based on the values for the partial derivatives of the entropy, it is possible to calculate the temperature, pressure, enthalpy, speed of sound, and secondary flow variables. Newton solver processes are used when the thermodynamic state is defined through variable pairs other than density and static energy. The initial values for density and static energy have to be defined by the user in the config file through ```DATADRIVEN_FLUID_INITIAL_DENSITY``` and ```DATADRIVEN_FLUID_INITIAL_ENERGY```. These values thave to be chosen carefully such that the initial condition of the simulation can be attained. The option ```DATADRIVEN_NEWTON_RELAXATION``` determines the relaxation factor for the Newton solver processes in the data-driven fluid model. Higher values result in faster convergence of the Newton solvers in stable regions. Lower values result in more iterations, but are more likely to avoid instabilities. 

## MLP Definition
Data regression using an MLP is enabled through selecting the ```MLP``` for the option ```INTERPOLATION_METHOD``` in the configuration file. In order to load an MLP architecture into SU2, an input file needs to be provided describing the network architecture, as well as the input and output variable names and ranges. An example of such an input file is provided in this folder (```MLP_Air.mlp```). This file can be generated from an MLP trained through Tensorflow using the ```Tensorflow2SU2.py``` script. Additional information regarding the translation from a Tensorflow model to an SU2 input file is provided in the python code. The script used to train the MLP is provided in ```MLPTrainer.py``` and the script used to generate the reference data from CoolProp in "Generate_Dataset.py". 

MLP regression is enabled through the MLPCpp submodule of SU2 (subprojects/MLPCpp). This submodule is enabled through the ```-Denable-mlpcpp=true``` meson command. The MLPCpp submodule can be used within any C++ code for MLP evaluation. Additional documentation regarding the MLPCpp module can be found on https://github.com/EvertBunschoten/MLPCpp 

## LUT Definition

In some cases it may be more convenient to use an LUT instead of an MLP for data regression. The data-driven fluid model in SU2 is also compatible with using an unstructured table (```Common/src/containers/CLookUpTable.cpp```) for the regression of the entropy and its partial derivatives. Data regression using an LUT is enabled through selecting the ```LUT``` for the option ```INTERPOLATION_METHOD``` in the configuration file. Examples for the .drg table format file can be found under ```UnitTests/Common/containers/``` or can be generated using the ```LUTWriter.m``` MATLAB script in this tutorial folder. 