import pyodbc

SERVER = "tcp:renteck-server.database.windows.net"
DATABASE = "renteckDB"
USERNAME = "renteck"
PASSWORD = "SA_Renteck"

conn_string = f"DRI:VER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
conn = pyodbc.connect(conn_string)
print("connexion success")
