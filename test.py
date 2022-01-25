import numpy as np
import datetime as dt
import matplotlib.dates as pltd
import matplotlib.pyplot as plt
import SleepAnalyser as sa
import locale

print(sa.nextMustBeAwake().strftime("%H:%M"))
print(sa.InbedSince())
toi = dt.date.today()-dt.timedelta(0)
toa = -2
tod = 14
# print(getMeanSlep(getStamps(dt.date.today(),28)))
# plotMultipleDays(dt.date.today()-dt.timedelta(0),14,type="capp")
# sa.plotSingleDay(dt.date.today()-dt.timedelta(0))
# plotTimestamps(nbDays=7)
# plotSlepAmount(nbDays=21)
# synchronousnPlot(date=dt.date.today()-dt.timedelta(1), nbDays=14, mode="tod")
# sa.plotData(dt.date.today(),-12,2,"capp")
# sa.plotData(toi,toa,tod,"capp")
# sa.plotData(toi,-2,12,"wigg")

# sa.plotMultipleDays(dt.date.today()-dt.timedelta(0),nbDays=7,type="wigg")
# sa.plotMultipleDays(dt.date.today()-dt.timedelta(0),nbDays=7,type="capp")

type="capp"
toa=1
tod=14
var=5
nbdays=3
cdata, time = sa.getSleepData(toa,tod,dt.date.today(),nbdays,type)
locale.setlocale(locale.LC_TIME,"fr_CA")
# plt.plot(time[0],cdata[0],label=time[0][-1].strftime("%a %m-%d")+" "+type)
# plt.plot(time[0],sa.filterData(cdata[0][:]),label=time[0][-1].strftime("%a %m-%d")+" deriv "+type)
# plt.plot(time[0],sa.derivData(sa.filterData(cdata[0][:])),label=time[0][-1].strftime("%a %m-%d")+" deriv "+type)

type="wigg"
var=2
wdata, time = sa.getSleepData(toa,tod,dt.date.today(),nbdays,type)
# plt.plot(time[0],wdata[0],label=time[0][-1].strftime("%a %m-%d")+" "+type)
# plt.plot(time[0],sa.filterData(wdata[0][:],var),label=time[0][-1].strftime("%a %m-%d")+" "+type)
# plt.plot(time[0],sa.derivData(sa.filterData(wdata[0][:],var)),label=time[0][-1].strftime("%a %m-%d")+" "+type)
for i in wdata:
    plt.plot(time[0],sa.filterData(i[:],var),label=time[0][-1].strftime("%a %m-%d")+" "+type)


plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
plt.legend()
plt.show()