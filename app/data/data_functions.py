from sqlite3 import connect
from data.table import Table
from random import *
data = connect("data.db", isolation_level=None, check_same_thread=False)

users = Table(data, "users", "email")

def reset_data():
    "resets the database to empty user and story tables"
    open("data.db", "w").close()

