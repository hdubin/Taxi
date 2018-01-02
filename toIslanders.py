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
endBarclays = open("./endBarclays.txt", "rt")
graphEndIslanders = plt.figure()

hockeyPattern = re.compile(r'html\">([0-9-]+).*time_game\" >([0-9]+)(:[0-9]{2}) ([PAM]{2}).*game_location\" ><.*goals\" >([0-9]+).*opp_goals\" >([0-9]+).*outcome\" >([WL]).*wins\" >([0-9]+).*\"losses\" >([0-9]+).*losses_ot\" >([0-9]+)')
# 0=date 1= hour 2 = colon minute 3= pm/am 4=goals for 5=goals against 6=outcome 7 = wins 8 = losses 9 = OT/SO losses


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

gridToNYI = [[0 for col in range(50)] for row in range(20)]

for j in endBarclays:
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
        
        try: taxiEndHour = int(k[1][11:13])
        except: taxiEndHour = 0
        try: taxiEndMinute = int(k[1][14:16])
        except: taxiEndMinute = 0
        taxiEndTime = taxiEndHour*60 + taxiEndMinute

        for i in eventMonth: #correct month list
            if int(i[1]) < 12 and i[3]=="PM":
                gameHour = int(i[1])+12
            else: gameHour = int(i[1])
            gameMinute = int(i[2][1:])
            gameStartTime = gameHour*60 + gameMinute
            gameDay = i[0]
            if k != [] and gameStartTime+15 >= taxiEndTime and gameStartTime-30 <= taxiEndTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip == 0) and fare: #if there is a tip (even if it is 0) and also a fare
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)

                    WLDiff = int(i[7])-int(i[8])-int(i[9]) #wins - regulation losses - OT losses
#to create a heatMap, more than one exact value of tipPercentage are added to create one y value
                    tipBin = math.floor(tipPercentage/.02)
#to keep all values positive, the differential presented is really 10 higher than it truly is
                    gridToNYI[tipBin][WLDiff+20]+=1
#logarithmically enhance the lesser used bins
for row in range(len(gridToNYI)):
    for col in range(len(gridToNYI[0])):
        if gridToNYI[row][col] >0:
            gridToNYI[row][col] = math.log(gridToNYI[row][col])

plt.title("To Islanders Games")
plt.xlabel("Win/Loss differential (+20)")
plt.ylabel("percentage of tip")
plt.imshow(gridToNYI, cmap = 'hot', interpolation = 'nearest')
graphEndIslanders.savefig("toIslanders.pdf")
