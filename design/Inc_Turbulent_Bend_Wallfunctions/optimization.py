# FADO script: Shape Optimization with Species Variance OF

from FADO import *
import glob
import time
import os

# get the path to su2 executable
su2_run= os.environ["SU2_RUN"] + "/"
print("SU2 executable obtained from ", su2_run)

# Define a few often used variables
configMaster="sudo.cfg"
meshName="sudo_coarse_FFD.su2"
# inlet BC file
inletName="inlet.dat"
restartAdjName="solution_adj_dp.csv"

# Design variables ----------------------------------------------------- #

# important, this has to match the nr of variables
# 6 x 6 x 6 = 216
# x,y = 432
# x,y,z = 648
#minus the 6x6=36 nodes of the symmetry plane
nDV = 648-36-36
# nr of cores for mpi
ncores="8"

# define the objective
objective = 'Surface_Pressure_Drop'

#########################################################################################################
ffd = InputVariable(0.0,PreStringHandler("DV_VALUE="),nDV)

#
# Note that the last two numbers are the bounds, reduce if you want to limit the maximum deformation 
#########################################################################################################
ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -0.10,0.10)
#########################################################################################################

# Parameters ----------------------------------------------------------- #

# The master config `configMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))

enable_not_def = Parameter([""], LabelReplacer("%__NOT_DEF__"))
enable_def = Parameter([""], LabelReplacer("%__DEF__"))

# Switch Objective Functions
if objective == 'Uniformity':
    print("1. set parameter for Uniformity")
    enable_obj = Parameter(["SURFACE_UNIFORMITY"], LabelReplacer("__OBJ_FUNC__"))

elif objective == 'Surface_Pressure_Drop':
    print("1. set parameter for Surface_Pressure_Drop")
    enable_obj = Parameter(["SURFACE_PRESSURE_DROP"], LabelReplacer("__OBJ_FUNC__"))

else:
    raise Exception("no valid objective found.")

print(" ")
print("Running validation for", objective)


# Evaluations ---------------------------------------------------------- #

def_command = "mpirun -n " + ncores + " " + su2_run + "SU2_DEF " + configMaster
cfd_command = "mpirun -n " + ncores + " " + su2_run + "SU2_CFD " + configMaster  + "; pwd; cp restart.csv ../../restart.csv"
cfd_ad_command = "mpirun -n " + ncores + " " + su2_run + "SU2_CFD_AD " + configMaster
dot_ad_command = "mpirun -n " + ncores + " " + su2_run + "SU2_DOT_AD " + configMaster

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addData(meshName)
deform.addData(inletName)
deform.addExpected("mesh_out.su2")
deform.addParameter(enable_def)
deform.addParameter(enable_obj)

# direct run
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addData(inletName)
direct.addData("solution.csv")
direct.addExpected("restart.csv")
direct.addParameter(enable_direct)
direct.addParameter(enable_not_def)
direct.addParameter(enable_obj)

# adjoint run
adjoint = ExternalRun("ADJOINT",cfd_ad_command,True)
adjoint.setMaxTries(max_tries)
adjoint.addConfig(configMaster)
adjoint.addData("DEFORM/mesh_out.su2", destination=meshName)
adjoint.addData(inletName)
adjoint.addData(restartAdjName)
# add primal solution file
adjoint.addData("DIRECT/restart.csv", destination="solution.csv")

if objective == 'Uniformity':
    print("2. set adjoint for Uniformity")
    adjoint.addExpected("restart_adj_uniform.csv")

elif objective == 'Surface_Pressure_Drop':
    print("2. set adjoint for Surface_Pressure_Drop")
    adjoint.addExpected("restart_adj_dp.csv")

else:
    raise Exception("no valid objective found.")

adjoint.addParameter(enable_adjoint)
adjoint.addParameter(enable_not_def)
adjoint.addParameter(enable_obj)

