import tkinter as tk
from tkinter import ttk
from tkinter import *
import numpy as np
import math as mth
import matplotlib.pyplot as plt
from random import randrange
sonar = tk.Tk()
sonar.title('Локатор')
sonar.geometry('700x750')


def result(peleng, Target, Dist_r):
    canvas = tk.Canvas(width=400, height=300, bg='blue')
    canvas.place(x=0, y=0)
    # Координаты гидролокатора
    x1_gidr = 195
    x2_gidr = 205
    y1_gidr = 145
    y2_gidr = 155
    canvas.create_oval([x1_gidr, y1_gidr], [x2_gidr, y2_gidr], fill='green')

    TargetR_x = np.sin(np.deg2rad(peleng)) * Dist_r/6
    TargetR_y = np.cos(np.deg2rad(peleng)) * Dist_r/6
    x1_tar = (x1_gidr + TargetR_x)
    y1_tar = (y1_gidr - TargetR_y)
    x2_tar = (x2_gidr + TargetR_x)
    y2_tar = (y2_gidr - TargetR_y)
    print(TargetR_x, TargetR_y)

    if Target == 'Пл':
        canvas.create_rectangle(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'red')
    elif Target == 'Имитатор':
        canvas.create_oval(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'blue')
    elif Target == 'Облако':
        canvas.create_oval(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'yellow')





def signal(AngleT, DistT):
    c = 1500
    M = 2
    d = 1
    m = np.arange(M-1, -1, -1)
    n = 1024# количество точек бпф
    f = 5000

    fd = 30000
    dt = 1/fd
    ts = np.arange(0, 0.02, dt) #длительность сигнала
    Tau = []
    #Создание массива массивов задержек
    Tau = np.zeros((len(DistT), len(m)))
    for i in range(len(DistT)):
        Tau2 = []
        Tau1 = np.sin(np.deg2rad(AngleT[i])) * d / c
        for j in range(len(m)):
            Tau2.append(m[j] * Tau1)
        Tau[i] = Tau2

    sig = np.zeros((len(m), len(ts)), dtype= float)
    sig = np.sin(2 * np.pi * f * ts)


    ##Формирование массива шума
    t = np.arange(0,3,dt)
    sNoise = 0.7*np.random.normal(size = t.size)  # длительность всего тракта с шумом
    SNoise = np.zeros((len(m), len(sNoise)), dtype=float)
    for i in range(len(m)):
        SNoise[i] = sNoise
    ##

    ## Нахождение первого и последнего отсчетов тракта, в которые пришли сигналы
    SigSTART = np.zeros((len(m), len(DistT)), dtype = int)
    SigEND = np.zeros((len(m), len(DistT)), dtype = int)
    for i in range(len(DistT)):
        SigSTART[0][i] = int(round(((2 * DistT[i] / c) / dt), 0))# время в момент прихода сигнала на первом элементе
        SigSTART[1][i] = SigSTART[0][i]+int(Tau[i][0]/dt)# время в момент прихода сигнала на втором элементе
        SigEND[0][i] = int(SigSTART[0][i] + ts.size - 1)# время в момент прекращения сигнала на первом элементе
        SigEND[1][i] = int(SigSTART[1][i] + ts.size - 1)# время в момент прекращения сигнала на втором элементе

    ##

    ##Формирование полного тракта с добавлением сигнала после отражения от цели
    for i in range(len(m)):
        for k in range(len(DistT)):
            a = 0
            for j in range(SigSTART[i][k], SigEND[i][k] + 1):
                SNoise[i][j] = SNoise[i][j] + sig[a]
                a = a+1

    ##
    Imp_Start = []
    Imp = np.zeros((len(m), len(t)))
    K = np.zeros(len(m))
    for j in range(len(m)):
        imp_Start = []
        ##Полосовой фильтр
        order = 6  # порядок
        nyq = 0.5 * fd  # полоса работы фильтра
        low = 4900 / nyq  # нижняя частота среза
        high = 5100 / nyq  # верхняя частота среза
        b, a = butter(order, [low, high], btype='band')  # коеф-нт фильтра
        sFilt = lfilter(b, a, SNoise[j])

        amplitudeS = np.abs(hilbert(sFilt))
        imp = np.array([])
        for i in range(0, t.size):
            if amplitudeS[i] > 0.9:
                imp = np.append(imp, 1)
            else:
                imp = np.append(imp, 0)
        Imp[j] = imp

        minUp, maxUp, k = 0, 0, 0
        arrInd = []
        for i in range(0, t.size):
            if imp[i] == 1:
                if maxUp == 0:
                    minUp = i


                if minUp != 0:
                    maxUp = i
            else:
                if (minUp != 0) and (maxUp != 0):
                    # arrInd [мин. индекс, макс. индекс, кол-во отсчетов импульса]
                    arrInd.append([minUp, maxUp, maxUp - minUp])
                    k = k + 1
                    imp_Start.append(minUp)
                    minUp = 0
                    maxUp = 0
        Imp_Start.append(imp_Start)
        K[j] = k
    ##Определение дистанции
    t_p = Imp_Start[0][0]
    Dist_r = t_p*dt*c/2

    ##Определение пеленга
    Tau_ras = (Imp_Start[1][0] - Imp_Start[0][0])*dt
    peleng = np.rad2deg(np.arcsin((SigSTART[1][0] - SigSTART[0][0])*dt*c/d))

    ##Определение типа цели
    if np.min(K)<=6 and np.max(amplitudeS)>1.5:
        Target = 'Пл'
    if np.max(amplitudeS)<1.5:
        Target = 'Имитатор'
    if np.min(K)>6 and np.max(amplitudeS)>1.5:
        Target = 'Облако'


   

    result(peleng, Target, Dist_r)


