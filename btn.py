import tkinter as tk
from tkinter import ttk
from tkinter import *
import numpy as np
import math as mth
import matplotlib.pyplot as plt
from random import randrange
from scipy.signal import butter, lfilter, hilbert

def rndm():
    canvas = tk.Canvas(width=400, height=300, bg='blue')
    canvas.place(x=10, y=10)
    # Координаты гидролокатора
    x1_gidr = 195
    x2_gidr = 205
    y1_gidr = 145
    y2_gidr = 155
    canvas.create_oval([x1_gidr, y1_gidr], [x2_gidr, y2_gidr], fill='green')

    TargetR_x = randrange(-100,100,10)
    TargetR_y = randrange(-50,50,10)
    x1_tar = (x1_gidr + TargetR_x)
    y1_tar = (y1_gidr - TargetR_y)
    x2_tar = (x2_gidr + TargetR_x)
    y2_tar = (y2_gidr - TargetR_y)

    net=randrange(1,3,1)
    if net == 1:
        canvas.create_rectangle(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'red')
    elif net == 2:
        canvas.create_oval(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'black')
    elif net == 3:
        canvas.create_oval(x1_tar, y1_tar, x2_tar, y2_tar, fill = 'yellow')

