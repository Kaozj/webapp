#project/db_create.py

##import sqlite3
##from _config import DATABASE_PATH

##with sqlite3.connect(DATABASE_PATH) as connection:

##	c= connection.cursor()

##	c.execute("CREATE TABLE tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, due_date TEXT NOT NULL, priority INTEGER NOT NULL, status INTEGER NOT NULL)")
##	c.execute("INSERT INTO tasks (name,due_date,priority,status) VALUES ('Finish_this_tutorial','03/25/2015',10,1)")
##	c.execute("INSERT INTO tasks (name,due_date,priority,status) VALUES ('Finish_plan','03/25/2015',10,1)")

from views import db
from models import Task
from datetime import date

db.create_all()

##db.session.add(Task('Finish this tutorial',date(2020,4,1),10,1))
##db.session.add(Task('Finish that',date(2020,5,1),10,1))

db.session.commit()

