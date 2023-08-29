#!/usr/bin/env python

## \file Generate_Dataset.py
#  \brief Example python script for training an MLP and writing an MLP 
#   input file formatted for the CDataDriven fluid model in SU2.
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

seed_value = 2
import os
from re import L
os.environ['PYTHONASHSEED'] = str(seed_value)
seed_value += 1
import random
random.seed(seed_value)
seed_value += 1
import numpy as np
np.random.seed(seed_value)
seed_value += 1 
import tensorflow as tf
tf.random.set_seed(seed_value)
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
import time 
from tensorflow import keras
import sys
import pickle
import matplotlib.pyplot as plt 

class Train_Flamelet_MLP:
    # Description:
    # Construct, train, and save an artificial neural network for data-driven NICFD simulations in SU2
    #

    # Training parameters:
    n_epochs = 250      # Number of epochs to train for
    alpha_expo = -3.0   # Alpha training exponent parameter
    lr_decay = 1.0      # Learning rate decay parameter
    batch_size = 10     # Mini-batch size exponent 

    # Activation function options
    activation_functions = [["relu"],
                            ["elu"], 
                            ["selu"], 
                            ["gelu"],
                            ["elu", "tanh"],
                            ["elu", "sigmoid"],
                            ["tanh"], 
                            ["sigmoid"], 
                            ["swish"]]
    
    i_activation_function = 0   # Activation function index

    hidden_layers = [] # Hidden layer architecture
    train_name = ""

    # Hardware info:
    kind_device = "CPU" # Device type used to train (CPU or GPU)
    device_index = 0    # Device index (node index or GPU card index)
    
    # Controlling variables
    controlling_vars = ["Density", 
                        "Energy"]
    
    # Variable names to train for
    train_vars = []

    # Input data files:
    Full_file = ""  # Full data set file name
    Train_file = "" # Train data set file name
    Test_file = ""  # Test data set file name
    Val_file = ""   # Validation data set file name

    save_dir = "/"  # Directory to save trained network information to

    def __init__(self, kind_train):
        
        # Set train variables based on what kind of network is trained
        self.train_name = kind_train
        self.train_vars = ['s','dsde_rho','dsdrho_e','d2sde2','d2sdedrho','d2sdrho2']

    # Setters/Getters:
    def SetNEpochs(self, n_input):
        self.n_epochs = n_input
    def SetActivationIndex(self, i_input):
        self.i_activation_function = i_input
    def SetFullInputFile(self, input_file):
        self.Full_file = input_file 
    def SetTrainInputFile(self, input_file):
        self.Train_file = input_file
    def SetTestInputFile(self, input_file):
        self.Test_file = input_file
    def SetValInputFile(self, input_file):
        self.Val_file = input_file
    def SetSaveDir(self, input_dir):
        self.save_dir = input_dir
    def SetDeviceKind(self, kind_device):
        self.kind_device = kind_device
    def SetDeviceIndex(self, device_index):
        self.device_index = device_index
    def SetControllingVariables(self, x_vars):
        self.controlling_vars = x_vars
    def SetLRDecay(self, lr_decay):
        self.lr_decay = lr_decay
    def SetAlphaExpo(self, alpha_expo):
        self.alpha_expo = alpha_expo
    def SetBatchSize(self, batch_size):
        self.batch_size = batch_size
    def SetHiddenLayers(self, hidden_layer_neurons):
        self.hidden_layers = hidden_layer_neurons
    def SetFreeFlameDir(self, freeflame_dir):
        self.freeflame_dir = freeflame_dir
    def SetBurnerFlameDir(self, burnerflame_dir):
        self.burnerflame_dir = burnerflame_dir    
    def SetEquilibriumDir(self, equilibrium_dir):
        self.equilibrium_dir = equilibrium_dir
    def GetTestScore(self):
        return self.test_score[0]
    def GetTestTime(self):
        return self.test_time
    
    # Obtain controlling variable data and train data from input file for 
    # a given set of variable names.
    def GetReferenceData(self, dataset_file, x_vars, train_variables):

        # Open data file and get variable names from the first line
        fid = open(dataset_file, 'r')
        line = fid.readline()
        fid.close()
        line = line.strip()
        line_split = line.split(',')
        if(line_split[0][0] == '"'):
            varnames = [s[1:-1] for s in line_split]
        else:
            varnames = line_split
        
        # Get indices of controlling and train variables
        iVar_x = [varnames.index(v) for v in x_vars]
        iVar_y = [varnames.index(v) for v in train_variables]

        # Retrieve respective data from data set
        D = np.loadtxt(dataset_file, delimiter=',', skiprows=1)
        X_data = D[:, iVar_x]
        Y_data = D[:, iVar_y]

        return X_data, Y_data

    # Obtain and preprocess train, test, and validation data
    def GetTrainData(self):

        # Retrieve full, train, test, and validation data
        print("Reading train, test, and validation data...")
        X_full, Y_full = self.GetReferenceData(self.Full_file, self.controlling_vars, self.train_vars)
        self.X_train, self.Y_train = self.GetReferenceData(self.Train_file, self.controlling_vars, self.train_vars)
        self.X_test, self.Y_test = self.GetReferenceData(self.Test_file, self.controlling_vars, self.train_vars)
        self.X_val, self.Y_val = self.GetReferenceData(self.Val_file, self.controlling_vars, self.train_vars)
        print("Done!")

        # Calculate normalization bounds of full data set
        self.X_min, self.X_max = np.min(X_full, 0), np.max(X_full, 0)
        self.Y_min, self.Y_max = np.min(Y_full, 0), np.max(Y_full, 0)

        # Free up memory
        del X_full
        del Y_full


        # Normalize train, test, and validation controlling variables
        self.X_train_norm = (self.X_train - self.X_min) / (self.X_max - self.X_min)
        self.X_test_norm = (self.X_test - self.X_min) / (self.X_max - self.X_min)
        self.X_val_norm = (self.X_val - self.X_min) / (self.X_max - self.X_min)

        # Normalize train, test, and validation data
        self.Y_train_norm = (self.Y_train - self.Y_min) / (self.Y_max - self.Y_min)
        self.Y_test_norm = (self.Y_test - self.Y_min) / (self.Y_max - self.Y_min)
        self.Y_val_norm = (self.Y_val - self.Y_min) / (self.Y_max - self.Y_min)
    
    # Construct MLP based on architecture information
    def DefineMLP(self):

        # Construct MLP on specified device
        with tf.device("/"+self.kind_device+":"+str(self.device_index)):

            # Initialize sequential model
            self.model = keras.models.Sequential()
            self.history = None 

            # Retrieve activation function(s) for the hidden layers
            activation_functions_in_MLP = self.activation_functions[self.i_activation_function]

            # Add input layer
            self.model.add(keras.layers.Dense(self.hidden_layers[0], input_dim=self.X_train.shape[1], activation=activation_functions_in_MLP[0], kernel_initializer='he_uniform'))

            # Add hidden layers
            iLayer = 1
            while iLayer < len(self.hidden_layers):
                activation_function = activation_functions_in_MLP[iLayer % len(activation_functions_in_MLP)]
                self.model.add(keras.layers.Dense(self.hidden_layers[iLayer], activation=activation_function, kernel_initializer="he_uniform"))
                iLayer += 1
            
            # Add output layer
            self.model.add(keras.layers.Dense(self.Y_train.shape[1], activation='linear'))

            # Define learning rate schedule and optimizer
            lr_schedule = keras.optimizers.schedules.ExponentialDecay(10**self.alpha_expo, decay_steps=10000,
                                                                    decay_rate=self.lr_decay, staircase=False)
            opt = keras.optimizers.Adam(learning_rate=lr_schedule, beta_1=0.9, beta_2=0.999, epsilon=1e-8, amsgrad=False) 

            # Compile model on device
            self.model.compile(optimizer=opt, loss="mean_squared_error", metrics=["mape"])
            self.cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=self.save_dir,
                                                    save_weights_only=True,
                                                    verbose=0)
    
    # Load previously trained MLP (did not try this yet!)
    def LoadMLP(self, model_filename):
        with tf.device("/"+self.kind_device+":"+str(self.device_index)):
            self.model = tf.keras.models.load_model(model_filename, compile=False)
            lr_schedule = keras.optimizers.schedules.ExponentialDecay(10**self.alpha_expo, decay_steps=10000,
                                                                    decay_rate=self.lr_decay, staircase=False)
            opt = keras.optimizers.Adam(learning_rate=lr_schedule, beta_1=0.9, beta_2=0.999, epsilon=1e-8, amsgrad=False) 
            self.model.compile(optimizer=opt, loss="mean_squared_error", metrics=["mape"])
            
    # Initialize MLP training 
    def Train_MLP(self):
        with tf.device("/"+self.kind_device+":"+str(self.device_index)):
            t_start = time.time()
            self.history = self.model.fit(self.X_train_norm, self.Y_train_norm, epochs=self.n_epochs, batch_size=2**self.batch_size,
                                        verbose=2, validation_data=(self.X_val_norm, self.Y_val_norm), shuffle=True,callbacks=[self.cp_callback])
            t_end = time.time()
            # Store training time in minutes
            self.train_time = (t_end - t_start) / 60
    
    # Evaluate test set 
    def Evaluate_TestSet(self):
        with tf.device("/"+self.kind_device+":"+str(self.device_index)):
            t_start_test = time.time()
            self.test_score = self.model.evaluate(self.X_test_norm, self.Y_test_norm, verbose=0)
            t_end_test = time.time()
            self.test_time = (t_end_test - t_start_test)
    
    # Write MLP input file for SU2 simulations
    def write_SU2_MLP(self, file_out):
        # This function writes the MLP to a format which can be read by the SU2 MLP import tool
        # Inputs:
        # - file_out: output file name without extension
        # - input_names: list of strings with the variable names of the MLP input(s)
        # - output names: list of strings with the variable names of the MLP output(s)
        # - model: tensorflow.keras.model; the trained model

        # MLP config
        model_config = self.model.get_config()

        # Number of input variables in the model
        n_inputs = model_config['layers'][0]['config']['batch_input_shape'][1]
        # Number of output variables in the model
        n_outputs = model_config['layers'][-1]['config']['units']

        # Checking if number of provided input and output names are equal to those in the model
        # if not n_inputs == len(input_names):
        #     raise Exeption("Number of input names unequal to the number of inputs in the model")
        # if not n_outputs == len(output_names):
        #     raise Exeption("Number of output names unequal to the number of outputs in the model")

        # Opening output file
        fid = open(file_out+'.mlp', 'w+')
        fid.write("<header>\n\n")
        n_layers = len(model_config['layers'])

        # Writing number of neurons per layer
        fid.write('[number of layers]\n%i\n\n' % n_layers)
        fid.write('[neurons per layer]\n')
        activation_functions = []

        for iLayer in range(n_layers-1):
            layer_class = model_config['layers'][iLayer]['class_name']
            if layer_class == 'InputLayer':
                # In case of the input layer, the input shape is written instead of the number of units
                activation_functions.append('linear')
                n_neurons = model_config['layers'][iLayer]['config']['batch_input_shape'][1]
            else:
                # try:
                #     activation_functions.append(model_config['layers'][iLayer]['config']['activation']['config']['activation'])
                # except:
                activation_functions.append(model_config['layers'][iLayer]['config']['activation'])#['config']['activation'])
                    #pass 

                n_neurons = model_config['layers'][iLayer]['config']['units']

            fid.write('%i\n' % n_neurons)
        fid.write('%i\n' % n_outputs)

        activation_functions.append('linear')

        # Writing the activation function for each layer
        fid.write('\n[activation function]\n')
        for iLayer in range(n_layers):
            fid.write(activation_functions[iLayer] + '\n')

        # Writing the input and output names
        fid.write('\n[input names]\n')
        for input in self.controlling_vars:
                fid.write(input + '\n')
        
        fid.write('\n[input normalization]\n')
        for i in range(len(self.controlling_vars)):
            fid.write('%+.16e\t%+.16e\n' % (self.X_min[i], self.X_max[i]))
        
        fid.write('\n[output names]\n')
        for output in self.train_vars:
            fid.write(output+'\n')
            
        fid.write('\n[output normalization]\n')
        for i in range(len(self.train_vars)):
            fid.write('%+.16e\t%+.16e\n' % (self.Y_min[i], self.Y_max[i]))

        fid.write("\n</header>\n")
        # Writing the weights of each layer
        fid.write('\n[weights per layer]\n')
        for layer in self.model.layers:
            fid.write('<layer>\n')
            weights = layer.get_weights()[0]
            for i in range(np.shape(weights)[0]):
                weights_of_neuron = weights[i, :]
                for j in range(len(weights_of_neuron)):
                    fid.write('%+.16e\t' % weights_of_neuron[j])
                fid.write('\n')
            fid.write('</layer>\n')
        
        # Writing the biases of each layer
        fid.write('\n[biases per layer]\n')
        
        # Input layer biases are set to zero
        fid.write('%+.16e\t%+.16e\t%+.16e\n' % (0.0, 0.0, 0.0))

        for layer in self.model.layers:
            biases = layer.get_weights()[1]
            for i in range(len(biases)):
                fid.write('%+.16e\t' % biases[i])
            fid.write('\n')


        fid.close()

    # Write an output file containing relevant training outcomes and network information
    def Save_Relevant_Data(self):
        
        pickle.dump(self.history.history, open(self.save_dir + "/training_history_"+self.train_name, "wb"))
        self.model.save(self.save_dir + "/MLP_"+self.train_name)

        fid = open(self.save_dir + "/MLP_"+self.train_name+"_performance.txt", "w+")
        fid.write("Training time[minutes]: %+.3e\n" % self.train_time)
        fid.write("Validation score: %+.16e\n" % self.test_score[0])
        fid.write("Total neuron count:  %i\n" % np.sum(np.array(self.hidden_layers)))
        fid.write("Evaluation time[seconds]: %+.3e\n" % (self.test_time))
        fid.write("Alpha exponent: %+.4e\n" % self.alpha_expo)
        fid.write("Learning rate decay: %+.4e\n" % self.lr_decay)
        fid.write("Batch size exponent: %i\n" % self.batch_size)
        fid.write("Activation function index: %i\n" % self.i_activation_function)
        fid.write("Number of hidden layers: %i\n" % len(self.hidden_layers))
        fid.write("Architecture: " + " ".join(str(n) for n in self.hidden_layers) + "\n")
        fid.close()

        self.write_SU2_MLP(self.save_dir + "/MLP_"+self.train_name)

    # Plot training history trend
    def Plot_and_Save_History(self):
        History = pickle.load(open(self.save_dir + "/training_history_"+self.train_name, 'rb'))

        fig = plt.figure()
        ax = plt.axes()
        ax.plot(np.log10(History['loss']), 'b', label='Training score')
        ax.plot(np.log10(History['val_loss']), 'r', label="Test score")
        ax.plot([0, len(History['loss'])], [np.log10(self.test_score[0]), np.log10(self.test_score[0])], 'm--', label=r"Validation score")
        ax.grid()
        ax.legend(fontsize=20)
        ax.set_xlabel("Iteration[-]", fontsize=20)
        ax.set_ylabel("Training loss function [-]", fontsize=20)
        ax.set_title(""+self.train_name+" Training History", fontsize=22)
        ax.tick_params(axis='both', which='major', labelsize=18)
        fig.savefig(self.save_dir + "/History_Plot_"+self.train_name+".png", format='png', bbox_inches='tight')
    
    # Visualize network architecture
    def Plot_Architecture(self):
        fig = plt.figure()
        plt.plot(np.zeros(len(self.controlling_vars)), np.arange(len(self.controlling_vars)) - 0.5*len(self.controlling_vars), 'bo')
        for i in range(len(self.hidden_layers)):
            plt.plot((i+1)*np.ones(int(self.hidden_layers[i])), np.arange(int(self.hidden_layers[i])) - 0.5*self.hidden_layers[i], 'ko')
        plt.plot((i+2)*np.ones(len(self.train_vars)), np.arange(len(self.train_vars)) - 0.5*len(self.train_vars), 'go')
        plt.axis('equal')
        fig.savefig(self.save_dir +"/"+self.train_name+"_architecture.png",format='png', bbox_inches='tight')
        plt.close(fig)
    

