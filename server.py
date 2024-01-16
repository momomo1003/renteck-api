from typing import Optional
import pyodbc
import flask


class Database:
    SERVER = "tcp:renteck-server.database.windows.net"
    DATABASE = "renteckDB"
    USERNAME = "renteck"
    PASSWORD = "SA_Server"

    def __init__(self) -> None:
        self.connection: Optional[pyodbc.Connection] = None
        self.cursor: Optional[pyodbc.Cursor] = None
        self.establish_connection()

    def get_connection_string(self):
        """
        データベースの文字列の生成。
        """
        return f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={self.SERVER};DATABASE={self.DATABASE};UID={self.USERNAME};PWD={self.PASSWORD}"

    def establish_connection(self):
        """
        接続の準備を行う。
        """
        try:
            self.connection = pyodbc.connect(self.get_connection_string())
        except:
            raise "接続不可能"
        self.cursor = self.connection.cursor()

    def execute_sql_query(self, sql: str):
        """
        SQLクエリーを実行する。
        """

        if self.cursor:
            try:
                self.cursor.execute(sql)
            except pyodbc.ProgrammingError:
                raise "SQLクエリー実行失敗"

    def commit(self):
        """
        データベースの変更を有効化する。
        """
        self.connection.commit()


app = flask.Flask(__name__)
db = Database()


def populate_entries():
    headers = [e[0] for e in db.cursor.description]
    entries = []
    for entry in db.cursor.fetchall():
        """
        zip:
            --------------------------------------------
           | header  |   entry                          |
           | -------------------------------------------
           | title1  |   entry1  ->  (title1, entry1)   |
           | title2  |   entry2  ->  (title2, entry2)   |
           | title3  |           ->                     |
            --------------------------------------------
        dict:
            以上のタプルを結合して辞書に保存する
        """
        entries.append(dict(zip(headers, entry)))
    return entries


@app.route("/table/<TABLE>")
def get_table(TABLE):
    sql = f""" SELECT * FROM {TABLE}"""
    db.execute_sql_query(sql)
    entries = populate_entries()
    """
    200 ->  成功コード
    """
    return flask.jsonify(entries), 200


@app.route("/table/<TABLE>/<ROW>")
def get_table(TABLE, ROW):
    sql = f""" SELECT {ROW} FROM {TABLE}"""
    db.execute_sql_query(sql)
    entries = populate_entries()
    return flask.jsonify(entries), 200


@app.route("/table/all")
def get_all_tables():
    sql = f""" SELECT * FROM INFORMATION_SCHEMA.TABLES"""
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


@app.route("/list")
def get_list_of_products():
    sql = """SELECT id FROM rental_management"""
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


@app.route("/available")
def get_available():
    sql = """SELECT id FROM rental_management WHERE returned = 0  """
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


@app.route("/number")
def get_number():
    sql = """SELECT COUNT(id) FROM rental_management WHERE returned = 0  """
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


app.run("0.0.0.0")
