# FADO script: Shape Optimization with pressure drop minimization 

from FADO import *
from timeit import default_timer as timer
import glob
import time
import os
import subprocess

# get the path to su2 executable
su2_run= os.environ["SU2_RUN"] + "/"
print("SU2 executable obtained from ", su2_run)

# Some settings that depend on the case

# nr of cores for mpi
ncores="2"

# Set to true if you want to use the restart files of previous design iterations
# this set RESTART= NO to RESTART=YES after the first design iteration
update_restart_file = False

# total number of design iterations. 
number_of_design_iterations = 0

configMaster="sudo.cfg"
meshName="sudo_coarse_FFD.su2"

# inlet BC file, needs to be copied
inletName="inlet.dat"
restartAdjName="solution_adj_dp.csv"

configCopy = "config.cfg"
# first, copy sudo.cfg to a copy config.cfg that is allowed to be altered.
copy_command = ['cp', configMaster, configCopy]
subprocess.run(copy_command)

# Design variables ----------------------------------------------------- #

# important, this has to match the nr of variables
# 6 x 6 x 6 = 216
# x,y,z = 648
NDIM = 3
DX = 6
nDV = DX * DX * DX * NDIM

# define the objective
objective = 'Surface_Pressure_Drop'

# start the time!
start = timer()

#
# Note that the last two numbers are the bounds, reduce if you want to limit the maximum deformation 
#########################################################################################################
ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -0.10,0.10)
#########################################################################################################


# ##### create string for DV_KIND ##### #
s = "FFD_CONTROL_POINT"
ffd_string = s
for i in range((DX**NDIM)*NDIM - 1):
  ffd_string = ffd_string + ", " + s 


# ##### create string for DV_PARAM ##### #
dv_param_string=""
for idim in range(NDIM):
  xdim = ydim = zdim = "0.0"
  if (idim==0): xdim="1.0"
  elif (idim==1): ydim="1.0"
  elif (idim==2): zdim="1.0"
  for k in range(DX):
    for j in range(DX):
      for i in range(DX):
        s = "( BOX, " + str(i) + ", " + str(j) + ", " + str(k) + ", " + xdim + ", " + ydim + ", " + zdim + " );"
        dv_param_string += s
# remove last semicolon
dv_param_string = dv_param_string[:-1]


# do not move FFD box nodes in vertical direction (bottom face with j=0 only )
# we remove 6*6=36 d.o.f.
nDV = nDV - 2*DX*DX
ffd_string.replace(s+", ","",2*DX*DX)


# for bottom planes j=0 and j=1 remove the entries that have (0.0, 1.0, 0.0) d.o.f. (the vertical direction)
jlist = [0,1]
dof = "0.0, 1.0, 0.0"

for j in jlist:
  for k in range(DX):
    for i in range(DX):
      remove_dof = "( BOX, " + str(i) + ", " + str(j) + ", " + str(k) + ", " + dof + " )"
      print("removing ", remove_dof)
      dv_param_string = dv_param_string.replace(remove_dof+";", "", 1)
      # in case the plane is at the end, the string does not have a semicolon
      dv_param_string = dv_param_string.replace(remove_dof, "", 1)


replace_dv_kind = Parameter([ffd_string], LabelReplacer("__FFD_CTRL_PTS__"))
replace_dv_param =Parameter([dv_param_string], LabelReplacer("__FFD_PARAM__"))

ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -0.10,0.10)

# Parameters ----------------------------------------------------------- #

# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))

enable_not_def = Parameter([""], LabelReplacer("%__NOT_DEF__"))
enable_def = Parameter([""], LabelReplacer("%__DEF__"))

# Switch Objective Functions
if objective == 'Uniformity':
    print("1. set parameter for Uniformity")
    enable_obj = Parameter(["SURFACE_UNIFORMITY"], LabelReplacer("__OBJ_FUNC__"))
    objstring="uniformity"

elif objective == 'Surface_Pressure_Drop':
    print("1. set parameter for Surface_Pressure_Drop")
    enable_obj = Parameter(["SURFACE_PRESSURE_DROP"], LabelReplacer("__OBJ_FUNC__"))
    objstring = "dp"

