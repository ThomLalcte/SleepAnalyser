import matplotlib.pyplot as plt
import matplotlib.dates as pltd
import socket
import datetime as dt
import locale

meanHighValue = 1276000
meanLowValue = 1160574
threshold = int(meanLowValue+(meanHighValue-meanLowValue)/2)

def getData(hourmin: int, hourend: int, date: dt.date, dateDelta: int):
    """poll data from hourmin to hourend of the day specified by date to said day minus dateDelta day before"""
    data:list[list[int]] = []
    time:list[list[dt.datetime]] = []
    server = socket.create_connection(("192.168.0.139",10000))
    server.send(b"slepdata")
    if server.recv(2) == b"ok":
        server.send((date.strftime("%Y-%m-%d")).encode("utf-8"))
        server.send(int.to_bytes(dateDelta,1,"big",signed=False))
        server.send(int.to_bytes(hourmin,1,"big",signed=True))
        server.send(int.to_bytes(hourend,1,"big",signed=True))
        for i in range(dateDelta):
            data.append([])
            time.append([])
            for ii in range(hourmin,hourend):
                for iii in range(20):
                    if ii<0:
                        time[i].append(dt.datetime.combine(date,dt.time(hour=24+ii,minute=iii*3))-dt.timedelta(1+i))
                    else:
                        time[i].append(dt.datetime.combine(date,dt.time(hour=ii,minute=iii*3))-dt.timedelta(i))
                    data[i].append(abs(int.from_bytes(server.recv(4),"big",signed=True)))
    else:
        raise Exception("Server did not responded with 'ok'")
    return data, time

def getStamps(date: dt.date, dateDelta: int):
    stamps:dict[str,list[dt.datetime]] = {}
    server = socket.create_connection(("192.168.0.139",10000))
    server.send(b"slepstamps")
    if server.recv(2) == b"ok":
        server.send((date.strftime("%Y-%m-%d")).encode("utf-8"))
        server.send(int.to_bytes(dateDelta,1,"big",signed=False))
        toa:str
        tod:str
        for i in range(dateDelta):
            toa=server.recv(5).decode("utf-8")
            if toa=="error" or toa=="":
                print((date-dt.timedelta(i)).strftime("%Y-%m-%d")+" has no usefull data")
                continue
            if toa=="keyer":
                server.recv(3)
                print((date-dt.timedelta(i)).strftime("%Y-%m-%d")+" is not catalogued")
                continue
            tod=server.recv(5).decode("utf-8")
            stamps.update({(date-dt.timedelta(i)).strftime("%Y-%m-%d"):[dt.datetime.combine(date-dt.timedelta(i),dt.time(hour=int(toa[0:2]),minute=int(toa[3:6]))),dt.datetime.combine(date-dt.timedelta(i),dt.time(hour=int(tod[0:2]),minute=int(tod[3:6])))]})
    return stamps

def filterData(unfiltered:list[list[int]], var:int=5):
    gaus=[]
    width=5*var
    for i in range(-width,width+1):
        gaus.append(2.71828**(-(i**2/(2*var**2)))/(var*(2*3.1415)**0.5))
    filtered = []
    for i in range(width):
        unfiltered.insert(0,unfiltered[0])
        unfiltered.append(unfiltered[-1])
    for i in range(width,len(unfiltered)-width):
        ng=len(gaus)
        tot=0
        for ii in range(ng):
            tot+=gaus[ii]*unfiltered[i+ii-round((ng-1)/2)]
        filtered.append(tot)
    return filtered

def derivDataOffset(underived:list[list[int]]):
    derived=[]
    underived.append(underived[-1])
    for i in range(len(underived)-1):
        derived.append(underived[i+1]-underived[i]+threshold)
    del underived[-1]
    return derived

def derivData(underived:list[list[int]]):
    derived=[]
    underived.append(underived[-1])
    for i in range(len(underived)-1):
        derived.append(underived[i+1]-underived[i])
    del underived[-1]
    return derived

