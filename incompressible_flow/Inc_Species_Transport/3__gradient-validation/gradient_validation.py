# FADO script: Finite Differences vs adjoint run

from FADO import *

# Design variables ----------------------------------------------------- #

nDV = 10
ffd = InputVariable(0.0,PreStringHandler("DV_VALUE="),nDV)

# Parameters ----------------------------------------------------------- #

# The master config `configMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))
enable_not_def = Parameter([""], LabelReplacer("%__NOT_DEF__"))
enable_def = Parameter([""], LabelReplacer("%__DEF__"))

# Switch Objective Functions
OF_SpecVar = Parameter([""], LabelReplacer("%__OF_SpecVar__"))

# Evaluations ---------------------------------------------------------- #

# Define a few often used variables
ncores="2"
configMaster="species3_primitiveVenturi.cfg"
meshName="primitiveVenturi.su2"

# Note that correct SU2 version needs to be in PATH

def_command = "SU2_DEF " + configMaster
cfd_command = "mpirun -n " + ncores + " SU2_CFD " + configMaster

cfd_ad_command = "mpirun -n " + ncores + " SU2_CFD_AD " + configMaster
dot_ad_command = "mpirun -n " + ncores + " SU2_DOT_AD " + configMaster

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addData(meshName)
deform.addExpected("mesh_out.su2")
deform.addParameter(enable_def)

# direct run
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addData("solution.csv")
direct.addExpected("restart.csv")
direct.addParameter(enable_direct)
direct.addParameter(enable_not_def)

# adjoint run
adjoint = ExternalRun("ADJOINT",cfd_ad_command,True)
adjoint.setMaxTries(max_tries)
adjoint.addConfig(configMaster)
adjoint.addData("DEFORM/mesh_out.su2", destination=meshName)
# add all primal solution files
adjoint.addData("DIRECT/restart.csv", destination="solution.csv")
adjoint.addExpected("restart_adj_specvar.csv")
adjoint.addParameter(enable_adjoint)
adjoint.addParameter(enable_not_def)
adjoint.addParameter(OF_SpecVar)

# gradient projection
dot = ExternalRun("DOT",dot_ad_command,True)
dot.setMaxTries(max_tries)
dot.addConfig(configMaster)
dot.addData("DEFORM/mesh_out.su2", destination=meshName)
dot.addData("ADJOINT/restart_adj_specvar.csv", destination="solution_adj_specvar.csv")
dot.addExpected("of_grad.csv")
dot.addParameter(enable_def)
dot.addParameter(OF_SpecVar) # necessary for correct file extension

# Functions ------------------------------------------------------------ #

specVar = Function("specVar", "DIRECT/history.csv",LabeledTableReader("\"Species_Variance\""))
specVar.addInputVariable(ffd,"DOT/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
specVar.addValueEvalStep(deform)
specVar.addValueEvalStep(direct)
specVar.addGradientEvalStep(adjoint)
specVar.addGradientEvalStep(dot)

# Driver --------------------------------------------------------------- #

# The input variable is the constraint tolerance which is not used for our purpose of finite differences
driver = ExteriorPenaltyDriver(0.005)
driver.addObjective("min", specVar)

driver.setWorkingDirectory("DOE")
driver.preprocessVariables()
driver.setStorageMode(True,"DSN_")

his = open("doe.csv","w",1)
driver.setHistorian(his)

# Simulation Runs ------------------------------------------------------ #

# Primal simulation for each deformed DV
for iLoop in range(0, nDV, 1):
    print("Computing deformed primal ", iLoop, "/", nDV-1)
    x = driver.getInitial()
    x[iLoop] = 1e-8 # DV_VALUE, FD-step
    driver.fun(x)
#end

# Undeformed/initial primal last in order to have the correct solution in
# the WorkindDirectory for the following adjoint
print("Computing baseline primal")
x = driver.getInitial()
driver.fun(x) # baseline evaluation

# Compute discrete adjoint gradient
print("Computing discrete adjoint gradient")
driver.grad(x)

his.close()

# For results run `python postprocess.py` to get screen output
# of the differences between primal and adjoint simulation.
