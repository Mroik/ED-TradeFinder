#!/bin/python

import json
import sys
import subprocess
import math
import findPath
import sqlite3
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#TODO Check the end of the file

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

print("Parsing \"listings.csv\"...", flush = True, end = "")
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

print("done")

print("Parsing \"commodities.json\"...", flush = True, end = "")
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

print("Parsing \"stations.json\"...", flush = True, end = "")
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

print("done")

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

print("Profit: {}".format(profit))

buy_place = buy_place["system_id"]
sell_place = sell_place["system_id"]

#TODO Implement route checking for the trade route
if buy_place != None and sell_place != None:
    galaxy = {}
    visited_systems = []
    
    max_jump = float(sys.argv[2])

    conn = sqlite3.connect("map.db")
    findPath.loadMap(conn, buy_place, sell_place, galaxy)
    findPath.genNeighbors(max_jump, sell_place, galaxy)
    conn.close()
    
    status, path = findPath.pathExists(buy_place, sell_place, max_jump, galaxy, visited_systems)
    if status:
        print("Path exists between {} and {}".format(galaxy[buy_place]["name"], galaxy[sell_place]["name"]))
    else:
        print("Path doesn't exist between {} and {}".format(galaxy[buy_place]["name"], galaxy[sell_place]["name"]))
        sys.exit()

    x = []
    y = []
    z = []
    x1 = []
    y1 = []
    z1 = []
    for i in galaxy:
        x.append(galaxy[i]["x"])
        y.append(galaxy[i]["y"])
        z.append(galaxy[i]["z"])
    fig = plt.figure()
    ax_galaxy = fig.add_subplot(projection="3d")
    ax_galaxy.scatter(x, y, z, c = "green")
    for a in path:
        x1.append(galaxy[a]["x"])
        y1.append(galaxy[a]["y"])
        z1.append(galaxy[a]["z"])
    ax_galaxy.plot(x1, y1, z1, c = "red")
    plt.show()
