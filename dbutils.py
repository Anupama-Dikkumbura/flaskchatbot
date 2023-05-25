import sqlite3
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

connection = sqlite3.connect(current_directory + "/database.db")

cursor = connection.cursor()
query = "INSERT INTO tasks VALUES(2,'es002','PM - Viva', 'BCS Foundation Certificate in BA', '15-06-2023')"
cursor.execute(query)
connection.commit()