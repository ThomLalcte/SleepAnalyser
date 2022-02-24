from tkinter import *
import SleepAnalyser as sa
import datetime as dt

root = Tk()

def buttPlotData(date:dt.date, hourmin: int, hourend: int, type:str):
    sa.plotData(date,hourmin,hourend,type)
    sa.showPlot()

# label1 = Label(root,text="Donkey Fart Box").pack()
butt = Button(root, text="yup", command=lambda:buttPlotData(dt.date.today(),0,24,"temp"))
butt.pack()

root.mainloop()