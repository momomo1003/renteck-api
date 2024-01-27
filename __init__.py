import json
from typing import Optional
import pyodbc
import flask
import random


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


def get_headers():
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


@app.route("/login/<USERNAME>/<PASSWORD>")
def verify_user(USERNAME, PASSWORD):
    sql = f"""SELECT password FROM member WHERE NAME=N'{USERNAME}' """
    db.execute_sql_query(sql)
    fetch = db.cursor.fetchall()
    if len(fetch) == 0:
        return flask.jsonify({"valid": False}), 200
    pw = fetch[0][0]
    isvalid = pw == PASSWORD
    return flask.jsonify({"valid": isvalid}), 200


@app.route("/uid/<USERNAME>")
def user_id(USERNAME):
    sql = f"""SELECT user_id FROM member WHERE NAME=N'{USERNAME}' """
    db.execute_sql_query(sql)
    fetch = db.cursor.fetchall()
    if len(fetch) == 0:
        return flask.jsonify({"valid": False}), 200
    uid = fetch[0][0]

    return flask.jsonify({"id": uid}), 200


@app.route("/mail/<USERNAME>")
def usermail(USERNAME):
    sql = f"""SELECT mail FROM member WHERE NAME=N'{USERNAME}' """
    db.execute_sql_query(sql)
    fetch = db.cursor.fetchall()
    if len(fetch) == 0:
        return flask.jsonify({"valid": False}), 200
    mail = fetch[0][0]

    return flask.jsonify({"mail": mail}), 200


@app.route("/register/<USERNAME>/<PASSWORD>/<MAIL>", methods=["POST"])
def add_new_member(USERNAME, PASSWORD, MAIL):
    db.execute_sql_query("""SELECT COUNT(*) AS user_count FROM member""")
    user_count = db.cursor.fetchone()[0]
    if not user_count:
        user_count = 0
    query = f"""INSERT INTO member(mail, name, password, status, user_id) VALUES ('{MAIL}', '{USERNAME}','{PASSWORD}', {'0' if True else '1'}, {user_count +1})"""
    db.execute_sql_query(query)
    db.commit()
    return "added succesfully", 200


@app.route("/table/info/<TABLE>")
def get_table_info(TABLE):
    sql = f"""SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = N'{TABLE}'
"""
    db.execute_sql_query(sql)
    entries = get_headers()
    """
    200 ->  成功コード
    """
    return flask.jsonify(json.dumps(entries)), 200


@app.route("/table/<TABLE>")
def get_table(TABLE):
    sql = f""" SELECT * FROM {TABLE}"""
    db.execute_sql_query(sql)
    entries = populate_entries()
    """
    200 ->  成功コード
    """
    return flask.jsonify({"data": entries}), 200


@app.route("/pcinfo/<PC_ID>")
def get_remaining(PC_ID):
    sql = f"""SELECT Inventory_control from Inventory_control WHERE pc_number = N'{PC_ID}'"""
    db.execute_sql_query(sql)
    remaining = db.cursor.fetchone()
    return flask.jsonify({"remaining": remaining[0]}), 200


@app.route("/products")
def get_products():
    sql = f"""SELECT * FROM pc_information"""
    db.execute_sql_query(sql)

    json_data = {
        item[0]: {
            "model": item[1],
            "manufacturer": item[2],
        }
        for item in db.cursor.fetchall()
    }

    return flask.jsonify(json_data), 200


@app.route("/table/<TABLE>/<ROW>")
def get_row_from_table(TABLE, ROW):
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


@app.route(
    "/rent/<rnum>/<pcnum>/<uid>/<begin>/<end>/<received>/<returned>", methods=["POST"]
)
def rent(rnum, pcnum, uid, begin, end, received, returned):
    updated = False
    try:
        query = f"""INSERT INTO rental_management(rental_number, pc_number, user_id, startdata, enddata, received, returned) VALUES ({rnum}, {pcnum}, '{uid}', '{str(begin)}', '{str(end)}', {received}, {returned})"""
        db.execute_sql_query(query)
        db.commit()
        updated = True
    except:
        print("something went wrong")
    if updated:
        query = f"""UPDATE Inventory_Control SET Inventory_Control = Inventory_Control - 1 WHERE pc_number = N'{pcnum}' """
        db.execute_sql_query(query)
        db.commit()
    return "rent success", 200


def update_return():
    ...


@app.route("/update_rental_status/<uid>/<rnum>", methods=["GET"])
def update_rental_status(uid, rnum):
    try:
        update_query = f"""UPDATE rental_management
                           SET returned = 1
                           WHERE user_id = N'{uid}' AND rental_number = N'{rnum}'"""
        db.execute_sql_query(update_query)

        return flask.jsonify({"message": "Rental status updated successfully"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@app.route("/rstatus/<uid>/<returned>")
def get_rental_status(uid, returned):
    datequery = f"""SELECT enddata, startdata, pc_number, rental_number, user_id FROM rental_management WHERE user_id = N'{uid}' AND returned = N'{returned}'"""
    db.execute_sql_query(datequery)
    rental_data_list = db.cursor.fetchall()
    if rental_data_list:
        response_list = []

        for rental_data in rental_data_list:
            enddata, startdata, pc_number, rentalnum, user = rental_data

            machinequery = f"""SELECT manufacturer, model FROM pc_information WHERE pc_number = N'{pc_number}'"""
            db.execute_sql_query(machinequery)
            machine_data = db.cursor.fetchone()

            if machine_data:
                manufacturer, model = machine_data

                response_dict = {
                    "enddata": enddata,
                    "startdata": startdata,
                    "pc_number": pc_number,
                    "manufacturer": manufacturer,
                    "model": model,
                    "rentalnum": rentalnum,
                    "userid": user,
                }
                response_list.append(response_dict)

        return flask.jsonify(response_list), 200

    return flask.jsonify({"error": "No data found"}), 404


@app.route("/list")
def get_list_of_products():
    sql = """SELECT user_id FROM rental_management"""
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


@app.route("/available")
def get_available():
    sql = """SELECT user_id FROM rental_management WHERE returned = 0  """
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


@app.route("/number")
def get_number():
    sql = """SELECT COUNT(id) FROM rental_management WHERE returned = 0  """
    db.execute_sql_query(sql)
    entries = populate_entries()

    return flask.jsonify(entries), 200


if __name__ == "__main__":
    app.run()
