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

graphEndRangers = plt.figure()

hockeyPattern = re.compile(r'html\">([0-9-]+).*time_game\" >([0-9]+)(:[0-9]{2}) ([PAM]{2}).*game_location\" ><.*goals\" >([0-9]+).*opp_goals\" >([0-9]+).*outcome\" >([WL]).*wins\" >([0-9]+).*\"losses\" >([0-9]+).*losses_ot\" >([0-9]+)')
# 0=date 1= hour 2 = colon minute 3= pm/am 4=goals for 5=goals against 6=outcome 7 = wins 8 = losses 9 = OT/SO losses

NYR2016 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYR/2016_games.html")
dataNYR2016 = NYR2016.read().decode()
patternNYR2016 = hockeyPattern
if dataNYR2016: foundNYR2016 = re.findall(patternNYR2016, dataNYR2016)
if foundNYR2016:
    for i in foundNYR2016:
        events[int(i[0][5:7])].append(i)

NYR2015 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYR/2015_games.html")
dataNYR2015 = NYR2015.read().decode()
patternNYR2015 = hockeyPattern
if dataNYR2015: foundNYR2015 = re.findall(patternNYR2015, dataNYR2015)
if foundNYR2015: 
    for i in foundNYR2015:
        events[int(i[0][5:7])].append(i)    

NYR2014 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYR/2014_games.html")
dataNYR2014 = NYR2014.read().decode()
patternNYR2014 = hockeyPattern
if dataNYR2014: foundNYR2014 = re.findall(patternNYR2014, dataNYR2014)
if foundNYR2014:
    for i in foundNYR2014:
        events[int(i[0][5:7])].append(i)     

#now check with each line of start/end documents if it matches a day and time of an event at the correct location--only compare it to the correct month list.
endMSG = open("./endMSG.txt","rt")

gridToNYR = [[0 for col in range(50)] for row in range(50)]

for j in endMSG:
    l = j.strip(
#k is now a list of the taxi data fields that are significant for analyzing the data for this program
    k = l.split("|")
    k.pop(0)
    if k != []:
        try: taxiMonth = int(k[0][5:7])
        except: taxiMonth = 0
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
            if k != [] and (gameStartTime -30) <= taxiEndTime and (gameStartTime+15) >= taxiEndTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip ==0) and fare: #if there is a tip (even if it is 0) and also a fare
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    WLDiff = int(i[7])-int(i[8])-int(i[9]) #wins - regulation losses - OT losses
#to create a heatMap, more than one exact value of tipPercentage are added to create one y value
                    tipBin = math.floor(tipPercentage/.02)
#to keep all values positive, the differential presented is really 10 higher than it truly is
                    gridToNYR[tipBin][WLDiff+20]+=1
#logarithmically enhance the lesser used bins
for row in range(len(gridToNYR)):
    for col in range(len(gridToNYR[0])):
        if gridToNYR[row][col] > 0:
            gridToNYR[row][col] = math.log(gridToNYR[row][col])


plt.title("To Rangers Games")
plt.xlabel("win/loss differential (+20)")
plt.ylabel("percentage of tip")
plt.imshow(gridToNYR, cmap = 'hot', interpolation = 'nearest')
#plt.show()
graphEndRangers.savefig("toRangers.pdf")