# gradient projection
dot = ExternalRun("DOT",dot_ad_command,True)
dot.setMaxTries(max_tries)
dot.addConfig(configMaster)
dot.addData("DEFORM/mesh_out.su2", destination=meshName)
dot.addData(inletName)
print("Objective = ",objective)

if objective == 'Uniformity':
    print("3. set restart file for Uniformity")
    dot.addData("ADJOINT/restart_adj_uniform.csv", destination="solution_adj_uniform.csv")

elif objective == 'Surface_Pressure_Drop':
    print("3. set restart file for Surface_Pressure_Drop")
    dot.addData("ADJOINT/restart_adj_dp.csv", destination="solution_adj_dp.csv")

else:
    raise Exception("no valid objective found.")

dot.addExpected("of_grad.csv")
dot.addParameter(enable_def)
dot.addParameter(enable_obj) # necessary for correct file extension

# update restart file
#update_restart = ExternalRun(".",update_restart_command,False) # True means sym links are used for addData



# Functions ------------------------------------------------------------ #
#
# ### names according to CFlowOutput::AddAnalyzeSurfaceOutput ###
#
func_uniformity = Function("uniformity", "DIRECT/history.csv",LabeledTableReader("\"Uniformity(outlet)\""))
func_uniformity.addInputVariable(ffd,"DOT/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
func_uniformity.addValueEvalStep(deform)
func_uniformity.addValueEvalStep(direct)
func_uniformity.addGradientEvalStep(adjoint)
func_uniformity.addGradientEvalStep(dot)
func_uniformity.setDefaultValue(0.0)

func_surfdp = Function("avg_dp", "DIRECT/history.csv",LabeledTableReader("\"Pressure_Drop\""))
func_surfdp.addInputVariable(ffd,"DOT/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
func_surfdp.addValueEvalStep(deform)
func_surfdp.addValueEvalStep(direct)
func_surfdp.addGradientEvalStep(adjoint)
func_surfdp.addGradientEvalStep(dot)
func_surfdp.setDefaultValue(0.0)

# Driver --------------------------------------------------------------- #

driver = ScipyDriver()

#printDocumentation(driver.addObjective)
# min = minimization of OF
# avgT = function to be optimized
# 1.0 = scale, optimizer will see funcVal*scale, Can be used to scale the gradient from of_grad
if objective == 'Uniformity':
    print("4. set objective for Uniformity")
    driver.addObjective("min", func_uniformity, 0.5)

# here we need to use a rather small scaling to prevent immediate blow-up
elif objective == 'Surface_Pressure_Drop':
    print("4. set objective for Surface_Pressure_Drop")
    driver.addObjective("min", func_surfdp, 0.0005)

else:
    raise Exception("no valid objective found.")


driver.setWorkingDirectory("OPTIM")
#printDocumentation(driver.setEvaluationMode)
# True = parallel evaluation mode
# 5.0 = driver will check every 5sec whether it can start a new eval
driver.setEvaluationMode(False,5.0)
#printDocumentation(driver.setStorageMode)
# True = keep all designs
# DSN_ = folder prefix
driver.setStorageMode(True,"DSN_")
#printDocumentation(driver.setFailureMode)
# SOFT = if func eval fails, just the default val will be taken
driver.setFailureMode("SOFT")

# file containing the objective values per design iteration
his = open("optim.csv","w",1)
driver.setHistorian(his)

# Optimization, SciPy -------------------------------------------------- #

import scipy.optimize

driver.preprocess()
x = driver.getInitial()

# disp:True prints convergence messages
# maxiter: int limits the optimization to maxiter number of iterations
# ftol: precision tolerance goal for the value of f in the stopping criterion
options = {'disp': True, 'ftol': 1e-10, 'maxiter': 10}

# Use Sequential Least Squares Programming SLSQP
optimum = scipy.optimize.minimize(driver.fun, x, method="SLSQP", jac=driver.grad,\
          constraints=driver.getConstraints(), bounds=driver.getBounds(), options=options)

print(" | Closing...")
his.close()

print(" +--- Finished")

