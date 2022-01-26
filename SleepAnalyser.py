import datetime as dt
import locale
import socket

import matplotlib.dates as pltd
import matplotlib.pyplot as plt
import json as js

meanHighValue = 1276000
meanLowValue = 1160574
threshold = int(meanLowValue+(meanHighValue-meanLowValue)/2)
meanSlep = dt.timedelta(hours=8,minutes=16,seconds=45)
address=("localhost",10000)
# address=("192.168.0.139",10000)


def getSleepData(hourmin: int, hourend: int, date: dt.date, dateDelta: int, type:str):
    """poll data from hourmin to hourend of the day specified by date to said day minus dateDelta day before"""
    data:list[list[int]] = []
    time:list[list[dt.datetime]] = []
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(address)
    server.send(b"data")
    if server.recv(2) == b"ok":
        server.send(type.encode("utf-8"))
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
                    sample=int.from_bytes(server.recv(4),"big",signed=True)
                    data[i].append(sample)
                if min(data[i])<-1:
                    print("{}: server encoutered error {} at {}:{}h".format("getSleepData",min(data[i]),ii,i))
                    server.close()
                    return data, time
                    
    else:
        raise Exception("Server did not responded with 'ok'")
    server.close()
    return data, time

def getStamps(date: dt.date, dateDelta: int):
    stamps:dict[str,list[dt.datetime]] = {}
    server = socket.create_connection(address)
    server.send(b"slepstamps")
    if server.recv(2) == b"ok":
        server.send((date.strftime("%Y-%m-%d")).encode("utf-8"))
        server.send(int.to_bytes(dateDelta,1,"big",signed=False))
        toa:str
        tod:str
        for i in range(dateDelta):
            toas=server.recv(5).decode("utf-8")
            datestr=(date-dt.timedelta(i)).strftime("%Y-%m-%d")
            if toas=="error" or toas=="":
                print("getStamps: "+ datestr+" has errors in it's data")
                continue
            elif toas=="keyer":
                print("getStamps: "+ datestr+" is not catalogued")
                continue
            elif toas=="inder":
                print("getStamps: "+ datestr+" index error was caught at the server side")
                continue
            elif toas=="inslp":
                print("getStamps: "+ datestr+" sleep pattern is invalid: see slep_timestamps_data.json for details")
                continue
            tods=server.recv(5).decode("utf-8")
            toa=dt.datetime.now().replace(hour=int(toas[0:2]),minute=int(toas[3:6]))
            tod=dt.datetime.now().replace(hour=int(tods[0:2]),minute=int(tods[3:6]))
            if tod<toa:
                toa=toa-dt.timedelta(1)
            stamps.update({datestr:[toa,tod]})
    return stamps

def filterData(unfiltered:list[int], var:int=5):
    if type(unfiltered[0])!=int and type(unfiltered[0])!=float:
        raise TypeError("content of unfiltered isn't of type int or float but instead of type {}".format(type(unfiltered[0])))
    gaus=[]
    width=round(5*var)
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

def derivDataOffset(underived:list[int]):
    if type(underived[0])!=int and type(underived[0])!=float:
        raise TypeError("content of unfiltered isn't of type int or float but instead of type {}".format(type(underived[0])))

    derived=[]
    underived.append(underived[-1])
    for i in range(len(underived)-1):
        derived.append(underived[i+1]-underived[i]+threshold)
    del underived[-1]
    return derived

def derivData(underived:list[int]):
    if type(underived[0])!=int and type(underived[0])!=float:
        raise TypeError("content of unfiltered isn't of type int or float but instead of type {}".format(type(underived[0])))
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
    server = socket.create_connection(address)
    server.send(b"isThomInBed")
    if server.recv(2)==b"ok":
        return int.from_bytes(server.recv(1),"big")

