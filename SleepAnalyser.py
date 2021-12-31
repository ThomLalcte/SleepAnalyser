import matplotlib.pyplot as plt
import matplotlib.dates as pltd
import socket
import datetime as dt
import locale

meanHighValue = 1276000
meanLowValue = 1160574
threshold = int(meanLowValue+(meanHighValue-meanLowValue)/2)
meanSlep = dt.timedelta(hours=8,minutes=16,seconds=45)

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
                    sample=int.from_bytes(server.recv(4),"big",signed=True)
                    data[i].append(abs(sample))
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
            toas=server.recv(5).decode("utf-8")
            datestr=(date-dt.timedelta(i)).strftime("%Y-%m-%d")
            if toas=="error" or toas=="":
                print(datestr+" has errors in it's data")
                continue
            elif toas=="keyer":
                print(datestr+" is not catalogued")
                continue
            elif toas=="inder":
                print(datestr+" index error was caught at the server side")
                continue
            elif toas=="inslp":
                print(datestr+" sleep pattern is invalid: see slep_timestamps_data.json for details")
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
        if min(data[i])<10:
            print("Error: Selected day has <10 values")
            return
        if max(list(map(abs,derivData(filterData(data[i][:])))))<1000:
            print("Error: Selected day has no significant deriv")
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
        if min(data[i])==1:
            print(time[i][-1].strftime("%a %m-%d")+" has errors")
            continue
        if max(list(map(abs,derivData(filterData(data[i][:])))))<1000:
            print(time[i][-1].strftime("%a %m-%d")+" has no meaningfull data")
            continue
        plt.plot(time[0],filterData(data[i][:]),label=time[i][-1].strftime("%a %m-%d"))
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.legend()
    plt.show()

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
    # plt.legend()
    plt.show()

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
    plt.show()

def synchronousnPlot(date:dt.date=dt.date.today(), nbDays: int=7, mode:str="toa"):
    if date==dt.date.today():
        data, time = getData(-1,min(14,dt.datetime.now().hour),date,nbDays)
    else:
        data, time = getData(-1,14,date,nbDays)
    to:list[int]=[]
    toDel=[]
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

    locale.setlocale(locale.LC_TIME,"fr_CA")
    for i in range(len(data)):
        if mode=="toa":
            plt.plot(time[0][:len(time[0])-to[i]],filterData(data[i][to[i]:],8),label=time[i][-1].strftime("%a %m-%d"))
        if mode=="tod":
            plt.plot(time[0][len(time[0])-to[i]:],filterData(data[i][:to[i]],8),label=time[i][-1].strftime("%a %m-%d"))
    plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
    plt.xlim([time[0][0],time[0][-1]+dt.timedelta(hours=2)])
    plt.legend()
    plt.show()
    
def debugData(hourmin: int=-1, hourend: int=min(14,dt.datetime.now().hour), date: dt.date=dt.date.today(), dateDelta: int=14):
    data, time = getData(-1,min(14,dt.datetime.now().hour),dt.date.today()-dt.timedelta(9),14)
    for i in data:
        if min(i)<10:
            print(time[data.index(i)][i.index(min(i))],"<10 ->",min(i)," in ",data.index(i)," at ",i.index(min(i)))
        if max(list(map(abs,derivData(filterData(i[:])))))<1000:
            print(time[data.index(i)][-1],"deriv<1000")

def simSlepReport2(SlepSample:int, wiggleSample:int):
    server = socket.create_connection(("192.168.0.139",10000))
    server.send(b"slep2")
    print("ETA: {} seconds".format(int.from_bytes(server.recv(4),"big")))
    server.send(int.to_bytes(SlepSample,4,"big"))
    server.send(int.to_bytes(wiggleSample,4,"big"))
    server.close()


#TODO graphique de la variance des toa/tod
#TODO score de sommeil basé sur la variance du signal durant la nuit

# print(getMeanSlep(getStamps(dt.date.today(),28)))
# plotMultipleDays(dt.date.today()-dt.timedelta(0),3)
# plotSingleDay(dt.date.today()-dt.timedelta(0))
plotTimestamps(nbDays=14)
# plotSlepAmount(nbDays=21)
# synchronousnPlot(date=dt.date.today()-dt.timedelta(1), nbDays=14, mode="tod")

