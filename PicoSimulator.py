import matplotlib
from ambiance import Atmosphere
import matplotlib.pyplot as plt
import math
import numpy as np
import time
R = 8.314472 #ideal gas constant
mwAtmo = 28.013e-3 #kg/mol

class Balloon:
    def __init__(self,volume,mass,molWeightLiftingGas,mols,burstPressure):
        self.volume = volume
        self.mass = mass
        self.mw = molWeightLiftingGas
        self.mols = mols
        self.burstPressure = burstPressure


balloon = Balloon(0.281156,47e-3+37e-3,4.002602e-3,3.81438441,3000)

endTime = 50000 #seconds
timeStep = 1 #second

t=[0]
burstTime = 0
altitude = [0]
atmo = Atmosphere(altitude[-1])
velocity = [0]
acceleration = [0.02]
pressure = [atmo.pressure[0]]
volume = [balloon.mols*R*atmo.temperature[0]/atmo.pressure[0]]
burst = False

while t[-1] < endTime and altitude[-1]>-1:
    
    timeStep = 0.2
    if abs(acceleration[-1])<0.001:
        timeStep = 3
    

    atmo = Atmosphere(altitude[-1])

    if not burst:
        volume.append((balloon.mols*R*atmo.temperature[0])/atmo.pressure[0])
    else:
        volume.append(0)

    if volume[-1]>balloon.volume:
        volume[-1] = balloon.volume
        pressure.append((balloon.mols*R*atmo.temperature[0]/balloon.volume))
    else:
        pressure.append(atmo.pressure[0])

    if pressure[-1]-atmo.pressure[0]>balloon.burstPressure:
        volume[-1] = 0
        if burstTime == 0:
            burstTime = t[-1]
            burst = True
    
    drag = 0.8*0.5* atmo.density[0]*velocity[-1]**2*(volume[-1]*0.75/math.pi)**(1/3)
    Force = volume[-1]*atmo.density[0] - balloon.mols*balloon.mw - balloon.mass - drag
    if burst:
        drag = 0.8*0.5* atmo.density[0]*velocity[-1]**2*(0.01*0.75/math.pi)**(1/3)
        Force = 0-balloon.mass-drag
    
    
    acceleration.append(Force/balloon.mass)
    
    velocity.append(velocity[-1]+acceleration[-1]*timeStep)
    
    altitude.append(altitude[-1]+velocity[-1]*timeStep)
    
    t.append(t[-1]+timeStep)
    
    '''
    print("Volume:",volume[-1])
    print("Force:",Force)
    print("Acc",acceleration[-1])
    print("Vel:",velocity[-1])
    print("Alt:",altitude[-1])
    '''
print("Balloon Pop:",burst)
fig, axs = plt.subplots(4,1)
axs[0].plot(t,altitude)
axs[0].set_xlabel("Time [s]")
axs[0].set_ylabel("Altitude [m]")

axs[1].plot(t,pressure)
axs[1].plot(t,Atmosphere(altitude).pressure)
axs[1].set_xlabel("Time [s]")
axs[1].set_ylabel("Pressure [Pa]")


axs[2].plot(t,velocity)
axs[2].set_xlabel("Time [s]")
axs[2].set_ylabel("Velocity [m/s]")


axs[3].plot(t,acceleration)
axs[3].set_xlabel("Time [s]")
axs[3].set_ylabel("Acceleration [m/s/s]")

plt.show()