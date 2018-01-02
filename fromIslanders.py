#!/usr/bin/env python3

import re
import urllib.request
import subprocess
import os
import gzip
import matplotlib.pyplot as plt
import math

#events is a list of 13 lists. Each month has a list of events that took place during that month, regardless of year. Now, each taxi line is only compared to each element of the correct month's list, significantly reducing the "Big-O"
events = [[]for i in range(13)]
startBarclays = open("./startBarclays.txt", "rt")
graphStartIslanders = plt.figure()

hockeyPattern = re.compile(r'html\">([0-9-]+).*time_game\" >([0-9]+)(:[0-9]{2}) ([PAM]{2}).*game_location\" ><.*goals\" >([0-9]+).*opp_goals\" >([0-9]+).*outcome\" >([WL]).*wins\" >([0-9]+).*\"losses\" >([0-9]+).*losses_ot\" >([0-9]+)')
# 0=date 1= hour 2 = colon minute 3= pm/am 4=goals for 5=goals against 6=outcome 7 = wins 8 = losses 9 = OT/SO losses

averageTime = 148.78
hockeyStdDev = 6.25

NYI2016 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYI/2016_games.html")
dataNYI2016 = NYI2016.read().decode()
patternNYI2016 = hockeyPattern
if dataNYI2016: foundNYI2016 = re.findall(patternNYI2016, dataNYI2016)
if foundNYI2016:
    for i in foundNYI2016:
        events[int(i[0][5:7])].append(i)

NYI2015 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYI/2015_games.html")
dataNYI2015 = NYI2015.read().decode()
patternNYI2015 = hockeyPattern
if dataNYI2015: foundNYI2015 = re.findall(patternNYI2015, dataNYI2015)
if foundNYI2015:
    for i in foundNYI2015:
        events[int(i[0][5:7])].append(i)

NYI2014 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYI/2014_games.html")
dataNYI2014 = NYI2014.read().decode()
patternNYI2014 = hockeyPattern
if dataNYI2014: foundNYI2014 = re.findall(patternNYI2014, dataNYI2014)
if foundNYI2014:
    for i in foundNYI2014:
        events[int(i[0][5:7])].append(i)
    

gridFromNYI = [[0 for col in range(35)] for row in range(15)]
for j in startBarclays:
    l = j.strip()
#k is now a list of the taxi data fields that are significant for analyzing the data for this program
    k = l.split("|")
    k.pop(0)
    if k != []:
        try: taxiMonth = int(k[0][5:7])
        except: taxiMonth = 0
        eventMonth = events[taxiMonth]
        try:taxiDay = k[1][:10]
        except: taxiDay = 0
        eventMonth = events[taxiMonth]

        try: taxiStartHour = int(k[0][11:13])
        except: taxiStartHour = 0
        try: taxiStartMinute = int(k[0][14:16])
        except: taxiStartMinute = 0
        taxiStartTime = taxiStartHour*60 + taxiStartMinute

        for i in eventMonth: #correct month list
            if int(i[1]) < 12 and i[3]=="PM":
                gameHour = int(i[1])+12
            else: gameHour = int(i[1])
            gameMinute = int(i[2][1:])
            gameStartTime = gameHour*60 + gameMinute
            gameEndTime = gameStartTime + hockeyStdDev + averageTime
            gameDay = i[0]
            if k != [] and gameEndTime-15 <= taxiStartTime and gameEndTime+30 >= taxiStartTime and gameDay == taxiDay:

                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip == 0) and fare: #if there is a tip (even if it is 0) and also a fare
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    if tipPercentage <= .3:
                        pointDiff = int(i[4])-int(i[5]) #goals for minus goals against
#to create a heatMap, more than one exact value of tipPercentage are added to create one y value
                        tipBin = math.floor(tipPercentage/.02)
#to keep all values positive, the differential presented is really 10 higher than it truly is
                        gridFromNYI[tipBin][pointDiff+20]+=1

#logarithmically enhance the lesser used bins
for row in range(len(gridFromNYI)):
    for col in range(len(gridFromNYI[0])):
        if gridFromNYI[row][col] >0:
            gridFromNYI[row][col] = math.log(gridFromNYI[row][col])

plt.title("From Islanders Games")
plt.xlabel("points differential (+20)")
plt.ylabel("percentage of tip")
plt.imshow(gridFromNYI, cmap = 'hot', interpolation = 'nearest')
#plt.show()
graphStartIslanders.savefig("fromIslanders.pdf")
