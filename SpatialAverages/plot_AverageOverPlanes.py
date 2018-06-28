from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

fileIn = "profile.dat"
data = pd.read_csv("profile.dat",delimiter=",",header=0)
data.rename(columns=lambda x: x.strip(' '),inplace=True)

u_tau = np.sqrt(data["tau_wall"][0]) # rho is 1

plt.semilogx(data["y+"],data["velocity_1"]/u_tau,label="mean")
plt.semilogx(data["y+"],data["velocity_ra_vol_1"]/u_tau,label="RA")
plt.xlabel("y+")
plt.ylabel("U+")
plt.legend()
plt.show()