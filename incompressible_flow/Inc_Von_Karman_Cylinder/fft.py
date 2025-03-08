#%matplotlib inline
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.fftpack
import csv

# Return value belonging to key in config.cfg 
# (splits key= value for you)
def find_config_key_value(filename,config_key):
  with open(filename, "r") as file:
    for line in file:
        line = line.split('=')
        if line[0] == config_key:
            print(line[-1].strip() )
            return(line[-1].strip())
  raise ValueError('key not found:',config_key)

# diameter of cylinder
D = 0.01

# read history, use comma as separator, with zero or more spaces before or after 
df = pd.read_csv('history.csv', sep='\s*,\s*')

T = float(find_config_key_value('unsteady_incomp_cylinder.cfg','TIME_STEP'))
U = find_config_key_value('unsteady_incomp_cylinder.cfg','INC_VELOCITY_INIT')
N = len(df.index)
print('timestep=',T)
print('samplepoints=',N)
print('velocity=',U)
U = float(U.replace('(','').replace(')','').split(',')[0].strip())
print('velocity=',U)

# assign data 
x = df['"Cur_Time"']
y = df['"CL"']

# compute DFT with optimized FFT 
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
yf = np.fft.fft(y) 
yf2 = 2.0/N * np.abs(yf[:N//2])

#fig, ax = plt.subplots()
#plt.xlim(0,5.0)
#ax.plot(xf, yf2 )
#plt.show()


print("index of max = ",np.argmax(yf2))
freq = xf[np.argmax(yf2)]
print("frequency of max = ",freq)

St = freq * D / U
print("strouhal number = ",St)
