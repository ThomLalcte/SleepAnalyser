import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

p=[6.31,6.25,6.14,5.87,6.17,6.44,6.23,6.38,6.57,6.33,6.07,5.64]
x=sum(p)/len(p)
print(x)
fart=0
for i in p:
    fart+=(i-x)**2
print((fart/(len(p)-1))**0.5)
