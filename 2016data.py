#!/usr/bin/env python3

import re
import urllib.request
import subprocess
import gzip
import sys

startMSG = open("./startMSG2.txt", "w")
endMSG = open("./endMSG2.txt", "w")
startBarclays =  open("./startBarclays2.txt", "w")
endBarclays = open("./endBarclays2.txt", "w")

def opener(fileNames):
    for name in fileNames:
        if name == "/data/raw/NYCTaxis/2015/yellow_tripdata_2015-01.csv.gz":
            f = gzip.open(name, "rt")
            yield (name, f)

def cat(fileDescriptors):
    for t in fileDescriptors:
        for line in t[1]:
            yield (line)


def cut(lines, fieldList, sep):
    for line in lines:
        ans = []
        fields = line.split(sep)
        if line != "\n": #there are blank lines between each entry
            if len(fieldList) > 0:
                ans.append(fields[fieldList[0]])
            else:
                ans = ""
            for i in range(1,len(fieldList)):
                ans.append(fields[fieldList[i]])
            yield ans


## 2016 data ## 01-06 ##same as 2015
# 0 VendorID
# 1 tpep_pickup_datetime
# 2 tpep_dropoff_datetime
# 3 passenger_count
# 4 trip_distance
# 5 pickup_longitude
# 6 pickup_latitude
# 7 RatecodeID
# 8 store_and_fwd_flag
# 9 dropoff_longitude
# 10 dropoff_latitude
# 11 payment_type
# 12 fare_amount
# 13 extra
# 14 mta_tax
# 15 tip_amount
# 16 tolls_amount
# 17 improvement_surcharge
# 18 total_amount

name = "/data/raw/NYCTaxis/2015/yellow_tripdata_2015-01.csv.gz"
files =  (name, gzip.open(name,"rt"))
descriptors = opener(files)
lines = cat(descriptors)
fieldList = [1,2,5,6,9,10,11,15,18]
sections = cut(lines, fieldList, ",")

longOffset = .00188
latOffset = .00144

# MSG = 40.7505 N, 73.9934 W
# Barclays = 40.6825 N, 73.9750 W
### citi = 40.7571, 73.8458 W
### yankee = 40.8296 N, 73.9262 W

def getLocationFile(x, longOffset, latOffset):
    if x[6]=="1" or x[6] == "CRD":
        try: 
            startLong = float(x[2]) * -1
        except: 
            startLong = 0
            print (x[2]," invalid startLong  ", x)
        try: 
            startLat = float(x[3])
        except: 
            startLat = 0
            print (x[3], "invalid startLat")
        try: 
            endLong = float(x[4]) * -1
        except: 
            endLong = 0
            print (x[4]," invalid endLong")
        try:
            endLat = float(x[5])
        except: 
            endLat = 0
            print (x[5]," invalid endLat")

        if startLong + longOffset >= 73.9934 and startLong - longOffset <= 73.9934  and startLat + latOffset >= 40.7505 and startLat - latOffset <= 40.7505:
            for i in x:
                startMSG.write(i+"|")
                
        elif endLong + longOffset >= 73.9934 and endLong - longOffset <=73.9934 and endLat + latOffset >= 40.7505 and endLat - latOffset <= 40.7505:
            for i in x:
                endMSG.write(i+"|")

        elif startLong + longOffset >= 73.9750 and startLong - longOffset <= 73.9750 and startLat + latOffset >= 40.6825 and startLat - latOffset <= 40.6825:
            for i in x:
                startBarclays.write(i+"|")

        elif endLong + longOffset >= 73.9750 and endLong - longOffset <= 73.9750 and endLat + latOffset >= 40.6825 and endLat - latOffset <= 40.6825:
            for i in x:
                endBarclays.write(i+"|")


def opener(fileNames):
    for name in fileNames:
        if name == "/data/raw/NYCTaxis/2016/yellow_tripdata_2016-01.csv.gz":
            f = gzip.open(name, "rt")
            yield (name, f)

name = "/data/raw/NYCTaxis/2016/yellow_tripdata_2016-01.csv.gz"
files =  (name, gzip.open(name,"rt"))
descriptors = opener(files)
lines = cat(descriptors)
fieldList = [1,2,5,6,9,10,11,15,18]
sections = cut(lines, fieldList, ",")

for x in sections:
    getLocationFile(x, longOffset, latOffset)