else:
    raise Exception("no valid objective found.")



print(" ")
print("Running validation for", objective)

# after the first iteration, we switch from restart=no to restart=yes, then update original cfg file
restart_yes="sed -i 's/RESTART_SOL= NO/RESTART_SOL= YES/' config.cfg && cp " + configCopy + " ../../"

# Evaluations ---------------------------------------------------------- #

def_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_DEF " + configCopy

if update_restart_file == True:
  cfd_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_CFD " + configCopy  + " && cp restart.csv ../../solution.csv"
  cfd_ad_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_CFD_AD " + configCopy + " && cp restart_adj_" + objstring + ".csv ../../solution_adj_"+objstring+".csv"
else :
  cfd_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_CFD " + configCopy  
  cfd_ad_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_CFD_AD " + configCopy 

dot_ad_command = "mpirun --allow-run-as-root -n " + ncores + " " + su2_run + "SU2_DOT_AD " + configCopy

max_tries = 1

#####################################################################
# mesh deformation, running in subdirectory DEFORM
#####################################################################
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configCopy)
deform.addData(meshName)
deform.addData(inletName)
deform.addExpected("mesh_out.su2")
deform.addParameter(replace_dv_kind)
deform.addParameter(replace_dv_param)
deform.addParameter(enable_def)
deform.addParameter(enable_obj)

#####################################################################
# direct run, running in subdirectory DIRECT
#####################################################################
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configCopy)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addData(inletName)
direct.addData("solution.csv")
direct.addExpected("restart.csv")
direct.addParameter(replace_dv_kind)
direct.addParameter(replace_dv_param)
direct.addParameter(enable_direct)
direct.addParameter(enable_not_def)
direct.addParameter(enable_obj)

#####################################################################
# adjoint run, running in subdorectory ADJOINT
#####################################################################
adjoint = ExternalRun("ADJOINT",cfd_ad_command,True)
adjoint.setMaxTries(max_tries)
adjoint.addConfig(configCopy)
adjoint.addData("DEFORM/mesh_out.su2", destination=meshName)
adjoint.addData(inletName)
adjoint.addData(restartAdjName)
# add primal solution file
adjoint.addData("DIRECT/restart.csv", destination="solution.csv")
adjoint.addParameter(replace_dv_kind)
adjoint.addParameter(replace_dv_param)

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

#####################################################################
# gradient projection, running in subdirectory DOT
#####################################################################
dot = ExternalRun("DOT",dot_ad_command,True)
dot.setMaxTries(max_tries)
dot.addConfig(configCopy)
dot.addData("DEFORM/mesh_out.su2", destination=meshName)
dot.addData(inletName)
dot.addParameter(replace_dv_kind)
dot.addParameter(replace_dv_param)
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

#####################################################################
# update restart file
#####################################################################
update_restart = ExternalRun("UPDATE_RESTART",restart_yes,False) # True means sym links are used for addData
update_restart.addData(configCopy)

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
if update_restart_file == True:
  func_surfdp.addGradientEvalStep(update_restart)
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

# Define the filename containing the objective values per design iteration
his = open("optim.csv","w",1)
driver.setHistorian(his)

# Optimization, SciPy -------------------------------------------------- #

import scipy.optimize

driver.preprocess()
x = driver.getInitial()

# disp:True prints convergence messages
# maxiter: number of (true) design iterations that will be run 
# ftol: precision tolerance goal for the value of f in the stopping criterion
options = {'disp': True, 'ftol': 1e-10, 'maxiter': number_of_design_iterations}

# Use Sequential Least Squares Programming SLSQP
optimum = scipy.optimize.minimize(driver.fun, x, method="SLSQP", jac=driver.grad,\
          constraints=driver.getConstraints(), bounds=driver.getBounds(), options=options)

print(" | Closing...")
his.close()

print(" +--- Finished")

end = timer()
print("total time: ",end-start," seconds, ",(end-start)/60.0," minutes.")