def meanData(data:list[int]):
    return sum(data)/len(data)

def isThomInBed(sample:int):
    return sample<threshold

def isThomInBedServer():
    server = socket.create_connection(("192.168.0.139",10000))
    server.send(b"isThomInBed")
    if server.recv(2)==b"ok":
        return int.from_bytes(server.recv(1),"big")

def plotSingleDay(date:dt.date=dt.date.today(), hourmin: int=-1, hourend: int=14):
    if date==dt.date.today():
        data, time = getData(hourmin,min(hourend,dt.datetime.now().hour),date,1)
    else:
        data, time = getData(hourmin,hourend,date,1)
    locale.setlocale(locale.LC_TIME,"fr_CA")
    for i in range(len(data)):
        if min(data[i])<10 or max(list(map(abs,derivData(filterData(data[i][:])))))<1000:
            print("Error: Selected day has no meaningfull data")
            return
        plt.plot(time[0],derivDataOffset(filterData(data[i][:])),label=time[i][-1].strftime("%a %m-%d")+" deriv")
        plt.plot(time[0],filterData(data[i][:]),label=time[i][-1].strftime("%a %m-%d")+" filtered")
        plt.plot(time[0],data[i],label=time[i][-1].strftime("%a %m-%d")+" raw")
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()
    plt.show()

def plotMultipleDays(date:dt.date=dt.date.today(), nbDays: int=7):
    if date==dt.date.today():
        data, time = getData(-1,min(14,dt.datetime.now().hour),date,nbDays)
    else:
        data, time = getData(-1,14,date,nbDays)

    locale.setlocale(locale.LC_TIME,"fr_CA")
    for i in range(len(data)):
        if min(data[i])<10 or max(list(map(abs,derivData(filterData(data[i][:])))))<1000:
            print(time[i][-1].strftime("%a %m-%d")+" has no meaningfull data")
            continue
        plt.plot(time[0],filterData(data[i][:]),label=time[i][-1].strftime("%a %m-%d"))
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()
    plt.show()

def plotTimestamps(date:dt.date=dt.date.today(), nbDays: int=7):
    """TODO mettre les marqueurs de semaine à chaque dimanche seulement"""
    stamps = getStamps(date,nbDays)
    for i in stamps:
        plt.bar(dt.datetime.strptime(i,"%Y-%m-%d"),stamps[i][1]-stamps[i][0],0.1,bottom=stamps[i][0].replace(day=dt.datetime.now().day,month=dt.datetime.now().month,year=dt.datetime.now().year),label=i,zorder=10)
    locale.setlocale(locale.LC_TIME,"fr_CA")
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter("%a %m-%d"))#"%Y-%m-%d"))
    plt.gca().yaxis.set_major_formatter(pltd.DateFormatter("%H:%M"))
    for i in range(0,nbDays+2,7):
        plt.axvline(dt.date.today()-dt.timedelta(i,hours=12),color="0.1")
    plt.ylim([dt.datetime.now().replace(hour=23,minute=0)-dt.timedelta(1), dt.datetime.now().replace(hour=14,minute=0)])
    plt.xlim([dt.date.today()-dt.timedelta(nbDays+1),dt.date.today()+dt.timedelta(1)])
    plt.grid(axis='x', color='0.7')
    plt.show()

def getMeanSlep(stamps:dict[str,list[dt.datetime]]):
    summ:int=0
    i:dt.datetime
    for i in stamps:
        summ+=(stamps[i][1]-stamps[i][0]).total_seconds()
    raw:float=summ/len(stamps)/60/60
    return dt.timedelta(hours=int(raw),minutes=int(raw%1*60),seconds=int(raw%1*60%1*60))

#TODO graphique de la qte heures de sommeil/jour
#TODO graphique de la variance des toa/tod

print(getMeanSlep(getStamps(dt.date.today(),30)))
# plotMultipleDays(dt.date.today()-dt.timedelta(0),7)
# plotSingleDay(dt.date.today()-dt.timedelta(0))
plotTimestamps(nbDays=16)