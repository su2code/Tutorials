# Multi-Layer Perceptrons in SU2

This tutorial explains how to use the multi-layer perceptron (MLP) class for data-driven methods in SU2. MLP's, or artificial neural networks, are being used in CFD calculations for a variety of regression processes. From turbulence closure models to data regression applications, MLP's have been shown to be a valuable tool in CFD. With the addition of the MLP classes in SU2, it is now possible to develop such models for use in the SU2 suite. In this tutorial, the code structure of the MLP classes in SU2 is explained, as well as an application in data-driven fluid property modeling. Supporting Python scripts are provided to prepare the necessary data files for the SU2 MLP classes to function. 


# MLP class file structure

The MLP class prototype files can be found under Common/include/toolboxes/multilayer_perceptron.
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

It is possible to load multiple networks with different input and output variables. In order to ensure the right CNeuralNetwork class(es) is/are selected when performing a regression given a set of input variables, the CIOMap class is used. To demonstrate what this class does, let's say you want to perform a regression operation predicting the temperature based on density and static energy. Two MLP files were loaded into the CLookUp_ANN class. MLP 1 has (ordered) inputs 1:static energy and 2:density and (ordered) outputs 1:specific heat, 2:speed of sound, 3:temperature. MLP 2 has the (ordered) inputs 1:pressure, 2:density and (ordered) outputs 1:temperature, 2:specific heat, 3:entropy. The CIOMap class checks which of the loaded MLPs have the same input variables (density and static energy) and include one or multiple of the output variables (temperature) of the desired regression operation. In this case, the CIOMap class will select MLP 1 only, since it has the same input variables as the regression operation and has temperature in its output variables. Although MLP 2 has temperature as one of its output variables, it is not included, as it does not include static energy in its input variables. An error will be raised if none of the loaded MLP's contains all the input variables or if some of the desired outputs are missing from the MLP output variables.

In addition to loading multiple networks with different input and output variables, it is possible to load multple networks with the same input and output variables, but with different data ranges. When performing a regression operation, the CLookUp_ANN class will check which of the loaded MLPs with the right input and output variables has an input variable normalization range that includes the query point. The corresponding MLP will then be selected for regression. If the query point lies outside the data range of all loaded MLPs, extrapolation will be performed using the MLP with a data range close to the query point. For example, two MLPs are loaded with input variables 1:density, 2:static energy and output variables 1:temperature, 2:pressure, 3:speed of sound. MLP 1 has a density normalization range between 1.0 and 10.0 kg m^{-3}, whereas MLP 2 has a range between 10.0 and 100.0 kg m^{-3}. If regression is performed on a query point with a density value of 5.0 kg m^{-3}, MLP 1 will be selected for regression. If the density is for example 50 kg m^{-3}, MLP 2 will be selected. If the density is 0.5 kg m^{-3}, MLP 1 will be selected as its data range lies closer to the query point. Vice versa if the density is for example 150 kg m^{-3}. 

# Data-Driven Fluid Model Class

The MLP class is implemented in the CDataDrivenFluid fluid model in SU2. Here, MLP's can be used to determine the thermodynamic state of complex fluids. This type of fluid model can be used as an alternative to the CoolProp fluid model if the fluid in question is not included in the CoolProp library or when computational performance is important. 

Currently, MLPs in SU2 can only be used in the context of a fluid model. The config option "DATADRIVEN_FLUID" for fluid model allows for the use of an MLP or look-up table for thermodynamic state evaluation. The option "INTERPOLATION_METHOD" refers to which kind of interpolator is used for thermodynamic state evaluation. The available methods here are "LUT" for a look-up table based approach, or "MLP" for the use of an MLP. In this tutorial, focus lies on the latter option. 

The datadriven fluid model in SU2 uses a general, entropic equation of state to calculate the primary and secondary flow variables <TODO: give reference to entropic equation of state>. The fluid entropy and its first and second partial derivatives are determined through the interpolation algorithm (LUT or MLP) given the controlling variables density and static energy. The user should therefore supply an MLP or LUT that uses inputs density and static energy and predicts the fluid entropy and its first and second partial derivatives with respect to the inputs. 

