import numpy as np
import datetime as dt
import matplotlib.dates as pltd
import matplotlib.pyplot as plt
import matplotlib.figure as fig
import SleepAnalyser as sa
import locale

# print(sa.nextMustBeAwake().strftime("%H:%M"))
# print(sa.InbedSince())
toi = dt.date.today()-dt.timedelta(0)
toa=0
tod=24
var=1
nbdays=5

type="temp"
tdata, time = sa.getSleepData(toa,tod,toi,nbdays,type)
locale.setlocale(locale.LC_TIME,"fr_CA")
for i in range(nbdays):
    for ii in range(len(tdata[i])):
        tdata[i][ii]=tdata[i][ii]*0.0078125
    plt.plot(time[0],tdata[i],label=time[i][-1].strftime("%a %m-%d")+" "+type)
    # plt.plot(time[0],sa.filterData(tdata[i][:],var=var),label=time[i][-1].strftime("%a %m-%d")+" "+type)

sa.showPlot()