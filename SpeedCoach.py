# -Importieren der Bibliotheken----------------------------------------------------------------------------------------#

import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from PyPDF2 import PdfMerger
import statistics
from scipy.interpolate import make_interp_spline
from scipy import signal
import math as m

# -Funktionen----------------------------------------------------------------------------------------------------------#


def get_sec(array):
    neu = np.ones(len(array))
    for k in range(len(array)):
        t, ms = array[k].split('.')
        h, m, s = t.split(':')
        neu[k] = float(h) * 3600 + float(m) * 60 + float(s) + float(ms)/10
    return neu


def get_sec2(value):
    neu = 0
    t, ms = value.split('.')
    h, m, s = t.split(':')
    neu = float(h) * 3600 + float(m) * 60 + float(s) + float(ms)/10
    return neu


def get_time(s):
    s = str(s)
    sec, ms = s.split('.')
    sec = float(sec)

    m = int(sec/60)
    sec = int(sec-(m*60))
    ms = ms[0]
    m = str(m)

    if sec < 10:
        sec = '0'+str(sec)
    else:
        sec = str(sec)

    time = '%s:%s.%s' % (m, sec, ms)
    return time

# -Auslese der Daten---------------------------------------------------------------------------------------------------#


def SpeedCoach(readCSV, workout):

    values = readCSV
    for i in range(0, 30):
        values = np.delete(values, 0)

    values = np.delete(values, len(values)-1)

    distance = []
    time = []
    split = []
    StrokeRate = []
    Stroke = []
    DistancePerStroke = []
    HeartRate = []

    for row in values:
        distanceR = float(row[1])
        timeR = row[3]
        splitR = row[4]
        StrokeRateR = float(row[8])
        StrokeR = float(row[9])
        DistancePerStrokeR = float(row[10])

        if row[12] == "---":
            HeartRateR = 0
        else:
            HeartRateR = float(row[12])

        distance.append(distanceR)
        time.append(timeR)
        split.append(splitR)
        StrokeRate.append(StrokeRateR)
        Stroke.append(StrokeR)
        DistancePerStroke.append(DistancePerStrokeR)
        HeartRate.append(HeartRateR)

    path = "data/"+workout + '/'

    # -Abspeichern als Arrays und umrechnung in float----------------------------------------------------------------------#


    StrokeRate = np.asarray(StrokeRate)
    Stroke = np.asarray(Stroke)
    DistancePerStroke = np.asarray(DistancePerStroke)
    distance = np.asarray(distance)

    time = np.asarray(time)
    time_sec = get_sec(time)

    split = np.asarray(split)
    split_sec = get_sec(split)

    correct_HR_values = True
    for i in HeartRate:
        if i == 0:
            correct_HR_values = False

    # -Durchschnitts- & Maximalwerte---------------------------------------------------------------------------------------#

    # Schlagzahl
    StrokeRateMean = round(np.mean(StrokeRate),1)
    MaxStrokeRate = 0
    for k in range(len(StrokeRate)):
        if MaxStrokeRate < StrokeRate[k] and StrokeRate[k] < 50:
            MaxStrokeRate = StrokeRate[k]

    # Distanz pro Schlag
    DistancePerStrokeMean = round(np.mean(DistancePerStroke),1)
    MaxDPS = 0
    for k in range(len(DistancePerStroke)):
        if MaxDPS < DistancePerStroke[k] and DistancePerStroke[k] < 15:
            MaxDPS = DistancePerStroke[k]

    # Split
    splitmean_sec = round(np.mean(split_sec),1)
    splitmean = get_time(splitmean_sec)
    maxsplit = np.min(split_sec)
    minsplit = np.min(split_sec)
    if len(distance) > 100:
        rangel = 30
    else:
        rangel = 10
    for k in range(rangel, len(split_sec)):
        if minsplit < split_sec[k]:
            minsplit = split_sec[k]

    # -Smooth line---------------------------------------------------------------------------------------------------------#

    smoothness = 5 # wähle aus wie viele Zahlen in einem moving window sind, muss ungerade sein

    edge_cut = m.floor(smoothness/2)
    new_dis = distance[edge_cut:-edge_cut]
    distance_new = np.linspace(0, max(new_dis), 10000)
		     
    new_split = signal.convolve(split_sec, np.ones(smoothness)/smoothness , mode = "valid")
    spl_split = make_interp_spline(new_dis, new_split)
    split_smooth = spl_split(distance_new)

    new_SR = signal.convolve(StrokeRate, np.ones(smoothness)/smoothness , mode = "valid")
    spl_SR = make_interp_spline(new_dis, new_SR)
    SR_smooth = spl_SR(distance_new)

    if correct_HR_values == True:
        spl_HR = make_interp_spline(distance, HeartRate)
        HR_smooth = spl_HR(distance_new)

    # -Diagramme-----------------------------------------------------------------------------------------------------------#

    newpath = workout
    if not os.path.exists(path):
        os.makedirs(path)

    if minsplit > 200:
        minimumy = 208
    else:
        minimumy = minsplit


    # split
    plt.plot(distance_new, split_smooth, color='navy', label='Split', lw=0.8)
    plt.yticks([80,85,90,95,100,105,110,115,120,125,130,135,140],
               ['1:20.0','1:25.0','1:30.0','1:35.0','1:40.0','1:45.0',
                '1:50.0','1:55.0','2:00.0', '2:05.0','2:10.0','2:15.0','2:20.0'])
    plt.grid(color='grey', ls=':')
    plt.axhline(y=splitmean_sec, xmin=0.05, xmax=0.95, color='red', ls='--', lw=0.5,
                label='Avg. split (%s min/500m)' % (splitmean))
    plt.ylim(maxsplit-2, minimumy+2)
    plt.xlim(0, distance[len(distance)-1]+10)
    plt.xlabel(r'Distance [$m$]', size=10)
    plt.ylabel(r'Split [$min/500m$]', size=10)
    plt.title(workout + ' - Split')
    plt.legend(fancybox=True)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(path + 'Split.pdf', format='PDF')
    plt.draw()
    plt.gcf().clear()

    # Stroke Rate
    plt.plot(distance_new, SR_smooth, color='navy', label='Stroke Rate', lw=0.8)
    plt.grid(color='grey', ls=':')
    plt.ylim(MaxStrokeRate+2, np.min(StrokeRate)-2)
    plt.xlim(0, distance[len(distance)-1]+10)
    plt.axhline(y=StrokeRateMean, xmin=0.05, xmax=0.95, color='red', ls='--', lw=0.5,
                label='Avg. Stroke Rate (%s spm)' % StrokeRateMean)
    plt.xlabel(r'Distance [$m$]', size=10)
    plt.ylabel(r'Stroke Rate [$spm$]', size=10)
    plt.title(workout + ' - Stroke Rate')
    plt.legend()
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(path+'StrokeRate.pdf', format='PDF')
    plt.draw()
    plt.gcf().clear()

    # Heart Rate
    if correct_HR_values == True:
        HRmean = round(statistics.mean(HeartRate),1)
        HRmax = max(HeartRate)

        plt.plot(distance_new, HR_smooth, color='navy', label='Heart Rate', lw=0.8)
        plt.grid(color='grey', ls=':')
        plt.ylim(HRmax+2, np.min(HeartRate)-2)
        plt.xlim(0, distance[len(distance)-1]+10)
        plt.axhline(y=HRmean, xmin=0.05, xmax=0.95, color='red', ls='--', lw=0.5,
                    label='Avg. Heart Rate (%s spm)' % HRmean)
        plt.xlabel(r'Distance [$m$]', size=10)
        plt.ylabel(r'Heart Rate [$spm$]', size=10)
        plt.title(workout + ' - Heart Rate')
        plt.legend()
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(path+'HeartRate.pdf', format='PDF')
        plt.draw()
        plt.gcf().clear()

    # Distance per Stroke per StrokeRate
    plt.plot(distance, DistancePerStroke, color='navy', label='Distance p. Stroke', lw=0, marker='o', markersize=5)
    plt.axhline(y=DistancePerStrokeMean, xmin=0.05, xmax=0.95, color='red', ls='--', lw=0.5,
                label='Avg. Heart Rate (%s spm)' % DistancePerStrokeMean)
    plt.grid(color='grey', ls=':')
    plt.ylim(5, 15)
    plt.xlim(0, distance[len(distance)-1]+10)
    plt.xlabel(r'Distance [$m$]', size=10)
    plt.ylabel(r'Distance p. Stroke [$m$]', size=10)
    plt.title(workout + ' - Distance p. Stroke')
    plt.legend()
    plt.tight_layout()
    plt.savefig(path+'DPS.pdf', format='PDF')
    plt.draw()
    plt.gcf().clear()

    # -PDF Merge-----------------------------------------------------------------------------------------------------------#

    if correct_HR_values == True:
        pdf_files = ['Split.pdf', 'StrokeRate.pdf', 'HeartRate.pdf', 'DPS.pdf']
    else:
        pdf_files = ['Split.pdf', 'StrokeRate.pdf', 'DPS.pdf']

    merger = PdfMerger()
    for files in pdf_files:
        merger.append(path+files)
    merger.write(path+workout+'.pdf')
    merger.close()
    os.remove(path+'StrokeRate.pdf')
    os.remove(path+'Split.pdf')
    if correct_HR_values == True:
        os.remove(path+'HeartRate.pdf')
    os.remove(path+'DPS.pdf')

    test = path+workout+'.pdf'
    path = path
    file = workout+'.pdf'

    # -Ende----------------------------------------------------------------------------------------------------------------#

    return path, file