def plotSingleDay(date:dt.date=dt.date.today(), hourmin: int=-1, hourend: int=14):
    if date==dt.date.today():
        wdata, time = getSleepData(hourmin,min(hourend,dt.datetime.now().hour),date,1,"wigg")
        cdata, time = getSleepData(hourmin,min(hourend,dt.datetime.now().hour),date,1,"capp")
    else:
        wdata, time = getSleepData(hourmin,hourend,date,1,"wigg")
        cdata, time = getSleepData(hourmin,hourend,date,1,"capp")
    locale.setlocale(locale.LC_TIME,"fr_CA")
    if min(cdata[0])<10:
        print("plotSingleDay: Selected day has <10 values")
        # return
    if max(list(map(abs,derivData(filterData(cdata[0][:])))))<1000:
        print("plotSingleDay: Selected day has no significant deriv")
        # return
    # maen = meanData(cdata[0][int(len(cdata[0])/3):int(2*len(cdata[0])/3)])
    for i in range(len(wdata[0])):
        wdata[0][i]+=threshold
    plt.plot(time[0],filterData(cdata[0][:]),label=time[0][-1].strftime("%a %m-%d")+" cap filtered")
    plt.plot(time[0],derivDataOffset(filterData(cdata[0][:])),label=time[0][-1].strftime("%a %m-%d")+" cap deriv")
    plt.plot(time[0],cdata[0],label=time[0][-1].strftime("%a %m-%d")+" cap raw")
    plt.plot(time[0],wdata[0],label=time[0][-1].strftime("%a %m-%d")+" wiggle raw")
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()

def plotMultipleDays(date:dt.date=dt.date.today(), nbDays: int=7, type:str="capp"):
    if date==dt.date.today():
        data, time = getSleepData(-1,min(14,dt.datetime.now().hour),date,nbDays,type)
    else:
        data, time = getSleepData(-1,14,date,nbDays,type)

    locale.setlocale(locale.LC_TIME,"fr_CA")
    for i in range(len(data)):
        if min(data[i])<0 and type=="capp":
            print("plotMultipleDays: "+ time[i][-1].strftime("%a %m-%d")+" has errors")
            continue
        if max(list(map(abs,derivData(filterData(data[i][:])))))<1000 and type=="capp":
            print("plotMultipleDays: "+ time[i][-1].strftime("%a %m-%d")+" has no meaningfull data")
            continue
        if type=="capp":
            plt.plot(time[0][:len(data[i])],filterData(data[i][:]),label=time[i][-1].strftime("%a %m-%d"))
        else:
            plt.plot(time[0][:len(data[i])],filterData(data[i][:]),label=time[i][-1].strftime("%a %m-%d"))
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()

def plotTimestamps(date:dt.date=dt.date.today(), nbDays: int=7):
    stamps = getStamps(date,nbDays)
    for i in stamps:
        plt.bar(dt.datetime.strptime(i,"%Y-%m-%d"),stamps[i][1]-stamps[i][0],0.1,bottom=stamps[i][0],label=i,zorder=10)
    locale.setlocale(locale.LC_TIME,"fr_CA")
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter("%a %m-%d"))#"%Y-%m-%d"))
    plt.gca().yaxis.set_major_formatter(pltd.DateFormatter("%H:%M"))
    for i in range(0,nbDays+2):
        if (dt.date.today()-dt.timedelta(i,hours=12)).weekday()==6:
            plt.axvline(dt.date.today()-dt.timedelta(i,hours=12),color="0.1")
    plt.ylim([dt.datetime.now().replace(hour=23,minute=0)-dt.timedelta(1), dt.datetime.now().replace(hour=14,minute=0)])
    plt.xlim([dt.date.today()-dt.timedelta(nbDays+1),dt.date.today()+dt.timedelta(1)])
    plt.grid(axis='x', color='0.7')

def getMeanSlep(stamps:dict[str,list[dt.datetime]]):
    summ:int=0
    i:dt.datetime
    for i in stamps:
        summ+=(stamps[i][1]-stamps[i][0]).total_seconds()
    raw:float=summ/len(stamps)/60/60
    return dt.timedelta(hours=int(raw),minutes=int(raw%1*60),seconds=int(raw%1*60%1*60))

def getSlepDuration(stamps:dict[str,list[dt.datetime]]):
    data:list[float]=[]
    time:list[list[dt.datetime]] = []
    i:dt.datetime
    for i in stamps:
        data+=[(stamps[i][1]-stamps[i][0]).total_seconds()/60/60]
        time+=[dt.datetime.strptime(i,"%Y-%m-%d")]
    return data,time

