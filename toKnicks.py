#!/usr/bin/env python3

import re
import urllib.request
import subprocess
import os
import gzip
import sys
import matplotlib.pyplot as plt
import math

events = [[]for i in range(13)]
graphEndNYK = plt.figure()

basketballPattern = re.compile(r'([0-9]{4})\">[A-Za-z]+, ([A-Za-z]+) ([0-9]{1,2}).*start_time\" >([0-9:ap]+).*location\" ><.*result\" >([WL]).*pts\" >([0-9]+).*opp_pts\" >([0-9]+).*wins\" >([0-9]+).*losses\" >([0-9]+)')
# baseketballPattern 0)year 1)month 2)day  3)time 4) win or loss 5)points for 6)points against 7)wins on season 8)losses on season

monthDict = {"Jan":"01", "Feb":"02","Mar":"03", "Apr":"04","May":"05","Jun":"06", "Jul":"07"," Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}

NYK2014 = urllib.request.urlopen("http://www.basketball-reference.com/teams/NYK/2014_games.html")
dataNYK2014 = NYK2014.read().decode()
patternNYK2014 = basketballPattern
if dataNYK2014: foundNYK2014 = re.findall(patternNYK2014, dataNYK2014)
if foundNYK2014:
    for i in foundNYK2014:

#from the websites, single-digit dates are written as only one character. However, in the taxi data, they are two characters so I am changing the single-digit date to be two digits
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)

NYK2015 = urllib.request.urlopen("http://www.basketball-reference.com/teams/NYK/2015_games.html")
dataNYK2015 = NYK2015.read().decode()
patternNYK2015 = basketballPattern
if dataNYK2015: foundNYK2015 = re.findall(patternNYK2015, dataNYK2015)
if foundNYK2015: 
    for i in foundNYK2015:
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)

NYK2016 = urllib.request.urlopen("http://www.basketball-reference.com/teams/NYK/2016_games.html")
dataNYK2016 = NYK2016.read().decode()
patternNYK2016 = basketballPattern
if dataNYK2016: foundNYK2016 = re.findall(patternNYK2016, dataNYK2016)
if foundNYK2016:
    for i in foundNYK2016:
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)


endNYK = open("endMSG.txt","rt")
gridToNYK = [[0 for col in range(52)] for row in range(35)]
#averageTime = 138.1

maxTip = 0
maxDiff = -10
minDiff = 10
#count = 0

for j in endNYK:

    l = j.strip()
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

# baseketballPattern 0)year 1)month 2)day  3)time 4) win or loss 5)points for 6)points against 7)wins on season 8)losses on season

        for i in eventMonth: #correct month list
            if int(i[3][:-4]) < 12 and i[3][-1]=="p":
                gameHour = int(i[3][:-4])+12
            else: gameHour = int(i[3][:-4])
            gameMinute = int(i[3][-3:-1])
            gameStartTime = gameHour*60 + gameMinute
            gameDay = i[0]+"-"+str(monthDict[i[1]])+"-"+i[2]
            if k != [] and (gameStartTime -30) <= taxiEndTime and (gameStartTime+15) >= taxiEndTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip ==0) and fare:
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    WLDiff = int(i[7])-int(i[8])
                    rowNum = math.floor(tipPercentage/.02)
                    gridToNYK[rowNum][WLDiff+50]+=1    

for row in range(len(gridToNYK)):
    for col in range(len(gridToNYK[0])):
        if gridToNYK[row][col] >0:
            gridToNYK[row][col] = math.log(gridToNYK[row][col])


plt.title("To Knicks games")
plt.xlabel("win/loss differential (+50)")
plt.ylabel("percentage of tip")
plt.imshow(gridToNYK, cmap = 'hot', interpolation = 'nearest')
graphEndNYK.savefig("toKnicks.pdf")
