###############################################################################################
#       #      _____ __  _____      ____        __        __  ____                   #        #
#       #     / ___// / / /__ \    / __ \____ _/ /_____ _/  |/  (_)___  ___  _____   #        #
#       #     \__ \/ / / /__/ /   / / / / __ `/ __/ __ `/ /|_/ / / __ \/ _ \/ ___/   #        #
#       #    ___/ / /_/ // __/   / /_/ / /_/ / /_/ /_/ / /  / / / / / /  __/ /       #        #
#       #   /____/\____//____/  /_____/\__,_/\__/\__,_/_/  /_/_/_/ /_/\___/_/        #        #
#       #                                                                            #        #
###############################################################################################

############################# FILE NAME: 0:generate_config.py #################################
#=============================================================================================#
# author: Evert Bunschoten                                                                    |
#    :PhD Candidate ,                                                                         |
#    :Flight Power and Propulsion                                                             |
#    :TU Delft,                                                                               |
#    :The Netherlands                                                                         |
#                                                                                             |
#                                                                                             |
# Description:                                                                                |
#  Generate configuration for defining a physics-informed neural network for modeling the     | 
#  fluid properties of siloxane MM in NICFD with the data-driven fluid model in SU2.          |
#                                                                                             |
# Version: 2.0.0                                                                              |
#                                                                                             |
#=============================================================================================#

from su2dataminer.config import Config_NICFD

# The fluid data for siloxane MM are generated with the CoolProp module using the Helmoltz
# equation of state.
fluid_name = "MM"
EoS_type = "HEOS"

Config = Config_NICFD()
Config.SetFluid(fluid_name)
Config.SetEquationOfState(EoS_type)

# Fluid data are generated on a density-energy grid rather than pressure-temperature.
Config.UsePTGrid(False)

# Display configuration settings and save config object.
Config.SetConfigName("SU2DataMiner_MM")
Config.PrintBanner()
Config.SaveConfig()