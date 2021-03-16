#!/bin/python

import sqlite3
import math

class System:
    def __init__(self, id, name, x, y, z):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.next = None

class Path:
    def __init__(self, start = None):
        self.start = start

def distance(x1, y1, z1, x2, y2, z2):
    x = x1 - x2
    y = y1 - y2
    z = z1 - z2
    ris = math.sqrt(x*x + y*y)
    ris = math.sqrt(ris*ris + z*z)
    return ris

def getNeighbors(conn, x, y, z, max_jump):
    neighbors = {}

    cursor = conn.cursor()
    query = "SELECT * FROM systems WHERE x >= ? AND x <= ? AND y >= ? AND y <= ? AND z >= ? AND z <= ?"
    cursor.execute(
            query,
            (x - max_jump,
            x + max_jump,
            y - max_jump,
            y + max_jump,
            z - max_jump,
            z + max_jump)
    )
    for row in cursor:
        if(distance(x, y, z, row[2], row[3], row[4]) <= max_jump):
            neighbors[row[0]] = {"name": row[1]}
    return neighbors

def pathExists(start_id, finish_id, conn, max_jump):
    global visited_systems

    if start_id == finish_id:
        return True

    cursor = conn.cursor()
    query = "SELECT * FROM systems WHERE id = ?"
    cursor.execute(query, (start_id,))
    data = cursor.fetchone()

    print("Visiting:",data[1])

    systemsToEval = getNeighbors(conn, data[2], data[3], data[4], max_jump)
    for sys_id in systemsToEval:
        if sys_id in visited_systems:
            continue
        else:
            visited_systems.append(sys_id)
        if pathExists(sys_id, finish_id, conn, max_jump):
            return True
    return False

DB_FILE = "map.db"
START = 1
FINISH = 30
MAX_JUMP = 25

visited_systems = []

conn = sqlite3.connect(DB_FILE)
if pathExists(START, FINISH, conn, MAX_JUMP):
    print("Path exists between {} and {}".format(START, FINISH))
else:
    print("Path does not exists between {} and {}".format(START, FINISH))
