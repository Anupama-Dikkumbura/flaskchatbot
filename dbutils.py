import sqlite3
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

connection = sqlite3.connect(current_directory + "/database.db")
cursor = connection.cursor()
query = "INSERT INTO users VALUES(1,'es001', 'Anupama')"
cursor.execute(query)
connection.commit()
