#!/bin/python

import sqlite3
from sqlite3 import Error
from math import sqrt

def distance(x1, x2, y1, y2, z1, z2):
    x = x1 - x2
    if x < 0:
        x = -x
    y = y1 - y2
    if y < 0:
        y = -y
    z = z1 - z2
    if z < 0:
        z = -z
    ris = sqrt(x*x + y*y)
    ris = sqrt(ris*ris + z*z)
    return ris

JUMP_DISTANCE = 15

conn = sqlite3.connect("map.db")
cursor = conn.cursor()
query = """
CREATE TABLE systems (
	id INT NOT NULL PRIMARY KEY,
	name TEXT NOT NULL,
	x FLOAT NOT NULL,
	y FLOAT NOT NULL,
	z FLOAT NOT NULL
);
"""
cursor.execute(query)
conn.commit()
query = "INSERT INTO systems(id, name, x, y, z) VALUES (?, ?, ?, ?, ?);"

print("Parsing \"systems.csv\"...", flush = True, end = "")
f = open("systems.csv", "r")
for x in f:
    data = x.split(",")
    values = (int(data[0]), data[2], float(data[3]), float(data[4]), float(data[5]))
    cursor.execute(query, values)
conn.commit()
f.close()
print("done", flush = True)

#This part is for creating the neighbors ta ble
query = """
CREATE TABLE neighbors (
	from_id INT NOT NULL,
	distance FLOAT NOT NULL,
	to_id INT NOT NULL,
	FOREIGN KEY (from_id) REFERENCES systems(id),
	FOREIGN KEY (to_id) REFERENCES systems(id)
);
"""
cursor.execute(query)
conn.commit()

query = "SELECT * FROM systems;"
insert_query = "INSERT INTO neighbors(from_id, distance, to_id) VALUES (?, ?, ?);"
cursor2 = conn.cursor() # 2nd select cursor
cursor3 = conn.cursor() # insert cursor

print("Calculating neighbors...", flush = True, end = "")
cursor.execute(query)
cont = 0
for x in cursor:
    cursor2.execute("SELECT * FROM systems WHERE systems.x > ? AND systems.x < ? AND systems.y > ? AND systems.y < ? AND systems.z > ? AND systems.z < ?", (x[2]-JUMP_DISTANCE, x[2]+JUMP_DISTANCE, x[3]-JUMP_DISTANCE, x[3]+JUMP_DISTANCE, x[4]-JUMP_DISTANCE, x[4]+JUMP_DISTANCE))
    for y in cursor2:
        if x[0] == y[0]:
            continue
        dista = distance(x[2], y[2],x[3], y[3], x[4], y[4])
        if dista <= JUMP_DISTANCE:
            cursor3.execute(insert_query, (x[0], dista, y[0]))
    #conn.commit()
    cont += 1 #DEBUG
    print(cont)
conn.commit()
cursor.close()
cursor2.close()
cursor3.close()
conn.close()

print("done")
