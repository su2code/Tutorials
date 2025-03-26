###############################################################################################
#       #      _____ __  _____      ____        __        __  ____                   #        #
#       #     / ___// / / /__ \    / __ \____ _/ /_____ _/  |/  (_)___  ___  _____   #        #
#       #     \__ \/ / / /__/ /   / / / / __ `/ __/ __ `/ /|_/ / / __ \/ _ \/ ___/   #        #
#       #    ___/ / /_/ // __/   / /_/ / /_/ / /_/ /_/ / /  / / / / / /  __/ /       #        #
#       #   /____/\____//____/  /_____/\__,_/\__/\__,_/_/  /_/_/_/ /_/\___/_/        #        #
#       #                                                                            #        #
###############################################################################################

########################### FILE NAME: 1:generate_fluid_data.py ###############################
#=============================================================================================#
# author: Evert Bunschoten                                                                    |
#    :PhD Candidate ,                                                                         |
#    :Flight Power and Propulsion                                                             |
#    :TU Delft,                                                                               |
#    :The Netherlands                                                                         |
#                                                                                             |
#                                                                                             |
# Description:                                                                                |
#  Generate the single-phase fluid data for siloxane MM which is used to train the            |
# physics-informed neural network.                                                            |
#                                                                                             |
# Version: 2.0.0                                                                              |
#                                                                                             |
#=============================================================================================#

from su2dataminer.config import Config_NICFD
from su2dataminer.generate_data import DataGenerator_CoolProp

# Load SU2 DataMiner configuration.
Config = Config_NICFD("SU2DataMiner_MM.cfg")

# Initiate data generator.
DG = DataGenerator_CoolProp(Config)
DG.PreprocessData()
DG.ComputeData()

# Visualize and save fluid data.
DG.VisualizeFluidData()
DG.SaveData()
