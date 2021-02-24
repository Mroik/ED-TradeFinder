#!/bin/python

import json
import sys
import subprocess
import math
import sqlite3
from sqlite3 import Error

#TODO Check the end of the file

class System:
    def __init__(self, id, name, x, y, z):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.neighbors = [] #The list will contain the ids of systems

    def addNeighbor(self, neighbor):
        self.neighbors.append(neighbor)

class Galaxy:
    def __init__(self):
        self.systems = {} #The keys of the dictionary are the id's of the systems
        self.visited = [] #This is a list of ids
        self.routeExists = False #This is used in doesRouteExist() as a flag to return the result

    def addSystem(self, system):
        self.systems[system.id] = system

    #start and end are objects of system
    def doesRouteExist(self, start, end):
        if start.id == end.id:
            self.visited.clear()
            self.routeExists = True
            return True
        if len(self.visited) == len(self.systems):
            self.visited.clear()
            self.routeExists = False
        for x in start.neighbors:
            if x.id not in self.visited:
                self.visited.append(x.id)
                surface = self.doesRouteExist(x, end)
                if surface == True:
                    return True
        return

def loadMap(start, end):
    galaxy = Galaxy()
    try:
        conn = sqlite3.connect("map.db")
        cursor = conn.cursor()
        query = "SELECT * FROM systems WHERE systems.id = ?;"
        cursor.execute(query, start)
        start = cursor.fetchone()
        cursor.execute(query, end)
        end = cursor.fetchone()

        #Fetching only systems between start and end
        if start[2] < end[2]:
            min_x, max_x = start[2], end[2]
        else:
            min_x, max_x = end[2], start[2]
        if start[3] < end[3]:
            min_y, max_y = start[3], end[3]
        else:
            min_y, max_y = end[3], start[3]
        if start[4] < end[4]:
            min_z, max_z = start[4], end[4]
        else:
            min_z, max_z = end[4], start[4]
        query = "SELECT * FROM systems WHERE systems.x >= ? AND systems.x <= ? AND systems.y >= ? AND systems.y <= ? AND systems.z >= ? AND systems.z <= ?;"
        data = (min_x, max_x, min_y, max_y, min_z, max_z)
        cursor.execute(query, data)
        query = "SELECT * FROM neighbors WHERE from_id = ?;"
        cursor2 = conn.cursor() #cursor for fetching neighbors
        for row in cursor:
            system = System(row[0], row[1], row[2], row[3], row[4])
            galaxy.addSystem(system)
        galaxy.addSystem(start)
        galaxy.addSystem(end)
        for syss in galaxy.systems:
            cursor2.execute(query)
            for neigh in cursor2:
                if neigh[2] in galaxy.systems:
                    system.addNeighbor(neigh[2])
        cursor.close()
        cursor2.close()
        conn.close()
        return galaxy
    except Error as err:
        print(err)
        return None

def distance(system1, system2):
    x = system1["x"] - system2["x"]
    if x < 0:
        x = -x
    y = system1["y"] - system2["y"]
    if y < 0:
        y = -y
    z = system1["z"] - system2["z"]
    if z < 0:
        z = -z
    ris = math.sqrt(x*x + y*y)
    ris = math.sqrt(ris*ris + z*z)
    return ris

listings = []

print("Parsing \"listings.csv\"...", flush = True, end = "", file = sys.stderr)
f = open("listings.csv", "r")

for line in f:
    data = line.split(",")
    try:
        commodity = {
                "station_id":   int(data[1]),
                "commodity_id": int(data[2]),
                "supply":       int(data[3]),
                "buy_price":    int(data[5]),
                "sell_price":   int(data[6]),
                "demand":       int(data[7])
        }
        listings.append(commodity)
    except:
        pass

f.close()

print("done", file = sys.stderr)

print("Parsing \"commodities.json\"...", flush = True, end = "", file = sys.stderr)
f = open("commodities.json")
data = json.loads(f.read())
f.close()

#This is for referencing the commodity names
reference = {}
for x in data:
    reference[x["id"]] = x["name"]

for x in range(len(listings)):
    listings[x]["name"] = reference[listings[x]["commodity_id"]]

print("done", file = sys.stderr)

print("Parsing \"stations.json\"...", flush = True, end = "", file = sys.stderr)
f = open("stations.json", "r")
data = json.loads(f.read())
f.close()

reference = {}
for x in data:
    reference[x["id"]] = {
            "name":                 x["name"],
            "system_id":            x["system_id"],
            "max_landing_pad_size": x["max_landing_pad_size"]
    }

for x in range(len(listings)):
    listings[x]["station_name"] = reference[listings[x]["station_id"]]["name"]
    listings[x]["system_id"] = reference[listings[x]["station_id"]]["system_id"]
    listings[x]["max_landing_pad_size"] = reference[listings[x]["station_id"]]["max_landing_pad_size"]

print("done", file = sys.stderr)

########################

buy_place = None
for x in listings:
    if buy_place == None or buy_place["buy_price"] > x["buy_price"]:
        if x["name"] == sys.argv[1] and x["buy_price"] != 0:
            buy_place = x

profit = buy_place["buy_price"]

sell_place = None
for x in listings:
    if sell_place == None or sell_place["sell_price"] < x["sell_price"]:
        if x["name"] == sys.argv[1] and x["sell_price"] != 0:
            sell_place = x

#TODO Implement route checking for the trade route
