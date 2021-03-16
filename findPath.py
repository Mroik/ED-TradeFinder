#!/bin/python

import sqlite3
import math
import sys

sys.setrecursionlimit(999999)

def distance(x1, y1, z1, x2, y2, z2):
    x = x1 - x2
    y = y1 - y2
    z = z1 - z2
    ris = math.sqrt(x*x + y*y)
    ris = math.sqrt(ris*ris + z*z)
    return ris

def pathExists(start_id, finish_id, max_jump):
    global visited_systems
    global galaxy

    if start_id == finish_id:
        return True

    print("Visiting:",galaxy[start_id]["name"])
    
    visited_systems.append(start_id)
    for x in galaxy[start_id]["neighbors"]:
        if x in visited_systems:
            continue
        if pathExists(x, finish_id, max_jump):
            return True
    return False

def loadMap(conn, start, finish):
    global galaxy
    cursor = conn.cursor()
    query = "SELECT * FROM systems WHERE id = ?"
    cursor.execute(query, (start,))
    start_data = cursor.fetchone()
    cursor.execute(query, (finish,))
    finish_data = cursor.fetchone()
    if start_data[2] < finish_data[2]:
        x_min, x_max = start_data[2], finish_data[2]
    else:
        x_min, x_max = finish_data[2], start_data[2]
    if start_data[3] < finish_data[3]:
        y_min, y_max = start_data[3], finish_data[3]
    else:
        y_min, y_max = finish_data[3], start_data[3]
    if start_data[4] < finish_data[4]:
        z_min, z_max = start_data[4], finish_data[4]
    else:
        z_min, z_max = finish_data[4], start_data[4]
    query = "SELECT * FROM systems WHERE x >= ? AND x <= ? AND y >= ? AND y <= ? AND z >= ? AND z <= ?"
    cursor.execute(query, (x_min, x_max, y_min, y_max, z_min, z_max))
    for row in cursor:
        galaxy[row[0]] = {
                "name": row[1],
                "x": row[2],
                "y": row[3],
                "z": row[4],
                "neighbors": []
        }
    cursor.close()

def genNeighbors(max_jump):
    global galaxy
    for i in galaxy:
        for j in galaxy:
            if i != j and distance(galaxy[i]["x"], galaxy[i]["y"], galaxy[i]["z"], galaxy[j]["x"], galaxy[j]["y"], galaxy[j]["z"]) <= max_jump:
                galaxy[i]["neighbors"].append(j)

DB_FILE = "map.db"
START = 1
FINISH = 30
MAX_JUMP = 25

visited_systems = []
galaxy = {}

conn = sqlite3.connect(DB_FILE)
loadMap(conn, START, FINISH)
genNeighbors(MAX_JUMP)
conn.close()
if pathExists(START, FINISH, MAX_JUMP):
    print("Path exists between {} and {}".format(START, FINISH))
else:
    print("Path does not exists between {} and {}".format(START, FINISH))
