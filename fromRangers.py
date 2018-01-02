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
graphStartRangers = plt.figure()

#find the average and standard deviation of length of a hockey game ##this number is used in both this file and fromIslanders.py
hockeyPatternStdDev = re.compile(r'html\">([0-9-]+).*time_game\" >([0-9]+)(:[0-9]{2}) ([PAM]{2}).*game_location\" ><.*goals\" >([0-9]+).*opp_goals\" >([0-9]+).*outcome\" >([WL]).*wins\" >([0-9]+).*\"losses\" >([0-9]+).*losses_ot\" >([0-9]+)(.*game_duration\" >)?([0-9:]+)?')
# hockeyPattern 1)date 2)time 3)goals for 4)goals against 5)outcome 6)wins on season 7)losses on season 8)OT/SO losses on season 9) UNNECESSARY (10)length of game)--only able to get for end of 2015

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
startNYR = open("./startMSG.txt","rt")

NYR2016 = urllib.request.urlopen("http://www.hockey-reference.com/teams/NYR/2016_games.html")
dataNYR2016 = NYR2016.read().decode()
patternNYR2016 = hockeyPatternStdDev
if dataNYR2016: foundNYR2016 = re.findall(patternNYR2016, dataNYR2016)
if foundNYR2016:
    totalTime = (int(foundNYR2016[0][11][0])*60) + int(foundNYR2016[0][11][-2:])
    for i in range(1, len(foundNYR2016)):
        totalTime += (int(foundNYR2016[i][11][0])*60) + int(foundNYR2016[i][11][-2:])
    averageTime = totalTime/(len(foundNYR2016))  
    indivTime = (int(foundNYR2016[0][11][0])*60) + int(foundNYR2016[0][11][-2:]) 
    indivDiff = (averageTime - indivTime)**2
    for i in range(1, len(foundNYR2016)):
        indivTime = (int(foundNYR2016[i][11][0])*60) + int(foundNYR2016[i][11][-2:])
        indivDiff += (averageTime - indivTime)**2


#std deviation for hockey length of game-
hockeyStdDev = ((indivDiff)/len(foundNYR2016))**.5
hockeyStdDev = float("%.2f" % hockeyStdDev)
averageTime = float("%.2f" % averageTime)

gridFromNYR = [[0 for col in range(30)] for row in range(37)] 


for j in startNYR:
    l = j.strip()
#k is now a list of the taxi data fields that are significant for analyzing the data for this program
    k = l.split("|")
    k.pop(0)
    if k != []:
        try: taxiMonth = int(k[0][5:7])
        except: taxiMonth = 0
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
            gameEndTime = gameHour*60 + gameMinute + hockeyStdDev + averageTime
            gameDay = i[0]

            if k != [] and (gameEndTime -15) <= taxiStartTime and (gameEndTime +30) >= taxiStartTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip ==0) and fare: #if there is a tip (even if it is 0) and also a fare
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    pointDiff = int(i[4])-int(i[5]) #goals for minus goals against
#to create a heatMap, more than one exact value of tipPercentage are added to create one y value
                    tipBin = math.floor(tipPercentage/.02)
#to keep all values positive, the differential presented is really 10 higher than it truly is
                    gridFromNYR[tipBin][pointDiff+20]+=1
#logarithmically enhance the lesser used bins
for row in range(len(gridFromNYR)):
    for col in range(len(gridFromNYR[0])):
        if gridFromNYR[row][col] >0:
            gridFromNYR[row][col] = math.log(gridFromNYR[row][col])


plt.title("From Rangers Games")
plt.xlabel("goals differential(+20)")
plt.ylabel("percentage of tip")
plt.imshow(gridFromNYR, cmap = 'hot', interpolation = 'nearest')
#plt.show()
graphStartRangers.savefig("fromRangers.pdf")

