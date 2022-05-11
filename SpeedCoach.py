# -Importieren der Bibliotheken----------------------------------------------------------------------------------------#

import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from PyPDF2 import PdfFileMerger
import statistics

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


    summary = readCSV[15]

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
    # StrokeRateMean = np.mean(StrokeRate)
    MaxStrokeRate = 0
    for k in range(len(StrokeRate)):
        if MaxStrokeRate < StrokeRate[k] and StrokeRate[k] < 50:
            MaxStrokeRate = StrokeRate[k]
    # print('Stroke Rate Mean: %s spm\nMax. Stroke Rate: %s spm\n' % (StrokeRateMean, MaxStrokeRate))

    # Distanz pro Schlag
    DistancePerStrokeMean = round(np.mean(DistancePerStroke),1)
    # DistancePerStrokeMean = np.mean(DistancePerStroke)
    MaxDPS = 0
    for k in range(len(DistancePerStroke)):
        if MaxDPS < DistancePerStroke[k] and DistancePerStroke[k] < 15:
            MaxDPS = DistancePerStroke[k]
    # print('Distance p. Stoke Mean = %s m\nMax. Distance p. Stroke = %s m\n' % (DistancePerStrokeMean, MaxDPS))

    # Split
    splitmean_sec = round(np.mean(split_sec),1)
    splitmean = get_time(splitmean_sec)
    maxsplit = np.min(split_sec)
    # print('Split Mean = %s /500m\nMax. Split = %s /500m\n' % (splitmean, get_time(maxsplit)))
    minsplit = np.min(split_sec)
    if len(distance) > 100:
        rangel = 30
    else:
        rangel = 10
    for k in range(rangel, len(split_sec)):
        if minsplit < split_sec[k]:
            minsplit = split_sec[k]

    # Herzfrequenz
    if correct_HR_values == True:
        HRmean = round(statistics.mean(HeartRate),1)
        HRmax = max(HeartRate)
        # print('Mean heart rate = %s spm\nMax. heart rate = %s spm' % (HRmean, HRmax))
    # else:
        # print("Heart rate values are not correct!")

    # -Diagramme-----------------------------------------------------------------------------------------------------------#

    newpath = workout
    if not os.path.exists(path):
        os.makedirs(path)

    if minsplit > 200:
        minimumy = 208
    else:
        minimumy = minsplit


    # split
    plt.plot(distance, split_sec, color='navy', label='Split', lw=0.8)
    plt.yticks([80,82,84,86,88,90,92,94,96,98,100,105,110,115,120,130,140,150,160,170,180,190,200],
               ['1:20.0','1:22.0','1:24.0','1:26.0','1:28.0','1:30.0','1:32.0','1:34.0','1:36.0','1:38.0','1:40.0','1:45.0',
                '1:50.0','1:55.0','2:00.0','2:10.0','2:20.0','2:30.0','2:40.0','2:50.0','3:00.0','3:10.0','3:20.0'])
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
    plt.plot(distance, StrokeRate, color='navy', label='Stroke Rate', lw=0.8)
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
        plt.plot(distance, HeartRate, color='navy', label='Heart Rate', lw=0.8)
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

    merger = PdfFileMerger()
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