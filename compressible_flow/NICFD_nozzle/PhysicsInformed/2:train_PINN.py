###############################################################################################
#       #      _____ __  _____      ____        __        __  ____                   #        #
#       #     / ___// / / /__ \    / __ \____ _/ /_____ _/  |/  (_)___  ___  _____   #        #
#       #     \__ \/ / / /__/ /   / / / / __ `/ __/ __ `/ /|_/ / / __ \/ _ \/ ___/   #        #
#       #    ___/ / /_/ // __/   / /_/ / /_/ / /_/ /_/ / /  / / / / / /  __/ /       #        #
#       #   /____/\____//____/  /_____/\__,_/\__/\__,_/_/  /_/_/_/ /_/\___/_/        #        #
#       #                                                                            #        #
###############################################################################################

################################ FILE NAME: 2:train_PINN.py ###################################
#=============================================================================================#
# author: Evert Bunschoten                                                                    |
#    :PhD Candidate ,                                                                         |
#    :Flight Power and Propulsion                                                             |
#    :TU Delft,                                                                               |
#    :The Netherlands                                                                         |
#                                                                                             |
#                                                                                             |
# Description:                                                                                |
#  Initate physics-informed machine learning process for training the neural network used to  |
#  model the fluid properties of siloxane MM in NICFD with the SU2 data-driven fluid model.   |
#                                                                                             |
# Version: 2.0.0                                                                              |
#                                                                                             |
#=============================================================================================#

from su2dataminer.config import Config_NICFD
from su2dataminer.manifold import TrainMLP_NICFD

# Load SU2 DataMiner configuration.
Config = Config_NICFD("SU2DataMiner_MM.cfg")

# Set learning rate parameters and define network architecture.
Eval = TrainMLP_NICFD(Config)

# Initial learning rate: 10^-3, learning rate decay parameter: 9.8787, mini-batch size: 2^6.
Eval.SetAlphaExpo(-3.0)
Eval.SetLRDecay(+9.8787e-01)
Eval.SetBatchExpo(6)

# Network architecture: two hidden layers with 12 nodes.
Eval.SetHiddenLayers([12,12])
# Hidden layer activation function: exp(x)
Eval.SetActivationFunction("exponential")
# Display training progress in the terminal.
Eval.SetVerbose(1)

# Initiate training process.
Eval.CommenceTraining()
Eval.TrainPostprocessing()

Config.UpdateMLPHyperParams(Eval)
Config.SaveConfig()