def target(TargetType, Angle, Dist):

    DistX = []
    DistX.append(0)
    DistY = []
    DistY.append(0)
    DX1 = int(float(Dist) * mth.cos(int(Angle)*np.pi/180))
    DY1 = int(float(Dist) * mth.sin(int(Angle)*np.pi/180))
    DX = []
    DY = []
    DistT = []
    AngleT = []
    if TargetType == 'Пл':
        for i in range(1, 7):
            DistX.append(DistX[i-1]+randrange(5, 15))
            DistY.append(randrange(-5, 5))
    elif TargetType == 'Имитатор':
        for i in range(1, 3):
            DistX.append(DistX[i-1]+randrange(25, 30))
            DistY.append(0)
    elif TargetType == 'Облако':
        for i in range(1, 15):
            DistX.append(randrange(-100, 100))
            DistY.append(randrange(-40, 50))

    for j in range(len(DistX)):
        DistX[j] = DistX[j]*mth.cos(int(Angle)*np.pi/180)-DistY[j]*mth.sin(int(Angle)*np.pi/180)
        DistY[j] = DistX[j]*mth.sin(int(Angle)*np.pi/180)+DistY[j]*mth.cos(int(Angle)*np.pi/180)
        DX.append(DX1 + DistX[j])
        DY.append(DY1 + DistY[j])
        DistT.append(mth.sqrt((int(DX1) + int(DistX[j]))**2+(int(DY1) + int(DistY[j]))**2))
        AngleT.append(mth.degrees(mth.atan((DY1 + DistY[j])/(DX1 + DistX[j]))))
    ###

    signal(AngleT, DistT)




def start():
    TargetType = Tbox.get()
    Angle = ugl.get()
    Dist = rast.get()
    target(TargetType, Angle, Dist)

  
ugl=IntVar()
rast=IntVar()
pole =Canvas(bg="blue", width=400, height=300)
pole.place(x=10, y=10)
label1 = ttk.Label(text="Входные данные",font=('Timews New Roman', 10, 'bold'))
label1.place(x=30, y=350)
label2 = ttk.Label(text="Результаты обработки",font=('Timews New Roman', 10, 'bold'))
label2.place(x=180, y=350)
label3=ttk.Label(text="Угол прихода")
label3.place(x=10,y=400)
label4=ttk.Label(text="Дистанция до цели")
label4.place(x=10,y=460)
label5=ttk.Label(text="Тип цели")
label5.place(x=10,y=540)
Start=Button(text = 'Старт',command = start)
Start.place(x=450, y=40)
random=Button(text = 'Случайно')
random.place(x=450, y=190)
Peleng = ttk.Entry(textvariable=ugl)
Peleng.place(x=10, y=420)
Rast = ttk.Entry(textvariable=rast)
Rast.place(x=10,y=480)

Tbox = ttk.Combobox(sonar, state = ('readonly'),values=['Пл','Имитатор','Облако'])
Tbox.place(x=10,y =560)
sonar.mainloop() 
