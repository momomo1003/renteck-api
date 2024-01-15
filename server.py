from typing import Optional
import pyodbc
import flask


class Database:
    SERVER = "tcp:renteck-server.database.windows.net"
    DATABASE = "renteckDB"
    USERNAME = "renteck"
    PASSWORD = "SA_Server"

    def __init__(self) -> None:
        self.conn: Optional[pyodbc.Connection] = None
        self.cursor: Optional[pyodbc.Cursor] = None

    def get_conn_str(self):
        return f"DRI:VER={{ODBC Driver 18 for SQL Server}};SERVER={self.SERVER};DATABASE={self.DATABASE};UID={self.USERNAME};PWD={self.PASSWORD}"

    def establish_conn(self):
        self.conn = pyodbc.connect(self.get_conn_str())
        self.cursor = self.conn.cursor()

    def exec_query(self, sql: str):
        if self.cursor:
            self.cursor.execute(sql)


app = flask.Flask(__name__)
db = Database()


@app.route("/list")
def get_list():
    sql = """SELECT FROM rental_management"""


@app.route("/available")
def get_available():
    ...


@app.route("/number")
def get_number():
    ...