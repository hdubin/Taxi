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
graphStartNYK = plt.figure()

basketballPattern = re.compile(r'([0-9]{4})\">[A-Za-z]+, ([A-Za-z]+) ([0-9]{1,2}).*start_time\" >([0-9:ap]+).*location\" ><.*result\" >([WL]).*pts\" >([0-9]+).*opp_pts\" >([0-9]+).*wins\" >([0-9]+).*losses\" >([0-9]+)')
# baseketballPattern 0)year 1)month 2)day  3)time 4) win or loss 5)points for 6)points against 7)wins on season 8)losses on season

monthDict = {"Jan":1, "Feb":2,"Mar":3, "Apr":4,"May":5,"Jun":6, "Oct":10, "Nov":11, "Dec":12}

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

startNYK = open("startMSG.txt","rt")
gridFromNYK = [[0 for col in range(45)] for row in range(31)]
averageTime = 138 #average length of game is 138 minutes


for j in startNYK:

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

        try: taxiStartHour = int(k[0][11:13])
        except: taxiStartHour = 0
        try: taxiStartMinute = int(k[0][14:16])
        except: taxiStartMinute = 0
        taxiStartTime = taxiStartHour*60 + taxiStartMinute

        for i in eventMonth: #correct month list
            if int(i[3][:-4]) < 12 and i[3][-1]=="p":
                gameHour = int(i[3][:-4])+12
            else: gameHour = int(i[3][:-4])
            gameMinute = int(i[3][-3:-1])
            gameStartTime = gameHour*60 + gameMinute
            gameEndTime = gameHour*60 + gameMinute + averageTime
            gameDay = i[0]+"-"+str(monthDict[i[1]])+"-"+i[2]
            if k != [] and (gameEndTime -15) <= taxiStartTime and (gameEndTime+30) >= taxiStartTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip ==0) and fare:
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    pointDiff = int(i[5])-int(i[6])
                    rowNum = math.floor(tipPercentage/.02)
                    gridFromNYK[rowNum][pointDiff+25]+=1
                    
for row in range(len(gridFromNYK)):
    for col in range(len(gridFromNYK[0])):
        if gridFromNYK[row][col] >0:
            gridFromNYK[row][col] = math.log(gridFromNYK[row][col])

plt.title("From Knicks games")
plt.xlabel("point differential (+25)")
plt.ylabel("percentage of tip")
plt.imshow(gridFromNYK, cmap = 'hot', interpolation = 'nearest')
graphStartNYK.savefig("fromKnicks.pdf")
