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
graphStartBRK = plt.figure()

basketballPattern = re.compile(r'([0-9]{4})\">[A-Za-z]+, ([A-Za-z]+) ([0-9]{1,2}).*start_time\" >([0-9:ap]+).*location\" ><.*result\" >([WL]).*pts\" >([0-9]+).*opp_pts\" >([0-9]+).*wins\" >([0-9]+).*losses\" >([0-9]+)')

# baseketballPattern 0)year 1)month 2)day  3)time 4) win or loss 5)points for 6)points against 7)wins on season 8)losses on season

monthDict = {"Jan":1, "Feb":2,"Mar":3, "Apr":4,"May":5,"Jun":6, "Oct":10, "Nov":11, "Dec":12}

BRK2014 = urllib.request.urlopen("http://www.basketball-reference.com/teams/BRK/2014_games.html")
dataBRK2014 = BRK2014.read().decode()
patternBRK2014 = basketballPattern
if dataBRK2014: foundBRK2014 = re.findall(patternBRK2014, dataBRK2014)
if foundBRK2014:
    for i in foundBRK2014:
        
#from the websites, single-digit dates are written as only one character. However, in the taxi data, they are two characters so I am changing the single-digit date to be two digits
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)
   
BRK2015 = urllib.request.urlopen("http://www.basketball-reference.com/teams/BRK/2015_games.html")
dataBRK2015 = BRK2015.read().decode()
patternBRK2015 = basketballPattern
if dataBRK2015: foundBRK2015 = re.findall(patternBRK2015, dataBRK2015)
if foundBRK2015:
    for i in foundBRK2015:
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)
    

BRK2016 = urllib.request.urlopen("http://www.basketball-reference.com/teams/BRK/2016_games.html")
dataBRK2016 = BRK2016.read().decode()
patternBRK2016 = basketballPattern
if dataBRK2016: foundBRK2016 = re.findall(patternBRK2016, dataBRK2016)
if foundBRK2016:
    for i in foundBRK2016:
        if len(i[2])==1: 
            elem2 = "0"+i[2]
        else: elem2 = i[2]
        newList = i[0], i[1], elem2, i[3],i[4],i[5],i[6],i[7],i[8]
        events[int(monthDict[i[1]])].append(newList)
       
startBRK = open("startBarclays.txt","rt")
gridFromBRK = [[0 for col in range(62)] for row in range(33)]
averageTime = 138.1

for j in startBRK:

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
            if k != [] and (gameEndTime -15) <= taxiStartTime and (gameEndTime +30) >= taxiStartTime and gameDay == taxiDay:
                try: fare = float(k[-1])
                except: print ("should be fare: ", float(k[-1]))
                try: tip = float(k[-2])
                except: print ("should be tip: ", float(k[-2]))
                if (tip or tip ==0) and fare:
                    tipPercentage = tip/fare
                    tipPercentage = float("%.2f" % tipPercentage)
                    pointDiff = int(i[5])-int(i[6])
                    rowNum = math.floor(tipPercentage/.02)
                    gridFromBRK[rowNum][pointDiff+30]+=1

                    
for row in range(len(gridFromBRK)):
    for col in range(len(gridFromBRK[0])):
        if gridFromBRK[row][col] >0:
            gridFromBRK[row][col] = math.log(gridFromBRK[row][col])

plt.title("From Nets games")
plt.xlabel("point differential (+30)")
plt.ylabel("percentage of tip")
plt.imshow(gridFromBRK, cmap = 'hot', interpolation = 'nearest')
graphStartBRK.savefig("fromNets.pdf")
