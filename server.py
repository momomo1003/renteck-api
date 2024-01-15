import pyodbc

SERVER = "tcp:renteck-server.database.windows.net"
DATABASE = "renteckDB"
USERNAME = "renteck"
PASSWORD = "SA_Server"

conn_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
conn = pyodbc.connect(conn_string)
if conn:
    print("connexion success")
else:
    print("Could not connect")

cursor = conn.cursor()
QUERY = """INSERT INTO rental_management(rental_number, pc_number, id, startdata, enddata, received, returned) VALUES (1, 1, 'laptop', '20200606 10:10:20 AM', '20210606 10:20:30',0,0)"""
cursor.execute(QUERY)
QUERY = """SELECT pc_number, id FROM rental_management"""

cursor.execute(QUERY)

re = cursor.fetchall()

for r in re:
    print(r)
