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

def pathExists(start_id, finish_id, max_jump, galaxy, visited_systems):

    if start_id == finish_id:
        return True,[start_id]

    print("Visiting:",galaxy[start_id]["name"], flush=True)
    
    visited_systems.append(start_id)

    # Order based on distance from finish
    if len(galaxy[start_id]["neighbors"]) > 1:
        for x in range(0, len(galaxy[start_id]["neighbors"]) - 1):
            for y in range(x+1, len(galaxy[start_id]["neighbors"])):
                if galaxy[galaxy[start_id]["neighbors"][x]]["distance"] > galaxy[galaxy[start_id]["neighbors"][y]]["distance"]:
                    temp = galaxy[start_id]["neighbors"][x]
                    galaxy[start_id]["neighbors"][x] = galaxy[start_id]["neighbors"][y]
                    galaxy[start_id]["neighbors"][y] = temp

    for x in galaxy[start_id]["neighbors"]:
        if x in visited_systems:
            continue
        temp, temp2 = pathExists(x, finish_id, max_jump, galaxy, visited_systems)
        if temp:
            temp2.append(start_id)
            return True,temp2
    return False,None

def loadMap(conn, start, finish, galaxy):
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
                "neighbors": [],
                "distance": 0
        }
    cursor.close()

def genNeighbors(max_jump, finish, galaxy):
    for i in galaxy:
        galaxy[i]["distance"] = distance(galaxy[i]["x"], galaxy[i]["y"], galaxy[i]["z"], galaxy[finish]["x"], galaxy[finish]["y"], galaxy[finish]["z"])
        for j in galaxy:
            if i != j and distance(galaxy[i]["x"], galaxy[i]["y"], galaxy[i]["z"], galaxy[j]["x"], galaxy[j]["y"], galaxy[j]["z"]) <= max_jump:
                galaxy[i]["neighbors"].append(j)

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    DB_FILE = "map.db"
    START = 1
    FINISH = 30
    MAX_JUMP = 25

    visited_systems = []
    galaxy = {}

    conn = sqlite3.connect(DB_FILE)
    loadMap(conn, START, FINISH, galaxy)
    genNeighbors(MAX_JUMP, FINISH, galaxy)
    conn.close()
    temp,temp2 = pathExists(START, FINISH, MAX_JUMP, galaxy, visited_systems)
    if temp:
        print("Path exists between {} and {}".format(START, FINISH))

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
        ax_galaxy.scatter(x,y,z)
        for a in temp2:
            x1.append(galaxy[a]["x"])
            y1.append(galaxy[a]["y"])
            z1.append(galaxy[a]["z"])
        ax_galaxy.plot(x1,y1,z1,c="red")
        plt.show()
        fig.savefig("{}to{}.png".format(START, FINISH))
    else:
        print("Path does not exists between {} and {}".format(START, FINISH))

    print(galaxy[START]["name"])
    print(galaxy[FINISH]["name"])
