import pandas as pd
#%matplotlib inline
import numpy as np
#import matplotlib.pyplot as plt
import scipy.fftpack
import csv

# diameter of cylinder
D = 0.01
# velocity
U = 0.10
# Number of samplepoints
N = 2500
# sample spacing (timestep)
T = 0.01

df = pd.read_csv('history.csv', sep='\s*,\s*', quotechar='"')

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

