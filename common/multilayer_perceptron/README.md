---
title: Multi-Layer Perceptrons and data-driven fluid model
permalink: /common/multilayer_peceptron/
---
# Multi-Layer Perceptrons in SU2

This tutorial explains how to use the multi-layer perceptron (MLP) class for data-driven methods in SU2. MLP's, or artificial neural networks, are being used in CFD calculations for a variety of regression processes. From turbulence closure models to data regression applications, MLP's have been shown to be a valuable tool in CFD. With the addition of the MLP classes in SU2, it is now possible to develop such models for use in the SU2 suite. In this tutorial, the code structure of the MLP classes in SU2 is explained, as well as an application in data-driven fluid property modeling. Supporting Python scripts are provided to prepare the necessary data files for the SU2 MLP classes to function. 


# MLP class description
The MLP class prototype files can be found under SU2/Common/include/toolboxes/multilayer_perceptron.
An MLP computes data by having its inputs manipulated by a series of operations, depending on the architecture of the network. Interpreting the network architecture and its respective input and output variables is therefore crucial for the MLP functionality. Information regarding the network architecture, input and output variables, and activation functions is provided to SU2 via a .mlp input file, of which an example is provided in this folder. More information regarding the file structure is provided in a later section. 

The main MLP class in SU2 which can be used for look-up operations is the CLookUp_ANN class. This class allows to load one or multiple networks given a list of input files. Each of these files is read by the CReadNeuralNetwork class. This class reads the .mlp input file and stores the architectural information listed in it. It will also run some compatibility checks on the file format. For example, the total layer count should be provided before listing the activation functions. For every read .mlp file, an MLP class is generated using the CNeuralNetwork class. This class stores the input and output variables, network architecture, activation functions, and weights and biases of every synapse and neuron. Currently, the CNeuralNetwork class only supports simple, feed-forward, dense neural network types. Supported activation function types are:
1: linear (y = x)
2: relu
3: elu
4: swish
5: sigmoid
6: tanh
7: selu
8: gelu
9: exponential (y = exp(x))

It is possible to load multiple networks with different input and output variables. An error will be raised if none of the loaded MLP's contains all the input variables or if some of the desired outputs are missing from the MLP output variables.
In addition to loading multiple networks with different input and output variables, it is possible to load multple networks with the same input and output variables, but with different data ranges. When performing a regression operation, the CLookUp_ANN class will check which of the loaded MLPs with the right input and output variables has an input variable normalization range that includes the query point. The corresponding MLP will then be selected for regression. If the query point lies outside the data range of all loaded MLPs, extrapolation will be performed using the MLP with a data range close to the query point. 

# MLP Definition
In order to load an MLP architecture into SU2, an input file needs to be provided describing the network architecture, as well as the input and output variable names and ranges. An example of such an input file is provided in this folder (MLP_Air_SU2.mlp). This file can be generated from an MLP trained through Tensorflow using the "Tensorflow2SU2.py" script. Additional information regarding the translation from a Tensorflow model to an SU2 input file is provided in the python code. 

# Data-Driven Fluid Model Class

The MLP class is used in the CDataDrivenFluid fluid model class in SU2. Here, MLP's can be used to determine the thermodynamic state of complex fluids. This type of fluid model can be used as an alternative to the CoolProp fluid model if the fluid in question is not included in the CoolProp library or when computational performance is important. 

Currently, MLPs in SU2 can only be used in the context of a fluid model. The config option "DATADRIVEN_FLUID" for fluid model allows for the use of an MLP or look-up table for thermodynamic state evaluation. The option "INTERPOLATION_METHOD" refers to which kind of interpolator is used for thermodynamic state evaluation. The available methods here are "LUT" for a look-up table based approach, or "MLP" for the use of an MLP. In this tutorial, focus lies on the latter option. 

The datadriven fluid model in SU2 uses a general, entropic equation of state to calculate the primary and secondary flow variables. The fluid entropy and its first and second partial derivatives are determined through the interpolation algorithm (LUT or MLP) given the controlling variables density and static energy. The user should therefore supply an MLP or LUT that uses inputs density and static energy and predicts the fluid entropy and its first and second partial derivatives with respect to the inputs. 
The input variables for the MLP should be named "Density" and "Energy". The output variables should be named:
"s": fluid entropy
"dsde_rho": first entropy derivative w.r.t. static energy
"dsdrho_e": first entropy derivative w.r.t. density
"d2sdedrho": second entropy derivative w.r.t density and static energy
"d2sde2": second entropy derivative w.r.t. static energy
"d2sdrho2": second entropy derivative w.r.t. density 

The order of the input or output variables in the input file does not affect the MLP or LUT regression processes.

