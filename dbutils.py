import sqlite3
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

connection = sqlite3.connect(current_directory + "/database.db")

cursor = connection.cursor()
query = "INSERT INTO tasks VALUES(5,'es004','Coursework 03 - ASE', 'BEng(Hons) (TOP UP) - LMU', '22-04-2023')"
cursor.execute(query)
connection.commit()