import matplotlib.pyplot as plt
import matplotlib.dates as pltd
import socket
import datetime
import locale

meanHighValue = 1276000
meanLowValue = 1160574
threshold =meanLowValue+(meanHighValue-meanLowValue)/2

def getData(hourmin: int, hourend: int, date: datetime.datetime, dateDelta: int):
    data = []
    time = []
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
                        time[i].append(date.replace(hour=24+ii,minute=iii*3)-datetime.timedelta(1+i))
                    else:
                        time[i].append(date.replace(hour=ii,minute=iii*3)-datetime.timedelta(i))
                    data[i].append(abs(int.from_bytes(server.recv(4),"big",signed=True)))
    else:
        raise Exception("Server did not responded with 'ok'")
    return data, time

def filterData(unfiltered):
    gaus=[]
    var=5
    width=20
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

def derivData(underived):
    derived=[]
    underived.append(underived[-1])
    for i in range(len(underived)-1):
        derived.append(underived[i+1]-underived[i])#+threshold)
    del underived[-1]
    return derived

def meanData(data):
    return sum(data)/len(data)

def isThomInBed(sample):
    return sample<threshold

def isThomInBedServer():
    server = socket.create_connection(("192.168.0.139",10000))
    server.send(b"isThomInBed")
    if server.recv(2)==b"ok":
        return int.from_bytes(server.recv(1),"big")


data, time = getData(-4,datetime.datetime.now().hour,datetime.datetime.now(),9)

# print("most likely arrival time: {}".format(time[deriv.index(min(deriv))].strftime("%H:%M")))
# print("most likely departure time: {}".format(time[deriv.index(max(deriv))].strftime("%H:%M")))
# print("estimated time slept: {}".format((time[deriv.index(max(deriv))]-time[deriv.index(min(deriv))])))

locale.setlocale(locale.LC_TIME,"fr_CA")
for i in range(len(data)):
    if min(data[i])<10 or max(list(map(abs,derivData(filterData(data[i][:])))))<1000:
        continue
    plt.plot(time[0],(filterData(data[i][:])),label=time[i][0].strftime("%a %m-%d"))
plt.gca().xaxis.set_major_formatter(pltd.DateFormatter('%H:%M'))
plt.legend()
plt.show()