def plotSlepAmount(date:dt.date=dt.date.today(), nbDays: int=7):
    sstamp = getStamps(date,nbDays)
    data, time = getSlepDuration(sstamp)
    plt.plot(time,data,"o-")
    plt.plot(time,filterData(data,1),"o-")
    plt.axhline(meanSlep.total_seconds()/60/60,color="0.5")
    for i in range(0,nbDays+2):
        if (dt.date.today()-dt.timedelta(i,hours=12)).weekday()==6:
            plt.axvline(dt.date.today()-dt.timedelta(i,hours=12),color="0.1")
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter("%a %m-%d"))#"%Y-%m-%d"))
    plt.ylim([0,12])
    plt.grid(axis='x', color='0.7')

def synchronousnPlot(date:dt.date=dt.date.today(), nbDays: int=7, mode:str="toa", type:str="capp", var:int=8):
    if date==dt.date.today() and dt.datetime.now().hour<8:
        data, time = getSleepData(-1,14,date-dt.timedelta(1),nbDays,type)
        stamps = getStamps(date-dt.timedelta(1),nbDays)
    elif date==dt.date.today():
        data, time = getSleepData(-1,min(14,dt.datetime.now().hour),date,nbDays,type)
        stamps = getStamps(date,nbDays)
    else:
        data, time = getSleepData(-1,14,date,nbDays,type)
        stamps = getStamps(date,nbDays)
    to:list[int]=[]
    toDel=[]
    if type=="capp":
        for i in data:
            if min(i)<10:
                print(time[data.index(i)][i.index(min(i))],"<10 ->",min(i)," in ",data.index(i)," at ",i.index(min(i)))
                print(time[data.index(i)][-1],"<10")
                toDel+=[data.index(i)]
            elif max(list(map(abs,derivData(filterData(i[:])))))<5000:
                print(time[data.index(i)][-1],"deriv<1000")
                toDel+=[data.index(i)]
        toDel.reverse()
        for i in toDel:
            del time[i]
            del data[i]
    for i in data:
        deriv=derivData(filterData(i[:]))
        if mode=="toa":
            to+=[deriv.index(min(deriv))]
        if mode=="tod":
            to+=[deriv.index(max(deriv))+3]
    #TODO remplacer ça par l'utilistion des stamps

    locale.setlocale(locale.LC_TIME,"fr_CA")
    for i in range(len(data)):
        if mode=="toa":
            plt.plot(time[0][:len(time[0])-to[i]],filterData(data[i][to[i]:],var),label=time[i][-1].strftime("%a %m-%d"))
        if mode=="tod":
            plt.plot(time[0][len(time[0])-to[i]:],filterData(data[i][:to[i]],var),label=time[i][-1].strftime("%a %m-%d"))
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.xlim([time[0][0]-dt.timedelta(hours=2),time[0][-1]+dt.timedelta(hours=2)])
    plt.legend()
    
def debugData(hourmin: int=-1, hourend: int=min(14,dt.datetime.now().hour), date: dt.date=dt.date.today(), dateDelta: int=14):
    data, time = getSleepData(-1,min(14,dt.datetime.now().hour),dt.date.today()-dt.timedelta(9),14,"capp")
    for i in data:
        if min(i)<10:
            print(time[data.index(i)][i.index(min(i))],"<10 ->",min(i)," in ",data.index(i)," at ",i.index(min(i)))
        if max(list(map(abs,derivData(filterData(i[:])))))<1000:
            print(time[data.index(i)][-1],"deriv<1000")

def plotData(date:dt.date, hourmin: int, hourend: int, type:str):
    data, time = getSleepData(hourmin,hourend,date,1,type)
    locale.setlocale(locale.LC_TIME,"fr_CA")
    plt.plot(time[0],data[0],label=time[0][-1].strftime("%a %m-%d")+" "+type)
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()

def InbedSince():
    cdata, time = getSleepData(-4,min(14,dt.datetime.now().hour),dt.date.today(),1,"capp")
    ddata = derivData(filterData(cdata[0][:]))
    minddata = min(ddata)
    if minddata >= -5000:
        print("Probably not sleeping right now") 
    return time[0][ddata.index(minddata)]

def nextMustBeAwake():
    with open("WakeSchedule.json","r") as file:
        filedata:dict = js.load(file)
        file.close()
    jourSem = dt.date.today().weekday()
    heure = filedata[jourSem.__str__()][0]
    return dt.datetime.now().replace(hour=int(heure),minute=heure%1*60)


#TODO graphique de la variance des toa/tod
#TODO score de sommeil basé sur la variance du signal durant la nuit