# Define save directory
save_dir = "./"
# Directory containing full, train, test, and validation data 
train_data_dir = "./"

# Hardware to train on (CPU / GPU)
device = "CPU"

# Hardware device index
device_index = 0

# Retrieve training parameters
alpha_expo = -3.1
lr_decay = 0.99
batch_size = 6
i_activation_function = 2

# Network hidden layer architecture information (perceptron count per hidden layer)
NN = [15, 20, 10]

fluidName = "Air"

# Define MLP trainer object
T = Train_Flamelet_MLP(fluidName)

# Set training parameters
T.SetNEpochs(350)
T.SetActivationIndex(i_activation_function)
T.SetBatchSize(batch_size)
T.SetLRDecay(lr_decay)
T.SetAlphaExpo(alpha_expo)
T.SetControllingVariables(["Density", "Energy"])

# Set train data file names
T.SetFullInputFile(train_data_dir + fluidName + "_dataset_full.csv")
T.SetTrainInputFile(train_data_dir +  fluidName + "_dataset_train.csv")
T.SetTestInputFile(train_data_dir +  fluidName + "_dataset_test.csv")
T.SetValInputFile(train_data_dir +  fluidName + "_dataset_dev.csv")


T.SetSaveDir(save_dir)

T.SetDeviceKind(device)
T.SetHiddenLayers(NN)
T.SetDeviceIndex(device_index)

# Retrieve relevant data
T.GetTrainData()

# Compile MLP on device
T.DefineMLP()

# Start training and evaluate performance 
T.Train_MLP()
T.Evaluate_TestSet()

# Save relevant data and postprocess
T.Save_Relevant_Data()
T.Plot_and_Save_History()
T.Plot_Architecture()
